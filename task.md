# TASK.md — Kế hoạch thực hiện Lab Day 12: Quán Ăn Chợ Nổi (Nhóm ForkMe)

> Tài liệu điều phối công việc bám sát **4 Phase / Checkpoints (CP)** trong **3 giờ**, phân công theo [`TEAM.md`](TEAM.md), và đối chiếu đủ **100 điểm đánh giá** trong [`README.md`](README.md) & [`AGENTS.md`](AGENTS.md).
>
> **Lưu ý về nguồn yêu cầu:** Các AC chi tiết của `PRD-0` (Phase 1) và đề mở rộng Phase 2–4 mở theo mốc giờ tại Lab Board (**Chợ Nổi Lab** trên `claude.ai`). Không tự bịa yêu cầu: khi mở từng phase, **PO** trích các `AC-Pn-??` và câu hỏi mở vào [`docs/clarify.md`](docs/clarify.md) rồi chốt vào kế hoạch phase tương ứng.

---

## 1. Tổ chức nhóm & Phân công vai trò

### Bảng thành viên (theo [`TEAM.md`](TEAM.md))

| Thành viên | GitHub handle | Module chính | Đề xuất Vai quy trình | Đề xuất Dự phòng cho | Ghi chú sở hữu chính |
|---|---|---|---|---|---|
| Đỗ Hồng Vỹ | `Do-Hong-Vy` | `sim/gather` | **Integrator** | `sim/quan` (`Cuubeo`) | `chonoi/sim/gather.py`, `docs/contracts/`, gắn tag `phase-1..4` & `v1.0.0` |
| Bùi Phước Anh | `Cuubeo` | `sim/quan` | **PO** | `sim/gather` (`Do-Hong-Vy`) | `chonoi/sim/quan.py`, `docs/clarify.md`, đọc & chốt AC từng phase từ Lab Board |
| Đinh Hoàng Phong | `Phog2811` | `client/ui` | **Scrum / Release** | `qa` (`Nguyenquoctoan0310`) | `chonoi/web/index.html` (UI/HUD/âm thanh/sáng tạo), `docs/standup.md`, `CHANGELOG.md`, `CREDITS.md`, Demo |
| Nguyễn Quốc Toàn | `Nguyenquoctoan0310` | `qa` | **QA Lead** | `client/ui` (`Phog2811`) | `tests/`, `chonoi/scenario.py`, `chonoi/contract.py`, `docs/verification/`, `docs/proof/` |

> **Việc cần làm ngay ở CP0:** Xác nhận bảng vai trò & người dự phòng trên, điền hoàn chỉnh cột `Vai quy trình`, `Người dự phòng cho`, và mục `Thỏa thuận làm việc nhóm (≤ 10 dòng)` trong [`TEAM.md`](TEAM.md), đồng thời sửa `"team": "ForkMe"` trong [`game.contract.json`](game.contract.json).

---

## 2. Ma trận bám tiêu chí chấm điểm (100 điểm — không bỏ sót)

