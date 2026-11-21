# Nguyenquoctoan0310 — phản tư cá nhân (≤ 200 từ)

> Soạn hộ bởi `Cuubeo` theo yêu cầu nhóm, **chỉ tổng hợp từ ghi chép của chính `Nguyenquoctoan0310`** trong `docs/ai-usage-log.md`, `docs/standup.md` và commit; `Nguyenquoctoan0310` rà lại và sửa nếu chưa đúng ý.

- **Tôi đã làm:** QA lead. CP0-6/7: sửa `test_template_is_rejected`, skill `verify-phase` (`597baee`); kiểm contract quán/menu + 42 ca scenario mục D -> mã 2, test tất định chuỗi gather->kho->quán, proof P1 (`db52e65`, `ebe2d52`); L2 Cá Sấu + validator/scenario/inputs v1.1 (`a27e45b`); smoke tích hợp, day ≤ 20 s, verification P2 (`b28f27e`).
- **Tôi đã review:** gộp 2 lần với code trùng của Do-Hong-Vy/Cuubeo; phát hiện `main` hỏng do merge mất `KINDS`.
- **AI sai ở đâu và tôi phát hiện thế nào:** AI định ghi đè `python3.exe` vào thư mục Python (bị chặn quyền) -> dùng venv tạm; AI viết kiểm `day_plan` trước `menu` khiến menu hỏng ra `KeyError` (mã 1 thay vì 2) -> test bắt được; lỗi cộng dồn số thực làm Cá Sấu tới waypoint trễ 1 tick -> test bắt, sửa luật; log proof lộ đường dẫn máy -> thay `$TMP`.
- **Điều tôi học được:** chạy test mới trên code cũ để chắc test bắt lỗi thật (19/20 fail trên bản cũ); chỗ ticket mơ hồ thì ghi clarify (#22) thay vì tự đổi.
