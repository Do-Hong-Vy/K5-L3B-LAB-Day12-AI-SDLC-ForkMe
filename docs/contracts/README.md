# Hợp đồng tích hợp — Nhóm ForkMe (Contract v1.0)

Tài liệu này chốt hợp đồng tích hợp giữa 4 module của nhóm (`sim/gather`, `sim/quan`, `client/ui`, `qa`) theo đúng **PRD-0 & Test Contract v1.0**. Khi thay đổi hợp đồng ở các phase sau, phải báo cả nhóm và ghi ADR tại `docs/adr/`.

---

## 1. Schema file kho (Contract G — `gather` → `quan`)

- **Định dạng JSON:** Object gốc chỉ có duy nhất một khóa `"items"`, ánh xạ từ `kind` sang số nguyên dương (`int > 0`; các nguyên liệu có số lượng `0` được lược bỏ khi ghi; kho rỗng là `{"items":{}}`).
- **Danh sách `kind` hợp lệ (Phase 1):** `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`.
- **File mẫu hợp lệ:** [`inventory.sample.json`](inventory.sample.json)
  ```json
  {"items":{"bong_sung":2,"ca_loc":1}}
  ```
- **Quy tắc tích hợp:**
  - `gather` chỉ ghi file kho (`--inventory-out`) **đúng 1 lần** khi phát sự kiện `gather_end` (ngất `fainted` ghi kho rỗng `{"items":{}}`; chạm `--ticks` trước khi kết thúc buổi sáng thì không tạo/ghi đè file). Nội dung file khớp 100% với trường `data.inventory` của sự kiện `gather_end`.
  - Ghi nguyên tử qua file tạm cùng thư mục rồi `os.replace` (`chonoi/inventory.py`).
  - `quan` đọc kho qua `--inventory` (hoặc `scenario.quan.stock`, không dùng đồng thời cả hai). Nếu sai schema, có `kind` lạ hoặc số lượng âm → thoát mã `2` trước khi chạy mô phỏng.

---

## 2. Giao diện giữa `sim/*` và `client/ui` (`chonoi.live` ↔ `chonoi/web/index.html`)

### 2.1. Trạng thái `client/ui` đọc (`GET /state`)
`LiveGame.state_json()` trả về JSON gộp từ `Session.snapshot()` và metadata của phiên chạy:
- **Trường chung mọi pha:**
  - `type`: `"snapshot"`, `tick`, `sim_tick`, `mode` (`"gather"` | `"quan"`), `phase`, `phase_tick`, `state` (`"playing"` | `"finished"`), `time_left_ticks`, `money`, `earned`, `reputation`, `score` (`earned + 100 * floor(reputation)`).
  - Trường bổ sung từ `LiveGame`: `meta` (`tuning[mode]`), `events` (tối đa 40 sự kiện gần nhất `{type, tick, phase, name, data}`), `finished` (`bool`), `reason` (`str | null`), `error` (`str | null`).
- **Trường riêng pha `gather`:**
  - `player`: `{pos: [x, d], vel: [vx, vd], heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`
  - `hold`: mảng `kind` theo thứ tự nhặt (LIFO, phần tử cuối là mới nhất), `hold_count`, `hold_capacity`
  - `nodes`: `[{id, pos: [x, d], kind, ready, regrow_ticks}]` (sắp theo `sort_by_id`)
  - `fish`: `[{id, pos: [x, d], kind, heading_deg}]` (sắp theo `sort_by_id`)
- **Trường riêng pha `quan`:**
  - `player`: `{pos: [x, z]}`
  - `stock`: `{kind: count}` (chỉ gồm các khóa có `count > 0`, bao gồm cả phần đang `reserved`)
  - `hand`: `null` hoặc `{order_id, dish_id, base_price}`
  - `stoves`: `[{id, pos: [x, z], state: "idle"|"cooking"|"ready", dish: null|{order_id, dish_id, base_price}, cook_ticks_left, ready_ticks}]`
  - `tables`: `[{id, pos: [x, z], customer_id: str|null}]`
  - `customers`: `[{id, table_id, dish_id, order_tick, state: "waiting"|"eating", patience_ticks_left, eat_ticks_left, order_status: "reserved"|"assigned"|"unfulfillable"|"served", reserved: {kind: count}, base_price, tip}]`

### 2.2. Lệnh `client/ui` gửi vào
- `POST /input`: `{"move": [a, b], "interact": bool, "catch": bool}`
  - `a, b ∈ [-1, 1]`. Ở `gather`: `[x, d]` (`d > 0` hướng xuống đáy sông). Ở `quan`: `[x, z]` (`z > 0` hướng lên/bắc).
  - `interact` (phím `E`) và `catch` (phím `Space`) được `LiveInputs` bắt cạnh lên (`false -> true`) giữa các tick.
- `POST /restart`: Khởi động lại lượt chơi hiện tại với cùng `seed` và `scenario`.
- **Nguyên tắc cô lập:** Mọi đồ họa, HUD, âm thanh, hướng dẫn và tính năng sáng tạo ở `client/ui` chỉ đọc từ `GET /state`, tuyệt đối không sửa state mô phỏng và tự động tắt khi chạy `chonoi.headless`.

---

## 3. Danh sách sự kiện (Contract E — PRD-0)

### 3.1. Sự kiện buổi sáng (`phase: "gather"`, phát bởi `GatherSim`)

