# David English — Design System v2

> "Page design is too simple, make it professional and interesting."
> Thiết kế v2: giữ neo thương hiệu navy + vàng, thêm chiều sâu (gradient, bóng,
> vạch màu, chip icon), font serif hệ thống cho tiêu đề. Không font ngoài,
> không ảnh ngoài, không tracker — chi phí $0.

## 1. Palette

| Token | Hex | Dùng cho | Tương phản (nền) |
|---|---|---|---|
| `--navy` | `#123a6d` | Neo thương hiệu, link, nút chính, chip B1 | trắng trên navy **11.34:1**; navy trên kem **10.40:1** |
| `--navy-dark` | `#0c2a50` | Tiêu đề, hover nút/link, footer | trắng trên navy-dark **14.36:1**; navy-dark trên kem **13.17:1** |
| `--navy-deep` | `#081f3a` | Đầu gradient hero | trắng **16.57:1**; vàng **7.48:1** |
| `--sky` | `#eaf1f8` | Dải nền xen kẽ (`.section-alt`), bong bóng AI | mực trên sky **13.26:1**; muted trên sky **4.80:1** |
| `--sky-line` | `#d3deea` | Viền dải sky | trang trí |
| `--accent` | `#e8a020` | Vàng điểm nhấn — nền badge, vạch header/footer, CTA hero | mực trên vàng **6.82:1**; vàng trên navy **5.12:1** |
| `--accent-dark` | `#b97d0d` | **Chỉ trang trí** (viền, gạch) — KHÔNG làm chữ: 3.50:1 trên trắng | — |
| `--gold-deep` | `#7a5200` | Chữ vàng / icon vàng / chip C1 trên nền sáng | trên trắng **6.92:1**; trên tint vàng **6.25:1** |
| `--gold-soft` | `#fdf3d7` | Nền tint vàng (badge thẻ, chip hover) | mực trên tint **13.65:1** |
| `--gold-line` | `#ecd28a` | Viền tint vàng | trang trí |
| `--teal` | `#0e7c6b` | Màu phụ 1 (kỹ năng, chip A2) | trắng trên teal **5.10:1** |
| `--teal-dark` | `#0a5c50` | Chữ teal / icon teal trên nền sáng | trên trắng **7.90:1**; trên tint teal **6.85:1** |
| `--teal-soft` | `#e3f2ef` | Nền tint teal | mực trên tint **13.10:1** |
| `--green` / `--green-soft` | `#177245` / `#e6f3ec` | Sách, chip A1 | trắng trên green **5.95:1**; green trên tint **5.21:1** |
| `--plum` / `--plum-soft` | `#6d4a8f` / `#efe9f5` | Công cụ | trắng **6.94:1**; plum trên tint **5.83:1** |
| `--coral` / `--coral-soft` | `#b3382e` / `#fbeae7` | Trẻ em | trắng **5.96:1**; coral trên tint **5.12:1** |
| `--indigo` / `--indigo-soft` | `#444a8a` / `#e9eaf4` | Công việc, chip B2 | trắng **8.10:1**; indigo trên tint **6.77:1** |
| `--steel` / `--steel-soft` | `#2f6da3` / `#e7f0f8` | Du học | trắng **5.47:1**; steel trên tint **4.75:1** |
| `--maroon` / `--maroon-soft` | `#7c2128` / `#f9e9ea` | Địa điểm, chip C2 | trắng **9.98:1**; maroon trên tint **8.49:1** |
| `--ink` | `#1d2733` | Chữ chính | trên kem **13.86:1**; trên trắng **15.11:1** |
| `--muted` | `#5b6b7d` | Chữ phụ | trên kem **5.01:1**; trên trắng **5.46:1** |
| `--slate` / `--slate-soft` | `#3d4f63` / `#e8edf2` | Badge "Sắp có" | slate trên tint **7.14:1** |
| `--bg` | `#f7f5ef` | Nền trang (kem, giữ v1) | — |
| `--card` | `#ffffff` | Nền thẻ | — |
| `--line` | `#dfe3e8` | Viền | — |
| `--ok` | `#1a7f4b` | Thành công | — |

### Quy tắc vàng
- `--accent` (`#e8a020`) và `--accent-dark` (`#b97d0d`) **không bao giờ làm màu chữ
  trên nền sáng** (3.50:1 / 3.21:1 — rớt AA). Chữ vàng dùng `--gold-deep`.
- Chữ vàng trên nền tối thì được: vàng trên navy **5.12:1**, trên navy-dark **6.48:1**.

## 2. Kiểu chữ (Type)