| Hạng mục | Điểm | Tiêu chí chấm cụ thể | Đầu ra / Bằng chứng bắt buộc | Người chịu trách nhiệm chính |
|---|---:|---|---|---|
| **1. Test tự động ẩn** | **25** | Headless chạy đúng `headless_cmd`; exit code `0/1/2` (lỗi input/mâu thuẫn thoát `2` *trước* khi ghi file); cùng `--seed` ra JSONL giống từng byte (`Streams`, `sort_by_id`, `IdAllocator`, không dùng `random`/clock); số liệu chỉ đọc từ `game.contract.json`; tính năng sáng tạo **tắt ở headless**; **qua cả regression phase trước**. | `chonoi/sim/gather.py`, `chonoi/sim/quan.py`, `chonoi/scenario.py`, `chonoi/contract.py`, `game.contract.json`, `tests/` | `Do-Hong-Vy`, `Cuubeo`, `Nguyenquoctoan0310` |
| **2. Làm việc nhóm** | **25** | Repo public `K5-L3B-LAB-Day12-AI-SDLC-ForkMe`; đủ 4 collaborator quyền Write; [`TEAM.md`](TEAM.md) hợp lệ (`tools/check_team.py` pass) & khớp `game.contract.json`; **mỗi người ≥ 3 commit có nội dung** bằng đúng GitHub account (pair ghi `Co-authored-by:`); chia việc rõ, tích hợp mượt, xử lý **đổi yêu cầu** (Change Request); gắn đúng 4 tag `phase-1..4` đúng hạn trên commit chạy được; có review code chéo. | Git history + Tags (`phase-1..4`, `v1.0.0`), `TEAM.md`, `docs/contracts/`, `docs/plan/phase-n.md`, `docs/standup.md`, `docs/clarify.md`, `docs/adr/`, PR/review | **All** (Integrator: `Do-Hong-Vy`, PO: `Cuubeo`) |
| **3. Kiểm chứng & bằng chứng** | **15** | Ma trận truy vết `AC → cách kiểm chứng → đường dẫn bằng chứng → kết quả trung thực`; bằng chứng thật (log test, output JSONL, screenshot UI); test unit + integration + regression do nhóm tự viết; không sửa test cho xanh khi luật sai (nếu sửa test phải ghi rõ lý do trong commit). | `docs/verification/phase-1..4.md`, `docs/proof/phase-1..4/*`, `tests/test_*.py` | `Nguyenquoctoan0310` (chủ trì), **All** (cung cấp proof phần mình) |
| **4. Harness AI** | **10** | [`AGENTS.md`](AGENTS.md) được **cập nhật qua từng phase** (lịch sử git phải thấy tiến hóa); nhóm **tự viết tối thiểu 2 skill / hook / command** đặt ở `.agents/skills/` (hoặc tương đương) và ghi tên + khi nào dùng vào `AGENTS.md`; nhật ký AI đầy đủ theo phase & theo người. | `AGENTS.md`, `.agents/skills/*`, `docs/ai-usage-log.md` | `Do-Hong-Vy`, `Nguyenquoctoan0310` (setup harness), **All** (log AI) |
| **5. Đánh giá & retro** | **10** | `docs/retro.md` có cả **Phase 2 (nhanh)** và **Phase 4 (cuối)** (rà hành động P2, số commit/người, cách đọc code, token/người, 1 lần AI sai & cách phát hiện, bài học); mỗi thành viên có file phản tư `≤ 200 từ` kèm link commit & link review. | `docs/retro.md`, `docs/members/Do-Hong-Vy.md`, `Cuubeo.md`, `Phog2811.md`, `Nguyenquoctoan0310.md` | `Phog2811` (chủ trì retro), **All** (viết `members/<handle>.md`) |
| **6. Chất lượng sản phẩm** | **10** | Hoàn thiện lõi đúng PRD-0 và các phase sau; UI/HUD/đồ họa/âm thanh hoàn chỉnh thay hình khối tạm; phần mở rộng/sáng tạo tuân 3 điều kiện (không phá lõi & tắt ở headless, ghi mục **"Sáng tạo của nhóm"** trong `README.md`, làm lõi đúng trước); asset ngoài đúng license CC0/CC-BY/MIT & ghi nguồn; không commit key/token/`.env`. | `chonoi/web/`, `README.md`, `CREDITS.md`, `CHANGELOG.md` | `Phog2811` (UI & sáng tạo), **All** |
| **7. Demo** | **5** | Bản live chạy ổn định tại tag `phase-4` / Release `v1.0.0`; trình bày mạch lạc luồng chơi (`gather` → kho → `quan` → `day`/sáng tạo) + chứng minh headless deterministic. | Release `v1.0.0`, kịch bản demo 2–3 phút | `Phog2811` + **All** |

---

## 3. Hiện trạng repo & Rủi ro kỹ thuật cần xử lý ngay

Kết quả kiểm tra repo trước khi bắt đầu:
1. **`TEAM.md` đang sửa dở (unstaged):** Đã điền 4 thành viên (`Do-Hong-Vy`, `Cuubeo`, `Phog2811`, `Nguyenquoctoan0310`), **chưa điền** `Vai quy trình`, `Người dự phòng cho`, và `Thỏa thuận làm việc nhóm`.
2. **`game.contract.json`:** Trường `"team"` vẫn là `"ten-nhom"` → cần đổi thành `"ForkMe"` (giữ `"team_size": 4`).
3. **Xung đột ở `tests/test_team_check.py`:** Hàm `test_template_is_rejected` hiện đọc trực tiếp `TEAM.md` và bắt buộc `TEAM.md` phải chưa hợp lệ. Ngay khi điền đủ `TEAM.md`, unit test này **FAIL**.
   - *Cách xử lý:* Cập nhật `test_template_is_rejected` để test chuỗi template mẫu (hoặc kiểm tra `TEAM.md` phải **pass** `check_team.validate` trên repo nhóm), và **ghi rõ lý do sửa test trong commit** theo quy tắc `AGENTS.md`.
4. **Môi trường Windows vs Linux CI (`python3`):** `game.contract.json` khai `"headless_cmd": "python3 -m chonoi.headless"`. Trên máy Windows có Windows Store alias, `python3` trong `subprocess` có thể báo `OSError: [WinError 1920]`, trong khi `python` chạy bình thường và CI (`ubuntu-latest`) dùng `python3`.
   - *Cách xử lý:* Kiểm tra ngay trên máy từng thành viên; **không tự ý đổi `headless_cmd`** làm hỏng môi trường chấm Linux nếu máy chấm chỉ có `python3` (hoặc kiểm chứng trước xem máy chấm/CI chấp nhận `python` không). Khi chạy test local trên Windows, đảm bảo `python` hoạt động hoặc tạo virtualenv / alias hợp lệ.

---

## 4. Chia Task chi tiết theo Checkpoints (CP)

---

### CP0 — Kickoff & Thiết lập nền tảng (0:00 – 0:15)

