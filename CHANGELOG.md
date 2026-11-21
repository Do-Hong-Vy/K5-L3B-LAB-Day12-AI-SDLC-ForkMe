# Changelog — Quán Ăn Chợ Nổi (Nhóm ForkMe)

## [1.0.0] — Phase 4 (Test Contract v1.3)
### Added
- `bench_cmd` (`python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`): cảnh sáng lõi, render phần mềm 1280×720, làm nóng 3 s; 5 trường `avg_fps, p1_low_fps, frames, measured_s, load_ms` (`Cuubeo`).
- `soak_cmd` (`python3 -m chonoi.soak --seed 7 --days 10 --out soak.json`): N Ngày một tiến trình, bot tất định, đếm crash; D1–D5 lặp ở Ngày 6+ (`Cuubeo`).
- Cảnh báo chữ + biểu tượng: 🐊 thủy quái gần, 🫧 oxy sắp hết, 😠 khách sắp giận; **chế độ tương phản cao** (phím `T` / nút ◐).
- Sprite CC0 Kenney: *Fish Pack 2.0* (cá linh/lóc/kèo, rong, đá, bong bóng) và *Toon Characters 1* (Út Sen + 3 dáng khách) — xem [CREDITS.md](CREDITS.md).
- Release notes, LICENSE (thông báo giấy phép), kịch bản demo.
### Changed
- `contract_version: "1.3"`; khai `bench_cmd`, `soak_cmd` ở gốc manifest. Gameplay/tuning/kho/JSONL giữ v1.2.
- `fish_initial` là **số 8** (clarify #22): đầu ca sinh 8 đàn ở 8 điểm khác nhau theo luật sinh cá.
### Removed
- Nhân vật parody từ thương hiệu khác trong chế độ Sáng tạo (vi phạm quy định asset/nhân vật của lab) — thay bằng Cá Sấu Năm Chèo và "Khách quen".

## [Phase 3] (Test Contract v1.2) — **BREAKING CHANGE: kho cá thể**
### Breaking
- File kho đổi từ kho đếm `{"items": {kind: n}}` sang **kho cá thể** `{"items": [{"id", "kind", "fresh"}]}`. Với `contract_version >= 1.2`, file kho đếm, kind lạ, id trùng, `fresh` ngoài [0, 100] -> **mã 2**.
- `gather.hold`, `quan.stock` trong scenario là **mảng cá thể**; `customers[].reserved` là **mảng id**; `cook_started.items`, `faint.lost`, `monster_hit.lost` là mảng cá thể.
- **Cập nhật fixture:** dùng `tests/helpers.py` — `stock({kind: n})`, `hold([kind, ...])` sinh cá thể fresh 100 (id `S1..`/`I1..`); `kinds(...)`, `counts(...)` để so theo loại. Độ tươi trong JSONL làm tròn 3 số -> so với file kho theo dung sai ±0.01.
### Added
- Độ tươi: giỏ hao 0.5/s, kho quán 0.25/s (kể cả hàng giữ), `spoiled` (hold/stock) đúng một lần theo id; độ tươi lưu số nguyên 240 đơn vị/điểm (ADR-0002) để ngưỡng 30 và `floor` chính xác.
- Giữ chỗ theo id (tươi nhất, hòa id), nhả và giữ lại một lần khi hàng vừa ươn, `unfulfillable` khi thiếu; giá theo tươi `floor(giá × trung bình fresh / 100)`.
- Id cá thể `I<n>` nối tiếp xuyên pha và Ngày trong `day`.
- HUD giỏ: vạch độ tươi, ⚠ hàng ươn.
- Validator contract nhận 1.2 + `freshness`; scenario nhận `gather.monsters[]` (ví dụ ticket dùng `monsters: []`).

## [Phase 2] (Test Contract v1.1)
### Added
- Số chuẩn Ticket-02: cá bơi/đổi hướng/phản xạ mép, sinh cá mỗi 360 tick theo trọng số, N5/N6 kèo nèo (`Do-Hong-Vy`).
- Cá Sấu Năm Chèo: patrol/chase/recoil, hit −1 Máu, rơi floor(n/2) LIFO, bất tử 90, M2 từ Ngày 3; validator v1.1, scenario/inputs v1.1 (`Nguyenquoctoan0310`).
- Quán 2 bếp / 4 bàn / 6 món / 6 nguyên liệu, `day_plan` D1–D5, dữ liệu `shop`; khách chỉ gọi món trong kế hoạch Ngày (`Cuubeo`).
- `--mode day --days 1..5`: gather -> quan -> Shop, kho bàn giao trong bộ nhớ, nâng cấp oxygen/hp có hiệu lực từ Ngày kế, `days_completed`; pause cả 3 mode (`Cuubeo`).
- UI v2.0: Menu, DayIntro/EveningIntro/DayResult/Shop/Pause/Summary, HUD v1.1, VFX 2.5D, Web Audio (`Phog2811`).
- Sáng tạo: bếp nhiều section — sơ chế từng nguyên liệu rồi gộp thành món (chỉ `chonoi.live`) (`Cuubeo`).
### Changed
- Test P1 cập nhật theo số chuẩn (1 -> 4 bàn, 6 -> 8 đàn cá; `test_con_03` cho phép `day`) — lý do ghi trong từng commit.
### Fixed
- Merge `9612d91` làm mất `KINDS` trong `inventory.py` (main đỏ toàn bộ) -> khôi phục ở `6642956`.

## [Phase 1] (Contract v1.0)
### Added
- Lõi buổi sáng `GatherSim` (`Do-Hong-Vy`): bơi + ramp, `dive`/`surface`, oxy/ngạt/ngất LIFO, hái nút & mọc lại, bắt cá & hồi chiêu, cập bến & xuất kho.
- Lõi buổi tối `QuanSim` (`Cuubeo`): lịch khách, giữ chỗ, nấu/bưng/phục vụ, tiền + boa + uy tín, đóng ca, `quan.player.vel`.
- Kiểm mâu thuẫn `scenario.py`, `contract.py`, test tự động + bằng chứng `docs/proof/phase-1/` (`Nguyenquoctoan0310`).
- UI/HUD v1.0 (`Phog2811`).
- Harness AI: `TEAM.md`, `AGENTS.md`, skill `check-contract`, `verify-phase`; hợp đồng `docs/contracts/`; PRD-0 + kế hoạch/clarify (`Cuubeo`).
