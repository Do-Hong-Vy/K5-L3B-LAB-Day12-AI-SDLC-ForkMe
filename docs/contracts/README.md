# Hợp đồng tích hợp — Nhóm ForkMe (Contract v1.0)

> Tài liệu chốt hợp đồng tích hợp giữa 4 module: `sim/gather` (`Do-Hong-Vy`), `sim/quan` (`Cuubeo`), `client/ui` (`Phog2811`), và `qa` (`Nguyenquoctoan0310`).
> **Quy tắc khóa:** Không tự ý sửa `docs/contracts/`, `game.contract.json` hoặc schema kho khi chưa báo cả nhóm. Khi đổi hợp đồng ở Phase 2–4, phải lập ADR trong [`docs/adr/`](../adr/0000-template.md).
> **Trạng thái đối chiếu PRD-0:** Các mục từ khung starter đã cố định theo mã nguồn; các payload/trường mở rộng chưa mở trên Lab Board được đánh dấu `[Đề xuất nhóm — chờ PO đối chiếu PRD-0]` tại [`docs/clarify.md`](../clarify.md).

---

## 1. Schema file kho (Contract G — `gather` → `quan`)

- **Định dạng JSON:** Object gốc chỉ có duy nhất một khóa `"items"`, ánh xạ từ `kind` sang số nguyên dương (`int > 0`; nguyên liệu có số lượng `0` bị lược bỏ; kho rỗng là `{"items":{}}`).
- **Danh sách `kind` hợp lệ (Phase 1):** `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung` (`KINDS_P1` trong [`chonoi/inventory.py`](../../chonoi/inventory.py)).
- **File mẫu hợp lệ:** [`inventory.sample.json`](inventory.sample.json)
  ```json
  {"items":{"bong_sung":2,"ca_loc":1}}
  ```
- **Quy tắc tích hợp (đã khóa trong `chonoi/inventory.py` & `chonoi/runner.py`):**
  - `gather` chỉ ghi file kho (`--inventory-out`) **đúng 1 lần** khi có sự kiện `gather_end` (`docked`, `time`, hoặc `fainted` → kho rỗng `{"items":{}}`); dừng do `--ticks` (`tick_limit`) thì giữ nguyên, không tạo/ghi đè file đích. Nội dung file khớp `data.inventory` của `gather_end`.
  - Ghi nguyên tử qua file tạm cùng thư mục rồi `os.replace`.
  - `quan` đọc kho qua `--inventory` hoặc `scenario.quan.stock` (truyền đồng thời cả hai → thoát mã `2`). Sai schema, có `kind` lạ hoặc số lượng âm → thoát mã `2` trước khi ghi output.

---

## 2. Giao diện giữa `sim/*` và `client/ui`

- Đặc tả đầy đủ các endpoint HTTP (`/state`, `/input`, `/restart`), trường snapshot chung, snapshot `gather`, snapshot `quan`, và ranh giới tính năng sáng tạo: xem [`sim-ui-interface.md`](sim-ui-interface.md).

---

## 3. Danh sách sự kiện (Contract E)

- Đặc tả đầy đủ tên sự kiện, payload `data`, điều kiện phát, bên nghe, và thứ tự xử lý trong `step()` cho cả `gather` và `quan`: xem [`events.md`](events.md).
