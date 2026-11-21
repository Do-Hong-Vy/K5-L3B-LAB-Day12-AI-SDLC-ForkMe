"""Đọc game.contract.json và kiểm dải hợp lệ của tuning P1 (PRD mục 13.2, Test Contract)."""

import json
import os

from .errors import BadInput
from .inventory import KINDS

NODE_KINDS = ("bong_dien_dien", "bong_sung", "keo_neo")
FISH_KINDS = ("ca_linh", "ca_loc", "ca_keo")

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    version = c.get("contract_version")
    if version not in SUPPORTED_VERSIONS:
        raise BadInput(f"contract_version phải là một trong {list(SUPPORTED_VERSIONS)}, đang là {version!r}")
    validate_tuning(c.get("tuning"))
    if version in ("1.2", "1.3"):  # v1.3 (Ticket-04): gameplay/tuning/kho/JSONL theo v1.2
        _validate_freshness(c["tuning"].get("freshness"))
    elif "freshness" in c["tuning"]:
        raise BadInput("tuning.freshness chỉ có từ contract_version 1.2")
    if version == "1.3":
        for key in ("bench_cmd", "soak_cmd"):
            if not isinstance(c.get(key), str) or not c[key].strip():
                raise BadInput(f"contract 1.3 cần khai {key} ở gốc game.contract.json")
    return c


def _validate_freshness(fr):
    """Ticket-03: freshness {initial, gather_decay_per_s, quan_decay_per_s, spoiled_below} = 100, 0.5, 0.25, 30."""
    keys = ("initial", "gather_decay_per_s", "quan_decay_per_s", "spoiled_below")
    if not isinstance(fr, dict) or set(fr) != set(keys):
        raise BadInput(f"tuning.freshness phải có đúng khóa {list(keys)} (contract 1.2)")
    for k in keys:
        if not _num(fr[k]) or fr[k] < 0 or fr[k] > 100:
            raise BadInput(f"tuning.freshness.{k} phải là số trong [0, 100]")
    if not (0 < fr["spoiled_below"] <= fr["initial"]) or fr["gather_decay_per_s"] <= 0 or fr["quan_decay_per_s"] <= 0:
        raise BadInput("tuning.freshness: hao tươi > 0 và 0 < spoiled_below <= initial")


# Validator kiểm schema v1.1 (Ticket-02) + v1.2 (Ticket-03: freshness, kho cá thể) + v1.3 (Ticket-04: bench/soak).
SUPPORTED_VERSIONS = ("1.1", "1.2", "1.3")
MAX_DAYS = 5


def _int_between(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải là số nguyên trong [{lo}, {hi}], đang là {v!r}")


def _pos_in(name, pos, bounds, keys):
    if (not isinstance(pos, list) or len(pos) != 2 or not all(_num(c) for c in pos)):
        raise BadInput(f"tuning.{name} phải là [số, số]")
    for c, k in zip(pos, keys):
        lo, hi = bounds[k]
        if not (lo <= c <= hi):
            raise BadInput(f"tuning.{name} nằm ngoài vùng {k} ∈ [{lo}, {hi}]")


def _bounds(name, b, keys):
    if not isinstance(b, dict) or set(b) != set(keys):
        raise BadInput(f"tuning.{name}.bounds phải có đúng khóa {list(keys)}")
    for k in keys:
        v = b[k]
        if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] == 0 and v[1] > 0):
            raise BadInput(f"tuning.{name}.bounds.{k} phải là [0, số dương]")