- **Tiêu đề (display):** `Georgia, 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif`
  — stack serif hệ thống, không tải font ngoài. Áp cho `h1–h3`, `.hero-title`,
  `.brand`, `.section-head h2`, `.de-chat-titles strong`.
- **Thân bài:** `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
- **Dấu tiếng Việt:** Georgia / Palatino / Times New Roman đều có đủ glyph Latin
  Extended trên Windows và macOS; stack có nhiều fallback nên dấu (à, ắ, ệ, ỗ, ư…)
  không rớt về font khác. Nếu một máy thiếu cả stack thì fallback `serif` mặc định
  của hệ thống vẫn giữ dấu đúng.
- **Thang chữ (mobile-first, body 17px):**

| Phần tử | Mobile | ≥ 720px |
|---|---|---|
| `.hero-title` | `clamp(2rem, 7.2vw, 3.25rem)` (32–52px), lh 1.12 | — |
| `h1` | 30px, lh 1.25 | 36px |
| `h2` | 22px | 26px |
| `h3` / `.card h2` | 19px / 20px | — |
| `.hero-lead` | 18px | 20px |
| `.lead` | 19px | — |
| `.section-sub` | 16px | — |
| body | 17px, lh 1.6 | — |
| `.muted` | 15px | — |
| `.hero-eyebrow` / `.page-eyebrow` | 13px, 800, uppercase, tracking 0.12–0.14em | — |

## 3. Components

### Header / nav
- Header: gradient `135deg, navy → navy-dark`, viền dưới vàng 3px.
- `.brand` serif 28px, chữ "ENGLISH" vàng; `.tagline` `#c9d6e6` (7.69:1 trên navy).
- Nav link: padding `10px 12px`, cao 44px; hover nền trắng 16%; `.active` nền
  vàng + chữ mực (6.82:1). Mobile: `<details class="nav-toggle">` giữ nguyên
  cơ chế — `summary` có viền trắng mờ, nav dọc khi mở.

### Hero (`.hero`, `.hero-eyebrow`, `.hero-title`, `.hero-lead`, `.hero-cta`)
- Dải **full-bleed** navy: gradient navy → navy-dark → navy-deep + 2 quầng sáng
  (vàng góc trên-phải, teal góc dưới-trái) + lưới chấm SVG data-URI mờ.
- `.hero-title strong` → vàng (builder bọc từ nhấn mạnh trong `<strong>`).
- CTA chính trong hero: `.btn-primary` nền vàng + chữ mực; `.btn-ghost` viền
  trắng. Ngoài hero, `.btn-primary` là navy, `.btn-ghost` viền navy.
- **Đặt hero:** trực tiếp trong `main.wrap` hoặc `body`. CSS dùng
  `margin-inline: calc(50% - 50vw)` + `padding-inline: max(20px, calc(50vw - 50%))`
  nên cả hai vị trí đều ra full-bleed đúng; nếu builder lồng hero sâu hơn một
  cấp thì hero chỉ hẹp lại (vẫn đẹp), không vỡ layout.

### Page head (`.page-head`, `.page-eyebrow`)
- Đầu trang con gọn: eyebrow vàng đậm uppercase + `h1` serif + `.lead`,
  gạch dưới `#dfe3e8`. Không dùng hero cho trang con.

### Section (`.section`, `.section-alt`, `.section-head`, `.section-sub`)
- `.section` padding dọc 28px. `.section-alt` là dải full-bleed nền sky gradient
  + viền trên/dưới `#d3deea` (cùng cơ chế `calc(50% - 50vw)` như hero — đặt
  trực tiếp trong `main.wrap`).
- `.section-head h2` 26px serif; `.section-sub` muted, tối đa 62 ký tự/dòng.

### Cards (`.cards`, `.card`, `.card-icon`, `.card-badge`, `.card-*`)
- Grid: 1 cột mobile → `repeat(auto-fill, minmax(280px, 1fr))` từ 640px.
- Thẻ trắng, bo 14px, bóng 2 lớp, vạch màu 4px trên cùng (`::before`),
  hover nâng `-3px` + bóng đậm. `.card h2 a` navy-dark, hover gạch chân.
- `.card-icon`: chip 48×48, bo 12px, nền tint + glyph màu đậm của loại thẻ
  (SVG inline 24×24 do builder chèn). Glyph trên tint đều ≥ 4.75:1.
- `.card-badge`: pill tint vàng, chữ `--gold-deep`, viền `#ecd28a`.
- Màu theo loại (`--card-accent` = vạch + tông chip):

