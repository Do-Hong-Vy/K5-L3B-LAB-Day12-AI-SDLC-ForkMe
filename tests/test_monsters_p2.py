"""CP2 (QA, lát L2) — AC-P2-04: Cá Sấu Năm Chèo (Ticket-02 mục 1.2, 4.5).

Unit test `chonoi.sim.monsters.MonsterSystem` với một sim giả (chỉ pos/hp/hold/invuln_ticks/_finish),
để kiểm luật trước khi ghép vào GatherSim. Số liệu lấy từ game.contract.json (v1.1).
"""

import copy
import json
import math
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

from chonoi.contract import load_contract
from chonoi.sim.monsters import MonsterSystem

G = copy.deepcopy(load_contract()["tuning"]["gather"])  # contract v1.1: monsters theo Ticket-02 1.2
SP = G["monsters"]["species"]["ca_sau"]
INVULN = G["monsters"]["invuln_ticks"]
RECOIL = SP["recoil_ticks"]


class FakeSim:
    def __init__(self, pos, hp=3, hold=(), invuln=0):
        self.pos, self.hp, self.hold, self.invuln_ticks = list(pos), hp, list(hold), invuln
        self.done, self.reason = False, None

    def _finish(self, reason, events):
        self.done, self.reason = True, reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": {}}}))


def system(monsters=None, day=1):
    return MonsterSystem(G, monsters, day)


def one(**kw):
    m = {"id": "M1", "kind": "ca_sau", "pos": [60, 24], "waypoints": [[60, 24], [64, 24]]}
    m.update(kw)
    return m


def run(ms, sim, n):
    ev = []
    for _ in range(n):
        ms.step(sim, ev)
    return ev


FAR = [5, 25]  # người chơi ở xa mọi quái


class Layout(unittest.TestCase):
    def test_ngay_1_chi_M1_ngay_3_co_M2(self):
        self.assertEqual([m["id"] for m in system(day=1).list], ["M1"])
        self.assertEqual([m["id"] for m in system(day=2).list], ["M1"])
        self.assertEqual([m["id"] for m in system(day=3).list], ["M1", "M2"])

    def test_mac_dinh_target_1_patrol(self):
        m = system().snapshot()[0]
        self.assertEqual((m["state"], m["target_idx"], m["pos"]), ("patrol", 1, [60.0, 24.0]))
        self.assertIsNone(m["recoil_dir"])

    def test_scenario_thay_danh_sach(self):
        self.assertEqual(system([one(id="Q7")]).snapshot()[0]["id"], "Q7")
        self.assertEqual(system([]).list, [])

    def test_tuning_khong_co_monsters_thi_tat(self):
        g = copy.deepcopy(G)
        g.pop("monsters")
        ms = MonsterSystem(g)
        self.assertFalse(ms.step(FakeSim([60, 24]), []))
        self.assertEqual(ms.snapshot(), [])


class Patrol(unittest.TestCase):
    def test_patrol_1ms_toi_waypoint_roi_doi_muc_tieu(self):
        ms, sim = system(), FakeSim(FAR)
        run(ms, sim, 60)
        self.assertAlmostEqual(ms.list[0]["pos"][0], 60 + SP["patrol_speed"], places=6)
        steps = int(round(4 / SP["patrol_speed"] * 60))
        run(ms, sim, steps - 60)
        self.assertEqual(ms.list[0]["pos"], [64.0, 24.0])
        self.assertEqual(ms.list[0]["target_idx"], 0)
        run(ms, sim, 1)
        self.assertLess(ms.list[0]["pos"][0], 64.0)


