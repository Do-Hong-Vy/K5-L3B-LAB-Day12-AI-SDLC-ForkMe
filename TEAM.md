# TEAM

**Tên nhóm:** ForkMe  **Số người:** 4  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Đỗ Hồng Vỹ | Do-Hong-Vy | `sim/gather` | Integrator | `sim/quan` (Cuubeo) |
| Bùi Phước Anh | Cuubeo | `sim/quan` | PO | `sim/gather` (Do-Hong-Vy) |
| Đinh Hoàng Phong | Phog2811 | `client/ui` | Scrum / Release | `qa` (Nguyenquoctoan0310) |
| Nguyễn Quốc Toàn | Nguyenquoctoan0310 | `qa` | QA Lead | `client/ui` (Phog2811) |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: Trực tiếp tại bàn + nhóm chat nội bộ của nhóm ForkMe.
- Khi bất đồng về thiết kế: Thảo luận tối đa 2 phút; nếu chưa chốt thì Integrator (`Do-Hong-Vy`) / PO (`Cuubeo`) quyết định và ghi lại lý do vào `docs/clarify.md` hoặc `docs/adr/`.
- Khi ai đó trễ hoặc vướng quá 10 phút: Báo ngay cho cả nhóm, người dự phòng tương ứng trong bảng trên nhận hỗ trợ hoặc tiếp quản lát đó.
- Giờ standup giữa phase: Phút 20–25 của mỗi phase (2–3 phút/lần), mỗi người cập nhật 1 dòng vào `docs/standup.md`.
- Cách đọc code của nhau: Review chéo theo cặp dự phòng (`Do-Hong-Vy` ↔ `Cuubeo`, `Phog2811` ↔ `Nguyenquoctoan0310`) trước khi chốt mỗi phase.
- Cách làm việc với Git: Mỗi thành viên code trên file/module mình sở hữu, chạy test xanh trước khi push lên `main`; Integrator (`Do-Hong-Vy`) điều phối tích hợp và gắn tag `phase-1..4`, `v1.0.0`.