> **Mục tiêu:** Chốt toàn bộ nền tảng nhóm, hợp đồng tích hợp, harness AI và môi trường chạy test xanh trước khi code luật Phase 1.

- [x] **CP0-1 (`Do-Hong-Vy` — Integrator):** Kiểm tra repo GitHub `K5-L3B-LAB-Day12-AI-SDLC-ForkMe` đã ở chế độ **Public** (`private: false`) và đã thêm đủ 4 collaborator có quyền Push/Write (`Do-Hong-Vy`, `Cuubeo`, `Phog2811`, `nguyenquoctoan0310`). *(Nhắc 4 người tự kiểm tra `git config user.name/email` khớp tài khoản GitHub).*
- [x] **CP0-2 (`Do-Hong-Vy` khởi tạo bản đầy đủ — chờ cả nhóm xác nhận nhanh):** Điền hoàn chỉnh [`TEAM.md`](TEAM.md) (đủ `Vai quy trình`, `Người dự phòng cho`, `Thỏa thuận làm việc nhóm ≤ 10 dòng` không còn dấu `…`). *(Cả nhóm đọc lướt và chỉnh lại nếu cần trước khi commit).*
- [x] **CP0-3 (`Do-Hong-Vy`):** Cập nhật `"team": "ForkMe"` trong [`game.contract.json`](game.contract.json) và chạy `python tools/check_team.py` xác nhận `OK: 4 thành viên`.
- [x] **CP0-4 (`Cuubeo` — PO — plan + clarify xong; chờ PRD-0 mở để trích AC):** Mở Lab Board (**Chợ Nổi Lab**), lấy toàn bộ yêu cầu **Phase 1 (PRD-0)** và danh sách AC (`AC-P1-??`). Giải đáp các mục đang chờ trong [`docs/clarify.md`](docs/clarify.md) và điền [`docs/plan/phase-1.md`](docs/plan/phase-1.md) (`≤ 1 trang`: mục tiêu, việc/người/phụ thuộc, rủi ro).
- [x] **CP0-5 (`Do-Hong-Vy` khởi tạo — chờ `Cuubeo` & `Phog2811` xác nhận/bổ sung theo PRD-0):** Chốt **Hợp đồng tích hợp** trong [`docs/contracts/`](docs/contracts/README.md):
  - Xác nhận schema file kho ([`docs/contracts/inventory.sample.json`](docs/contracts/inventory.sample.json): `{"items": {"bong_sung": 2, "ca_loc": 1}}`).
  - Tạo [`docs/contracts/sim-ui-interface.md`](docs/contracts/sim-ui-interface.md) khóa cấu trúc `snapshot()` & `/state`, `/input`, `/restart`.
  - Tạo [`docs/contracts/events.md`](docs/contracts/events.md) liệt kê các sự kiện `gather` & `quan` (đánh dấu rõ các payload `[Chờ PO đối chiếu PRD-0]` trong [`docs/clarify.md`](docs/clarify.md)).
- [ ] **CP0-6 (`Nguyenquoctoan0310` — QA):** Sửa lỗi môi trường chạy test local (Windows `python` vs `python3`), xử lý `test_template_is_rejected` trong [`tests/test_team_check.py`](tests/test_team_check.py) (ghi rõ lý do trong commit), xác nhận chạy xanh toàn bộ test suite hiện có (32 tests).
- [ ] **CP0-7 (`Do-Hong-Vy` xong Skill 1; chờ `Nguyenquoctoan0310` làm Skill 2 — Harness AI):**
  - [x] **Skill 1 (`Do-Hong-Vy`):** Tạo [`.agents/skills/check-contract/SKILL.md`](.agents/skills/check-contract/SKILL.md) và cập nhật [`AGENTS.md`](AGENTS.md) (lần 1).
  - [ ] **Skill 2 (`Nguyenquoctoan0310`):** Tạo skill QA kiểm chứng AC / sinh bằng chứng `docs/verification/` & `docs/proof/` trong `.agents/skills/` và bổ sung vào [`AGENTS.md`](AGENTS.md).

---

### CP1 — Phase 1: Lõi `gather` + `quan` + Kho v1.0 (0:00 – 1:00 | Hạn tag `phase-1`: trước 1:00)

> **Mục tiêu:** Hoàn thiện toàn bộ luật chơi Phase 1 cho `gather` và `quan`, validation `scenario`/`contract`, giao diện chơi thử nâng cấp v1.0, pass toàn bộ smoke test + unit/integration test tự viết, xuất bằng chứng và gắn tag `phase-1`.

