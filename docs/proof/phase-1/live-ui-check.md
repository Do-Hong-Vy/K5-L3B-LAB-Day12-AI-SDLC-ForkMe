# Kiểm chứng giao diện trực tiếp (`chonoi.live` — `AC-P1-14`)

Kiểm tra trực tiếp bằng trình duyệt Chrome đối với cả hai chế độ của [`chonoi.live`](../../../chonoi/live.py) & [`chonoi/web/index.html`](../../../chonoi/web/index.html):

1. **Chế độ `gather` (`http://127.0.0.1:8001/`, seed 42):**
   - Tải `<canvas>` thành công, `GET /` và `GET /state` trả `200 OK`, **0 lỗi JavaScript / Page Error**, không cảnh báo mất kết nối hay lỗi sim.
   - Đã thử phím `R` (reset), `D` + `S` (bơi phải và lặn xuống `d = 1.5m`): tọa độ chuyển từ `x=2.0m, d=0.0m` sang `x=3.6m, d=1.5m`, `OXY` giảm từ `30s/30s` xuống `12s/30s`, log ghi `t158 Lặn xuống nước (d=0.5m)`.
   - HUD hiển thị đủ: đồng hồ, thanh `OXY`, `MÁU: ♥ ♥ ♥`, tọa độ, hồi chiêu vợt bắt cá, giỏ lưới LIFO `0/12`, nút hái `N1..N4`, 6 đàn cá `F1..F6`, bến (`E`), sổ tay thực đơn 3 món (`[H]`).
   - Ảnh chụp: [`ui-gather-live.png`](ui-gather-live.png).

2. **Chế độ `quan` (`http://127.0.0.1:8002/`, `--inventory docs/contracts/inventory.sample.json`, seed 42):**
   - Tải `<canvas>` thành công, `GET /` và `GET /state` trả `200 OK`, **0 lỗi JavaScript / Page Error**.
   - Sau `R` và chờ `first_customer_tick = 120`, khách `C1` xuất hiện tại `BÀN T1` (`t120 Khách C1 vào bàn T1 gọi Cá lóc nướng trui`). Đã thử phím `A`/`W` di chuyển gần `BẾP B1`.
   - HUD hiển thị đủ: đồng hồ, `Tiền`, `Tổng thu`, `Uy tín: 3.0 / 5.0`, `ĐIỂM (SCORE): 300`, món trên tay, `BẾP B1`, `BÀN T1`, thẻ đơn `C1`, thanh kiên nhẫn kèm mốc boa `50%`, `KHO KHẢ DỤNG (Tồn - Giữ chỗ)`, sổ tay thực đơn & nhật ký sự kiện.
   - Ảnh chụp: [`ui-quan-live.png`](ui-quan-live.png).

3. **Unit test server live (`tests/test_live.py`):** `1/1 OK`.