class Chase(unittest.TestCase):
    def test_phat_hien_trong_10m_chase_3ms(self):
        ms, sim = system(), FakeSim([60 + SP["detect_radius"], 24])  # đúng mép bán kính
        run(ms, sim, 1)
        m = ms.list[0]
        self.assertEqual(m["state"], "chase")
        self.assertAlmostEqual(m["pos"][0], 60 + SP["chase_speed"] / 60, places=6)

    def test_ngoai_10m_khong_phat_hien(self):
        ms = system()
        run(ms, FakeSim([60 + SP["detect_radius"] + 0.01, 24]), 1)
        self.assertEqual(ms.list[0]["state"], "patrol")

    def test_nguoi_choi_nong_khong_bi_duoi(self):
        ms = system([one(pos=[60, 10], waypoints=[[60, 10], [64, 10]])])
        run(ms, FakeSim([60, SP["depths"][0] - 0.5]), 1)
        self.assertEqual(ms.list[0]["state"], "patrol")

    def test_roi_chase_khi_xa_hon_16m(self):
        ms = system([one(state="chase")])
        run(ms, FakeSim([60 + SP["exit_radius"] + 0.5, 24]), 1)
        self.assertEqual(ms.list[0]["state"], "patrol")

    def test_giu_chase_trong_16m(self):
        ms = system([one(state="chase")])
        run(ms, FakeSim([60 + SP["exit_radius"] - 0.5, 24]), 1)
        self.assertEqual(ms.list[0]["state"], "chase")

    def test_roi_chase_khi_nguoi_choi_len_nong(self):
        ms = system([one(pos=[60, 12], waypoints=[[60, 12], [64, 12]], state="chase")])
        run(ms, FakeSim([61, SP["depths"][0] - 1]), 1)
        self.assertEqual(ms.list[0]["state"], "patrol")

    def test_chan_trong_dai_do_sau_loai(self):
        ms = system([one(pos=[60, 11], waypoints=[[60, 11], [64, 11]], state="chase")])
        run(ms, FakeSim([60, 10.0]), 120)  # người chơi đúng ngưỡng d = 10, quái không lên quá 10
        self.assertGreaterEqual(ms.list[0]["pos"][1], SP["depths"][0])


class Hit(unittest.TestCase):
    def test_hit_mat_1_mau_roi_nua_gio_lifo_bat_tu(self):
        ms = system()
        sim = FakeSim([61, 24], hold=["ca_loc", "bong_sung", "ca_linh", "ca_linh", "keo_neo"])
        ev = run(ms, sim, 1)
        self.assertEqual(len(ev), 1)
        name, data = ev[0]
        self.assertEqual(name, "monster_hit")
        self.assertEqual(data["monster_id"], "M1")
        self.assertEqual(data["hp"], 2)
        self.assertEqual(data["lost"], ["keo_neo", "ca_linh"])  # floor(5 × 0.5) = 2, nhặt sau mất trước
        self.assertEqual(data["pos"], [61, 24])
        self.assertEqual(sim.hold, ["ca_loc", "bong_sung", "ca_linh"])
        self.assertEqual(sim.invuln_ticks, INVULN)
        m = ms.list[0]
        self.assertEqual((m["state"], m["state_ticks_left"]), ("recoil", RECOIL))

    def test_gio_rong_va_le_lam_tron_xuong(self):
        sim = FakeSim([61, 24], hold=["ca_loc"])
        ev = run(system(), sim, 1)
        self.assertEqual(ev[0][1]["lost"], [])  # floor(0.5) = 0
        self.assertEqual(sim.hold, ["ca_loc"])

    def test_dung_mep_hit_radius(self):
        ms = system([one(waypoints=[[60, 24], [60, 24]])])
        ev = run(ms, FakeSim([60, 24 + SP["hit_radius"]]), 1)  # quái chase lại gần hơn -> vẫn trúng
        self.assertEqual(ev[0][0], "monster_hit")

    def test_dang_bat_tu_khong_hit_khong_recoil(self):
        ms, sim = system(), FakeSim([61, 24], invuln=5)
        self.assertEqual(run(ms, sim, 1), [])
        self.assertNotEqual(ms.list[0]["state"], "recoil")
        self.assertEqual(sim.hp, 3)

    def test_nguoi_choi_nong_khong_bi_hit(self):
        ms = system([one(pos=[60, 10], waypoints=[[60, 10], [60, 10]])])
        self.assertEqual(run(ms, FakeSim([60, SP["depths"][0] - 0.2]), 1), [])

    def test_mot_hit_moi_buoc_con_gan_nhat_hoa_id(self):
        ms = system([one(id="M2", pos=[59, 24], waypoints=[[59, 24], [59, 24]]),
                     one(id="M1", pos=[61, 24], waypoints=[[61, 24], [61, 24]])])
        sim = FakeSim([60, 24])
        ev = run(ms, sim, 1)
        self.assertEqual([e[0] for e in ev], ["monster_hit"])
        self.assertEqual(ev[0][1]["monster_id"], "M1")  # cùng khoảng cách -> id nhỏ
        self.assertEqual(sim.hp, 2)


