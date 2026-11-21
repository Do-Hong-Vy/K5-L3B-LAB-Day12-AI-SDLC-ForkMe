# Standup giữa phase (mỗi người một dòng, 2–3 phút)

| Phase | Người | Đã xong | Sắp làm | Vướng gì |
|---|---|---|---|---|
| Phase 1 | Do-Hong-Vy | Chốt CP0, cài đặt xong `GatherSim` (`AC-P1-01..05`) + 11 test `test_gather_p1.py` (44/44 pass), bổ sung `README.md` (`AC-P1-15`) | Chờ `Cuubeo` xong `sim/quan` để review chéo, chạy `check-contract` toàn bộ và gắn tag `phase-1` trước 1:00 | Không |
| Phase 1 | Cuubeo | `sim/quan` (`AC-P1-06..08`, `quan.player.vel`) + 14 test `test_quan_p1.py` (58/58 pass toàn bộ); review chéo `gather` của Vỹ: đạt; smoke 2 tiến trình mục G đạt | Hỗ trợ QA điền verification; chờ Vỹ review `quan` và gắn tag | **Báo `Phog2811`:** `hand` và `stoves[].dish` là object `{order_id, dish_id, base_price}`, `customers[].base_price/tip` là `null` tới khi chốt. **Báo `Nguyenquoctoan0310`:** có `tests/test_quan_p1.py`; kiểm mâu thuẫn scenario quan (mục D) vẫn chờ `scenario.py` |
| Phase 1 | Phog2811 | Hoàn thiện UI/HUD v1.0 (`chonoi/web/index.html` — `AC-P1-14`): cảnh sông Chín Khúc (`gather`) & nhà bè Má Tư (`quan`), xử lý đúng `st.dish` / `hand` dạng object `{order_id, dish_id, base_price}` theo báo cáo của `Cuubeo`, tính kho khả dụng (`stock - reserved`), thanh kiên nhẫn có mốc tip 50%, sổ tay thực đơn 3 món & màn hình tổng kết ca | Phối hợp QA chụp bằng chứng live UI và chuẩn bị gắn tag `phase-1` | Không |
