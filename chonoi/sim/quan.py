"""Buổi tối — Mở Quán (`quan`). Luật theo PRD-0 mục F (Quán), sự kiện theo mục E, scenario theo mục D.

Mặt bằng nhà bè nhìn từ trên xuống: vị trí `[x, z]`, z hướng bắc.

Một bước (đúng thứ tự PRD-0 F):
  1. đồng hồ: phase_tick + 1, giảm timer ca, nấu, ăn, kiên nhẫn; ready_ticks + 1 chỉ cho món đã ready ĐẦU bước
  2. bếp theo id: cooking hết giờ -> ready (ready_ticks = 0), `dish_ready`
  3. di chuyển rồi tối đa MỘT interact, chọn theo (khoảng cách, bếp trước bàn, id)
       bếp idle  -> nấu đơn reserved cũ nhất (order_tick, id bàn), tiêu phần giữ, chốt giá  `cook_started`
       bếp ready -> giao món cho tay trống, bếp về idle                                     `dish_picked`
       bàn       -> giao đúng order_id, khách ăn với timer đầy, chốt boa                    `served`
  4. theo id bàn: ăn xong trả tiền (`paid`) rồi rời; còn giờ + kiên nhẫn 0 -> `customer_left` (patience);
     hết ca: đang ăn trả ngay (closing), đang chờ rời (closing, không trừ uy tín) -> `quan_end`
  5. còn giờ: lượt khách theo lịch -> bàn trống id nhỏ nhất, chọn đều theo seed trong món khả dụng
     (trong `day`: chỉ món thuộc kế hoạch Ngày — Ticket-02 mục 2, 4.5),
     giữ chỗ ngay -> `customer_arrived`; có bàn mà không món nào đủ -> `no_dish`

Số liệu chỉ đọc từ tuning (game.contract.json). Ngẫu nhiên chỉ qua Streams (luồng "customers").
"""

import math

from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0
CUSTOMER_PREFIX = "C"  # id khách = order_id (PRD-0 D); họ id mới nối sau hậu tố lớn nhất đã nạp


def _ticks(seconds) -> int:
    return int(round(seconds * TICK))


UNITS = 240  # ADR-0002: 240 đơn vị nguyên = 1 điểm tươi -> so ngưỡng 30 và floor giá không sai số thực


