---
name: check-contract
description: Kiểm tra hợp đồng tích hợp, tính tất định headless và quy tắc không hard-code của nhóm ForkMe trước khi merge PR hoặc gắn tag phase-N.
---

# Skill: `check-contract` (Integrator Contract Guard)

Dùng skill này **trước khi gộp code vào `main`**, **khi có Change Request đụng tới `game.contract.json` / `docs/contracts/`**, và **bắt buộc trước mỗi lần gắn tag `phase-1`..`phase-4` / `v1.0.0`**.

## 1. Kiểm tra danh sách thành viên & cấu hình hợp đồng
1. Chạy lệnh kiểm tra thành viên:
   - Linux/macOS/CI: `python3 tools/check_team.py`
   - Windows (nếu `python3` bị alias): `python tools/check_team.py`
2. Xác nhận đầu ra bắt đầu bằng `OK: 4 thành viên:` và trùng khớp `team_size` trong `game.contract.json`, `team` là `"ForkMe"`.
3. Kiểm tra không có file bí mật (`.env`, API key, token) trong `git status` hoặc `git diff`.

## 2. Kiểm tra quy tắc vàng trong `chonoi/sim/*.py`
Đọc diff / code trong `chonoi/sim/` và xác nhận:
- **Không hard-code số liệu game:** Mọi thông số thời lượng, tốc độ, bán kính, sức chứa, cooldown, giá, tỷ lệ boa, uy tín... đều đọc từ `tuning` (`game.contract.json`), không dùng hằng số phép thuật trong luật.
- **Tất định (Determinism):**
  - Không import hoặc gọi `random.*` toàn cục; mọi ngẫu nhiên đi qua `self.rng.get("<stream_name>")` (`chonoi/rng.py`).
  - Không dùng `time.*`, `datetime.*` trong `chonoi/sim/`.
  - Mọi vòng lặp quyết định thứ tự thực thể/sự kiện đều sắp qua `ids.sort_by_id`; cấp id mới qua `IdAllocator`.
- **Không phá phần cố định khi sáng tạo:** Mọi logic hiệu ứng/âm thanh/tính năng mở rộng ngoài đề phải tắt hoàn toàn ở `chonoi.headless`.

## 3. Đối chiếu Hợp đồng tích hợp (`docs/contracts/`)
So sánh `chonoi/sim/gather.py`, `chonoi/sim/quan.py`, `chonoi/inventory.py` và `chonoi/web/index.html` với 3 tài liệu trong `docs/contracts/`:
1. **Schema kho (`inventory.sample.json`):** `{"items": {<id>: <int > 0>}}`, bỏ mục `0`, ghi một lần khi `gather_end`.
2. **Snapshot UI (`docs/contracts/sim-ui-interface.md`):** UI chỉ đọc trường có trong `snapshot()`, không tự suy diễn luật; nếu sim thêm/đổi khóa trong `snapshot()`, phải cập nhật tài liệu hợp đồng và báo cho `client/ui` (`Phog2811`).
3. **Sự kiện (`docs/contracts/events.md`):** Tên sự kiện, khóa trong `data`, và thứ tự ghi trong `step()` khớp giữa `sim/*` và tài liệu.
4. **Cơ chế Change Request:** Nếu PR có sửa `game.contract.json` hoặc `docs/contracts/`, kiểm tra bắt buộc đã có ADR mới trong `docs/adr/` (hoặc ghi chú rõ lý do + bảng tác động) và đã thông báo cả nhóm.

## 4. Kiểm chứng Headless nối chuỗi & Determinism từng byte
Chạy thử nối chuỗi `gather` → kho → `quan` 2 lần với cùng `--seed` (trên Windows thay `python3` bằng `python` nếu cần, giữ nguyên `game.contract.json` nếu dùng cho Linux CI):

```bash
python -m chonoi.headless --mode gather --seed 42 --ticks 600 --out /tmp/g1.jsonl --inventory-out /tmp/inv1.json
python -m chonoi.headless --mode gather --seed 42 --ticks 600 --out /tmp/g2.jsonl --inventory-out /tmp/inv2.json
```

Xác nhận:
- Mã thoát `0`; nếu chưa có `gather_end`, file `--inventory-out` không được tạo.
- Hai lần chạy cùng `seed` và cùng `inputs` cho file JSONL **giống hệt từng byte**.
- Chạy đầu vào lỗi (vd `--ticks -1` hoặc scenario sai mode) phải thoát mã `2` và **không tạo file `--out`**.
- Nếu `gather` kết thúc bình thường tạo `inv.json`, chạy tiếp `--mode quan --inventory inv.json` phải nạp `stock` khớp chính xác và thoát mã `0`.

## 5. Điều kiện xuất kết quả (Gate trước khi gắn tag)
Chỉ báo **ĐẠT** khi đủ cả 4 mục trên và không sửa test cho xanh khi luật sai. Ghi ngắn gọn kết quả kiểm tra (lệnh đã chạy, pass/fail, độ sai lệch nếu có) vào mô tả commit hoặc gửi QA Lead đưa vào `docs/verification/phase-N.md`.