class Recoil(unittest.TestCase):
    def test_recoil_lui_xa_nguoi_choi_60_buoc_khong_hit_roi_patrol(self):
        ms = system([one(waypoints=[[60, 24], [60, 24]])])
        sim = FakeSim([61, 24])
        run(ms, sim, 1)  # hit; quái chase lại gần trước khi chạm
        m = ms.list[0]
        self.assertEqual(m["recoil_dir"], [-1.0, 0.0])
        x0 = m["pos"][0]
        sim.invuln_ticks = 0  # cố tình hết bất tử: recoil vẫn không được gây hit
        for i in range(RECOIL - 1):
            self.assertEqual(run(ms, sim, 1), [], f"bước recoil {i + 1} không được hit")
            sim.invuln_ticks = 0
        self.assertEqual(m["state"], "recoil")
        self.assertEqual(run(ms, sim, 1), [])  # bước recoil cuối -> patrol, chưa xét chạm
        self.assertEqual(m["state"], "patrol")
        self.assertAlmostEqual(m["pos"][0], x0 - SP["recoil_dist"], places=6)
        self.assertIsNone(m["recoil_dir"])

    def test_sau_recoil_xet_cham_tu_buoc_ke(self):
        ms = system([one(pos=[60, 24], waypoints=[[60, 24], [60, 24]], state="recoil", state_ticks_left=1,
                         recoil_dir=[1, 0])])
        sim = FakeSim([60, 24])
        self.assertEqual(run(ms, sim, 1), [])
        self.assertEqual(run(ms, sim, 1)[0][0], "monster_hit")

    def test_trung_tam_dung_huong_x_duong(self):
        ms = system([one(waypoints=[[60, 24], [60, 24]])])
        run(ms, FakeSim([60, 24]), 1)
        self.assertEqual(ms.list[0]["recoil_dir"], [1.0, 0.0])

    def test_recoil_chan_mep_do_sau(self):
        ms = system([one(pos=[60, 10], waypoints=[[60, 10], [60, 10]], state="recoil", state_ticks_left=30,
                         recoil_dir=[0, -1])])
        run(ms, FakeSim(FAR), 30)
        self.assertEqual(ms.list[0]["pos"][1], SP["depths"][0])


class Faint(unittest.TestCase):
    def test_mau_ve_0_ngat_cause_monster(self):
        sim = FakeSim([61, 24], hp=1, hold=["ca_loc", "bong_sung", "ca_linh"])
        ev = []
        self.assertTrue(system().step(sim, ev))
        self.assertEqual([e[0] for e in ev], ["monster_hit", "faint", "gather_end"])
        self.assertEqual(ev[0][1]["lost"], ["ca_linh"])
        self.assertEqual(ev[1][1], {"cause": "monster", "lost": ["bong_sung", "ca_loc"], "hp": 0})
        self.assertEqual(ev[2][1]["reason"], "fainted")
        self.assertEqual(sim.hold, [])
        self.assertTrue(sim.done)


class Deterministic(unittest.TestCase):
    def test_cung_dau_vao_cung_ket_qua(self):
        def trace():
            ms, sim = system(day=3), FakeSim([70, 22], hold=["ca_loc"] * 6)
            out = []
            for k in range(900):
                sim.pos = [70 + 15 * math.sin(k / 50), 22]
                ev = []
                ms.step(sim, ev)
                out.append((repr(ms.snapshot()), ev))
            return out
        self.assertEqual(trace(), trace())


