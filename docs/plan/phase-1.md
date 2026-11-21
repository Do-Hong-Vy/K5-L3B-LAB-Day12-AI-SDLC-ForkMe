# Kế hoạch Phase 1 (≤ 1 trang)

> PO: Cuubeo. Nguồn: [`docs/prd0.md`](../prd0.md). PRD-0 không đánh mã AC sẵn → PO đặt `AC-P1-xx` theo DoD (mục 7) + Test Contract (A–G) (`docs/clarify.md` #6).

- **Mục tiêu:** Lõi `gather` (oxy, ngạt, Máu, ngất, hái nút, bắt cá, giỏ LIFO, cập bến) + lõi `quan` (khách, giữ chỗ, bếp, bưng, phục vụ, tiền, boa, uy tín) + kho v1.0 nối `gather → quan`; headless tất định, test xanh; tag `phase-1` trước **1:00**.

- **AC Phase 1** (kiểm chứng ở `docs/verification/phase-1.md`):

| AC | Nội dung (PRD-0) | Người |
|---|---|---|
| AC-P1-01 | Bơi `[x,d]`: ramp ≤ `ramp_max_ticks`, Δt=1/60, chặn biên + triệt vận tốc ra ngoài, hướng theo move gần nhất (F) | Do-Hong-Vy |
| AC-P1-02 | Oxy/ngạt/Máu/ngất: mặt nước +6 & reset ngạt, dưới nước −1; `oxygen_empty`, `choke` mỗi 60 tick, `faint` bỏ giỏ LIFO → `gather_end` `fainted` kho rỗng; `dive`/`surface` (F, E) | Do-Hong-Vy |
| AC-P1-03 | Hái: bến xét trước; chỉ ở mặt nước, nút ready gần nhất (hòa id), `regrow_s×60`, `gather`/`hold_full`, `node_regrown` (F) | Do-Hong-Vy |
| AC-P1-04 | Bắt cá: dưới nước, hết hồi, đàn gần nhất; đủ chỗ thì thêm toàn bộ yield + xóa đàn + cooldown; thiếu chỗ `hold_full`, giữ đàn & cooldown (F) | Do-Hong-Vy |
| AC-P1-05 | Kết thúc `docked`/`time`/`fainted`; file kho ghi đúng 1 lần khi `gather_end`, nguyên tử; chạm `--ticks` trước thì không ghi (F, G) | Do-Hong-Vy |
| AC-P1-06 | Khách theo lịch `first_customer_tick` + `customer_interval_s×60`; bàn trống id nhỏ nhất; chọn món đều theo seed trong món khả dụng; giữ chỗ khi gọi; `customer_arrived`/`no_dish` (F) | Cuubeo |
| AC-P1-07 | Một interact/bước theo (khoảng cách, bếp trước bàn, id); bếp idle nấu đơn reserved cũ nhất → `cook_started`/`dish_ready`; bưng `dish_picked`; `served` với `tip = floor(price×tip_rate)` theo ngưỡng kiên nhẫn (F) | Cuubeo |
| AC-P1-08 | Ăn xong `paid` (`finished_eating`); hết kiên nhẫn `customer_left` (`patience`, −0.5 uy tín); đóng ca: ăn → `paid` `closing`, chờ → rời `closing` không trừ uy tín; boa dương +`tip_reputation`, kẹp; `quan_end` (F) | Cuubeo |
| AC-P1-09 | CLI headless đủ cờ mục B; `--inventory` chỉ quan, `--inventory-out` chỉ gather; mã 0/1/2; kiểm dữ liệu trước khi ghi (B, C, D) | Nguyenquoctoan0310 |
| AC-P1-10 | Scenario/inputs sai hoặc mâu thuẫn → mã 2 (danh sách mục D, C) | Nguyenquoctoan0310 |
| AC-P1-11 | JSONL: snapshot tick 0/bội `--snapshot-every`/tick dừng, event trước snapshot, `end` cuối; đủ trường mục E (kể cả `quan.player.vel`), tọa độ 3 chữ số, `score` | Cuubeo + Do-Hong-Vy |
| AC-P1-12 | Tất định: cùng seed + đầu vào → JSONL và file kho giống từng byte (E) | Nguyenquoctoan0310 |
| AC-P1-13 | Smoke 2 tiến trình (`dock.json`, seed 42) → quán tick 0 có `stock:{"bong_sung":2,"ca_loc":1}` (G) | Nguyenquoctoan0310 |
| AC-P1-14 | Chơi được cả hai buổi; HUD: thời gian, oxy, Máu, giỏ / kho khả dụng, món gọi, kiên nhẫn, bếp, tay, tiền, uy tín (mục 2, DoD) | Phog2811 |
| AC-P1-15 | README: chạy từ clone sạch ≤ 3 lệnh, điều khiển, cách tính điểm, lệnh test 1 lệnh; `game.contract.json` khớp bản chạy (DoD) | Phog2811 + Do-Hong-Vy |
| AC-P1-16 | Ghi chép: TEAM.md, hợp đồng kho, `docs/verification/phase-1.md` + `docs/proof/phase-1/`, clarify, ai-usage-log; tag `phase-1` trên `main` trước 1:00 (DoD, 6.3) | Cả nhóm (tag: Do-Hong-Vy) |

- **Việc / người / phụ thuộc:**

| # | Việc | Người | Phụ thuộc | Mốc |
|---|---|---|---|---|
| 1 | Chốt TEAM.md, contract `team`, hợp đồng tích hợp, 2 skill | Cả nhóm | — | 0:15 |
| 2 | `gather` lát 1: bơi, oxy, choke, faint (AC-01, 02) | Do-Hong-Vy | #1 | 0:30 |
| 3 | `gather` lát 2: hái, bắt cá, hold_full, cập bến, kho (AC-03..05) | Do-Hong-Vy | #2 | 0:45 |
| 4 | `quan` lát 3: khách, giữ chỗ, kiên nhẫn (AC-06, 08) | Cuubeo | #1 | 0:35 |
| 5 | `quan` lát 4: bếp, bưng, phục vụ, tiền, `player.vel` (AC-07, 08, 11) | Cuubeo | #4 | 0:50 |
| 6 | HUD + README (AC-14, 15) | Phog2811 | #1 | 0:50 |
| 7 | Mã 2, unit + smoke + determinism, verification + proof (AC-09, 10, 12, 13) | Nguyenquoctoan0310 | #2–#5 | 0:55 |
| 8 | Tích hợp trên `main`, chạy test, gắn tag `phase-1` (AC-16) | Do-Hong-Vy | #7 | 1:00 |

- **Rủi ro:**
  - Lệch payload sự kiện giữa sim và UI/test → chỉ dùng `docs/contracts/events.md` (đã đối chiếu PRD-0), đổi phải báo Integrator.
  - Mất tất định (dùng `random`/clock, không sắp id) → mọi ngẫu nhiên qua `Streams`, QA chạy 2 lần cùng seed so byte (skill `verify-phase`).
  - Biên thời gian (ngạt ở t+59, phục vụ đúng tick kiên nhẫn 0, E đúng mép bến ở bước cuối) → viết test riêng cho từng biên.
  - Windows `python3`/encoding → `PYTHONUTF8=1`; không đổi `headless_cmd`.
  - Xung đột git ở `game.contract.json` → chỉ Integrator sửa contract.
