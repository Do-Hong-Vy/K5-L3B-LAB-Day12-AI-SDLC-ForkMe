"""CP2 (QA) — AC-P2-11 (scenario v1.1) và phần inputs của AC-P2-10 (Ticket-02 mục 4.2, 4.3).

Gọi thẳng load_scenario / load_frames với tuning v1.1 chuẩn (test_contract_v11.v11()) vì headless chưa chạy
--mode day / gather v1.1. Khi lát L1/L4 ghép xong, các ca này nên có thêm bản hộp đen qua headless_cmd.
"""

import copy
import unittest

from helpers import Workdir, frames, hold, kinds, write_json
from test_contract_v11 import v11

from chonoi.errors import BadInput
from chonoi.inputs import BUTTONS_V10, BUTTONS_V11, InputPlayer, load_frames
from chonoi.scenario import load_scenario

T = v11()
G = T["gather"]
SP = G["monsters"]["species"]["ca_sau"]


def m1(**kw):
    m = {"id": "M1", "kind": "ca_sau", "pos": [60, 24], "waypoints": [[60, 24], [64, 24]]}
    m.update(kw)
    return m


def load(data, mode, tuning=T):
    with Workdir() as w:
        return load_scenario(write_json(w.path("sc.json"), data), mode, tuning)


