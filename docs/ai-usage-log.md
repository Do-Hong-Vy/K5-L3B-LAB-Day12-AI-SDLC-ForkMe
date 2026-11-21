# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 (CP0) | Do-Hong-Vy | Antigravity (Gemini) | Khởi tạo `task.md`, hoàn thiện `TEAM.md`, cập nhật `game.contract.json`, chốt `docs/contracts/`, viết skill `check-contract` & cập nhật `AGENTS.md` | Đang theo dõi (cập nhật cuối Phase 1) | Không có sẵn đề `PRD-0` trong repo; cần PO đối chiếu các payload event chưa có ở starter vào `docs/clarify.md` thay vì tự suy diễn. |
| Phase 1 (CP0) | Cuubeo | Claude Code (Opus 5.5) | CP0-4: điền `docs/plan/phase-1.md` (việc/người/mốc/rủi ro), thêm câu hỏi #6–#7 vào `docs/clarify.md` | ~1 phiên | AI làm song song với nhóm nên ghi đè TEAM.md/contracts của đồng đội khi rebase → phát hiện qua xung đột, bỏ bản của AI và giữ bản đã có trên `main`. Payload sự kiện chưa xác nhận vì PRD-0 chưa mở. |
