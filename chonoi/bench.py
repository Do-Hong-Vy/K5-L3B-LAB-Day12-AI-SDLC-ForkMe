"""Benchmark có render (Ticket-04 mục 1): python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json

Cảnh đo: buổi sáng lõi (độ tươi, cá bơi/sinh, Cá Sấu Năm Chèo, hiệu ứng mặc định), Út Sen đứng yên ở bến.
Mỗi khung: một bước mô phỏng 60 Hz + render phần mềm vào framebuffer RGB 1280×720 (nền sông 3 tầng độ sâu
theo dải, sóng mặt nước, nút hái, đàn cá, thủy quái, người chơi, HUD oxy/Máu/giỏ). Chỉ thư viện chuẩn Python.
Làm nóng 3 s rồi đo `--duration` s theo đồng hồ thực.

bench.json: {avg_fps, p1_low_fps, frames, measured_s, load_ms}
  avg_fps    = frames / measured_s
  p1_low_fps = 1 / (trung bình thời gian của max(1, ceil(0.01 × frames)) khung chậm nhất)
  load_ms    = mili giây từ lúc khởi chạy tới khung đầu tiên của cảnh đo
Giới hạn đã biết: đo render phần mềm của bản Python (không phải canvas trình duyệt chonoi.live).
"""

import argparse
import json
import math
import sys
import time

T_START = time.perf_counter()

W, H = 1280, 720
WARMUP_S = 3.0

from .contract import load_contract  # noqa: E402  (đo load_ms tính cả thời gian import)
from .ids import IdAllocator  # noqa: E402
from .inputs import InputState  # noqa: E402
from .rng import Streams  # noqa: E402
from .sim.gather import GatherSim  # noqa: E402

KIND_RGB = {"ca_loc": (132, 169, 85), "ca_linh": (96, 165, 250), "ca_keo": (52, 211, 153),
            "bong_dien_dien": (250, 204, 21), "bong_sung": (244, 114, 182), "keo_neo": (163, 230, 53)}


class Framebuffer:
    """Bộ đệm RGB 1280×720; vẽ bằng gán lát bytearray (nhanh hơn từng điểm ảnh)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)

    def rect(self, x, y, w, h, rgb):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(rgb) * (x1 - x0)
        stride = self.w * 3
        for yy in range(y0, y1):
            off = yy * stride + x0 * 3
            self.buf[off:off + len(row)] = row

    def disc(self, cx, cy, r, rgb):
        r = max(1, int(r))
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - half, cy + dy, 2 * half + 1, 1, rgb)


def render(fb, sim, frame):
    g = sim.t
    X, D = g["bounds"]["x"][1], g["bounds"]["d"][1]
    sky = 90
    sx = lambda x: x / X * (W - 40) + 20  # noqa: E731
    sy = lambda d: sky + d / D * (H - sky - 80)  # noqa: E731
    fb.rect(0, 0, W, sky, (253, 186, 116))  # bình minh
    for i, (top, bot, rgb) in enumerate(((0, 10, (56, 189, 248)), (10, 20, (14, 116, 144)), (20, D, (12, 74, 110)))):
        fb.rect(0, sy(top), W, sy(bot) - sy(top) + 1, rgb)
    for k in range(0, W, 16):  # sóng mặt nước động
        fb.rect(k, sky - 3 + 3 * math.sin(frame * 0.12 + k * 0.05), 10, 3, (224, 242, 254))
    for n in sim.nodes:
        fb.disc(sx(n["pos"][0]), sy(0) - 6, 7 if n["regrow_ticks"] == 0 else 4, KIND_RGB[n["kind"]])
    for f in sim.fish:
        cx, cy = sx(f["pos"][0]), sy(f["pos"][1])
        fb.disc(cx, cy, 9, KIND_RGB[f["kind"]])
        fb.rect(cx - 16, cy - 5, 8, 10, KIND_RGB[f["kind"]])
    for m in (sim.monsters.list if hasattr(sim.monsters, "list") else getattr(sim.monsters, "monsters", [])):
        fb.rect(sx(m["pos"][0]) - 24, sy(m["pos"][1]) - 7, 48, 14, (77, 124, 15))
    px, py = sx(sim.pos[0]), sy(sim.pos[1])
    fb.disc(px, py, 12, (249, 115, 22))
    fb.rect(20, H - 60, 300 * sim.oxygen_ticks / max(1, sim.oxygen_max), 14, (56, 189, 248))  # HUD oxy
    for i in range(sim.hp):
        fb.disc(340 + i * 24, H - 53, 8, (239, 68, 68))
    for i, h in enumerate(sim.hold):
        fb.rect(20 + i * 30, H - 36, 26, 20, KIND_RGB[h["kind"] if isinstance(h, dict) else h])


def bench(seed: int, duration: float) -> dict:
    tuning = load_contract()["tuning"]
    sim = GatherSim(tuning, {}, Streams(seed), IdAllocator())  # Út Sen đứng yên ở bến (vị trí xuất phát)
    idle = InputState((0.0, 0.0), {}, set())
    fb = Framebuffer(W, H)
    frame, load_ms = 0, None

    def one():
        nonlocal sim, frame
        if sim.done:  # hết ca 180 s: dựng lại cảnh để đo liên tục
            sim = GatherSim(tuning, {}, Streams(seed), IdAllocator())
        sim.step(idle)
        render(fb, sim, frame)
        frame += 1

    t_warm = time.perf_counter()
    while time.perf_counter() - t_warm < WARMUP_S:
        one()
        if load_ms is None:
            load_ms = round((time.perf_counter() - T_START) * 1000)
    times = []
    t0 = time.perf_counter()
    last = t0
    while last - t0 < duration:
        one()
        now = time.perf_counter()
        times.append(now - last)
        last = now
    measured = last - t0
    n = len(times)
    worst = sorted(times, reverse=True)[:max(1, math.ceil(0.01 * n))]
    return {"avg_fps": round(n / measured, 2), "p1_low_fps": round(1 / (sum(worst) / len(worst)), 2),
            "frames": n, "measured_s": round(measured, 3), "load_ms": load_ms}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.bench")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if not (a.duration > 0):
        sys.stderr.write("đầu vào sai: --duration phải > 0\n")
        return 2
    out = bench(a.seed, a.duration)
    try:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out, f)
    except OSError as e:
        sys.stderr.write(f"lỗi ghi: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
