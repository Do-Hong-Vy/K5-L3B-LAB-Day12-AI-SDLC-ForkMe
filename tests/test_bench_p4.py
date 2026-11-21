"""Benchmark có render (Ticket-04 mục 1) — AC-P4-01: bench_cmd tạo bench.json đúng 5 trường, contract v1.3."""

import json
import math
import os
import shlex
import subprocess
import unittest

from helpers import ROOT, Workdir

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    C = json.load(f)


class Bench(unittest.TestCase):
    def test_contract_13_khai_lenh(self):
        self.assertEqual(C["contract_version"], "1.3")
        self.assertTrue(C["bench_cmd"].strip() and C["soak_cmd"].strip())

    def test_bench_json_dung_cau_truc(self):
        with Workdir() as w:
            out = w.path("bench.json")
            p = subprocess.run([*shlex.split(C["bench_cmd"]), "--seed", "42", "--duration", "1", "--out", out],
                               cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(p.returncode, 0, p.stderr)
            b = json.load(open(out, encoding="utf-8"))
            self.assertEqual(set(b), {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"})
            self.assertGreater(b["frames"], 0)
            self.assertTrue(math.isclose(b["avg_fps"], b["frames"] / b["measured_s"], rel_tol=0.01))
            self.assertLessEqual(b["p1_low_fps"], b["avg_fps"] + 1e-6)
            self.assertGreaterEqual(b["load_ms"], 0)


if __name__ == "__main__":
    unittest.main()
