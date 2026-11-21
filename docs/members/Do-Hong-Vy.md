# Do-Hong-Vy — phản tư cá nhân (≤ 200 từ)

- **Vai:** Integrator, `sim/gather`, `docs/contracts/`, gắn tag & phát hành.
- **Tôi đã làm:**
  - Thiết lập `task.md`, `TEAM.md`, `AGENTS.md`, skill `check-contract` ([68ec0e3](../../commit/68ec0e3), [299880c](../../commit/299880c)) và bộ hợp đồng `docs/contracts/` ([8d0c215](../../commit/8d0c215), [ce4192e](../../commit/ce4192e)).
  - Cài đặt `GatherSim` Phase 1 + test ([f801a39](../../commit/f801a39)), chốt `phase-1` ([199f067](../../commit/199f067)).
  - Nâng Contract v1.1 phần `gather`/`monsters`, 6 nguyên liệu, cá bơi/sinh & `test_gather_p2` ([80f4d6d](../../commit/80f4d6d)).
  - Đồng bộ `docs/contracts/` v1.2–v1.3, dọn `kho.json`, hoàn tất kiểm chứng cuối, gắn tag `phase-2..4` & `v1.0.0`.
- **Tôi đã review:** Review chéo `QuanSim` của `Cuubeo` ([review](../proof/phase-1/review-quan-by-Do-Hong-Vy.md)), kiểm thử trực tiếp `chonoi.live` ([live-ui-check](../proof/phase-1/live-ui-check.md)), rà đồng bộ contract giữa các phase.
- **AI sai ở đâu & cách phát hiện:** Ở `test_gather_p2.py`, AI đặt sai số `places=9` khi đọc snapshot JSONL dù `JsonlWriter` làm tròn 3 chữ số; khi chạy test phát hiện lệch nhỏ nên sửa đối chiếu `round(..., 3)` / `delta=0.0015`. Ở P1, AI tính thiếu tick tăng tốc `ramp_max_ticks` khi đảo chiều.
- **Điều tôi học được:** Khóa hợp đồng/ADR trước khi chia lát và tách luồng `Streams` giúp nhóm sửa song song không dẫm nhau; luôn chạy lại full suite trước khi merge/tag/push.
