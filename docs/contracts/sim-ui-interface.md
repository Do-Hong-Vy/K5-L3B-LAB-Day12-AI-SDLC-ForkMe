# Giao diện tích hợp `sim/*` ↔ `client/ui` (Contract v1.3 / gameplay v1.2)

> UI chỉ **ĐỌC** snapshot từ `GET /state` (hoặc `Session.snapshot()`) và **GỬI** input qua `POST /input`, `POST /restart`. Tuyệt đối không tự tính lại luật chơi ở phía client.

---

## 1. Kênh giao tiếp Live ([`chonoi/live.py`](../../chonoi/live.py))

| Endpoint | Phương thức | Payload / Phản hồi | Ghi chú |
|---|---|---|---|
| `/state` | `GET` | JSON snapshot hiện tại + `meta` (`tuning[phase]` khi `mode == "day"`), `events` (tối đa 40 sự kiện gần nhất `{type, tick, phase, [day], name, data}`), `finished` (`bool`), `reason` (`str \| null`), `error` (`str \| null`) | Poll định kỳ phía client (`16ms`); asset CC0 phục vụ tĩnh tại `/assets/...` |
| `/input` | `POST` | `{"move": [a, b], "interact": bool, "catch": bool, "pause": bool, "shop_done": bool, "buy": str}` | `a, b ∈ [-1, 1]`. `gather`: `+b` hướng xuống (`d+`); `quan`: `+b` hướng bắc (`z+`). Cạnh lên do `LiveInputs` bắt; `buy` chạy chỉ tại frame khai báo |
| `/restart` | `POST` | `{}` → `{"ok": true}` | Chơi lại cùng `seed` & `scenario` |

---

## 2. Trường Snapshot chung ([`chonoi/runner.py`](../../chonoi/runner.py))

- `type`: `"snapshot"`
- `tick` (bước ngoài), `sim_tick` (bước gameplay, đứng yên khi `paused`), `phase_tick` (`0` lúc đổi pha): `int >= 0`
- `mode`: `"gather"` | `"quan"` | `"day"`
- `phase`: `"gather"` | `"quan"` | `"shop"`
- `state`: `"playing"` | `"paused"` | `"finished"`
- `time_left_ticks`: `int >= 0`
- `money`, `earned`, `reputation`, `score` (`earned + reputation_multiplier * floor(reputation)`)
- Bổ sung khi `mode == "day"`: `day` (`1..N`), `day_plan` (`{dishes, ingredients}`), `upgrades` (đã mua), `active_upgrades` (đang áp dụng ở Ngày này)

---

## 3. Snapshot riêng của `gather` ([`chonoi/sim/gather.py`](../../chonoi/sim/gather.py))

- `player`: `{pos: [x, d], vel: [vx, vd], heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`
- `hold`: mảng cá thể theo thứ tự nhặt LIFO `[{"id": str, "kind": str, "fresh": float}]` (v1.2+; `fresh` trong `[0, 100]`, ươn `< 30`), `hold_count`: `int`, `hold_capacity`: `int`
- `nodes`: `[{id, pos: [x, d], kind, ready, regrow_ticks}]` (`N1–N6`, thêm `keo_neo`; sắp theo `sort_by_id`)
- `fish`: `[{id, pos: [x, d], kind, heading_deg}]` (v1.3: `fish_initial: 8` chọn điểm đầu ca qua `Streams("fish_spawn")`, tối đa 12, bơi & sinh theo tick khi `random_fish=true`; sắp theo `sort_by_id`)
- `monsters`: `[{id, kind, pos: [x, d], waypoints: [[x1,d1],[x2,d2]], target_idx: 0|1, state: "patrol"|"chase"|"recoil", state_ticks_left: int, recoil_dir: null|[ux, ud]}]` (`M1` từ Ngày 1, `M2` từ Ngày 3; sắp theo `sort_by_id`)

---

## 4. Snapshot riêng của `quan` ([`chonoi/sim/quan.py`](../../chonoi/sim/quan.py)) & `shop` ([`chonoi/sim/day.py`](../../chonoi/sim/day.py))

- `quan`:
  - `player`: `{pos: [x, z], vel: [vx, vz]}`
  - `stock`: mảng cá thể `[{"id": str, "kind": str, "fresh": float}]` sắp theo `id_key` (v1.2+, gồm cả cá thể ươn & phần đang `reserved`)
  - `tables`: `[{id, pos: [x, z], customer_id: str | null}]` (`T1–T4`)
  - `hand`: `null` hoặc `{order_id, dish_id, base_price}` (`base_price` đã tính theo độ tươi)
  - `stoves`: `[{id, pos: [x, z], state: "idle"|"cooking"|"ready", dish: null|{order_id, dish_id, base_price}, cook_ticks_left, ready_ticks}]` (`B1–B2`)
  - `customers`: `[{id, table_id, dish_id, order_tick, state: "waiting"|"eating", patience_ticks_left, eat_ticks_left, order_status: "reserved"|"assigned"|"unfulfillable"|"served", reserved: [item_id, ...], base_price, tip}]` *(sắp theo `sort_by_id`; chỉ liệt kê khách còn ngồi; trong `day` chỉ chọn món thuộc `day_plan[day].dishes`)*
- `shop`: `stock`: mảng cá thể `[{"id": str, "kind": str, "fresh": float}]` (tồn dư từ ca quán, bỏ qua sau khi Shop đóng)

---

## 5. Kết thúc (`type: "end"`), CLI phụ trợ (v1.3) & Ranh giới Sáng tạo
- Dòng `end`: `type, ticks, sim_tick, mode, state, reason, money, earned, reputation, score` (+ `days_completed` khi `mode == "day"`, `reason: "days_complete"` khi đóng đủ Shop).
- `bench_cmd` ([`chonoi/bench.py`](../../chonoi/bench.py)): `--seed 42 --duration 30 --out bench.json` → `{avg_fps, p1_low_fps, frames, measured_s, load_ms}` (render phần mềm 1280×720 cảnh sáng lõi).
- `soak_cmd` ([`chonoi/soak.py`](../../chonoi/soak.py)): `--seed 7 --days 10 --out soak.json` → `{days, days_completed, crashes, results[], duration_s}` (bot tất định qua nhiều Ngày, kế hoạch D1–D5 lặp từ Ngày 6).
- **Ranh giới Sáng tạo:** Mọi đồ họa 2.5D, sprite CC0 Kenney (`chonoi/web/assets/`), Web Audio, cảnh báo + tương phản cao (`T`), và bếp nhiều section (`--no-creative` để tắt ở `live`) tách biệt khỏi `chonoi.headless`.
