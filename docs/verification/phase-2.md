# Ma trận truy vết Phase 2 (Ticket-02, Test Contract v1.1)

> QA lead: `Nguyenquoctoan0310` (skill [`verify-phase`](../../.agents/skills/verify-phase/SKILL.md)). Mã AC theo [`docs/plan/phase-2.md`](../plan/phase-2.md).
> Kiểm trên commit `7f29b9e` (main). Toàn bộ suite **257/257 OK** (P1 + P2 + regression): [unittest-full.txt](../proof/phase-2/unittest-full.txt).

| AC | Cách kiểm chứng | Bằng chứng | Kết quả (trung thực) |
|---|---|---|---|
| AC-P2-01 contract v1.1, số chuẩn, 6 nguyên liệu / 6 món, validator | `tests/test_contract_v11.py` (contract repo hợp lệ + 36 ca hỏng → `BadInput`: cá bơi/sinh, `keo_neo`, monsters, `day_plan` ingredients = công thức × suất, shop, `contract_version` lạ → mã 2 hộp đen); `test_gather_p2.GatherContractV11Tests`; `test_quan_p2.Data` | [unittest-full.txt](../proof/phase-2/unittest-full.txt) | Đạt — **mở**: clarify #22 (`fish_initial` là số 8 hay danh sách 8 đàn) chờ PO |
| AC-P2-02 cá bơi 1.5 m/s, đổi hướng mỗi 120 bước, phản xạ mép, `age_ticks` | `test_gather_p2.FishSwimmingTests` (3 test, Do-Hong-Vy) | [unittest-full.txt](../proof/phase-2/unittest-full.txt) | Đạt |
| AC-P2-03 8 đàn đầu ca, trần 12, sinh mỗi 360 tick theo trọng số + clearance, `fish_spawned` | `test_gather_p2.FishSpawnAndOrderTests` (Do-Hong-Vy) | [unittest-full.txt](../proof/phase-2/unittest-full.txt), [day-perf-determinism.log](../proof/phase-2/day-perf-determinism.log) (`fish_spawned`: 4) | Đạt |
| AC-P2-04 Cá Sấu patrol/chase/recoil, hit −1 Máu, rơi floor(n/2) LIFO, bất tử 90, `monster_hit`, M2 từ Ngày 3, `faint` cause monster | `tests/test_monsters_p2.py`: 24 unit (`MonsterSystem`) + 9 hộp đen qua `headless_cmd` (hit, bất tử chặn hit, ngất kho rỗng, M2 Ngày 3 trong `day`, tất định byte với hit thật) | [unittest-full.txt](../proof/phase-2/unittest-full.txt), [day-perf-determinism.log](../proof/phase-2/day-perf-determinism.log) (5 Ngày: M2 từ Ngày 3) | Đạt — giả định clarify #21 (`recoil_dist` là quãng lùi tổng) |
| AC-P2-05 thứ tự bước gather v1.1 | `test_monsters_p2.HeadlessMonsters.test_ngat_truoc_hit_cung_tick` (choke → monster_hit → faint), `test_ngat_choke_khong_xet_hit`, `test_gather_p2.test_step_order_catch_before_swim_and_no_swim_on_time_end` | [unittest-full.txt](../proof/phase-2/unittest-full.txt) | Đạt |
| AC-P2-06 2 bếp / 4 bàn / 6 món, hòa bếp trước bàn rồi id | `test_quan_p2.FourTablesTwoStoves` (Cuubeo) + regression `test_quan_p1` | [quan-l3-tests.log](../proof/phase-2/quan-l3-tests.log) | Đạt |
| AC-P2-07 `day_plan` D1–D5, lọc món theo kế hoạch, quán độc lập dùng 6 món | `test_quan_p2.PlanFilter`, `test_day_p2.test_ke_hoach_D1_D5_va_lap_lai` | [quan-l3-tests.log](../proof/phase-2/quan-l3-tests.log), [day-l4-tests.log](../proof/phase-2/day-l4-tests.log) | Đạt |
| AC-P2-08 `--mode day` đổi pha, kho bàn giao trong bộ nhớ, `days_completed` | `test_day_p2.DayFlow` (Cuubeo); chạy 1 và 5 Ngày | [day-smoke.log](../proof/phase-2/day-smoke.log), [day-perf-determinism.log](../proof/phase-2/day-perf-determinism.log) | Đạt |
| AC-P2-09 Shop: `bought`/`buy_failed`, tự đóng 600 tick, cấp có hiệu lực Ngày kế | `test_day_p2.Shop` (3 test) | [day-l4-tests.log](../proof/phase-2/day-l4-tests.log) | Đạt |
| AC-P2-10 pause cả 3 mode | `test_day_p2.Pause.test_pause_dung_moi_timer`; inputs `pause`/`shop_done`/`buy` (cạnh lên, `buy` chỉ tại frame khai báo): `test_scenario_v11.InputsV11` | [unittest-full.txt](../proof/phase-2/unittest-full.txt) | Đạt (sim) — phần UI Esc/P xem AC-P2-13 |
| AC-P2-11 scenario v1.1 (`day`, `age_ticks`, `monsters[]`, cấm `quan.stock`/`quan.reputation` khi day) | `tests/test_scenario_v11.py` (GatherV11 24 ca, DayScenario 19 ca), `test_day_p2.test_scenario_day_mau_thuan_ma_2`; từng ca sai đã đối chiếu đúng thông báo lỗi | [unittest-full.txt](../proof/phase-2/unittest-full.txt) | Đạt |
| AC-P2-12 snapshot/event v1.1 (`monsters[]`, `player.invuln_ticks`, `day`, `day_plan`, `upgrades`, `active_upgrades`, vỏ event có `day`) | `test_monsters_p2.test_snapshot_tick0_co_monsters_ngay_1`, `test_hit_qua_headless`; `test_day_p2.test_snapshot_day_co_truong_xuyen_ngay` | [day-smoke.log](../proof/phase-2/day-smoke.log) (event có `day`) | Đạt |
| AC-P2-13 menu, intro/result, pause menu, HUD v1.1, chữ ≥ 18 px, ≥ 30 FPS | Chơi thử `chonoi.live` + ảnh chụp/đo FPS | — (chờ `Phog2811`) | **Chưa kiểm chứng** |
| AC-P2-14 headless 1 Ngày ≤ 20 s, tất định, smoke tích hợp + day | 1 Ngày không input **2.69 s**, có bot **1.46–6.17 s**; 2 lần cùng seed + inputs **IDENTICAL**; 5 Ngày 12.2 s; smoke `gather --inventory-out → quan --inventory` có `ca_keo`/`keo_neo`, quán tick 0 khớp file kho; `test_day_p2.test_mot_ngay_duoi_20_giay_va_tat_dinh` | [integration.log](../proof/phase-2/integration.log), [day-perf-determinism.log](../proof/phase-2/day-perf-determinism.log) | Đạt (đo trên máy QA Windows; máy chấm Linux có thể khác) |
| AC-P2-15 regression P1 với số chuẩn, test đổi có lý do, ghi chép, tag | Regression P1 (`test_gather_p1`, `test_quan_p1`, `test_smoke_p1`, `test_scenario_quan_p1`, `test_contract_quan`) xanh trong full suite; test đổi: `test_quan_p1` hết bàn → 4 bàn (Cuubeo, `307bd44`), validator test bỏ tham số version sau gộp với `80f4d6d` | [unittest-full.txt](../proof/phase-2/unittest-full.txt) | Chưa đạt — chờ retro P2 + tag `phase-2` (Integrator) |

