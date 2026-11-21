"""Sáng tạo của nhóm — Bếp nhiều section (chỉ chonoi.live). Kiểm: luật sơ chế/gộp và headless KHÔNG đổi."""

import json
import os
import unittest

from helpers import ROOT, Workdir, read_jsonl, run_headless, write_json

from chonoi.creative import load_kitchen
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]
KITCHEN = load_kitchen()
SEC = {s["kind"]: s for s in KITCHEN["sections"]}
PREP = {k: int(round(v * 60)) for k, v in KITCHEN["prep_s"].items()}
IDLE = InputState((0.0, 0.0), set(), set())
PRESS = InputState((0.0, 0.0), {"interact"}, {"interact"})


def make(dish, stock, kitchen=KITCHEN):
    sc = {"stock": stock, "random_customers": False,
          "customers": [{"id": "C1", "table_id": "T1", "dish_id": dish}]}
    return QuanSim(TUNING, sc, Streams(1), IdAllocator(), kitchen=kitchen)


def at(sim, pos):
    sim.pos = [float(c) for c in pos]
    return sim


def run(sim, n, inp=IDLE):
    out = []
    for _ in range(n):
        out += sim.step(inp)
    return out


class Kitchen(unittest.TestCase):
    def test_bep_tu_choi_don_chua_so_che(self):
        sim = at(make("ca_loc_nuong_trui", {"ca_loc": 1}), TUNING["quan"]["stoves"][0]["pos"])
        self.assertEqual(sim.step(PRESS), [])  # bếp idle nhưng đơn chưa sơ chế -> bỏ lượt

    def test_so_che_roi_gop_thanh_mon(self):
        sim = at(make("canh_chua_ca_loc", {"ca_loc": 1, "bong_dien_dien": 1}), SEC["ca_loc"]["pos"])
        self.assertEqual(sim.step(PRESS), [("prep_started", {"section_id": SEC["ca_loc"]["id"], "order_id": "C1",
                                                             "kind": "ca_loc"})])
        self.assertEqual(sim.step(PRESS), [])  # section đang làm -> không nhận thêm
        at(sim, SEC["bong_dien_dien"]["pos"])
        self.assertEqual(sim.step(PRESS)[0][0], "prep_started")
        ev = run(sim, max(PREP.values()))
        self.assertEqual(sorted(e[1]["kind"] for e in ev if e[0] == "prep_done"), ["bong_dien_dien", "ca_loc"])
        self.assertEqual(sim.snapshot()["prepped"], {"C1": {"bong_dien_dien": 1, "ca_loc": 1}})
        at(sim, TUNING["quan"]["stoves"][0]["pos"])
        cs = sim.step(PRESS)
        self.assertEqual(cs[0][0], "cook_started")
        self.assertEqual(cs[0][1]["items"], ["bong_dien_dien", "ca_loc"])
        self.assertEqual(sim.snapshot()["prepped"], {})

    def test_mon_nhieu_phan_can_so_che_tung_phan(self):
        sim = at(make("lau_ca_linh_dien_dien", {"ca_linh": 3, "bong_dien_dien": 1}), SEC["ca_linh"]["pos"])
        for _ in range(3):
            self.assertEqual(sim.step(PRESS)[0][0], "prep_started")
            run(sim, PREP["ca_linh"])
        self.assertEqual(sim.step(PRESS), [])  # đủ 3 phần cá linh -> không cần thêm
        self.assertEqual(sim.snapshot()["prepped"]["C1"], {"ca_linh": 3})

    def test_section_khong_nhan_nguyen_lieu_khong_can(self):
        sim = at(make("ca_loc_nuong_trui", {"ca_loc": 1}), SEC["bong_sung"]["pos"])
        self.assertEqual(sim.step(PRESS), [])

    def test_khach_roi_huy_so_che(self):
        sim = make("ca_loc_nuong_trui", {"ca_loc": 1})
        sim.customers[0]["patience_ticks_left"] = 3
        at(sim, SEC["ca_loc"]["pos"]).step(PRESS)
        ev = run(sim, 3)
        self.assertIn("customer_left", [e[0] for e in ev])
        snap = sim.snapshot()
        self.assertEqual((snap["prepped"], snap["sections"][0]["state"]), ({}, "idle"))


class HeadlessUnchanged(unittest.TestCase):
    def test_tat_o_headless(self):
        sim = QuanSim(TUNING, {"stock": {}}, Streams(1), IdAllocator())
        self.assertNotIn("sections", sim.snapshot())
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"quan": {"stock": {"ca_loc": 1}}})
            code, err = run_headless("--mode", "quan", "--seed", "1", "--scenario", sc, "--ticks", "200",
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("q.jsonl"))
            self.assertFalse(any("sections" in r or "prepped" in r for r in rows))
            self.assertFalse(any(r.get("name", "").startswith("prep_") for r in rows))


if __name__ == "__main__":
    unittest.main()
