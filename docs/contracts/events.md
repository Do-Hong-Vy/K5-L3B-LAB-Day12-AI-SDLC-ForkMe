# Danh sách sự kiện tích hợp (`events`, Contract v1.3 / gameplay v1.2)

> Mọi sự kiện được `sim.step(inp)` trả về dạng `(name, data)` và `runner.Session` ghi thành dòng JSONL **trước** snapshot cuối tick đó:
> `{"type":"event","tick":<k+1>,"phase":<phase>,["day":<int>],"name":<name>,"data":<dict>}` *(trường `"day"` thêm khi chạy `--mode day`)*.
>
> Nhiều thực thể được duyệt trong cùng tick phải đi theo thứ tự `ids.sort_by_id`.

---

## 1. Sự kiện buổi sáng (`phase: "gather"`, phát bởi `GatherSim`)

| Tên sự kiện | Payload `data` | Khi nào phát |
|---|---|---|
| `node_regrown` | `{"node_id": str}` | Đầu bước 1, khi `regrow_ticks` giảm từ `1` về `0` (theo `sort_by_id`). |
| `spoiled` | `{"item_id": str, "kind": str, "location": "hold"}` | Bước 1 (v1.2), khi độ tươi cá thể trong giỏ đi từ `>= 30` xuống `< 30` (theo `id_key`), phát đúng 1 lần. |
| `dive` | `{"pos": [x, d]}` | Bước 2, chuyển từ mặt nước (`d <= surface_depth`) xuống dưới nước (`d > surface_depth`). |
| `surface` | `{"pos": [x, d]}` | Bước 2, chuyển từ dưới nước lên mặt nước (`d <= surface_depth`). |
| `oxygen_empty` | `{"oxygen_ticks": 0}` | Bước 2, `oxygen_ticks` dưới nước giảm từ `> 0` xuống `0`. |
| `choke` | `{"hp": int}` | Bước 2, dưới nước với `oxygen_ticks == 0` khi `zero_oxy_ticks` đạt `choke_interval_ticks`, trừ `1` HP. |
| `monster_hit` | `{"monster_id": str, "hp": int, "lost": [item, ...], "pos": [x, d]}` | Bước 2.5 (L2), khi quái gần nhất (`<= hit_radius`, `d >= depths[0]`, `invuln_ticks == 0`) chạm: trừ `1` HP, bỏ `floor(n * loss_ratio)` theo LIFO (`lost` là mảng `{id, kind, fresh}` ở v1.2), đặt bất tử `90` tick và `recoil` `60` tick. |
| `faint` | `{"cause": "choke"\|"monster", "lost": [item, ...], "hp": 0}` | Khi `choke` hoặc `monster_hit` làm `hp == 0`; `lost` là phần giỏ còn lại theo LIFO trước khi `gather_end(fainted)`. |
| `gather` | `{"node_id": str, "kind": str, "amount": int}` | Bước `interact` ngoài bến ở mặt nước, hái nút `ready` gần nhất (`N1–N6`, thêm `keo_neo`). |
| `fish_caught` | `{"fish_id": str, "kind": str, "yield": int}` | Bước `catch` dưới nước (`catch_cd_ticks == 0`), bắt đàn cá gần nhất theo vị trí trước khi cá bơi (`ca_linh`/`ca_loc`/`ca_keo`). |
| `hold_full` | `{"action": "gather"\|"catch", "node_id"\|"fish_id": str, "required": int, "free": int}` | Khi nút/đàn cá trong tầm nhưng chỗ trống giỏ `free < required`. |
| `fish_spawned` | `{"id": str, "kind": str, "pos": [x, d]}` | Khi còn giờ và `random_fish=true`, tại `phase_tick = 360·k` (`k >= 1`) sau khi cá bơi nếu `< fish_max` và còn điểm hợp lệ (`clearance > 1 m`). |
| `gather_end` | `{"reason": "time"\|"docked"\|"fainted", "inventory": {"items": [...]}}` | Khi ngất (`fainted`), cập bến (`docked`), hoặc hết giờ (`time`); `inventory.items` là mảng `{id, kind, fresh}` ở v1.2+. |

---

## 2. Sự kiện buổi tối (`phase: "quan"`, phát bởi `QuanSim`)