| Tên sự kiện (`name`) | Payload (`data`) | Khi nào phát | Ai nghe |
|---|---|---|---|
| `node_regrown` | `{"node_id": str}` | Đầu bước 1, khi `regrow_ticks` của nút giảm từ `1` về `0` (duyệt theo `sort_by_id`). | Headless JSONL, Live UI |
| `dive` | `{"pos": [x, d]}` | Sau di chuyển bước 2, khi chuyển từ mặt nước (`d <= surface_depth`) xuống dưới nước (`d > surface_depth`). | Headless JSONL, Live UI |
| `surface` | `{"pos": [x, d]}` | Sau di chuyển bước 2, khi chuyển từ dưới nước lên mặt nước (`d <= surface_depth`). | Headless JSONL, Live UI |
| `oxygen_empty` | `{"oxygen_ticks": 0}` | Bước 2, khi `oxygen_ticks` dưới nước giảm từ `> 0` xuống `0`. | Headless JSONL, Live UI |
| `choke` | `{"hp": int}` | Bước 2, dưới nước với `oxygen_ticks == 0` khi `zero_oxy_ticks` đạt `choke_interval_ticks` (60), reset đếm về 0 và trừ 1 Máu. | Headless JSONL, Live UI |
| `faint` | `{"cause": "choke", "lost": [kind, ...], "hp": 0}` | Bước 2, ngay sau `choke` làm `hp == 0`; `lost` là giỏ bỏ ra theo thứ tự LIFO (nhặt sau bỏ trước). | Headless JSONL, Live UI |
| `gather` | `{"node_id": str, "kind": str, "amount": int}` | Bước 3 (`interact` ngoài bến, ở mặt nước), hái nút `ready` gần nhất trong `interact_radius` khi đủ chỗ trong giỏ. | Headless JSONL, Live UI |
| `fish_caught` | `{"fish_id": str, "kind": str, "yield": int}` | Bước 4 (`catch` dưới nước, `catch_cd_ticks == 0`), bắt đàn cá gần nhất trong `catch_radius` khi đủ chỗ cho toàn bộ `yield`. | Headless JSONL, Live UI |
| `hold_full` | `{"action": "gather"\|"catch", "node_id"\|"fish_id": str, "required": int, "free": int}` | Bước 3 hoặc 4, khi nút/đàn cá trong tầm nhưng số ô trống `free < required`. | Headless JSONL, Live UI |
| `gather_end` | `{"reason": "time"\|"docked"\|"fainted", "inventory": {"items": {...}}}` | Khi ngất (`fainted`), cập bến (`docked`), hoặc hết giờ (`time`). Dừng mô phỏng và kích hoạt ghi file kho. | Runner, Inventory, Headless JSONL, Live UI |

### 3.2. Sự kiện buổi tối (`phase: "quan"`, phát bởi `QuanSim`)

| Tên sự kiện (`name`) | Payload (`data`) | Khi nào phát | Ai nghe |
|---|---|---|---|
| `dish_ready` | `{"stove_id": str, "order_id": str, "dish_id": str}` | Bước 2 (duyệt bếp theo ID), khi bếp `cooking` có `cook_ticks_left` về `0` chuyển sang `ready`. | Headless JSONL, Live UI |
| `cook_started` | `{"stove_id": str, "order_id": str, "dish_id": str, "items": [kind, ...], "base_price": int}` | Bước 3 (`interact` tại bếp `idle`), lấy đơn `reserved` cũ nhất theo `(order_tick, table_id)`, tiêu nguyên liệu giữ chỗ (`items` sắp theo mã kind). | Headless JSONL, Live UI |
| `dish_picked` | `{"stove_id": str, "order_id": str, "dish_id": str}` | Bước 3 (`interact` tại bếp `ready` khi `hand is None`), chuyển món lên tay và bếp về `idle`. | Headless JSONL, Live UI |
| `served` | `{"order_id": str, "table_id": str, "dish_id": str, "patience_ticks_left": int, "base_price": int, "tip": int}` | Bước 3 (`interact` tại bàn có khách `waiting` khớp `hand.order_id`), giao món và chốt `tip`. | Headless JSONL, Live UI |
| `paid` | `{"order_id": str, "table_id": str, "base_price": int, "tip": int, "amount": int, "reason": "finished_eating"\|"closing"}` | Bước 4 (duyệt theo ID bàn), khi khách `eating` có `eat_ticks_left == 0` hoặc khi đóng ca (`closing`). | Headless JSONL, Live UI |
| `customer_left` | `{"order_id": str, "table_id": str, "reason": "patience"\|"closing", "reputation": float}` | Bước 4 (duyệt theo ID bàn), khi khách `waiting` hết kiên nhẫn (`patience`, còn giờ) hoặc còn chờ lúc đóng ca (`closing`). | Headless JSONL, Live UI |
| `customer_arrived` | `{"order_id": str, "table_id": str, "dish_id": str}` | Bước 5 (khi còn giờ, đúng lịch khách), có bàn trống và chọn được món đủ nguyên liệu khả dụng. | Headless JSONL, Live UI |
| `no_dish` | `{}` | Bước 5 (khi còn giờ, đúng lịch khách), có bàn trống nhưng không có món nào đủ nguyên liệu khả dụng. | Headless JSONL, Live UI |
| `quan_end` | `{"reason": "time", "money": int, "earned": int, "shift_earned": int, "reputation": float}` | Bước 4 khi `time_left_ticks == 0`, sau khi đã thanh toán khách `eating` và cho khách `waiting` rời bàn. | Runner, Headless JSONL, Live UI |
