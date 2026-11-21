# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test (Linux/CI): `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Test (Windows PowerShell): `$env:PYTHONPATH="tests;."; python -m unittest discover -s tests -v`
- Kiểm tra thành viên: `python tools/check_team.py` (hoặc `python3 tools/check_team.py` trên Linux)
- Headless: `python -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl` (trên Linux dùng `python3`)
- Chơi thử trên trình duyệt: `python -m chonoi.live --mode gather|quan` (mở địa chỉ in ra; WASD, E, Space, R)

> Lưu ý Windows: `game.contract.json` đang giữ `"headless_cmd": "python3 -m chonoi.headless"` cho CI `ubuntu-latest` và máy chấm Linux. Trên Windows có thể gặp `[WinError 1920]` với alias `python3`; không tự ý sửa `headless_cmd` khi chưa kiểm chứng tương thích chấm điểm.
> Test hộp đen gọi `python3` qua `subprocess`; nếu Windows không có `python3` thì 20 test smoke/live báo `FileNotFoundError`. Cách sửa cục bộ (không commit): tạo `python3.exe` cạnh `python.exe` (copy), hoặc dùng venv rồi copy `Scripts/python.exe` → `Scripts/python3.exe`.

## Cấu trúc & quy ước
- Kế hoạch & phân công theo CP: xem [`task.md`](task.md) và [`TEAM.md`](TEAM.md).
- Hợp đồng tích hợp đã chốt tại [`docs/contracts/`](docs/contracts/README.md) (`sim-ui-interface.md`, `events.md`, `inventory.sample.json`).
- Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm và ghi ADR (`docs/adr/`).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO (`Cuubeo`).
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase, `task.md`, và hợp đồng trong `docs/contracts/` trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- **Skill 1 — `check-contract`** ([`.agents/skills/check-contract/SKILL.md`](.agents/skills/check-contract/SKILL.md)): do `Do-Hong-Vy` (Integrator) duy trì. Dùng trước khi merge lát tính năng, khi có Change Request đụng contract, và trước khi gắn tag `phase-1..4` để kiểm tra `check_team`, không hard-code tuning, determinism từng byte và đồng bộ `docs/contracts/`.
- **Skill 2 — `verify-phase`** ([`.agents/skills/verify-phase/SKILL.md`](.agents/skills/verify-phase/SKILL.md)): do `Nguyenquoctoan0310` (QA Lead) duy trì. Dùng sau khi gộp một lát, sau mỗi Change Request, và trước tag `phase-N` (chạy sau `check-contract`): chạy full test + regression, kiểm tra determinism từng byte và mã thoát `2`, lưu log vào `docs/proof/phase-N/` và điền `docs/verification/phase-N.md`.
