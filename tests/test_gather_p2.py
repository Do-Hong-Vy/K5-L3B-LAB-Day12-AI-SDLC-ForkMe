"""Kiểm thử Phase 2 cho Contract v1.1 phần gather & L1 cá bơi/sinh (AC-P2-01, 02, 03, 05)."""

import copy
import json
import math
import os
import unittest

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.inventory import KINDS, validate_items
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim
from helpers import Workdir, close, counts, events, frames, hold, read_jsonl, run_headless, snapshots, write_json


def _contract():
    return copy.deepcopy(load_contract())


class GatherContractV11Tests(unittest.TestCase):
    def test_contract_v11_gather_fields_and_standards(self):
        c = _contract()
        # v1.2 (Ticket-03) kế thừa toàn bộ khóa v1.1 của gather; chỉ số phiên bản đổi.
        self.assertIn(c["contract_version"], ("1.1", "1.2"))
        g = c["tuning"]["gather"]
        self.assertEqual(g["fish_yield"], {"ca_linh": 3, "ca_loc": 1, "ca_keo": 2})
        self.assertEqual(len(g["nodes"]), 6)
        self.assertEqual(
            [(n["id"], n["kind"], n["pos"]) for n in g["nodes"]],
            [
                ("N1", "bong_dien_dien", [12, 0]),
                ("N2", "bong_dien_dien", [28, 0]),
                ("N3", "bong_sung", [44, 0]),
                ("N4", "bong_sung", [60, 0]),
                ("N5", "keo_neo", [76, 0]),
                ("N6", "keo_neo", [90, 0]),
            ],
        )
        self.assertEqual(len(g["fish_initial"]), 8)
        pts = {tuple(f["pos"]) for f in g["fish_initial"]}
        self.assertEqual(len(pts), 8)
        self.assertEqual(g["fish_speed"], 1.5)
        self.assertEqual(g["fish_turn_ticks"], 120)
        self.assertEqual(g["fish_max"], 12)
        self.assertEqual(g["fish_spawn_ticks"], 360)
        self.assertEqual(g["fish_spawn_clearance"], 1.0)
        self.assertEqual(g["fish_x"], [4, 96])
        self.assertEqual(g["fish_depths"], {"ca_linh": [3, 12], "ca_loc": [8, 20], "ca_keo": [22, 28]})
        self.assertEqual(g["fish_weights"], {"ca_linh": 0.4, "ca_loc": 0.3, "ca_keo": 0.3})
        m = g["monsters"]
        self.assertEqual(m["invuln_ticks"], 90)
        self.assertEqual(m["loss_ratio"], 0.5)
        self.assertIn("ca_sau", m["species"])
        self.assertEqual([(s["id"], s["from_day"]) for s in m["spawns"]], [("M1", 1), ("M2", 3)])

    def test_contract_and_scenario_reject_invalid_v11_gather(self):
        c = _contract()
        t_bad_fish = copy.deepcopy(c["tuning"])
        t_bad_fish["gather"]["fish_initial"].pop()
        with self.assertRaises(BadInput):
            validate_tuning(t_bad_fish)

        t_bad_mon = copy.deepcopy(c["tuning"])
        t_bad_mon["gather"]["monsters"]["spawns"][0]["from_day"] = 9
        with self.assertRaises(BadInput):
            validate_tuning(t_bad_mon)

        self.assertEqual(validate_items({"ca_keo": 2, "keo_neo": 1}), {"ca_keo": 2, "keo_neo": 1})
        self.assertEqual(set(KINDS), {"ca_loc", "ca_linh", "ca_keo", "bong_dien_dien", "bong_sung", "keo_neo"})

        with Workdir() as w:
            out = w.path("out.jsonl")
            for bad_fish in (
                {"id": "F1", "kind": "ca_keo", "pos": [20, 24], "age_ticks": -1},
                {"id": "F1", "kind": "ca_keo", "pos": [20, 24], "age_ticks": True},
                {"id": "F1", "kind": "ca_keo", "pos": [20, 24], "extra": 1},
            ):
                sc = write_json(w.path("sc.json"), {"gather": {"fish": [bad_fish]}})
                code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--scenario", sc, "--out", out)
                self.assertEqual(code, 2, bad_fish)
                self.assertFalse(os.path.exists(out))

    def test_harvest_keo_neo_and_catch_ca_keo_handover(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [76, 0]},
                    "fish": [{"id": "F1", "kind": "ca_keo", "pos": [76, 0.8]}],
                    "random_fish": False,
                }
            })
            # Tick 0 hái N5 (keo_neo) tại [76, 0]
            inp = write_json(w.path("in1.json"), frames({"tick": 0, "interact": True}, {"tick": 1, "interact": False}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "2", "--scenario", sc,
                                     "--inputs", inp, "--out", w.path("g1.jsonl"))
            self.assertEqual(code, 0, err)
            ev = events(read_jsonl(w.path("g1.jsonl")), "gather")
            self.assertEqual(ev[0]["data"], {"node_id": "N5", "kind": "keo_neo", "amount": 1})

            sc2 = write_json(w.path("sc2.json"), {
                "gather": {
                    "player": {"pos": [30, 24]},
                    "hold": hold(["keo_neo"]),
                    "fish": [{"id": "F7", "kind": "ca_keo", "pos": [30, 24]}],
                    "time_left_ticks": 1,
                    "random_fish": False,
                }
            })
            inp2 = write_json(w.path("in2.json"), frames({"tick": 0, "catch": True}))
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--scenario", sc2,
                                     "--inputs", inp2, "--inventory-out", inv, "--out", w.path("g2.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("g2.jsonl"))
            self.assertEqual(events(rows, "fish_caught")[0]["data"], {"fish_id": "F7", "kind": "ca_keo", "yield": 2})
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(counts(json.load(f)["items"]), {"ca_keo": 2, "keo_neo": 1})


class FishSwimmingTests(unittest.TestCase):
    def test_fish_speed_1_5_and_random_fish_false_stationary(self):
        with Workdir() as w:
            sc_move = write_json(w.path("move.json"), {
                "gather": {
                    "fish": [{"id": "F1", "kind": "ca_linh", "pos": [15, 5], "heading_deg": 0}],
                    "random_fish": True,
                }
            })
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "60",
                                     "--scenario", sc_move, "--snapshot-every", "60", "--out", w.path("m.jsonl"))
            self.assertEqual(code, 0, err)
            f = snapshots(read_jsonl(w.path("m.jsonl")))[-1]["fish"][0]
            self.assertTrue(close(f["pos"][0], 16.5, 1e-6), f)
            self.assertTrue(close(f["pos"][1], 5.0, 1e-6), f)
            self.assertEqual(f["heading_deg"], 0)

            sc_still = write_json(w.path("still.json"), {
                "gather": {
                    "fish": [{"id": "F1", "kind": "ca_linh", "pos": [15, 5], "heading_deg": 35}],
                    "random_fish": False,
                }
            })
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "400",
                                     "--scenario", sc_still, "--out", w.path("s.jsonl"))
            self.assertEqual(code, 0, err)
            rows_still = read_jsonl(w.path("s.jsonl"))
            self.assertEqual(events(rows_still, "fish_spawned"), [])
            f_still = snapshots(rows_still)[-1]["fish"][0]
            self.assertEqual(f_still["pos"], [15.0, 5.0])
            self.assertEqual(f_still["heading_deg"], 35.0)

    def test_fish_turns_at_age_120_before_moving(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "fish": [{"id": "F1", "kind": "ca_linh", "pos": [50, 7], "heading_deg": 0, "age_ticks": 118}],
                    "random_fish": True,
                }
            })
            code, err = run_headless("--mode", "gather", "--seed", "42", "--ticks", "3",
                                     "--scenario", sc, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            snaps = {s["tick"]: s["fish"][0] for s in snapshots(read_jsonl(w.path("o.jsonl")))}
            # tick 1: age 118->119 (chưa đổi hướng), đi +0.025 trên x
            self.assertEqual(snaps[1]["heading_deg"], 0.0)
            self.assertTrue(close(snaps[1]["pos"][0], 50.025, 1e-9))
            # tick 2: age 119->120 -> đổi hướng TRƯỚC khi đi bước này (JSONL làm tròn 3 chữ số thập phân)
            expected_h = Streams(42).get("fish_turn").uniform(0.0, 360.0)
            self.assertEqual(snaps[2]["heading_deg"], round(expected_h, 3))
            step = 1.5 / 60.0
            self.assertEqual(snaps[2]["pos"][0], round(50.025 + step * math.cos(math.radians(expected_h)), 3))
            self.assertEqual(snaps[2]["pos"][1], round(7.0 + step * math.sin(math.radians(expected_h)), 3))
            # tick 3: age 120->121, giữ hướng mới
            self.assertEqual(snaps[3]["heading_deg"], round(expected_h, 3))

    def test_fish_edge_and_corner_reflection(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "fish": [
                        # Chạm mép phải x=96
                        {"id": "F1", "kind": "ca_linh", "pos": [95.99, 7], "heading_deg": 0},
                        # Chạm mép trên d=3 của ca_linh
                        {"id": "F2", "kind": "ca_linh", "pos": [20, 3.01], "heading_deg": 270},
                        # Chạm góc (x=4, d=22) của ca_keo
                        {"id": "F3", "kind": "ca_keo", "pos": [4.01, 22.01], "heading_deg": 225},
                    ],
                    "random_fish": True,
                }
            })
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1",
                                     "--scenario", sc, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            by_id = {f["id"]: f for f in snapshots(read_jsonl(w.path("o.jsonl")))[-1]["fish"]}
            # F1: 95.99 + 0.025 = 96.015 -> phản xạ 95.985, hướng 0 -> 180
            self.assertEqual(by_id["F1"]["pos"][0], 95.985)
            self.assertEqual(by_id["F1"]["pos"][1], 7.0)
            self.assertEqual(by_id["F1"]["heading_deg"], 180.0)
            # F2: 3.01 - 0.025 = 2.985 -> phản xạ 3.015, hướng 270 -> 90
            self.assertEqual(by_id["F2"]["pos"][1], 3.015)
            self.assertEqual(by_id["F2"]["heading_deg"], 90.0)
            # F3 chạm cả hai mép góc: đảo cả x lẫn d, hướng 225 -> 45
            step_comp = (1.5 / 60.0) * math.cos(math.radians(45.0))
            self.assertEqual(by_id["F3"]["pos"][0], round(4.0 + abs(4.01 - step_comp - 4.0), 3))
            self.assertEqual(by_id["F3"]["pos"][1], round(22.0 + abs(22.01 - step_comp - 22.0), 3))
            self.assertEqual(by_id["F3"]["heading_deg"], 45.0)


