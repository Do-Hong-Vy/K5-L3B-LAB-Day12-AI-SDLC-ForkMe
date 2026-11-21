# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| AC-P1-06 (khách, lịch, giữ chỗ, no_dish) | `tests/test_quan_p1.py::QuanCustomers` (7 test hộp đen qua `headless_cmd`) | [quan-tests.log](../proof/phase-1/quan-tests.log) | Đạt |
| AC-P1-07 (interact: nấu, bưng, phục vụ, boa) | `QuanService.test_vong_phuc_vu_day_du_co_boa`, `test_boa_0_khi_kien_nhan_duoi_nguong`, `test_bep_dang_nau_khong_tuong_tac...` | [quan-tests.log](../proof/phase-1/quan-tests.log) | Đạt (thứ tự hòa "bếp trước bàn" chưa có test riêng vì preset bếp/bàn cách xa) |
| AC-P1-08 (trả tiền, rời bàn, uy tín, đóng ca) | `test_het_kien_nhan_roi_ban_tru_uy_tin`, `test_khach_roi_bo_mon_dang_nau`, `test_dong_ca_tra_tien_closing...` | [quan-tests.log](../proof/phase-1/quan-tests.log) | Đạt |
| AC-P1-11 (phần quan: snapshot có `player.vel`, customers đủ trường) | `test_snapshot_quan_player_co_vel`, `test_khach_den_dung_first_customer_tick_va_giu_cho` | [quan-tests.log](../proof/phase-1/quan-tests.log) | Đạt (phần quan) |
| AC-P1-12 (phần quan: tất định) | Chạy 2 lần seed 3, 10800 tick, `cmp` từng byte + `test_cung_seed_cung_byte` | [quan-determinism.log](../proof/phase-1/quan-determinism.log) | Đạt (phần quan) |
| AC-P1-13 (smoke 2 tiến trình) | Lệnh mẫu PRD-0 mục G, seed 42 | [smoke-gather-quan.log](../proof/phase-1/smoke-gather-quan.log) | Đạt — quán tick 0 `stock:{"bong_sung":2,"ca_loc":1}` |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt:
- Điều cần chỉnh cho phase sau:
