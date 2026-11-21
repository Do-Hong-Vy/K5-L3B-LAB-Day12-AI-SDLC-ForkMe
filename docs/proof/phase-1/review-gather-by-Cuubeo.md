# Review chéo `sim/gather` (commit `f801a39`, Do-Hong-Vy) — người review: Cuubeo

Đối chiếu `chonoi/sim/gather.py` với PRD-0 mục F (Gather) + E. Kết luận: **đạt, không cần sửa**.

| Điểm PRD-0 | Code | Kết quả |
|---|---|---|
| Thứ tự bước: đồng hồ/hồi → bơi + dive/surface → oxy theo d cuối bước → interact (bến trước) → catch → hết giờ | `step()` | Đạt |
| Mặt nước +`oxygen_refill_per_tick`, kẹp max, reset ngạt; dưới nước −1, `oxygen_empty` khi từ dương về 0 | `_update_oxygen_and_choke` | Đạt |
| Đếm ngạt gồm cả bước vừa chạm 0 → ngạt lần đầu ở t+59; nổi lên đúng bước đó thì không ngạt | đếm `zero_oxy_ticks` sau khi trừ oxy | Đạt |
| Máu 0: `lost` theo LIFO, `faint` rồi `gather_end` fainted, kho rỗng, dừng bước | `lost = reversed(hold)`, `return True` | Đạt |
| Hái chỉ ở mặt nước, nút ready gần nhất (tính mép, hòa id); thiếu chỗ → `hold_full`, nút giữ nguyên | `_try_harvest`, `_nearest_in_radius` | Đạt |
| Bắt: dưới nước + hết hồi; đủ chỗ thêm toàn bộ yield, xóa đàn, đặt cooldown; thiếu chỗ giữ đàn & cooldown, không thử đàn khác | `_try_catch` | Đạt |
| Cooldown đặt ở t dùng lại từ t+L | giảm ở bước 1, đặt `catch_cooldown_s×60` | Đạt |
| Payload sự kiện khớp `docs/contracts/events.md` | — | Đạt |

Kiểm chứng thêm: toàn bộ test 58/58 OK (gồm `test_gather_p1.py` của Vỹ và `test_quan_p1.py`);
smoke 2 tiến trình mục G với gather thật → [`smoke-gather-quan.log`](smoke-gather-quan.log).

Ghi chú nhỏ (không chặn): `invuln_ticks` có trong snapshot nhưng PRD-0 không dùng ở Phase 1 (clarify #9b).
