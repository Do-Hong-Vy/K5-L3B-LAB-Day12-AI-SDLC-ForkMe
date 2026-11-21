"""Soak headless (Ticket-04 mục 2) — AC-P4-02: soak_cmd chạy N Ngày, tất định, không crash."""

import json
import os
import shlex
import subprocess
import unittest

from helpers import ROOT, Workdir

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    SOAK = shlex.split(json.load(f)["soak_cmd"])


def run_soak(w, name, seed, days):
    out = w.path(name)
    p = subprocess.run([*SOAK, "--seed", str(seed), "--days", str(days), "--out", out], cwd=ROOT,
                       capture_output=True, text=True)
    return p.returncode, (json.load(open(out, encoding="utf-8")) if p.returncode == 0 else p.stderr)


class Soak(unittest.TestCase):
    def test_10_ngay_khong_crash_va_tat_dinh(self):
        with Workdir() as w:
            code, a = run_soak(w, "a.json", 7, 10)
            self.assertEqual(code, 0, a)
            self.assertEqual(set(a), {"days", "days_completed", "crashes", "results", "duration_s"})
            self.assertEqual((a["days"], a["days_completed"], a["crashes"]), (10, 10, 0))
            self.assertEqual([r["day"] for r in a["results"]], list(range(1, 11)))
            self.assertTrue(all(set(r) == {"day", "earned", "reputation", "score"} for r in a["results"]))
            _, b = run_soak(w, "b.json", 7, 10)
            a.pop("duration_s"), b.pop("duration_s")
            self.assertEqual(a, b)

    def test_days_sai_ma_2(self):
        with Workdir() as w:
            self.assertEqual(run_soak(w, "x.json", 7, 0)[0], 2)


if __name__ == "__main__":
    unittest.main()