| Class | Accent | Tint chip |
|---|---|---|
| `.card-level` | navy `#123a6d` | sky |
| `.card-skill` | teal `#0e7c6b` (glyph `--teal-dark`) | teal-soft |
| `.card-exam` | gold-deep `#7a5200` | gold-soft |
| `.card-tool` | plum `#6d4a8f` | plum-soft |
| `.card-book` | green `#177245` | green-soft |
| `.card-kids` | coral `#b3382e` | coral-soft |
| `.card-work` | indigo `#444a8a` | indigo-soft |
| `.card-abroad` | steel `#2f6da3` | steel-soft |
| `.card-resource` | teal-dark `#0a5c50` | teal-soft |
| `.card-place` | maroon `#7c2128` | maroon-soft |

### Buttons (`.btn`, `.btn-primary`, `.btn-ghost`)
- `min-height: 44px`, padding `12px 22px`, bo 10px, chữ 16px/700, hover nâng `-1px`.
- `.btn` và `.btn-primary` giống nhau (navy) — builder dùng class nào cũng được;
  `.btn-ghost` nền trong suốt, viền navy.

### Badges
- `.badge` giữ nguyên v1: nền vàng, chữ mực (6.82:1).
- `.badge-soon` (mới, cho "Sắp có"): nền `--slate-soft`, chữ `--slate`, viền
  đứt nét — nhìn là biết "chưa có", khác hẳn badge vàng. Builder thay
  `<span class="badge">Sắp có</span>` bằng `<span class="badge badge-soon">Sắp có</span>`
  khi tiện; `.badge` cũ vẫn hiển thị đúng nếu chưa đổi.

### Level chips (`.level-chip` + `.lv-a1` … `.lv-c2`)
- Pill, tối thiểu 44×44px, chữ trắng 800, mỗi cấp một màu:

| Class | Màu | Trắng trên màu |
|---|---|---|
| `.lv-a1` | `#177245` | 5.95:1 |
| `.lv-a2` | `#0e7c6b` | 5.10:1 |
| `.lv-b1` | `#123a6d` | 11.34:1 |
| `.lv-b2` | `#444a8a` | 8.10:1 |
| `.lv-c1` | `#7a5200` | 6.92:1 |
| `.lv-c2` | `#7c2128` | 9.98:1 |

### Form / kết quả
- Input/textarea giữ 16px (tránh iOS zoom), focus viền navy. `.result` thêm bóng
  nhẹ, giữ vạch trái vàng.

### Footer
- Nền navy-dark, viền trên vàng 3px (đối xứng header). Chữ muted `#c9d6e6`
  **9.74:1**. Link trắng (14.36:1), hover vàng (6.48:1).

### Chat (`chat/de-chat.css`, tự chứa — không phụ thuộc `style.css`)
- FAB: gradient navy, icon vàng, bóng navy, hover nâng `-2px`.
- Panel: header gradient navy + viền dưới vàng 3px, tiêu đề serif 17px,
  sub `#c9d6e6`; nút đóng nền trắng 14%.
- Bong bóng user: navy + chữ trắng (11.34:1). Bong bóng AI: nền sky `#eaf1f8`
  + viền `#d3deea` (mực 13.26:1). Chip gợi ý hover viền vàng + nền tint vàng.
- Input giữ **16px**, `min-height: 44px`; nút gửi navy, `min-height: 44px`.

### Favicon
- `favicon.svg`: nền gradient navy → navy-dark, chữ "DE" Georgia trắng,
  gạch vàng dưới + chấm vàng góc trên-phải (khớp palette v2).

## 4. Accessibility floors (đã đo bằng script WCAG, xem §1)

| Floor | Yêu cầu | Đo được |
|---|---|---|
| Footer muted | ≥ 9.74:1 | **9.74:1** — `#c9d6e6` trên `#0c2a50` (giữ nguyên v1) |
| Link hover | ≥ 13.17:1 | **13.17:1** — `#0c2a50` trên `#f7f5ef`; trên trắng **14.36:1** |
| Body link | ≥ 4.5:1 | 10.40:1 trên kem, 11.34:1 trên trắng |
| Muted text | ≥ 4.5:1 | 5.01:1 trên kem, 5.46:1 trên trắng, 4.80:1 trên sky |
| Tap target | ≥ 44px | Nav link 44px · nav-toggle 44px · `.btn` min-height 44px · `.level-chip` 44px · chat chip/close/send/input ≥ 44px · FAB 56px |
| Focus | outline 3px | `:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }` cả 2 file |
| Reduced motion | tắt animation | `@media (prefers-reduced-motion: reduce)` tắt mọi `animation`/`transition` cả 2 file |

## 5. Quyết định thiết kế (vì sao)

1. **Giữ neo navy + vàng** (David đã duyệt thương hiệu v1) — v2 chỉ thêm chiều
   sâu, không đổi nhận diện.
