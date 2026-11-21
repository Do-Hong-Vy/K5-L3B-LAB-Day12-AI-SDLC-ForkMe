# Danh sách sự kiện tích hợp (`events`, Contract v1.1)

> Mọi sự kiện được `sim.step(inp)` trả về dạng `(name, data)` và `runner.Session` ghi thành dòng JSONL **trước** snapshot cuối tick đó:
> `{"type":"event","tick":<k+1>,"phase":<phase>,["day":<int>],"name":<name>,"data":<dict>}` *(trường `"day"` thêm khi chạy `--mode day` ở v1.1)*.
>
> Nhiều thực thể được duyệt trong cùng tick phải đi theo thứ tự `ids.sort_by_id`.

---

## 1. Sự kiện buổi sáng (`phase: "gather"`, phát bởi `GatherSim`)

| Tên sự kiện | Payload `data` | Khi nào phát | Trạng thái |
|---|---|---|---|
| `node_regrown` | `{"node_id": str}` | Đầu bước 1, khi `regrow_ticks` giảm từ `1` về `0` (duyệt theo `sort_by_id`). | **Đã khóa (starter)** |
| `dive` | `{"pos": [x, d]}` | Sau bước 2, khi chuyển từ mặt nước (`d <= surface_depth`) xuống dưới nước (`d > surface_depth`). | **Đã chốt (PRD-0 mục E)** |
| `surface` | `{"pos": [x, d]}` | Sau bước 2, khi chuyển từ dưới nước lên mặt nước (`d <= surface_depth`). | **Đã chốt (PRD-0 mục E)** |
| `oxygen_empty` | `{"oxygen_ticks": 0}` | Bước 2, khi `oxygen_ticks` dưới nước giảm từ `> 0` xuống `0`. | **Đã chốt (PRD-0 mục E)** |
| `choke` | `{"hp": int}` | Bước 2, dưới nước với `oxygen_ticks == 0` khi `zero_oxy_ticks` đạt `choke_interval_ticks`, reset đếm về `0` và trừ `1` HP. | **Đã chốt (PRD-0 mục E)** |
| `faint` | `{"cause": "choke"\|"monster", "lost": [kind, ...], "hp": 0}` | Khi `choke` hoặc `monster_hit` (L2) làm `hp == 0`; `lost` là các vật phẩm trong giỏ mất theo LIFO. | **Cập nhật v1.1 (Ticket-02)** |
| `gather` | `{"node_id": str, "kind": str, "amount": int}` | Bước `interact` ngoài bến ở mặt nước, hái nút `ready` gần nhất (`N1–N6`, thêm `keo_neo`). | **Cập nhật v1.1 (Ticket-02)** |
| `fish_caught` | `{"fish_id": str, "kind": str, "yield": int}` | Bước `catch` dưới nước (`catch_cd_ticks == 0`), bắt đàn cá gần nhất trong `catch_radius` **theo vị trí trước khi cá bơi** (`ca_linh`/`ca_loc`/`ca_keo`). | **Cập nhật v1.1 (Ticket-02)** |
| `hold_full` | `{"action": "gather"\|"catch", "node_id"\|"fish_id": str, "required": int, "free": int}` | Bước hái hoặc bắt cá, khi nút/đàn cá trong tầm nhưng chỗ trống giỏ `free < required`. | **Đã chốt (PRD-0 mục E)** |
| `fish_spawned` | `{"id": str, "kind": str, "pos": [x, d]}` | Bước sau hết giờ (khi còn giờ và `random_fish=true`), tại `phase_tick = 360·k` (`k >= 1`) sau khi cá bơi nếu còn `< fish_max` và có điểm hợp lệ (`clearance > 1 m`). | **Mới v1.1 — L1 (`Do-Hong-Vy`)** |
| `gather_end` | `{"reason": "time"\|"docked"\|"fainted", "inventory": {"items": {...}}}` | Khi ngất (`fainted`), cập bến (`docked`), hoặc hết giờ (`time`). Dừng sim & kích hoạt ghi kho. | **Đã khóa (starter)** |

*Bên nghe:* Headless JSONL, Live UI (`gather_end` còn kích hoạt `runner` ghi file kho).

---

## 2. Sự kiện buổi tối (`phase: "quan"`, phát bởi `QuanSim`)

| Tên sự kiện | Payload `data` | Khi nào phát | Trạng thái |
|---|---|---|---|
| `dish_ready` | `{"stove_id": str, "order_id": str, "dish_id": str}` | Bước 2 (duyệt bếp theo `sort_by_id`), khi bếp `cooking` có `cook_ticks_left` về `0` → `ready`. | **Đã chốt (PRD-0 mục E)** |
| `cook_started` | `{"stove_id": str, "order_id": str, "dish_id": str, "items": [kind, ...], "base_price": int}` | Bước 3 (`interact` bếp `idle`), lấy đơn `reserved` cũ nhất theo `(order_tick, table_id)`, tiêu nguyên liệu giữ chỗ. | **Đã chốt (PRD-0 mục E)** |
| `dish_picked` | `{"stove_id": str, "order_id": str, "dish_id": str}` | Bước 3 (`interact` bếp `ready` khi `hand is None`), chuyển món lên tay, bếp về `idle`. | **Đã chốt (PRD-0 mục E)** |
| `served` | `{"order_id": str, "table_id": str, "dish_id": str, "patience_ticks_left": int, "base_price": int, "tip": int}` | Bước 3 (`interact` bàn có khách `waiting` khớp `hand.order_id`), giao món & chốt `tip`. | **Đã chốt (PRD-0 mục E)** |
| `paid` | `{"order_id": str, "table_id": str, "base_price": int, "tip": int, "amount": int, "reason": "finished_eating"\|"closing"}` | Bước 4 (duyệt theo ID bàn), khi khách `eating` có `eat_ticks_left == 0` hoặc khi đóng ca (`closing`). | **Đã chốt (PRD-0 mục E)** |
| `customer_left` | `{"order_id": str, "table_id": str, "reason": "patience"\|"closing", "reputation": float}` | Bước 4 (duyệt theo ID bàn), khi khách `waiting` hết kiên nhẫn hoặc còn chờ lúc đóng ca. | **Đã chốt (PRD-0 mục E)** |
| `customer_arrived` | `{"order_id": str, "table_id": str, "dish_id": str}` | Bước 5 (còn giờ, đúng lịch khách), có bàn trống và chọn được món đủ nguyên liệu khả dụng. | **Đã chốt (PRD-0 mục E)** |
| `no_dish` | `{}` | Bước 5 (còn giờ, đúng lịch khách), có bàn trống nhưng không có món nào đủ nguyên liệu khả dụng. | **Đã chốt (PRD-0 mục E)** |
| `quan_end` | `{"reason": "time", "money": int, "earned": int, "shift_earned": int, "reputation": float}` | Bước 4 khi `time_left_ticks == 0`, sau khi xử lý khách `eating` & `waiting`. | **Đã khóa (starter)** |

*Bên nghe:* Headless JSONL, Live UI.