#### A. `Do-Hong-Vy` (`sim/gather` — [`chonoi/sim/gather.py`](chonoi/sim/gather.py))
- [ ] **CP1-G1 (Lát 1 — Bơi, phân vùng, oxy, ngạt, ngất, giỏ LIFO):**
  - Theo dõi trạng thái mặt nước/dưới nước đầu bước vs cuối bước (`d <= surface_depth`) → phát event `dive` / `surface` với `data` chứa `pos` (đối chiếu chính xác schema `data` trong PRD-0).
  - Cập nhật oxy theo `d` **cuối bước**: ở mặt nước hồi `oxygen_refill_per_tick`, dưới nước trừ `1` tick/tick, kẹp `[0, oxygen_max_ticks]`.
  - Phát `oxygen_empty` khi `oxygen_ticks` chuyển từ dương xuống `0`.
  - Khi `oxygen_ticks == 0` và đang dưới nước: tăng `zero_oxy_ticks`; đủ `choke_interval_ticks` thì trừ `1` HP, reset bộ đếm ngạt và phát `choke`.
  - Khi `hp <= 0`: phát `faint`, xóa sạch giỏ (`self.hold.clear()`), gọi `_finish("fainted", events)` (đảm bảo `gather_end` với `reason: "fainted"` và kho rỗng `{}`), và `return events`.
  - Quản lý giỏ `self.hold` theo thứ tự nhặt (LIFO, tối đa `hold_capacity`, không hard-code `12`).
- [ ] **CP1-G2 (Lát 2 — Hái nút, bắt cá, cập bến, xuất kho):**
  - Trong `interact`: giữ logic kiểm tra `_in_dock()` **TRƯỚC** hái nút (`docked` → `gather_end`).
  - Nếu không ở bến và đang ở mặt nước (`_at_surface()`): tìm nút `ready` (`regrow_ticks == 0`) gần nhất trong `interact_radius` (tie-break theo `id_key` nhỏ nhất); nếu giỏ còn chỗ thêm vào `hold`, đặt `regrow_ticks = round(regrow_s * 60)`, phát `gather`; nếu giỏ đầy phát `hold_full` (kiểm tra cơ chế một phần hay toàn phần khi thêm từ `node_yield` theo PRD-0!).
  - Trong `catch`: chỉ thực hiện khi `catch_cd_ticks == 0` và đang dưới nước (`not _at_surface()`): tìm đàn cá gần nhất trong `catch_radius` (tie-break `id_key`), kiểm tra sức chứa giỏ với `fish_yield[kind]`, xử lý `fish_caught` / `hold_full`, đặt `catch_cd_ticks = round(catch_cooldown_s * 60)`, xử lý đàn cá sau khi bắt (biến mất hay respawn — kiểm tra kỹ PRD-0!).
- [ ] **CP1-G3 (Tích hợp & Tag P1):** Đọc review/PR cho `Cuubeo`, gộp các lát vào `main` sạch sẽ, kiểm tra mọi số liệu đều đọc từ `tuning`, chạy test và gắn tag `phase-1` trước `1:00`.

#### B. `Cuubeo` (`sim/quan` — [`chonoi/sim/quan.py`](chonoi/sim/quan.py) + PO)
- [ ] **CP1-Q1 (Lát 3 — Khách, chọn món, giữ chỗ, kiên nhẫn, bỏ đi):**
  - Dựng khách có sẵn từ `scenario["customers"]` và suy ra/kiểm tra `reserved` (nguyên liệu giữ chỗ).
  - Sinh khách mới theo lịch (`first_customer_tick`, sau đó mỗi `customer_interval_s * 60` ticks) nếu còn bàn trống (chọn bàn & chọn món bằng `Streams` trong `self.rng`, tuyệt đối không dùng `random` toàn cục).
  - Khách chọn món nấu được dựa trên `stock - tổng reserved` và `menu`: nếu có món nấu được → giữ chỗ nguyên liệu vào `reserved` của khách; nếu không có món nào đủ nguyên liệu → phát `no_dish` (khách không ngồi/bỏ đi — đối chiếu PRD-0).
  - Giảm `patience_ticks_left` của khách đang chờ theo từng tick; khi về `0` → giải phóng `reserved`, xóa khách khỏi bàn, cộng/trừ uy tín theo `left_reputation_delta` (kẹp `[reputation_min, reputation_max]`), phát `customer_left`.
- [ ] **CP1-Q2 (Lát 4 — Bếp, bưng món, phục vụ, ăn, trả tiền, boa, uy tín, hết ca):**
  - Ở `interact`: tối đa **1 tương tác/bước**, chọn đối tượng hợp lệ trong `interact_radius` theo thứ tự ưu tiên `(khoảng cách, bếp trước bàn, id_key)`:
    - Tại **bếp (`idle`)**: nếu tay đang rỗng (`hand is None`) và có khách đang chờ món chưa có ai nấu (hoặc món hợp lệ theo PRD-0), bắt đầu nấu → chuyển bếp sang `cooking`, đặt `cook_ticks_left`, trừ nguyên liệu khỏi `stock` (và giải phóng phần `reserved` tương ứng), phát `cook_started`.
    - Bếp đếm ngược `cook_ticks_left` mỗi bước; về `0` → chuyển `ready`, phát `dish_ready`.
    - Tại **bếp (`ready`)**: nếu tay đang rỗng (`hand is None`) → nhặt món lên `self.hand`, đưa bếp về `idle`, phát `dish_picked`.
    - Tại **bàn có khách đang chờ đúng món trên tay**: đặt món phục vụ khách → chuyển khách sang `eating` với `eat_ticks_left = round(eat_s * 60)`, xóa `self.hand`, phát `served`.
  - Đếm ngược `eat_ticks_left` của khách `eating`; về `0` → tính tiền món (`price`) + tiền boa (`round(price * tip_rate)` nếu tỉ lệ kiên nhẫn còn lại `>= tip_min_patience_ratio`), cộng `money`, `earned`, `shift_earned`, cộng `tip_reputation` nếu có boa (kẹp `[reputation_min, reputation_max]`), phát `paid`, giải phóng bàn.
  - Hết giờ: phát `quan_end` đúng schema.
