"""Kiểm thử luật Phase 1 cho buổi sáng (`gather` — AC-P1-01 .. AC-P1-05)."""

import json
import unittest

from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


def tuning_gather():
    with open("game.contract.json", encoding="utf-8") as f:
        return json.load(f)["tuning"]["gather"]


class GatherPhase1Rules(unittest.TestCase):
    def test_dive_surface_and_oxygen_refill_clamp(self):
        g = tuning_gather()
        oxy_max = int(round(g["oxygen_max_s"] * 60))
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"player": {"pos": [20, 0.4]}, "random_fish": False}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [0, 1]}, {"tick": 20, "move": [0, -1]}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "60", "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            dives = events(rows, "dive")
            surfs = events(rows, "surface")
            self.assertEqual(len(dives), 1)
            self.assertGreater(dives[0]["data"]["pos"][1], g["surface_depth"])
            self.assertEqual(len(surfs), 1)
            self.assertLessEqual(surfs[0]["data"]["pos"][1], g["surface_depth"])
            last = snapshots(rows)[-1]["player"]
            self.assertEqual(last["oxygen_ticks"], oxy_max)
            self.assertEqual(last["zero_oxy_ticks"], 0)
            self.assertTrue(last["at_surface"])

    def test_oxygen_empty_choke_at_t_plus_59(self):
        g = tuning_gather()
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {"player": {"pos": [20, 10], "oxygen_ticks": 1, "zero_oxy_ticks": 0, "hp": g["hp_max"]},
                           "random_fish": False}
            })
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "60", "--scenario", sc,
                                     "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            empty_ev = events(rows, "oxygen_empty")
            choke_ev = events(rows, "choke")
            self.assertEqual(len(empty_ev), 1)
            self.assertEqual(empty_ev[0]["tick"], 1)
            self.assertEqual(empty_ev[0]["data"], {"oxygen_ticks": 0})
            self.assertEqual(len(choke_ev), 1)
            self.assertEqual(choke_ev[0]["tick"], 60)  # chạm 0 ở tick 1 -> ngạt lần đầu ở t + 59 = 60
            self.assertEqual(choke_ev[0]["data"], {"hp": g["hp_max"] - 1})

    def test_surface_on_choke_tick_prevents_choke(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {"player": {"pos": [20, 0.51], "vel": [0, -4.0], "oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1},
                           "random_fish": False}
            })
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [0, -1]}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "2", "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            self.assertEqual(events(rows, "choke"), [])
            self.assertEqual(events(rows, "faint"), [])
            self.assertEqual(len(events(rows, "surface")), 1)
            self.assertEqual(snapshots(rows)[-1]["player"]["hp"], 1)

    def test_faint_drops_hold_lifo_and_writes_empty_inventory(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [2, 1.0], "oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1},
                    "hold": ["ca_loc", "bong_sung", "ca_linh"],
                    "random_fish": False,
                }
            })
            # Dù đang ở trong vùng bến và bấm E cùng lúc, hết Máu ở bước 2 phải ngất thay vì docked.
            inp = write_json(w.path("in.json"), frames({"tick": 0, "interact": True}))
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--scenario", sc,
                                     "--inputs", inp, "--inventory-out", inv, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            faint_ev = events(rows, "faint")
            self.assertEqual(len(faint_ev), 1)
            self.assertEqual(faint_ev[0]["data"], {
                "cause": "choke",
                "lost": ["ca_linh", "bong_sung", "ca_loc"],
                "hp": 0,
            })
            end_ev = events(rows, "gather_end")
            self.assertEqual(len(end_ev), 1)
            self.assertEqual(end_ev[0]["data"], {"reason": "fainted", "inventory": {"items": {}}})
            self.assertEqual(rows[-1]["reason"], "fainted")
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {}})

    def test_harvest_nearest_tiebreak_regrow_and_hold_full(self):
        g = tuning_gather()
        regrow_ticks = int(round(g["regrow_s"] * 60))
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [20, 0]},
                    "nodes": [
                        {"id": "N10", "kind": "bong_sung", "pos": [22, 0], "regrow_ticks": 0},
                        {"id": "N2", "kind": "bong_dien_dien", "pos": [18, 0], "regrow_ticks": 1},
                    ],
                    "hold": ["ca_loc"] * (g["hold_capacity"] - 1),
                    "random_fish": False,
                }
            })
            # Tick 0: N2 giảm regrow từ 1 -> 0 (node_regrown) và hái được ngay (tie-break N2 < N10).
            # Tick 2: bấm interact khi giỏ đã đầy -> chọn N10 nhưng bị hold_full, N10 vẫn ready.
            inp = write_json(w.path("in.json"), frames(
                {"tick": 0, "interact": True},
                {"tick": 1, "interact": False},
                {"tick": 2, "interact": True},
            ))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "3", "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            self.assertEqual([e["data"] for e in events(rows, "node_regrown")], [{"node_id": "N2"}])
            g_ev = events(rows, "gather")
            self.assertEqual(len(g_ev), 1)
            self.assertEqual(g_ev[0]["tick"], 1)
            self.assertEqual(g_ev[0]["data"], {"node_id": "N2", "kind": "bong_dien_dien", "amount": g["node_yield"]})
            hf_ev = events(rows, "hold_full")
            self.assertEqual(len(hf_ev), 1)
            self.assertEqual(hf_ev[0]["tick"], 3)
            self.assertEqual(hf_ev[0]["data"], {"action": "gather", "node_id": "N10", "required": g["node_yield"], "free": 0})
            last_nodes = {n["id"]: n for n in snapshots(rows)[-1]["nodes"]}
            self.assertEqual(last_nodes["N2"]["regrow_ticks"], regrow_ticks - 2)
            self.assertTrue(last_nodes["N10"]["ready"])

    def test_catch_nearest_tiebreak_removes_school_cooldown_and_no_miss_cooldown(self):
        g = tuning_gather()
        cd_ticks = int(round(g["catch_cooldown_s"] * 60))
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [20, 10]},
                    # v1.1: cá bơi khi random_fish=True nên cố định cá để test cooldown bắt ở tọa độ cũ
                    "random_fish": False,
                    "fish": [
                        {"id": "F10", "kind": "ca_loc", "pos": [22, 10]},
                        {"id": "F2", "kind": "ca_linh", "pos": [18, 10]},
                    ],
                }
            })
            # Tick 0: bắt F2 (F2 < F10), đặt cd = 30.
            # Tick 2: trong cooldown -> không bắt được.
            # Tick 30 (= 0 + cd_ticks): hết hồi -> bắt được F10.
            inp = write_json(w.path("in.json"), frames(
                {"tick": 0, "catch": True},
                {"tick": 1, "catch": False},
                {"tick": 2, "catch": True},
                {"tick": 3, "catch": False},
                {"tick": cd_ticks, "catch": True},
            ))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", str(cd_ticks + 1), "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            caught = events(rows, "fish_caught")
            self.assertEqual([(e["tick"], e["data"]) for e in caught], [
                (1, {"fish_id": "F2", "kind": "ca_linh", "yield": g["fish_yield"]["ca_linh"]}),
                (cd_ticks + 1, {"fish_id": "F10", "kind": "ca_loc", "yield": g["fish_yield"]["ca_loc"]}),
            ])
            self.assertEqual(snapshots(rows)[-1]["fish"], [])

    def test_catch_hold_full_keeps_fish_and_cooldown_and_does_not_fallback(self):
        g = tuning_gather()
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [20, 10]},
                    "hold": ["bong_sung"] * (g["hold_capacity"] - 2),
                    "fish": [
                        {"id": "F1", "kind": "ca_linh", "pos": [20.5, 10]},  # gần hơn, yield=3 > free=2
                        {"id": "F2", "kind": "ca_loc", "pos": [21.5, 10]},   # xa hơn nhưng vừa chỗ -> không được thử
                    ],
                }
            })
            inp = write_json(w.path("in.json"), frames({"tick": 0, "catch": True}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            self.assertEqual(events(rows, "fish_caught"), [])
            hf = events(rows, "hold_full")
            self.assertEqual(len(hf), 1)
            self.assertEqual(hf[0]["data"], {"action": "catch", "fish_id": "F1", "required": 3, "free": 2})
            snap = snapshots(rows)[-1]
            self.assertEqual(snap["player"]["catch_cd_ticks"], 0)
            self.assertEqual([f["id"] for f in snap["fish"]], ["F1", "F2"])

    def test_catch_miss_and_surface_catch_ignored_without_cooldown(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "gather": {
                    "player": {"pos": [20, 0.5]},
                    "fish": [{"id": "F1", "kind": "ca_loc", "pos": [20, 1.0]}],
                }
            })
            # Tick 0: đang ở mặt nước (d=0.5) bấm catch -> bỏ qua, không hồi chiêu.
            # Tick 1: lặn xuống d > 0.5 nhưng không có đàn nào gần (ví dụ ở xa) -> test riêng.
            inp = write_json(w.path("in.json"), frames({"tick": 0, "catch": True}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            self.assertEqual(events(rows, "fish_caught"), [])
            self.assertEqual(snapshots(rows)[-1]["player"]["catch_cd_ticks"], 0)

            sc2 = write_json(w.path("sc2.json"), {"gather": {"player": {"pos": [20, 10]}, "fish": []}})
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc2,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o2.jsonl"))
            self.assertEqual(code, 0, err)
            rows2 = read_jsonl(w.path("o2.jsonl"))
            self.assertEqual(events(rows2, "fish_caught"), [])
            self.assertEqual(snapshots(rows2)[-1]["player"]["catch_cd_ticks"], 0)

    def test_last_tick_dock_and_last_tick_catch(self):
        g = tuning_gather()
        with Workdir() as w:
            # Cập bến đúng mép dock_radius ở bước cuối cùng -> docked
            sc = write_json(w.path("sc.json"), {
                "gather": {"player": {"pos": [g["dock_pos"][0] + g["dock_radius"], g["dock_pos"][1]]},
                           "hold": ["ca_loc"], "time_left_ticks": 1, "random_fish": False}
            })
            inp = write_json(w.path("in.json"), frames({"tick": 0, "interact": True}))
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--scenario", sc,
                                     "--inputs", inp, "--inventory-out", inv, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            self.assertEqual(rows[-1]["reason"], "docked")
            self.assertEqual(events(rows, "gather_end")[0]["data"]["reason"], "docked")

            # Bắt cá ở bước cuối khi time_left_ticks=1 -> vẫn vào kho khi kết thúc time
            sc2 = write_json(w.path("sc2.json"), {
                "gather": {"player": {"pos": [20, 10]}, "fish": [{"id": "F1", "kind": "ca_loc", "pos": [20, 10]}],
                           "time_left_ticks": 1}
            })
            inp2 = write_json(w.path("in2.json"), frames({"tick": 0, "catch": True}))
            inv2 = w.path("inv2.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--scenario", sc2,
                                     "--inputs", inp2, "--inventory-out", inv2, "--out", w.path("o2.jsonl"))
            self.assertEqual(code, 0, err)
            rows2 = read_jsonl(w.path("o2.jsonl"))
            self.assertEqual(rows2[-1]["reason"], "time")
            self.assertEqual(len(events(rows2, "fish_caught")), 1)
            with open(inv2, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {"ca_loc": g["fish_yield"]["ca_loc"]}})

    def test_gather_full_flow_deterministic_bytes(self):
        with Workdir() as w:
            inp = write_json(w.path("in.json"), frames(
                {"tick": 0, "move": [1, 0]},
                {"tick": 150, "move": [0, 0], "interact": True},
                {"tick": 151, "interact": False, "move": [0.4, 1]},
                {"tick": 230, "move": [0, 0], "catch": True},
                {"tick": 231, "catch": False, "move": [-1, -0.8]},
                {"tick": 420, "move": [0, 0], "interact": True},
            ))
            for i in (1, 2):
                code, err = run_headless("--mode", "gather", "--seed", "7", "--ticks", "500", "--inputs", inp,
                                         "--inventory-out", w.path(f"inv{i}.json"), "--out", w.path(f"o{i}.jsonl"))
                self.assertEqual(code, 0, err)
            for name in ("o", "inv"):
                ext = "jsonl" if name == "o" else "json"
                with open(w.path(f"{name}1.{ext}"), "rb") as a, open(w.path(f"{name}2.{ext}"), "rb") as b:
                    self.assertEqual(a.read(), b.read())

    def test_no_hardcoded_tuning_constants(self):
        with open("game.contract.json", encoding="utf-8") as f:
            tuning = json.load(f)["tuning"]
        custom = json.loads(json.dumps(tuning))
        custom["gather"].update({
            "surface_depth": 1.2,
            "oxygen_max_s": 0.5,
            "oxygen_refill_per_tick": 2,
            "choke_interval_ticks": 3,
            "hp_max": 2,
            "hold_capacity": 6,
            "node_yield": 2,
            "regrow_s": 0.5,
            "catch_cooldown_s": 0.25,
            "fish_yield": {"ca_linh": 4, "ca_loc": 2},
        })
        sc = {
            "player": {"pos": [20, 1.1], "oxygen_ticks": 1, "hp": 2},
            "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [20, 0]}],
            "fish": [{"id": "F1", "kind": "ca_loc", "pos": [20, 1.5]}],
            "random_fish": False,
        }
        sim = GatherSim(custom, sc, Streams(1), IdAllocator())
        # Ở d = 1.1 <= 1.2 (surface_depth tùy biến), hái nút cho node_yield = 2 và regrow = 30
        ev1 = sim.step(InputState((0.0, 0.0), {"interact": True}, {"interact"}))
        self.assertEqual(ev1, [("gather", {"node_id": "N1", "kind": "bong_sung", "amount": 2})])
        self.assertEqual(sim.hold, ["bong_sung", "bong_sung"])
        self.assertEqual(sim.nodes[0]["regrow_ticks"], 30)
        self.assertEqual(sim.oxygen_ticks, 3)  # 1 + 2 = 3 <= 30

        # Lặn xuống d > 1.2 -> dive, oxy 1 -> 0 -> oxygen_empty, zero_oxy=1; thêm 2 bước -> choke
        sim.pos = [20.0, 1.195]
        sim.oxygen_ticks = 1
        ev2 = sim.step(InputState((0.0, 1.0), {}, set()))  # d = 1.206 > 1.2, oxy 1 -> 0, zero_oxy=1
        self.assertEqual([n for n, _ in ev2], ["dive", "oxygen_empty"])
        self.assertEqual(sim.zero_oxy_ticks, 1)
        sim.step(InputState((0.0, 0.0), {}, set()))  # zero_oxy=2
        ev4 = sim.step(InputState((0.0, 0.0), {}, set()))  # zero_oxy=3 -> choke (hp 2->1)
        self.assertEqual(ev4, [("choke", {"hp": 1})])

        # Bắt cá F1 dưới nước -> fish_yield["ca_loc"] = 2, catch_cd = 15
        ev5 = sim.step(InputState((0.0, 0.0), {"catch": True}, {"catch"}))
        self.assertEqual(ev5, [("fish_caught", {"fish_id": "F1", "kind": "ca_loc", "yield": 2})])
        self.assertEqual(sim.catch_cd_ticks, 15)


if __name__ == "__main__":
    unittest.main()
