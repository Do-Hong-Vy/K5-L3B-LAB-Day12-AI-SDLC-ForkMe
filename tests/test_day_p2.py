"""Lát 4 Phase 2 (Ticket-02 mục 2, 4.1–4.5) — AC-P2-08, 09, 10, 14: --mode day, Shop, pause.

Hộp đen qua headless_cmd. Số liệu đọc từ game.contract.json.
"""

import json
import os
import time
import unittest

from helpers import ROOT, Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]
G, Q, SHOP = TUNING["gather"], TUNING["quan"], TUNING["shop"]
GT = int(round(G["duration_s"] * 60))
QT = int(round(Q["duration_s"] * 60))
DAY_TICKS = GT + QT + SHOP["max_ticks"]  # 22.200


def run_day(w, *args, scenario=None, inputs=None, ticks=None, days=None, every=10):
    a = ["--mode", "day", "--seed", "1", "--out", w.path("d.jsonl"), "--snapshot-every", str(every),
         "--ticks", str(ticks if ticks is not None else DAY_TICKS * (days or 1) + 10)]
    if days is not None:
        a += ["--days", str(days)]
    if scenario is not None:
        a += ["--scenario", write_json(w.path("sc.json"), scenario)]
    if inputs is not None:
        a += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*a, *args)
    return code, err, (read_jsonl(w.path("d.jsonl")) if code == 0 else None)


def names(rows):
    return [(e["tick"], e["phase"], e.get("day"), e["name"]) for e in events(rows) if e["name"] != "no_dish"
            and e["name"] not in ("customer_arrived", "customer_left")]


DOCK = {"day": {"money": 1000, "earned": 1000}, "gather": {"hold": ["ca_loc", "bong_sung", "bong_sung"], "random_fish": False}}
DOCK_IN = [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}]


class DayFlow(unittest.TestCase):
    def test_mot_ngay_khong_input_dung_22200_tick_va_thu_tu_doi_pha(self):
        with Workdir() as w:
            code, err, rows = run_day(w)
            self.assertEqual(code, 0, err)
            self.assertEqual(names(rows), [
                (0, "gather", 1, "day_start"), (0, "gather", 1, "day_plan"), (0, "gather", 1, "phase_start"),
                (GT, "gather", 1, "gather_end"), (GT, "quan", 1, "phase_start"),
                (GT + QT, "quan", 1, "quan_end"), (GT + QT, "shop", 1, "phase_start"),
                (DAY_TICKS, "shop", 1, "shop_end")])
            end = rows[-1]
            self.assertEqual((end["mode"], end["reason"], end["days_completed"], end["ticks"]),
                             ("day", "days_complete", 1, DAY_TICKS))
            plan = events(rows, "day_plan")[0]
            self.assertEqual(plan["data"], {k: TUNING["day_plan"][0][k] for k in ("dishes", "ingredients")})

    def test_snapshot_day_co_truong_xuyen_ngay(self):
        with Workdir() as w:
            _, _, rows = run_day(w, ticks=0)
            s = snapshots(rows)[0]
            self.assertEqual((s["mode"], s["phase"], s["phase_tick"], s["day"]), ("day", "gather", 0, 1))
            self.assertEqual((s["upgrades"], s["active_upgrades"]), ({}, {}))
            self.assertIn("day_plan", s)
            self.assertEqual(rows[0]["name"], "day_start")  # event dựng Ngày trước snapshot tick 0

    def test_ban_giao_kho_trong_bo_nho_va_ke_hoach_loc_mon(self):
        with Workdir() as w:
            _, err, rows = run_day(w, scenario=DOCK, inputs=DOCK_IN, ticks=2, every=1)
            self.assertEqual(events(rows, "gather_end")[0]["data"]["inventory"], {"items": {"bong_sung": 2, "ca_loc": 1}})
            q = snapshots(rows)[-1]
            self.assertEqual((q["phase"], q["phase_tick"], q["stock"]), ("quan", 1, {"bong_sung": 2, "ca_loc": 1}))
            self.assertEqual((q["money"], q["earned"]), (1000, 1000))

    def test_ke_hoach_D1_D5_va_lap_lai(self):
        with Workdir() as w:
            _, _, rows = run_day(w, days=5)
            plans = [e["data"]["dishes"] for e in events(rows, "day_plan")]
            self.assertEqual(plans, [p["dishes"] for p in TUNING["day_plan"]])
            self.assertEqual(rows[-1]["days_completed"], 5)


