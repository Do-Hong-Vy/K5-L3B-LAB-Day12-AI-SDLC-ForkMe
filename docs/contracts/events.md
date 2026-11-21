# Danh sách sự kiện tích hợp (`events`, Contract v1.0)

> Mọi sự kiện được `sim.step(inp)` trả về dạng `(name, data)` và `runner.Session` ghi thành dòng JSONL:
> `{"type":"event","tick":<k+1>,"phase":<phase>,"name":<name>,"data":<dict>}`

## 1. Sự kiện chế độ `gather` (`chonoi/sim/gather.py`)

| Tên sự kiện | Nguồn phát | Bên nghe | Payload `data` | Trạng thái contract |
|---|---|---|---|---|
| `node_regrown` | `GatherSim` | `client/ui`, `qa` | `{"node_id": str}` | Đã có sẵn trong starter |
| `dive` | `GatherSim` | `client/ui`, `qa` | `{"pos": [x, d]}` | Tham chiếu comment `gather.py` *(chờ PO xác nhận key `pos`)* |
| `surface` | `GatherSim` | `client/ui`, `qa` | `{"pos": [x, d]}` | Tham chiếu comment `gather.py` *(chờ PO xác nhận key `pos`)* |
| `oxygen_empty` | `GatherSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khi oxy chuyển từ `> 0` về `0` |
| `choke` | `GatherSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khi hết oxy dưới nước đủ `choke_interval_ticks`, `-1` HP |
| `faint` | `GatherSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khi `hp` về `0` |
| `gather` | `GatherSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` (thường `node_id`, `kind`, ...) | Hái nút thành công ở mặt nước |
| `fish_caught` | `GatherSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` (thường `fish_id`, `kind`, ...) | Bắt cá thành công dưới nước |
| `hold_full` | `GatherSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Không đủ chỗ trong giỏ khi hái/bắt cá |
| `gather_end` | `GatherSim`, `runner` | `client/ui`, `inventory`, `qa` | `{"reason": "docked"\|"time"\|"fainted", "inventory": {"items": {...}}}` | Đã có sẵn trong starter |

## 2. Sự kiện chế độ `quan` (`chonoi/sim/quan.py`)

| Tên sự kiện | Nguồn phát | Bên nghe | Payload `data` | Trạng thái contract |
|---|---|---|---|---|
| `customer_arrived` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khách vào bàn và gọi món |
| `no_dish` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khách đến nhưng không còn món nấu được |
| `customer_left` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khách hết kiên nhẫn bỏ đi |
| `cook_started` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Bắt đầu nấu tại bếp |
| `dish_ready` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Bếp nấu xong món |
| `dish_picked` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Nhặt món từ bếp lên tay |
| `served` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Đặt món phục vụ khách tại bàn |
| `paid` | `QuanSim` | `client/ui`, `qa` | `[Chờ PO đối chiếu PRD-0]` | Khách ăn xong trả tiền (và boa nếu đạt) |
| `quan_end` | `QuanSim` | `client/ui`, `qa` | `{"reason": "time", "money": num, "earned": num, "shift_earned": num, "reputation": num}` | Đã có sẵn trong starter |

## 3. Thứ tự phát sự kiện trong một bước
- Mọi sự kiện trong cùng 1 tick được ghi **trước** snapshot cuối tick đó (`runner.Session.step` → `JsonlWriter`).
- Nhiều thực thể được duyệt trong cùng tick phải duyệt theo `ids.sort_by_id` để đảm bảo thứ tự tất định.