- [ ] **CP1-Q3 (PO):** Cập nhật [`docs/clarify.md`](docs/clarify.md) với mọi thắc mắc đã hỏi giảng viên/giả định của nhóm. Review code cho `Do-Hong-Vy`.

#### C. `Phog2811` (`client/ui` — [`chonoi/web/index.html`](chonoi/web/index.html) / UI của nhóm)
- [ ] **CP1-U1 (Nâng cấp UI/HUD Gather & Quán v1.0):**
  - Đảm bảo giao diện đọc hoàn toàn từ snapshot `GET /state` và gửi điều khiển qua `POST /input`, `POST /restart` (không phá tương thích `tests/test_live.py`!).
  - Nâng cấp đồ họa/HUD buổi sáng (`gather`): hiển thị rõ thuyền/Út Sen, thanh Oxy (cảnh báo khi thấp), Tim HP, trạng thái đang ngạt (`zero_oxy_ticks`), cooldown bắt cá, giỏ LIFO trực quan, các nút hái (`bong_dien_dien`, `bong_sung` + đếm ngược mọc lại), đàn cá (`ca_linh`, `ca_loc`), vùng bến (`E`).
  - Nâng cấp đồ họa/HUD buổi tối (`quan`): hiển thị rõ bếp (`idle`/`cooking`/`ready` + tiến độ nấu), món đang cầm trên tay, bàn + khách + món gọi + thanh kiên nhẫn + trạng thái `eating`, kho nguyên liệu, Tiền, Uy tín (sao), Điểm, log sự kiện dễ đọc.
- [ ] **CP1-U2 (Trải nghiệm & Luật chơi tại chỗ):** Thêm bảng hướng dẫn/menu công thức nấu ăn ngay trên HUD để người chơi biết món cần nguyên liệu gì; bổ sung màn hình tổng kết cuối ca rõ ràng (số món, tiền, uy tín, phím `R` chơi lại).
- [ ] **CP1-U3 (Scrum):** Nhắc cả nhóm cập nhật [`docs/standup.md`](docs/standup.md) giữa Phase 1 và kiểm tra tiến độ trước mốc `0:50`.

#### D. `Nguyenquoctoan0310` (`qa` — Validation, Tests & Verification Phase 1)
- [ ] **CP1-T1 (Validation mức luật — mã thoát 2):**
  - Hoàn thiện `TODO(nhóm)` trong [`chonoi/scenario.py`](chonoi/scenario.py): kiểm tra mâu thuẫn mức luật (ví dụ: tổng `reserved` của các khách vượt `stock`, khách `assigned`/`waiting`/`eating` sai định dạng món không có trong `menu`, thiếu giá/tip khi đang `eating`, bàn/bếp trùng hoặc không hợp lệ...) → ném `BadInput` để thoát mã `2` *trước* khi ghi file.
  - Rà soát [`chonoi/contract.py`](chonoi/contract.py): bổ sung validate các khóa `quan` còn thiếu (`stoves`, `tables`, `reputation_initial/min/max`, `start_pos`, `menu` recipes chỉ dùng nguyên liệu hợp lệ).
- [ ] **CP1-T2 (Bộ test Phase 1 — `tests/test_phase1_rules.py`):**
  - Test `gather`: phân vùng `dive`/`surface`, tiêu hao & hồi oxy, `oxygen_empty` → `choke` → `faint` (mất sạch giỏ, kho rỗng), hái nút + mọc lại + tie-break id, bắt cá + cooldown + chỉ dưới nước, đầy giỏ `hold_full`, cập bến ở tick khác 0.
  - Test `quan`: đọc kho từ `gather`, lịch khách, chọn món theo `stock`, giữ chỗ nguyên liệu, khách bỏ đi giải phóng `reserved` & giảm uy tín, `no_dish`, nấu ăn, ưu tiên tương tác `(khoảng cách, bếp trước bàn, id)`, phục vụ, ăn xong trả tiền + boa + tăng uy tín, `quan_end`.
  - Test **Determinism**: chạy headless 2 lần cùng seed & cùng inputs cho cả `gather` và `quan` → so sánh byte-by-byte giống hệt nhau.
