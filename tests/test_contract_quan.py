"""CP1-T1 (QA): kiểm game.contract.json phần quán + menu.

Unit: validate_tuning phải ném BadInput với từng kiểu contract hỏng.
Hộp đen: headless chạy với contract hỏng phải thoát mã 2 và KHÔNG tạo file --out.
"""

import copy
import json
import os
import shutil
import unittest

from helpers import ROOT, Workdir, run_headless

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput


def _base():
    return copy.deepcopy(load_contract()["tuning"])


class QuanContractUnit(unittest.TestCase):
    def assertRejected(self, mutate):
        t = _base()
        mutate(t)
        with self.assertRaises(BadInput):
            validate_tuning(t)

    def test_repo_contract_is_valid(self):
        validate_tuning(_base())

    # --- vị trí xuất phát ---
    def test_start_pos_out_of_bounds(self):
        self.assertRejected(lambda t: t["quan"].__setitem__("start_pos", [999, 5]))

    def test_start_pos_wrong_shape(self):
        self.assertRejected(lambda t: t["quan"].__setitem__("start_pos", [8]))

    # --- bếp / bàn ---
    def test_stoves_empty(self):
        self.assertRejected(lambda t: t["quan"].__setitem__("stoves", []))

    def test_tables_missing(self):
        self.assertRejected(lambda t: t["quan"].pop("tables"))

    def test_duplicate_table_id(self):
        def m(t):
            tb = t["quan"]["tables"]
            tb.append(dict(tb[0]))
        self.assertRejected(m)

    def test_stove_without_id(self):
        self.assertRejected(lambda t: t["quan"]["stoves"][0].pop("id"))

    def test_stove_pos_out_of_bounds(self):
        self.assertRejected(lambda t: t["quan"]["stoves"][0].__setitem__("pos", [2, -1]))

    def test_table_pos_out_of_bounds(self):
        self.assertRejected(lambda t: t["quan"]["tables"][0].__setitem__("pos", [100, 2]))

    # --- uy tín ---
    def test_reputation_initial_above_max(self):
        self.assertRejected(lambda t: t["quan"].__setitem__("reputation_initial", t["quan"]["reputation_max"] + 1))

    def test_reputation_initial_below_min(self):
        self.assertRejected(lambda t: t["quan"].__setitem__("reputation_initial", t["quan"]["reputation_min"] - 1))

    def test_reputation_min_not_below_max(self):
        def m(t):
            t["quan"]["reputation_min"] = t["quan"]["reputation_max"]
        self.assertRejected(m)

    def test_reputation_not_number(self):
        self.assertRejected(lambda t: t["quan"].__setitem__("reputation_max", "5"))

    # --- menu ---
    def test_menu_empty(self):
        self.assertRejected(lambda t: t.__setitem__("menu", {}))

    def test_recipe_unknown_ingredient(self):
        def m(t):
            dish = next(iter(t["menu"].values()))
            dish["recipe"] = {"ca_map": 1}
        self.assertRejected(m)

    def test_recipe_zero_amount(self):
        def m(t):
            dish = next(iter(t["menu"].values()))
            k = next(iter(dish["recipe"]))
            dish["recipe"][k] = 0
        self.assertRejected(m)

    def test_recipe_float_amount(self):
        def m(t):
            dish = next(iter(t["menu"].values()))
            k = next(iter(dish["recipe"]))
            dish["recipe"][k] = 1.5
        self.assertRejected(m)

    def test_recipe_missing(self):
        self.assertRejected(lambda t: next(iter(t["menu"].values())).pop("recipe"))


class QuanContractBlackBox(unittest.TestCase):
    """Chép package chonoi + contract hỏng vào thư mục tạm, chạy headless ở đó."""

    def _run_with(self, mutate, mode):
        with Workdir() as w:
            root = w.path("repo")
            shutil.copytree(os.path.join(ROOT, "chonoi"), os.path.join(root, "chonoi"),
                            ignore=shutil.ignore_patterns("__pycache__"))
            with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
                c = json.load(f)
            mutate(c["tuning"])
            with open(os.path.join(root, "game.contract.json"), "w", encoding="utf-8") as f:
                json.dump(c, f)
            out = os.path.join(root, "out.jsonl")
            code, err = run_headless("--mode", mode, "--seed", "1", "--ticks", "10", "--out", out, cwd=root)
            return code, err, os.path.exists(out)

    def test_bad_recipe_exits_2_without_output(self):
        def m(t):
            next(iter(t["menu"].values()))["recipe"] = {"ca_map": 1}
        for mode in ("gather", "quan"):
            code, err, made = self._run_with(m, mode)
            self.assertEqual(code, 2, err)
            self.assertFalse(made, "không được tạo file --out khi contract sai")

    def test_bad_reputation_exits_2_without_output(self):
        def m(t):
            t["quan"]["reputation_initial"] = t["quan"]["reputation_max"] + 1
        code, err, made = self._run_with(m, "quan")
        self.assertEqual(code, 2, err)
        self.assertFalse(made)


if __name__ == "__main__":
    unittest.main()
