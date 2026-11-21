# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 (CP0) | Do-Hong-Vy | Antigravity (Gemini) | Khởi tạo `task.md`, hoàn thiện `TEAM.md`, cập nhật `game.contract.json`, chốt `docs/contracts/`, viết skill `check-contract` & cập nhật `AGENTS.md` | Đang theo dõi (cập nhật cuối Phase 1) | Không có sẵn đề `PRD-0` trong repo; cần PO đối chiếu các payload event chưa có ở starter vào `docs/clarify.md` thay vì tự suy diễn. |
| Phase 1 (CP0) | Nguyenquoctoan0310 | Claude Code (Claude Opus 5.5) | Sửa `test_template_is_rejected` (dùng chuỗi template, thêm test `TEAM.md` thật hợp lệ), chẩn đoán lỗi `python3` trên Windows, viết skill `verify-phase`, cập nhật `AGENTS.md` | Đang theo dõi (cập nhật cuối Phase 1) | AI định ghi đè `python3.exe` vào thư mục cài Python, bị chặn quyền → chuyển sang venv tạm để kiểm chứng; người dùng tự tạo shim cục bộ. |
