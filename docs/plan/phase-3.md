# Kế hoạch Phase 3 (≤ 1 trang)

> PO: Cuubeo. Nguồn: [`docs/ticket-03.md`](../ticket-03.md) (Change Request "Mùa Nước Nổi", Test Contract v1.2). Quyết định đổi schema: [`docs/adr/0002-kho-ca-the-v1-2.md`](../adr/0002-kho-ca-the-v1-2.md).

- **Mục tiêu:** kho đếm → kho cá thể `{id,kind,fresh}`; hao tươi giỏ 0.5/s, kho quán 0.25/s; ươn < 30 + `spoiled`; giữ chỗ theo id; giá theo tươi; contract v1.2 (`freshness`); file kho đếm → mã 2; tag `phase-3` trước **2:30**.

- **AC Phase 3:**

| AC | Nội dung (Ticket-03) | Người |
|---|---|---|
| AC-P3-01 | Schema kho cá thể: đọc/ghi `{"items":[{id,kind,fresh}]}`, chọn schema theo `contract_version`; v1.2 từ chối kho đếm, kind lạ, id trùng, fresh ngoài [0,100] → mã 2; ghi nguyên tử, xuất theo id, đủ chính xác ở ngưỡng 30 | Nguyenquoctoan0310 (adapter) |
| AC-P3-02 | Gather: cá thể mới fresh 100, cấp id I1, I2… theo thứ tự vào giỏ (xuyên pha/Ngày), hao 0.5/s từ bước sau; `spoiled` (location hold) đúng một lần; LIFO khi mất hàng; `gather_end.inventory` cùng schema | Do-Hong-Vy |
| AC-P3-03 | Quán: kho cá thể, hao 0.25/s kể cả hàng giữ; `spoiled` (location stock) theo id trước khi xử lý giữ chỗ | Cuubeo |
| AC-P3-04 | Giữ chỗ theo id: tươi nhất, hòa theo id; giữ có cá thể vừa ươn → nhả và thử giữ lại một lần (order_tick, id bàn); thiếu → `unfulfillable` | Cuubeo |
| AC-P3-05 | Giá theo tươi: `base_price = floor(giá × trung bình fresh / 100)` lúc `cook_started`; `items` là mảng cá thể sắp kind rồi id; boa tính trên giá đã chốt | Cuubeo |
| AC-P3-06 | Scenario v1.2: `gather.hold`, `quan.stock` là mảng cá thể, `customers[].reserved` là mảng id; mâu thuẫn → mã 2 | Nguyenquoctoan0310 |
| AC-P3-07 | Bàn giao trong `day`: cùng tick chuyển pha, không hao thêm; snapshot `hold`/`stock`/`reserved` theo schema mới | Cuubeo (day) + Do-Hong-Vy |
| AC-P3-08 | HUD hiện độ tươi / hàng ươn | Phog2811 |
| AC-P3-09 | Smoke ngưỡng (fresh 30 → `spoiled` tick 1) + smoke bàn giao file; regression P1–P2; CHANGELOG breaking change; verification phase-3; tag `phase-3` | Nguyenquoctoan0310 (tag: Do-Hong-Vy) |

- **Thứ tự tích hợp (giữ `main` chạy được):** (1) adapter đọc/ghi hai schema theo `contract_version`, mặc định vẫn v1.1 → (2) gather + quán làm song song trên mảng cá thể → (3) bật `contract_version:"1.2"` + `freshness` khi cả hai đầu đã xanh → (4) smoke file + day, regression, tag.

- **Rủi ro:** sai số thực ở ngưỡng 30 → lưu độ tươi bằng số nguyên "đơn vị" (240 đơn vị/điểm: gather −2/tick, quán −1/tick) như ticket gợi ý; test P1/P2 dùng kho đếm phải đổi fixture (ghi lý do).
