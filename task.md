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

Kết quả rà soát sau các commit CP0 (`f4fa4aa`):
1. **CP0 đã hoàn thiện 100% (`CP0-1` .. `CP0-7`):** [`TEAM.md`](TEAM.md), [`game.contract.json`](game.contract.json) (`"team": "ForkMe"`), [`tests/test_team_check.py`](tests/test_team_check.py) (5/5 pass), [`AGENTS.md`](AGENTS.md), 2 skills ([`check-contract`](.agents/skills/check-contract/SKILL.md) & [`verify-phase`](.agents/skills/verify-phase/SKILL.md)), [`docs/prd0.md`](docs/prd0.md), [`docs/plan/phase-1.md`](docs/plan/phase-1.md) (`AC-P1-01..16`), [`docs/clarify.md`](docs/clarify.md) (`#1–#9` đã chốt), và [`docs/ai-usage-log.md`](docs/ai-usage-log.md) (đủ 4 thành viên) đã có trên `main`.
2. **Hợp đồng `docs/contracts/` đã đối chiếu PRD-0:** PO (`Cuubeo`) đã đối chiếu khớp mục D/E/G trong [`docs/prd0.md`](docs/prd0.md) (`f4fa4aa`) — mọi payload sự kiện ở [`events.md`](docs/contracts/events.md) và snapshot ở [`sim-ui-interface.md`](docs/contracts/sim-ui-interface.md) đã chuyển trạng thái **Đã chốt**.
3. **Điểm lệch cần sửa ngay đầu CP1 (`clarify #9`):** Khung starter `QuanSim.snapshot()` mới chỉ có `player.pos`, nhưng PRD-0 mục D yêu cầu `quan.player` có `{pos, vel}` → `Cuubeo` bổ sung `vel` vào `QuanSim.snapshot()` ở `CP1-Q2` (`AC-P1-11`).
4. **Môi trường test Windows local & CI:**
   - Đã kiểm chứng toàn bộ **33/33 tests PASS** (`32/32` với `test_team_check` + `test_python_starter_units` + `test_smoke_p1` qua venv shim `python3.exe` tạm, và `1/1` với `test_live` khi cho phép bind socket localhost). Nếu máy Windows của thành viên nào chưa có `python3.exe` trong PATH, làm theo hướng dẫn cục bộ (không commit) trong [`AGENTS.md`](AGENTS.md#L12-L13).
   - GitHub Actions workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) đang ở trạng thái `active` trên repo fork (tùy chọn bật chạy trên web nếu chưa tự kích hoạt).

---

## 4. Chia Task chi tiết theo Checkpoints (CP)

---

### CP0 — Kickoff & Thiết lập nền tảng (0:00 – 0:15)

> **Mục tiêu:** Chốt toàn bộ nền tảng nhóm, hợp đồng tích hợp, harness AI và môi trường chạy test xanh trước khi code luật Phase 1.

- [x] **CP0-1 (`Do-Hong-Vy` — Integrator):** Repo `K5-L3B-LAB-Day12-AI-SDLC-ForkMe` đã ở chế độ **Public** (`private: false`), đủ 4 collaborator có quyền Push/Write, và **cả 4 người đã có commit trên `main`** (`Do-Hong-Vy`, `Phog2811`, `Cuubeo`, `nguyenquoctoan0310`).
- [x] **CP0-2 (`All`):** Hoàn thiện [`TEAM.md`](TEAM.md) (đủ `Vai quy trình`, `Người dự phòng cho`, `Thỏa thuận làm việc nhóm ≤ 10 dòng` không còn `…`), `python tools/check_team.py` đạt `OK: 4 thành viên`.
- [x] **CP0-3 (`Do-Hong-Vy`):** Cập nhật `"team": "ForkMe"`, `"team_size": 4` trong [`game.contract.json`](game.contract.json).
- [x] **CP0-4 (`Cuubeo` — PO):**
  - [x] Điền kế hoạch tổng quan [`docs/plan/phase-1.md`](docs/plan/phase-1.md) và ghi câu hỏi #6–#7 vào [`docs/clarify.md`](docs/clarify.md).
  - [x] *(Phụ thuộc Lab Board — xong, nguồn `docs/prd0.md`)* Trích danh sách `AC-P1-??` chính thức và giải đáp các mục #1–#4, #7 trong [`docs/clarify.md`](docs/clarify.md) ngay khi Lab Board mở `PRD-0`.
- [x] **CP0-5 (`Do-Hong-Vy` + `Cuubeo` + `Phog2811` — Hợp đồng tích hợp):** Đã tạo, đồng bộ và đối chiếu khớp [`docs/prd0.md`](docs/prd0.md) mục D/E/G tại [`docs/contracts/README.md`](docs/contracts/README.md), [`docs/contracts/sim-ui-interface.md`](docs/contracts/sim-ui-interface.md), [`docs/contracts/events.md`](docs/contracts/events.md), [`docs/contracts/inventory.sample.json`](docs/contracts/inventory.sample.json) (`f4fa4aa`).
- [x] **CP0-6 (`Nguyenquoctoan0310` + `Do-Hong-Vy` — Môi trường & Smoke Test):**
  - `Nguyenquoctoan0310` đã sửa `test_template_is_rejected` và thêm `test_repo_team_md_is_valid` trong [`tests/test_team_check.py`](tests/test_team_check.py) (5/5 pass), giữ `python3` trong `game.contract.json` cho CI Linux, bổ sung hướng dẫn fix Windows vào [`AGENTS.md`](AGENTS.md).
  - Đã kiểm chứng trên máy `Do-Hong-Vy` qua shim `python3.exe` tạm + `test_live`: **33/33 tests PASS**. *(Nhắc các bạn dùng Windows tạo `python3.exe` cục bộ không commit nếu máy chưa có sẵn).*
- [x] **CP0-7 (`Do-Hong-Vy` + `Nguyenquoctoan0310` + `All` — Harness AI):**
  - [x] **Skill 1 (`Do-Hong-Vy`):** [`.agents/skills/check-contract/SKILL.md`](.agents/skills/check-contract/SKILL.md) + cập nhật [`AGENTS.md`](AGENTS.md).
  - [x] **Skill 2 (`Nguyenquoctoan0310`):** [`.agents/skills/verify-phase/SKILL.md`](.agents/skills/verify-phase/SKILL.md) + cập nhật [`AGENTS.md`](AGENTS.md).
  - [x] **Nhật ký AI CP0 (`Phog2811`):** Đã bổ sung dòng CP0 của `Phog2811` vào [`docs/ai-usage-log.md`](docs/ai-usage-log.md) (cả 4 thành viên `Do-Hong-Vy`, `Nguyenquoctoan0310`, `Cuubeo`, `Phog2811` đã ghi đủ).

---

### CP1 — Phase 1: Lõi `gather` + `quan` + Kho v1.0 (0:00 – 1:00 | Hạn tag `phase-1`: trước 1:00)

> **Mục tiêu:** Đạt đủ **`AC-P1-01` .. `AC-P1-16`** trong [`docs/plan/phase-1.md`](docs/plan/phase-1.md) theo đúng [`docs/prd0.md`](docs/prd0.md) & [`docs/contracts/`](docs/contracts/README.md), xuất bằng chứng thật và gắn tag `phase-1` trước 1:00.

#### A. `Do-Hong-Vy` (`sim/gather` — [`chonoi/sim/gather.py`](chonoi/sim/gather.py))
- [x] **CP1-G1 (Lát 1 — Bơi, phân vùng, oxy, ngạt, ngất, giỏ LIFO | `AC-P1-01`, `AC-P1-02`):**
  - Bơi `[x,d]` (`ramp_max_ticks`, `Δt=1/60`, chặn biên + triệt vận tốc ra ngoài, `heading_deg` theo `move != 0` gần nhất — đã có phần khung, rà kỹ biên).
  - So đầu/cuối bước (`d <= surface_depth`) → phát `dive` / `surface` với `{"pos": [x, d]}` (pos sau di chuyển).
  - Cập nhật oxy theo `d` **cuối bước**: mặt nước `+oxygen_refill_per_tick` (kẹp max) và **reset `zero_oxy_ticks = 0`**; dưới nước `-1` tick (kẹp 0).
  - Phát `oxygen_empty` (`{"oxygen_ticks": 0}`) khi từ `> 0` xuống `0`.
  - Mỗi bước dưới nước kết thúc với `oxygen_ticks == 0` (**kể cả bước vừa chạm 0**) tăng `zero_oxy_ticks` (`chạm 0 ở t → ngạt lần đầu ở t+59`). Đủ `choke_interval_ticks` → reset về `0`, trừ `1` HP, phát `choke` (`{"hp": self.hp}`).
  - Khi `hp <= 0`: lấy `lost = list(reversed(self.hold))` (LIFO), `self.hold.clear()`, phát `faint` (`{"cause": "choke", "lost": lost, "hp": 0}`), gọi `_finish("fainted", events)` (kho rỗng `{}`), và `return events`.
- [x] **CP1-G2 (Lát 2 — Hái nút, bắt cá, cập bến, xuất kho | `AC-P1-03`, `AC-P1-04`, `AC-P1-05`):**
  - Trong `interact`: xét `_in_dock()` **TRƯỚC** hái nút (`docked` → `gather_end`, kể cả ở bước cuối nếu còn Máu).
  - Ngoài bến, chỉ hái khi `_at_surface()`: chọn nút `ready` (`regrow_ticks == 0`) gần nhất trong `interact_radius` (cả đúng mép, hòa theo `id_key`). Đủ chỗ cho `node_yield` (`len(hold) + amount <= hold_capacity`) → thêm vào `hold`, đặt `regrow_ticks = round(regrow_s * 60)`, phát `gather` (`{"node_id", "kind", "amount"}`). Thiếu chỗ → phát `hold_full` (`{"action": "gather", "node_id", "required", "free"}`), **giữ nguyên nút**.
  - Trong `catch`: chỉ khi `catch_cd_ticks == 0` và dưới nước (`not _at_surface()`): chọn đàn gần nhất trong `catch_radius` (hòa `id_key`). Đủ chỗ cho toàn bộ `fish_yield[kind]` → thêm vào `hold`, **xóa đàn khỏi `self.fish`**, đặt `catch_cd_ticks = round(catch_cooldown_s * 60)`, phát `fish_caught` (`{"fish_id", "kind", "yield"}`). Thiếu chỗ → phát `hold_full` (`{"action": "catch", "fish_id", "required", "free"}`), **giữ đàn & giữ cooldown**, không thử đàn khác. Không có đàn trong tầm → không event, không hồi chiêu.
  - Bước cuối `time_left_ticks == 0`: kết thúc `time` ở mọi độ sâu *sau* các hành động trên, giữ giỏ hiện có.
- [x] **CP1-G3 (Tích hợp, `README` & Tag P1 | `AC-P1-15`, `AC-P1-16`):**
  - [x] Rà soát [README.md](README.md) (`≤ 3` lệnh clone-to-run macOS/Linux, điều khiển, cách tính điểm, lệnh test `1` lệnh), đối chiếu [game.contract.json](game.contract.json), và ghi standup Phase 1 vào [docs/standup.md](docs/standup.md).
  - [x] Review code cho `Cuubeo` (`docs/proof/phase-1/review-quan-by-Do-Hong-Vy.md`), tạo `gather_sample.jsonl`/`quan_sample.jsonl`, kiểm chứng `AC-P1-14`/`AC-P1-15`, chạy `check-contract` (`90/90` tests OK).
  - [x] Commit bản chốt cuối & gắn tag `phase-1` (`199f067`, Do-Hong-Vy).

#### B. `Cuubeo` (`sim/quan` — [`chonoi/sim/quan.py`](chonoi/sim/quan.py) + PO)
- [x] **CP1-Q1 (Lát 3 — Khách, giữ chỗ, kiên nhẫn, bỏ đi | `AC-P1-06`, `AC-P1-08`):**
  - Khởi tạo khách từ `scenario["customers"]` (suy `reserved` theo công thức nếu đơn `reserved` thiếu `reserved`, theo `order_tick` rồi `id` bàn).
  - Bước 1: giảm timer ca, nấu, ăn, kiên nhẫn; tăng `ready_ticks` **chỉ cho món đã `ready` ở đầu bước**.
  - Bước 5 (khi còn giờ, đúng lịch `first_customer_tick` + `customer_interval_s * 60` theo `phase_tick` sau tăng): còn bàn trống → chọn bàn trống id nhỏ nhất; chọn **đều theo `Streams`** trong các món đủ nguyên liệu khả dụng (`stock - tổng reserved`, ứng viên sắp theo mã Unicode id món); giữ chỗ ngay (`order_status: "reserved"`, `order_tick = phase_tick`, kiên nhẫn đầy và giảm từ bước sau), phát `customer_arrived`. Không có món đủ → phát `no_dish` (`{}`).
  - Bước 4 (duyệt theo id bàn): nếu còn giờ, khách `waiting` có `patience_ticks_left == 0` → nhả giữ chỗ, cộng `left_reputation_delta` (kẹp `[reputation_min, reputation_max]`), phát `customer_left` (`reason: "patience"`).
