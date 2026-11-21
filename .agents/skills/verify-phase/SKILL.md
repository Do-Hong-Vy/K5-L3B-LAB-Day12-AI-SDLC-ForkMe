---
name: verify-phase
description: Kiểm chứng một phase (chạy toàn bộ test + regression, kiểm tra determinism từng byte, mã thoát 2) rồi ghi bằng chứng thật vào docs/proof/phase-N/ và ma trận truy vết docs/verification/phase-N.md. Dùng trước khi gắn tag phase-N.
---

# Skill: `verify-phase` (QA Lead — `Nguyenquoctoan0310`)

Dùng khi: **(1)** một lát tính năng vừa gộp vào `main`, **(2)** trước mỗi tag `phase-1..4` / `v1.0.0` (chạy sau `check-contract`), **(3)** sau mỗi Change Request (chạy lại regression các phase trước).

Đầu vào: số phase `N` và danh sách `AC-PN-??` do PO chốt trong `docs/plan/phase-N.md`.

## 0. Chuẩn bị môi trường
- `game.contract.json` dùng `python3` (cho CI Ubuntu) → **không sửa `headless_cmd`**.
- Windows: cần `python3` gọi được trong `subprocess` (tạo `python3.exe` cạnh `python.exe`, hoặc dùng venv có `python3.exe`; tắt App execution alias `python3.exe` nếu gặp `WinError 1920`).
- Tạo thư mục bằng chứng: `mkdir -p docs/proof/phase-N`.

## 1. Toàn bộ test (unit + integration + regression)
```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v 2>&1 | tee docs/proof/phase-N/unittest.txt
python3 tools/check_team.py | tee docs/proof/phase-N/check_team.txt
```
(PowerShell: `$env:PYTHONPATH="tests;."` rồi chạy cùng lệnh, ghi bằng `| Out-File -Encoding utf8`.)
- Mọi test phase cũ (`tests/test_phase1_*.py`, ...) **phải chạy lại** — không xoá/skip test cũ khi đổi yêu cầu; nếu luật đổi theo đề, sửa test kèm lý do trong commit và ghi vào ADR.

## 2. Determinism từng byte (cùng seed ⇒ cùng JSONL)
```bash
P=docs/proof/phase-N
python3 -m chonoi.headless --mode gather --seed 7 --ticks 600 --out $P/gather_a.jsonl --inventory-out $P/inv_a.json
python3 -m chonoi.headless --mode gather --seed 7 --ticks 600 --out $P/gather_b.jsonl --inventory-out $P/inv_b.json
cmp $P/gather_a.jsonl $P/gather_b.jsonl && echo "gather: IDENTICAL" | tee $P/determinism.txt
python3 -m chonoi.headless --mode quan --seed 7 --ticks 600 --out $P/quan_a.jsonl [--inventory $P/inv_a.json]
python3 -m chonoi.headless --mode quan --seed 7 --ticks 600 --out $P/quan_b.jsonl [--inventory $P/inv_a.json]
cmp $P/quan_a.jsonl $P/quan_b.jsonl && echo "quan: IDENTICAL" | tee -a $P/determinism.txt
```
- Windows không có `cmp`: `fc /b a b` (cmd) hoặc `(Get-FileHash a).Hash -eq (Get-FileHash b).Hash`.
- Thử thêm với `--inputs` có thao tác (lặn/bắt/hái/nấu) để đường code luật thực sự chạy. Từ Phase 3: thêm `--mode day` nếu đã mở khoá.
- Giữ lại `gather_a.jsonl`, `quan_a.jsonl` làm mẫu; xoá bản `_b` nếu trùng.

## 3. Mã thoát & không ghi file khi lỗi
```bash
python3 -m chonoi.headless --mode gather --seed 1 --ticks -1 --out $P/bad.jsonl; echo "exit=$?"   # phải là 2
test ! -e $P/bad.jsonl && echo "OK: không tạo file khi lỗi input"
```
Ghi kết quả vào `$P/exit_codes.txt`. Với scenario mâu thuẫn (vd tổng `reserved` > `stock`) cũng phải thoát `2` trước khi ghi.

## 4. Sáng tạo tắt ở headless
Grep `chonoi/sim/` và `chonoi/headless.py`: không có code âm thanh/hiệu ứng/tính năng sáng tạo nào thay đổi JSONL. Nếu có cờ sáng tạo, chạy headless có/không cờ → JSONL phải giống nhau.

## 5. Điền ma trận truy vết `docs/verification/phase-N.md`
Mỗi `AC-PN-??` một dòng: `AC | Cách kiểm chứng (tên test / lệnh) | Link docs/proof/phase-N/... | Đạt / Chưa đạt`.
- **Trung thực:** AC chưa làm/fail ghi "Chưa đạt" + lý do; không ghi "Đạt" khi chưa có bằng chứng.
- Mục "Đánh giá ngắn": AC chưa đạt, việc chuyển phase sau.

## 6. Kết thúc
- Commit bằng chứng: `git add docs/proof/phase-N docs/verification/phase-N.md` — message ghi số test pass/fail và kết quả determinism.
- Báo Integrator (`Do-Hong-Vy`): ĐẠT → được gắn tag `phase-N`; KHÔNG ĐẠT → liệt kê test/AC fail cho người sở hữu module.
