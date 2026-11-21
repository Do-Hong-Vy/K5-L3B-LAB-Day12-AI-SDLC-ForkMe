"""Buổi sáng — Lặn & Hái (`gather`).

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Luật Phase 1 (PRD-0) & Phase 2 L1 (Ticket-02 mục 1.1, 4.3–4.5):
  - Bơi + ramp + chặn mép, phân vùng mặt nước (`dive`/`surface`), oxy/ngạt (`oxygen_empty`,
    `choke`), Máu về 0 (`faint`, mất giỏ LIFO, `gather_end` reason `fainted` với kho rỗng), giỏ LIFO.
  - `interact` (bến trước -> `docked`, ngoài bến ở mặt nước -> hái nút `ready`, `hold_full`,
    mọc lại `node_regrown`), `catch` (dưới nước + hết hồi -> bắt đàn cá theo vị trí trước khi bơi),
    hết giờ (`time`).
  - Đàn cá bơi (`fish_speed`, `fish_turn_ticks` qua `Streams("fish_turn")`, phản xạ mép/góc trong
    `fish_x × fish_depths[kind]`) và sinh đàn mới theo lịch `fish_spawn_ticks` (`Streams("fish_spawn")`,
    trần `fish_max`, clearance > `fish_spawn_clearance`, phát `fish_spawned`). Tắt bơi/sinh khi `random_fish=false`.
"""

import math

from ..ids import id_key, sort_by_id
from ..inventory import hold_to_items
from .ramp import ramp_velocity

TICK = 60.0
AXES = ("x", "d")