- [x] **CP1-Q2 (Lát 4 — Bếp, bưng, phục vụ, tiền, boa, uy tín, `player.vel` | `AC-P1-07`, `AC-P1-08`, `AC-P1-11`):**
  - Bổ sung `"vel": self.vel` vào `QuanSim.snapshot()["player"]` (`clarify #9`, `AC-P1-11`).
  - Bước 2 (duyệt bếp theo `sort_by_id`): `cooking` hết giờ → `ready` (`ready_ticks = 0`), phát `dish_ready`.
  - Bước 3 (`interact` tối đa 1 đối tượng theo `(khoảng cách, bếp trước bàn, id_key)`): bếp `idle` lấy đơn `reserved` cũ nhất theo `(order_tick, table_id)`, tiêu nguyên liệu giữ, chốt `base_price` → `cook_started`; bếp `ready` & tay trống → `dish_picked`; bàn có khách khớp `hand.order_id` → chốt `tip = floor(base_price * tip_rate)` nếu tỷ lệ kiên nhẫn còn lại **sau bước 1** `>= tip_min_patience_ratio` (ngược lại `0`), chuyển `eating` → `served` (hợp lệ cả đúng tick kiên nhẫn về 0 hoặc hết ca).
  - Bước 4: khách `eating` xong trả `paid` (`finished_eating`), boa dương cộng `tip_reputation` (kẹp `[min, max]`), rời bàn. Hết ca (`time_left_ticks == 0`): khách `eating` trả ngay `paid` (`closing`), khách `waiting` rời `customer_left` (`closing`, **không trừ uy tín**), phát `quan_end`.
- [x] **CP1-Q3 (PO):** *(review `gather` xong: `docs/proof/phase-1/review-gather-by-Cuubeo.md`)* Giữ [`docs/clarify.md`](docs/clarify.md) luôn cập nhật nếu phát sinh câu hỏi mới; review code cho `Do-Hong-Vy`.

#### C. `Phog2811` (`client/ui` — [`chonoi/web/index.html`](chonoi/web/index.html) & `README.md`)
- [x] **CP1-U1 (Nâng cấp UI/HUD Gather & Quán v1.0 | `AC-P1-14`):**
  - Đọc hoàn toàn từ `GET /state`, gửi `POST /input`, `POST /restart` (giữ pass `tests/test_live.py`).
  - HUD buổi sáng (`gather`): thời gian, thanh Oxy (cảnh báo khi thấp), Tim HP, trạng thái ngạt (`zero_oxy_ticks`), hồi chiêu bắt cá, giỏ LIFO, nút hái + đếm ngược mọc lại, đàn cá, vùng bến (`E`).
  - HUD buổi tối (`quan`): kho khả dụng (`stock - reserved`), bếp (`idle`/`cooking`/`ready` + đọc đúng `st.dish.dish_id ?? st.dish`), món trên tay (`hand.dish_id ?? hand`), bàn + khách + món gọi + thanh kiên nhẫn + trạng thái `eating`, tiền, uy tín, điểm, log sự kiện.
- [x] **CP1-U2 (Trải nghiệm & README DoD | `AC-P1-14`, `AC-P1-15`):** Thêm bảng công thức 3 món trên HUD, màn hình kết thúc ca rõ ràng; rà soát [README.md](README.md) đảm bảo đủ hướng dẫn chạy từ clone sạch `≤ 3` lệnh macOS/Linux, điều khiển, công thức tính điểm và lệnh test 1 lệnh.
- [x] **CP1-U3 (Scrum):** Nhắc cả nhóm điền [`docs/standup.md`](docs/standup.md) giữa Phase 1 (phút 20–25) và kiểm tra tiến độ trước `0:50`.

