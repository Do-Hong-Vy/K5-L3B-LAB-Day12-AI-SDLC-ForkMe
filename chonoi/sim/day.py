"""Vòng ngày (`--mode day`, Ticket-02 mục 2, 4.2–4.5): gather → quan → shop, lặp 1..N Ngày.

Đổi pha (mục 4.5):
  dựng Ngày:   day_start → day_plan → phase_start(gather)                     (cùng tick)
  gather_end → dựng quán với kho bàn giao trong bộ nhớ → phase_start(quan)     (cùng tick, kể cả ngất)
  quan_end   → dựng Shop → phase_start(shop)                                   (cùng tick)
  shop_end   → days_completed + 1 → kết thúc (days_complete) hoặc dựng Ngày kế (cùng tick)
Pha mới chạy gameplay từ bước sau. Event kết thúc mang pha cũ; vỏ event có `day`.

Xuyên Ngày giữ: money, earned, reputation, upgrades (cấp đã mua). Cấp đã mua chỉ chép sang active_upgrades
khi dựng Ngày mới. Mỗi Ngày: Máu/oxy đầy theo cấp đang áp dụng, giỏ mới, kho dư bỏ sau Shop.
Id khách không nối tiếp qua Ngày (clarify #14): mỗi pha một IdAllocator mới.
Mọi số liệu đọc từ tuning (game.contract.json): day_plan, shop.
"""

import copy

from ..ids import IdAllocator
from .gather import GatherSim
from .quan import QuanSim

UPGRADE_FIELD = {"oxygen": ("gather", "oxygen_max_s"), "hp": ("gather", "hp_max")}


