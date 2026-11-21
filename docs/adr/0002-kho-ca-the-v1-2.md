# ADR-0002: Kho cá thể và độ tươi (Test Contract v1.2, Ticket-03)

- Trạng thái: chấp nhận (Change Request bắt buộc)
- Ngày, người quyết: 2026-11-21, PO `Cuubeo` + Integrator `Do-Hong-Vy`

## Bối cảnh
Ticket-03 thay kho đếm `{"items":{kind:n}}` bằng kho cá thể `{"items":[{id,kind,fresh}]}`, thêm hao tươi, hàng ươn,
giữ chỗ theo id và giá theo độ tươi. Đây là **breaking change** của hợp đồng tích hợp gather → quan (PRD-0 mục G).

## Các lựa chọn đã cân nhắc
1. Đổi thẳng sang v1.2 trong một commit lớn — **loại**: nhiều lát sửa cùng lúc, `main` dễ đỏ.
2. Adapter đọc/ghi cả hai schema theo `contract_version`, bật v1.2 khi gather + quán đều sẵn sàng — **chọn** (ticket gợi ý).

## Quyết định
- Độ tươi lưu nội bộ bằng **số nguyên đơn vị**: 240 đơn vị = 1 điểm tươi (fresh 100 = 24 000). Gather −2 đơn vị/tick (0.5/s),
  quán −1 đơn vị/tick (0.25/s). Ngưỡng ươn so `units < 30 × 240` → không sai số thực. Xuất `fresh = units / 240`.
- Id cá thể `I<n>` cấp bằng `IdAllocator` họ `I`, tiếp tục xuyên pha và Ngày (khác id khách — clarify #14).
- `customers[].reserved` đổi từ map kind → số sang **mảng id**; `cook_started.items`, `faint.lost`, `monster_hit.lost` là mảng cá thể.
- `contract_version` quyết định schema đọc: `"1.2"` → chỉ nhận kho cá thể, kho đếm → mã 2.

## Hệ quả (bảng tác động)

| Module | File cần đổi | Test bị ảnh hưởng | Người |
|---|---|---|---|
| Adapter | `chonoi/inventory.py`, `chonoi/contract.py` | `test_smoke_p1` (kho đếm), test kho | Nguyenquoctoan0310 |
| Lặn | `chonoi/sim/gather.py` | `test_gather_p1` (hold là mảng kind) | Do-Hong-Vy |
| Quán | `chonoi/sim/quan.py` | `test_quan_p1`, `test_quan_p2` (stock map, reserved map) — đổi fixture, ghi lý do | Cuubeo |
| day | `chonoi/sim/day.py` | test day | Cuubeo |
| Scenario | `chonoi/scenario.py` | `test_scenario_quan_p1` | Nguyenquoctoan0310 |
| HUD | `chonoi/web/index.html` | `test_live` | Phog2811 |
