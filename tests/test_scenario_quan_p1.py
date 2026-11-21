"""CP1-T1 / CP1-T2 (QA) — AC-P1-09, AC-P1-10, AC-P1-12.

Hộp đen qua headless_cmd:
  * scenario quán mâu thuẫn (PRD-0 mục D) -> mã 2 và KHÔNG tạo file --out;
  * fixture hợp lệ phức tạp (bếp cooking/ready, món trên tay, khách eating) -> mã 0;
  * tất định: cùng seed + đầu vào -> JSONL và file kho giống từng byte, chuỗi gather -> kho -> quan.
Số liệu đọc từ game.contract.json.
"""

import filecmp
import json
import os
import unittest

from helpers import INDIVIDUAL, ROOT, Workdir, counts, frames, hold, read_jsonl, run_headless, snapshots, stock, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]
Q, MENU = TUNING["quan"], TUNING["menu"]
STOVE, TABLE = Q["stoves"][0]["id"], Q["tables"][0]["id"]
PATIENCE = int(round(Q["patience_s"] * 60))
EAT = int(round(Q["eat_s"] * 60))
DISH = sorted(MENU)[0]
RECIPE = MENU[DISH]["recipe"]
PRICE = MENU[DISH]["price"]
COOK = int(round(MENU[DISH]["cook_s"] * 60))
OTHER_DISH = next(d for d in sorted(MENU) if MENU[d]["recipe"] != RECIPE)


def payload(order_id="C1", dish=DISH):
    return {"order_id": order_id, "dish_id": dish, "base_price": MENU[dish]["price"]}


def cust(**kw):
    c = {"id": "C1", "table_id": TABLE, "dish_id": DISH}
    c.update(kw)
    return c


def assigned(**kw):
    return cust(order_status="assigned", reserved={}, base_price=PRICE, **kw)


def cooking(dish=None, ticks=1):
    return [{"id": STOVE, "state": "cooking", "dish": dish or payload(), "cook_ticks_left": ticks}]


def v12(block):
    """v1.2 (Ticket-03): fixture kho đếm -> kho cá thể; reserved rỗng {} -> []. Mâu thuẫn khác giữ nguyên để
    vẫn kiểm mã 2 (reserved dạng map ở v1.2 cũng là sai schema -> mã 2)."""
    b = dict(block)
    if "stock" in b:
        b["stock"] = stock(b["stock"])
    if INDIVIDUAL:
        b["customers"] = [dict(c, reserved=[]) if c.get("reserved") == {} else c for c in b.get("customers", [])]
    return b


def run_quan(w, block, extra=()):
    sc = write_json(w.path("sc.json"), {"quan": v12(block)})
    out = w.path("q.jsonl")
    code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "5", "--scenario", sc, "--out", out, *extra)
    return code, err, os.path.exists(out)