class FishSpawnAndOrderTests(unittest.TestCase):
    def test_spawn_at_360_cap_12_and_new_fish_swims_next_step(self):
        with Workdir() as w:
            code, err = run_headless("--mode", "gather", "--seed", "7", "--ticks", "361",
                                     "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            spawned = events(rows, "fish_spawned")
            self.assertEqual(len(spawned), 1)
            self.assertEqual(spawned[0]["tick"], 360)
            self.assertEqual(spawned[0]["data"]["id"], "F9")
            snaps = {s["tick"]: s["fish"] for s in snapshots(rows)}
            self.assertEqual(len(snaps[359]), 8)
            self.assertEqual(len(snaps[360]), 9)
            f9_at_360 = [f for f in snaps[360] if f["id"] == "F9"][0]
            f9_at_361 = [f for f in snaps[361] if f["id"] == "F9"][0]
            self.assertEqual(f9_at_360["pos"], spawned[0]["data"]["pos"])
            # Mới sinh ở tick 360 tham gia bơi từ bước sau (tick 361); JSONL làm tròn 3 chữ số
            self.assertAlmostEqual(math.dist(f9_at_360["pos"], f9_at_361["pos"]), 1.5 / 60.0, delta=0.0015)

            # Trần 12 đàn khi chạy đủ lâu (5 * 360 = 1800)
            code, err = run_headless("--mode", "gather", "--seed", "7", "--ticks", "1805",
                                     "--snapshot-every", "360", "--out", w.path("cap.jsonl"))
            self.assertEqual(code, 0, err)
            cap_rows = read_jsonl(w.path("cap.jsonl"))
            self.assertEqual(len(events(cap_rows, "fish_spawned")), 4)  # 8 + 4 = 12
            self.assertEqual(len(snapshots(cap_rows)[-1]["fish"]), 12)

    def test_spawn_clearance_and_weight_normalization_and_skip_when_full(self):
        t = _contract()["tuning"]
        custom = copy.deepcopy(t)
        # Chỉ còn 2 điểm sinh: ca_linh ở [15, 5], ca_loc ở [30, 10]
        custom["gather"].update({
            "fish_spawn_ticks": 1,
            "fish_spawn_x": [15, 30],
            "fish_spawn_depths": {"ca_linh": [5], "ca_loc": [10], "ca_keo": [24]},
            "fish_max": 12,
        })
        # Đặt cá chặn điểm [30, 10] đúng clearance = 1.0 m (<= 1.0 không hợp lệ) và chặn ca_keo [15, 24], [30, 24];
        # còn duy nhất [15, 5] của ca_linh cách > 1.0 m
        custom["gather"]["fish_spawn_x"] = [15]
        custom["gather"]["fish_spawn_depths"] = {"ca_linh": [5], "ca_loc": [10], "ca_keo": [24]}
        # Chú ý cá sẽ bơi ở tick 1 TRƯỚC khi sinh: đặt heading=90/0 chậm hoặc clearance=1.0 -> đặt cá ở chính tâm
        sc = {
            "fish": [
                {"id": "F1", "kind": "ca_loc", "pos": [15, 10], "heading_deg": 0},   # khoảng cách tới [15,10] = 0.025 <= 1.0
                {"id": "F2", "kind": "ca_keo", "pos": [15, 24], "heading_deg": 0},   # chặn ca_keo
            ]
        }
        sim = GatherSim(custom, sc, Streams(3), IdAllocator())
        ev = sim.step(InputState((0.0, 0.0), {}, set()))
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0][0], "fish_spawned")
        self.assertEqual(ev[0][1]["kind"], "ca_linh")
        self.assertEqual(ev[0][1]["id"], "F3")
        self.assertEqual(ev[0][1]["pos"], [15.0, 5.0])

        # Chặn nốt [15, 5] -> hết điểm hợp lệ -> bỏ lượt không sinh thêm
        sc_blocked = {
            "fish": [
                {"id": "F1", "kind": "ca_linh", "pos": [15, 5], "heading_deg": 0},
                {"id": "F2", "kind": "ca_loc", "pos": [15, 10], "heading_deg": 0},
                {"id": "F3", "kind": "ca_keo", "pos": [15, 24], "heading_deg": 0},
            ]
        }
        sim2 = GatherSim(custom, sc_blocked, Streams(3), IdAllocator())
        self.assertEqual(sim2.step(InputState((0.0, 0.0), {}, set())), [])
        self.assertEqual(len(sim2.fish), 3)

    def test_step_order_catch_before_swim_and_no_swim_on_time_end(self):
        with Workdir() as w:
            # Cá ở [21.99, 10] bơi +x (+0.025 -> [22.015, 10]), người chơi [20, 10] bấm catch -> bắt ĐƯỢC trước khi cá bơi!
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [20, 10]},
                    "fish": [{"id": "F1", "kind": "ca_loc", "pos": [21.99, 10], "heading_deg": 0}],
                    "random_fish": True,
                }
            })
            inp = write_json(w.path("in.json"), frames({"tick": 0, "catch": True}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1",
                                     "--scenario", sc, "--inputs", inp, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual(len(events(read_jsonl(w.path("o.jsonl")), "fish_caught")), 1)

            # Ở bước hết giờ (time_left_ticks=1 tại phase_tick=360? kiểm trực tiếp ở tick=1): không cho cá bơi/sinh thêm
            sc_end = write_json(w.path("sc_end.json"), {
                "gather": {
                    "player": {"pos": [20, 10]},
                    "fish": [{"id": "F1", "kind": "ca_loc", "pos": [25, 10], "heading_deg": 0}],
                    "time_left_ticks": 1,
                    "random_fish": True,
                }
            })
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5",
                                     "--scenario", sc_end, "--out", w.path("end.jsonl"))
            self.assertEqual(code, 0, err)
            f_end = snapshots(read_jsonl(w.path("end.jsonl")))[-1]["fish"][0]
            self.assertEqual(f_end["pos"], [25.0, 10.0])

    def test_gather_p2_deterministic_bytes(self):
        with Workdir() as w:
            for i in (1, 2):
                code, err = run_headless("--mode", "gather", "--seed", "99", "--ticks", "800",
                                         "--out", w.path(f"r{i}.jsonl"))
                self.assertEqual(code, 0, err)
            with open(w.path("r1.jsonl"), "rb") as a, open(w.path("r2.jsonl"), "rb") as b:
                self.assertEqual(a.read(), b.read())


if __name__ == "__main__":
    unittest.main()
