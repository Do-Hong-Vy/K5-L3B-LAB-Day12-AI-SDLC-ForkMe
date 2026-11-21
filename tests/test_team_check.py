"""Test cho tools/check_team.py (kiểm danh sách thành viên)."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import check_team  # noqa: E402

GOOD = """# TEAM
| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Đỗ Hồng Vỹ | @Do-Hong-Vy | sim/gather | Integrator | sim/quan |
| Bùi Phước Anh | Cuubeo | sim/quan | PO | sim/gather |
| Đinh Hoàng Phong | Phog2811 | client/ui | Scrum / Release | qa |
| Nguyễn Quốc Toàn | Nguyenquoctoan0310 | qa | QA lead | client/ui |
"""

TEMPLATE = """# TEAM
| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| | | `sim/gather` | | |
| | | `sim/quan` | | |
| | | `client/ui` | | |
| | | `qa` | | |
"""


class TeamCheck(unittest.TestCase):
    def test_good(self):
        m = check_team.parse_team(GOOD)
        self.assertEqual([x["handle"] for x in m], ["Do-Hong-Vy", "Cuubeo", "Phog2811", "Nguyenquoctoan0310"])
        self.assertEqual(check_team.validate(m, 4, actor="Do-Hong-Vy", event="pull_request"), [])

    def test_template_is_rejected(self):
        # Template gốc (ô handle trống) phải bị từ chối. Trước đây test đọc TEAM.md thật,
        # nhưng nhóm đã điền TEAM.md hợp lệ nên chuyển sang chuỗi TEMPLATE cố định.
        self.assertTrue(check_team.validate(check_team.parse_team(TEMPLATE), 4))

    def test_repo_team_md_is_valid(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "TEAM.md"), encoding="utf-8") as f:
            m = check_team.parse_team(f.read())
        with open(os.path.join(root, "game.contract.json"), encoding="utf-8") as f:
            size = json.load(f)["team_size"]
        self.assertEqual(check_team.validate(m, size), [])

    def test_wrong_size_duplicate_and_outsider(self):
        m = check_team.parse_team(GOOD)
        self.assertTrue(any("team_size" in e for e in check_team.validate(m, 5)))
        dup = check_team.parse_team(GOOD.replace("Cuubeo", "Do-Hong-Vy"))
        self.assertTrue(any("trùng" in e for e in check_team.validate(dup, 4)))
        self.assertTrue(any("không có trong danh sách" in e for e in check_team.validate(m, 4, actor="ai-do", event="pull_request")))
        self.assertEqual(check_team.validate(m, 4, actor="ai-do", event="push"), [])
        self.assertEqual(check_team.validate(m, 4, actor="dependabot[bot]", event="pull_request"), [])

    def test_too_few_members(self):
        three = "\n".join(GOOD.splitlines()[:-1]) + "\n"
        self.assertTrue(any("4 đến 6" in e for e in check_team.validate(check_team.parse_team(three), 3)))


if __name__ == "__main__":
    unittest.main()