class Shop(unittest.TestCase):
    SHOP_AT = GT  # cập bến tick 0 -> gather_end tick 1; quán hết ca ở 1 + QT; shop bắt đầu bước sau đó

    def _shop_inputs(self, *fr):
        start = 1 + QT
        return DOCK_IN + [dict(f, tick=start + f["tick"]) for f in fr]

    def test_mua_nang_cap_va_hieu_luc_tu_ngay_ke(self):
        up = SHOP["upgrades"]
        inp = self._shop_inputs({"tick": 0, "buy": "oxygen"}, {"tick": 1, "buy": "oxygen"}, {"tick": 2, "buy": "hp"},
                                {"tick": 3, "buy": "oxygen"}, {"tick": 4, "buy": "xyz"}, {"tick": 5, "shop_done": True})
        with Workdir() as w:
            _, err, rows = run_day(w, scenario=DOCK, inputs=inp, days=2, ticks=1 + QT + 8, every=1)
            got = [(e["name"], e["data"]) for e in events(rows) if e["name"] in ("bought", "buy_failed")]
            m = 1000 - up["oxygen"][0]["price"]
            m2 = m - up["oxygen"][1]["price"]
            m3 = m2 - up["hp"][0]["price"]
            self.assertEqual(got, [
                ("bought", {"upgrade": "oxygen", "level": 1, "price": up["oxygen"][0]["price"], "money": m}),
                ("bought", {"upgrade": "oxygen", "level": 2, "price": up["oxygen"][1]["price"], "money": m2}),
                ("bought", {"upgrade": "hp", "level": 1, "price": up["hp"][0]["price"], "money": m3}),
                ("buy_failed", {"action": "oxygen", "reason": "max_level"}),
                ("buy_failed", {"action": "xyz", "reason": "unknown"})])
            shop = [s for s in snapshots(rows) if s["phase"] == "shop"][-1]
            self.assertEqual((shop["upgrades"], shop["active_upgrades"]), ({"hp": 1, "oxygen": 2}, {}))
            self.assertEqual(shop["earned"], 1000)  # mua trừ money, giữ earned
            d2 = [s for s in snapshots(rows) if s.get("day") == 2][0]
            self.assertEqual(d2["active_upgrades"], {"hp": 1, "oxygen": 2})
            self.assertEqual(d2["player"]["oxygen_max_ticks"], int(up["oxygen"][1]["oxygen_max_s"] * 60))
            self.assertEqual((d2["player"]["hp"], d2["player"]["hp_max"]), (up["hp"][0]["hp_max"],) * 2)

    def test_khong_du_tien_buy_failed_funds(self):
        sc = {"gather": DOCK["gather"]}
        with Workdir() as w:
            _, _, rows = run_day(w, scenario=sc, inputs=self._shop_inputs({"tick": 0, "buy": "hp"}), ticks=1 + QT + 2)
            self.assertEqual(events(rows, "buy_failed")[0]["data"], {"action": "hp", "reason": "funds"})

    def test_shop_tu_dong_sau_max_ticks(self):
        with Workdir() as w:
            _, _, rows = run_day(w, scenario=DOCK, inputs=DOCK_IN)
            se = events(rows, "shop_end")[0]
            self.assertEqual((se["tick"], se["data"]), (1 + QT + SHOP["max_ticks"], {"reason": "time"}))


class Pause(unittest.TestCase):
    def test_pause_dung_moi_timer(self):
        inp = [{"tick": 5, "pause": True}, {"tick": 6, "pause": False}, {"tick": 9, "pause": True},
               {"tick": 10, "pause": False}]
        for mode in ("gather", "quan", "day"):
            with Workdir() as w:
                out = w.path("o.jsonl")
                code, err = run_headless("--mode", mode, "--seed", "1", "--ticks", "12", "--snapshot-every", "1",
                                         "--inputs", write_json(w.path("i.json"), frames(*inp)), "--out", out)
                self.assertEqual(code, 0, err)
                rows = read_jsonl(out)
                ev = [(e["tick"], e["name"]) for e in events(rows) if e["name"] in ("paused", "resumed")]
                self.assertEqual(ev, [(6, "paused"), (10, "resumed")], mode)
                snap = {s["tick"]: s for s in snapshots(rows)}
                self.assertEqual(snap[7]["state"], "paused", mode)
                self.assertEqual(snap[6]["sim_tick"], snap[9]["sim_tick"], mode)
                self.assertEqual(snap[6]["time_left_ticks"], snap[9]["time_left_ticks"], mode)
                self.assertEqual(snap[10]["sim_tick"], snap[9]["sim_tick"] + 1, mode)  # resumed chạy ngay


class Cli(unittest.TestCase):
    def test_co_sai_ma_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            for args in (["--mode", "gather", "--days", "1"], ["--mode", "day", "--days", "0"],
                         ["--mode", "day", "--days", "6"], ["--mode", "day", "--inventory-out", w.path("k.json")]):
                self.assertEqual(run_headless(*args, "--seed", "1", "--ticks", "0", "--out", out)[0], 2, args)
            self.assertFalse(os.path.exists(out))

    def test_scenario_day_mau_thuan_ma_2(self):
        with Workdir() as w:
            for sc in ({"quan": {"stock": {}}}, {"quan": {"reputation": 4}}, {"day": {"money": 300, "earned": 200}},
                       {"day": {"upgrades": {"oxygen": 9}}}, {"day": {"day_plan": [{"day": 1, "dishes": {"x": 1}}]}},
                       {"day": {"day_plan": [{"day": 1, "dishes": {"goi_bong_sung": 1}, "ingredients": {"bong_sung": 9}}]}}):
                code, _, _ = run_day(w, scenario=sc, ticks=0)
                self.assertEqual(code, 2, sc)

    def test_mot_ngay_duoi_20_giay_va_tat_dinh(self):
        outs = []
        for _ in range(2):
            with Workdir() as w:
                t0 = time.perf_counter()
                code, err, _ = run_day(w)
                self.assertLess(time.perf_counter() - t0, 20)
                with open(w.path("d.jsonl"), "rb") as f:
                    outs.append(f.read())
        self.assertEqual(outs[0], outs[1])


if __name__ == "__main__":
    unittest.main()
