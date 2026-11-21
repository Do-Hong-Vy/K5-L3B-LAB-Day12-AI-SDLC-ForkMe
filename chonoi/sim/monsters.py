"""Thủy quái buổi sáng — Cá Sấu Năm Chèo (Ticket-02 mục 1.2, 4.3–4.5). Lát L2: Nguyenquoctoan0310.

Tách khỏi `gather.py` để làm song song với L1 (cá bơi). GatherSim ghép bằng 3 điểm:
    __init__ : self.monsters = MonsterSystem(t, scenario.get("monsters"), day)
    step     : sau bơi/oxy/ngạt, trước tương tác ->  if self.monsters.step(self, events): return events
    snapshot : "monsters": self.monsters.snapshot()

Luật một bước (theo id quái):
  patrol  : bơi `patrol_speed` tới waypoints[target_idx]; tới nơi thì đổi mục tiêu cho bước sau.
            Người chơi ở d >= depths[0] và cách <= detect_radius -> chase ngay bước này.
  chase   : bơi `chase_speed` về phía người chơi; cách > exit_radius hoặc người chơi lên d < depths[0] -> patrol.
  recoil  : lùi theo recoil_dir mỗi bước recoil_dist / recoil_ticks (trước chặn mép), không gây hit;
            hết timer -> patrol, xét phát hiện/chạm từ bước kế.
  Chặn quái trong biên map (x) và dải độ sâu của loài (d).
Sau khi di chuyển: tối đa MỘT hit — quái gần nhất (hòa id) trong hit_radius, người chơi d >= depths[0], hết bất tử.
  hit: −1 Máu, bỏ floor(n × loss_ratio) món theo LIFO, bất tử invuln_ticks, quái vào recoil từ bước sau.
  Máu 0 -> faint(cause monster, lost = phần giỏ còn lại) rồi gather_end(fainted).
Số liệu chỉ đọc từ tuning; không dùng ngẫu nhiên.
"""

import math

from ..ids import id_key, sort_by_id

TICK = 60.0
EPS = 1e-9
STATES = ("patrol", "chase", "recoil")


def _unit(dx, dd):
    n = math.hypot(dx, dd)
    if n == 0:
        return [1.0, 0.0]  # trùng tâm: dùng +x
    return [dx / n, dd / n]