#### D. `Nguyenquoctoan0310` (`qa` — Validation, Tests & Verification Phase 1)
- [x] **CP1-T1 (Validation mức luật — mã thoát 2 | `AC-P1-09`, `AC-P1-10`):**
  - Hoàn thiện [`chonoi/scenario.py`](chonoi/scenario.py) (`_validate_quan_rules`, `check_quan_stock` trong `headless.py`/`live.py`) và [`chonoi/contract.py`](chonoi/contract.py) (`_validate_quan_layout`, `_validate_menu`).
- [x] **CP1-T2 (Bộ test Phase 1 | `AC-P1-01`..`AC-P1-13`):** `tests/test_gather_p1.py` (11), `tests/test_quan_p1.py` (14), `tests/test_scenario_quan_p1.py` (12), `tests/test_contract_quan.py` (20) + smoke/unit/live = **90/90 OK**.
- [x] **CP1-T3 (Bằng chứng & Ma trận truy vết P1 | `AC-P1-14`, `AC-P1-15`, `AC-P1-16`):**
  - Chạy `verify-phase` + kiểm chứng live UI (`browser`) + kiểm README/contract; đầy đủ bằng chứng trong `docs/proof/phase-1/` và [`docs/verification/phase-1.md`](docs/verification/phase-1.md).

#### E. Checklist đóng CP1 (trước `1:00`)
- [x] Toàn bộ unit test + smoke test + test Phase 1 xanh (**90/90 OK**), `python3 tools/check_team.py` đạt `OK`.
- [x] Đủ bằng chứng trong `docs/proof/phase-1/` và [`docs/verification/phase-1.md`](docs/verification/phase-1.md) cho `AC-P1-01..15`.
- [x] [`docs/ai-usage-log.md`](docs/ai-usage-log.md) & [`docs/standup.md`](docs/standup.md) cập nhật đủ cho cả 4 thành viên.
- [x] Cả 4 thành viên đều có `≥ 3` commit có nội dung gắn với tài khoản GitHub thật (`Cuubeo`: 9, `Do-Hong-Vy`: 7+, `Phog2811`: 4, `nguyenquoctoan0310`: 3).
- [x] Commit bản chốt cuối, gắn tag `phase-1` (`199f067`) và `git push origin main --tags` (`AC-P1-01..16` hoàn tất).

---

### CP2 — Phase 2: Mở rộng & Đổi yêu cầu đợt 1 (1:00 – 1:55 | Hạn tag `phase-2`: trước 1:55)

> Kế hoạch chi tiết & mã AC chính thức: [`docs/ticket-02.md`](docs/ticket-02.md) (Test Contract v1.1), [`docs/plan/phase-2.md`](docs/plan/phase-2.md) (`AC-P2-01..15`), [`docs/adr/0001-contract-v1-1.md`](docs/adr/0001-contract-v1-1.md).

- [x] **CP2-0 (PO `Cuubeo` + Integrator `Do-Hong-Vy`, 1:00 – 1:08):**
  - Đọc đề Phase 2 trên Lab Board, tách toàn bộ AC (`AC-P2-??`) vào `docs/plan/phase-2.md` (`≤ 1 trang`).
  - Ghi mọi câu hỏi/đổi yêu cầu vào [`docs/clarify.md`](docs/clarify.md).
  - Nếu có thay đổi `game.contract.json`, schema snapshot/event/inventory hoặc quy tắc sẵn có: tạo **ADR** trong `docs/adr/0001-<tieu-de>.md` (theo `0000-template.md`, có bảng tác động module/file/test) và thông báo cả nhóm trước khi code.