class GatherV11(unittest.TestCase):
    def ok(self, block):
        return load({"gather": block}, "gather")

    def bad(self, block, mode="gather"):
        with self.assertRaises(BadInput):
            load({"gather": block} if mode == "gather" else block, mode)

    def test_hop_le(self):
        self.ok({"player": {"pos": [60, 22], "invuln_ticks": 30},
                 "hold": hold(["ca_keo", "keo_neo", "ca_loc"]),
                 "nodes": [{"id": "N5", "kind": "keo_neo", "pos": [76, 0], "regrow_ticks": 5}],
                 "fish": [{"id": "F1", "kind": "ca_keo", "pos": [40, 25], "heading_deg": 90, "age_ticks": 119}],
                 "monsters": [m1(), m1(id="M9", pos=[62, 24], state="recoil", state_ticks_left=10,
                                   recoil_dir=[0.6, 0.8], target_idx=0)],
                 "random_fish": True})

    def test_monsters_rong_hop_le(self):
        self.ok({"monsters": []})

    def test_age_ticks_am(self):
        self.bad({"fish": [{"id": "F1", "kind": "ca_linh", "pos": [40, 5], "age_ticks": -1}]})

    def test_fish_truong_la(self):
        self.bad({"fish": [{"id": "F1", "kind": "ca_linh", "pos": [40, 5], "speed": 3}]})

    def test_node_truong_la(self):
        self.bad({"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [12, 0], "ready": True}]})

    def test_loai_ca_la(self):
        self.bad({"fish": [{"id": "F1", "kind": "ca_map", "pos": [40, 5]}]})

    def test_invuln_vuot_tran(self):
        self.bad({"player": {"invuln_ticks": G["monsters"]["invuln_ticks"] + 1}})

    def test_attack_cd_chua_bat_lao(self):
        self.bad({"player": {"attack_cd_ticks": 0}})

    def test_ca_ho_chua_bat_so_tay(self):
        self.bad({"ca_ho": None})

    # --- monsters[] ---
    def test_monster_id_trung(self):
        self.bad({"monsters": [m1(), m1()]})

    def test_monster_kind_la(self):
        self.bad({"monsters": [m1(kind="ran")]})

    def test_monster_truong_la(self):
        self.bad({"monsters": [m1(hp=3)]})

    def test_monster_ngoai_dai_do_sau(self):
        self.bad({"monsters": [m1(pos=[60, 5])]})

    def test_monster_waypoint_ngoai_ban_do(self):
        self.bad({"monsters": [m1(waypoints=[[60, 24], [120, 24]])]})

    def test_monster_mot_waypoint(self):
        self.bad({"monsters": [m1(waypoints=[[60, 24]])]})

    def test_target_idx_2(self):
        self.bad({"monsters": [m1(target_idx=2)]})

    def test_state_stunned_chua_bat_lao(self):
        self.bad({"monsters": [m1(state="stunned", state_ticks_left=10)]})

    def test_recoil_timer_0(self):
        self.bad({"monsters": [m1(state="recoil", state_ticks_left=0, recoil_dir=[1, 0])]})

    def test_recoil_timer_vuot(self):
        self.bad({"monsters": [m1(state="recoil", state_ticks_left=SP["recoil_ticks"] + 1, recoil_dir=[1, 0])]})

    def test_recoil_thieu_huong(self):
        self.bad({"monsters": [m1(state="recoil", state_ticks_left=5)]})

    def test_recoil_huong_khong_don_vi(self):
        self.bad({"monsters": [m1(state="recoil", state_ticks_left=5, recoil_dir=[2, 0])]})

    def test_patrol_co_recoil_dir(self):
        self.bad({"monsters": [m1(recoil_dir=[1, 0])]})

    def test_patrol_co_timer(self):
        self.bad({"monsters": [m1(state_ticks_left=3)]})

    def test_monsters_khi_tuning_khong_co_quai(self):
        t = copy.deepcopy(T)
        t["gather"].pop("monsters")
        with self.assertRaises(BadInput):
            load({"gather": {"monsters": []}}, "gather", t)


class DayScenario(unittest.TestCase):
    def bad(self, data):
        with self.assertRaises(BadInput):
            load(data, "day")

    def test_vi_du_ticket_hop_le(self):
        sc = load({"day": {"money": 200, "earned": 200},
                   "gather": {"hold": hold(["ca_loc", "bong_sung", "bong_sung"]), "random_fish": False}}, "day")
        self.assertEqual(sc["day"], {"money": 200, "earned": 200})
        self.assertEqual(kinds(sc["gather"]["hold"]), ["ca_loc", "bong_sung", "bong_sung"])
        self.assertEqual(sc.get("quan", {}), {})

    def test_day_day_du_hop_le(self):
        load({"day": {"money": 100, "earned": 500, "reputation": 4.5, "upgrades": {"oxygen": 2, "hp": 0},
                      "day_plan": [{"day": 2, "dishes": {"ca_keo_nuong": 3}, "ingredients": {"ca_keo": 6}}]},
              "quan": {"time_left_ticks": 100}}, "day")

    def test_cam_quan_stock(self):
        self.bad({"quan": {"stock": {"ca_loc": 1}}})

    def test_cam_quan_reputation(self):
        self.bad({"quan": {"reputation": 3}})

    def test_khoi_la(self):
        self.bad({"shop": {}})

    def test_day_truong_la(self):
        self.bad({"day": {"days": 3}})

    def test_money_lon_hon_earned(self):
        self.bad({"day": {"money": 300, "earned": 200}})

    def test_money_khong_khai_earned(self):
        self.bad({"day": {"money": 50}})

    def test_money_am(self):
        self.bad({"day": {"money": -1, "earned": 0}})

    def test_uy_tin_ngoai_khoang(self):
        self.bad({"day": {"reputation": 6}})

    def test_nang_cap_la(self):
        self.bad({"day": {"upgrades": {"weapon": 1}}})

    def test_nang_cap_vuot_cap_toi_da(self):
        self.bad({"day": {"upgrades": {"hp": 3}}})

    def test_day_plan_ingredients_sai(self):
        self.bad({"day": {"day_plan": [{"day": 1, "dishes": {"goi_bong_sung": 1}, "ingredients": {"bong_sung": 3}}]}})

    def test_day_plan_mon_la(self):
        self.bad({"day": {"day_plan": [{"day": 1, "dishes": {"pho": 1}}]}})

    def test_day_plan_thieu_dishes(self):
        self.bad({"day": {"day_plan": [{"day": 1}]}})

    def test_day_plan_ngay_trung(self):
        self.bad({"day": {"day_plan": [{"day": 1, "dishes": {"goi_bong_sung": 1}},
                                       {"day": 1, "dishes": {"goi_bong_sung": 2}}]}})

    def test_day_plan_ngay_6(self):
        self.bad({"day": {"day_plan": [{"day": 6, "dishes": {"goi_bong_sung": 1}}]}})

    def test_gather_mau_van_duoc_kiem(self):
        self.bad({"gather": {"hold": ["ca_map"]}})

    def test_mode_doc_lap_khong_nhan_khoi_day(self):
        with self.assertRaises(BadInput):
            load({"day": {}}, "gather")


class InputsV11(unittest.TestCase):
    """inputs v1.1 (Ticket-02 4.2) — API của chonoi/inputs.py (lát L4, Cuubeo): mặc định BUTTONS_V11, state.buy."""

    def test_nut_v11(self):
        self.assertEqual(BUTTONS_V11, ("interact", "catch", "pause", "shop_done"))

    def test_bo_nut_v10_tu_choi_pause(self):
        with Workdir() as w, self.assertRaises(BadInput):
            load_frames(write_json(w.path("i.json"), frames({"tick": 0, "pause": True})), BUTTONS_V10)

    def test_pause_shop_done_buy(self):
        with Workdir() as w:
            fr = load_frames(write_json(w.path("i.json"), frames({"tick": 0, "pause": True},
                                                                 {"tick": 1, "shop_done": True, "buy": "oxygen"})))
        pl = InputPlayer(fr)
        s0 = pl.advance(0)
        self.assertTrue(s0.pressed("pause"))
        self.assertIsNone(s0.buy)
        s1 = pl.advance(1)
        self.assertTrue(s1.pressed("shop_done"))
        self.assertFalse(s1.pressed("pause"))  # giữ nút không tạo cạnh mới
        self.assertEqual(s1.buy, "oxygen")
        self.assertIsNone(pl.advance(2).buy)  # buy chỉ chạy tại frame khai báo

    def test_buy_phai_la_chuoi_khac_rong(self):
        for bad in ("", 1, True, None):
            with self.subTest(bad), Workdir() as w, self.assertRaises(BadInput):
                load_frames(write_json(w.path("i.json"), frames({"tick": 0, "buy": bad})))

    def test_buy_lenh_la_van_hop_le_o_inputs(self):
        # lệnh không hỗ trợ không phải lỗi input: Shop phát buy_failed(unknown) (Ticket-02 4.2)
        with Workdir() as w:
            load_frames(write_json(w.path("i.json"), frames({"tick": 0, "buy": "rocket"})))

    def test_attack_photo_van_bi_tu_choi(self):
        for b in ("attack", "photo"):
            with self.subTest(b), Workdir() as w, self.assertRaises(BadInput):
                load_frames(write_json(w.path("i.json"), frames({"tick": 0, b: True})))

    def test_pause_phai_boolean(self):
        with Workdir() as w, self.assertRaises(BadInput):
            load_frames(write_json(w.path("i.json"), frames({"tick": 0, "pause": 1})))


if __name__ == "__main__":
    unittest.main()
