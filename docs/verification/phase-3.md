# Ma trận truy vết Phase 3 (Ticket-03 "Mùa Nước Nổi", Test Contract v1.2)

> AC theo [`docs/plan/phase-3.md`](../plan/phase-3.md); quyết định schema: [ADR-0002](../adr/0002-kho-ca-the-v1-2.md).
> Kiểm trên `main` sau khi gộp v1.2 với L2 Cá Sấu (`b4eb273` trở đi). Suite đầy đủ: [v12-tests.log](../proof/phase-3/v12-tests.log)
> (267 OK, 1 skip chỉ áp dụng v1.1). Smoke theo đúng ví dụ ticket: [smoke-v12.log](../proof/phase-3/smoke-v12.log).
> Ghi trung thực: Phase 3 được hoàn tất **sau** mốc 2:30; tag `phase-3` gắn muộn (xem retro).

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P3-01 schema kho cá thể, chọn theo `contract_version`, v1.2 từ chối kho đếm / kind lạ / id trùng / fresh ngoài miền | `test_smoke_p1.test_inv_bad_schema_exit_2` (6 ca v1.2), `test_v12_monsters.test_kho_dem_bi_tu_choi_o_v12`; ghi nguyên tử + xuất theo id | [v12-tests.log](../proof/phase-3/v12-tests.log), [smoke-v12.log](../proof/phase-3/smoke-v12.log) | Đạt |
| AC-P3-02 gather: fresh 100, id I1.. theo thứ tự vào giỏ, hao 0.5/s từ bước sau, `spoiled` hold một lần, `lost` cá thể LIFO, `gather_end.inventory` cùng schema | `test_v12_monsters.FreshGather` (ví dụ ngưỡng ticket, id kế tiếp + hao từ bước sau), `test_gather_p1` faint LIFO, `test_monsters_p2` hit/faint | [smoke-v12.log](../proof/phase-3/smoke-v12.log) (`spoiled` tick 1) | Đạt |
| AC-P3-03 quán: kho cá thể, hao 0.25/s kể cả hàng giữ, `spoiled` stock theo id trước xử lý giữ chỗ | `test_quan_p3.Stock` (4 test: sắp id, hao 0.25/s, spoiled theo id một lần, ngưỡng chính xác 30 + 1/240) | [v12-tests.log](../proof/phase-3/v12-tests.log) | Đạt |
| AC-P3-04 giữ theo id: tươi nhất hòa id; vừa ươn -> nhả và giữ lại một lần; thiếu -> `unfulfillable` | `test_quan_p3.Reserve` (4 test) | [v12-tests.log](../proof/phase-3/v12-tests.log) | Đạt |
| AC-P3-05 giá theo tươi `floor(giá × tb fresh / 100)`, `items` cá thể sắp kind rồi id, boa trên giá đã chốt | `test_quan_p3.Price` (2 test), `test_quan_p1.test_vong_phuc_vu_day_du_co_boa` (giá chốt sau 1 tick hao) | [v12-tests.log](../proof/phase-3/v12-tests.log) | Đạt |
| AC-P3-06 scenario v1.2: `hold`/`stock` mảng cá thể, `reserved` mảng id, liên kết sai -> mã 2 | `chonoi/scenario.py::_check_reserved_ids`; `test_scenario_quan_p1` chạy trên fixture v1.2 | [v12-tests.log](../proof/phase-3/v12-tests.log) | Đạt |
| AC-P3-07 bàn giao trong `day` cùng tick, id cá thể nối tiếp qua Ngày | `test_v12_monsters.test_id_ca_the_tiep_tuc_qua_ngay` (I1 Ngày 1, I2 Ngày 2), `test_day_p2` | [smoke-v12.log](../proof/phase-3/smoke-v12.log) (5 Ngày giống từng byte) | Đạt |
| AC-P3-08 HUD độ tươi / hàng ươn | `chonoi/web/index.html`: ô giỏ có vạch độ tươi xanh/vàng/đỏ, xám + ⚠ khi < 30; kho khả dụng bỏ hàng ươn (`de2ebfc`) | kiểm tay trên `chonoi.live` | Đạt (kiểm tay) |
| AC-P3-09 smoke ngưỡng + bàn giao file, regression P1–P2, CHANGELOG breaking change | [smoke-v12.log](../proof/phase-3/smoke-v12.log); fixture test cũ chuyển qua `tests/helpers.py` (`stock/hold/kinds/counts`) — lý do trong commit `6065631`; [CHANGELOG](../../CHANGELOG.md) | [v12-tests.log](../proof/phase-3/v12-tests.log) | Đạt |

## Đánh giá ngắn
- Đạt toàn bộ lõi v1.2. Mở rộng Phase 3 (dòng lũ, khách đặt trước) **không làm** (nhóm 4 người không bắt buộc).
- Rủi ro đã xử lý: số thực ở ngưỡng 30 -> độ tươi lưu số nguyên 240 đơn vị/điểm (ADR-0002).