class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids):
        t = tuning["gather"]
        self.t = t
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.oxygen_max = int(round(t["oxygen_max_s"] * TICK))
        self.oxygen_ticks = p.get("oxygen_ticks", self.oxygen_max)
        self.hp = p.get("hp", t["hp_max"])
        self.zero_oxy_ticks = p.get("zero_oxy_ticks", 0)
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.catch_cd_ticks = p.get("catch_cd_ticks", 0)
        self.hold = list(scenario.get("hold", []))  # thứ tự nhặt, cuối mảng là mới nhất
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.phase_tick = 0
        self.random_fish = bool(scenario.get("random_fish", True))
        # nút và đàn cá: scenario THAY THẾ danh sách mặc định; random_fish=false tắt cá mặc định, bơi và sinh
        src_nodes = scenario["nodes"] if "nodes" in scenario else t["nodes"]
        self.nodes = [{"id": n["id"], "kind": n["kind"], "pos": [float(c) for c in n["pos"]],
                       "regrow_ticks": n.get("regrow_ticks", 0)} for n in src_nodes]
        if "fish" in scenario:
            src_fish = scenario["fish"]
        elif self.random_fish:
            src_fish = t["fish_initial"]
        else:
            src_fish = []
        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": float(f.get("heading_deg", 0)), "age_ticks": int(f.get("age_ticks", 0))}
                     for f in src_fish]
        for coll in (self.nodes, self.fish):
            for e in coll:
                ids.reserve(e["id"])
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self) -> dict:
        return hold_to_items(self.hold)

    def snapshot(self) -> dict:
        return {
            "player": {"pos": self.pos, "vel": self.vel, "heading_deg": self.heading,
                       "oxygen_ticks": self.oxygen_ticks, "oxygen_max_ticks": self.oxygen_max,
                       "hp": self.hp, "hp_max": self.t["hp_max"], "zero_oxy_ticks": self.zero_oxy_ticks,
                       "invuln_ticks": self.invuln_ticks, "catch_cd_ticks": self.catch_cd_ticks,
                       "at_surface": self._at_surface()},
            "hold": self.hold, "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": n["pos"], "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]}
                      for n in sort_by_id(self.nodes)],
            "fish": [{"id": f["id"], "pos": f["pos"], "kind": f["kind"], "heading_deg": f["heading_deg"]}
                     for f in sort_by_id(self.fish)],
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        if self.done:
            return []
        events = []
        # 1. đồng hồ và hàng có sẵn: giảm bộ đếm, nút mọc lại
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.catch_cd_ticks = max(0, self.catch_cd_ticks - 1)
        for n in sort_by_id(self.nodes):
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))
        # 2. bơi + chặn mép + phân vùng + oxy/ngạt/ngất
        was_at_surface = self._at_surface()
        self._move(inp)
        now_at_surface = self._at_surface()
        if was_at_surface and not now_at_surface:
            events.append(("dive", {"pos": list(self.pos)}))
        elif not was_at_surface and now_at_surface:
            events.append(("surface", {"pos": list(self.pos)}))
        if self._update_oxygen_and_choke(events):
            return events
        # 3. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            self._try_harvest(events)
        # 4. bắt cá (dùng vị trí cá TRƯỚC khi bơi — Ticket-02 mục 4.5)
        if inp.pressed("catch"):
            self._try_catch(events)
        # 5. hết giờ; nếu còn giờ mới cho cá bơi & sinh thêm
        if self.time_left_ticks <= 0:
            self._finish("time", events)
            return events
        if self.random_fish:
            self._swim_and_spawn_fish(events)
        return events

    # --- tiện ích ---------------------------------------------------------------
    def _at_surface(self) -> bool:
        return self.pos[1] <= self.t["surface_depth"]

    def _in_dock(self) -> bool:
        return math.dist(self.pos, self.t["dock_pos"]) <= self.t["dock_radius"]

    def _nearest_in_radius(self, items, radius, predicate=None):
        """Chọn thực thể gần nhất trong bán kính Euclid (tính cả mép), hòa theo id_key."""
        best = None
        best_key = None
        for item in items:
            if predicate and not predicate(item):
                continue
            d = math.dist(self.pos, item["pos"])
            if d <= radius:
                key = (d, id_key(item["id"]))
                if best_key is None or key < best_key:
                    best = item
                    best_key = key
        return best

    def _update_oxygen_and_choke(self, events) -> bool:
        """Cập nhật oxy và ngạt theo d cuối bước; trả True nếu ngất và kết thúc lượt."""
        if self._at_surface():
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + int(self.t["oxygen_refill_per_tick"]))
            self.zero_oxy_ticks = 0
            return False
        prev_oxy = self.oxygen_ticks
        self.oxygen_ticks = max(0, self.oxygen_ticks - 1)
        if prev_oxy > 0 and self.oxygen_ticks == 0:
            events.append(("oxygen_empty", {"oxygen_ticks": 0}))
        if self.oxygen_ticks == 0:
            self.zero_oxy_ticks += 1
            if self.zero_oxy_ticks >= int(self.t["choke_interval_ticks"]):
                self.zero_oxy_ticks = 0
                self.hp = max(0, self.hp - 1)
                events.append(("choke", {"hp": self.hp}))
                if self.hp <= 0:
                    lost = list(reversed(self.hold))
                    self.hold.clear()
                    events.append(("faint", {"cause": "choke", "lost": lost, "hp": 0}))
                    self._finish("fainted", events)
                    return True
        return False

    def _try_harvest(self, events):
        """Hái nút ready gần nhất nếu đang ở mặt nước; từ chối toàn bộ nếu thiếu chỗ."""
        if not self._at_surface():
            return
        node = self._nearest_in_radius(self.nodes, self.t["interact_radius"], lambda n: n["regrow_ticks"] == 0)
        if node is None:
            return
        amount = int(self.t["node_yield"])
        free = int(self.t["hold_capacity"]) - len(self.hold)
        if free >= amount:
            self.hold.extend([node["kind"]] * amount)
            node["regrow_ticks"] = int(round(self.t["regrow_s"] * TICK))
            events.append(("gather", {"node_id": node["id"], "kind": node["kind"], "amount": amount}))
        else:
            events.append(("hold_full", {"action": "gather", "node_id": node["id"], "required": amount, "free": free}))

    def _try_catch(self, events):
        """Bắt đàn cá gần nhất nếu dưới nước và hết hồi chiêu; từ chối toàn bộ nếu thiếu chỗ."""
        if self.catch_cd_ticks > 0 or self._at_surface():
            return
        fish = self._nearest_in_radius(self.fish, self.t["catch_radius"])
        if fish is None:
            return
        yld = int(self.t["fish_yield"][fish["kind"]])
        free = int(self.t["hold_capacity"]) - len(self.hold)
        if free >= yld:
            self.hold.extend([fish["kind"]] * yld)
            self.fish.remove(fish)
            self.catch_cd_ticks = int(round(self.t["catch_cooldown_s"] * TICK))
            events.append(("fish_caught", {"fish_id": fish["id"], "kind": fish["kind"], "yield": yld}))
        else:
            events.append(("hold_full", {"action": "catch", "fish_id": fish["id"], "required": yld, "free": free}))

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": self.inventory_items()}}))

    def _move(self, inp):
        speed = self.t["swim_speed"]
        mx, md = inp.move
        self.vel = ramp_velocity(self, (mx * speed, md * speed), int(self.t["ramp_max_ticks"]))
        if (mx, md) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(md, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(AXES):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])

    @staticmethod
    def _reflect_axis(old: float, delta: float, lo: float, hi: float, bound_lo: float, bound_hi: float):
        """Di chuyển 1 trục và phản xạ phần dư khi chạm/vượt mép `[lo, hi]`; trả `(pos, flipped)`."""
        target = old + delta
        # Giữ nguyên nếu cá scenario xuất phát ngoài dải loài cho tới khi vào trong dải (không nhảy tức thì).
        if not (lo <= old <= hi) or lo >= hi:
            if delta < -1e-12 and target <= bound_lo:
                return max(bound_lo, 2.0 * bound_lo - target), True
            if delta > 1e-12 and target >= bound_hi:
                return min(bound_hi, 2.0 * bound_hi - target), True
            return target, False
        if (delta < -1e-12 and target <= lo) or (delta > 1e-12 and target >= hi):
            flipped = False
            while target < lo or target > hi:
                if target < lo:
                    target = 2.0 * lo - target
                else:
                    target = 2.0 * hi - target
                flipped = not flipped
            # Chạm đúng mép không dư quãng (target == lo hoặc hi) vẫn đảo hướng vuông góc.
            return target, flipped or (target == lo and delta < -1e-12) or (target == hi and delta > 1e-12)
        return target, False

    def _swim_and_spawn_fish(self, events):
        """Cá bơi trong dải loài, đổi hướng mỗi `fish_turn_ticks` và sinh thêm tại `fish_spawn_ticks * k`."""
        turn_ticks = int(self.t["fish_turn_ticks"])
        step_dist = float(self.t["fish_speed"]) / TICK
        x_lo, x_hi = [float(c) for c in self.t["fish_x"]]
        bx_lo, bx_hi = [float(c) for c in self.t["bounds"]["x"]]
        bd_lo, bd_hi = [float(c) for c in self.t["bounds"]["d"]]
        depths_map = self.t["fish_depths"]
        turn_rng = self.rng.get("fish_turn")

        for f in sort_by_id(self.fish):
            f["age_ticks"] += 1
            if f["age_ticks"] % turn_ticks == 0:
                f["heading_deg"] = turn_rng.uniform(0.0, 360.0)
            rad = math.radians(f["heading_deg"])
            dx, dd = step_dist * math.cos(rad), step_dist * math.sin(rad)
            d_lo, d_hi = [float(c) for c in depths_map[f["kind"]]]
            nx, flip_x = self._reflect_axis(f["pos"][0], dx, x_lo, x_hi, bx_lo, bx_hi)
            nd, flip_d = self._reflect_axis(f["pos"][1], dd, d_lo, d_hi, bd_lo, bd_hi)
            f["pos"] = [nx, nd]
            h = f["heading_deg"]
            if flip_x:
                h = (180.0 - h) % 360.0
            if flip_d:
                h = (-h) % 360.0
            f["heading_deg"] = h

        spawn_ticks = int(self.t["fish_spawn_ticks"])
        if self.phase_tick <= 0 or self.phase_tick % spawn_ticks != 0:
            return
        if len(self.fish) >= int(self.t["fish_max"]):
            return
        weights = self.t["fish_weights"]
        clearance = float(self.t["fish_spawn_clearance"])
        spawn_xs = [float(x) for x in self.t["fish_spawn_x"]]
        spawn_depths = self.t["fish_spawn_depths"]
        candidates = {}
        for kind in sorted(weights):
            if float(weights[kind]) <= 0:
                continue
            pts = [
                [x, float(d)]
                for x in spawn_xs
                for d in spawn_depths.get(kind, ())
                if all(math.dist((x, float(d)), f["pos"]) > clearance for f in self.fish)
            ]
            if pts:
                candidates[kind] = pts
        if not candidates:
            return
        spawn_rng = self.rng.get("fish_spawn")
        valid_kinds = sorted(candidates)
        raw_w = [float(weights[k]) for k in valid_kinds]
        total_w = sum(raw_w)
        norm_w = [w / total_w for w in raw_w]
        kind = spawn_rng.choices(valid_kinds, weights=norm_w, k=1)[0]
        pos = list(spawn_rng.choice(candidates[kind]))
        heading = spawn_rng.uniform(0.0, 360.0)
        fid = self.ids.new("F")
        self.fish.append({"id": fid, "kind": kind, "pos": pos, "heading_deg": heading, "age_ticks": 0})
        events.append(("fish_spawned", {"id": fid, "kind": kind, "pos": list(pos)}))
