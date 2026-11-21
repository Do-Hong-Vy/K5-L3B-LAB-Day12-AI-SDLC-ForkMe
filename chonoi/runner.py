"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.

`Session` là API bước tick gọn dùng chung cho headless (`run`) và cửa sổ chơi trực tiếp (`chonoi.live`):
cả hai chạy CÙNG một lớp sim, không nhân đôi logic.
"""

import math

from .ids import IdAllocator
from .inputs import InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.day import DaySim
from .sim.gather import GatherSim
from .sim.quan import QuanSim


def build_sim(mode, tuning, scenario, seed, inventory, kitchen=None, days=1):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    if mode == "day":  # v1.1 (Ticket-02): vòng ngày gather -> quan -> shop
        return DaySim(tuning, scenario, streams, days=days)
    # kitchen: sáng tạo 'bếp nhiều section' — chỉ chonoi.live truyền vào; headless luôn None (Test Contract).
    return QuanSim(tuning, scenario, streams, ids, inventory=inventory, kitchen=kitchen)


def _common(sim, tick, sim_tick, phase_tick, tuning, state):
    mult = tuning["score"]["reputation_multiplier"]
    return {
        "type": "snapshot", "tick": tick, "sim_tick": sim_tick, "mode": sim.mode, "phase": sim.phase,
        "phase_tick": phase_tick, "state": state, "time_left_ticks": sim.time_left_ticks,
        "money": sim.money, "earned": sim.earned, "reputation": sim.reputation,
        "score": sim.earned + mult * math.floor(sim.reputation),
    }


class Session:
    """Một lượt chơi: dựng sim, bước từng tick, lấy snapshot / dòng end.

    v1.1 (Ticket-02 mục 4.2): `tick` là số bước ngoài; `sim_tick` chỉ tăng khi gameplay chạy (không pause).
    Cạnh `pause` xét trước: vào pause chỉ tăng tick ngoài và phát `paused`; còn pause thì bỏ qua mọi hành động;
    cạnh kế tiếp phát `resumed` và chạy gameplay ngay trong bước đó.
    """

    def __init__(self, mode, tuning, scenario, seed, inventory=None, kitchen=None, days=1):
        self.mode = mode
        self.tuning = tuning
        self.sim = build_sim(mode, tuning, scenario, seed, inventory, kitchen, days)
        self.tick = 0
        self.sim_tick = 0
        self.paused = False

    @property
    def done(self) -> bool:
        return self.sim.done

    def _phase_tick(self):
        return getattr(self.sim, "phase_tick", self.sim_tick) if self.mode == "day" else self.sim_tick

    def _state(self):
        return "finished" if self.sim.done else ("paused" if self.paused else "playing")

    def _row(self, name, data, phase=None, day=None):
        row = {"type": "event", "tick": self.tick, "phase": phase or self.sim.phase}
        if day is not None:
            row["day"] = day
        row.update(name=name, data=data)
        return row

    def _rows(self, events):
        out = []
        for e in events:
            if len(e) == 4:  # day: (name, data, phase, day)
                out.append(self._row(e[0], e[1], e[2], e[3]))
            else:
                out.append(self._row(e[0], e[1], None, getattr(self.sim, "day", None) if self.mode == "day" else None))
        return out

    def initial_rows(self) -> list:
        """Event dựng lượt ở tick 0 (day: day_start, day_plan, phase_start) — ghi trước snapshot tick 0."""
        take = getattr(self.sim, "take_pending", None)
        return self._rows(take()) if take else []

    def snapshot(self) -> dict:
        s = _common(self.sim, self.tick, self.sim_tick, self._phase_tick(), self.tuning, self._state())
        s.update(self.sim.snapshot())
        return s

    def step(self, inp) -> list:
        """Chạy một bước với `inp` (chonoi.inputs.InputState); trả các dòng event (tick = k + 1)."""
        pre = []
        if inp.pressed("pause"):
            if not self.paused:
                self.paused = True
                self.tick += 1
                return self._rows([("paused", {})])
            self.paused = False
            pre = [("resumed", {})]
        elif self.paused:
            self.tick += 1
            return []
        events = self.sim.step(inp)
        self.tick += 1
        self.sim_tick += 1
        return self._rows(pre) + self._rows(events)

    def end_row(self) -> dict:
        sim = self.sim
        score = _common(sim, self.tick, self.sim_tick, self.sim_tick, self.tuning, "")["score"]
        row = {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": sim.mode,
               "state": "finished" if sim.done else "playing",
               "reason": sim.reason if sim.done else "tick_limit",
               "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": score}
        if self.mode == "day":
            row["days_completed"] = sim.days_completed
        return row

    def write_inventory_if_done(self, inventory_out):
        """File kho: ghi MỘT lần khi có gather_end; chưa kết thúc thì giữ nguyên file đích."""
        if self.mode == "gather" and self.sim.done and inventory_out:
            write_inventory(inventory_out, self.sim.inventory_items())


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None,
        days=1):
    sess = Session(mode, tuning, scenario, seed, inventory, days=days)
    player = InputPlayer(frames)
    w = JsonlWriter(out_path)
    try:
        for row in sess.initial_rows():
            w.write(row)
        w.write(sess.snapshot())  # tick 0: sau khi dựng scenario, trước mọi input
        last_snapped = 0
        while sess.tick < ticks and not sess.done:
            inp = player.advance(sess.tick)  # bước k đọc input có tick == k
            for row in sess.step(inp):
                w.write(row)
            if sess.tick % snapshot_every == 0 or sess.done:
                w.write(sess.snapshot())
                last_snapped = sess.tick
        if last_snapped != sess.tick:
            w.write(sess.snapshot())
        w.write(sess.end_row())
    finally:
        w.close()
    sess.write_inventory_if_done(inventory_out)
    return sess.sim
