# Kế hoạch Phase 1 (≤ 1 trang)

> PO: Cuubeo. Lập ở CP0 khi PRD-0 chưa mở trên Lab Board — AC chính thức sẽ trích vào đây khi tab Phase 1 mở (`docs/clarify.md` #6).

- **Mục tiêu:** Lõi `gather` (oxy, ngạt, Máu, ngất, hái nút, bắt cá, giỏ LIFO, cập bến) + lõi `quan` (khách, giữ chỗ, bếp, bưng, phục vụ, tiền, boa, uy tín) + kho v1.0 nối `gather → quan`; headless tất định, test xanh; tag `phase-1` trước **1:00**.

- **Việc / người / phụ thuộc:**

| # | Việc | Người | Phụ thuộc | Mốc |
|---|---|---|---|---|
| 1 | Chốt TEAM.md, contract `team`, hợp đồng tích hợp, 2 skill | Cả nhóm | — | 0:15 |
| 2 | `gather` lát 1: dive/surface, oxy, choke, faint | Do-Hong-Vy | #1 (events.md) | 0:30 |
| 3 | `gather` lát 2: hái nút, bắt cá, hold_full, kho | Do-Hong-Vy | #2 | 0:45 |
| 4 | `quan` lát 3: khách theo lịch, chọn món, giữ chỗ, kiên nhẫn, customer_left, no_dish | Cuubeo | #1 | 0:35 |
| 5 | `quan` lát 4: interact bếp/bàn, cook/ready/picked/served, paid, tip, uy tín | Cuubeo | #4 | 0:50 |
| 6 | HUD đọc snapshot gather + quan (oxy, Máu, giỏ, bếp, khách) | Phog2811 | #1 (sim-ui-interface.md) | 0:50 |
| 7 | Kiểm mâu thuẫn scenario (mã 2), unit + smoke + determinism test, verification + proof | Nguyenquoctoan0310 | #2–#5 | 0:55 |
| 8 | Tích hợp trên `main`, chạy test, gắn tag `phase-1` | Do-Hong-Vy | #7 | 1:00 |

- **Rủi ro:**
  - PRD-0 mở muộn / khác giả định → làm theo TODO trong khung trước, PO cập nhật ngay khi có AC.
  - Lệch payload sự kiện giữa sim và UI/test → chỉ dùng `docs/contracts/events.md`, đổi phải báo Integrator.
  - Mất tất định (dùng `random`/clock, không sắp id) → mọi ngẫu nhiên qua `Streams`, QA chạy 2 lần cùng seed so byte (skill QA của Nguyenquoctoan0310).
  - Windows `python3`/encoding → `PYTHONUTF8=1`; không đổi `headless_cmd`.
  - Xung đột git ở `game.contract.json` → chỉ Integrator sửa contract.
