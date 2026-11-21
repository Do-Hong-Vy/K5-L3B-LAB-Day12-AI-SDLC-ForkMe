# Credits — Nhóm ForkMe

## 1. Tài nguyên đồ họa & âm thanh
- **Đồ họa 2D/2.5D & Hiệu ứng VFX (`chonoi/web/index.html`):** 100% tự vẽ bằng mã HTML5 Canvas 2D Procedural Vector bởi thành viên `Phog2811` (Đinh Hoàng Phong) — bao gồm bối cảnh Sông Chín Khúc, Nhà Bè Má Tư, nhân vật Út Sen, 6 loài nguyên liệu/cá/rau, Cá Sấu Năm Chèo, Rắn Hổ Mây, và các nhân vật parody chế độ Sáng tạo (*A-Qua-Mèn*, *Gô-Ku SSJ3*, *Z-Warriors*). Không sử dụng bất kỳ tệp hình ảnh PNG/SVG bên ngoài nào.
- **Âm nhạc & Hiệu ứng âm thanh (Web Audio API Synthesizer trong `chonoi/web/index.html`):** 100% tự tổng hợp thời gian thực bằng bộ dao động Web Audio API (giai điệu ngũ cung miền Tây, nhạc nền Anime Boss Battle chiptune, và các hiệu ứng SFX tương tác). Không sử dụng tệp `.mp3`/`.wav` bên ngoài.
- **Sprite cá, rong, đá, bong bóng (`chonoi/web/assets/kenney/`):** *Fish Pack 2.0* của **Kenney** (www.kenney.nl), giấy phép **CC0 1.0** (public domain, ghi công không bắt buộc — vẫn ghi để cảm ơn). Tải từ OpenGameArt (`opengameart.org/content/fish-pack-0`, file `kenney_fish-pack_2.0.zip`); bản License.txt gốc lưu kèm trong thư mục. Dùng: `fish_blue` (cá linh), `fish_grey` (cá lóc), `fish_green` (cá kèo), `seaweed_*`, `rock_*`, `bubble_*`. Chỉ vẽ phía client, không ảnh hưởng headless. Tích hợp bởi `Cuubeo`.
- **Khung mã nguồn khởi tạo (`chonoi/`):** Khung Python starter do giảng viên môn AI SDLC (VinUni) cung cấp.

## 2. Công cụ AI đã sử dụng (theo `docs/ai-usage-log.md`)
- **Antigravity (Gemini + skill `ui-ux-pro-max`):** Hỗ trợ thiết kế UI/UX, đồ họa 2.5D Canvas, Web Audio API, `sim/gather`, hợp đồng tích hợp và kiểm chứng.
- **Claude Code (Claude Opus 5.5):** Hỗ trợ phân tích PRD/Ticket, `sim/quan`, hệ thống validation `scenario.py` / `contract.py` và bộ test tự động.
