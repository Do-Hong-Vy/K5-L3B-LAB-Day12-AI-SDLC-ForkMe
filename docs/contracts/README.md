# Hợp đồng tích hợp — Nhóm ForkMe (Contract v1.3, gameplay v1.2)

> Tài liệu chốt hợp đồng tích hợp giữa 4 module: `sim/gather` (`Do-Hong-Vy`), `sim/quan` (`Cuubeo`), `client/ui` (`Phog2811`), và `qa` (`Nguyenquoctoan0310`).
> **Quy tắc khóa:** Không tự ý sửa `docs/contracts/`, `game.contract.json` hoặc schema kho khi chưa báo cả nhóm và lập ADR trong [`docs/adr/`](../adr/0000-template.md) (v1.1: [ADR-0001](../adr/0001-contract-v1-1.md), v1.2: [ADR-0002](../adr/0002-kho-ca-the-v1-2.md)).

---

## 1. Schema file kho (`gather` → `quan`)

- **Định dạng JSON v1.2/v1.3 (từ Phase 3 — Ticket-03):**
  - Object gốc chỉ có duy nhất một khóa `"items"`, là **mảng cá thể** `[{"id": str, "kind": str, "fresh": float}]` sắp theo `id_key(id)` (`I1, I2, ...` nối tiếp xuyên pha và Ngày); kho rỗng là `{"items":[]}`.
  - `id` duy nhất khác rỗng, `fresh` hữu hạn trong `[0, 100]` (ngưỡng ươn `< 30`). Với `contract_version >= 1.2`, truyền kho đếm cũ (`{kind: int}`) bị từ chối với mã `2`.
  - *(Lịch sử v1.0/v1.1: kho đếm `{"items": {kind: int > 0}}` vẫn được `chonoi/inventory.py` giữ qua nhánh tương thích theo `contract_version`.)*
- **Danh sách 6 `kind` hợp lệ (v1.1+):** `ca_loc`, `ca_linh`, `ca_keo`, `bong_dien_dien`, `bong_sung`, `keo_neo` (`KINDS` trong [`chonoi/inventory.py`](../../chonoi/inventory.py)).
- **File mẫu hợp lệ (v1.2+):** [`inventory.sample.json`](inventory.sample.json)
  ```json
  {"items":[{"id":"I1","kind":"ca_loc","fresh":100},{"id":"I2","kind":"bong_sung","fresh":97.5}]}
  ```
- **Quy tắc tích hợp (`chonoi/inventory.py`, `chonoi/runner.py`, `chonoi/sim/day.py`):**
  - `gather --inventory-out` ghi **đúng 1 lần** khi có `gather_end` (`docked`, `time`, hoặc `fainted` → `{"items":[]}`); chạm `--ticks` trước khi kết thúc thì không ghi file đích. Nội dung khớp `gather_end.data.inventory`.
  - Ghi nguyên tử qua file tạm cùng thư mục rồi `os.replace`. Trong `--mode day`, kho bàn giao trong bộ nhớ cùng tick đổi pha mà không hao thêm độ tươi.
  - `quan` đọc kho qua `--inventory` hoặc `scenario.quan.stock` (truyền đồng thời cả hai hoặc giữ chỗ quá tồn → thoát mã `2` trước khi ghi output).

---

## 2. Giao diện giữa `sim/*`, `day` và `client/ui`

- Đặc tả đầy đủ các endpoint HTTP (`/state`, `/input`, `/restart`), snapshot chung, `gather`, `quan`, `shop`, `bench_cmd`/`soak_cmd`, và ranh giới sáng tạo + asset CC0: xem [`sim-ui-interface.md`](sim-ui-interface.md).

---

## 3. Danh sách sự kiện (Contract E)

- Đặc tả đầy đủ tên sự kiện, payload `data`, điều kiện phát, và thứ tự xử lý trong `step()` cho `gather`, `quan`, `day`, `shop`, `pause` và độ tươi v1.2: xem [`events.md`](events.md).
