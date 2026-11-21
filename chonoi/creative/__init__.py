"""Sáng tạo của nhóm ForkMe — chỉ bật trong chonoi.live, không bao giờ ở headless (Test Contract giữ nguyên)."""

import json
import os

from ..errors import BadInput
from ..inventory import KINDS

KITCHEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kitchen.json")


def load_kitchen(path=KITCHEN_PATH) -> dict:
    """Bếp nhiều section: mỗi section sơ chế 1 loại nguyên liệu; đủ phần sơ chế mới gộp ở bếp."""
    try:
        with open(path, encoding="utf-8") as f:
            k = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    secs, prep = k.get("sections"), k.get("prep_s")
    if not isinstance(secs, list) or not isinstance(prep, dict):
        raise BadInput("kitchen.json cần 'sections' (mảng) và 'prep_s' (object)")
    ids = set()
    for s in secs:
        if s.get("kind") not in KINDS or s.get("id") in ids or not isinstance(s.get("pos"), list):
            raise BadInput(f"kitchen.json: section sai {s!r}")
        ids.add(s["id"])
    if set(prep) != {s["kind"] for s in secs} or not all(isinstance(v, (int, float)) and v > 0 for v in prep.values()):
        raise BadInput("kitchen.json: prep_s phải có thời gian dương cho đúng mỗi loại của section")
    return {"sections": secs, "prep_s": prep}
