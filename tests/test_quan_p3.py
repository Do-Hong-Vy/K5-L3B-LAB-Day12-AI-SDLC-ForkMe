"""Phase 3 phía Quán (Ticket-03) — AC-P3-03, 04, 05: kho cá thể, hao tươi, ươn, giữ theo id, giá theo tươi.

Contract đang chạy vẫn v1.1 cho tới khi gather + adapter sẵn sàng (ADR-0002) -> test dựng tuning v1.2 bằng
cách thêm khối `freshness` theo Ticket-03 rồi gọi QuanSim trực tiếp.
"""

import copy
import json
import math
import os
import unittest

from helpers import ROOT

from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    BASE = json.load(f)["tuning"]
T = copy.deepcopy(BASE)
T.setdefault("freshness", {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30})
Q, MENU = T["quan"], T["menu"]
STOVE = Q["stoves"][0]["pos"]
IDLE = InputState((0.0, 0.0), set(), set())
PRESS = InputState((0.0, 0.0), {"interact"}, {"interact"})
TICK_DECAY = T["freshness"]["quan_decay_per_s"] / 60  # 0.25/s


def it(i, kind, fresh):
    return {"id": i, "kind": kind, "fresh": fresh}


def sim(stock, customers=(), pos=None, **kw):
    sc = {"stock": list(stock), "random_customers": False, "customers": list(customers)}
    sc.update(kw)
    s = QuanSim(T, sc, Streams(1), IdAllocator())
    if pos:
        s.pos = [float(c) for c in pos]
    return s


def cust(dish, **kw):
    c = {"id": "C1", "table_id": "T1", "dish_id": dish}
    c.update(kw)
    return c


class Stock(unittest.TestCase):
    def test_snapshot_kho_ca_the_sap_theo_id(self):
        s = sim([it("I2", "ca_loc", 97.5), it("I10", "ca_linh", 100), it("I1", "ca_linh", 50)])
        self.assertEqual(s.snapshot()["stock"], [it("I1", "ca_linh", 50.0), it("I2", "ca_loc", 97.5),
                                                 it("I10", "ca_linh", 100.0)])

    def test_hao_025_moi_giay_ke_ca_hang_giu(self):
        s = sim([it("I1", "ca_loc", 100)], [cust("ca_loc_nuong_trui")])
        for _ in range(60):
            s.step(IDLE)
        self.assertAlmostEqual(s.snapshot()["stock"][0]["fresh"], 100 - 0.25, places=6)
        self.assertEqual(s.snapshot()["customers"][0]["reserved"], ["I1"])

    def test_uon_phat_spoiled_dung_mot_lan_theo_id(self):
        s = sim([it("I2", "ca_linh", 30), it("I1", "ca_loc", 30), it("I3", "bong_sung", 31)])
        ev = s.step(IDLE)
        self.assertEqual(ev, [("spoiled", {"item_id": "I1", "kind": "ca_loc", "location": "stock"}),
                              ("spoiled", {"item_id": "I2", "kind": "ca_linh", "location": "stock"})])
        self.assertEqual([e for e in s.step(IDLE) if e[0] == "spoiled"], [])  # không phát lại
        self.assertEqual(len(s.snapshot()["stock"]), 3)  # hàng ươn vẫn trong kho

    def test_nguong_chinh_xac_khong_sai_so_thuc(self):
        # fresh 30 + đúng 1 tick hao -> ươn ở bước 1; fresh 30 + 1 đơn vị (1/240) -> chưa ươn ở bước 1
        s = sim([it("I1", "ca_loc", 30 + 1 / 240)])
        self.assertEqual(s.step(IDLE), [])
        self.assertEqual(s.step(IDLE)[0][0], "spoiled")


class Reserve(unittest.TestCase):
    def test_giu_ca_the_tuoi_nhat_hoa_theo_id(self):
        s = sim([it("I3", "ca_loc", 80), it("I1", "ca_loc", 90), it("I2", "ca_loc", 90)], [cust("ca_loc_nuong_trui")])
        self.assertEqual(s.snapshot()["customers"][0]["reserved"], ["I1"])

    def test_khach_moi_khong_dung_hang_uon(self):
        s = QuanSim(T, {"stock": [it("I1", "ca_loc", 20)]}, Streams(1), IdAllocator())
        ev = []
        for _ in range(Q["first_customer_tick"]):
            ev += s.step(IDLE)
        self.assertEqual(ev[-1], ("no_dish", {}))

    def test_hang_giu_vua_uon_thi_giu_lai_mot_lan(self):
        s = sim([it("I1", "ca_loc", 30), it("I2", "ca_loc", 60)], [cust("ca_loc_nuong_trui", reserved=["I1"])])
        s.step(IDLE)
        c = s.snapshot()["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I2"]))

    def test_giu_lai_khong_du_thi_unfulfillable(self):
        s = sim([it("I1", "ca_loc", 30)], [cust("ca_loc_nuong_trui", reserved=["I1"])])
        s.step(IDLE)
        c = s.snapshot()["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"], c["state"]), ("unfulfillable", [], "waiting"))


class Price(unittest.TestCase):
    def test_gia_theo_tuoi_va_items_ca_the(self):
        # canh chua 90: ca_loc 100 + bong_dien_dien 50 -> sau 1 tick hao ở bước nấu
        s = sim([it("I2", "ca_loc", 100), it("I1", "bong_dien_dien", 50)], [cust("canh_chua_ca_loc")], pos=STOVE)
        ev = s.step(PRESS)
        cs = [e for e in ev if e[0] == "cook_started"][0][1]
        f1, f2 = 50 - TICK_DECAY, 100 - TICK_DECAY
        self.assertEqual([(x["id"], x["kind"]) for x in cs["items"]], [("I1", "bong_dien_dien"), ("I2", "ca_loc")])
        self.assertAlmostEqual(cs["items"][0]["fresh"], f1, places=6)
        want = math.floor(MENU["canh_chua_ca_loc"]["price"] * ((f1 + f2) / 2) / 100)
        self.assertEqual(cs["base_price"], want)
        self.assertEqual(s.snapshot()["stock"], [])  # tiêu đúng các id đang giữ
        self.assertEqual(s.snapshot()["stoves"][0]["dish"]["base_price"], want)

    def test_hang_tuoi_100_giu_gia_niem_yet(self):
        s = sim([it("I1", "ca_loc", 100)], [cust("ca_loc_nuong_trui")], pos=STOVE)
        s.fresh.decay = 0  # cô lập phép tính giá: không hao
        cs = [e for e in s.step(PRESS) if e[0] == "cook_started"][0][1]
        self.assertEqual(cs["base_price"], MENU["ca_loc_nuong_trui"]["price"])


class V11Unchanged(unittest.TestCase):
    def test_khong_co_freshness_thi_kho_dem_nhu_cu(self):
        s = QuanSim(BASE, {"stock": {"ca_loc": 1}}, Streams(1), IdAllocator()) if "freshness" not in BASE else None
        if s is None:
            self.skipTest("contract đã ở v1.2")
        self.assertEqual(s.snapshot()["stock"], {"ca_loc": 1})


if __name__ == "__main__":
    unittest.main()