def _validate_gather(g):
    """Dải hợp lệ P1 theo PRD mục 13.2."""
    _between("gather.duration_s", g.get("duration_s"), 60, 600)
    _bounds("gather", g.get("bounds"), ("x", "d"))
    b = g["bounds"]
    _between("gather.dock_radius", g.get("dock_radius"), 0.5, 5)
    _between("gather.interact_radius", g.get("interact_radius"), 0.5, 5)
    _between("gather.catch_radius", g.get("catch_radius"), 0.5, 5)
    _between("gather.swim_speed", g.get("swim_speed"), 1, 10)
    _between("gather.catch_cooldown_s", g.get("catch_cooldown_s"), 0, 10)
    _between("gather.oxygen_max_s", g.get("oxygen_max_s"), 10, 120)
    _int_between("gather.ramp_max_ticks", g.get("ramp_max_ticks"), 0, 6)
    _int_between("gather.hold_capacity", g.get("hold_capacity"), 4, 30)
    _int_between("gather.hp_max", g.get("hp_max"), 1, 99)
    _int_between("gather.oxygen_refill_per_tick", g.get("oxygen_refill_per_tick"), 1, 10_000)
    _int_between("gather.choke_interval_ticks", g.get("choke_interval_ticks"), 1, 10_000)
    _int_between("gather.node_yield", g.get("node_yield"), 1, 12)
    _between("gather.regrow_s", g.get("regrow_s"), 0.1, 600)
    _between("gather.surface_depth", g.get("surface_depth"), 0, 5)
    _pos_in("gather.dock_pos", g.get("dock_pos"), b, ("x", "d"))
    _pos_in("gather.start_pos", g.get("start_pos"), b, ("x", "d"))
    if not _num(g.get("start_heading_deg")):
        raise BadInput("tuning.gather.start_heading_deg phải là số")
    fy = g.get("fish_yield")
    if not isinstance(fy, dict) or set(fy) != set(FISH_KINDS):
        raise BadInput(f"tuning.gather.fish_yield phải có đúng {FISH_KINDS}")
    for k, v in fy.items():
        _int_between(f"gather.fish_yield.{k}", v, 1, g["hold_capacity"])
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or len(nodes) < 3:
        raise BadInput("tuning.gather.nodes phải là mảng nút hợp lệ")
    seen, kinds = set(), set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in seen:
            raise BadInput("tuning.gather.nodes: mỗi nút cần id duy nhất")
        seen.add(n["id"])
        if n.get("kind") not in NODE_KINDS:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        kinds.add(n["kind"])
        _pos_in(f"gather.nodes.{n['id']}.pos", n.get("pos"), b, ("x", "d"))
        if n["pos"][1] != 0:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
    if kinds != set(NODE_KINDS):
        raise BadInput(f"tuning.gather.nodes phải có ít nhất một nút mỗi loại {NODE_KINDS}")
    _validate_gather_fish_tuning(g, b, fy)
    _validate_gather_monsters(g, b)


def _range_pair(name, v, lo, hi, strict_lo=False):
    if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v)):
        raise BadInput(f"tuning.{name} phải là [min, max]")
    if (v[0] <= lo if strict_lo else v[0] < lo) or v[0] >= v[1] or v[1] > hi:
        raise BadInput(f"tuning.{name} nằm ngoài [{lo}, {hi}] hoặc min >= max")


