"""Test hộp đen luật Quán (PRD-0 mục F Quán, E sự kiện) — AC-P1-06, AC-P1-07, AC-P1-08, AC-P1-11.

Chạy qua headless_cmd nên dùng được với mọi ngôn ngữ. Số liệu đọc từ game.contract.json.
"""

import json
import math
import os
import unittest

from helpers import (INDIVIDUAL, ROOT, Workdir, counts, events, frames, kinds, read_jsonl, run_headless, snapshots,
                     stock, write_json)

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]
Q = TUNING["quan"]
MENU = TUNING["menu"]
FIRST = Q["first_customer_tick"]
PATIENCE = int(round(Q["patience_s"] * 60))
EAT = int(round(Q["eat_s"] * 60))
INTERVAL = int(round(Q["customer_interval_s"] * 60))
STOVE = Q["stoves"][0]
TABLE = Q["tables"][0]


def v12(block):
    """v1.2 (Ticket-03): fixture viết theo kho đếm -> kho cá thể; reserved rỗng -> mảng rỗng."""
    b = dict(block)
    if "stock" in b:
        b["stock"] = stock(b["stock"])
    if INDIVIDUAL:
        b["customers"] = [dict(c, reserved=[]) if c.get("reserved") == {} else c for c in b.get("customers", [])]
    return b


def cooked_price(price, aged_ticks=1):
    """v1.2: giá chốt theo tươi lúc nấu; cá thể fresh 100 đã hao `aged_ticks` tick ở quán (1 đơn vị/tick)."""
    return (price * (24000 - aged_ticks)) // 24000 if INDIVIDUAL else price


def rcounts(snap, c):
    """Phần giữ của khách -> {kind: n} (v1.1 map / v1.2 mảng id tra trong snapshot stock)."""
    r = c["reserved"]
    if isinstance(r, dict):
        return r
    kind = {it["id"]: it["kind"] for it in snap["stock"]}
    return counts([{"kind": kind[i]} for i in r])


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


def waiting(dish="ca_loc_nuong_trui", **kw):
    c = {"id": "C1", "table_id": TABLE["id"], "dish_id": dish}
    c.update(kw)
    return c


class QuanCustomers(unittest.TestCase):
    """AC-P1-06: khách theo lịch, bàn trống, chọn món khả dụng, giữ chỗ, no_dish."""

    def test_khach_den_dung_first_customer_tick_va_giu_cho(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}}, ticks=FIRST + 1)
            ev = events(rows, "customer_arrived")
            self.assertEqual(len(ev), 1)
            self.assertEqual(ev[0]["tick"], FIRST)
            self.assertEqual(ev[0]["data"], {"order_id": "C1", "table_id": TABLE["id"], "dish_id": "ca_loc_nuong_trui"})
            snap = [s for s in snapshots(rows) if s["tick"] == FIRST][0]
            c = snap["customers"][0]
            self.assertEqual((c["order_tick"], c["state"], c["order_status"]), (FIRST, "waiting", "reserved"))
            self.assertEqual(rcounts(snap, c), {"ca_loc": 1})
            self.assertEqual(c["patience_ticks_left"], PATIENCE)
            self.assertEqual(counts(snap["stock"]), {"ca_loc": 1})  # kho vật lý vẫn gồm phần giữ
            self.assertEqual(snap["tables"][0]["customer_id"], "C1")

    def test_kien_nhan_giam_tu_buoc_sau(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}}, ticks=FIRST + 2)
            snap = [s for s in snapshots(rows) if s["tick"] == FIRST + 2][0]
            self.assertEqual(snap["customers"][0]["patience_ticks_left"], PATIENCE - 2)

    def test_no_dish_khi_co_ban_ma_thieu_mon(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"bong_sung": 1}}, ticks=FIRST + 1)
            ev = events(rows, "no_dish")
            self.assertEqual([(e["tick"], e["data"]) for e in ev], [(FIRST, {})])
            self.assertEqual(events(rows, "customer_arrived"), [])

    def test_het_ban_thi_bo_luot_khong_su_kien(self):
        # v1.1 (Ticket-02): 4 bàn T1–T4 -> dựng khách fixture kín mọi bàn (trước đây 1 bàn T1 là đủ).
        busy = [{"id": f"C{i}", "table_id": tb["id"], "dish_id": "ca_loc_nuong_trui"}
                for i, tb in enumerate(Q["tables"], 1)]
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": len(busy) + 1}, "customers": busy}, ticks=FIRST + 1)
            self.assertEqual(events(rows, "customer_arrived"), [])
            self.assertEqual(events(rows, "no_dish"), [])

    def test_random_customers_false_tat_khach_tu_sinh(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "random_customers": False}, ticks=FIRST + 1)
            self.assertEqual(events(rows, "customer_arrived") + events(rows, "no_dish"), [])

    def test_fixture_reserved_mac_dinh_theo_cong_thuc(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_linh": 3, "bong_dien_dien": 1}, "random_customers": False,
                                "customers": [waiting("lau_ca_linh_dien_dien")]}, ticks=0)
            c = snapshots(rows)[0]["customers"][0]
            self.assertEqual(rcounts(snapshots(rows)[0], c), {"bong_dien_dien": 1, "ca_linh": 3})
            self.assertEqual((c["state"], c["order_status"], c["order_tick"], c["patience_ticks_left"]),
                             ("waiting", "reserved", 0, PATIENCE))

    def test_cung_seed_cung_byte(self):
        stock = {"ca_loc": 5, "bong_sung": 10, "ca_linh": 9, "bong_dien_dien": 3}
        outs = []
        for _ in range(2):
            with Workdir() as w:
                run_quan(w, {"stock": stock}, ticks=3000, seed=7)
                with open(w.path("q.jsonl"), "rb") as f:
                    outs.append(f.read())
        self.assertEqual(outs[0], outs[1])


