# Cuubeo — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm:** PO cả 4 phase — lưu PRD-0/Ticket-02..04, kế hoạch + AC, clarify #6–#22, ADR-0001/0002. Code: `sim/quan` P1 (`4ca8652`), quán 2 bếp/4 bàn/6 món + `day_plan` (`3268d1b`), `--mode day`/Shop/pause (`6b8f628`), độ tươi phía quán (`b6e11c0`), giúp Vỹ/Toàn bật v1.2 (`44605b2`, `cd08db2`, `a68c45d`, `6065631`), `soak_cmd` (`578d4b6`), `bench_cmd` + cảnh báo (`cd9e371`), sprite CC0 (`a08a9e7`, `6c52b9f`).
- **Tôi đã review:** `gather` P1 của Vỹ ([review](../proof/phase-1/review-gather-by-Cuubeo.md)); gộp L2 Cá Sấu của Toàn với v1.2 (`b4eb273`).
- **AI sai ở đâu, phát hiện thế nào:** agent push khi test đỏ — điều kiện kiểm `tail` thay vì kết quả test; phát hiện qua log `FAILED (95)` ngay sau push, sửa ở `6642956` và từ đó chỉ push khi suite xanh. AI cũng chọn nhầm sprite (cá nóc cho cá lóc) — phát hiện khi mở ảnh xem trước.
- **Điều tôi học được:** chốt hợp đồng/ADR trước khi code giúp 4 lát chạy song song; mọi lệnh push phải gắn với kết quả test thật.