class MonsterSystem:
    def __init__(self, gather_tuning, scenario_monsters=None, day=1):
        cfg = gather_tuning.get("monsters")
        self.enabled = cfg is not None
        self.list = []
        if not self.enabled:
            return
        self.species = cfg["species"]
        self.invuln = int(cfg["invuln_ticks"])
        self.loss_ratio = cfg["loss_ratio"]
        self.bx = gather_tuning["bounds"]["x"]
        if scenario_monsters is not None:
            src = scenario_monsters
        else:
            src = [s for s in cfg["spawns"] if s["from_day"] <= day]
        for s in src:
            state = s.get("state", "patrol")
            self.list.append({
                "id": s["id"], "kind": s["kind"],
                "pos": [float(c) for c in s["pos"]],
                "waypoints": [[float(c) for c in w] for w in s["waypoints"]],
                "target_idx": s.get("target_idx", 1),
                "state": state,
                "state_ticks_left": s.get("state_ticks_left", 0),
                "recoil_dir": list(s["recoil_dir"]) if s.get("recoil_dir") is not None else None,
            })
        self.list = sort_by_id(self.list)

    # --- giao diện cho GatherSim --------------------------------------------------
    def snapshot(self):
        return [{k: m[k] for k in ("id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left",
                                   "recoil_dir")} for m in self.list]

    def step(self, sim, events) -> bool:
        """Di chuyển quái rồi xét tối đa một hit. Trả True nếu người chơi ngất (đã phát gather_end)."""
        if not self.list:
            return False
        fresh = set()  # vừa hết recoil bước này: chưa xét chạm
        for m in self.list:
            if self._move(m, sim.pos):
                fresh.add(m["id"])
        if sim.invuln_ticks > 0:
            return False
        best, best_key = None, None
        for m in self.list:
            if m["state"] == "recoil" or m["id"] in fresh:
                continue
            sp = self.species[m["kind"]]
            if sim.pos[1] < sp["depths"][0]:
                continue
            dist = math.dist(m["pos"], sim.pos)
            if dist <= sp["hit_radius"]:
                key = (dist, id_key(m["id"]))
                if best_key is None or key < best_key:
                    best, best_key = m, key
        if best is None:
            return False
        return self._hit(best, sim, events)

    # --- nội bộ -----------------------------------------------------------------
    def _clamp(self, m):
        lo, hi = self.species[m["kind"]]["depths"]
        m["pos"][0] = min(max(m["pos"][0], self.bx[0]), self.bx[1])
        m["pos"][1] = min(max(m["pos"][1], lo), hi)

    def _toward(self, m, target, speed):
        """Bơi tới target với tốc độ speed (m/s), không vượt quá. Trả True nếu tới nơi."""
        dx, dd = target[0] - m["pos"][0], target[1] - m["pos"][1]
        dist = math.hypot(dx, dd)
        step = speed / TICK
        if dist <= step + EPS:  # EPS: cộng dồn k × (1/60) lệch ~1e-13, không để tới nơi trễ 1 tick
            m["pos"] = [float(target[0]), float(target[1])]
            return True
        m["pos"] = [m["pos"][0] + dx / dist * step, m["pos"][1] + dd / dist * step]
        return False

    def _move(self, m, player):
        """Cập nhật một quái. Trả True nếu vừa hết recoil (chưa xét phát hiện/chạm bước này)."""
        sp = self.species[m["kind"]]
        if m["state"] == "recoil":
            per = sp["recoil_dist"] / sp["recoil_ticks"]
            m["pos"] = [m["pos"][0] + m["recoil_dir"][0] * per, m["pos"][1] + m["recoil_dir"][1] * per]
            self._clamp(m)
            m["state_ticks_left"] -= 1
            if m["state_ticks_left"] <= 0:
                m["state"], m["state_ticks_left"], m["recoil_dir"] = "patrol", 0, None
                return True
            return False
        deep = player[1] >= sp["depths"][0]
        dist = math.dist(m["pos"], player)
        if m["state"] == "chase" and (not deep or dist > sp["exit_radius"]):
            m["state"] = "patrol"
        elif m["state"] == "patrol" and deep and dist <= sp["detect_radius"]:
            m["state"] = "chase"
        if m["state"] == "chase":
            self._toward(m, player, sp["chase_speed"])
        elif self._toward(m, m["waypoints"][m["target_idx"]], sp["patrol_speed"]):
            m["target_idx"] = 1 - m["target_idx"]
        self._clamp(m)
        return False

    def _hit(self, m, sim, events) -> bool:
        sp = self.species[m["kind"]]
        sim.hp = max(0, sim.hp - 1)
        n_lost = math.floor(len(sim.hold) * self.loss_ratio)
        lost = [sim._view(sim.hold.pop()) for _ in range(n_lost)]  # nhặt sau mất trước; v1.2 -> {id,kind,fresh}
        sim.invuln_ticks = self.invuln
        m["state"], m["state_ticks_left"] = "recoil", int(sp["recoil_ticks"])
        m["recoil_dir"] = _unit(m["pos"][0] - sim.pos[0], m["pos"][1] - sim.pos[1])
        events.append(("monster_hit", {"monster_id": m["id"], "hp": sim.hp, "lost": lost, "pos": list(sim.pos)}))
        if sim.hp <= 0:
            rest = [sim._view(h) for h in reversed(sim.hold)]
            sim.hold.clear()
            events.append(("faint", {"cause": "monster", "lost": rest, "hp": 0}))
            sim._finish("fainted", events)
            return True
        return False