class QuanScenarioRejected(unittest.TestCase):
    """AC-P1-10: mỗi mâu thuẫn mục D -> mã 2, không ghi file."""

    CASES = {
        # trường / phạm vi
        "khach_truong_la": {"stock": RECIPE, "customers": [cust(vip=True)]},
        "khach_mon_ngoai_menu": {"customers": [cust(dish_id="pho_bo")]},
        "khach_thieu_mon": {"customers": [{"id": "C1", "table_id": TABLE}]},
        "khach_state_sai": {"stock": RECIPE, "customers": [cust(state="sleeping")]},
        "order_status_sai": {"stock": RECIPE, "customers": [cust(order_status="cancelled")]},
        "kien_nhan_am": {"stock": RECIPE, "customers": [cust(patience_ticks_left=-1)]},
        "kien_nhan_vuot_tran": {"stock": RECIPE, "customers": [cust(patience_ticks_left=PATIENCE + 1)]},
        "order_tick_am": {"stock": RECIPE, "customers": [cust(order_tick=-3)]},
        "reputation_vuot_tran": {"reputation": Q["reputation_max"] + 1},
        "reputation_duoi_san": {"reputation": Q["reputation_min"] - 1},
        "random_customers_khong_bool": {"random_customers": "no"},
        # giữ chỗ
        "giu_khac_cong_thuc": {"stock": {k: v + 5 for k, v in RECIPE.items()},
                               "customers": [cust(reserved={k: v + 1 for k, v in RECIPE.items()})]},
        "giu_qua_ton_khai_reserved": {"stock": {}, "customers": [cust(reserved=dict(RECIPE))]},
        "giu_qua_ton_suy_tu_cong_thuc": {"customers": [cust()]},
        "unfulfillable_con_giu": {"stock": RECIPE, "customers": [cust(order_status="unfulfillable",
                                                                       reserved=dict(RECIPE))]},
        "nguyen_lieu_la_trong_reserved": {"stock": RECIPE, "customers": [cust(reserved={"ca_map": 1})]},
        # eating
        "eating_khong_served": {"customers": [cust(state="eating", order_status="assigned", reserved={},
                                                   eat_ticks_left=10, base_price=PRICE, tip=0)]},
        "eating_timer_0": {"customers": [cust(state="eating", order_status="served", reserved={},
                                              eat_ticks_left=0, base_price=PRICE, tip=0)]},
        "eating_thieu_tip": {"customers": [cust(state="eating", order_status="served", reserved={},
                                                eat_ticks_left=10, base_price=PRICE)]},
        "eating_vuot_tran_an": {"customers": [cust(state="eating", order_status="served", reserved={},
                                                   eat_ticks_left=EAT + 1, base_price=PRICE, tip=0)]},
        "served_ma_waiting": {"customers": [cust(order_status="served", reserved={}, base_price=PRICE, tip=0)]},
        "waiting_co_timer_an": {"stock": RECIPE, "customers": [cust(eat_ticks_left=5)]},
        # bếp
        "bep_id_khong_ton_tai": {"stoves": [{"id": "B9", "state": "idle"}]},
        "ban_id_khong_ton_tai": {"tables": [{"id": "T9", "pos": [1, 1]}]},
        "bep_truong_la": {"stoves": [{"id": STOVE, "fire": True}]},
        "bep_ngoai_mien": {"stoves": [{"id": STOVE, "pos": [999, 1]}]},
        "bep_state_sai": {"stoves": [{"id": STOVE, "state": "burnt"}]},
        "bep_idle_co_mon": {"customers": [assigned()],
                            "stoves": [{"id": STOVE, "state": "idle", "dish": payload()}]},
        "bep_cooking_timer_0": {"customers": [assigned()], "stoves": cooking(ticks=0)},
        "bep_cooking_timer_vuot_thoi_gian_nau": {"customers": [assigned()], "stoves": cooking(ticks=COOK + 1)},
        "bep_cooking_khong_mon": {"stoves": [{"id": STOVE, "state": "cooking", "cook_ticks_left": 5}]},
        "bep_ready_con_timer": {"customers": [assigned()],
                                "stoves": [{"id": STOVE, "state": "ready", "dish": payload(), "cook_ticks_left": 3}]},
        "bep_ready_ticks_am": {"customers": [assigned()],
                               "stoves": [{"id": STOVE, "state": "ready", "dish": payload(), "ready_ticks": -1}]},
        # liên kết món <-> đơn
        "mon_khong_khop_don": {"customers": [assigned()], "stoves": cooking(dish=payload(dish=OTHER_DISH))},
        "mon_cua_don_khong_ton_tai": {"stoves": cooking(dish=payload(order_id="C7"))},
        "mon_cua_don_dang_reserved": {"stock": RECIPE, "customers": [cust()], "stoves": cooking()},
        "bep_va_tay_cung_don": {"customers": [assigned()], "stoves": cooking(), "hand": payload()},
        "assigned_khong_co_mon": {"customers": [assigned()]},
        "assigned_con_giu_cho": {"stock": RECIPE, "customers": [cust(order_status="assigned",
                                                                     reserved=dict(RECIPE))], "hand": payload()},
        "hand_payload_thieu_khoa": {"customers": [assigned()], "hand": {"order_id": "C1", "dish_id": DISH}},
        "hand_mon_ngoai_menu": {"hand": {"order_id": "C1", "dish_id": "pho_bo", "base_price": 10}},
        "hand_gia_khong_duong": {"customers": [assigned()], "hand": dict(payload(), base_price=0)},
    }

    def test_moi_mau_thuan_exit_2_khong_tao_file(self):
        for name, block in self.CASES.items():
            with self.subTest(name), Workdir() as w:
                code, err, made = run_quan(w, block)
                self.assertEqual(code, 2, f"{name}: mong mã 2, được {code}; stderr={err!r}")
                self.assertFalse(made, f"{name}: không được tạo file --out")

    def test_giu_qua_ton_voi_file_inventory_exit_2(self):
        with Workdir() as w:
            inv = write_json(w.path("inv.json"), {"items": stock({})})
            code, err, made = run_quan(w, {"customers": [cust()]}, extra=("--inventory", inv))
            self.assertEqual(code, 2, err)
            self.assertFalse(made)


