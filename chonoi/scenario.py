"""Nạp và kiểm scenario (Contract D). Trả về dict của đúng khối theo mode.

KHUNG: kiểm cú pháp, id trùng, bộ đếm âm, khoang vượt sức chứa, trường lạ.
Nhóm (CP1-T1): `_validate_quan_rules` kiểm mâu thuẫn mức luật của quán theo PRD-0 mục D (bếp/tay/khách,
trạng thái đơn, liên kết món <-> đơn); `check_quan_stock` kiểm giữ chỗ quá tồn — gọi sau khi đã biết kho.
"""

import json

from .errors import BadInput
from .ids import id_key
from .inventory import KINDS, validate_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "random_fish", "time_left_ticks"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks"}
FISH_KEYS = {"id", "kind", "pos", "heading_deg", "age_ticks"}
NODE_KINDS = ("bong_dien_dien", "bong_sung", "keo_neo")
FISH_KINDS = ("ca_linh", "ca_loc", "ca_keo")
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


DAY_KEYS = {"money", "earned", "reputation", "upgrades", "day_plan"}


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    if mode == "day":
        return _load_day(data, tuning)
    if not isinstance(data, dict) or not set(data) <= {"gather", "quan"}:
        raise BadInput("scenario chỉ được có khối 'gather' hoặc 'quan'")
    if set(data) - {mode}:
        raise BadInput(f"khối sai mode: chạy --mode {mode} chỉ nhận khối '{mode}'")
    return _load_block(mode, data.get(mode, {}), tuning)


def _load_block(mode, block, tuning):
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = GATHER_KEYS if mode == "gather" else QUAN_KEYS
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    dur = int(round(tuning[mode]["duration_s"] * 60))
    if "time_left_ticks" in block:
        t = block["time_left_ticks"]
        if isinstance(t, bool) or not isinstance(t, int) or not (1 <= t <= dur):
            raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)
    return block


