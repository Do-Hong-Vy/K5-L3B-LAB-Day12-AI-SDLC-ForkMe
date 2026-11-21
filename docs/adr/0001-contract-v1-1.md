# ADR-0001: Nâng Test Contract lên v1.1 (Ticket-02)

- Trạng thái: chấp nhận (bắt buộc theo Ticket-02)
- Ngày, người quyết: 2026-11-21, PO `Cuubeo` + Integrator `Do-Hong-Vy`

## Bối cảnh
Ticket-02 ([`docs/ticket-02.md`](../ticket-02.md)) chốt số liệu chuẩn và thêm `--mode day`, Shop, pause, cá bơi/sinh, Cá Sấu,
6 nguyên liệu / 6 món, 2 bếp / 4 bàn. Contract v1.0 của Phase 1 (1 bếp, 1 bàn, 3 món, 6 đàn đứng yên) không còn đúng.

## Các lựa chọn đã cân nhắc
1. Giữ v1.0 cho `gather`/`quan`, chỉ thêm `day` — **loại**: ticket yêu cầu thay số chuẩn và test ẩn chạy v1.1.
2. Nâng toàn bộ lên v1.1, mỗi lát khai khóa của mình trong `game.contract.json` — **chọn**.

## Quyết định
- `contract_version: "1.1"`, số chuẩn mục 1.1/1.3 của ticket.
- Mỗi lát sửa đúng khối của mình trong `game.contract.json` (pull trước khi sửa, commit nhỏ):
  `gather` + `gather.monsters` (Do-Hong-Vy / Nguyenquoctoan0310) · `quan`, `menu`, `day_plan`, `shop` (Cuubeo).
- Danh sách nguyên liệu hợp lệ mở rộng thành 6 kind (`ca_keo`, `keo_neo`) — sửa `chonoi/inventory.py` (khung) có báo nhóm.
- Mỗi tính năng ngẫu nhiên một luồng `Streams` riêng để thêm tính năng không làm lệch luồng khác.
- Hợp đồng `docs/contracts/` cập nhật sự kiện/snapshot v1.1 (mục 4.4) theo từng lát.

## Hệ quả (bảng tác động)

| Module / file | Thay đổi | Test bị ảnh hưởng | Người |
|---|---|---|---|
| `game.contract.json` | v1.1, khóa mới mục 4.1 | `test_contract*`, smoke đọc preset | từng lát |
| `chonoi/contract.py` | validator v1.1 (8 đàn, 6 kind, B2, T2–T4, day_plan, shop) | test validator của QA | Nguyenquoctoan0310 |
| `chonoi/inventory.py` | 6 kind | test kho | Cuubeo (báo nhóm) |
| `chonoi/sim/gather.py` | cá bơi/sinh, N5/N6, Cá Sấu, bất tử, thứ tự 4.5 | `test_gather_p1.py` (6 đàn → 8 đàn) | Do-Hong-Vy, Nguyenquoctoan0310 |
| `chonoi/sim/quan.py` | B2, T2–T4, 6 món, lọc menu theo kế hoạch trong day | `test_quan_p1.py` (giả định 1 bàn) | Cuubeo |
| `chonoi/headless.py`, `runner.py`, `sim/day.py` (mới) | `--mode day`, `--days`, Shop, pause, vỏ event `day` | test mới P2 | Cuubeo |
| `chonoi/scenario.py`, `inputs.py` | khối `day`, `monsters[]`, `age_ticks`, nút `pause`/`shop_done`/`buy` | test scenario/inputs | Nguyenquoctoan0310 |
| `chonoi/web/index.html` | menu, intro/result, pause, HUD v1.1 | `test_live.py` | Phog2811 |