| Tên sự kiện | Payload `data` | Khi nào phát |
|---|---|---|
| `spoiled` | `{"item_id": str, "kind": str, "location": "stock"}` | Bước 1 (v1.2), khi cá thể trong kho quán đi từ `>= 30` xuống `< 30` theo id (phát hết trước khi xử lý nhả/giữ lại đơn bị ươn). |
| `dish_ready` | `{"stove_id": str, "order_id": str, "dish_id": str}` | Bước 2 (theo `sort_by_id` bếp `B1`/`B2`), khi `cook_ticks_left` về `0` → `ready`. |
| `cook_started` | `{"stove_id": str, "order_id": str, "dish_id": str, "items": [item, ...], "base_price": int}` | Bước 3 (`interact` bếp `idle`), lấy đơn `reserved` cũ nhất theo `(order_tick, table_id)`, tiêu đúng id đang giữ; ở v1.2 `items` là mảng `{id, kind, fresh}` sắp `kind` rồi `id`, `base_price = floor(giá × trung bình fresh / 100)`. |
| `dish_picked` | `{"stove_id": str, "order_id": str, "dish_id": str}` | Bước 3 (`interact` bếp `ready` khi `hand is None`). |
| `served` | `{"order_id": str, "table_id": str, "dish_id": str, "patience_ticks_left": int, "base_price": int, "tip": int}` | Bước 3 (`interact` bàn `T1–T4` có khách `waiting` khớp `hand.order_id`), chốt `tip = floor(base_price × tip_rate)` nếu còn `>= 50%` kiên nhẫn. |
| `paid` | `{"order_id": str, "table_id": str, "base_price": int, "tip": int, "amount": int, "reason": "finished_eating"\|"closing"}` | Bước 4 (theo id bàn), khi khách `eating` ăn xong hoặc đóng ca (`closing`). |
| `customer_left` | `{"order_id": str, "table_id": str, "reason": "patience"\|"closing", "reputation": float}` | Bước 4 (theo id bàn), khách `waiting` hết kiên nhẫn (`-0.5` uy tín) hoặc còn chờ lúc đóng ca (không trừ uy tín). |
| `customer_arrived` | `{"order_id": str, "table_id": str, "dish_id": str}` | Bước 5 (còn giờ, đúng lịch khách), bàn trống id nhỏ nhất + món khả dụng (trong `day`: lọc theo `day_plan[day].dishes`). |
| `no_dish` | `{}` | Bước 5, có bàn trống nhưng không món nào đủ nguyên liệu khả dụng (chưa ươn). |
| `quan_end` | `{"reason": "time", "money": int, "earned": int, "shift_earned": int, "reputation": float}` | Bước 4 khi `time_left_ticks == 0`, sau khi xử lý khách `eating` & `waiting`. |

---

## 3. Sự kiện Vòng ngày (`--mode day`), `Shop` & `Pause`

| Tên sự kiện | Payload `data` | Khi nào phát |
|---|---|---|
| `day_start` | `{}` | Khi dựng Ngày mới (`tick: 0` trước snapshot đầu, hoặc cùng tick đóng Shop Ngày trước). |
| `day_plan` | `{"dishes": {id: int}, "ingredients": {kind: int}}` | Ngay sau `day_start`, công bố thực đơn & nguyên liệu cần của Ngày đó. |
| `phase_start` | `{}` | Khi mở từng pha `gather`, `quan`, `shop` (`phase` đổi sang pha mới; event kết thúc pha cũ vẫn mang `phase` cũ). |
| `paused` | `{}` | Nhận cạnh lên `pause` lúc đang chơi (`tick` ngoài tăng, `sim_tick`/`phase_tick`/timer/hao tươi đứng yên). |
| `resumed` | `{}` | Nhận cạnh lên `pause` lúc đang `paused` (chạy gameplay ngay trong bước đó). |
| `bought` | `{"upgrade": str, "level": int, "price": int, "money": int}` | Trong `shop`, lệnh `buy` hợp lệ đủ `money` (`upgrades[id]` tăng ngay, hiệu lực từ Ngày kế `active_upgrades`). |
| `buy_failed` | `{"action": str, "reason": "funds"\|"max_level"\|"unknown"}` | Trong `shop`, lệnh `buy` thiếu tiền, tối đa cấp hoặc không hỗ trợ. |
| `shop_end` | `{"reason": "done"\|"time"}` | Nhận cạnh `shop_done` (`done`) hoặc hết `max_ticks` (`time`); tăng `days_completed`. |

*Sáng tạo tắt ở headless:* Các sự kiện sáng tạo (`prep_started`/`prep_done` của bếp nhiều section) chỉ phát khi chạy `chonoi.live` không truyền `--no-creative`.
