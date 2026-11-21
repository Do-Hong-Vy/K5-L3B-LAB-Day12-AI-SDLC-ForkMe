# Quán Ăn Chợ Nổi v1.0.0 — Nhóm ForkMe

Út Sen lặn sông Chín Khúc bắt cá, hái rau buổi sáng; tối mở quán trên nhà bè Má Tư; cuối ngày mua nâng cấp ở Shop. Chơi trọn 5 Ngày theo kế hoạch của Má Tư.

## Điểm mới
- **Vòng ngày đầy đủ** (`--mode day`, 1–5 Ngày): gather -> quán -> Shop, tiền/uy tín/nâng cấp giữ qua Ngày.
- **Độ tươi (v1.2):** mỗi nguyên liệu là một cá thể có id và độ tươi; hàng ươn không nấu được; giá món theo độ tươi.
- **Sông sống động:** 8 đàn cá bơi và sinh thêm, Cá Sấu Năm Chèo tuần tra/rượt đuổi; quán 2 bếp, 4 bàn, 6 món.
- **Cảnh báo dễ nhận biết + tương phản cao** (phím `T`); nhân vật người và cá bằng sprite CC0 (Kenney).
- **Benchmark** (`bench_cmd`) và **soak** 10 Ngày (`soak_cmd`).

## Cách chạy (Python 3.10+, chỉ thư viện chuẩn; macOS / Linux)
```bash
git clone https://github.com/Do-Hong-Vy/K5-L3B-LAB-Day12-AI-SDLC-ForkMe.git && cd K5-L3B-LAB-Day12-AI-SDLC-ForkMe
PYTHONPATH=tests:. python3 -m unittest discover -s tests      # toàn bộ test
python3 -m chonoi.live --mode day --days 5                     # chơi trên trình duyệt, mở địa chỉ in ra
```
Bản đóng gói đính kèm (`chonoi-forkme-v1.0.0.zip`) là mã nguồn tại tag `v1.0.0`; giải nén rồi chạy 2 lệnh cuối.

Điều khiển: `WASD`/mũi tên di chuyển · `E` tương tác · `Space` bắt cá · `Esc`/`P` tạm dừng · `T` tương phản cao · `C` chế độ Sáng tạo · `R` chơi lại.

## Giới hạn đã biết
- Benchmark đo render phần mềm của bản Python (framebuffer 1280×720), không đo canvas trình duyệt.
- Mở rộng chưa làm: dòng nước lũ, khách đặt trước, Lao xua, vợt hút cá, Rắn Hổ Mây, cháy món, Chợ Chú Sáu, Sổ tay, leaderboard, phụ đề SFX.
- Trên Windows cần `PYTHONUTF8=1` khi chạy test (xem AGENTS.md).
- Tag `phase-2..4` và Release được gắn sau mốc giờ của lab (ghi trong retro).
