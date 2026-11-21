# Giao diện tích hợp `sim/*` ↔ `client/ui` (Contract v1.1)

> UI chỉ **ĐỌC** snapshot từ `GET /state` (hoặc `Session.snapshot()`) và **GỬI** input qua `POST /input`, `POST /restart`. Tuyệt đối không tự tính lại luật chơi ở phía client.
> Ghi chú v1.1: Lát L1 đã cập nhật mục `gather` (N1–N6 gồm `keo_neo`, 8 đàn `ca_linh`/`ca_loc`/`ca_keo`, cá bơi & sinh thêm). Các mục L2 (`monsters[]`), L3 (`B2`, `T2–T4`, 6 món), L4 (`--mode day`, `shop`, `pause`) sẽ được điền tiếp khi các lát tương ứng gộp.

---

## 1. Kênh giao tiếp Live ([`chonoi/live.py`](../../chonoi/live.py))

| Endpoint | Phương thức | Payload / Phản hồi | Ghi chú |
|---|---|---|---|
| `/state` | `GET` | JSON snapshot hiện tại + `meta` (`tuning[mode]`), `events` (tối đa 40 sự kiện gần nhất `{type, tick, phase, name, data}`), `finished` (`bool`), `reason` (`str \| null`), `error` (`str \| null`) | Poll định kỳ phía client (`16ms` trong starter) |
| `/input` | `POST` | `{"move": [a, b], "interact": bool, "catch": bool}` | `a, b ∈ [-1, 1]`. `gather`: `+b` hướng xuống (`d+`); `quan`: `+b` hướng bắc (`z+`). Cạnh lên do `LiveInputs` bắt |
| `/restart` | `POST` | `{}` → `{"ok": true}` | Chơi lại cùng `seed` & `scenario` |

---

## 2. Trường Snapshot chung ([`chonoi/runner.py`](../../chonoi/runner.py))

- `type`: `"snapshot"`
- `tick`, `sim_tick`, `phase_tick`: `int >= 0`
- `mode`: `"gather"` | `"quan"` (v1.0; `"day"` từ v1.1)
- `phase`: `"gather"` | `"quan"`
- `state`: `"playing"` | `"finished"`
- `time_left_ticks`: `int >= 0`
- `money`, `earned`, `reputation`, `score` (`earned + reputation_multiplier * floor(reputation)`)

---

## 3. Snapshot riêng của `gather` ([`chonoi/sim/gather.py`](../../chonoi/sim/gather.py))

- `player`: `{pos: [x, d], vel: [vx, vd], heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`
- `hold`: `list[str]` (thứ tự nhặt, phần tử cuối là mới nhất — LIFO; gồm 6 loại v1.1: `ca_loc`, `ca_linh`, `ca_keo`, `bong_dien_dien`, `bong_sung`, `keo_neo`), `hold_count`: `int`, `hold_capacity`: `int`
- `nodes`: `[{id, pos: [x, d], kind, ready, regrow_ticks}]` (6 nút `N1–N6`, sắp theo `sort_by_id`)
- `fish`: `[{id, pos: [x, d], kind, heading_deg}]` (mặc định 8 đàn đầu ca ở 8 điểm khác nhau, tối đa 12, bơi & sinh theo tick khi `random_fish=true`; sắp theo `sort_by_id`)

---

## 4. Snapshot riêng của `quan` ([`chonoi/sim/quan.py`](../../chonoi/sim/quan.py))

- **Đã khóa từ khung starter:**
  - `player`: `{pos: [x, z], vel: [vx, vz]}` *(PRD-0 mục D — starter chỉ có `pos`, `sim/quan` bổ sung `vel` ở CP1, xem `docs/clarify.md` #9)*
  - `stock`: `{kind: count}` (chỉ chứa mục `> 0`, sắp theo key; gồm cả phần đang `reserved` khi chưa trừ lúc nấu)
  - `tables`: `[{id, pos: [x, z], customer_id: str | null}]`
- **Đã chốt theo PRD-0 mục D, E** (PO `Cuubeo` đối chiếu, `docs/clarify.md` #3):
  - `hand`: `null` hoặc `{order_id, dish_id, base_price}` *(Lưu ý: `chonoi/web/index.html` hiện đọc an toàn cả `str` và `hand.dish_id`)*
  - `stoves`: `[{id, pos: [x, z], state: "idle"|"cooking"|"ready", dish: null|{order_id, dish_id, base_price}, cook_ticks_left, ready_ticks}]` *(Lưu ý: `index.html` starter đang in trực tiếp `st.dish`; nếu `dish` là object thì `client/ui` cần đọc `st.dish.dish_id ?? st.dish`)*
  - `customers`: `[{id, table_id, dish_id, order_tick, state: "waiting"|"eating", patience_ticks_left, eat_ticks_left, order_status: "reserved"|"assigned"|"unfulfillable"|"served", reserved: {kind: count}, base_price, tip}]` *(sắp theo `sort_by_id`; **chỉ liệt kê khách còn ngồi**)*

---

## 5. Ranh giới Sáng tạo của nhóm
- Mọi đồ họa, HUD, âm thanh, hướng dẫn và tính năng sáng tạo đặt tại `client/ui` (`chonoi/web/`), chỉ đọc `GET /state`.
- Nếu có trạng thái phụ phục vụ hiển thị, phải **tắt hoàn toàn** khi chạy `chonoi.headless` để không làm đổi JSONL chuẩn.