## Ghi chú
1. **Sự cố tích hợp đã xử lý:** merge `9612d91` làm mất `KINDS` trong `chonoi/inventory.py` → `main` NameError, 95 test fail / 13 lỗi (QA chạy lại trên worktree sạch để xác nhận). Đã khôi phục ở `6642956` (Cuubeo).
2. **Cá Sấu** viết tách ở `chonoi/sim/monsters.py` để làm song song với lát cá bơi; ghép vào `GatherSim.step` đúng thứ tự 4.5 (sau oxy/ngạt, trước tương tác), `DaySim` truyền `day` cho bố trí theo Ngày.
3. **Lỗi luật do test bắt:** Cá Sấu tới waypoint trễ 1 tick do cộng dồn 1/60 (63.99999999999977 ≠ 64) → sửa ở luật bằng sai số 1e-9, không sửa test.

## Đánh giá ngắn
- Đạt: AC-P2-01..12, 14 có bằng chứng tự động. Chưa kiểm chứng: AC-P2-13 (UI). Mở: clarify #21, #22. AC-P2-15 chờ retro + tag.
- Điều chỉnh cho phase sau: nhiều người cùng sửa `contract.py`/`scenario.py`/`inputs.py` gây trùng việc 2 lần → chốt chủ sở hữu file trước khi code (đưa vào retro).
