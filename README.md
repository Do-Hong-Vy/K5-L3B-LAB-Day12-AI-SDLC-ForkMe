# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

**Yêu cầu:** Python 3.10+ (chỉ thư viện chuẩn), trình duyệt bất kỳ. Trên Windows đặt `PYTHONUTF8=1` khi chạy test.

Chạy từ clone sạch (macOS / Linux, ≤ 3 lệnh):

```bash
git clone https://github.com/Do-Hong-Vy/K5-L3B-LAB-Day12-AI-SDLC-ForkMe.git && cd K5-L3B-LAB-Day12-AI-SDLC-ForkMe
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # chạy toàn bộ test (1 lệnh)
python3 -m chonoi.live --mode day --days 5                          # chơi trọn 5 Ngày trên trình duyệt (mở địa chỉ in ra)
```

Chơi riêng từng buổi: `python3 -m chonoi.live --mode gather --inventory-out kho.json` rồi `python3 -m chonoi.live --mode quan --inventory kho.json`.

- **Điều khiển:** `WASD`/mũi tên bơi (`gather`) / đi (`quan`) · `E` tương tác (cập bến, hái rau ở mặt nước; nấu / bưng / phục vụ ở quán) · `Space` bắt cá khi lặn · `Esc`/`P` tạm dừng · `T` tương phản cao · `C` chế độ Sáng tạo · `H` sổ thực đơn · `M` âm thanh · `R` chơi lại. Shop: mua `oxygen` / `hp` rồi đóng Shop.
- **Cách tính điểm:** `score = earned + reputation_multiplier × floor(reputation)` (mặc định `reputation_multiplier = 100`); tiền là số nguyên nghìn đồng; giá món theo độ tươi `floor(giá × trung bình fresh / 100)`, boa `floor(giá × 0.2)` nếu còn ≥ 50% kiên nhẫn.

| Lệnh | Mục đích |
|---|---|
| `python3 -m chonoi.headless --mode gather\|quan\|day [--days N] --seed S --ticks T --out out.jsonl` | Headless theo Test Contract v1.3 (gameplay v1.2), tất định từng byte |
| `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json` | Benchmark có render (`bench_cmd`) |
| `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json` | Soak 10 Ngày (`soak_cmd`) |