class QuanScenarioAccepted(unittest.TestCase):
    """Fixture hợp lệ (không được chặn nhầm) -> mã 0, snapshot tick 0 phản ánh đúng fixture."""

    def _ok(self, block, extra=()):
        with Workdir() as w:
            code, err, _ = run_quan(w, block, extra)
            self.assertEqual(code, 0, f"fixture hợp lệ bị chặn: {err}")
            return snapshots(read_jsonl(w.path("q.jsonl")))[0]

    def test_reserved_suy_tu_cong_thuc_du_ton(self):
        s0 = self._ok({"stock": RECIPE, "customers": [cust()]})
        r = s0["customers"][0]["reserved"]
        if INDIVIDUAL:  # v1.2: mảng id cá thể -> đổi về {kind: n} qua snapshot stock
            kind = {it["id"]: it["kind"] for it in s0["stock"]}
            r = counts([{"kind": kind[i]} for i in r])
        self.assertEqual(r, dict(sorted(RECIPE.items())))

    def test_reserved_du_ton_qua_file_inventory(self):
        with Workdir() as w:
            inv = write_json(w.path("inv.json"), {"items": stock(RECIPE)})
            code, err, _ = run_quan(w, {"customers": [cust()]}, extra=("--inventory", inv))
            self.assertEqual(code, 0, err)

    def test_don_assigned_dang_nau(self):
        s0 = self._ok({"customers": [assigned()], "stoves": cooking(ticks=COOK)})
        self.assertEqual(s0["stoves"][0]["state"], "cooking")

    def test_don_assigned_mon_ready_tren_bep(self):
        s0 = self._ok({"customers": [assigned()],
                       "stoves": [{"id": STOVE, "state": "ready", "dish": payload(), "ready_ticks": 4}]})
        self.assertEqual(s0["stoves"][0]["ready_ticks"], 4)

    def test_don_assigned_mon_tren_tay(self):
        s0 = self._ok({"customers": [assigned()], "hand": payload()})
        self.assertEqual(s0["hand"], payload())

    def test_khach_dang_an(self):
        s0 = self._ok({"customers": [cust(state="eating", order_status="served", reserved={},
                                          eat_ticks_left=EAT, base_price=PRICE, tip=0)]})
        self.assertEqual(s0["customers"][0]["state"], "eating")

    def test_don_unfulfillable_cho(self):
        self._ok({"customers": [cust(order_status="unfulfillable", reserved={})]})

    def test_uy_tin_dung_mep(self):
        self.assertEqual(self._ok({"reputation": Q["reputation_max"]})["reputation"], Q["reputation_max"])


class Determinism(unittest.TestCase):
    """AC-P1-12: cùng seed + đầu vào -> JSONL và file kho giống từng byte (cả chuỗi gather -> quan)."""

    def _chain(self, w, tag):
        g = TUNING["gather"]
        sc = write_json(w.path("g_sc.json"), {"gather": {"hold": hold(["ca_loc", "bong_sung", "bong_sung"])}})
        inp = write_json(w.path("g_in.json"), frames({"tick": 0, "move": [1, 0]}, {"tick": 30, "move": [0, 0]},
                                                     {"tick": 31, "interact": True}, {"tick": 32, "interact": False}))
        gout, inv = w.path(f"g_{tag}.jsonl"), w.path(f"inv_{tag}.json")
        code, err = run_headless("--mode", "gather", "--seed", "42", "--scenario", sc, "--inputs", inp,
                                 "--ticks", str(int(g["duration_s"] * 60)), "--out", gout, "--inventory-out", inv)
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.exists(inv), "gather phải kết thúc và ghi kho")
        qin = write_json(w.path("q_in.json"), frames({"tick": 0, "move": [-1, 1]}, {"tick": 200, "interact": True},
                                                     {"tick": 201, "interact": False}))
        qout = w.path(f"q_{tag}.jsonl")
        code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", inv, "--inputs", qin,
                                 "--ticks", "3000", "--out", qout)
        self.assertEqual(code, 0, err)
        return gout, inv, qout

    def test_chuoi_gather_kho_quan_giong_tung_byte(self):
        with Workdir() as w:
            a, b = self._chain(w, "a"), self._chain(w, "b")
            for x, y in zip(a, b):
                self.assertTrue(filecmp.cmp(x, y, shallow=False), f"{os.path.basename(x)} khác byte")

    def test_seed_khac_van_hop_le(self):
        with Workdir() as w:
            for seed in ("-7", "0", "9007199254740991"):
                code, err = run_headless("--mode", "quan", "--seed", seed, "--ticks", "100",
                                         "--out", w.path(f"q{seed}.jsonl"))
                self.assertEqual(code, 0, f"seed {seed}: {err}")


if __name__ == "__main__":
    unittest.main()
