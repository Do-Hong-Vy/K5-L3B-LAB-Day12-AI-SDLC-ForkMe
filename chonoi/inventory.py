"""File kho — adapter hai schema, chọn theo contract_version (ADR-0002).

v1.0/v1.1 (Contract G): kho đếm {"items": {kind: số nguyên >= 0}}.
v1.2 (Ticket-03):        kho cá thể {"items": [{"id", "kind", "fresh"}]}, fresh hữu hạn trong [0, 100], id duy nhất.
Đọc: từ chối sai schema / kind lạ / số âm / id trùng / fresh ngoài miền (BadInput -> mã 2). v1.2 từ chối kho đếm.
Ghi: qua file tạm cùng thư mục rồi thay thế nguyên tử, byte-ổn-định; v1.2 xuất theo id, fresh đủ chính xác
(repr float khứ hồi chính xác) để giữ nhánh ở ngưỡng 30.
"""

import json
import math
import os
import tempfile

from .ids import id_key

from .errors import BadInput

# v1.1 (Ticket-02, ADR-0001): 6 nguyên liệu. Merge 9612d91 làm mất dòng KINDS -> khôi phục.
KINDS = ("ca_loc", "ca_linh", "ca_keo", "bong_dien_dien", "bong_sung", "keo_neo")
KINDS_P1 = KINDS  # alias tương thích ngược cho module/test P1


def validate_items(items, kinds=KINDS):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def is_individual(contract_version) -> bool:
    """Kho cá thể từ contract v1.2."""
    try:
        return tuple(int(x) for x in str(contract_version).split(".")[:2]) >= (1, 2)
    except ValueError:
        return False


def validate_individuals(items, kinds=KINDS, name="items") -> list:
    """Mảng cá thể {id, kind, fresh}: id chuỗi khác rỗng duy nhất, kind hợp lệ, fresh hữu hạn trong [0, 100]."""
    if not isinstance(items, list):
        raise BadInput(f"{name} phải là mảng cá thể {{id, kind, fresh}} (contract v1.2)")
    seen, out = set(), []
    for i, it in enumerate(items):
        if not isinstance(it, dict) or set(it) != {"id", "kind", "fresh"}:
            raise BadInput(f"{name}[{i}] phải có đúng khóa id, kind, fresh")
        iid, kind, fresh = it["id"], it["kind"], it["fresh"]
        if not isinstance(iid, str) or not iid:
            raise BadInput(f"{name}[{i}].id phải là chuỗi khác rỗng")
        if iid in seen:
            raise BadInput(f"{name}: id trùng {iid}")
        seen.add(iid)
        if kind not in kinds:
            raise BadInput(f"{name}[{i}]: nguyên liệu lạ {kind!r}")
        if isinstance(fresh, bool) or not isinstance(fresh, (int, float)) or not math.isfinite(fresh)                 or not (0 <= fresh <= 100):
            raise BadInput(f"{name}[{i}].fresh phải là số hữu hạn trong [0, 100]")
        out.append({"id": iid, "kind": kind, "fresh": fresh})
    return out


def read_inventory(path: str, kinds=KINDS, individual=False):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    if individual:
        return validate_individuals(data["items"], kinds)
    return validate_items(data["items"], kinds)


def hold_to_items(hold: list) -> dict:
    """Khoang (mảng id theo thứ tự nhặt) -> object đếm, sắp theo id nguyên liệu."""
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def write_inventory(path: str, items):
    if isinstance(items, list):  # v1.2: cá thể, xuất theo id
        items = [{"id": it["id"], "kind": it["kind"], "fresh": it["fresh"]} for it in sorted(items, key=lambda x: id_key(x["id"]))]
    else:
        items = {k: items[k] for k in sorted(items) if items[k] > 0}
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"items": items}, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