- [x] **CP2-1 (`All` — Standup nhanh):** Điền dòng Phase 2 trong [`docs/standup.md`](docs/standup.md).
- [x] **CP2-2 (`Do-Hong-Vy` — `sim/gather`):** Triển khai các lát tính năng/đổi yêu cầu Phase 2 thuộc buổi sáng (`gather`) — giữ nguyên quy tắc `Streams` tách luồng (`rng.get("<ten_luong>")`) để không làm lệch RNG cũ; đọc mọi tham số mới từ `game.contract.json`.
- [x] **CP2-3 (`Cuubeo` — `sim/quan`):** Triển khai các lát tính năng/đổi yêu cầu Phase 2 thuộc buổi tối (`quan`) hoặc ghép ca/chế độ mới theo đề Phase 2.
- [x] **CP2-4 (`Phog2811` — `client/ui`):** Cập nhật UI/HUD hiển thị đầy đủ các thực thể/trạng thái/nút bấm/cơ chế mới của Phase 2; trau chuốt hình ảnh thay thế hình khối tạm (đảm bảo mọi hiệu ứng thêm chỉ chạy phía client/live, không chạm vào output headless).
- [x] **CP2-5 (`Nguyenquoctoan0310` — `qa`):**
  - Cập nhật validation mới trong `contract.py` / `scenario.py` / `inputs.py` (nếu contract nâng cấp).
  - Viết bộ test Phase 2 (`tests/test_phase2_*.py`) + **chạy lại toàn bộ test Phase 1 (regression)**.
  - Xuất bằng chứng vào `docs/proof/phase-2/` và hoàn thiện `docs/verification/phase-2.md`.
- [x] **CP2-6 (`Phog2811` + `All` — Retro nhanh Phase 2, ~1:45):**
  - Điền mục **Phase 2 (nhanh)** trong [`docs/retro.md`](docs/retro.md): *Điều tốt*, *Điều tệ*, *1 hành động cụ thể cho Phase 3*.
- [ ] **CP2-7 (`Do-Hong-Vy` + `All` — Harness & Tag P2):**
  - Cập nhật [`AGENTS.md`](AGENTS.md) với quy tắc/bẫy mới phát hiện ở Phase 1–2 (tạo diff rõ trong git history).
  - Cập nhật [`docs/ai-usage-log.md`](docs/ai-usage-log.md) cho cả 4 người (Phase 2).
  - Kiểm tra mọi người đã có `≥ 2` commit tích lũy; chạy full test xanh; gắn tag `phase-2` và push trước **1:55**.

---

### CP3 — Phase 3: Mở rộng & Tích hợp hoàn chỉnh (1:55 – 2:30 | Hạn tag `phase-3`: trước 2:30)

> **Mục tiêu:** Đáp ứng toàn bộ yêu cầu Phase 3 mở lúc 1:55 (ví dụ chế độ nối ngày `--mode day` / nâng cấp gameplay / cân bằng hệ thống theo đề), thực thi hành động cải tiến từ Retro P2, giữ regression P1+P2 xanh.

- [x] **CP3-0 (PO `Cuubeo`, 1:55 – 2:00):** Đọc đề Phase 3, cập nhật [`docs/clarify.md`](docs/clarify.md) & tạo `docs/plan/phase-3.md`; lập ADR (`docs/adr/0002-...md`) nếu đổi contract/schema.
- [x] **CP3-1 (`All` — Thực thi hành động Retro P2 & Standup):** Áp dụng ngay 1 hành động đã cam kết ở Retro Phase 2; điền dòng Phase 3 trong [`docs/standup.md`](docs/standup.md).
- [x] **CP3-2 (`Do-Hong-Vy` & `Cuubeo` — Core Sim & Tích hợp):**
  - Triển khai các thay đổi/tính năng Phase 3 trên `sim/gather`, `sim/quan`, và `sim/day` / `runner` (nếu Phase 3 mở khóa `--mode day` hoặc luồng chuyển sáng→tối).
  - Rà soát độ ổn định deterministic: chạy kiểm tra cùng seed với mọi chế độ.
- [x] **CP3-3 (`Phog2811` — `client/ui` + Chuẩn bị Sáng tạo):**
  - Hoàn thiện UI cho các tính năng Phase 3 (menu, chuyển cảnh sáng-tối, hiệu ứng phản hồi, âm thanh Web Audio API tự tạo hoặc asset CC0/MIT).
  - Bắt đầu phần **Sáng tạo của nhóm** (chỉ khi lõi Phase 3 chạy đúng): giữ tuyệt đối nguyên tắc **tắt ở headless**.
- [x] **CP3-4 (`Nguyenquoctoan0310` — `qa`):**
  - Viết test Phase 3 (`tests/test_phase3_*.py`) + **regression toàn bộ Phase 1 & Phase 2**.
  - Lưu log/output vào `docs/proof/phase-3/` và hoàn thiện `docs/verification/phase-3.md`.