- [ ] **CP1-T3 (Bằng chứng & Ma trận truy vết P1):**
  - Lưu log chạy test và output JSONL mẫu vào `docs/proof/phase-1/` (ví dụ `unittest.txt`, `gather_sample.jsonl`, `quan_sample.jsonl`, ảnh chụp live UI từ `Phog2811`).
  - Điền đầy đủ [`docs/verification/phase-1.md`](docs/verification/phase-1.md) (trung thực trạng thái Đạt / Chưa đạt của từng AC).

#### E. Checklist đóng CP1 (trước `1:00`)
- [ ] Toàn bộ unit test + smoke test + test Phase 1 xanh (`python -m unittest discover -s tests -v`), `python tools/check_team.py` đạt `OK`.
- [ ] Cả 4 thành viên đều đã có ít nhất **1 commit** có nội dung bằng tài khoản GitHub thật.
- [ ] [`docs/ai-usage-log.md`](docs/ai-usage-log.md) đã ghi đủ log Phase 1 cho cả 4 người.
- [ ] [`docs/standup.md`](docs/standup.md) đã cập nhật dòng Phase 1 cho cả 4 người.
- [ ] Push `main` lên `origin`, gắn tag `phase-1` và `git push origin phase-1` trước **1:00**.

---

### CP2 — Phase 2: Mở rộng & Đổi yêu cầu đợt 1 (1:00 – 1:55 | Hạn tag `phase-2`: trước 1:55)

> **Lưu ý:** Yêu cầu cụ thể của Phase 2 mở trên Lab Board lúc **1:00** (thường bổ sung hành vi/sinh vật/cơ chế mới hoặc đổi yêu cầu từ Phase 1 — ví dụ trong khung đã để chỗ cho cá bơi/sinh thêm, cơ chế mới, nút mới, `burn_s`, v.v.). Chỉ triển khai đúng theo đề Lab Board công bố lúc 1:00.

- [ ] **CP2-0 (PO `Cuubeo` + Integrator `Do-Hong-Vy`, 1:00 – 1:08):**
  - Đọc đề Phase 2 trên Lab Board, tách toàn bộ AC (`AC-P2-??`) vào `docs/plan/phase-2.md` (`≤ 1 trang`).
  - Ghi mọi câu hỏi/đổi yêu cầu vào [`docs/clarify.md`](docs/clarify.md).
  - Nếu có thay đổi `game.contract.json`, schema snapshot/event/inventory hoặc quy tắc sẵn có: tạo **ADR** trong `docs/adr/0001-<tieu-de>.md` (theo `0000-template.md`, có bảng tác động module/file/test) và thông báo cả nhóm trước khi code.
- [ ] **CP2-1 (`All` — Standup nhanh):** Điền dòng Phase 2 trong [`docs/standup.md`](docs/standup.md).
- [ ] **CP2-2 (`Do-Hong-Vy` — `sim/gather`):** Triển khai các lát tính năng/đổi yêu cầu Phase 2 thuộc buổi sáng (`gather`) — giữ nguyên quy tắc `Streams` tách luồng (`rng.get("<ten_luong>")`) để không làm lệch RNG cũ; đọc mọi tham số mới từ `game.contract.json`.
- [ ] **CP2-3 (`Cuubeo` — `sim/quan`):** Triển khai các lát tính năng/đổi yêu cầu Phase 2 thuộc buổi tối (`quan`) hoặc ghép ca/chế độ mới theo đề Phase 2.
- [ ] **CP2-4 (`Phog2811` — `client/ui`):** Cập nhật UI/HUD hiển thị đầy đủ các thực thể/trạng thái/nút bấm/cơ chế mới của Phase 2; trau chuốt hình ảnh thay thế hình khối tạm (đảm bảo mọi hiệu ứng thêm chỉ chạy phía client/live, không chạm vào output headless).
- [ ] **CP2-5 (`Nguyenquoctoan0310` — `qa`):**
  - Cập nhật validation mới trong `contract.py` / `scenario.py` / `inputs.py` (nếu contract nâng cấp).
  - Viết bộ test Phase 2 (`tests/test_phase2_*.py`) + **chạy lại toàn bộ test Phase 1 (regression)**.
  - Xuất bằng chứng vào `docs/proof/phase-2/` và hoàn thiện `docs/verification/phase-2.md`.
- [ ] **CP2-6 (`Phog2811` + `All` — Retro nhanh Phase 2, ~1:45):**
  - Điền mục **Phase 2 (nhanh)** trong [`docs/retro.md`](docs/retro.md): *Điều tốt*, *Điều tệ*, *1 hành động cụ thể cho Phase 3*.
- [ ] **CP2-7 (`Do-Hong-Vy` + `All` — Harness & Tag P2):**
  - Cập nhật [`AGENTS.md`](AGENTS.md) với quy tắc/bẫy mới phát hiện ở Phase 1–2 (tạo diff rõ trong git history).
  - Cập nhật [`docs/ai-usage-log.md`](docs/ai-usage-log.md) cho cả 4 người (Phase 2).
  - Kiểm tra mọi người đã có `≥ 2` commit tích lũy; chạy full test xanh; gắn tag `phase-2` và push trước **1:55**.

