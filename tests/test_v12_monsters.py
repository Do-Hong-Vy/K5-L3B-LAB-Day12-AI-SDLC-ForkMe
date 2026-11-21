"""v1.2 (Ticket-03) gather + bàn giao, và Cá Sấu (Ticket-02 mục 1.2) — AC-P3-01, 02, 07, 09 · AC-P2-04.

Hộp đen qua headless_cmd với contract đang chạy; số liệu đọc từ game.contract.json.
"""

import json
import math
import os
import unittest

from helpers import INDIVIDUAL, ROOT, Workdir, close, events, frames, read_jsonl, run_headless, snapshots, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    C = json.load(f)
G = C["tuning"]["gather"]
MON = G["monsters"]
CROC = MON["species"]["ca_sau"]


def gather(w, sc, inputs=(), ticks=1, every=1, extra=()):
    a = ["--mode", "gather", "--seed", "1", "--scenario", write_json(w.path("sc.json"), {"gather": sc}),
         "--ticks", str(ticks), "--out", w.path("g.jsonl"), "--snapshot-every", str(every), *extra]
    if inputs:
        a += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*a)
    assert code == 0, err
    return read_jsonl(w.path("g.jsonl"))


@unittest.skipUnless(INDIVIDUAL, "chỉ áp dụng contract v1.2")
class FreshGather(unittest.TestCase):
    def test_vi_du_nguong_ticket03(self):
        with Workdir() as w:
            rows = gather(w, {"hold": [{"id": "I1", "kind": "ca_linh", "fresh": 30}], "random_fish": False, "monsters": []})
            self.assertEqual(events(rows, "spoiled"), [{"type": "event", "tick": 1, "phase": "gather", "name": "spoiled",
                                                        "data": {"item_id": "I1", "kind": "ca_linh", "location": "hold"}}])

    def test_smoke_ban_giao_file_ticket03(self):
        with Workdir() as w:
            inv = w.path("inv.json")
            gather(w, {"hold": [{"id": "I1", "kind": "ca_linh", "fresh": 100}], "random_fish": False, "monsters": []},
                   inputs=[{"tick": 0, "interact": True}], extra=("--inventory-out", inv))
            saved = json.load(open(inv, encoding="utf-8"))
            self.assertEqual([(x["id"], x["kind"]) for x in saved["items"]], [("I1", "ca_linh")])
            self.assertEqual(saved["items"][0]["fresh"], 100 - C["tuning"]["freshness"]["gather_decay_per_s"] / 60)
            code, err = run_headless("--mode", "quan", "--seed", "1", "--inventory", inv, "--ticks", "0",
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            q = snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"]
            self.assertEqual([(x["id"], x["kind"]) for x in q], [("I1", "ca_linh")])
            self.assertTrue(close(q[0]["fresh"], saved["items"][0]["fresh"], 0.01))

    def test_hang_moi_cap_id_tiep_theo_va_hao_tu_buoc_sau(self):
        with Workdir() as w:
            rows = gather(w, {"player": {"pos": [44, 0]}, "hold": [{"id": "I7", "kind": "ca_loc", "fresh": 50}],
                              "random_fish": False, "monsters": []},
                          inputs=[{"tick": 0, "interact": True}], ticks=2)
            s1, s2 = [s for s in snapshots(rows) if s["tick"] in (1, 2)]
            self.assertEqual([h["id"] for h in s1["hold"]], ["I7", "I8"])
            self.assertEqual(s1["hold"][1]["fresh"], 100)
            self.assertTrue(close(s2["hold"][1]["fresh"], 100 - 0.5 / 60, 0.001))  # JSONL làm tròn 3 số

    def test_kho_dem_bi_tu_choi_o_v12(self):
        with Workdir() as w:
            p = write_json(w.path("inv.json"), {"items": {"ca_loc": 1}})
            self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--inventory", p, "--ticks", "0",
                                          "--out", w.path("q.jsonl"))[0], 2)

    def test_id_ca_the_tiep_tuc_qua_ngay(self):
        sc = {"gather": {"hold": [{"id": "I1", "kind": "ca_loc", "fresh": 100}], "random_fish": False, "monsters": []}}
        inp = [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}]
        q = int(C["tuning"]["quan"]["duration_s"] * 60)
        start2 = 1 + q + C["tuning"]["shop"]["max_ticks"]
        inp += [{"tick": start2, "interact": True}]
        with Workdir() as w:
            code, err = run_headless("--mode", "day", "--days", "2", "--seed", "1", "--ticks", str(start2 + 2),
                                     "--scenario", write_json(w.path("sc.json"), sc),
                                     "--inputs", write_json(w.path("in.json"), frames(*inp)), "--out", w.path("d.jsonl"))
            self.assertEqual(code, 0, err)
            ends = events(read_jsonl(w.path("d.jsonl")), "gather_end")
            self.assertEqual([[x["id"] for x in e["data"]["inventory"]["items"]] for e in ends], [["I1"], ["I2"]])


