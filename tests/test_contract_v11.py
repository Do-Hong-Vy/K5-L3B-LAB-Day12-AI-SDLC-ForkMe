"""CP2 (QA) — AC-P2-01: validator contract v1.1 (Ticket-02 mục 1.1–1.3, 2, 4.1).

Mỗi test làm hỏng đúng một chỗ trong contract v1.1 của repo và đòi validator ném BadInput (headless mã 2).
"""

import copy
import json
import os
import shutil
import unittest

from helpers import ROOT, Workdir, run_headless

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput

def v11():
    """Tuning v1.1 của repo (contract_version "1.1", số chuẩn Ticket-02 do Integrator khai)."""
    c = load_contract()
    # v1.2 (Ticket-03) giữ nguyên mọi khóa v1.1 và thêm freshness -> test v1.1 vẫn áp dụng.
    assert c["contract_version"] in ("1.1", "1.2", "1.3"), "test v1.1 cần game.contract.json từ 1.1"
    return copy.deepcopy(c["tuning"])


class ContractV11(unittest.TestCase):
    def rejected(self, mutate):
        t = v11()
        mutate(t)
        with self.assertRaises(BadInput):
            validate_tuning(t)

    def test_so_chuan_v11_hop_le(self):
        validate_tuning(v11())

    # --- cá ---
    def test_fish_initial_khong_du_8_dan(self):
        # clarify #22: fish_initial là số 8 (Ticket-02 4.1)
        self.rejected(lambda t: t["gather"].update(fish_initial=7))

    def test_fish_initial_trung_vi_tri(self):
        # dạng danh sách cũ vẫn được kiểm: 8 đàn nhưng trùng vị trí -> từ chối
        def m(t):
            f = [{"id": f"F{i}", "kind": "ca_linh", "pos": [15, 5]} for i in range(1, 9)]
            t["gather"]["fish_initial"] = f
        self.rejected(m)

    def test_thieu_ca_keo_trong_yield(self):
        self.rejected(lambda t: t["gather"]["fish_yield"].pop("ca_keo"))

    def test_thieu_khoa_fish_speed(self):
        self.rejected(lambda t: t["gather"].pop("fish_speed"))

    def test_fish_depths_thieu_loai(self):
        self.rejected(lambda t: t["gather"]["fish_depths"].pop("ca_keo"))

    def test_fish_depths_tren_mat_nuoc(self):
        self.rejected(lambda t: t["gather"]["fish_depths"].__setitem__("ca_linh", [0, 12]))

    def test_fish_x_ngoai_bien(self):
        self.rejected(lambda t: t["gather"].__setitem__("fish_x", [4, 200]))

    def test_diem_sinh_ngoai_dai_loai(self):
        self.rejected(lambda t: t["gather"]["fish_spawn_depths"].__setitem__("ca_keo", [5]))

    def test_spawn_x_ngoai_fish_x(self):
        self.rejected(lambda t: t["gather"].__setitem__("fish_spawn_x", [2, 30]))

    def test_trong_so_am(self):
        self.rejected(lambda t: t["gather"]["fish_weights"].__setitem__("ca_loc", -1))

    def test_turn_ticks_khong_nguyen(self):
        self.rejected(lambda t: t["gather"].__setitem__("fish_turn_ticks", 1.5))

    # --- nút hái ---
    def test_thieu_nut_keo_neo(self):
        self.rejected(lambda t: t["gather"].__setitem__("nodes", t["gather"]["nodes"][:4]))

    # --- Cá Sấu ---
    def test_thieu_monsters(self):
        self.rejected(lambda t: t["gather"].pop("monsters"))

    def test_species_thieu_khoa(self):
        self.rejected(lambda t: t["gather"]["monsters"]["species"]["ca_sau"].pop("hit_radius"))

    def test_exit_nho_hon_detect(self):
        self.rejected(lambda t: t["gather"]["monsters"]["species"]["ca_sau"].__setitem__("exit_radius", 5))

    def test_spawn_ngoai_dai_do_sau(self):
        def m(t):
            s = t["gather"]["monsters"]["spawns"][0]
            s["pos"], s["waypoints"] = [60, 5], [[60, 5], [64, 5]]
        self.rejected(m)

    def test_waypoint_dau_khac_vi_tri(self):
        self.rejected(lambda t: t["gather"]["monsters"]["spawns"][0].__setitem__("waypoints", [[61, 24], [64, 24]]))

    def test_mot_waypoint(self):
        self.rejected(lambda t: t["gather"]["monsters"]["spawns"][0].__setitem__("waypoints", [[60, 24]]))

    def test_spawn_id_trung(self):
        self.rejected(lambda t: t["gather"]["monsters"]["spawns"][1].__setitem__("id", "M1"))

    def test_from_day_ngoai_1_5(self):
        self.rejected(lambda t: t["gather"]["monsters"]["spawns"][1].__setitem__("from_day", 6))

    def test_khong_con_nao_tu_ngay_1(self):
        self.rejected(lambda t: t["gather"]["monsters"]["spawns"][0].__setitem__("from_day", 2))

    def test_loss_ratio_ngoai_0_1(self):
        self.rejected(lambda t: t["gather"]["monsters"].__setitem__("loss_ratio", 1.5))

    # --- day_plan / shop ---
    def test_day_plan_ingredients_sai_tong(self):
        self.rejected(lambda t: t["day_plan"][0]["ingredients"].__setitem__("ca_loc", 4))

    def test_day_plan_mon_la(self):
        self.rejected(lambda t: t["day_plan"][1]["dishes"].__setitem__("pho_bo", 1))

    def test_day_plan_thieu_ngay(self):
        self.rejected(lambda t: t["day_plan"].pop())

    def test_day_plan_sai_thu_tu(self):
        def m(t):
            t["day_plan"][0], t["day_plan"][1] = t["day_plan"][1], t["day_plan"][0]
        self.rejected(m)

    def test_shop_thieu_hp(self):
        self.rejected(lambda t: t["shop"]["upgrades"].pop("hp"))

    def test_shop_cap_sai_thu_tu(self):
        self.rejected(lambda t: t["shop"]["upgrades"]["oxygen"][1].__setitem__("level", 3))

    def test_shop_gia_khong_duong(self):
        self.rejected(lambda t: t["shop"]["upgrades"]["hp"][0].__setitem__("price", 0))

    def test_shop_max_ticks_am(self):
        self.rejected(lambda t: t["shop"].__setitem__("max_ticks", -1))

    def test_menu_nhan_6_nguyen_lieu(self):
        validate_tuning(v11())
        t = v11()
        t["menu"]["lau_mam"]["recipe"]["ca_map"] = 1
        with self.assertRaises(BadInput):
            validate_tuning(t)


class ContractVersionBlackBox(unittest.TestCase):
    """contract_version lạ / v1.1 khai mà gather còn v1.0 -> headless mã 2, không tạo --out."""

    def _run(self, mutate):
        with Workdir() as w:
            root = w.path("repo")
            shutil.copytree(os.path.join(ROOT, "chonoi"), os.path.join(root, "chonoi"),
                            ignore=shutil.ignore_patterns("__pycache__"))
            with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
                c = json.load(f)
            mutate(c)
            with open(os.path.join(root, "game.contract.json"), "w", encoding="utf-8") as f:
                json.dump(c, f)
            out = os.path.join(root, "o.jsonl")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--out", out, cwd=root)
            return code, err, os.path.exists(out)

    def test_version_la_exit_2(self):
        code, err, made = self._run(lambda c: c.__setitem__("contract_version", "9.9"))
        self.assertEqual(code, 2, err)
        self.assertFalse(made)

    def test_day_plan_sai_exit_2(self):
        code, err, made = self._run(lambda c: c["tuning"]["day_plan"][0]["ingredients"].__setitem__("ca_loc", 99))
        self.assertEqual(code, 2, err)
        self.assertFalse(made)


if __name__ == "__main__":
    unittest.main()