---

### CP3 — Phase 3: Mở rộng & Tích hợp hoàn chỉnh (1:55 – 2:30 | Hạn tag `phase-3`: trước 2:30)

> **Mục tiêu:** Đáp ứng toàn bộ yêu cầu Phase 3 mở lúc 1:55 (ví dụ chế độ nối ngày `--mode day` / nâng cấp gameplay / cân bằng hệ thống theo đề), thực thi hành động cải tiến từ Retro P2, giữ regression P1+P2 xanh.

- [ ] **CP3-0 (PO `Cuubeo`, 1:55 – 2:00):** Đọc đề Phase 3, cập nhật [`docs/clarify.md`](docs/clarify.md) & tạo `docs/plan/phase-3.md`; lập ADR (`docs/adr/0002-...md`) nếu đổi contract/schema.
- [ ] **CP3-1 (`All` — Thực thi hành động Retro P2 & Standup):** Áp dụng ngay 1 hành động đã cam kết ở Retro Phase 2; điền dòng Phase 3 trong [`docs/standup.md`](docs/standup.md).
- [ ] **CP3-2 (`Do-Hong-Vy` & `Cuubeo` — Core Sim & Tích hợp):**
  - Triển khai các thay đổi/tính năng Phase 3 trên `sim/gather`, `sim/quan`, và `sim/day` / `runner` (nếu Phase 3 mở khóa `--mode day` hoặc luồng chuyển sáng→tối).
  - Rà soát độ ổn định deterministic: chạy kiểm tra cùng seed với mọi chế độ.
- [ ] **CP3-3 (`Phog2811` — `client/ui` + Chuẩn bị Sáng tạo):**
  - Hoàn thiện UI cho các tính năng Phase 3 (menu, chuyển cảnh sáng-tối, hiệu ứng phản hồi, âm thanh Web Audio API tự tạo hoặc asset CC0/MIT).
  - Bắt đầu phần **Sáng tạo của nhóm** (chỉ khi lõi Phase 3 chạy đúng): giữ tuyệt đối nguyên tắc **tắt ở headless**.
- [ ] **CP3-4 (`Nguyenquoctoan0310` — `qa`):**
  - Viết test Phase 3 (`tests/test_phase3_*.py`) + **regression toàn bộ Phase 1 & Phase 2**.
  - Lưu log/output vào `docs/proof/phase-3/` và hoàn thiện `docs/verification/phase-3.md`.
- [ ] **CP3-5 (`All` — Harness & Tag P3):**
  - Cập nhật [`AGENTS.md`](AGENTS.md) (nếu có skill/hook hoặc rule mới cho Phase 3) & [`docs/ai-usage-log.md`](docs/ai-usage-log.md) (Phase 3).
  - Chạy full test xanh; đảm bảo mỗi thành viên có **≥ 3 commit có nội dung** (hoặc hoàn tất ở đầu CP4); gắn tag `phase-3` và push trước **2:30**.

---

### CP4 — Phase 4: Hoàn thiện, Sáng tạo, Retro cuối, Release `v1.0.0` & Demo (2:30 – 3:00 | Hạn tag `phase-4` + Release `v1.0.0`: trước 3:00)

> **Mục tiêu:** Đóng toàn bộ yêu cầu Phase 4, hoàn thiện sản phẩm sáng tạo, khóa bằng chứng 100 điểm, hoàn thành retro cá nhân & nhóm, gắn tag `phase-4` + Release `v1.0.0`, sẵn sàng Demo.

- [ ] **CP4-1 (Xử lý yêu cầu Phase 4 — 2:30 – 2:42):**
  - PO `Cuubeo` đọc đề Phase 4 trên Lab Board → cập nhật `docs/plan/phase-4.md`, [`docs/clarify.md`](docs/clarify.md).
  - `Do-Hong-Vy` & `Cuubeo` xử lý nốt phần sim / edge cases / cân bằng tham số (nếu Phase 4 yêu cầu).
  - `Phog2811` chốt hoàn thiện UI/đồ họa/âm thanh và phần **Sáng tạo của nhóm** (đảm bảo **tắt khi chạy headless**!).
- [ ] **CP4-2 (Kiểm chứng cuối cùng — `Nguyenquoctoan0310`):**
  - Chạy lại toàn bộ test suite (`tests/` cho P1 + P2 + P3 + P4) + test kiểm tra sáng tạo tắt ở headless + `python tools/check_team.py`.
  - Kiểm tra không lộ API key, token, `.env` trong toàn bộ commit/repo.
  - Lưu bằng chứng cuối vào `docs/proof/phase-4/` và hoàn thiện `docs/verification/phase-4.md`.
