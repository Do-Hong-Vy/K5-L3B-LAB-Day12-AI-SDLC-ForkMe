# Hợp đồng tích hợp (Nhóm ForkMe — Contract v1.0)

> Chốt tại **CP0** giữa `sim/gather` (`Do-Hong-Vy`), `sim/quan` (`Cuubeo`), `client/ui` (`Phog2811`) và `qa` (`Nguyenquoctoan0310`).
> **Quy tắc khóa:** Không tự ý sửa `docs/contracts/`, `game.contract.json` hoặc schema kho khi chưa báo cả nhóm. Mọi thay đổi ở Phase 2–4 phải ghi kèm ADR trong [`docs/adr/`](../adr/0000-template.md).

## 1. Schema file kho (Contract G)
- Định dạng JSON hợp lệ duy nhất khóa gốc `"items"`:
  ```json
  {"items": {"<ingredient_id>": <int >= 1>}}
  ```
- Danh sách nguyên liệu Phase 1 (`KINDS_P1` trong [`chonoi/inventory.py`](../../chonoi/inventory.py)): `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`.
- Quy tắc đọc/ghi (đã khóa trong `chonoi/inventory.py`):
  - Khi ghi (`write_inventory`): chỉ giữ mục có số lượng `> 0`, sắp key tăng dần (`sorted(items)`), ghi nguyên tử qua file tạm cùng thư mục.
  - Khi đọc (`read_inventory`): từ chối khóa gốc khác `{"items"}`, nguyên liệu lạ, số âm, hoặc kiểu không phải số nguyên (`BadInput` → mã thoát `2`).
  - Lệnh `gather` chỉ ghi kho **một lần** khi có `gather_end` (`docked`, `time`, hoặc `fainted` → kho rỗng `{}`), không ghi khi dừng do `tick_limit`.
  - Lệnh `quan` không được truyền đồng thời `--inventory` và `scenario.quan.stock` (mâu thuẫn → mã thoát `2`).
- File kho mẫu hợp lệ: [`inventory.sample.json`](inventory.sample.json).

## 2. Giao diện giữa `sim/*` và `client/ui`
- Chi tiết snapshot và input: xem [`sim-ui-interface.md`](sim-ui-interface.md).

## 3. Danh sách sự kiện
- Chi tiết tên sự kiện, payload `data`, nguồn phát & bên tiêu thụ: xem [`events.md`](events.md).

> **Lưu ý kiểm chứng PRD-0:** Các trường/payload chi tiết chưa có sẵn trong starter được đánh dấu `[Chờ PO đối chiếu PRD-0]` và đã liệt kê tại [`docs/clarify.md`](../clarify.md).
