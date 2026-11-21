# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt: Phân chia 4 lát song song rõ ràng (`L1` cá bơi/sinh, `L2` Cá Sấu/validator, `L3` quán 2 bếp/4 bàn/6 món, `L4` day/shop/UI v2.0); ADR-0001 khóa hợp đồng v1.1 sớm giúp `client/ui` và `sim/quan` triển khai song song mà không phải chờ nhau; giao diện live đạt đủ Menu/Pause/Shop/HUD v1.1 kèm hệ thống 2.5D VFX + Web Audio + Sáng tạo Đa Vũ Trụ tách bạch hoàn toàn khỏi headless.
- Điều tệ: Việc thay đổi số liệu chuẩn giữa v1.0 và v1.1 (1 bàn → 4 bàn, 6 đàn cá → 8 đàn cá) làm một số test cũ ở Phase 1 phải cập nhật lại; thao tác gắn tag `phase-1` bị trễ nhẹ so với mốc đầu Phase 2; vẫn cần đồng bộ sát khi nâng cấp `chonoi/live.py` cho `--mode day` và nút `pause`/`buy`.
- 1 hành động cho Phase 3: Trước khi code lát mới ở Phase 3, `Do-Hong-Vy` (Integrator) và `Cuubeo` (PO) chốt cứng cấu trúc snapshot + các cờ CLI/live mới trong `docs/contracts/` trong 5 phút đầu, và `Phog2811` (Scrum) nhắc kiểm tra tiến độ + tag sớm trước hạn 10 phút để không trễ mốc bàn giao.

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:
