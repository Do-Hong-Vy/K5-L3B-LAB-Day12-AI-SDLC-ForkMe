# Credits — Nhóm ForkMe

## 1. Tài nguyên đồ họa & âm thanh
- **Đồ họa 2D/2.5D & Hiệu ứng VFX (`chonoi/web/index.html`):** tự vẽ bằng HTML5 Canvas 2D bởi `Phog2811` (Đinh Hoàng Phong) — bối cảnh Sông Chín Khúc, Nhà Bè Má Tư, Cá Sấu Năm Chèo, Rắn Hổ Mây, VFX. Nhân vật parody từ thương hiệu khác (trước đây) đã được gỡ bỏ và thay bằng nhân vật gốc của lab + sprite CC0 bên dưới.
- **Âm nhạc & Hiệu ứng âm thanh (Web Audio API Synthesizer trong `chonoi/web/index.html`):** 100% tự tổng hợp thời gian thực bằng bộ dao động Web Audio API (giai điệu ngũ cung miền Tây, nhạc nền Anime Boss Battle chiptune, và các hiệu ứng SFX tương tác). Không sử dụng tệp `.mp3`/`.wav` bên ngoài.
- **Sprite cá, rong, đá, bong bóng (`chonoi/web/assets/kenney/`):** *Fish Pack 2.0* của **Kenney** (www.kenney.nl), giấy phép **CC0 1.0** (public domain, ghi công không bắt buộc — vẫn ghi để cảm ơn). Tải từ OpenGameArt (`opengameart.org/content/fish-pack-0`, file `kenney_fish-pack_2.0.zip`); bản License.txt gốc lưu kèm trong thư mục. Dùng: `fish_blue` (cá linh), `fish_grey` (cá lóc), `fish_green` (cá kèo), `seaweed_*`, `rock_*`, `bubble_*`. Chỉ vẽ phía client, không ảnh hưởng headless. Tích hợp bởi `Cuubeo`.
- **Nhân vật người Út Sen và khách (`chonoi/web/assets/toon/`):** *Toon Characters 1* của **Kenney** (www.kenney.nl), giấy phép **CC0 1.0**. Tải từ OpenGameArt (`opengameart.org/content/toon-characters-1`, file `kenney_toonCharacters1.zip`); License.txt gốc lưu kèm. Dùng: Female person (Út Sen), Male person / Female adventurer / Male adventurer (khách), các tư thế idle, walk, fall, hold, hurt, talk, cheer. Tích hợp bởi `Cuubeo`.
- **Món ăn, dụng cụ bếp, kèo nèo (`chonoi/web/assets/food/`):** *Food Kit 2.0* của **Kenney**, **CC0 1.0** (`opengameart.org/content/food-kit`, `kenney_food-kit.zip`): fish (cá lóc nướng trui), salad (gỏi bông súng), pot-stew (lẩu cá linh), bowl-soup (canh chua), skewer (cá kèo nướng), pan-stew (lẩu mắm), frying-pan, pot, plate, leek (kèo nèo). License.txt gốc lưu kèm.
- **Cá Sấu Năm Chèo (`chonoi/web/assets/animal/crocodile.png`):** *Animal Pack Redux* của **Kenney**, **CC0 1.0** (`opengameart.org/content/animal-pack-redux`). License.txt gốc lưu kèm.
- **Khung mã nguồn khởi tạo (`chonoi/`):** Khung Python starter do giảng viên môn AI SDLC (VinUni) cung cấp.

## 2. Công cụ AI đã sử dụng (theo `docs/ai-usage-log.md`)
- **Antigravity (Gemini + skill `ui-ux-pro-max`):** Hỗ trợ thiết kế UI/UX, đồ họa 2.5D Canvas, Web Audio API, `sim/gather`, hợp đồng tích hợp và kiểm chứng.
- **Claude Code (Claude Opus 5.5):** Hỗ trợ phân tích PRD/Ticket, `sim/quan`, hệ thống validation `scenario.py` / `contract.py` và bộ test tự động.