class Crocodile(unittest.TestCase):
    def _croc(self, **kw):
        m = {"id": "M1", "kind": "ca_sau", "pos": [50, 20], "waypoints": [[50, 20], [54, 20]]}
        m.update(kw)
        return m

    def test_bo_tri_mac_dinh_ngay_1_va_patrol(self):
        with Workdir() as w:
            rows = gather(w, {"random_fish": False}, ticks=60)
            m = snapshots(rows)[-1]["monsters"]
            self.assertEqual([x["id"] for x in m], [s["id"] for s in MON["spawns"] if s["from_day"] <= 1])
            self.assertEqual(m[0]["state"], "patrol")
            self.assertTrue(close(m[0]["pos"][0], MON["spawns"][0]["pos"][0] + CROC["patrol_speed"], 1e-6))

    def test_chase_khi_gan_va_hit_mat_mau_rot_hang_bat_tu(self):
        hold = [{"id": f"I{i}", "kind": "ca_loc", "fresh": 100} for i in range(1, 6)] if INDIVIDUAL else ["ca_loc"] * 5
        with Workdir() as w:
            rows = gather(w, {"player": {"pos": [50, 20]}, "hold": hold, "random_fish": False,
                              "monsters": [self._croc(pos=[51, 20])]}, ticks=3)
            hits = events(rows, "monster_hit")
            self.assertEqual(len(hits), 1)
            d = hits[0]["data"]
            self.assertEqual((hits[0]["tick"], d["monster_id"], d["hp"]), (1, "M1", G["hp_max"] - 1))
            self.assertEqual(len(d["lost"]), math.floor(5 * MON["loss_ratio"]))
            if INDIVIDUAL:
                self.assertEqual([x["id"] for x in d["lost"]], ["I5", "I4"])  # LIFO
            s = snapshots(rows)[-1]
            self.assertEqual(s["player"]["invuln_ticks"], MON["invuln_ticks"] - 2)
            self.assertEqual((s["monsters"][0]["state"], s["monsters"][0]["state_ticks_left"]),
                             ("recoil", CROC["recoil_ticks"] - 2))

    def test_khong_hit_khi_nguoi_choi_o_vung_nong(self):
        with Workdir() as w:
            rows = gather(w, {"player": {"pos": [50, 5]}, "random_fish": False,
                              "monsters": [self._croc(pos=[50, 10])]}, ticks=30)
            self.assertEqual(events(rows, "monster_hit"), [])
            self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "patrol")

    def test_ngat_do_quai(self):
        with Workdir() as w:
            rows = gather(w, {"player": {"pos": [50, 20], "hp": 1}, "random_fish": False,
                              "monsters": [self._croc(pos=[50, 20])]}, ticks=3)
            names = [e["name"] for e in events(rows)]
            self.assertEqual(names[-3:], ["monster_hit", "faint", "gather_end"])
            self.assertEqual(events(rows, "faint")[0]["data"]["cause"], "monster")
            self.assertEqual(rows[-1]["reason"], "fainted")

    def test_scenario_quai_sai_ma_2(self):
        with Workdir() as w:
            for bad in ([self._croc(kind="ca_map")], [self._croc(waypoints=[[50, 20]])], [self._croc(state="recoil")],
                        [self._croc(target_idx=2)], [self._croc(x=1)]):
                sc = write_json(w.path("b.json"), {"gather": {"monsters": bad}})
                self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--scenario", sc, "--ticks", "0",
                                              "--out", w.path("o.jsonl"))[0], 2, bad)


if __name__ == "__main__":
    unittest.main()