class HeadlessMonsters(unittest.TestCase):
    """Hộp đen qua headless_cmd sau khi ghép vào GatherSim (Ticket-02 4.4 snapshot/event, 4.5 thứ tự)."""

    def run_gather(self, w, block, ticks=1, inputs=None):
        args = ["--mode", "gather", "--seed", "1", "--ticks", str(ticks), "--snapshot-every", "1",
                "--scenario", write_json(w.path("sc.json"), {"gather": block}),
                "--out", w.path("g.jsonl"), "--inventory-out", w.path("inv.json")]
        if inputs:
            args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
        code, err = run_headless(*args)
        self.assertEqual(code, 0, err)
        return read_jsonl(w.path("g.jsonl"))

    STILL = {"id": "M1", "kind": "ca_sau", "pos": [61, 24], "waypoints": [[61, 24], [61, 24]]}

    def test_snapshot_tick0_co_monsters_ngay_1(self):
        with Workdir() as w:
            s0 = snapshots(self.run_gather(w, {}, ticks=0))[0]
        self.assertEqual([m["id"] for m in s0["monsters"]], ["M1"])
        m = s0["monsters"][0]
        self.assertEqual((m["state"], m["target_idx"], m["recoil_dir"]), ("patrol", 1, None))
        self.assertEqual(s0["player"]["invuln_ticks"], 0)

    def test_hit_qua_headless(self):
        with Workdir() as w:
            rows = self.run_gather(w, {"player": {"pos": [60, 24]}, "hold": ["ca_loc", "bong_sung"],
                                       "fish": [], "monsters": [self.STILL]})
        hit = events(rows, "monster_hit")
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["tick"], 1)
        self.assertEqual(hit[0]["data"]["lost"], ["bong_sung"])
        s1 = snapshots(rows)[-1]
        self.assertEqual(s1["player"]["hp"], G["hp_max"] - 1)
        self.assertEqual(s1["player"]["invuln_ticks"], INVULN)
        self.assertEqual(s1["hold"], ["ca_loc"])
        self.assertEqual(s1["monsters"][0]["state"], "recoil")

    def test_bat_tu_tu_scenario_chan_hit(self):
        with Workdir() as w:
            rows = self.run_gather(w, {"player": {"pos": [60, 24], "invuln_ticks": 5}, "fish": [],
                                       "monsters": [self.STILL]})
        self.assertEqual(events(rows, "monster_hit"), [])

    def test_ngat_do_quai_kho_rong(self):
        with Workdir() as w:
            rows = self.run_gather(w, {"player": {"pos": [60, 24], "hp": 1}, "hold": ["ca_loc", "ca_linh", "keo_neo"],
                                       "fish": [], "monsters": [self.STILL]}, ticks=5)
            with open(w.path("inv.json"), encoding="utf-8") as f:
                inv = json.load(f)
        names = [e["name"] for e in events(rows)]
        self.assertEqual(names[-3:], ["monster_hit", "faint", "gather_end"])
        faint = events(rows, "faint")[0]["data"]
        self.assertEqual(faint, {"cause": "monster", "lost": ["ca_linh", "ca_loc"], "hp": 0})
        self.assertEqual(events(rows, "gather_end")[0]["data"]["reason"], "fainted")
        self.assertEqual(inv, {"items": {}})
        self.assertEqual(rows[-1]["reason"], "fainted")

    def test_ngat_truoc_hit_cung_tick(self):
        # oxy 0, đếm ngạt 59 -> bước 1 ngạt (−1 Máu) rồi Cá Sấu chạm (−1 Máu): 2 -> 0, faint do monster
        with Workdir() as w:
            rows = self.run_gather(w, {"player": {"pos": [60, 24], "hp": 2, "oxygen_ticks": 0,
                                                  "zero_oxy_ticks": 59}, "fish": [], "monsters": [self.STILL]})
        names = [e["name"] for e in events(rows)]
        self.assertEqual(names, ["choke", "monster_hit", "faint", "gather_end"])
        self.assertEqual(events(rows, "faint")[0]["data"]["cause"], "monster")

    def test_ngat_choke_khong_xet_hit(self):
        # Máu 1 + ngạt -> faint(choke) và dừng bước, không còn monster_hit
        with Workdir() as w:
            rows = self.run_gather(w, {"player": {"pos": [60, 24], "hp": 1, "oxygen_ticks": 0,
                                                  "zero_oxy_ticks": 59}, "fish": [], "monsters": [self.STILL]})
        self.assertEqual([e["name"] for e in events(rows)], ["choke", "faint", "gather_end"])
        self.assertEqual(events(rows, "faint")[0]["data"]["cause"], "choke")

    def test_cap_ben_khi_bi_quai_duoi_van_docked(self):
        # quái không xuống được d < 10 nên người chơi ở bến luôn an toàn; cập bến ưu tiên trước bắt cá
        with Workdir() as w:
            rows = self.run_gather(w, {"fish": []}, inputs=[{"tick": 0, "interact": True}])
        self.assertEqual(rows[-1]["reason"], "docked")

    def test_M2_tu_ngay_3_trong_day(self):
        with Workdir() as w:
            sc = write_json(w.path("d.json"), {"gather": {"time_left_ticks": 5}, "quan": {"time_left_ticks": 5}})
            code, err = run_headless("--mode", "day", "--days", "3", "--seed", "1", "--scenario", sc,
                                     "--ticks", "5000", "--out", w.path("d.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("d.jsonl"))
        first = {}
        for r in snapshots(rows):
            if r["phase"] == "gather" and r["phase_tick"] == 0:
                first.setdefault(r["day"], [m["id"] for m in r["monsters"]])
        self.assertEqual(first, {1: ["M1"], 2: ["M1"], 3: ["M1", "M2"]})

    def test_tat_dinh_tung_byte_co_quai_duoi(self):
        inp = [{"tick": 0, "move": [1, 1]}, {"tick": 400, "move": [1, 0]}, {"tick": 900, "move": [0, 0]}]
        outs = []
        for _ in range(2):
            with Workdir() as w:
                self.run_gather(w, {"player": {"pos": [50, 20]}}, ticks=1500, inputs=inp)
                with open(w.path("g.jsonl"), "rb") as f:
                    outs.append(f.read())
        self.assertEqual(outs[0], outs[1])
        self.assertIn(b'"monster_hit"', outs[0], "kịch bản phải thật sự có hit để kiểm tất định")


if __name__ == "__main__":
    unittest.main()
