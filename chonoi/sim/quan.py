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
  5. còn giờ: lượt khách theo lịch -> bàn trống id nhỏ nhất, chọn đều theo seed trong món khả dụng,
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


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2). Kho là tồn VẬT LÝ, gồm phần giữ chỗ.
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
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
                c["reserved"] = dict(recipe) if c["order_status"] == "reserved" else {}
        return out

    # --- giao diện cho runner -------------------------------------------------
    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": [self._customer_view(c) for c in sort_by_id(self.customers)],
        }

    @staticmethod
    def _customer_view(c):
        keys = ("id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left", "eat_ticks_left",
                "order_status", "reserved", "base_price", "tip")
        view = {k: c.get(k) for k in keys}
        view["reserved"] = {k: v for k, v in sorted(c.get("reserved", {}).items()) if v > 0}
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
                cands.append((d, 1, id_key(tb["id"]), "table", tb))
        if not cands:
            return
        _, _, _, kind, obj = min(cands, key=lambda x: x[:3])
        if kind == "stove":
            if obj["state"] == "idle":
                self._start_cooking(obj, events)
            elif obj["state"] == "ready" and self.hand is None:
                self._pick_dish(obj, events)
        else:
            self._serve(obj, events)  # đối tượng không tương tác được -> bỏ lượt

    def _start_cooking(self, stove, events):
        orders = [c for c in self.customers if c["order_status"] == "reserved"]
        if not orders:
            return
        c = min(orders, key=lambda c: (c["order_tick"], id_key(c["table_id"])))
        dish = self.menu[c["dish_id"]]
        items = []
        for kind in sorted(c["reserved"]):
            n = c["reserved"][kind]
            self.stock[kind] = self.stock.get(kind, 0) - n
            items.extend([kind] * n)
        c["reserved"] = {}
        c["order_status"] = "assigned"
        c["base_price"] = dish["price"]
        stove["state"] = "cooking"
        stove["dish"] = {"order_id": c["id"], "dish_id": c["dish_id"], "base_price": dish["price"]}
        stove["cook_ticks_left"] = _ticks(dish["cook_s"])
        stove["ready_ticks"] = 0
        events.append(("cook_started", dict(self._dish_ref(stove), items=items, base_price=dish["price"])))

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
        c["reserved"] = {}
        for s in self.stoves:
            if s["dish"] and s["dish"].get("order_id") == c["id"]:
                s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        if self.hand and self.hand.get("order_id") == c["id"]:
            self.hand = None
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
        avail = dict(self.stock)
        for c in self.customers:
            for kind, n in c.get("reserved", {}).items():
                avail[kind] = avail.get(kind, 0) - n
        return avail

    def _spawn_customer(self, events):
        busy = {c["table_id"] for c in self.customers}
        free = [tb for tb in self.tables if tb["id"] not in busy]  # self.tables đã sắp theo id
        if not free:
            return
        avail = self._available()
        dishes = [d for d in sorted(self.menu)
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
            "order_status": "reserved", "reserved": dict(self.menu[dish_id]["recipe"]),
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
