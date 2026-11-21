# Changelog — Quán Ăn Chợ Nổi (Nhóm ForkMe)

## [Phase 2 — In Progress] (Contract v1.1)
### Added
- **Quán v1.1 (`sim/quan`):** Mở rộng 2 bếp (`B1`, `B2`), 4 bàn (`T1`–`T4`), 6 nguyên liệu (`ca_keo`, `keo_neo`), 6 món ăn, `day_plan` D1–D5 và dữ liệu `shop` (`Cuubeo`).
- **UI/HUD v2.0 & Sáng tạo Đa Vũ Trụ (`chonoi/web/index.html` — `Phog2811`):**
  - Hoàn thiện Menu chính (`Chơi` / `Thoát` / Cài đặt âm thanh), màn hình `DayIntro`, `EveningIntro`, `DayResult`, `Shop` (mua nâng cấp Bình Oxy / Áo Phao, phím `1`/`2`/`Enter`), `Pause` (`Esc`/`P`) và `Summary` (thống kê món bán chạy).
  - Hỗ trợ đủ 6 nguyên liệu, 6 món ăn, 2 bếp, 4 bàn, 3 tầng độ sâu sông, hiển thị thủy quái (`monsters[]`) + cảnh báo viền tím `"THỦY QUÁI!"` và viền đỏ `"HẾT HƠI!"`, cỡ chữ HUD chính ≥ 18px ở 1280×720.
  - **Sáng tạo (tắt 100% ở headless, bật/tắt bằng phím `C`):** Đồ họa 2.5D Stylized + Particle VFX + Screen Shake + Web Audio API BGM/SFX (lưu cài đặt `Master/Music/SFX` trong `localStorage`) + Chế độ **A-Qua-Mèn (dưới sông) × Gô-Ku SSJ3 & Z-Warriors (trên nhà bè)** với hiệu ứng đấu chưởng Kamehame-Lẩu.
- **Tài liệu:** Cập nhật mục `"Sáng tạo của nhóm"` trong `README.md`, `CREDITS.md`, `docs/retro.md` (Phase 2 nhanh), `docs/standup.md`, `docs/ai-usage-log.md`.

## [Phase 1] (Contract v1.0)
### Added
- Hoàn thiện lõi buổi sáng `GatherSim` (`chonoi/sim/gather.py` — `Do-Hong-Vy`): bơi + ramp, `dive`/`surface`, oxy/ngạt/ngất LIFO, hái nút & mọc lại, bắt cá & hồi chiêu, cập bến & xuất kho.
- Hoàn thiện lõi buổi tối `QuanSim` (`chonoi/sim/quan.py` — `Cuubeo`): lịch khách, giữ chỗ nguyên liệu, nấu/bưng/phục vụ, tiền + boa + uy tín, đóng ca.
- Hoàn thiện kiểm chứng mức luật `scenario.py`, `contract.py` và 90/90 bài test tự động + bằng chứng `docs/proof/phase-1/` (`Nguyenquoctoan0310`).
- Nâng cấp UI/HUD v1.0 (`chonoi/web/index.html` — `Phog2811`): đồ họa sông Chín Khúc & nhà bè Má Tư, sửa hiển thị object `stoves[].dish` / `hand`, kho khả dụng (`stock - reserved`), sổ tay thực đơn và màn hình tổng kết.
- Thiết lập Harness AI: `TEAM.md`, `AGENTS.md`, 2 custom skills (`check-contract`, `verify-phase`) và hợp đồng `docs/contracts/`.