- [ ] **CP4-3 (Hoàn thiện tài liệu sản phẩm & nguồn — `Phog2811` + `Do-Hong-Vy`):**
  - Cập nhật [`README.md`](README.md): bổ sung mục **"Sáng tạo của nhóm"** (liệt kê rõ phần thêm, cách chơi/trải nghiệm, và xác nhận đã tắt ở headless).
  - Cập nhật [`CREDITS.md`](CREDITS.md): liệt kê tất cả asset ngoài (CC0/CC-BY/MIT hoặc tự tạo) và công cụ AI đã dùng.
  - Cập nhật [`CHANGELOG.md`](CHANGELOG.md): ghi tóm tắt các thay đổi từ `phase-1` đến `v1.0.0`.
- [ ] **CP4-4 (Retro cuối & Phản tư cá nhân — `All`, 2:42 – 2:52):**
  - Hoàn thiện mục **Phase 4 (cuối)** trong [`docs/retro.md`](docs/retro.md):
    - Rà lại hành động Phase 2 (đã làm chưa? vì sao?).
    - Điều tốt / điều tệ cả 4 phase.
    - Số liệu thật: số commit theo người (`git shortlog -sn`), cách nhóm đọc code của nhau, token/chi phí theo người (từ `docs/ai-usage-log.md`).
    - Một lần AI sai cụ thể và cách nhóm phát hiện.
    - Nếu làm lại, đổi gì.
  - Mỗi thành viên viết file phản tư cá nhân (`≤ 200 từ`, đủ 4 gạch đầu dòng kèm link commit & link review thật):
    - [ ] `docs/members/Do-Hong-Vy.md`
    - [ ] `docs/members/Cuubeo.md`
    - [ ] `docs/members/Phog2811.md`
    - [ ] `docs/members/Nguyenquoctoan0310.md`
  - Chốt dòng Phase 4 trong [`docs/ai-usage-log.md`](docs/ai-usage-log.md) & [`docs/standup.md`](docs/standup.md) + cập nhật lần cuối [`AGENTS.md`](AGENTS.md).
- [ ] **CP4-5 (Kiểm tra commit & Release — `Do-Hong-Vy`):**
  - Xác nhận mỗi người có **≥ 3 commit có nội dung** bằng đúng handle trong `TEAM.md` (`git log --format="%h %an <%ae> %s"`).
  - Gắn tag `phase-4` và tag `v1.0.0` trên commit sạch cuối cùng đã pass mọi test, push lên `origin`, tạo GitHub Release `v1.0.0` trước **3:00**.
- [ ] **CP4-6 (Chuẩn bị Demo 5 điểm — `Phog2811` + `All`):**
  - Mở sẵn game bằng `run_cmd` (`python -m chonoi.live ...`), kiểm tra chơi mượt không lỗi console/terminal.
  - Chạy thử kịch bản Demo 2–3 phút:
    1. Bắt đầu ngày: `gather` (lặn, oxy, bắt cá, hái rau, cập bến giữ giỏ).
    2. Chuyển ca: `quan` (nấu món từ kho vừa kiếm, phục vụ khách, boa & uy tín).
    3. Trình diễn tính năng Phase 2–4 & **Sáng tạo của nhóm** trên UI.
    4. Chứng minh 1 lệnh `headless` chạy ra kết quả deterministic, cùng test suite xanh.

---

## 5. Checklist đầu ra theo từng thành viên (Kiểm tra nhanh trước khi nộp)

| Thành viên | Commit tối thiểu | Code / Test phụ trách | Docs cá nhân & chung phải có tên mình |
|---|---|---|---|
| **Đỗ Hồng Vỹ** (`Do-Hong-Vy`) | ≥ 3 commit nội dung | `sim/gather`, `docs/contracts/`, gắn tag `phase-1..4` & `v1.0.0`, skills/AGENTS | `docs/members/Do-Hong-Vy.md`, dòng trong `ai-usage-log.md` & `standup.md`, review cho `Cuubeo` |
| **Bùi Phước Anh** (`Cuubeo`) | ≥ 3 commit nội dung | `sim/quan`, quản lý AC & Change Request | `docs/clarify.md`, `docs/plan/phase-1..4.md`, `docs/members/Cuubeo.md`, dòng trong `ai-usage-log.md` & `standup.md`, review cho `Do-Hong-Vy` |
| **Đinh Hoàng Phong** (`Phog2811`) | ≥ 3 commit nội dung | `client/ui`, đồ họa/HUD/âm thanh, phần Sáng tạo của nhóm, Demo | `docs/standup.md`, `docs/retro.md`, `README.md` ("Sáng tạo của nhóm"), `CREDITS.md`, `CHANGELOG.md`, `docs/members/Phog2811.md`, dòng trong `ai-usage-log.md` |
| **Nguyễn Quốc Toàn** (`Nguyenquoctoan0310`) | ≥ 3 commit nội dung | `scenario.py`, `contract.py`, `tests/` (unit + integration + regression), skills verify | `docs/verification/phase-1..4.md`, `docs/proof/phase-1..4/*`, `docs/members/Nguyenquoctoan0310.md`, dòng trong `ai-usage-log.md` & `standup.md` |
