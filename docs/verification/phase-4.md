# Ma trận truy vết Phase 4 (Ticket-04 "Phát hành v1.0.0", Test Contract v1.3)

> AC theo [`docs/plan/phase-4.md`](../plan/phase-4.md). Bằng chứng ở [`docs/proof/phase-4/`](../proof/phase-4/).
> Regression đầy đủ trên commit bàn giao: [regression-tests.log](../proof/phase-4/regression-tests.log).

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P4-01 `bench_cmd --seed 42 --duration 30 --out bench.json`, 5 trường đúng công thức | `python3 -m chonoi.bench --seed 42 --duration 30`; `tests/test_bench_p4.py` (cấu trúc, avg = frames/measured_s, p1_low ≤ avg) | [bench.json](../proof/phase-4/bench.json): avg 545.3 FPS, 1% low 232.5 FPS, 16 360 khung / 30.0 s, load 41 ms | Đạt — **giới hạn:** render phần mềm 1280×720 của bản Python, không đo canvas trình duyệt |
| AC-P4-02 `soak_cmd --seed 7 --days 10 --out soak.json`, `days_completed = days`, `crashes = 0`, tất định | `tests/test_soak_p4.py` (10 Ngày, 2 lần giống nhau bỏ `duration_s`) | [soak.json](../proof/phase-4/soak.json): 10/10 Ngày, 0 crash, ~6.6 s | Đạt |
| AC-P4-03 cảnh báo chữ/biểu tượng: thủy quái gần, oxy sắp hết, khách sắp giận; chế độ tương phản cao | `index.html::currentAlerts/drawAlerts` (🐊 / 🫧 < 25% / 😠 < 25%), phím `T` + nút ◐ (lưu localStorage) | kiểm tay trên `chonoi.live` ở cả hai chế độ | Đạt (kiểm tay) |
| AC-P4-04 clone sạch ≤ 3 lệnh, README đủ môi trường / điều khiển / lệnh test, headless, bench | Clone repo vào thư mục trống, chạy test + day headless | [clean-clone.log](../proof/phase-4/clean-clone.log) (269 OK, day exit 0) | Đạt |
| AC-P4-05 Release v1.0.0 + bản đóng gói + release notes; CHANGELOG theo phase; CREDITS/LICENSE | [release notes](../release-notes-v1.0.0.md), [CHANGELOG](../../CHANGELOG.md), [CREDITS](../../CREDITS.md), [LICENSE](../../LICENSE), [docs/contracts/](../contracts/README.md) | Tag `phase-1..4` + `v1.0.0`, đóng gói `chonoi-forkme-v1.0.0.zip` | Đã gắn tag `phase-1..4`, `v1.0.0`, dọn `kho.json` và đồng bộ hợp đồng v1.3 (GitHub Release đính kèm zip công bố qua `gh`/GitHub) |
| AC-P4-06 regression P1–P3 còn hiệu lực | toàn bộ `tests/` (P1, P2, P3, P4) + `python3 tools/check_team.py` | [regression-tests.log](../proof/phase-4/regression-tests.log) | Đạt |
| AC-P4-07 retro rà hành động P2, một lỗi AI + cách xác minh; phản tư đủ người | [retro](../retro.md) mục Phase 4; [`docs/members/`](../members/) | `Cuubeo.md`, `Do-Hong-Vy.md` đã hoàn tất (`<= 200` từ); `Phog2811.md`, `Nguyenquoctoan0310.md` còn bản nháp chờ chính chủ | Đạt phần retro & phản tư của `Cuubeo` + `Do-Hong-Vy`; còn 2 file thành viên giữ nguyên trạng bản nháp |

## Đánh giá ngắn
- Mở rộng Phase 4 (leaderboard, phụ đề SFX): **không làm**.
- Ghi trung thực: các tag `phase-2..4` và Release gắn sau mốc giờ của lab.