def _load_day(data, tuning):
    """Ticket-02 mục 4.3: day nhận gather/quan làm mẫu mỗi Ngày + khối day dựng trạng thái xuyên Ngày."""
    if not isinstance(data, dict) or not set(data) <= {"day", "gather", "quan"}:
        raise BadInput("scenario day chỉ nhận khối 'day', 'gather', 'quan'")
    out = {}
    for mode in ("gather", "quan"):
        if mode in data:
            out[mode] = _load_block(mode, data[mode], tuning)
    q = out.get("quan", {})
    for banned in ("stock", "reputation"):
        if banned in q:
            raise BadInput(f"cấm quan.{banned} khi chạy day (dùng gather.hold / day.reputation)")
    d = data.get("day", {})
    if not isinstance(d, dict) or set(d) - DAY_KEYS:
        raise BadInput(f"khối day chỉ có {sorted(DAY_KEYS)}")
    money, earned = d.get("money", 0), d.get("earned", 0)
    for name, v in (("money", money), ("earned", earned)):
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"day.{name} phải là số nguyên >= 0")
    if ("money" in d) != ("earned" in d) and money > 0:
        raise BadInput("khai cả day.money và day.earned khi có tiền đầu kỳ")
    if money > earned:
        raise BadInput("cần 0 <= day.money <= day.earned")
    q_t = tuning["quan"]
    if "reputation" in d and not (_num(d["reputation"]) and q_t["reputation_min"] <= d["reputation"] <= q_t["reputation_max"]):
        raise BadInput("day.reputation ngoài miền uy tín")
    ups = d.get("upgrades", {})
    shop = tuning["shop"]["upgrades"]
    if not isinstance(ups, dict):
        raise BadInput("day.upgrades phải là object")
    for k, lv in ups.items():
        levels = [u["level"] for u in shop.get(k, [])]
        if k not in shop or isinstance(lv, bool) or not isinstance(lv, int) or not (0 <= lv <= max(levels)):
            raise BadInput(f"day.upgrades.{k} không hợp lệ")
    plan = d.get("day_plan", [])
    days_known = {p["day"] for p in tuning["day_plan"]}
    if not isinstance(plan, list):
        raise BadInput("day.day_plan phải là mảng")
    seen = set()
    for p in plan:
        if not isinstance(p, dict) or p.get("day") not in days_known or p["day"] in seen:
            raise BadInput("day.day_plan: mỗi mục cần day hợp lệ, không trùng")
        seen.add(p["day"])
        dishes = p.get("dishes")
        if not isinstance(dishes, dict) or not dishes or any(
                k not in tuning["menu"] or isinstance(n, bool) or not isinstance(n, int) or n <= 0
                for k, n in dishes.items()):
            raise BadInput(f"day.day_plan[{p['day']}].dishes phải là map id món -> số nguyên dương")
        if "ingredients" in p:
            need = {}
            for dish, n in dishes.items():
                for k, qn in tuning["menu"][dish]["recipe"].items():
                    need[k] = need.get(k, 0) + qn * n
            if p["ingredients"] != need:
                raise BadInput(f"day.day_plan[{p['day']}].ingredients khác tổng công thức × suất")
    out["day"] = d
    return out


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    for arr in ("nodes", "fish"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        if not isinstance(h, list) or any(k not in KINDS for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = int(round(g["oxygen_max_s"] * 60))
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        if n.get("kind") not in NODE_KINDS:
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        extra_f = set(f) - FISH_KEYS
        if extra_f:
            raise BadInput(f"fish.{f['id']}: trường lạ/chưa hỗ trợ {sorted(extra_f)}")
        if f.get("kind") not in FISH_KINDS:
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {FISH_KINDS}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")
        if "age_ticks" in f:
            _nonneg_int(f"fish.{f['id']}.age_ticks", f["age_ticks"])


def _validate_quan(b, tuning):
    for arr in ("stoves", "tables", "customers"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "stock" in b:
        validate_items(b["stock"])
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    table_ids = [c.get("table_id") for c in b.get("customers", [])]
    known = {t["id"] for t in tuning["quan"]["tables"]} | {t.get("id") for t in b.get("tables", [])}
    for c in b.get("customers", []):
        if not isinstance(c.get("table_id"), str) or c["table_id"] not in known:
            raise BadInput(f"customers.{c['id']}: table_id phải là bàn có thật")
    if len(table_ids) != len(set(table_ids)):
        raise BadInput("hai khách cùng bàn")
    _validate_quan_rules(b, tuning)


# --- Kiểm mâu thuẫn mức luật của quán (nhóm ForkMe, CP1-T1 — PRD-0 mục D) -------------------------

STOVE_KEYS = {"id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks"}
TABLE_KEYS = {"id", "pos"}
CUSTOMER_KEYS = {"id", "table_id", "dish_id", "order_tick", "state", "patience_ticks_left", "eat_ticks_left",
                 "order_status", "reserved", "base_price", "tip"}
DISH_KEYS = {"order_id", "dish_id", "base_price"}
STOVE_STATES = ("idle", "cooking", "ready")
CUSTOMER_STATES = ("waiting", "eating")
ORDER_STATUSES = ("reserved", "assigned", "unfulfillable", "served")


def _pos_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
        raise BadInput(f"{name} phải là số nguyên dương")


def _check_dish(name, d, menu):
    """Payload món {order_id, dish_id, base_price}."""
    if not isinstance(d, dict) or set(d) != DISH_KEYS:
        raise BadInput(f"{name} phải là payload món có đúng khóa {sorted(DISH_KEYS)} hoặc null")
    if not isinstance(d["order_id"], str) or not d["order_id"]:
        raise BadInput(f"{name}.order_id phải là chuỗi khác rỗng")
    if d["dish_id"] not in menu:
        raise BadInput(f"{name}.dish_id {d['dish_id']!r} không có trong menu")
    _pos_int(f"{name}.base_price", d["base_price"])


def _merged(defaults, updates, keys, label, qb):
    """stoves/tables cập nhật theo id hiện có; id lạ hoặc trường lạ -> mã 2."""
    by_id = {d["id"]: dict(d) for d in defaults}
    for u in updates:
        extra = set(u) - keys
        if extra:
            raise BadInput(f"{label}.{u['id']}: trường lạ/chưa hỗ trợ {sorted(extra)}")
        if u["id"] not in by_id:
            raise BadInput(f"{label}.{u['id']}: id cập nhật không tồn tại trong tuning")
        if "pos" in u:
            _pos(f"{label}.{u['id']}.pos", u["pos"], qb, axes=("x", "z"))
        by_id[u["id"]].update(u)
    return list(by_id.values())


def _validate_quan_rules(b, tuning):
    q, menu = tuning["quan"], tuning["menu"]
    qb = q["bounds"]
    patience_full = int(round(q["patience_s"] * 60))
    eat_full = int(round(q["eat_s"] * 60))

    if "reputation" in b:
        r = b["reputation"]
        if not _num(r) or not (q["reputation_min"] <= r <= q["reputation_max"]):
            raise BadInput(f"reputation phải là số trong [{q['reputation_min']}, {q['reputation_max']}]")
    if "random_customers" in b and not isinstance(b["random_customers"], bool):
        raise BadInput("random_customers phải là boolean")

    # Món đang tồn tại ở bếp / tay: order_id -> nơi giữ
    holders = {}

    def hold(where, dish):
        oid = dish["order_id"]
        if oid in holders:
            raise BadInput(f"đơn {oid} có món ở hai nơi ({holders[oid][0]} và {where})")
        holders[oid] = (where, dish)

    hand = b.get("hand")
    if hand is not None:
        _check_dish("hand", hand, menu)
        hold("hand", hand)

    _merged(q["tables"], b.get("tables", []), TABLE_KEYS, "tables", qb)
    for s in _merged(q["stoves"], b.get("stoves", []), STOVE_KEYS, "stoves", qb):
        sid, state = s["id"], s.get("state", "idle")
        if state not in STOVE_STATES:
            raise BadInput(f"stoves.{sid}.state phải là một trong {STOVE_STATES}")
        cook, ready, dish = s.get("cook_ticks_left", 0), s.get("ready_ticks", 0), s.get("dish")
        _nonneg_int(f"stoves.{sid}.cook_ticks_left", cook)
        _nonneg_int(f"stoves.{sid}.ready_ticks", ready)
        if state == "idle":
            if dish is not None or cook or ready:
                raise BadInput(f"stoves.{sid}: bếp idle không có món, cook_ticks_left = ready_ticks = 0")
            continue
        if dish is None:
            raise BadInput(f"stoves.{sid}: bếp {state} phải có món")
        _check_dish(f"stoves.{sid}.dish", dish, menu)
        if state == "cooking":
            if cook <= 0:
                raise BadInput(f"stoves.{sid}: bếp cooking phải có cook_ticks_left > 0")
            if cook > int(round(menu[dish["dish_id"]]["cook_s"] * 60)):
                raise BadInput(f"stoves.{sid}: cook_ticks_left vượt thời gian nấu món")
            if ready:
                raise BadInput(f"stoves.{sid}: bếp cooking không có ready_ticks")
        elif cook:
            raise BadInput(f"stoves.{sid}: bếp ready phải có cook_ticks_left = 0")
        hold(f"stoves.{sid}", dish)

    customers = {}
    for c in b.get("customers", []):
        cid = c["id"]
        extra = set(c) - CUSTOMER_KEYS
        if extra:
            raise BadInput(f"customers.{cid}: trường lạ/chưa hỗ trợ {sorted(extra)}")
        if c.get("dish_id") not in menu:
            raise BadInput(f"customers.{cid}.dish_id phải là món có trong menu")
        state = c.get("state", "waiting")
        status = c.get("order_status", "reserved")
        if state not in CUSTOMER_STATES:
            raise BadInput(f"customers.{cid}.state phải là một trong {CUSTOMER_STATES}")
        if status not in ORDER_STATUSES:
            raise BadInput(f"customers.{cid}.order_status phải là một trong {ORDER_STATUSES}")
        _nonneg_int(f"customers.{cid}.order_tick", c.get("order_tick", 0))
        patience = c.get("patience_ticks_left", patience_full)
        eat = c.get("eat_ticks_left", 0)
        _nonneg_int(f"customers.{cid}.patience_ticks_left", patience)
        _nonneg_int(f"customers.{cid}.eat_ticks_left", eat)
        if patience > patience_full:
            raise BadInput(f"customers.{cid}.patience_ticks_left vượt kiên nhẫn tối đa {patience_full}")
        if eat > eat_full:
            raise BadInput(f"customers.{cid}.eat_ticks_left vượt thời gian ăn {eat_full}")
        reserved = validate_items(c["reserved"]) if "reserved" in c else None
        for key in ("base_price", "tip"):
            v = c.get(key)
            if v is not None and (isinstance(v, bool) or not isinstance(v, int) or v < 0):
                raise BadInput(f"customers.{cid}.{key} phải là số nguyên không âm hoặc null")
        # trạng thái khách <-> trạng thái đơn
        if state == "eating":
            if status != "served":
                raise BadInput(f"customers.{cid}: khách eating phải có order_status served")
            if eat <= 0:
                raise BadInput(f"customers.{cid}: khách eating phải có eat_ticks_left > 0")
            if c.get("base_price") is None or c.get("tip") is None:
                raise BadInput(f"customers.{cid}: khách eating phải khai base_price và tip đã chốt")
            _pos_int(f"customers.{cid}.base_price", c["base_price"])
        else:
            if status == "served":
                raise BadInput(f"customers.{cid}: đơn served thì khách phải đang eating")
            if eat:
                raise BadInput(f"customers.{cid}: khách waiting không có eat_ticks_left")
        if status == "reserved":
            if reserved is not None and reserved != validate_items(menu[c["dish_id"]]["recipe"]):
                raise BadInput(f"customers.{cid}: reserved khác công thức món {c['dish_id']}")
        elif reserved:
            raise BadInput(f"customers.{cid}: đơn {status} phải có reserved rỗng")
        customers[cid] = (c, status)

    # liên kết món <-> đơn
    for oid, (where, dish) in holders.items():
        if oid not in customers:
            raise BadInput(f"{where}: món của đơn {oid} không có khách tương ứng")
        c, status = customers[oid]
        if status != "assigned":
            raise BadInput(f"{where}: món của đơn {oid} nhưng đơn đang {status} (phải assigned)")
        if dish["dish_id"] != c["dish_id"]:
            raise BadInput(f"{where}: món {dish['dish_id']} không khớp đơn {oid} ({c['dish_id']})")
    for cid, (c, status) in customers.items():
        if status == "assigned" and cid not in holders:
            raise BadInput(f"customers.{cid}: đơn assigned phải có đúng một món ở bếp hoặc tay")


def check_quan_stock(block, stock, tuning):
    """Tổng phần giữ chỗ không được vượt tồn vật lý. Gọi SAU khi biết kho (--inventory hoặc quan.stock).

    Đơn reserved thiếu `reserved` thì cấp theo công thức, duyệt theo order_tick rồi id bàn (PRD-0 D).
    """
    menu = tuning["menu"]
    used = {}
    order = sorted(block.get("customers", []), key=lambda c: (c.get("order_tick", 0), id_key(c["table_id"])))
    for c in order:
        if c.get("order_status", "reserved") != "reserved":
            continue
        need = c["reserved"] if "reserved" in c else menu[c["dish_id"]]["recipe"]
        for kind, n in need.items():
            used[kind] = used.get(kind, 0) + n
            if used[kind] > stock.get(kind, 0):
                raise BadInput(f"customers.{c['id']}: giữ chỗ {kind} vượt tồn kho "
                               f"({used[kind]} > {stock.get(kind, 0)})")
