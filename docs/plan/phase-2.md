# Kế hoạch Phase 2 (≤ 1 trang)

> PO: Cuubeo. Nguồn: [`docs/ticket-02.md`](../ticket-02.md) (Test Contract v1.1). Ticket không đánh mã AC → PO đặt `AC-P2-xx` theo DoD + mục 1–4. Thay đổi contract: [`docs/adr/0001-contract-v1-1.md`](../adr/0001-contract-v1-1.md).

- **Mục tiêu:** contract v1.1 với số chuẩn; cá bơi/sinh, Cá Sấu + Máu/ngất; quán 2 bếp/4 bàn/6 món; `--mode day` chơi trọn vòng ngày (gather → quan → Shop) 1–5 Ngày; pause; menu/HUD; regression P1 xanh; tag `phase-2` trước **1:55**.

- **AC Phase 2:**

| AC | Nội dung (Ticket-02) | Lát / người |
|---|---|---|
| AC-P2-01 | `contract_version:"1.1"`, tuning chuẩn mục 1.1/1.3, 6 nguyên liệu (`ca_keo`, `keo_neo`), 6 món, N5/N6, validator nhận khóa mới (4.1) | Integrator Do-Hong-Vy (+ mỗi lát khai khóa của mình) |
| AC-P2-02 | Cá bơi 1.5 m/s trong dải loài, đổi hướng theo seed mỗi 120 bước bơi, phản xạ mép; `age_ticks` (1.1, 4.3) | L1 Do-Hong-Vy |
| AC-P2-03 | 8 đàn đầu ca ở 8 điểm khác nhau, trần 12, sinh mỗi 360 tick theo trọng số 40/30/30 + clearance > 1 m, `fish_spawned`; `random_fish:false` cá đứng yên (1.1) | L1 Do-Hong-Vy |
| AC-P2-04 | Cá Sấu patrol/chase/recoil, hit: −1 Máu, rơi floor(n/2) LIFO, bất tử 90, `monster_hit`; M2 từ Ngày 3; `faint` cause monster (1.2, 4.4) | L2 Nguyenquoctoan0310 (pair Do-Hong-Vy) |
| AC-P2-05 | Thứ tự bước gather v1.1 (4.5): ngạt → quái/hit → tương tác → bắt (vị trí cá trước khi bơi) → hết giờ → cá bơi/sinh | L1 + L2 |
| AC-P2-06 | Quán 2 bếp B1/B2, 4 bàn T1–T4, 6 món, hòa bếp trước bàn rồi id; regression luật quán v1.0 (1.3) | L3 Cuubeo |
| AC-P2-07 | `day_plan` D1–D5 trong contract (ingredients = tổng công thức × suất); trong day khách chỉ chọn món của kế hoạch; quán độc lập dùng cả 6 món (2) | L3 Cuubeo |
| AC-P2-08 | `--mode day --days 1..5`: `day_start` → `day_plan` → `phase_start(gather)` → `gather_end` → `phase_start(quan)` → `quan_end` → `phase_start(shop)` → `shop_end`; kho bàn giao trong bộ nhớ; money/earned/uy tín/cấp giữ qua Ngày; Máu/oxy hồi đầy; `days_completed`, `days_complete` (2, 4.4, 4.5) | L4 Cuubeo (backend) |
| AC-P2-09 | Shop: `buy` oxygen/hp theo dữ liệu, `bought`/`buy_failed` (funds/max_level/unknown), `shop_done`/tự đóng 600 tick, `shop_end`; cấp có hiệu lực từ Ngày kế (`active_upgrades`) (2, 4.2, 4.5) | L4 Cuubeo |
| AC-P2-10 | Pause cả 3 mode: cạnh `pause` xét trước, `paused`/`resumed`, `state:"paused"`, sim_tick/phase_tick/timer đứng yên (4.2) | L4 Cuubeo (sim) + Phog2811 (UI Esc/P) |
| AC-P2-11 | Scenario v1.1: khối `day`, `fish[].age_ticks`, `monsters[]`, cấm `quan.stock`/`quan.reputation` khi day; mâu thuẫn → mã 2 (4.3) | Nguyenquoctoan0310 |
| AC-P2-12 | Snapshot/event v1.1: `monsters[]`, `player.invuln_ticks`, `day`, `day_plan`, `upgrades`, `active_upgrades`, vỏ event có `day` (4.4) | Mỗi lát phần mình, QA kiểm |
| AC-P2-13 | Menu chính, DayIntro/EveningIntro/DayResult/Summary, pause menu, HUD sáng/tối theo mục 2; chữ ≥ 18 px ở 1280×720; ≥ 30 FPS | Phog2811 |
| AC-P2-14 | Headless 1 Ngày (≤ 22.200 tick) ≤ 20 s; tất định từng byte; smoke `gather --inventory-out → quan --inventory` (`docs/proof/phase-2/integration.*`) + smoke `day --days 1` và nhiều Ngày | Nguyenquoctoan0310 |
| AC-P2-15 | Regression P1 với số chuẩn; test đổi có ghi lý do; `docs/verification/phase-2.md`, clarify, ai-usage-log, retro; tag `phase-2` trước 1:55 | Cả nhóm (tag: Do-Hong-Vy) |

- **Việc / người / phụ thuộc / mốc:**

| # | Việc | Người | Phụ thuộc | Mốc |
|---|---|---|---|---|
| 0 | Gắn tag `phase-1` (đang thiếu!) trên commit P1 đã kiểm | Do-Hong-Vy | — | **ngay** |
| 1 | Re-plan, ADR-0001, clarify | Cuubeo + Do-Hong-Vy | — | 1:05 |
| 2 | Contract v1.1: khối `quan`/`menu`/`day_plan`/`shop` + 6 kind | Cuubeo | #1 | 1:10 |
| 3 | Contract v1.1: khối `gather` (số chuẩn, cá, N5/N6, monsters) | Do-Hong-Vy | #1 | 1:10 |
| 4 | L1 cá bơi/sinh | Do-Hong-Vy | #3 | 1:30 |
| 5 | L2 Cá Sấu, Máu/ngất | Nguyenquoctoan0310 | #3 | 1:30 |
| 6 | L3 quán 2 bếp/4 bàn/6 món + lọc menu theo kế hoạch | Cuubeo | #2 | 1:15 |
| 7 | L4 `--mode day`, Shop, pause (sim/runner) | Cuubeo | #6 | 1:35 |
| 8 | UI: menu, intro/result, pause, HUD v1.1 | Phog2811 | #2, #7 (snapshot day) | 1:40 |
| 9 | Validator v1.1, test P2, regression P1, proof, verification | Nguyenquoctoan0310 | #4–#7 | 1:45 |
| 10 | Retro nhanh P2 | Phog2811 + cả nhóm | — | 1:47 |
| 11 | Tích hợp, full test, tag `phase-2` | Do-Hong-Vy | #9 | 1:55 |

- **Rủi ro:**
  - Lát 4 (`day`) lớn nhất và phụ thuộc mọi lát → dựng khung `day` sớm với gather/quan hiện có, ghép luật mới sau.
  - Đổi số chuẩn làm vỡ test P1 (vd. 8 đàn cá, 2 bếp) → QA sửa test có ghi lý do, không sửa luật cho xanh.
  - Nhiều người cùng sửa `game.contract.json` → mỗi người chỉ sửa khối của mình, pull trước khi sửa.
  - Thứ tự RNG: mỗi tính năng một luồng `Streams` riêng (`fish_turn`, `fish_spawn`, `customers`...).
