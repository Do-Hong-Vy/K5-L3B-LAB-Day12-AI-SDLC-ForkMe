# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt: Phân chia 4 lát song song rõ ràng (`L1` cá bơi/sinh, `L2` Cá Sấu/validator, `L3` quán 2 bếp/4 bàn/6 món, `L4` day/shop/UI v2.0); ADR-0001 khóa hợp đồng v1.1 sớm giúp `client/ui` và `sim/quan` triển khai song song mà không phải chờ nhau; giao diện live đạt đủ Menu/Pause/Shop/HUD v1.1 kèm hệ thống 2.5D VFX + Web Audio + Sáng tạo Đa Vũ Trụ tách bạch hoàn toàn khỏi headless.
- Điều tệ: Việc thay đổi số liệu chuẩn giữa v1.0 và v1.1 (1 bàn → 4 bàn, 6 đàn cá → 8 đàn cá) làm một số test cũ ở Phase 1 phải cập nhật lại; thao tác gắn tag `phase-1` bị trễ nhẹ so với mốc đầu Phase 2; vẫn cần đồng bộ sát khi nâng cấp `chonoi/live.py` cho `--mode day` và nút `pause`/`buy`.
- 1 hành động cho Phase 3: Trước khi code lát mới ở Phase 3, `Do-Hong-Vy` (Integrator) và `Cuubeo` (PO) chốt cứng cấu trúc snapshot + các cờ CLI/live mới trong `docs/contracts/` trong 5 phút đầu, và `Phog2811` (Scrum) nhắc kiểm tra tiến độ + tag sớm trước hạn 10 phút để không trễ mốc bàn giao.

## Phase 4 (cuối)
> Soạn bởi `Cuubeo` (PO) từ git log, `docs/standup.md`, `docs/ai-usage-log.md`; các bạn bổ sung ý riêng vào từng mục.

- **Rà lại hành động Phase 2** ("chốt snapshot/cờ CLI trong 5 phút đầu, nhắc tag sớm 10 phút"): *làm một nửa.* Hợp đồng v1.2 được chốt sớm bằng ADR-0002 + `docs/plan/phase-3.md`, nhưng **tag `phase-2..4` vẫn trễ** — vì cả nhóm dồn vào code lõi (v1.2, Cá Sấu, day) và chưa ai giữ đồng hồ mốc tag.
- **Điều tốt:** chia 4 lát song song theo gợi ý ticket; ADR + clarify giúp quyết nhanh (#12–#22); test hộp đen qua `headless_cmd` bắt được lỗi tích hợp sớm (merge làm mất `KINDS`, `lost` sai schema v1.2); helpers `stock/hold/kinds/counts` cho phép chuyển cả bộ test sang v1.2 mà không đổi luật.
- **Điều tệ:** tag trễ; hai người làm trùng Cá Sấu (Cuubeo và Toàn) do không báo trước khi bắt tay; UI từng dùng nhân vật thương hiệu khác (đã gỡ ở P4); merge thủ công làm đỏ `main` một lần.
- **Số liệu:** commit (không tính merge, tới lúc chốt retro): Cuubeo 32, Do-Hong-Vy 9, Nguyenquoctoan0310 5, Phog2811 4 (+ 9 commit starter của giảng viên). Cách đọc code của nhau: review chéo gather↔quan (P1), gộp/sửa chéo L2↔v1.2 (P3). Token: xem `docs/ai-usage-log.md` (nhóm chưa đo chính xác).
- **Một lần AI sai và cách nhóm phát hiện:** agent của `Cuubeo` push khi suite đỏ (điều kiện kiểm `tail` thay vì kết quả test) -> phát hiện qua log `FAILED (95)`; sửa `6642956` và thêm quy tắc "chỉ push khi suite xanh" vào AGENTS.md.
- **Nếu làm lại, đổi gì / hành động tiếp theo:** (1) Integrator đặt nhắc giờ tag ở phút 45 mỗi phase — người nhận: `Do-Hong-Vy`; (2) ai nhận lát nào thì ghi vào `docs/standup.md` trước khi code để tránh làm trùng — người nhận: `Phog2811` (Scrum); (3) chỉ dùng asset CC0/CC-BY/MIT, rà ở review — người nhận: `Nguyenquoctoan0310`.
