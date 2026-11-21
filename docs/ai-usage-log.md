# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 (CP0) | Do-Hong-Vy | Antigravity (Gemini) | Khởi tạo `task.md`, hoàn thiện `TEAM.md`, cập nhật `game.contract.json`, chốt & đồng bộ `docs/contracts/`, viết skill `check-contract` & cập nhật `AGENTS.md` | Đang theo dõi (cập nhật cuối Phase 1) | Không có sẵn đề `PRD-0` trong repo; hợp đồng mở rộng được đánh dấu rõ là `[Đề xuất nhóm — chờ PO đối chiếu PRD-0]` vào `docs/clarify.md` thay vì tự suy diễn là chuẩn PRD. |
| Phase 1 (CP0) | Nguyenquoctoan0310 | Claude Code (Claude Opus 5.5) | Sửa `test_template_is_rejected` (dùng chuỗi template, thêm test `TEAM.md` thật hợp lệ), chẩn đoán lỗi `python3` trên Windows, viết skill `verify-phase`, cập nhật `AGENTS.md` | Đang theo dõi (cập nhật cuối Phase 1) | AI định ghi đè `python3.exe` vào thư mục cài Python, bị chặn quyền → chuyển sang venv tạm để kiểm chứng; người dùng tự tạo shim cục bộ. |
| Phase 1 (CP0) | Cuubeo | Claude Code (Opus 5.5) | CP0-4: điền `docs/plan/phase-1.md` (việc/người/mốc/rủi ro), thêm câu hỏi #6–#7 vào `docs/clarify.md` | ~1 phiên | AI làm song song với nhóm nên ghi đè TEAM.md/contracts của đồng đội khi rebase → phát hiện qua xung đột, bỏ bản của AI và giữ bản đã có trên `main`. Payload sự kiện chưa xác nhận vì PRD-0 chưa mở. |
