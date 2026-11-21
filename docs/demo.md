# Kịch bản demo (≤ 5 phút) — checklist Ticket-04

| # | Việc | Lệnh / thao tác | Người trình bày |
|---|---|---|---|
| 1 | Chơi một Ngày: Lặn & Hái -> Mở Quán -> Shop đóng | `python3 -m chonoi.live --mode day --days 1` · hái bông súng (N3/N4), bắt cá lóc (xám, thân dài), về bến `E`; quán: `E` bếp -> `E` bưng -> `E` bàn; Shop: mua `oxygen`, đóng | Phog2811 |
| 2 | Cảnh báo + tương phản cao | lặn sâu gần Cá Sấu (🐊), để oxy < 25% (🫧), để khách chờ (😠); bấm `T` | Phog2811 |
| 3 | Chạy test, cho thấy đạt | `PYTHONPATH=tests:. python3 -m unittest discover -s tests` | Nguyenquoctoan0310 |
| 4 | Headless tất định + bench + soak | `python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 30000 --out d.jsonl` (chạy 2 lần, `cmp`); `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`; `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json` | Nguyenquoctoan0310 |
| 5 | Bằng chứng chia việc & đóng góp | `TEAM.md`, `task.md`, `git shortlog -sn`, `docs/standup.md`, `docs/members/` | Do-Hong-Vy |
| 6 | Ma trận truy vết | `docs/verification/phase-1..4.md` -> mở 1 dòng AC -> file trong `docs/proof/` | Cuubeo |