class ShopPhase:
    """Shop cuối Ngày: một `buy` mỗi bước rồi tới cạnh `shop_done`; tự đóng sau `max_ticks` bước hoạt động."""

    mode = "day"
    phase = "shop"

    def __init__(self, tuning, day_sim, leftover_stock):
        self.t = tuning["shop"]
        self.day = day_sim
        self.stock = dict(leftover_stock)
        self.time_left_ticks = int(self.t["max_ticks"])
        self.done = False

    def snapshot(self) -> dict:
        return {"stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0}}

    def step(self, inp):
        events = []
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        if inp.buy is not None:
            self._buy(inp.buy, events)
        if inp.pressed("shop_done"):
            self.done = True
            events.append(("shop_end", {"reason": "done"}))
        elif self.time_left_ticks == 0:
            self.done = True
            events.append(("shop_end", {"reason": "time"}))
        return events

    def _buy(self, action, events):
        levels = self.t["upgrades"].get(action)
        if levels is None:
            events.append(("buy_failed", {"action": action, "reason": "unknown"}))
            return
        nxt = self.day.upgrades.get(action, 0) + 1
        lv = next((u for u in levels if u["level"] == nxt), None)
        if lv is None:
            events.append(("buy_failed", {"action": action, "reason": "max_level"}))
            return
        if self.day.money < lv["price"]:  # đủ đúng giá vẫn mua được
            events.append(("buy_failed", {"action": action, "reason": "funds"}))
            return
        self.day.money -= lv["price"]  # trừ money, giữ earned và điểm
        self.day.upgrades[action] = nxt
        events.append(("bought", {"upgrade": action, "level": nxt, "price": lv["price"], "money": self.day.money}))


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, streams, days=1):
        self.tuning = tuning
        self.scenario = scenario
        self.rng = streams
        self.days = days
        d = scenario.get("day", {})
        self.money = d.get("money", 0)
        self.earned = d.get("earned", 0)
        self.reputation = d.get("reputation", tuning["quan"]["reputation_initial"])
        self.upgrades = dict(d.get("upgrades", {}))
        self.active_upgrades = {}
        self.plan = self._plan(d.get("day_plan", []))
        self.days_completed = 0
        self.day = 0
        self.cur = None
        self.phase = "gather"
        self.phase_tick = 0
        self.done = False
        self.reason = None
        self.pending = []  # event dựng Ngày đầu, runner ghi ở tick 0
        self._start_day(self.pending)

    # --- kế hoạch -------------------------------------------------------------
    def _plan(self, overrides):
        base = {p["day"]: copy.deepcopy(p) for p in self.tuning["day_plan"]}
        for o in overrides:  # scenario day.day_plan ghi đè theo số Ngày; ingredients tính lại từ dishes
            base[o["day"]] = {"day": o["day"], "dishes": dict(o["dishes"]),
                              "ingredients": self._ingredients(o["dishes"])}
        return base

    def _ingredients(self, dishes):
        need = {}
        for dish, n in dishes.items():
            for k, q in self.tuning["menu"][dish]["recipe"].items():
                need[k] = need.get(k, 0) + q * n
        return need

    def plan_of(self, day):
        """Kế hoạch Ngày `day`; D1–D5 lặp lại cho Ngày 6+ (Ticket-04 soak)."""
        n = len(self.tuning["day_plan"])
        return self.plan[((day - 1) % n) + 1]

    # --- dựng pha ---------------------------------------------------------------
    def _day_tuning(self):
        t = copy.deepcopy(self.tuning)
        for up, level in self.active_upgrades.items():
            block, field = UPGRADE_FIELD[up]
            lv = next(u for u in self.tuning["shop"]["upgrades"][up] if u["level"] == level)
            t[block][field] = lv[field]
        return t

    def _ev(self, events, name, data, phase=None, day=None):
        events.append((name, data, phase or self.phase, day or self.day))

    def _start_day(self, events):
        self.day += 1
        self.active_upgrades = dict(self.upgrades)
        self.day_tuning = self._day_tuning()
        self.phase = "gather"
        self.phase_tick = 0
        self.cur = GatherSim(self.day_tuning, copy.deepcopy(self.scenario.get("gather", {})), self.rng, IdAllocator())
        self._sync_into(self.cur)
        plan = self.plan_of(self.day)
        self._ev(events, "day_start", {})
        self._ev(events, "day_plan", {"dishes": dict(plan["dishes"]), "ingredients": dict(plan["ingredients"])})
        self._ev(events, "phase_start", {})

    def _start_quan(self, events, items):
        self.phase = "quan"
        self.phase_tick = 0
        plan = self.plan_of(self.day)
        self.cur = QuanSim(self.day_tuning, copy.deepcopy(self.scenario.get("quan", {})), self.rng, IdAllocator(),
                           inventory=dict(items), dish_ids=list(plan["dishes"]))
        self._sync_into(self.cur)
        self._ev(events, "phase_start", {})

    def _start_shop(self, events):
        self.phase = "shop"
        self.phase_tick = 0
        self.cur = ShopPhase(self.tuning, self, self.cur.stock)
        self._ev(events, "phase_start", {})

    def _sync_into(self, sim):
        sim.money, sim.earned, sim.reputation = self.money, self.earned, self.reputation

    def _sync_from(self, sim):
        self.money, self.earned, self.reputation = sim.money, sim.earned, sim.reputation

    # --- giao diện cho runner ---------------------------------------------------
    @property
    def time_left_ticks(self):
        return self.cur.time_left_ticks

    def take_pending(self):
        ev, self.pending = self.pending, []
        return ev

    def snapshot(self) -> dict:
        snap = {"day": self.day,
                "day_plan": {"dishes": dict(self.plan_of(self.day)["dishes"]),
                             "ingredients": dict(self.plan_of(self.day)["ingredients"])},
                "upgrades": dict(sorted(self.upgrades.items())),
                "active_upgrades": dict(sorted(self.active_upgrades.items()))}
        snap.update(self.cur.snapshot())
        return snap

    def step(self, inp):
        events = []
        self.phase_tick += 1
        old_phase, sim = self.phase, self.cur
        for name, data in sim.step(inp):
            self._ev(events, name, data, phase=old_phase)
        if self.phase != "shop":
            self._sync_from(sim)
        if not sim.done:
            return events
        if old_phase == "gather":
            self._start_quan(events, sim.inventory_items())
        elif old_phase == "quan":
            self._start_shop(events)
        else:
            self.days_completed += 1
            if self.days_completed >= self.days:
                self.done = True
                self.reason = "days_complete"
            else:
                self._start_day(events)
        return events
