"""Tiện ích test: chạy headless, đọc JSONL, dựng fixture, so sánh có dung sai."""

import json
import math
import os
import shlex
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return path


def frames(*fr):
    return {"frames": list(fr)}


def headless_cmd():
    """Lệnh headless khai trong game.contract.json — test chạy qua đây nên dùng được với MỌI ngôn ngữ."""
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return shlex.split(json.load(f)["headless_cmd"])


def run_headless(*args, cwd=ROOT):
    """Chạy `<headless_cmd> <args>`; trả (mã thoát, stderr)."""
    p = subprocess.run([*headless_cmd(), *args], cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stderr


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def snapshots(rows):
    return [r for r in rows if r["type"] == "snapshot"]


def events(rows, name=None):
    return [r for r in rows if r["type"] == "event" and (name is None or r["name"] == name)]


def close(a, b, tol=0.1):
    return abs(a - b) <= tol


def dist(p, q):
    return math.dist(p, q)


class Workdir:
    """Thư mục tạm tự dọn: with Workdir() as w: w.path('x.json')."""

    def __enter__(self):
        self._d = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, *a):
        self._d.cleanup()

    def path(self, name):
        return os.path.join(self._d.name, name)


# --- v1.2 (Ticket-03, ADR-0002): kho cá thể. Fixture viết theo kho đếm được chuyển qua các hàm dưới. ----------
def _contract():
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return json.load(f)


INDIVIDUAL = tuple(int(x) for x in _contract()["contract_version"].split(".")[:2]) >= (1, 2)


def stock(counts, fresh=100, prefix="S"):
    """{kind: n} -> mảng cá thể {id, kind, fresh} (v1.2) hoặc giữ nguyên (v1.1). Id S1, S2… theo kind đã sắp."""
    if not INDIVIDUAL:
        return dict(counts)
    out, n = [], 0
    for kind in sorted(counts):
        for _ in range(counts[kind]):
            n += 1
            out.append({"id": f"{prefix}{n}", "kind": kind, "fresh": fresh})
    return out


def hold(kinds, fresh=100):
    """Mảng kind theo thứ tự nhặt -> mảng cá thể I1, I2… (v1.2) hoặc giữ nguyên (v1.1)."""
    if not INDIVIDUAL:
        return list(kinds)
    return [{"id": f"I{i}", "kind": k, "fresh": fresh} for i, k in enumerate(kinds, 1)]


def kinds(items):
    """Snapshot giỏ / lost / items -> mảng kind (dùng chung hai schema)."""
    return [x["kind"] if isinstance(x, dict) else x for x in items]


def counts(items):
    """Snapshot kho / gather_end.inventory.items -> {kind: n} (dùng chung hai schema)."""
    if isinstance(items, dict):
        return dict(items)
    out = {}
    for x in items:
        out[x["kind"]] = out.get(x["kind"], 0) + 1
    return {k: out[k] for k in sorted(out)}
