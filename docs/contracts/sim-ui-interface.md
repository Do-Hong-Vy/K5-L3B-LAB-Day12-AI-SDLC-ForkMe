# Giao diện tích hợp `sim/*` ↔ `client/ui` (Contract v1.0)

> UI chỉ **ĐỌC** snapshot từ `GET /state` (hoặc `Session.snapshot()`) và **GỬI** input qua `POST /input`, `POST /restart`. Tuyệt đối không tính lại luật chơi ở phía client.

## 1. Kênh giao tiếp Live ([`chonoi/live.py`](../../chonoi/live.py))

| Endpoint | Phương thức | Payload / Phản hồi | Ghi chú |
|---|---|---|---|
| `/state` | `GET` | JSON snapshot hiện tại + `meta` (`tuning[mode]`), `events` (tối đa 40 sự kiện gần nhất), `finished` (`bool`), `reason` (`str \| null`), `error` (`str \| null`) | Poll định kỳ phía client |
| `/input` | `POST` | `{"move": [a, b], "interact": bool, "catch": bool}` | `a, b ∈ [-1, 1]`. `gather`: `+b` là xuống (`d+`); `quan`: `+b` là lên bắc (`z+`). Cạnh lên do `LiveInputs` xử lý |
| `/restart` | `POST` | `{}` → `{"ok": true}` | Chơi lại cùng `seed` & `scenario` |

## 2. Trường Snapshot chung ([`chonoi/runner.py`](../../chonoi/runner.py))

Mọi dòng `snapshot` đều có:
- `type`: `"snapshot"`
- `tick`, `sim_tick`, `phase_tick`: số nguyên `>= 0`
- `mode`: `"gather"` | `"quan"` (v1.0; `"day"` từ v1.1)
- `phase`: `"gather"` | `"quan"`
- `state`: `"playing"` | `"finished"`
- `time_left_ticks`: số tick còn lại
- `money`, `earned`, `reputation`, `score` (`earned + reputation_multiplier * floor(reputation)`)

## 3. Snapshot riêng của `gather` ([`chonoi/sim/gather.py`](../../chonoi/sim/gather.py))

- `player`: `{pos: [x, d], vel: [vx, vd], heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`
- `hold`: `list[str]` (thứ tự nhặt, phần tử cuối là mới nhất — LIFO)
- `hold_count`: `int`, `hold_capacity`: `int`
- `nodes`: `[{id, pos: [x, d], kind, ready, regrow_ticks}]` (sắp theo `id_key`)
- `fish`: `[{id, pos: [x, d], kind, heading_deg}]` (sắp theo `id_key`)

## 4. Snapshot riêng của `quan` ([`chonoi/sim/quan.py`](../../chonoi/sim/quan.py))

- `player`: `{pos: [x, z]}`
- `stock`: `{kind: qty}` (chỉ chứa mục `> 0`, sắp theo key)
- `hand`: `null | str | {dish_id, ...}` *(UI hỗ trợ cả `str` và object có `dish_id`; [Chờ PO đối chiếu PRD-0] để chốt kiểu chính xác)*
- `stoves`: `[{id, pos: [x, z], state ("idle"|"cooking"|"ready"), dish, cook_ticks_left, ready_ticks}]`
- `tables`: `[{id, pos: [x, z], customer_id}]`
- `customers`: danh sách khách sắp theo `id_key`. Các trường UI đang đọc: `id`, `table_id`, `state`, `dish_id`, `patience_ticks_left` *(trường `reserved`, `eat_ticks_left`, v.v. [Chờ PO đối chiếu PRD-0])*

## 5. Ranh giới Sáng tạo của nhóm
- Tính năng sáng tạo đồ họa/âm thanh/HUD nằm hoàn toàn ở `chonoi/web/` (hoặc client riêng), chỉ đọc trường snapshot hợp lệ hoặc hiệu ứng phía trình duyệt.
- Nếu thêm trạng thái hiển thị phía sim, phải **tắt hoàn toàn** khi chạy `chonoi.headless` để không làm lệch JSONL chuẩn.