2. **Teal làm màu phụ 1** thay vì thêm một màu nóng: teal hợp với navy (cùng họ
   lạnh), đủ tách khỏi vàng, và dùng được cho cả "kỹ năng" lẫn điểm nhấn hero.
3. **Serif hệ thống cho tiêu đề** thay vì webfont: $0, không tracker, không
   FOUT; Georgia có cá tính đủ để trang trông "chuyên nghiệp" hơn system-ui
   toàn trang, và dấu tiếng Việt an toàn.
4. **Thẻ có vạch màu + chip icon tint** thay vì thẻ trắng phẳng: mỗi chuyên mục
   nhận diện bằng màu ngay từ cái nhìn đầu tiên, nhưng vẫn giữ nền trắng để
   chữ luôn đạt tương phản cao.
5. **Hero full-bleed navy + CTA vàng**: trang chủ cũ mở đầu bằng `h1` khô trên
   nền kem — hero là thay đổi lớn nhất về cảm giác "chuyên nghiệp".
6. **Không ảnh ngoài**: mọi trang trí là CSS gradient + SVG data-URI (lưới chấm
   hero). Không có request mạng thêm nào.
7. **Mobile-first**: 1 cột, tap target 44px, chữ body 17px, input 16px — khán
   giả là người Việt học trên điện thoại.

## 6. Ghi chú cho template builder / merger

- **Mọi class trong brief đều đã có style** trong `assets/style.css`
  (kể cả class chưa xuất hiện trong markup hiện tại): `.hero*`, `.page-head`,
  `.page-eyebrow`, `.section*`, `.card*` (10 loại), `.card-icon`, `.card-badge`,
  `.btn*`, `.badge-soon`, `.level-chip` + `.lv-a1…c2`.
- `.hero` và `.section-alt` **phải là con trực tiếp của `main.wrap`** (hoặc của
  `body`) để cơ chế full-bleed `calc(50% - 50vw)` đúng. Lồng sâu hơn vẫn hiển
  thị được nhưng dải sẽ hẹp lại.
- `.hero-title strong` → vàng: bọc từ cần nhấn trong `<strong>`.
- `.card-icon` chờ **SVG inline 24×24** từ builder (màu glyph lấy từ
  `currentColor` — đặt `fill="currentColor"` / `stroke="currentColor"`).
- `.badge-soon` là class bổ sung, không thay thế `.badge` — trang cũ vẫn đúng
  nếu builder chưa đổi markup "Sắp có".
- `.btn` và `.btn-primary` tương đương — dùng một trong hai đều ra nút navy.
- **Không đổi** `_build.py`, `.html`, `api/chat.js` trong đợt này — chỉ 3 file
  dưới đây.
- `chat/de-chat.css` tự chứa biến màu riêng (không `@import` style.css) vì
  widget có thể load độc lập.

## 7. Bổ sung 23/11 (đợt nhất quán UI)

- **Bảng:** mọi `<table>` trong `_build.py` đều bọc `<div class="table-wrap">`
  (cuộn ngang trên mobile). CSS trong `style.css`: tiêu đề `th` nền navy chữ
  trắng (serif), `td` nền trắng, hàng chẵn `#fbfaf6`, chữ 15px.
- **OG image:** mọi trang đều có `og:image` →
  `https://davidenglish.vercel.app/assets/og-default.png` (1200×630, PIL: gradient
  navy + "DAVID ENGLISH" serif + tagline) và `og:url` chính tắc theo đường
  dẫn trang. File: `assets/og-default.png`.
- **Trò chơi (`tro-choi/`, file đơn):** mỗi game có dải `.de-back` giống hệt
  nhau ngay sau `<body>` — nền navy `#123a6d`, link "← David English" về `/`,
  cao tối thiểu 44px, hover vàng, `:focus-visible` viền vàng. Nền sáng của
  game là kem `#f7f5ef` (giống trang chính); dark mode của từng game giữ
  nguyên. Ngoại lệ cố ý: **TOEIC Arcade tối theo thiết kế** (nền `--ink`
  `#14173A`) — không đổi. Mỗi game giữ font hiển thị riêng nhưng mọi stack
  đều kết thúc bằng generic (`serif`/`sans-serif`/`monospace`) và mọi link
  Google Fonts đều có `display=swap`. Tất cả game đều có `lang="vi"` và
  `meta description` (lấy từ trang hub `/tro-choi/`).
- **Footer:** không còn dòng "khung sườn v1" — footer ghi "Bài học, trò chơi
  và sách học miễn phí — nội dung mới thêm dần."
