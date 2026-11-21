"""Lát 3 Phase 2 (Ticket-02 mục 1.3, 2) — AC-P2-06, AC-P2-07: 2 bếp / 4 bàn / 6 món, kế hoạch ngày.

Số liệu đọc từ game.contract.json. Test hộp đen qua headless_cmd; riêng lọc menu theo kế hoạch gọi QuanSim
trực tiếp (lát này chưa có --mode day).
"""

import json
import os
import unittest

from helpers import INDIVIDUAL, ROOT, Workdir, counts, events, frames, read_jsonl, run_headless, snapshots, stock, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]
Q, MENU = TUNING["quan"], TUNING["menu"]
FIRST = Q["first_customer_tick"]
INTERVAL = int(round(Q["customer_interval_s"] * 60))


def v12(block):
    """v1.2 (Ticket-03): fixture kho đếm -> kho cá thể; reserved rỗng -> mảng rỗng."""
    b = dict(block)
    if "stock" in b:
        b["stock"] = stock(b["stock"])
    if INDIVIDUAL:
        b["customers"] = [dict(c, reserved=[]) if c.get("reserved") == {} else c for c in b.get("customers", [])]
    return b


def run_quan(w, block, inputs=None, ticks=200, seed=1):
    sc = write_json(w.path("sc.json"), {"quan": v12(block)})
    args = ["--mode", "quan", "--seed", str(seed), "--scenario", sc, "--ticks", str(ticks),
            "--out", w.path("q.jsonl"), "--snapshot-every", "1"]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path("q.jsonl"))


def press(tick):
    return [{"tick": tick, "interact": True}, {"tick": tick + 1, "interact": False}]


class Data(unittest.TestCase):
    def test_so_chuan_bep_ban_mon(self):
        self.assertEqual([(s["id"], s["pos"]) for s in Q["stoves"]], [("B1", [2, 8]), ("B2", [5, 8])])
        self.assertEqual([(t["id"], t["pos"]) for t in Q["tables"]],
                         [("T1", [9, 2]), ("T2", [13, 2]), ("T3", [9, 6]), ("T4", [13, 6])])
        self.assertEqual(sorted(MENU), sorted(["ca_loc_nuong_trui", "goi_bong_sung", "lau_ca_linh_dien_dien",
                                               "canh_chua_ca_loc", "ca_keo_nuong", "lau_mam"]))
        self.assertEqual(MENU["lau_mam"], {"recipe": {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1},
                                           "cook_s": 12, "price": 200})

    def test_day_plan_ingredients_bang_tong_cong_thuc(self):
        plan = TUNING["day_plan"]
        self.assertEqual([p["day"] for p in plan], [1, 2, 3, 4, 5])
        for p in plan:
            need = {}
            for dish, n in p["dishes"].items():
                for k, q in MENU[dish]["recipe"].items():
                    need[k] = need.get(k, 0) + q * n
            self.assertEqual(p["ingredients"], need, "Ngày %d" % p["day"])
        self.assertEqual(plan[0]["ingredients"], {"ca_loc": 3, "bong_sung": 6})

    def test_shop_theo_du_lieu(self):
        up = TUNING["shop"]["upgrades"]
        self.assertEqual(TUNING["shop"]["max_ticks"], 600)
        self.assertEqual([(u["level"], u["price"], u["oxygen_max_s"]) for u in up["oxygen"]], [(1, 200, 45), (2, 400, 60)])
        self.assertEqual([(u["level"], u["price"], u["hp_max"]) for u in up["hp"]], [(1, 250, 4), (2, 500, 5)])