class FreshStock:
    """Kho cá thể v1.2 (Ticket-03): {id: {id, kind, units}}; fresh = units / 240. Kho là tồn vật lý (gồm hàng giữ)."""

    def __init__(self, items, fr):
        self.decay = int(round(fr["quan_decay_per_s"] * UNITS / TICK))  # 0.25/s -> 1 đơn vị/tick
        self.spoil_below = int(round(fr["spoiled_below"] * UNITS))
        self.items = {it["id"]: {"id": it["id"], "kind": it["kind"], "units": int(round(it["fresh"] * UNITS))}
                      for it in items}

    @staticmethod
    def view(it):
        return {"id": it["id"], "kind": it["kind"], "fresh": it["units"] / UNITS}

    def spoiled(self, iid) -> bool:
        return self.items[iid]["units"] < self.spoil_below

    def decay_step(self):
        """Hao tươi một tick; trả id vừa đi từ >= ngưỡng xuống < ngưỡng (theo id)."""
        crossed = []
        for iid in sorted(self.items, key=id_key):
            it = self.items[iid]
            before = it["units"]
            it["units"] = max(0, before - self.decay)
            if before >= self.spoil_below > it["units"]:
                crossed.append(iid)
        return crossed

    def pick(self, recipe, taken):
        """Chọn cá thể khả dụng tươi nhất (hòa theo id) cho từng loại; None nếu thiếu."""
        out = []
        for kind in sorted(recipe):
            cand = [it for it in self.items.values()
                    if it["kind"] == kind and it["id"] not in taken and not self.spoiled(it["id"])]
            cand.sort(key=lambda it: (-it["units"], id_key(it["id"])))
            if len(cand) < recipe[kind]:
                return None
            out += [it["id"] for it in cand[:recipe[kind]]]
        return out


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, dish_ids=None, kitchen=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        # Ticket-02 mục 2: trong `day` khách chỉ gọi món thuộc kế hoạch Ngày; quán độc lập dùng cả menu.
        self.dish_ids = sorted(dish_ids) if dish_ids is not None else sorted(self.menu)
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2). Kho là tồn VẬT LÝ, gồm phần giữ chỗ.
        # v1.2 (Ticket-03): tuning có `freshness` -> kho cá thể (mảng {id,kind,fresh}), giữ chỗ theo id.
        raw = inventory if inventory is not None else scenario.get("stock", [] if "freshness" in tuning else {})
        self.fresh = FreshStock(raw, tuning["freshness"]) if "freshness" in tuning else None
        self.stock = {} if self.fresh else dict(raw)
        self.hand = scenario.get("hand")
        self.duration_ticks = _ticks(t["duration_s"])
        self.time_left_ticks = scenario.get("time_left_ticks", self.duration_ticks)
        self.phase_tick = 0
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.random_customers = scenario.get("random_customers", True)
        self.patience_full = _ticks(t["patience_s"])
        self.eat_full = _ticks(t["eat_s"])
        self.interval_ticks = _ticks(t["customer_interval_s"])
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = self._load_customers(scenario.get("customers", []))
        for e in self.customers:
            ids.reserve(e["id"])
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None
        # Sáng tạo của nhóm — Bếp nhiều section (chonoi/creative/kitchen.json). None = luật lõi Test Contract.
        self.kitchen = kitchen
        if kitchen is not None:
            self.sections = [dict(s, state="idle", order_id=None, ticks_left=0)
                             for s in sort_by_id(kitchen["sections"])]
            self.prep_ticks = {k: _ticks(v) for k, v in kitchen["prep_s"].items()}
            self.prepped = {}  # order_id -> {kind: số phần đã sơ chế}

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                from ..errors import BadInput
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _load_customers(self, src):
        """Khách dựng sẵn (PRD-0 D): điền mặc định; đơn reserved thiếu `reserved` thì cấp theo công thức,
        duyệt theo order_tick rồi id bàn."""
        out = []
        for c in src:
            c = dict(c)
            c.setdefault("state", "waiting")
            c.setdefault("order_tick", 0)
            c.setdefault("patience_ticks_left", self.patience_full)
            c.setdefault("eat_ticks_left", 0)
            c.setdefault("order_status", "reserved")
            c.setdefault("base_price", None)
            c.setdefault("tip", None)
            out.append(c)
        for c in sorted(out, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
            if "reserved" not in c:
                recipe = self.menu.get(c.get("dish_id"), {}).get("recipe", {})
                if self.fresh is None:
                    c["reserved"] = dict(recipe) if c["order_status"] == "reserved" else {}
                elif c["order_status"] == "reserved":  # v1.2: cấp id tươi nhất rồi id nhỏ
                    c["reserved"] = self.fresh.pick(recipe, self._taken(out)) or []
                else:
                    c["reserved"] = []
        return out

    # --- v1.2: giữ chỗ theo id ----------------------------------------------------
    def _taken(self, customers=None):
        return {i for c in (customers if customers is not None else self.customers) for i in (c.get("reserved") or [])
                if isinstance(c.get("reserved"), list)}

    def _reserved_counts(self, c) -> dict:
        """Phần giữ của đơn theo loại (dùng chung v1.1 map và v1.2 mảng id)."""
        r = c.get("reserved") or {}
        if isinstance(r, dict):
            return r
        out = {}
        for iid in r:
            k = self.fresh.items[iid]["kind"]
            out[k] = out.get(k, 0) + 1
        return out

    def _handle_spoiled(self, crossed, events):
        """Phát spoiled theo id, rồi xử lý các đơn có phần giữ vừa ươn: nhả và thử giữ lại đúng một lần."""
        for iid in crossed:
            events.append(("spoiled", {"item_id": iid, "kind": self.fresh.items[iid]["kind"], "location": "stock"}))
        hit = set(crossed)
        affected = [c for c in self.customers if c["order_status"] == "reserved" and hit & set(c["reserved"])]
        for c in sorted(affected, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
            c["reserved"] = []
            got = self.fresh.pick(self.menu[c["dish_id"]]["recipe"], self._taken())
            if got is None:
                c["order_status"] = "unfulfillable"
            else:
                c["reserved"] = got

    # --- giao diện cho runner -------------------------------------------------
    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": self.stock_view(),
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": [self._customer_view(c) for c in sort_by_id(self.customers)],
            **self._kitchen_view(),
        }

    def _kitchen_view(self) -> dict:
        if self.kitchen is None:
            return {}  # headless / Test Contract: snapshot không đổi
        return {
            "sections": [{k: s[k] for k in ("id", "kind", "pos", "state", "order_id", "ticks_left")}
                         | {"ticks_total": self.prep_ticks[s["kind"]]} for s in self.sections],
            "prepped": {oid: dict(sorted(v.items())) for oid, v in sorted(self.prepped.items(), key=lambda x: id_key(x[0]))},
        }

    def stock_view(self):
        """v1.1: {kind: n>0} sắp theo kind · v1.2: mảng cá thể {id,kind,fresh} sắp theo id (gồm hàng ươn)."""
        if self.fresh is not None:
            return [FreshStock.view(self.fresh.items[i]) for i in sorted(self.fresh.items, key=id_key)]
        return {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0}

    def _customer_view(self, c):
        keys = ("id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left", "eat_ticks_left",
                "order_status", "reserved", "base_price", "tip")
        view = {k: c.get(k) for k in keys}
        r = c.get("reserved") or ({} if self.fresh is None else [])
        view["reserved"] = sorted(r, key=id_key) if isinstance(r, list) else {k: v for k, v in sorted(r.items()) if v > 0}
        return view

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        # 1. đồng hồ, timer ca, nấu, ăn, kiên nhẫn
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        for s in self.stoves:
            if s["state"] == "ready":
                s["ready_ticks"] += 1
            elif s["state"] == "cooking":
                s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
        for c in self.customers:
            if c["state"] == "eating":
                c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)
            elif c["state"] == "waiting":
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)
        if self.fresh is not None:  # v1.2: hao tươi kho thô, spoiled theo id, rồi xử lý giữ chỗ bị ươn
            self._handle_spoiled(self.fresh.decay_step(), events)
        if self.kitchen is not None:
            self._tick_sections(events)
        # 2. bếp theo id: nấu xong -> ready (burn_s: null, không cháy)
        for s in self.stoves:
            if s["state"] == "cooking" and s["cook_ticks_left"] == 0:
                s["state"] = "ready"
                s["ready_ticks"] = 0
                events.append(("dish_ready", self._dish_ref(s)))
        # 3. di chuyển rồi tối đa một interact
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        # 4. thanh toán / rời bàn theo id bàn
        closing = self.time_left_ticks == 0
        for c in sorted(self.customers, key=lambda c: id_key(c["table_id"])):
            if c["state"] == "eating" and (c["eat_ticks_left"] == 0 or closing):
                self._pay(c, "finished_eating" if c["eat_ticks_left"] == 0 else "closing", events)
            elif c["state"] == "waiting" and closing:
                self._leave(c, "closing", events)
            elif c["state"] == "waiting" and c["patience_ticks_left"] == 0:
                self._leave(c, "patience", events)
        if closing:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
            return events
        # 5. lượt khách theo lịch
        if self.random_customers and self._customer_due():
            self._spawn_customer(events)
        return events

    # --- bước 3: tương tác ------------------------------------------------------
    def _interact(self, events):
        r = self.t["interact_radius"]
        cands = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= r:
                cands.append((d, 0, id_key(s["id"]), "stove", s))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= r:
                cands.append((d, 2, id_key(tb["id"]), "table", tb))
        if self.kitchen is not None:  # sáng tạo: section xếp sau bếp, trước bàn
            for sec in self.sections:
                d = math.dist(self.pos, sec["pos"])
                if d <= r:
                    cands.append((d, 1, id_key(sec["id"]), "section", sec))
        if not cands:
            return
        _, _, _, kind, obj = min(cands, key=lambda x: x[:3])
        if kind == "stove":
            if obj["state"] == "idle":
                self._start_cooking(obj, events)
            elif obj["state"] == "ready" and self.hand is None:
                self._pick_dish(obj, events)
        elif kind == "section":
            self._start_prep(obj, events)
        else:
            self._serve(obj, events)  # đối tượng không tương tác được -> bỏ lượt

    # --- sáng tạo: bếp nhiều section -------------------------------------------
    def _prep_need(self, c, kind) -> int:
        """Số phần `kind` đơn `c` còn cần đưa vào section (trừ phần đã xong và đang làm)."""
        done = self.prepped.get(c["id"], {}).get(kind, 0)
        working = sum(1 for s in self.sections if s["state"] == "working" and s["order_id"] == c["id"]
                      and s["kind"] == kind)
        return self._reserved_counts(c).get(kind, 0) - done - working

    def _prep_complete(self, c) -> bool:
        got = self.prepped.get(c["id"], {})
        return all(got.get(k, 0) >= n for k, n in self._reserved_counts(c).items())

    def _start_prep(self, sec, events):
        if sec["state"] != "idle":
            return
        orders = [c for c in self.customers if c["order_status"] == "reserved" and self._prep_need(c, sec["kind"]) > 0]
        if not orders:
            return
        c = min(orders, key=lambda c: (c["order_tick"], id_key(c["table_id"])))
        sec.update(state="working", order_id=c["id"], ticks_left=self.prep_ticks[sec["kind"]])
        events.append(("prep_started", {"section_id": sec["id"], "order_id": c["id"], "kind": sec["kind"]}))

    def _tick_sections(self, events):
        for sec in self.sections:
            if sec["state"] != "working":
                continue
            sec["ticks_left"] -= 1
            if sec["ticks_left"] <= 0:
                got = self.prepped.setdefault(sec["order_id"], {})
                got[sec["kind"]] = got.get(sec["kind"], 0) + 1
                events.append(("prep_done", {"section_id": sec["id"], "order_id": sec["order_id"], "kind": sec["kind"]}))
                sec.update(state="idle", order_id=None, ticks_left=0)

    def _start_cooking(self, stove, events):
        orders = [c for c in self.customers if c["order_status"] == "reserved"]
        if self.kitchen is not None:  # sáng tạo: chỉ gộp đơn đã sơ chế đủ mọi nguyên liệu
            orders = [c for c in orders if self._prep_complete(c)]
        if not orders:
            return
        c = min(orders, key=lambda c: (c["order_tick"], id_key(c["table_id"])))
        dish = self.menu[c["dish_id"]]
        price = dish["price"]
        if self.fresh is None:
            items = []
            for kind in sorted(c["reserved"]):
                n = c["reserved"][kind]
                self.stock[kind] = self.stock.get(kind, 0) - n
                items.extend([kind] * n)
        else:  # v1.2: tiêu đúng các id đang giữ; giá = floor(giá niêm yết × trung bình fresh / 100)
            used = [self.fresh.items.pop(i) for i in c["reserved"]]
            used.sort(key=lambda it: (it["kind"], id_key(it["id"])))
            items = [FreshStock.view(it) for it in used]
            price = (price * sum(it["units"] for it in used)) // (len(used) * UNITS * 100)
        c["reserved"] = {} if self.fresh is None else []
        c["order_status"] = "assigned"
        c["base_price"] = price
        if self.kitchen is not None:
            self.prepped.pop(c["id"], None)
        stove["state"] = "cooking"
        stove["dish"] = {"order_id": c["id"], "dish_id": c["dish_id"], "base_price": price}
        stove["cook_ticks_left"] = _ticks(dish["cook_s"])
        stove["ready_ticks"] = 0
        events.append(("cook_started", dict(self._dish_ref(stove), items=items, base_price=price)))

    def _pick_dish(self, stove, events):
        ref = self._dish_ref(stove)
        self.hand = stove["dish"]
        stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        events.append(("dish_picked", ref))

    def _serve(self, table, events):
        c = next((c for c in self.customers if c["table_id"] == table["id"]), None)
        if c is None or c["state"] != "waiting" or self.hand is None or self.hand.get("order_id") != c["id"]:
            return
        price = self.hand["base_price"]
        ratio = c["patience_ticks_left"] / self.patience_full
        tip = math.floor(price * self.t["tip_rate"]) if ratio >= self.t["tip_min_patience_ratio"] else 0
        c.update(state="eating", order_status="served", eat_ticks_left=self.eat_full, base_price=price, tip=tip)
        self.hand = None
        events.append(("served", {"order_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"],
                                  "patience_ticks_left": c["patience_ticks_left"], "base_price": price, "tip": tip}))

    # --- bước 4: trả tiền / rời bàn ----------------------------------------------
    def _pay(self, c, reason, events):
        amount = c["base_price"] + c["tip"]
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        if c["tip"] > 0:
            self._add_reputation(self.t["tip_reputation"])
        self.customers.remove(c)
        events.append(("paid", {"order_id": c["id"], "table_id": c["table_id"], "base_price": c["base_price"],
                                "tip": c["tip"], "amount": amount, "reason": reason}))

    def _leave(self, c, reason, events):
        # nhả phần giữ thô (kho là tồn vật lý nên không đổi); bỏ món của đơn đang nấu / ready / trên tay
        c["reserved"] = {} if self.fresh is None else []
        for s in self.stoves:
            if s["dish"] and s["dish"].get("order_id") == c["id"]:
                s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        if self.hand and self.hand.get("order_id") == c["id"]:
            self.hand = None
        if self.kitchen is not None:  # sáng tạo: bỏ phần sơ chế dở của đơn
            self.prepped.pop(c["id"], None)
            for sec in self.sections:
                if sec["order_id"] == c["id"]:
                    sec.update(state="idle", order_id=None, ticks_left=0)
        if reason == "patience":
            self._add_reputation(self.t["left_reputation_delta"])
        self.customers.remove(c)
        events.append(("customer_left", {"order_id": c["id"], "table_id": c["table_id"], "reason": reason,
                                         "reputation": self.reputation}))

    def _add_reputation(self, delta):
        self.reputation = min(self.t["reputation_max"], max(self.t["reputation_min"], self.reputation + delta))

    # --- bước 5: khách mới -------------------------------------------------------
    def _customer_due(self) -> bool:
        first = self.t["first_customer_tick"]
        k = self.phase_tick - first
        return k >= 0 and k % self.interval_ticks == 0

    def _available(self) -> dict:
        """Kho khả dụng = tồn vật lý − tổng phần đang giữ chỗ."""
        if self.fresh is not None:  # v1.2: cá thể chưa ươn và chưa bị giữ
            taken, avail = self._taken(), {}
            for it in self.fresh.items.values():
                if it["id"] not in taken and not self.fresh.spoiled(it["id"]):
                    avail[it["kind"]] = avail.get(it["kind"], 0) + 1
            return avail
        avail = dict(self.stock)
        for c in self.customers:
            for kind, n in self._reserved_counts(c).items():
                avail[kind] = avail.get(kind, 0) - n
        return avail

    def _spawn_customer(self, events):
        busy = {c["table_id"] for c in self.customers}
        free = [tb for tb in self.tables if tb["id"] not in busy]  # self.tables đã sắp theo id
        if not free:
            return
        avail = self._available()
        dishes = [d for d in self.dish_ids  # lọc theo kế hoạch trước, rồi mới lọc nguyên liệu khả dụng
                  if all(avail.get(k, 0) >= n for k, n in self.menu[d]["recipe"].items())]
        if not dishes:
            events.append(("no_dish", {}))
            return
        dish_id = dishes[self.rng.get("customers").randrange(len(dishes))]
        table = free[0]
        cid = self.ids.new(CUSTOMER_PREFIX)
        self.customers.append({
            "id": cid, "table_id": table["id"], "dish_id": dish_id, "order_tick": self.phase_tick,
            "state": "waiting", "patience_ticks_left": self.patience_full, "eat_ticks_left": 0,
            "order_status": "reserved",
            "reserved": (dict(self.menu[dish_id]["recipe"]) if self.fresh is None
                         else self.fresh.pick(self.menu[dish_id]["recipe"], self._taken())),
            "base_price": None, "tip": None,
        })
        events.append(("customer_arrived", {"order_id": cid, "table_id": table["id"], "dish_id": dish_id}))

    # --- tiện ích ---------------------------------------------------------------
    @staticmethod
    def _dish_ref(stove):
        d = stove["dish"]
        return {"stove_id": stove["id"], "order_id": d["order_id"], "dish_id": d["dish_id"]}

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