- [ ] **CP3-5 (`All` — Harness & Tag P3):**
  - Cập nhật [`AGENTS.md`](AGENTS.md) (nếu có skill/hook hoặc rule mới cho Phase 3) & [`docs/ai-usage-log.md`](docs/ai-usage-log.md) (Phase 3).
  - Chạy full test xanh; đảm bảo mỗi thành viên có **≥ 3 commit có nội dung** (hoặc hoàn tất ở đầu CP4); gắn tag `phase-3` và push trước **2:30**.

---

### CP4 — Phase 4: Hoàn thiện, Sáng tạo, Retro cuối, Release `v1.0.0` & Demo (2:30 – 3:00 | Hạn tag `phase-4` + Release `v1.0.0`: trước 3:00)

> **Mục tiêu:** Đóng toàn bộ yêu cầu Phase 4, hoàn thiện sản phẩm sáng tạo, khóa bằng chứng 100 điểm, hoàn thành retro cá nhân & nhóm, gắn tag `phase-4` + Release `v1.0.0`, sẵn sàng Demo.

- [x] **CP4-1 (Xử lý yêu cầu Phase 4 — 2:30 – 2:42):**
  - PO `Cuubeo` đọc đề Phase 4 trên Lab Board → cập nhật `docs/plan/phase-4.md`, [`docs/clarify.md`](docs/clarify.md).
  - `Do-Hong-Vy` & `Cuubeo` xử lý nốt phần sim / edge cases / cân bằng tham số (nếu Phase 4 yêu cầu).
  - `Phog2811` chốt hoàn thiện UI/đồ họa/âm thanh và phần **Sáng tạo của nhóm** (đảm bảo **tắt khi chạy headless**!).
- [x] **CP4-2 (Kiểm chứng cuối cùng — `Nguyenquoctoan0310`):**
  - Chạy lại toàn bộ test suite (`tests/` cho P1 + P2 + P3 + P4) + test kiểm tra sáng tạo tắt ở headless + `python tools/check_team.py`.
  - Kiểm tra không lộ API key, token, `.env` trong toàn bộ commit/repo.
  - Lưu bằng chứng cuối vào `docs/proof/phase-4/` và hoàn thiện `docs/verification/phase-4.md`.
- [x] **CP4-3 (Hoàn thiện tài liệu sản phẩm & nguồn — `Phog2811` + `Do-Hong-Vy`):**
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
    - [x] `docs/members/Cuubeo.md`
    - [ ] `docs/members/Phog2811.md`
    - [ ] `docs/members/Nguyenquoctoan0310.md`
  - Chốt dòng Phase 4 trong [`docs/ai-usage-log.md`](docs/ai-usage-log.md) & [`docs/standup.md`](docs/standup.md) + cập nhật lần cuối [`AGENTS.md`](AGENTS.md).
- [ ] **CP4-5 (Kiểm tra commit & Release — `Do-Hong-Vy`):**
  - Xác nhận mỗi người có **≥ 3 commit có nội dung** bằng đúng handle trong `TEAM.md` (`git log --format="%h %an <%ae> %s"`).
  - Gắn tag `phase-4` và tag `v1.0.0` trên commit sạch cuối cùng đã pass mọi test, push lên `origin`, tạo GitHub Release `v1.0.0` trước **3:00**.
- [x] **CP4-6 (Chuẩn bị Demo 5 điểm — `Phog2811` + `All`):**
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

---

### Trạng thái chốt (Cuubeo, cập nhật cuối buổi)
- Còn mở: **CP2-7 / CP3-5 / CP4-5** — đẩy `main`, gắn tag `phase-2`, `phase-3`, `phase-4` và công bố GitHub Release `v1.0.0` (Integrator `Do-Hong-Vy`); **CP4-4** — `docs/members/Do-Hong-Vy.md`, `Nguyenquoctoan0310.md`, `Phog2811.md` đã có bản nháp bằng chứng, chờ chính chủ viết phần phản tư.
- Bằng chứng: `docs/verification/phase-1..4.md`, `docs/proof/phase-1..4/`, `CHANGELOG.md`, `docs/release-notes-v1.0.0.md`, `docs/demo.md`.
