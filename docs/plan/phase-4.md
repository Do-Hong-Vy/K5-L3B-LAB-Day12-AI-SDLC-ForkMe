# Kế hoạch Phase 4 (≤ 1 trang)

> PO: Cuubeo. Nguồn: [`docs/ticket-04.md`](../ticket-04.md) (Test Contract v1.3). Phát hành v1.0.0.

- **Mục tiêu:** `bench_cmd`, `soak_cmd` khai ở gốc manifest (`contract_version:"1.3"`); 3 cảnh báo dễ nhận biết + tương phản cao; chạy từ clone sạch ≤ 3 lệnh; Release v1.0.0 + release notes; retro + phản tư đủ 4 người; tag `phase-4` + Release cùng commit trước **3:00**.

| AC | Nội dung (Ticket-04) | Vai / người |
|---|---|---|
| AC-P4-01 | `bench_cmd --seed 42 --duration 30 --out bench.json` → 5 trường `avg_fps,p1_low_fps,frames,measured_s,load_ms`; artifact ở `docs/proof/phase-4/` | Bench/QA Nguyenquoctoan0310 |
| AC-P4-02 | `soak_cmd --seed 7 --days 10 --out soak.json` → `days,days_completed,crashes,results[],duration_s`; D1–D5 lặp ở 6–10; đạt khi `days_completed = days`, `crashes = 0` | Cuubeo (dựa trên `--mode day`) |
| AC-P4-03 | Cảnh báo bằng chữ/biểu tượng: thủy quái gần, oxy sắp hết, khách sắp giận; chế độ tương phản cao | Phog2811 |
| AC-P4-04 | README: yêu cầu môi trường, ≤ 3 lệnh từ clone sạch, điều khiển, lệnh test/headless/bench | Đóng gói Phog2811 + Do-Hong-Vy |
| AC-P4-05 | Release v1.0.0 có bản đóng gói, release notes; CHANGELOG theo phase; rà CREDITS/LICENSE | Release/Integrator Do-Hong-Vy |
| AC-P4-06 | Regression P1–P3 còn hiệu lực; `docs/verification/phase-4.md` khớp commit tag | Nguyenquoctoan0310 |
| AC-P4-07 | Retro rà hành động P2, một lỗi AI + cách xác minh; `docs/members/<handle>.md` đủ 4 người | Điều phối retro Phog2811 + cả nhóm |

- **Phụ thuộc:** AC-P4-02 cần `--mode day` (lát 4 Phase 2) chạy nhiều Ngày.
- **Rủi ro:** tính năng P2/P3 chưa xong → ưu tiên tag + Release đúng giờ, ghi trung thực phần chưa đạt trong verification.
