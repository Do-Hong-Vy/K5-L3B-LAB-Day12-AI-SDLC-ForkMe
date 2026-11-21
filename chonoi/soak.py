"""Soak headless (Ticket-04 mục 2): python3 -m chonoi.soak --seed 7 --days 10 --out soak.json

Chạy N Ngày trong MỘT tiến trình bằng bot tất định (clarify #20): mỗi Ngày gather không input tới hết giờ,
quán chạy hết ca, Shop tự đóng sau max_ticks — đi qua gather → quan → shop. D1–D5 lặp ở Ngày 6+ (DaySim.plan_of).
Tiền, earned, uy tín, cấp nâng cấp, số Ngày tiếp tục xuyên suốt. Không ghi bảng xếp hạng.

soak.json: {days, days_completed, crashes, results:[{day,earned,reputation,score}], duration_s}.
Trường gameplay tất định theo seed; chỉ duration_s là đồng hồ thực (bỏ khi so).
"""

import argparse
import json
import math
import sys
import time
import traceback

from .contract import load_contract
from .errors import BadInput
from .inputs import InputPlayer
from .runner import Session


def soak(seed: int, days: int) -> dict:
    t0 = time.perf_counter()
    tuning = load_contract()["tuning"]
    mult = tuning["score"]["reputation_multiplier"]
    results, crashes, completed = [], 0, 0
    try:
        sess = Session("day", tuning, {}, seed, days=days)
        sess.initial_rows()
        bot = InputPlayer([])  # bot tất định: không input
        while not sess.done:
            for row in sess.step(bot.advance(sess.tick)):
                if row["name"] == "shop_end":
                    sim = sess.sim
                    results.append({"day": row["day"], "earned": sim.earned, "reputation": sim.reputation,
                                    "score": sim.earned + mult * math.floor(sim.reputation)})
        completed = sess.sim.days_completed
    except Exception:  # đếm crash thay vì làm sập runner lớp
        crashes += 1
        traceback.print_exc()
    return {"days": days, "days_completed": completed, "crashes": crashes, "results": results,
            "duration_s": round(time.perf_counter() - t0, 3)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.soak")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if a.days < 1:
        sys.stderr.write("đầu vào sai: --days phải >= 1\n")
        return 2
    try:
        out = soak(a.seed, a.days)
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    try:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
    except OSError as e:
        sys.stderr.write(f"lỗi ghi: {e}\n")
        return 1
    return 0 if out["crashes"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