def _validate_gather_fish_tuning(g, b, fy):
    """Kiểm tham số bơi/sinh và 8 đàn ban đầu trong gather (Test Contract v1.1)."""
    _between("gather.fish_speed", g.get("fish_speed"), 0.1, 20)
    _int_between("gather.fish_turn_ticks", g.get("fish_turn_ticks"), 1, 10_000)
    _int_between("gather.fish_spawn_ticks", g.get("fish_spawn_ticks"), 1, 10_000)
    _between("gather.fish_spawn_clearance", g.get("fish_spawn_clearance"), 0, 50)
    _range_pair("gather.fish_x", g.get("fish_x"), b["x"][0], b["x"][1])
    fx_lo, fx_hi = g["fish_x"]
    fdepths = g.get("fish_depths")
    if not isinstance(fdepths, dict) or set(fdepths) != set(FISH_KINDS):
        raise BadInput(f"tuning.gather.fish_depths phải có đúng {FISH_KINDS}")
    for k in FISH_KINDS:
        _range_pair(f"gather.fish_depths.{k}", fdepths[k], g["surface_depth"], b["d"][1], strict_lo=True)
    sx = g.get("fish_spawn_x")
    if not isinstance(sx, list) or not sx or not all(_num(x) and fx_lo <= x <= fx_hi for x in sx):
        raise BadInput("tuning.gather.fish_spawn_x phải là danh sách x không rỗng trong fish_x")
    sd = g.get("fish_spawn_depths")
    if not isinstance(sd, dict) or set(sd) != set(FISH_KINDS):
        raise BadInput(f"tuning.gather.fish_spawn_depths phải có đúng {FISH_KINDS}")
    for k in FISH_KINDS:
        d_lo, d_hi = fdepths[k]
        pts = sd[k]
        if not isinstance(pts, list) or not pts or not all(_num(d) and d_lo <= d <= d_hi for d in pts):
            raise BadInput(f"tuning.gather.fish_spawn_depths.{k} phải thuộc fish_depths.{k}")
    fw = g.get("fish_weights")
    if not isinstance(fw, dict) or set(fw) != set(FISH_KINDS) or any(not _num(fw[k]) or fw[k] <= 0 for k in FISH_KINDS):
        raise BadInput(f"tuning.gather.fish_weights phải có trọng số > 0 cho {FISH_KINDS}")
    fish = g.get("fish_initial")
    if isinstance(fish, int) and not isinstance(fish, bool):  # Ticket-02 4.1: "fish_initial là số 8" (clarify #22)
        if fish != 8:
            raise BadInput("tuning.gather.fish_initial phải là 8 (số đàn đầu ca, Contract v1.1)")
        _int_between("gather.fish_max", g.get("fish_max"), fish, 100)
        return
    if not isinstance(fish, list) or len(fish) != 8:
        raise BadInput("tuning.gather.fish_initial phải là số 8 hoặc danh sách đúng 8 đàn (Contract v1.1)")
    _int_between("gather.fish_max", g.get("fish_max"), len(fish), 100)
    seen, seen_pos = set(), set()
    for f in fish:
        if not isinstance(f, dict) or not isinstance(f.get("id"), str) or f["id"] in seen:
            raise BadInput("tuning.gather.fish_initial: mỗi đàn cần id duy nhất")
        seen.add(f["id"])
        if f.get("kind") not in fy:
            raise BadInput(f"tuning.gather.fish_initial.{f['id']}: kind phải thuộc fish_yield")
        _pos_in(f"gather.fish_initial.{f['id']}.pos", f.get("pos"), b, ("x", "d"))
        px, pd = float(f["pos"][0]), float(f["pos"][1])
        if pd <= g["surface_depth"]:
            raise BadInput(f"tuning.gather.fish_initial.{f['id']}: đàn cá phải ở dưới nước")
        if (px, pd) in seen_pos:
            raise BadInput(f"tuning.gather.fish_initial.{f['id']}: trùng vị trí ban đầu {[px, pd]}")
        seen_pos.add((px, pd))
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"tuning.gather.fish_initial.{f['id']}.heading_deg phải là số")


def _validate_gather_monsters(g, b):
    """Kiểm cấu trúc gather.monsters (Contract v1.1, Ticket-02 mục 4.1)."""
    m = g.get("monsters")
    if not isinstance(m, dict):
        raise BadInput("tuning.gather.monsters phải là object")
    _int_between("gather.monsters.invuln_ticks", m.get("invuln_ticks"), 0, 10_000)
    ratio = m.get("loss_ratio")
    if not _num(ratio) or not (0 <= ratio <= 1):
        raise BadInput("tuning.gather.monsters.loss_ratio phải trong [0, 1]")
    sp = m.get("species")
    if not isinstance(sp, dict) or "ca_sau" not in sp:
        raise BadInput("tuning.gather.monsters.species phải có ca_sau")
    for sname, cfg in sp.items():
        if not isinstance(cfg, dict):
            raise BadInput(f"tuning.gather.monsters.species.{sname} phải là object")
        for key in ("patrol_speed", "chase_speed", "detect_radius", "hit_radius", "recoil_dist"):
            _between(f"gather.monsters.species.{sname}.{key}", cfg.get(key), 0.01, 100)
        _between(f"gather.monsters.species.{sname}.exit_radius", cfg.get("exit_radius"), cfg["detect_radius"], 200)
        _int_between(f"gather.monsters.species.{sname}.recoil_ticks", cfg.get("recoil_ticks"), 1, 10_000)
        _range_pair(f"gather.monsters.species.{sname}.depths", cfg.get("depths"), g["surface_depth"], b["d"][1], strict_lo=True)
    spawns = m.get("spawns")
    if not isinstance(spawns, list) or not spawns:
        raise BadInput("tuning.gather.monsters.spawns phải là mảng không rỗng")
    seen = set()
    for e in spawns:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or e["id"] in seen:
            raise BadInput("tuning.gather.monsters.spawns: mỗi phần tử cần id duy nhất")
        seen.add(e["id"])
        kind = e.get("kind")
        if kind not in sp:
            raise BadInput(f"tuning.gather.monsters.spawns.{e['id']}: kind lạ {kind!r}")
        d_lo, d_hi = sp[kind]["depths"]
        _pos_in(f"gather.monsters.spawns.{e['id']}.pos", e.get("pos"), b, ("x", "d"))
        if not (d_lo <= e["pos"][1] <= d_hi):
            raise BadInput(f"tuning.gather.monsters.spawns.{e['id']}.pos nằm ngoài dải độ sâu của {kind}")
        wps = e.get("waypoints")
        if not isinstance(wps, list) or len(wps) != 2:
            raise BadInput(f"tuning.gather.monsters.spawns.{e['id']}.waypoints phải gồm 2 điểm")
        for idx, wp in enumerate(wps):
            _pos_in(f"gather.monsters.spawns.{e['id']}.waypoints[{idx}]", wp, b, ("x", "d"))
            if not (d_lo <= wp[1] <= d_hi):
                raise BadInput(f"tuning.gather.monsters.spawns.{e['id']}.waypoints[{idx}] ngoài dải độ sâu của {kind}")
        if list(wps[0]) != list(e["pos"]):
            raise BadInput(f"tuning.gather.monsters.spawns.{e['id']}: waypoint đầu phải là vị trí xuất phát (Ticket-02 1.2)")
        _int_between(f"gather.monsters.spawns.{e['id']}.from_day", e.get("from_day"), 1, MAX_DAYS)
    if not any(e["from_day"] == 1 for e in spawns):
        raise BadInput("tuning.gather.monsters.spawns cần ít nhất một con từ Ngày 1 (gather độc lập dùng bố trí Ngày 1)")