class QuanService(unittest.TestCase):
    """AC-P1-07, AC-P1-08: nấu, bưng, phục vụ, boa, trả tiền, rời bàn, đóng ca."""

    def fixture(self, **kw):
        b = {"stock": {"ca_loc": 1}, "random_customers": False, "player": {"pos": list(STOVE["pos"])},
             "customers": [waiting()]}
        b.update(kw)
        return b

    def test_vong_phuc_vu_day_du_co_boa(self):
        cook = int(round(MENU["ca_loc_nuong_trui"]["cook_s"] * 60))
        price = MENU["ca_loc_nuong_trui"]["price"]
        serve_at = cook + 5
        with Workdir() as w:
            # đứng ở bếp: bước 0 nấu, chín sau `cook` tick, bước cook+1 bưng lên tay
            rows = run_quan(w, self.fixture(), inputs=press(0) + press(cook + 1), ticks=cook + 3)
            names = [e["name"] for e in events(rows)]
            self.assertEqual(names, ["cook_started", "dish_ready", "dish_picked"])
            cs = events(rows, "cook_started")[0]
            self.assertEqual(cs["tick"], 1)
            # v1.2: items là mảng cá thể, giá chốt theo tươi (đã hao 1 tick) — Ticket-03 [THAY THẾ]
            self.assertEqual(kinds(cs["data"].pop("items")), ["ca_loc"])
            self.assertEqual(cs["data"], {"stove_id": STOVE["id"], "order_id": "C1", "dish_id": "ca_loc_nuong_trui",
                                          "base_price": cooked_price(price)})
            self.assertEqual(events(rows, "dish_ready")[0]["tick"], 1 + cook)
            last = snapshots(rows)[-1]
            self.assertEqual(last["hand"], {"order_id": "C1", "dish_id": "ca_loc_nuong_trui",
                                            "base_price": cooked_price(price)})
            self.assertEqual(counts(last["stock"]), {})
            self.assertEqual(last["customers"][0]["order_status"], "assigned")
        # phục vụ: dựng fixture tay đang cầm món, đứng ở bàn
        hand = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": price}
        with Workdir() as w:
            rows = run_quan(w, self.fixture(stock={}, hand=hand, player={"pos": list(TABLE["pos"])},
                                            customers=[waiting(order_status="assigned", reserved={})]),
                            inputs=press(serve_at), ticks=serve_at + EAT + 2)
            sv = events(rows, "served")[0]
            tip = math.floor(price * Q["tip_rate"])
            self.assertEqual(sv["data"], {"order_id": "C1", "table_id": TABLE["id"], "dish_id": "ca_loc_nuong_trui",
                                          "patience_ticks_left": PATIENCE - serve_at - 1, "base_price": price, "tip": tip})
            pd = events(rows, "paid")[0]
            self.assertEqual(pd["tick"], serve_at + 1 + EAT)
            self.assertEqual(pd["data"], {"order_id": "C1", "table_id": TABLE["id"], "base_price": price, "tip": tip,
                                          "amount": price + tip, "reason": "finished_eating"})
            end = rows[-1]
            self.assertEqual((end["money"], end["earned"]), (price + tip, price + tip))
            self.assertAlmostEqual(end["reputation"], Q["reputation_initial"] + Q["tip_reputation"], places=6)
            self.assertEqual(snapshots(rows)[-1]["customers"], [])

    def test_boa_0_khi_kien_nhan_duoi_nguong(self):
        price = MENU["ca_loc_nuong_trui"]["price"]
        hand = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": price}
        low = int(PATIENCE * Q["tip_min_patience_ratio"]) - 10
        with Workdir() as w:
            rows = run_quan(w, self.fixture(stock={}, hand=hand, player={"pos": list(TABLE["pos"])},
                                            customers=[waiting(order_status="assigned", reserved={},
                                                               patience_ticks_left=low)]),
                            inputs=press(0), ticks=EAT + 2)
            self.assertEqual(events(rows, "served")[0]["data"]["tip"], 0)
            self.assertEqual(rows[-1]["reputation"], Q["reputation_initial"])
            self.assertEqual(rows[-1]["money"], price)

    def test_het_kien_nhan_roi_ban_tru_uy_tin(self):
        with Workdir() as w:
            rows = run_quan(w, self.fixture(customers=[waiting(patience_ticks_left=3)]), ticks=5)
            ev = events(rows, "customer_left")
            self.assertEqual(len(ev), 1)
            self.assertEqual(ev[0]["tick"], 3)
            rep = Q["reputation_initial"] + Q["left_reputation_delta"]
            self.assertEqual(ev[0]["data"], {"order_id": "C1", "table_id": TABLE["id"], "reason": "patience",
                                             "reputation": rep})
            self.assertEqual(snapshots(rows)[-1]["customers"], [])
            self.assertEqual(counts(snapshots(rows)[-1]["stock"]), {"ca_loc": 1})  # nhả phần giữ, kho không đổi

    def test_khach_roi_bo_mon_dang_nau(self):
        with Workdir() as w:
            rows = run_quan(w, self.fixture(customers=[waiting(patience_ticks_left=5)]), inputs=press(0), ticks=7)
            self.assertEqual([e["name"] for e in events(rows)], ["cook_started", "customer_left"])
            last = snapshots(rows)[-1]
            self.assertEqual((last["stoves"][0]["state"], last["stoves"][0]["dish"]), ("idle", None))
            self.assertEqual(counts(last["stock"]), {})  # nguyên liệu đã dùng không hoàn lại

    def test_dong_ca_tra_tien_closing_va_khach_cho_khong_tru_uy_tin(self):
        price = MENU["ca_loc_nuong_trui"]["price"]
        hand = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": price}
        with Workdir() as w:
            rows = run_quan(w, self.fixture(stock={}, hand=hand, player={"pos": list(TABLE["pos"])},
                                            time_left_ticks=3,
                                            customers=[waiting(order_status="assigned", reserved={})]),
                            inputs=press(0), ticks=10)
            self.assertEqual([e["name"] for e in events(rows)], ["served", "paid", "quan_end"])
            self.assertEqual(events(rows, "paid")[0]["data"]["reason"], "closing")
            self.assertEqual(rows[-1]["reason"], "time")
        with Workdir() as w:
            rows = run_quan(w, self.fixture(time_left_ticks=2), ticks=10)
            left = events(rows, "customer_left")[0]
            self.assertEqual((left["tick"], left["data"]["reason"]), (2, "closing"))
            self.assertEqual(left["data"]["reputation"], Q["reputation_initial"])
            end = events(rows, "quan_end")[0]["data"]
            self.assertEqual(end, {"reason": "time", "money": 0, "earned": 0, "shift_earned": 0,
                                   "reputation": Q["reputation_initial"]})

    def test_bep_dang_nau_khong_tuong_tac_va_ban_khong_khop_bo_luot(self):
        with Workdir() as w:
            rows = run_quan(w, self.fixture(), inputs=press(0) + press(5), ticks=8)
            self.assertEqual([e["name"] for e in events(rows)], ["cook_started"])
        with Workdir() as w:  # tay trống ở bàn -> không phục vụ
            rows = run_quan(w, self.fixture(player={"pos": list(TABLE["pos"])}), inputs=press(0), ticks=2)
            self.assertEqual(events(rows), [])

    def test_snapshot_quan_player_co_vel(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {}}, inputs=[{"tick": 0, "move": [1, 0]}], ticks=6)
            p = snapshots(rows)[-1]["player"]
            self.assertEqual(set(p), {"pos", "vel"})
            self.assertAlmostEqual(p["vel"][0], Q["walk_speed"], places=3)


if __name__ == "__main__":
    unittest.main()