class FourTablesTwoStoves(unittest.TestCase):
    def test_khach_vao_ban_trong_id_nho_nhat_lan_luot(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 4}}, ticks=FIRST + 3 * INTERVAL + 1)
            arr = events(rows, "customer_arrived")
            self.assertEqual([(e["tick"], e["data"]["table_id"], e["data"]["order_id"]) for e in arr],
                             [(FIRST + k * INTERVAL, t, f"C{k + 1}") for k, t in enumerate(["T1", "T2", "T3", "T4"])])

    def test_nguyen_lieu_moi_va_mon_moi(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_keo": 2, "keo_neo": 1}}, ticks=FIRST + 1)
            self.assertEqual(counts(snapshots(rows)[0]["stock"]), {"ca_keo": 2, "keo_neo": 1})
            self.assertEqual(events(rows, "customer_arrived")[0]["data"]["dish_id"], "ca_keo_nuong")

    def test_hai_bep_nau_song_song_hoa_theo_id(self):
        # [3.5, 8] cách đều B1 [2,8] và B2 [5,8] (1.5 m, đúng mép) -> hòa theo id: B1 trước; B1 đang nấu
        # thì interact sau chọn lại B1 (không tương tác được) -> bỏ lượt; bước tới đứng sát B2 để nấu đơn 2.
        two = [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"},
               {"id": "C2", "table_id": "T2", "dish_id": "goi_bong_sung"}]
        block = {"stock": {"ca_loc": 1, "bong_sung": 2}, "random_customers": False, "customers": two,
                 "player": {"pos": [3.5, 8]}}
        with Workdir() as w:
            rows = run_quan(w, block, inputs=press(0) + press(2), ticks=4)
            self.assertEqual([(e["data"]["stove_id"], e["data"]["order_id"]) for e in events(rows, "cook_started")],
                             [("B1", "C1")])
        block["player"] = {"pos": [5, 8]}
        block["stoves"] = [{"id": "B1", "state": "cooking", "cook_ticks_left": 100,
                            "dish": {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}}]
        block["stock"] = {"bong_sung": 2}
        block["customers"] = [dict(two[0], order_status="assigned", reserved={}), two[1]]
        with Workdir() as w:
            rows = run_quan(w, block, inputs=press(0), ticks=2)
            self.assertEqual([(e["data"]["stove_id"], e["data"]["order_id"]) for e in events(rows, "cook_started")],
                             [("B2", "C2")])
            self.assertEqual([s["state"] for s in snapshots(rows)[-1]["stoves"]], ["cooking", "cooking"])

    def test_bep_truoc_ban_khi_cach_deu(self):
        # dời T1 về [2,6] (scenario cập nhật bàn theo id): đứng [2,7] cách đều B1 và T1 -> chọn bếp
        cust = [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "random_customers": False, "customers": cust,
                                "tables": [{"id": "T1", "pos": [2, 6]}], "player": {"pos": [2, 7]}},
                            inputs=press(0), ticks=2)
            self.assertEqual([e["name"] for e in events(rows)], ["cook_started"])


class PlanFilter(unittest.TestCase):
    """AC-P2-07: trong day chỉ chọn món của kế hoạch (QuanSim nhận dish_ids); quán độc lập dùng cả 6 món."""

    def _spawn(self, dish_ids, stock_counts):
        from chonoi.ids import IdAllocator
        from chonoi.inputs import InputState
        from chonoi.rng import Streams
        from chonoi.sim.quan import QuanSim
        sim = QuanSim(TUNING, v12({"stock": stock_counts}), Streams(1), IdAllocator(), dish_ids=dish_ids)
        idle = InputState((0.0, 0.0), set(), set())
        out = []
        for _ in range(FIRST):
            out += sim.step(idle)
        return out

    def test_chi_mon_trong_ke_hoach(self):
        d1 = list(TUNING["day_plan"][0]["dishes"])  # ca_loc_nuong_trui, goi_bong_sung
        self.assertEqual(self._spawn(d1, {"ca_keo": 2, "bong_sung": 2}),
                         [("customer_arrived", {"order_id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung"})])

    def test_mon_ngoai_ke_hoach_thi_no_dish(self):
        d1 = list(TUNING["day_plan"][0]["dishes"])
        self.assertEqual(self._spawn(d1, {"ca_keo": 2}), [("no_dish", {})])

    def test_quan_doc_lap_dung_ca_6_mon(self):
        self.assertEqual(self._spawn(None, {"ca_keo": 2})[0][1]["dish_id"], "ca_keo_nuong")


if __name__ == "__main__":
    unittest.main()