def validate_tuning(t):
    if not isinstance(t, dict):
        raise BadInput("thiếu khối tuning")
    g, q, menu = t.get("gather"), t.get("quan"), t.get("menu")
    if not isinstance(g, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có gather, quan, menu")
    _validate_gather(g)
    # Quán: dải hợp lệ P1 (PRD mục 13.2)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _bounds("quan", q.get("bounds"), ("x", "z"))
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("quan.interact_radius", q.get("interact_radius"), 0.5, 5)
    _int_between("quan.ramp_max_ticks", q.get("ramp_max_ticks", 6), 0, 6)
    _between("quan.eat_s", q.get("eat_s"), 0.1, 600)
    _between("quan.customer_interval_s", q.get("customer_interval_s"), 0.1, 600)
    _int_between("quan.first_customer_tick", q.get("first_customer_tick"), 1, int(q["duration_s"] * 60) - 1)
    if not (_num(q.get("tip_rate")) and q["tip_rate"] > 0 and _num(q.get("left_reputation_delta"))
            and q["left_reputation_delta"] < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    ratio = q.get("tip_min_patience_ratio")
    if not (_num(ratio) and 0 < ratio <= 1):
        raise BadInput("quan.tip_min_patience_ratio phải thuộc (0, 1]")
    if not (_num(q.get("tip_reputation")) and q["tip_reputation"] > 0):
        raise BadInput("quan.tip_reputation phải > 0")
    if q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null ở Phase 1")
    _validate_quan_layout(q)
    _validate_menu(menu)
    # day_plan đọc công thức menu -> kiểm SAU menu để menu hỏng báo BadInput (mã 2) chứ không KeyError
    _validate_day_plan(t.get("day_plan"), menu)
    _validate_shop(t.get("shop"))


def _validate_quan_layout(q):
    """Bếp/bàn, vị trí xuất phát và uy tín của quán (bổ sung của nhóm ForkMe, CP1-T1)."""
    b = q["bounds"]
    _pos_in("quan.start_pos", q.get("start_pos"), b, ("x", "z"))
    for arr in ("stoves", "tables"):
        items = q.get(arr)
        if not isinstance(items, list) or not items:
            raise BadInput(f"tuning.quan.{arr} phải là mảng không rỗng")
        seen = set()
        for e in items:
            if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"] or e["id"] in seen:
                raise BadInput(f"tuning.quan.{arr}: mỗi phần tử cần id (chuỗi) duy nhất")
            seen.add(e["id"])
            _pos_in(f"quan.{arr}.{e['id']}.pos", e.get("pos"), b, ("x", "z"))
    lo, hi, init = q.get("reputation_min"), q.get("reputation_max"), q.get("reputation_initial")
    if not (_num(lo) and _num(hi) and _num(init)):
        raise BadInput("tuning.quan.reputation_min/max/initial phải là số")
    if not (lo < hi):
        raise BadInput(f"tuning.quan.reputation_min ({lo}) phải < reputation_max ({hi})")
    if not (lo <= init <= hi):
        raise BadInput(f"tuning.quan.reputation_initial ({init}) phải trong [{lo}, {hi}]")


def _validate_menu(menu):
    """Món: giá nguyên > 0, cook_s > 0, công thức chỉ dùng nguyên liệu P1 với số lượng nguyên > 0."""
    if not menu:
        raise BadInput("tuning.menu không được rỗng")
    for dish_id, d in menu.items():
        if not isinstance(d, dict):
            raise BadInput(f"menu.{dish_id} phải là object")
        price, cook = d.get("price"), d.get("cook_s")
        if isinstance(price, bool) or not isinstance(price, int) or price <= 0 or not _num(cook) or cook <= 0:
            raise BadInput(f"menu.{dish_id}: price (nguyên) và cook_s phải > 0")
        recipe = d.get("recipe")
        if not isinstance(recipe, dict) or not recipe:
            raise BadInput(f"menu.{dish_id}.recipe phải là object không rỗng")
        for kind, n in recipe.items():
            if kind not in KINDS:
                raise BadInput(f"menu.{dish_id}.recipe: nguyên liệu lạ {kind!r} (chỉ nhận {list(KINDS)})")
            if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
                raise BadInput(f"menu.{dish_id}.recipe.{kind} phải là số nguyên > 0")


def _validate_day_plan(plan, menu):
    """day_plan: 5 Ngày, dishes thuộc menu, ingredients = tổng công thức × suất (Ticket-02 2, 4.1)."""
    if not isinstance(plan, list) or len(plan) != MAX_DAYS:
        raise BadInput(f"tuning.day_plan phải là mảng {MAX_DAYS} Ngày")
    for i, e in enumerate(plan, start=1):
        p = f"day_plan[{i - 1}]"
        if not isinstance(e, dict) or set(e) != {"day", "dishes", "ingredients"}:
            raise BadInput(f"tuning.{p} phải có đúng khóa day, dishes, ingredients")
        if e["day"] != i:
            raise BadInput(f"tuning.{p}.day phải là {i} (theo thứ tự)")
        dishes = e["dishes"]
        if not isinstance(dishes, dict) or not dishes:
            raise BadInput(f"tuning.{p}.dishes phải là map món -> số suất, không rỗng")
        need = {}
        for dish, n in dishes.items():
            if dish not in menu:
                raise BadInput(f"tuning.{p}.dishes: món lạ {dish!r}")
            _int_between(f"{p}.dishes.{dish}", n, 1, 1000)
            for kind, k in menu[dish]["recipe"].items():
                need[kind] = need.get(kind, 0) + k * n
        ing = e["ingredients"]
        if not isinstance(ing, dict) or any(isinstance(v, bool) or not isinstance(v, int) or v <= 0
                                           for v in ing.values()):
            raise BadInput(f"tuning.{p}.ingredients phải là map kind -> số nguyên dương")
        if ing != need:
            raise BadInput(f"tuning.{p}.ingredients {ing} khác tổng công thức × suất {need}")


def _validate_shop(shop):
    """shop {max_ticks, upgrades{oxygen[], hp[]}}, mảng theo cấp 1..n (Ticket-02 4.1)."""
    if not isinstance(shop, dict) or not {"max_ticks", "upgrades"} <= set(shop):
        raise BadInput("tuning.shop phải có max_ticks và upgrades")
    _int_between("shop.max_ticks", shop["max_ticks"], 1, 100_000)
    ups = shop["upgrades"]
    if not isinstance(ups, dict) or not {"oxygen", "hp"} <= set(ups):
        raise BadInput("tuning.shop.upgrades phải có oxygen và hp")
    fields = {"oxygen": ("oxygen_max_s", 10, 120, False), "hp": ("hp_max", 1, 99, True)}
    for uid, levels in ups.items():
        p = f"shop.upgrades.{uid}"
        if not isinstance(levels, list) or not levels:
            raise BadInput(f"tuning.{p} phải là mảng cấp không rỗng")
        for i, lv in enumerate(levels, start=1):
            if not isinstance(lv, dict) or lv.get("level") != i:
                raise BadInput(f"tuning.{p}[{i - 1}].level phải là {i} (mảng theo cấp)")
            _int_between(f"{p}[{i - 1}].price", lv.get("price"), 1, 10_000_000)
            if uid in fields:
                key, lo, hi, integer = fields[uid]
                (_int_between if integer else _between)(f"{p}[{i - 1}].{key}", lv.get(key), lo, hi)
