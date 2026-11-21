# Review chéo `sim/quan` (commit `4ca8652`, Cuubeo) — người review: Do-Hong-Vy

Đối chiếu [`chonoi/sim/quan.py`](../../../chonoi/sim/quan.py) với [`docs/prd0.md`](../../prd0.md) mục D, E, F và [`docs/contracts/`](../../contracts/README.md). Kết luận: **đạt, không cần sửa**.

| Điểm PRD-0 | Code trong `chonoi/sim/quan.py` | Kết quả |
|---|---|---|
| Thứ tự 5 bước mỗi tick: đồng hồ → bếp chín → di chuyển + tối đa 1 `interact` → trả tiền / rời bàn / `quan_end` → khách theo lịch | `step()` | Đạt |
| `ready_ticks` chỉ tăng cho món đã `ready` ở đầu bước; `burn_s: null` không cháy | `step()` bước 1–2 | Đạt |
| `interact` ưu tiên `(khoảng cách, bếp trước bàn, id_key)`, bỏ lượt nếu không tương tác được | `_interact()` | Đạt |
| Bếp `idle` nấu đơn `reserved` cũ nhất theo `(order_tick, id_key(table_id))`, trừ `stock`, chốt `base_price`, `cook_started` | `_start_cooking()` | Đạt |
| Phục vụ chốt `tip = floor(base_price * tip_rate)` theo tỷ lệ kiên nhẫn sau bước 1 `>= tip_min_patience_ratio` | `_serve()` | Đạt |
| Đóng ca `closing`: khách `eating` trả tiền ngay, khách `waiting` rời không trừ uy tín; khách rời bỏ món ở bếp/tay không hoàn nguyên liệu | `_pay()`, `_leave()` | Đạt |
| Khách mới theo lịch, bàn trống id nhỏ nhất, chọn đều qua `Streams("customers")` từ món đủ `stock - reserved`, cấp id bằng `IdAllocator("C")` | `_customer_due()`, `_spawn_customer()` | Đạt |
| Snapshot có `player: {pos, vel}` (`clarify #9`), `customers` chỉ liệt kê khách còn ngồi, sắp theo `sort_by_id` | `snapshot()` | Đạt |
| Số liệu đọc từ `tuning` (`game.contract.json`), không dùng `random` toàn cục / đồng hồ hệ thống | Rà toàn file | Đạt |

Kiểm chứng kèm theo:
- Bộ test `tests/test_quan_p1.py` (`14/14` OK) + toàn bộ test suite (`90/90` OK khi chạy `test_live.py` ngoài sandbox).
- Lưu ý đồng bộ đã ghi nhận ở [docs/verification/phase-1.md](../../verification/phase-1.md#L14): trường hợp hòa khoảng cách `"bếp trước bàn"` đã cài đúng ở `_interact()` (`0` cho stove, `1` cho table), chưa có test riêng do `B1`/`T1` mặc định cách xa.