**Giới hạn đã biết:** benchmark đo render phần mềm của bản Python (không đo canvas trình duyệt); chưa làm các mở rộng tùy chọn (dòng lũ, khách đặt trước, Lao, vợt, Rắn, cháy món, Chợ, Sổ tay, leaderboard, phụ đề SFX). Chi tiết khung Python: [`docs/STARTER.md`](docs/STARTER.md). Lịch sử thay đổi: [`CHANGELOG.md`](CHANGELOG.md) · phát hành: [`docs/release-notes-v1.0.0.md`](docs/release-notes-v1.0.0.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Sáng tạo của nhóm

Nhóm **ForkMe** (phụ trách UI/Sáng tạo: `Phog2811`) xây dựng chế độ **⚡ Đại Chiến Chợ Nổi (Năm Chèo × Khách quen) + Đồ họa 2.5D VFX & Âm thanh Web Audio API** hoàn toàn ở tầng client ([`chonoi/web/index.html`](chonoi/web/index.html)):

- **Đồ họa 2.5D Stylized & Particle VFX (60 FPS, Canvas 2D):**
  - *Buổi sáng (`gather`):* Bình minh sông Chín Khúc nhiều tầng parallax, rặng dừa nước đung đưa, sóng mặt nước động, tia nắng xuyên 3 tầng độ sâu (Nông / Giữa / Sâu), rong/đá đáy sông, bong bóng khí, hiệu ứng sóng xung kích khi hái/bắt cá và rung màn hình khi ngạt hoặc gặp thủy quái.
  - *Buổi tối (`quan`):* Mặt sông đêm lung linh, sàn gỗ nhà bè có đổ bóng 2.5D, dây đèn lồng vàng tỏa sáng, lửa/khói bếp khi nấu ăn, mưa tiền xu khi thu tiền.
- **Nhân vật người & sinh vật bằng sprite CC0 (Kenney, xem [`CREDITS.md`](CREDITS.md)):** Út Sen (đứng / đi bộ có hoạt ảnh / lặn nằm ngang theo hướng bơi / bưng món / bị thương) và 3 dáng khách (chờ, gọi món, vui khi ăn, giận khi kiên nhẫn < 25%) — *Toon Characters 1*; cá linh / cá lóc / cá kèo, rong, đá, bong bóng — *Fish Pack 2.0*.
- **Chế độ Sáng tạo Chợ Nổi (bật/tắt bằng phím `C` hoặc nút trên HUD/Menu):**
  - *Dưới sông (`gather`):* Boss **Cá Sấu Năm Chèo** tuần tra tầng sâu, thoại giọng Nam Bộ. Khi Út Sen bắt cá (`Space`) hoặc bấm `Q` / click chuột, Út Sen tung **Chưởng Sóng Bà Ba** đấu với Năm Chèo.
  - *Trên nhà bè (`quan`):* Khách quen tại các bàn `T1–T4` rung sàn bè khi kiên nhẫn xuống thấp; khi phục vụ (`E`), Út Sen tung chiêu **Chưởng Lẩu**; nhấn `Q` / `Space` / click chuột để kích hoạt hiệu ứng **Đấu Chưởng (Beam Clash)**.
- **Âm nhạc & Hiệu ứng âm thanh Web Audio API (100% tự tổng hợp, lưu cài đặt trong `localStorage`):**
  - Nhạc nền tự động đổi giữa **Ngũ cung Miền Tây** (chế độ thuần) và **Boss Battle Synth** (chế độ Chợ Nổi), kèm đầy đủ SFX theo từng sự kiện (`dive`, `gather`, `fish_caught`, `cook_started`, `dish_ready`, `served`, `paid`, `customer_arrived`...). Có 3 thanh trượt âm lượng `Master / Music / SFX` và phím tắt `M`.
- **Cam kết không phá lõi & tắt 100% ở headless:** Toàn bộ tính năng đồ họa, VFX, âm thanh và nhân vật sáng tạo nằm độc lập trong `chonoi/web/index.html`, chỉ đọc snapshot từ `GET /state` và hoàn toàn **không chạy** khi thực thi `python3 -m chonoi.headless`. Toàn bộ bộ test tự động (`unittest`) và kiểm tra determinism từng byte vẫn đạt 100%.

## Sáng tạo của nhóm

### Bếp nhiều section (Cuubeo)
- **Cách chơi:** quán có 6 section sơ chế (S1 cá lóc, S2 cá linh, S3 cá kèo, S4 bông điên điển, S5 bông súng, S6 kèo nèo — xem `chonoi/creative/kitchen.json`). Đứng tại section nhấn **E**: section sơ chế 1 phần nguyên liệu cho đơn cũ nhất còn cần loại đó (1–2 s, người chơi đi làm việc khác được). Khi mọi nguyên liệu của đơn đã sơ chế đủ, tới bếp nhấn **E** để **gộp lại thành món** và nấu như luật thường. Khách bỏ đi thì phần sơ chế dở bị hủy.
- **Bật/tắt:** chỉ bật trong `python3 -m chonoi.live --mode quan`; thêm `--no-creative` để chơi đúng luật lõi. **Headless không bao giờ bật** (`runner.build_sim` mặc định `kitchen=None`).
- **Bằng chứng lõi vẫn đúng:** `tests/test_creative_kitchen.py::HeadlessUnchanged` (headless không có `sections`/`prepped`/`prep_*`) + toàn bộ test lõi xanh — [`docs/proof/phase-2/creative-kitchen-tests.log`](docs/proof/phase-2/creative-kitchen-tests.log).

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
