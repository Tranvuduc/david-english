# _build.py — sinh khung sườn HTML cho David English (v1, skeleton).
# Chạy: python3 _build.py  (ghi đè các file HTML trong thư mục này)
# KHÔNG đưa nội dung bài học nào vào đây — chỉ khung + mô tả "sắp có".
# Markup theo design system v2 (xem DESIGN-SYSTEM.md): hero, page-head,
# section/section-alt, card theo loại + icon SVG, badge-soon, level-chip.
# Chỉ đổi markup trình bày — không đổi chữ, link hay cấu trúc nội dung.
import html as htmlmod
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))

TAGLINE = "Học tiếng Anh miễn phí — giải thích bằng tiếng Việt"

LEAD_RE = re.compile(r'<p class="lead">(.*?)</p>', re.S)


def _svg(inner):
    return ('<svg viewBox="0 0 24 24" width="24" height="24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{inner}</svg>')


# Icon SVG inline 24x24 (currentColor) cho từng loại thẻ — vẽ tay, không asset ngoài.
ICON_SVG = {
    "level": _svg('<path d="M4 20h4v-4h4v-4h4V8h4"/>'),
    "skill": _svg('<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/>'
                  '<circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/>'),
    "exam": _svg('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 13l2 2 4-4.5"/>'),
    "tool": _svg('<path d="M4 8h8M16 8h4M4 16h2M10 16h10"/>'
                 '<circle cx="14" cy="8" r="2"/><circle cx="8" cy="16" r="2"/>'),
    "book": _svg('<path d="M12 6.5C10 5 7 4.5 4 4.5v14c3 0 6 .5 8 2 2-1.5 5-2 8-2v-14c-3 0-6 .5-8 2z"/>'
                 '<path d="M12 6.5v14"/>'),
    "kids": _svg('<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.7l5.9-.9z"/>'),
    "work": _svg('<rect x="3" y="8" width="18" height="12" rx="2"/>'
                 '<path d="M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>'),
    "abroad": _svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
                   '<path d="M12 3c2.8 3.6 2.8 14.4 0 18"/><path d="M12 3c-2.8 3.6-2.8 14.4 0 18"/>'),
    "resource": _svg('<path d="M10 14a4.5 4.5 0 0 0 6.4 0l2.8-2.8a4.5 4.5 0 0 0-6.4-6.4l-1.4 1.4"/>'
                     '<path d="M14 10a4.5 4.5 0 0 0-6.4 0l-2.8 2.8a4.5 4.5 0 0 0 6.4 6.4l1.4-1.4"/>'),
    "place": _svg('<path d="M12 21s-6.5-5.6-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21z"/>'
                  '<circle cx="12" cy="10.5" r="2.3"/>'),
}


def card_icon(kind):
    return f'<span class="card-icon" aria-hidden="true">{ICON_SVG[kind]}</span>'


def guide_sections(body_html):
    """Chia trang hướng dẫn sách thành <section class="section"> xen kẽ
    .section-alt theo từng <h2>; không đổi bất kỳ chữ hay link nào."""
    parts = re.split(r'(<h2>.*?</h2>)', body_html, flags=re.S)
    out = [parts[0]]
    alt = False
    for i in range(1, len(parts), 2):
        m = re.match(r'<h2>(.*?)</h2>', parts[i], re.S)
        head = f'<div class="section-head"><h2>{m.group(1)}</h2></div>'
        chunk = parts[i + 1] if i + 1 < len(parts) else ""
        cls = "section section-alt" if alt else "section"
        alt = not alt
        out.append(f'<section class="{cls}">\n{head}\n{chunk}</section>')
    return "".join(out)

NAV = [
    ("Trang chủ", "/"),
    ("Bài xếp lớp", "/bai-xep-lop.html"),
    ("Theo trình độ", "/trinh-do/"),
    ("Theo kỹ năng", "/ky-nang/"),
    ("Luyện thi", "/luyen-thi/"),
    ("Trẻ em", "/tre-em.html"),
    ("Tiếng Anh công việc", "/cong-viec.html"),
    ("Du học", "/du-hoc.html"),
    ("Tài nguyên miễn phí", "/tai-nguyen.html"),
    ("Sách học", "/sach/"),
    ("Trò chuyện AI", "/tro-chuyen-ai.html"),
]

STYLE = "/assets/style.css"
CHAT_CSS = "/chat/de-chat.css"
CHAT_JS = "/chat/de-chat.js"


def nav_html(active):
    items = []
    for label, href in NAV:
        cls = ' class="active" aria-current="page"' if href == active else ""
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n".join(items)


def _short(text, limit=150):
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def derive_desc(body_html):
    m = re.search(r'<p class="lead">(.*?)</p>', body_html, re.S)
    raw = m.group(1) if m else re.sub(r"<[^>]+>", " ", body_html)
    text = htmlmod.unescape(re.sub(r"<[^>]+>", " ", raw))
    return _short(text)


def page(path, title, h1, body_html, active="/", desc=None, eyebrow=None, hero=None):
    d = desc or derive_desc(body_html)
    desc_esc = htmlmod.escape(d, quote=True)
    title_esc = htmlmod.escape(title, quote=True)
    if hero is not None:
        # Trang chủ: hero full-bleed, con trực tiếp của <main class="wrap">.
        head_html = (
            '<section class="hero"><div class="wrap">'
            f'<p class="hero-eyebrow">{hero["eyebrow"]}</p>'
            f'<h1 class="hero-title">{hero["title_html"]}</h1>'
            f'<p class="hero-lead">{hero["lead"]}</p>'
            '<div class="hero-cta">'
            f'<a class="btn btn-primary" href="{hero["cta_primary"][1]}">{hero["cta_primary"][0]}</a>'
            f'<a class="btn btn-ghost" href="{hero["cta_secondary"][1]}">{hero["cta_secondary"][0]}</a>'
            "</div></div></section>"
        )
    else:
        # Trang con: dời <p class="lead"> đầu tiên vào trong .page-head
        # (cùng eyebrow + h1), đúng cấu trúc designer đã style.
        lead_html = ""
        m = LEAD_RE.search(body_html)
        if m:
            lead_html = m.group(0)
            body_html = body_html[: m.start()] + body_html[m.end():]
        if eyebrow:
            head_html = (
                '<div class="page-head">'
                f'<p class="page-eyebrow">{eyebrow}</p>'
                f"<h1>{h1}</h1>"
                f"{lead_html}"
                "</div>"
            )
        else:
            head_html = f"<h1>{h1}</h1>{lead_html}"
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_esc} | David English</title>
<meta name="description" content="{desc_esc}">
<meta property="og:title" content="{title_esc} | David English">
<meta property="og:description" content="{desc_esc}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#123a6d">
<link rel="icon" href="/favicon.svg">
<link rel="stylesheet" href="{STYLE}">
<link rel="stylesheet" href="{CHAT_CSS}">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">DAVID <span>ENGLISH</span></a>
    <p class="tagline">{TAGLINE}</p>
    <details class="nav-toggle">
      <summary>☰ Danh mục</summary>
      <nav class="site-nav" aria-label="Điều hướng chính">
{nav_html(active)}
      </nav>
    </details>
    <nav class="site-nav desktop" aria-label="Điều hướng chính">
{nav_html(active)}
    </nav>
  </div>
</header>
<main class="wrap">
{head_html}
{body_html}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p><strong>David English</strong> — Học tiếng Anh miễn phí cho người Việt.</p>
    <p>Mọi câu trả lời của AI đều ghi rõ “AI, chưa duyệt” — chưa được giáo viên duyệt.</p>
    <p><a href="/">Trang chủ</a> · <a href="/tro-chuyen-ai.html">Trò chuyện AI</a> · <a href="/bai-xep-lop.html">Bài xếp lớp</a> · <a href="/tai-nguyen.html">Tài nguyên miễn phí</a> · <a href="/cong-cu/tu-vung.html">Tra từ</a> · <a href="/cong-cu/viet.html">Chữa bài viết</a></p>
    <p class="muted">Trang đang xây dựng — khung sườn v1, nội dung sẽ thêm sau.</p>
  </div>
</footer>
<script src="{CHAT_JS}" defer></script>
</body>
</html>
"""
    rel = "index.html" if path == "/" else path.lstrip("/")
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    return full


def soon(title, lines, extra="", parent=None, prev=None, next=None, ai_question=None, chip=None):
    lis = "".join(f"<li>{l}</li>" for l in lines)
    ai_href = "/tro-chuyen-ai.html"
    if ai_question:
        ai_href += "?q=" + quote(ai_question, safe="")
    links = []
    if parent:
        links.append(f'<a href="{parent[1]}">← {parent[0]}</a>')
    links.append('<a href="/">← Về trang chủ</a>')
    links.append(f'<a href="{ai_href}">Hỏi AI về lộ trình học →</a>')
    sib = []
    if prev:
        sib.append(f'<a href="{prev[1]}">← {prev[0]}</a>')
    if next:
        sib.append(f'<a href="{next[1]}">{next[0]} →</a>')
    sib_html = f"<p>{' · '.join(sib)}</p>\n" if sib else ""
    chip_html = f'<p><span class="level-chip lv-{chip}">{chip.upper()}</span></p>\n' if chip else ""
    return f"""
<section class="section">
<p><span class="badge badge-soon">Sắp có</span></p>
{chip_html}<p>{title}</p>
<ul>{lis}</ul>
{extra}
{sib_html}<p>{" · ".join(links)}</p>
</section>
"""


PAGES = []


def add(path, title, h1, body, active="/", desc=None, eyebrow=None, hero=None):
    PAGES.append((path, title, h1, body, active, desc, eyebrow, hero))


# ---------------- Trang chủ ----------------
add("/", "Trang chủ", "Học tiếng Anh miễn phí, từ đầu tới giỏi",
    f"""
<p><span class="badge">Khung sườn v1</span> Trang đang xây dựng: các mục dưới đây đã có khung, nội dung bài học sẽ thêm sau.</p>
<section class="section">
<div class="cards">
  <article class="card card-tool">{card_icon("tool")}<h2><a href="/bai-xep-lop.html">Bài xếp lớp</a></h2><p>Bản demo với 3 câu mẫu — thử giao diện xếp lớp rồi gợi ý lộ trình học phù hợp.</p></article>
  <article class="card card-level">{card_icon("level")}<h2><a href="/trinh-do/">Theo trình độ (A1–C2)</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>Lộ trình học theo từng cấp độ sẽ có, từ người mới bắt đầu tới nâng cao.</p></article>
  <article class="card card-skill">{card_icon("skill")}<h2><a href="/ky-nang/">Theo kỹ năng</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>Nghe, nói, đọc, viết — sẽ luyện từng kỹ năng riêng, có giải thích tiếng Việt.</p></article>
  <article class="card card-exam">{card_icon("exam")}<h2><a href="/luyen-thi/">Luyện thi</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>IELTS · TOEIC · PTE · TOEFL · VSTEP — sẽ có đề thi thử và mẹo làm bài từng phần.</p></article>
  <article class="card card-kids">{card_icon("kids")}<h2><a href="/tre-em.html">Trẻ em</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>Tiếng Anh cho trẻ em: sẽ có từ vựng theo chủ đề, bài hát, trò chơi, truyện ngắn.</p></article>
  <article class="card card-work">{card_icon("work")}<h2><a href="/cong-viec.html">Tiếng Anh công việc</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>Tiếng Anh cho từng ngành nghề sẽ có: kinh doanh, y tế, công nghệ, du lịch, và hơn nữa.</p></article>
  <article class="card card-abroad">{card_icon("abroad")}<h2><a href="/du-hoc.html">Du học</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>Chuẩn bị tiếng Anh đi du học sẽ có: học bổng, hồ sơ, phỏng vấn, đời sống ở nước ngoài.</p></article>
  <article class="card card-resource">{card_icon("resource")}<h2><a href="/tai-nguyen.html">Tài nguyên miễn phí</a></h2><p>Link tới tài nguyên học tiếng Anh miễn phí chất lượng cao trên mạng (British Council, BBC, Cambridge…).</p></article>
  <article class="card card-book">{card_icon("book")}<h2><a href="/sach/">Sách học</a></h2><p>Hướng dẫn tự học với các sách tiếng Anh phổ biến: Global Success, American English File, Barron's TOEIC, Mindset for IELTS.</p></article>
</div>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Công cụ AI</h2></div>
<div class="cards">
  <article class="card card-tool">{card_icon("tool")}<h2><a href="/tro-chuyen-ai.html">Trò chuyện AI</a></h2><p>Hỏi bất cứ gì về tiếng Anh — ngữ pháp, từ vựng, phát âm, luyện thi. Trả lời bằng tiếng Việt.</p></article>
  <article class="card card-tool">{card_icon("tool")}<h2><a href="/cong-cu/tu-vung.html">Tra từ bằng AI</a></h2><p>Gõ một từ tiếng Anh, AI giải nghĩa bằng tiếng Việt, kèm ví dụ và cách phát âm.</p></article>
  <article class="card card-tool">{card_icon("tool")}<h2><a href="/cong-cu/viet.html">Chữa bài viết bằng AI</a></h2><p>Dán đoạn văn tiếng Anh của bạn, AI sửa lỗi và gợi ý cách viết hay hơn.</p></article>
</div>
</section>
<p class="muted">Mọi câu trả lời của AI đều ghi rõ “AI, chưa duyệt”.</p>
""", desc="David English đang xây dựng thư viện học tiếng Anh miễn phí cho người Việt, giải thích bằng tiếng Việt — mọi trình độ, mọi kỳ thi.",
    hero={
        "eyebrow": TAGLINE,
        "title_html": "Học tiếng Anh <strong>miễn phí</strong>, từ đầu tới giỏi",
        "lead": "David English đang xây dựng thư viện học tiếng Anh miễn phí cho người Việt — không cần đăng ký, giải thích bằng tiếng Việt, từ trẻ em tới người lớn, mọi trình độ, mọi ngành nghề, mọi kỳ thi.",
        "cta_primary": ("Bài xếp lớp", "/bai-xep-lop.html"),
        "cta_secondary": ("Theo trình độ", "/trinh-do/"),
    })

# ---------------- Bài xếp lớp (stub tương tác) ----------------
add("/bai-xep-lop.html", "Bài xếp lớp", "Bài xếp lớp",
    """
<p class="lead">Bài kiểm tra ngắn giúp bạn biết mình đang ở trình độ nào (A1–C2), để chọn lộ trình học phù hợp.</p>
<p><span class="badge">Đang hoàn thiện</span> Đây là bản demo giao diện — bộ câu hỏi chính thức và cách chấm điểm thật chưa có. Kết quả dưới đây chỉ để thử giao diện, chưa dùng để xếp lớp thật.</p>
<section class="section">
<form id="placementForm">
  <fieldset>
    <legend>Câu 1 (mẫu) — Chọn câu đúng ngữ pháp:</legend>
    <label><input type="radio" name="q1" value="0"> She don't like coffee.</label>
    <label><input type="radio" name="q1" value="1"> She doesn't like coffee.</label>
    <label><input type="radio" name="q1" value="0"> She not like coffee.</label>
  </fieldset>
  <fieldset>
    <legend>Câu 2 (mẫu) — “Book” trong câu “I read a book every week” là:</legend>
    <label><input type="radio" name="q2" value="0"> Động từ</label>
    <label><input type="radio" name="q2" value="1"> Danh từ</label>
    <label><input type="radio" name="q2" value="0"> Tính từ</label>
  </fieldset>
  <fieldset>
    <legend>Câu 3 (mẫu) — Câu nào lịch sự nhất khi nhờ giúp đỡ?</legend>
    <label><input type="radio" name="q3" value="0"> Help me now.</label>
    <label><input type="radio" name="q3" value="0"> You help me.</label>
    <label><input type="radio" name="q3" value="1"> Could you help me, please?</label>
  </fieldset>
  <button type="submit" class="btn">Xem kết quả demo</button>
</form>
<div id="placementResult" class="result" hidden></div>
</section>
<p class="muted">Bộ câu hỏi chính thức sẽ có nhiều câu hơn, phủ nghe — nói — đọc — viết, và chấm theo khung CEFR. Khi đó kết quả sẽ dẫn thẳng tới lộ trình học của bạn.</p>
<script>
(function () {
  var form = document.getElementById('placementForm');
  var out = document.getElementById('placementResult');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var score = 0, answered = 0;
    ['q1', 'q2', 'q3'].forEach(function (n) {
      var sel = form.querySelector('input[name="' + n + '"]:checked');
      if (sel) { answered += 1; score += Number(sel.value); }
    });
    if (answered < 3) {
      out.hidden = false;
      out.innerHTML = '<p>Vui lòng trả lời cả 3 câu mẫu.</p>';
      return;
    }
    var level = score === 3 ? 'A2 (tạm tính)' : score === 2 ? 'A1–A2 (tạm tính)' : 'A1 (tạm tính)';
    out.hidden = false;
    out.innerHTML = '<p><strong>Kết quả demo: ' + level + '</strong> — ' + score + '/3 câu đúng.</p>'
      + '<p>Đây là kết quả tạm tính từ 3 câu mẫu, <strong>không phải kết quả xếp lớp thật</strong>. Bộ câu hỏi chính thức đang hoàn thiện.</p>'
      + '<p><a href="/trinh-do/">Xem lộ trình theo trình độ →</a></p>';
  });
})();
</script>
""", active="/bai-xep-lop.html", eyebrow="Bài xếp lớp", desc="Bài xếp lớp demo: 3 câu mẫu để thử giao diện và gợi ý lộ trình học theo trình độ A1–C2. Bộ câu hỏi chính thức đang hoàn thiện.")

# ---------------- Theo trình độ ----------------
LEVELS = [
    ("a1", "A1 — Mới bắt đầu", "Người chưa biết gì hoặc biết rất ít tiếng Anh: bảng chữ cái, chào hỏi, giới thiệu bản thân, số đếm, ngày giờ."),
    ("a2", "A2 — Sơ cấp", "Giao tiếp được trong các tình huống quen thuộc hằng ngày: gia đình, mua sắm, đi lại, công việc đơn giản."),
    ("b1", "B1 — Trung cấp", "Tự xử lý được hầu hết tình huống khi đi du lịch, kể chuyện, bày tỏ ý kiến, đọc hiểu văn bản quen thuộc."),
    ("b2", "B2 — Trung cấp cao", "Giao tiếp trôi chảy với người bản xứ, hiểu ý chính của văn bản phức tạp, viết luận và tranh luận."),
    ("c1", "C1 — Nâng cao", "Dùng tiếng Anh linh hoạt trong học thuật và công việc: đọc tài liệu chuyên ngành, thuyết trình, viết báo cáo."),
    ("c2", "C2 — Thành thạo", "Gần như người bản xứ: hiểu mọi thứ đọc/nghe được, diễn đạt tinh tế, viết văn bản phức tạp."),
]
add("/trinh-do/index.html", "Theo trình độ", "Học theo trình độ (A1–C2)",
    """
<p class="lead">Chọn trình độ của bạn để đi đúng lộ trình — mỗi cấp độ sẽ có từ vựng, ngữ pháp, bài đọc, bài nghe và bài tập riêng.</p>
<p>Chưa biết mình ở đâu? <a href="/bai-xep-lop.html">Làm bài xếp lớp →</a></p>
<section class="section">
<div class="cards">
""" + "".join(
        f'<article class="card card-level">{card_icon("level")}<span class="level-chip lv-{slug}">{slug.upper()}</span><h2><a href="/trinh-do/{slug}.html">{name}</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>{desc}</p></article>'
        for slug, name, desc in LEVELS
    ) + """
</div>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Sách học theo trình độ</h2><p class="section-sub">Hai bộ sách có hướng dẫn tự học chi tiết trên trang này:</p></div>
<ul>
  <li><a href="/sach/global-success.html">Global Success</a> — sách giáo khoa tiếng Anh lớp 3–12, học theo từng unit trên lớp.</li>
  <li><a href="/sach/american-english-file.html">American English File</a> — giáo trình tiếng Anh Mỹ từ A1 đến C1, chọn cuốn theo trình độ của bạn.</li>
</ul>
<p><a href="/sach/">Xem tất cả sách học →</a></p>
</section>
""", active="/trinh-do/", eyebrow="Theo trình độ", desc="Học tiếng Anh theo trình độ A1–C2: chọn cấp độ của bạn để xem lộ trình, từ vựng, ngữ pháp và bài tập sắp có.")
for i, (slug, name, desc) in enumerate(LEVELS):
    prev = (LEVELS[i - 1][0].upper(), f"/trinh-do/{LEVELS[i - 1][0]}.html") if i > 0 else None
    next_ = (LEVELS[i + 1][0].upper(), f"/trinh-do/{LEVELS[i + 1][0]}.html") if i < len(LEVELS) - 1 else None
    last = ("Lộ trình duy trì và nâng cao trình độ C2." if slug == "c2"
            else f"Lộ trình lên cấp độ tiếp theo từ {slug.upper()}.")
    add(f"/trinh-do/{slug}.html", name, name,
        soon("Trang này sẽ có:",
             [f"Mô tả năng lực của trình độ {slug.upper()} theo khung CEFR.",
              "Từ vựng và ngữ pháp trọng tâm của cấp độ này.",
              "Bài học, bài đọc, bài nghe và bài tập — giải thích bằng tiếng Việt.",
              last],
             parent=("Tất cả trình độ", "/trinh-do/"),
             prev=prev, next=next_,
             ai_question=f"Cho tôi lộ trình học tiếng Anh trình độ {slug.upper()}.",
             chip=slug),
        active="/trinh-do/", eyebrow="Theo trình độ", desc=desc)

# ---------------- Theo kỹ năng ----------------
SKILLS = [
    ("nghe", "Nghe", "Luyện nghe hiểu: nghe hội thoại, tin tức, bài giảng — từ chậm tới tốc độ thật, có phụ đề và giải thích."),
    ("noi", "Nói", "Luyện nói: phát âm, ngữ điệu, mẫu câu giao tiếp, luyện nói theo chủ đề, mẹo trả lời phỏng vấn."),
    ("doc", "Đọc", "Luyện đọc hiểu: đọc truyện ngắn, báo, tài liệu — kèm từ vựng và câu hỏi kiểm tra."),
    ("viet", "Viết", "Luyện viết: viết câu, đoạn văn, email, luận — có AI chữa bài và gợi ý cách viết hay hơn."),
]
add("/ky-nang/index.html", "Theo kỹ năng", "Luyện từng kỹ năng",
    """
<p class="lead">Bốn kỹ năng nghe — nói — đọc — viết, sẽ luyện riêng từng kỹ năng với bài tập và giải thích bằng tiếng Việt.</p>
<section class="section">
<div class="cards">
""" + "".join(
        f'<article class="card card-skill">{card_icon("skill")}<h2><a href="/ky-nang/{slug}.html">{name}</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>{desc}</p></article>'
        for slug, name, desc in SKILLS
    ) + """
</div>
</section>
<p>Muốn AI chữa bài viết? <a href="/cong-cu/viet.html">Dùng công cụ chữa bài viết →</a></p>
""", active="/ky-nang/", eyebrow="Theo kỹ năng", desc="Luyện từng kỹ năng nghe, nói, đọc, viết tiếng Anh với bài tập và giải thích bằng tiếng Việt. Các mục đang được xây dựng.")
for i, (slug, name, desc) in enumerate(SKILLS):
    prev = (SKILLS[i - 1][1], f"/ky-nang/{SKILLS[i - 1][0]}.html") if i > 0 else None
    next_ = (SKILLS[i + 1][1], f"/ky-nang/{SKILLS[i + 1][0]}.html") if i < len(SKILLS) - 1 else None
    add(f"/ky-nang/{slug}.html", name, f"Luyện {name.lower()}",
        soon("Trang này sẽ có:",
             [desc,
              "Bài tập theo từng cấp độ (A1–C2).",
              "Mẹo luyện tập hằng ngày và lỗi thường gặp của người Việt."],
             parent=("Tất cả kỹ năng", "/ky-nang/"),
             prev=prev, next=next_,
             ai_question=f"Làm sao để luyện {name.lower()} tiếng Anh hiệu quả?"),
        active="/ky-nang/", eyebrow="Theo kỹ năng", desc=desc)

# ---------------- Luyện thi ----------------
# Hướng dẫn sử dụng sách đã có sẵn cho IELTS và TOEIC — gắn vào trang luyện thi.
LUYEN_THI_GUIDE_EXTRA = {
    "ielts": "<p>Đã có hướng dẫn: <a href=\"/sach/mindset-for-ielts.html\">Học IELTS với sách Mindset for IELTS</a> — chọn đúng cấp độ, học từng unit trong 7 ngày và kế hoạch theo tuần.</p>",
    "toeic": "<p>Đã có hướng dẫn: <a href=\"/sach/barrons-toeic.html\">Học TOEIC với sách Barron's</a> — chọn đúng cuốn, kế hoạch 8 tuần và cách luyện đề hiệu quả.</p>",
}
TESTS = [
    ("ielts", "IELTS", "Luyện thi IELTS (Academic & General): 4 kỹ năng, thang điểm 0–9, đề thi thử và mẹo làm bài từng phần."),
    ("toeic", "TOEIC", "Luyện thi TOEIC (Listening & Reading, Speaking & Writing): thang điểm 10–990, đề thi thử và chiến thuật làm bài."),
    ("pte", "PTE Academic", "Luyện thi PTE Academic: thi trên máy tính, chấm bằng AI, thang điểm 10–90."),
    ("toefl", "TOEFL iBT", "Luyện thi TOEFL iBT: thi trên máy tính, thang điểm 0–120, cho mục đích du học Mỹ và quốc tế."),
    ("vstep", "VSTEP", "Luyện thi VSTEP (khung năng lực 6 bậc của Việt Nam): bậc 3–5 (B1–C1), đề thi thử theo format chính thức."),
]
add("/luyen-thi/index.html", "Luyện thi", "Luyện thi tiếng Anh",
    """
<p class="lead">Chuẩn bị cho kỳ thi của bạn: sẽ có đề thi thử, mẹo làm bài từng phần kèm giải thích bằng tiếng Việt.</p>
<p class="muted">Đề thi thử trên trang là đề tự biên soạn để luyện tập — điểm chỉ là ước lượng, không phải điểm thi thật.</p>
<section class="section">
<div class="cards">
""" + "".join(
        f'<article class="card card-exam">{card_icon("exam")}<h2><a href="/luyen-thi/{slug}.html">{name}</a></h2><p><span class="badge badge-soon">Sắp có</span></p><p>{desc}</p></article>'
        for slug, name, desc in TESTS
    ) + """
</div>
</section>
""", active="/luyen-thi/", eyebrow="Luyện thi", desc="Luyện thi IELTS, TOEIC, PTE, TOEFL và VSTEP: đề thi thử tự biên soạn, mẹo làm bài từng phần, giải thích bằng tiếng Việt.")
for i, (slug, name, desc) in enumerate(TESTS):
    prev = (TESTS[i - 1][1], f"/luyen-thi/{TESTS[i - 1][0]}.html") if i > 0 else None
    next_ = (TESTS[i + 1][1], f"/luyen-thi/{TESTS[i + 1][0]}.html") if i < len(TESTS) - 1 else None
    add(f"/luyen-thi/{slug}.html", name, f"Luyện thi {name}",
        soon("Trang này sẽ có:",
             [desc,
              "Cấu trúc bài thi và thang điểm — kiểm chứng theo nguồn chính thức.",
              "Đề thi thử từng phần + đáp án và giải thích bằng tiếng Việt.",
              "Mẹo làm bài và lỗi thường gặp."],
             extra=LUYEN_THI_GUIDE_EXTRA.get(slug, ""),
             parent=("Tất cả kỳ thi", "/luyen-thi/"),
             prev=prev, next=next_,
             ai_question=f"Lộ trình luyện thi {name} như thế nào?"),
        active="/luyen-thi/", eyebrow="Luyện thi", desc=desc)

# ---------------- Các mục còn lại ----------------
add("/tre-em.html", "Trẻ em", "Tiếng Anh cho trẻ em",
    soon("Trang này sẽ có:",
         ["Từ vựng theo chủ đề quen thuộc với trẻ (gia đình, trường học, động vật, màu sắc…).",
          "Bài hát, truyện ngắn và trò chơi học tiếng Anh.",
          "Bài học ngắn, hình ảnh lớn, phù hợp cho trẻ từ mầm non tới tiểu học.",
          "Hướng dẫn cho phụ huynh cùng học với con."],
         ai_question="Cho tôi lộ trình dạy tiếng Anh cho trẻ em."),
    active="/tre-em.html", eyebrow="Trẻ em",
    desc="Tiếng Anh cho trẻ em: từ vựng theo chủ đề, bài hát, truyện ngắn và trò chơi — bài học ngắn, hình ảnh lớn. Sắp có.")

add("/cong-viec.html", "Tiếng Anh công việc", "Tiếng Anh cho công việc",
    soon("Trang này sẽ có:",
         ["Tiếng Anh theo từng ngành nghề: kinh doanh, y tế, công nghệ thông tin, du lịch, nhà hàng — khách sạn…",
          "Mẫu email, họp, thuyết trình, phỏng vấn xin việc bằng tiếng Anh.",
          "Từ vựng chuyên ngành kèm giải thích tiếng Việt."],
         ai_question="Tôi muốn học tiếng Anh cho công việc, bắt đầu từ đâu?"),
    active="/cong-viec.html", eyebrow="Tiếng Anh công việc",
    desc="Tiếng Anh cho công việc theo từng ngành nghề: mẫu email, họp, thuyết trình và phỏng vấn xin việc bằng tiếng Anh. Sắp có.")

add("/du-hoc.html", "Du học", "Chuẩn bị tiếng Anh đi du học",
    soon("Trang này sẽ có:",
         ["Tiếng Anh cần cho du học: thi IELTS/TOEFL/PTE, viết luận xin học bổng, phỏng vấn visa.",
          "Học bổng toàn phần: Chevening, Fulbright, Australia Awards, DAAD, GKS, MEXT, Erasmus Mundus.",
          "Đời sống ở nước ngoài: nhà ở, ngân hàng, giao tiếp hằng ngày."],
         ai_question="Tôi muốn đi du học, cần chuẩn bị tiếng Anh như thế nào?"),
    active="/du-hoc.html", eyebrow="Du học",
    desc="Chuẩn bị tiếng Anh đi du học: thi IELTS/TOEFL/PTE, học bổng toàn phần, phỏng vấn visa và đời sống ở nước ngoài. Sắp có.")

add("/tai-nguyen.html", "Tài nguyên miễn phí", "Tài nguyên học tiếng Anh miễn phí",
    f"""
<p class="lead">Các tài nguyên học tiếng Anh miễn phí, chất lượng cao — bấm để mở trang gốc (mở tab mới).</p>
<section class="section">
<ul>
  <li><a href="https://learnenglish.britishcouncil.org/" target="_blank" rel="noopener">British Council LearnEnglish</a> — bài học và bài tập tiếng Anh miễn phí của Hội đồng Anh.</li>
  <li><a href="https://www.bbc.co.uk/learningenglish" target="_blank" rel="noopener">BBC Learning English</a> — học tiếng Anh qua tin tức, video và bài nghe của BBC.</li>
  <li><a href="https://www.cambridgeenglish.org/" target="_blank" rel="noopener">Cambridge English</a> — tài liệu và bài kiểm tra trình độ của Cambridge.</li>
  <li><a href="https://www.usalearns.org/" target="_blank" rel="noopener">USA Learns</a> — khóa học tiếng Anh trực tuyến miễn phí cho người mới bắt đầu.</li>
  <li><a href="https://learningenglish.voanews.com/" target="_blank" rel="noopener">VOA Learning English</a> — tin tức tiếng Anh đọc chậm, dành cho người học.</li>
</ul>
</section>
<p class="muted">Chỉ liên kết, không sao chép tài nguyên của người khác — tôn trọng bản quyền. Giới thiệu ngắn bằng tiếng Việt cho từng link sẽ được bổ sung sau.</p>
<section class="section section-alt">
<div class="section-head"><h2>Hướng dẫn sử dụng sách</h2><p class="section-sub">Hướng dẫn tự học chi tiết với các sách tiếng Anh phổ biến — cách chọn đúng cuốn, học từng bài và kế hoạch theo tuần:</p></div>
<ul>
  <li><a href="/sach/global-success.html">Global Success</a> — sách giáo khoa tiếng Anh lớp 3–12 theo chương trình GDPT 2018.</li>
  <li><a href="/sach/american-english-file.html">American English File</a> — giáo trình tiếng Anh Mỹ của Oxford, từ A1 đến C1.</li>
  <li><a href="/sach/barrons-toeic.html">Barron's TOEIC</a> — luyện thi TOEIC Listening &amp; Reading với bộ sách của Lin Lougheed.</li>
  <li><a href="/sach/mindset-for-ielts.html">Mindset for IELTS</a> — luyện thi IELTS Academic theo từng cấp độ, từ Foundation đến Level 3.</li>
</ul>
<p><a href="/">← Về trang chủ</a> · <a href="/tro-chuyen-ai.html?q={quote("Có những tài nguyên miễn phí nào để học tiếng Anh?", safe="")}">Hỏi AI về tài nguyên học tiếng Anh →</a></p>
</section>
""", active="/tai-nguyen.html", eyebrow="Tài nguyên miễn phí",
    desc="Tài nguyên học tiếng Anh miễn phí: British Council LearnEnglish, BBC Learning English, Cambridge, USA Learns, VOA Learning English.")

# ---------------- Trò chuyện AI (trang riêng) ----------------
add("/tro-chuyen-ai.html", "Trò chuyện AI", "Trò chuyện AI",
    """
<p class="lead">Hỏi bất cứ gì về tiếng Anh — ngữ pháp, từ vựng, phát âm, luyện thi, lộ trình học. AI trả lời bằng tiếng Việt.</p>
<p><span class="badge">AI, chưa duyệt</span> Mọi câu trả lời do AI soạn, chưa được giáo viên duyệt — hãy đối chiếu với sách và giáo viên của bạn.</p>
<section class="section">
<div id="deChatPage"><noscript><p>Trò chuyện AI cần bật JavaScript để hiển thị. Bạn vẫn có thể xem các mục khác của trang, hoặc bật JavaScript rồi tải lại trang.</p></noscript></div>
</section>
<script>
(function () {
  var q = new URLSearchParams(window.location.search).get('q');
  if (!q) return;
  var tries = 0;
  var timer = setInterval(function () {
    tries++;
    var input = document.querySelector('#deChatPage .de-chat-foot input');
    if (input) { input.value = q; input.focus(); clearInterval(timer); }
    else if (tries > 10) { clearInterval(timer); }
  }, 200);
})();
</script>
<p class="muted">Chat dùng cùng hệ thống với khung chat góc màn hình. Nếu tính năng chưa sẵn sàng, trang sẽ báo “đang được chuẩn bị”.</p>
""", active="/tro-chuyen-ai.html", eyebrow="Công cụ AI",
    desc="Trò chuyện với AI về tiếng Anh: ngữ pháp, từ vựng, phát âm, luyện thi và lộ trình học — trả lời bằng tiếng Việt.")

# ---------------- Công cụ AI ----------------
add("/cong-cu/tu-vung.html", "Tra từ bằng AI", "Tra từ bằng AI",
    """
<p class="lead">Gõ một từ hoặc cụm từ tiếng Anh — AI giải nghĩa bằng tiếng Việt, kèm ví dụ, cách phát âm và từ đồng nghĩa.</p>
<p><span class="badge">AI, chưa duyệt</span> Nghĩa do AI đưa ra, chưa được giáo viên duyệt.</p>
<section class="section">
<form id="vocabForm">
  <label for="vocabWord">Từ hoặc cụm từ tiếng Anh:</label>
  <input id="vocabWord" type="text" maxlength="100" placeholder="VD: perseverance" autocomplete="off">
  <button type="submit" class="btn">Tra từ</button>
</form>
<div id="vocabResult" class="result" hidden></div>
</section>
<p class="muted">Nếu công cụ chưa sẵn sàng, trang sẽ báo “đang được chuẩn bị” — bạn thử lại sau.</p>
<script>
(function () {
  var form = document.getElementById('vocabForm');
  var input = document.getElementById('vocabWord');
  var out = document.getElementById('vocabResult');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var w = input.value.trim();
    if (!w) {
      out.hidden = false;
      out.innerHTML = '<p>Vui lòng nhập một từ hoặc cụm từ tiếng Anh trước đã nhé.</p>';
      input.focus();
      return;
    }
    out.hidden = false;
    out.innerHTML = '<p>Đang tra…</p>';
    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'Giải thích từ/cụm từ tiếng Anh này bằng tiếng Việt: ' + w + '. Cho nghĩa, phiên âm, 2 ví dụ, và 1 từ đồng nghĩa.', mode: 'vocab' })
    })
      .then(function (r) { return r.json().then(function (d) { return { status: r.status, d: d }; }); })
      .then(function (res) {
        var d = res.d || {};
        if (res.status === 200 && d.answer) {
          out.innerHTML = '<p>' + d.answer.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>') + '</p><p class="muted">AI, chưa duyệt.</p>';
        } else {
          out.innerHTML = '<p>' + (d.message || 'Có lỗi xảy ra, mời thử lại sau.') + '</p>';
        }
      })
      .catch(function () { out.innerHTML = '<p>Không kết nối được, thử lại sau.</p>'; });
  });
})();
</script>
""", active=None, eyebrow="Công cụ AI", desc="Tra từ tiếng Anh bằng AI: giải nghĩa bằng tiếng Việt, kèm ví dụ, cách phát âm và từ đồng nghĩa.")

add("/cong-cu/viet.html", "Chữa bài viết bằng AI", "Chữa bài viết bằng AI",
    """
<p class="lead">Dán đoạn văn tiếng Anh của bạn (tối đa 350 ký tự) — AI chỉ ra lỗi ngữ pháp, từ vựng và gợi ý cách viết hay hơn, giải thích bằng tiếng Việt.</p>
<p><span class="badge">AI, chưa duyệt</span> Góp ý do AI đưa ra, chưa được giáo viên duyệt.</p>
<section class="section">
<form id="writingForm">
  <label for="writingText">Đoạn văn tiếng Anh của bạn:</label>
  <textarea id="writingText" rows="6" maxlength="350" placeholder="VD: Yesterday I go to school and meet my friend. We was very happy…"></textarea>
  <p class="muted" id="writingCount">0/350 ký tự</p>
  <button type="submit" class="btn">Nhờ AI chữa bài</button>
</form>
<div id="writingResult" class="result" hidden></div>
</section>
<p class="muted">Nếu công cụ chưa sẵn sàng, trang sẽ báo “đang được chuẩn bị” — bạn thử lại sau.</p>
<script>
(function () {
  var form = document.getElementById('writingForm');
  var input = document.getElementById('writingText');
  var out = document.getElementById('writingResult');
  var count = document.getElementById('writingCount');
  input.addEventListener('input', function () {
    count.textContent = input.value.length + '/350 ký tự';
  });
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var t = input.value.trim();
    if (!t) {
      out.hidden = false;
      out.innerHTML = '<p>Vui lòng nhập đoạn văn tiếng Anh trước đã nhé.</p>';
      input.focus();
      return;
    }
    out.hidden = false;
    out.innerHTML = '<p>Đang chữa bài…</p>';
    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'Chữa đoạn văn tiếng Anh sau đây. Liệt kê lỗi ngữ pháp và từ vựng, sửa từng lỗi, giải thích bằng tiếng Việt, rồi gợi ý bản viết lại hay hơn: ' + t, mode: 'writing' })
    })
      .then(function (r) { return r.json().then(function (d) { return { status: r.status, d: d }; }); })
      .then(function (res) {
        var d = res.d || {};
        if (res.status === 200 && d.answer) {
          out.innerHTML = '<p>' + d.answer.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>') + '</p><p class="muted">AI, chưa duyệt.</p>';
        } else {
          out.innerHTML = '<p>' + (d.message || 'Có lỗi xảy ra, mời thử lại sau.') + '</p>';
        }
      })
      .catch(function () { out.innerHTML = '<p>Không kết nối được, thử lại sau.</p>'; });
  });
})();
</script>
""", active=None, eyebrow="Công cụ AI", desc="Chữa bài viết tiếng Anh bằng AI: chỉ ra lỗi ngữ pháp, từ vựng và gợi ý cách viết hay hơn, giải thích bằng tiếng Việt.")

# ---------------- Sách học (hướng dẫn sử dụng sách) ----------------
# Nội dung các trang dưới đây được chuyển nguyên văn từ các bản thảo
# hướng dẫn đã kiểm chứng trong ~/workspace/david-english-content/guides/
# — chỉ chuyển định dạng Markdown sang HTML, không thêm link hay thông tin mới.
add("/sach/index.html", "Sách học", "Hướng dẫn sử dụng sách học",
    f"""
<p class="lead">Hướng dẫn tự học với các sách tiếng Anh phổ biến — cách chọn đúng cuốn, học từng bài và lên kế hoạch theo tuần, kèm link mua sách và nghe audio đã kiểm chứng.</p>
<section class="section">
<div class="cards">
<article class="card card-book">{card_icon("book")}<h2><a href="/sach/global-success.html">Hướng dẫn học với sách Global Success</a></h2><p>Cách tự học hiệu quả với sách giáo khoa tiếng Anh Global Success (lớp 3–12): cấu trúc sách, cách học từng unit, kế hoạch theo tuần.</p></article><article class="card card-book">{card_icon("book")}<h2><a href="/sach/american-english-file.html">Hướng dẫn học với sách American English File</a></h2><p>Hướng dẫn tự học American English File (Oxford) từ A1 đến C1: chọn đúng trình độ, học từng File, luyện nghe–nói và mua sách chính hãng.</p></article><article class="card card-book">{card_icon("book")}<h2><a href="/sach/barrons-toeic.html">Hướng dẫn học với sách Barron&#x27;s TOEIC</a></h2><p>Hướng dẫn học TOEIC với bộ sách Barron&#x27;s của Lin Lougheed: chọn đúng cuốn, học theo tuần và luyện đề hiệu quả.</p></article><article class="card card-book">{card_icon("book")}<h2><a href="/sach/mindset-for-ielts.html">Hướng dẫn học với sách Mindset for IELTS</a></h2><p>Hướng dẫn tự học bộ sách Mindset for IELTS theo từng cấp độ, từ Foundation đến Level 3, kèm kế hoạch tuần và mẹo thi.</p></article>
</div>
</section>
<p class="muted">Sẽ bổ sung thêm hướng dẫn cho các sách khác — hiện mới có 4 cuốn trên đây.</p>
""", active="/sach/", eyebrow="Sách học",
    desc="Hướng dẫn tự học với các sách tiếng Anh phổ biến: Global Success, American English File, Barron's TOEIC, Mindset for IELTS.")
add("/sach/global-success.html", "Hướng dẫn học với sách Global Success", "Học tiếng Anh với sách Global Success",
    guide_sections("""
<p><a href="/sach/">← Tất cả sách học</a></p>
<p class="lead">Cách tự học hiệu quả với sách giáo khoa tiếng Anh Global Success (lớp 3–12): cấu trúc sách, cách học từng unit, kế hoạch theo tuần.</p>
<h2>Sách này là gì</h2>
<p>Global Success là bộ sách giáo khoa tiếng Anh của Nhà xuất bản Giáo dục Việt Nam, được biên soạn theo Chương trình Giáo dục phổ thông 2018 môn Tiếng Anh. Bộ sách được xây dựng đồng bộ, thống nhất từ lớp 1 đến lớp 12, do GS.TS. Hoàng Văn Vân làm Tổng chủ biên, với đội ngũ tác giả là người Việt Nam.</p>
<p>Về chuyên môn, Nhà xuất bản Giáo dục Việt Nam hợp tác với Macmillan Education ở bậc Tiểu học và Pearson Education ở bậc Trung học cơ sở và Trung học phổ thông.</p>
<p>Bộ sách hướng đến việc phát triển năng lực giao tiếp: học sinh học từ vựng, phát âm, ngữ pháp và luyện cả bốn kỹ năng Nghe – Nói – Đọc – Viết qua các chủ đề gần gũi với đời sống hằng ngày, kết hợp văn hóa Việt Nam và văn hóa các nước nói tiếng Anh. Cuối mỗi nhóm bài học có phần ôn tập (Review), và cuối sách có bảng tra từ vựng (Glossary) cùng bản đồ nội dung (Book Map) giúp tra cứu nhanh chủ đề, từ vựng, ngữ pháp và kỹ năng của từng unit.</p>
<p>Đi kèm sách học sinh còn có Sách bài tập và Sách giáo viên, cùng học liệu điện tử (xem mục &quot;Mua sách và nghe audio ở đâu&quot;).</p>
<p>Lưu ý về bản quyền: Global Success là sách giáo khoa thương mại có bản quyền. Trang này chỉ là hướng dẫn tự học do chúng tôi tự viết — chúng tôi không đăng lại nội dung, bài tập hay file nghe của sách. Bạn cần có sách in chính hãng (hoặc bản điện tử chính thức) để học theo hướng dẫn dưới đây.</p>
<h2>Sách này dành cho ai</h2>
<ul><li><strong>Học sinh từ lớp 3 đến lớp 12</strong> đang học tiếng Anh theo chương trình GDPT 2018 tại trường — đây là sách giáo khoa chính trên lớp của rất nhiều trường trên cả nước.</li><li><strong>Phụ huynh</strong> muốn kèm con học ở nhà theo đúng tiến độ trên lớp, đặc biệt ở bậc tiểu học, nơi trẻ cần người lớn hướng dẫn nghe và đọc cùng.</li><li><strong>Người tự học lại từ đầu</strong> muốn có một lộ trình có sẵn: mỗi lớp là một nấc, học hết một lớp thì lên lớp tiếp theo.</li><li><strong>Giáo viên và gia sư</strong> cần một khung tham khảo để lên kế hoạch ôn tập theo unit cho học sinh.</li></ul>
<p>Hướng dẫn này tập trung vào lớp 3–12. Bộ sách có cả sách lớp 1 và lớp 2, nhưng ở hai lớp đầu tiếng Anh chỉ là môn làm quen, nên cách học khác hẳn (chủ yếu là nghe, hát và chơi) và không nằm trong trọng tâm của bài này.</p>
<h2>Cấu trúc sách</h2>
<p>Mỗi lớp có một cuốn sách học sinh (ở tiểu học thường chia thành hai tập, một tập cho mỗi học kỳ). Số unit đã kiểm chứng được:</p>
<ul><li><strong>Lớp 3:</strong> 20 unit, chia thành hai tập (Tập 1: Starter và Unit 1–10; Tập 2: Unit 11–20). Cứ sau mỗi 5 unit có một phần Review và Fun time để ôn tập qua trò chơi, bài hát và hoạt động nhóm.</li><li><strong>Lớp 6, 7, 8, 9:</strong> mỗi lớp 12 unit. Ví dụ lớp 7 có Review sau Unit 3, 6, 9 và 12; lớp 8 có 4 phần Review và Glossary cuối sách.</li><li><strong>Lớp 10 và lớp 12:</strong> mỗi lớp 10 unit và 4 phần Review. Ví dụ lớp 10: Review 1 ôn Unit 1–3, Review 2 ôn Unit 4–5, Review 3 ôn Unit 6–8, Review 4 ôn Unit 9–10.</li></ul>
<p>Cấu trúc một unit ở bậc THCS và THPT (lớp 6–12) gồm các phần sau, theo thứ tự trong sách:</p>
<ol><li><strong>Getting Started</strong> — mở đầu chủ đề bằng một đoạn hội thoại hoặc tình huống quen thuộc, giới thiệu từ vựng và ý chính của unit.</li><li><strong>Language</strong> — từ vựng, phát âm và ngữ pháp trọng tâm của unit.</li><li><strong>Reading</strong> — đọc hiểu một bài đọc theo chủ đề, luyện cách tìm thông tin cụ thể và thông tin tổng quát.</li><li><strong>Speaking</strong> — luyện nói theo chủ đề, thường là trình bày ngắn hoặc trao đổi theo cặp/nhóm.</li><li><strong>Listening</strong> — nghe và tìm thông tin.</li><li><strong>Writing</strong> — viết đoạn văn hoặc email ngắn theo chủ đề.</li><li><strong>Communication and Culture / CLIL</strong> — giao tiếp mở rộng và kiến thức liên môn, văn hóa.</li><li><strong>Looking Back &amp; Project</strong> — ôn lại kiến thức của unit và làm một dự án nhỏ (thuyết trình, áp phích, bài viết ngắn) để vận dụng những gì đã học.</li></ol>
<p>Ở bậc tiểu học (lớp 3–5), mỗi unit gọn hơn, thường gồm phần mở đầu (Getting Started) và ba bài học (Lesson 1, Lesson 2, Lesson 3), xoay quanh nghe – nói – đọc – viết ở mức đơn giản, gắn với chủ đề như bản thân, bạn bè, gia đình, trường học, đồ chơi và vật nuôi.</p>
<p>Điểm chung của mọi lớp: từ vựng và ngữ pháp của một unit luôn phục vụ cho chủ đề của unit đó, và bốn kỹ năng được luyện xen kẽ trong cùng một chủ đề chứ không tách riêng. Vì vậy, học một unit nghĩa là đi hết một vòng: biết từ mới, hiểu mẫu câu, rồi dùng chúng để nghe, nói, đọc và viết.</p>
<h2>Cách học một bài (unit)</h2>
<p>Dưới đây là quy trình tự học một unit trong khoảng 4–5 buổi, mỗi buổi 30–45 phút. Áp dụng cho lớp 6–12; với lớp 3–5, rút ngắn mỗi buổi còn 20–30 phút và nhờ phụ huynh hoặc thầy cô hỗ trợ phần nghe.</p>
<p><strong>Buổi 1 — Mở đầu và từ vựng (Getting Started + Language)</strong></p>
<ul><li>Đọc lướt toàn bộ unit một lượt để biết chủ đề và xem unit này dạy những gì. Nhìn vào Book Map ở đầu sách để nắm nhanh từ vựng, ngữ pháp và kỹ năng của unit.</li><li>Học từ vựng trước: đọc to từng từ mới, nghe phát âm trong audio chính thức, lặp lại, rồi tự đặt một câu đơn giản với mỗi từ. Viết từ mới ra sổ hoặc thẻ học, kèm phiên âm và nghĩa tiếng Việt do chính bạn tra và ghi — đừng chỉ đọc lướt.</li><li>Học phần phát âm: luyện riêng các âm được nêu trong unit, đọc to và ghi âm lại giọng mình để so sánh với audio.</li><li>Học ngữ pháp: đọc phần giải thích, tự viết 3–5 câu ví dụ của riêng mình với mỗi cấu trúc. Câu ví dụ phải nói về đời sống thật của bạn thì mới nhớ lâu.</li></ul>
<p><strong>Buổi 2 — Đọc và nghe (Reading + Listening)</strong></p>
<ul><li>Đọc bài đọc một lượt không tra từ điển để nắm ý chính, rồi đọc lại lần hai, tra những từ chưa biết và gạch chân câu chứa thông tin quan trọng.</li><li>Sau khi đọc, tự tóm tắt bài đọc bằng 3–5 câu tiếng Anh của mình. Đây là bước nhiều người bỏ qua nhưng lại là bước giúp nhớ từ vựng lâu nhất.</li><li>Nghe bài nghe lần một chỉ để hiểu ý chung; nghe lần hai và ghi lại các thông tin cụ thể (số, tên, địa điểm, ý kiến); nghe lần ba vừa nghe vừa đọc theo transcript (nếu có trong sách điện tử chính thức) để bắt những chỗ mình nghe sót.</li></ul>
<p><strong>Buổi 3 — Nói và viết (Speaking + Writing)</strong></p>
<ul><li>Nói: dùng các câu hỏi gợi ý trong sách để tự nói 1–2 phút về chủ đề của unit, ghi âm lại và nghe lại để sửa phát âm và ngữ pháp. Nếu có bạn học cùng, hãy đóng vai hội thoại với nhau; nếu học một mình, hãy nói trước gương hoặc thu âm.</li><li>Viết: viết đoạn văn theo yêu cầu trong sách, rồi tự kiểm tra lại: mỗi câu có đúng cấu trúc ngữ pháp của unit không, có dùng được từ mới của unit không, có đủ ý không. Hôm sau đọc lại bài viết của mình một lần nữa — lỗi thường lộ ra sau một đêm.</li></ul>
<p><strong>Buổi 4 — Ôn lại và làm dự án (Communication and Culture / CLIL + Looking Back &amp; Project)</strong></p>
<ul><li>Làm phần ôn tập cuối unit (Looking Back) như một bài kiểm tra nhỏ: làm xong mới đối chiếu đáp án, ghi lại những câu sai vào sổ lỗi.</li><li>Làm Project: dù là áp phích, bài thuyết trình ngắn hay đoạn văn, hãy làm thật thay vì bỏ qua — đây là phần duy nhất buộc bạn phải dùng tiếng Anh một cách tự do, không theo khuôn mẫu có sẵn.</li><li>Làm bài tập tương ứng trong Sách bài tập (nếu có) để củng cố thêm.</li></ul>
<p><strong>Khi gặp phần Review (sau mỗi nhóm unit)</strong></p>
<ul><li>Dành riêng một buổi cho Review: làm toàn bộ phần Review như một bài kiểm tra, tính giờ. Sau đó xem lại các unit đã học, chỉ ôn những chỗ mình làm sai trong Review — đừng học lại từ đầu cả nhóm unit.</li></ul>
<h2>Kế hoạch học theo tuần</h2>
<p>Kế hoạch mẫu dưới đây giả định bạn học theo tiến độ trên lớp (khoảng 1 unit mỗi 1–2 tuần) và có thể tự học thêm 4 buổi mỗi tuần, mỗi buổi 30–45 phút. Nếu bạn đang ôn thi hoặc bị chậm tiến độ, hãy tăng lên 5–6 buổi/tuần; nếu chỉ cần theo kịp trên lớp, 3 buổi/tuần là đủ.</p>
<p><strong>Tuần học một unit mới (lặp lại cho mỗi unit):</strong></p>
<table><thead><tr><th>Buổi</th><th>Nội dung</th><th>Thời gian</th></tr></thead><tbody><tr><td>Thứ 2</td><td>Buổi 1: mở đầu + từ vựng + phát âm + ngữ pháp</td><td>40 phút</td></tr><tr><td>Thứ 4</td><td>Buổi 2: đọc hiểu + nghe</td><td>40 phút</td></tr><tr><td>Thứ 6</td><td>Buổi 3: nói + viết</td><td>40 phút</td></tr><tr><td>Chủ nhật</td><td>Buổi 4: ôn lại + dự án + Sách bài tập</td><td>45 phút</td></tr></tbody></table>
<p><strong>Tuần có phần Review (sau mỗi 3–5 unit tùy lớp):</strong></p>
<table><thead><tr><th>Buổi</th><th>Nội dung</th><th>Thời gian</th></tr></thead><tbody><tr><td>Thứ 2</td><td>Làm toàn bộ phần Review, tính giờ như kiểm tra thật</td><td>40 phút</td></tr><tr><td>Thứ 4</td><td>Chữa lỗi: ôn lại chỉ những unit có câu sai, làm lại các câu sai</td><td>40 phút</td></tr><tr><td>Thứ 6</td><td>Ôn từ vựng của cả nhóm unit bằng thẻ học; viết lại một đoạn văn cũ cho hay hơn</td><td>30 phút</td></tr><tr><td>Chủ nhật</td><td>Nghỉ hoặc nghe lại audio của các unit đã học như nghe thụ động</td><td>Tùy ý</td></tr></tbody></table>
<p><strong>Quy tắc duy trì:</strong></p>
<ul><li><strong>Từ vựng ôn theo lịch lặp lại:</strong> từ mới của unit này ôn lại sau 1 ngày, 3 ngày, 1 tuần và 1 tháng. Chỉ cần 5 phút mỗi lần với thẻ học.</li><li><strong>Nghe mỗi ngày, dù chỉ 10 phút:</strong> nghe lại audio của unit đang học khi đi xe, nấu ăn hay trước khi ngủ. Nghe thụ động không thay được nghe chủ động, nhưng giúp tai quen với âm điệu.</li><li><strong>Một sổ lỗi duy nhất:</strong> mọi lỗi ngữ pháp, phát âm và từ vựng dùng sai đều ghi vào một cuốn sổ, xem lại vào đầu mỗi tuần Review.</li><li><strong>Đừng học vượt quá 2 unit cùng lúc.</strong> Học dồn nhiều unit một lúc khiến từ vựng các unit lẫn vào nhau và không unit nào chắc.</li></ul>
<h2>Mẹo học hiệu quả</h2>
<ol><li><strong>Học từ vựng theo chủ đề của unit, không học từ rời rạc.</strong> Từ vựng trong sách đã được chọn để phục vụ cho chủ đề — học theo cụm và đặt câu với bối cảnh của unit sẽ nhớ lâu hơn học danh sách từ riêng lẻ.</li><li><strong>Nghe trước khi đọc transcript.</strong> Với mọi bài nghe, hãy nghe ít nhất một lần mà không nhìn chữ. Đọc transcript ngay từ đầu sẽ khiến bạn tưởng mình nghe được, nhưng thực ra là đang đọc.</li><li><strong>Nói to, đừng học thầm.</strong> Tiếng Anh là kỹ năng miệng. Đọc to từ mới, đọc to bài đọc, tự nói to phần Speaking — học thầm chỉ luyện được mắt, không luyện được miệng.</li><li><strong>Viết lại bằng lời của mình.</strong> Sau mỗi bài đọc, tóm tắt lại bằng 3–5 câu của mình; sau mỗi unit, viết một đoạn ngắn về chủ đề đó. Viết là cách kiểm tra xem bạn có thực sự hiểu hay chỉ nhận ra mặt chữ.</li><li><strong>Dùng Glossary cuối sách làm công cụ ôn tập.</strong> Trước mỗi bài kiểm tra, hãy lật Glossary và tự kiểm tra: che nghĩa đi, đọc từ tiếng Anh và nói nghĩa; từ nào không nhớ thì đánh dấu ôn lại.</li><li><strong>Làm Project thật, dù không bị chấm điểm.</strong> Phần dự án cuối unit là nơi duy nhất bạn được dùng tiếng Anh tự do. Bỏ qua nó là bỏ qua một nửa giá trị của unit.</li><li><strong>Học theo nhóm 2–3 người nếu có thể.</strong> Phần Speaking và Project hiệu quả hơn hẳn khi có người đối thoại thật. Hai người có thể thay nhau hỏi – đáp theo gợi ý trong sách.</li><li><strong>Với học sinh tiểu học:</strong> phụ huynh nên nghe audio cùng con và cho con nhắc lại, thay vì để con tự học một mình với sách. Trẻ nhớ qua tai và qua chơi (bài hát, trò chơi trong phần Fun time) nhiều hơn qua đọc – chép.</li></ol>
<h2>Lỗi thường gặp</h2>
<ul><li><strong>Chỉ làm bài tập mà bỏ phần nghe.</strong> Sách in không kèm đĩa; audio nằm trên nền tảng điện tử chính thức. Nhiều học sinh học cả năm không nghe một lần, đến khi kiểm tra nghe thì không theo kịp. Hãy nghe audio của unit ngay trong tuần học unit đó.</li><li><strong>Chép đáp án thay vì tự làm.</strong> Các trang giải bài tập lan truyền trên mạng khiến việc chép đáp án rất dễ — nhưng đáp án chép được không bao giờ thành kiến thức. Hãy tự làm trước, chỉ dùng đáp án để đối chiếu sau.</li><li><strong>Học từ vựng mà không học phát âm.</strong> Biết mặt chữ nhưng đọc sai thì khi nghe sẽ không nhận ra từ đó, và khi nói người khác cũng không hiểu. Luôn nghe và đọc to mỗi từ mới.</li><li><strong>Học ngữ pháp thuộc lòng công thức nhưng không đặt câu.</strong> Công thức chỉ nhớ được khi đã dùng. Mỗi cấu trúc mới cần ít nhất 3–5 câu ví dụ do chính bạn viết về đời sống thật của mình.</li><li><strong>Bỏ qua phần Review và Looking Back.</strong> Đây là hai phần được thiết kế để gom kiến thức lại trước khi kiểm tra. Bỏ qua chúng đồng nghĩa với việc để kiến thức rơi rớt dần sau mỗi unit.</li><li><strong>Học dồn trước kỳ thi.</strong> Học 5 unit trong một tuần trước khi thi chỉ giúp nhớ ngắn hạn. Lịch ôn lặp lại (1 ngày – 3 ngày – 1 tuần – 1 tháng) trong mục kế hoạch ở trên hiệu quả hơn nhiều.</li><li><strong>Mua nhầm bộ sách khác.</strong> Theo chương trình GDPT 2018 có nhiều bộ sách tiếng Anh khác nhau (Global Success chỉ là một trong số đó). Khi mua sách, hãy đối chiếu đúng tên &quot;Global Success&quot;, đúng lớp và đúng tập với sách trường con bạn đang dùng, và mua ở nhà sách uy tín để tránh sách in lậu, thiếu trang hoặc không có mã kích hoạt bản điện tử.</li><li><strong>Dùng file PDF trôi nổi trên mạng.</strong> Ngoài việc vi phạm bản quyền, các file này thường thiếu trang, sai thứ tự hoặc không có audio đi kèm. Hãy dùng sách in chính hãng và các nền tảng chính thức dưới đây.</li></ul>
<h2>Mua sách và nghe audio ở đâu</h2>
<p>Chỉ liệt kê các kênh đã kiểm chứng. Không tải sách từ các trang chia sẻ file không rõ nguồn gốc.</p>
<ul><li><strong>Nhà xuất bản Giáo dục Việt Nam — bài giới thiệu chính thức về bộ sách Global Success:</strong> <a href="https://nxbgd.vn/bai-viet/global-success-bo-sach-giao-khoa-tieng-anh-cua-nguoi-viet-nam" target="_blank" rel="noopener">https://nxbgd.vn/bai-viet/global-success-bo-sach-giao-khoa-tieng-anh-cua-nguoi-viet-nam</a> — đã mở và đọc trực tiếp ngày 23/11/2026; bài viết xác nhận bộ sách dùng cho lớp 1–12, Tổng chủ biên Hoàng Văn Vân, đối tác Macmillan (tiểu học) và Pearson (THCS, THPT), cùng các kênh học liệu số chính thức.</li><li><strong>Học Liệu (hoclieu.vn) — thư viện học liệu số chính thức của Nhà xuất bản Giáo dục Việt Nam:</strong> <a href="https://hoclieu.vn/" target="_blank" rel="noopener">https://hoclieu.vn/</a> — đã mở trực tiếp ngày 23/11/2026, trang tải được; đây là nơi đọc sách điện tử và dùng học liệu số của bộ sách theo như bài viết chính thức của NXB.</li><li><strong>Sách Mềm (sachmem.vn) — hệ thống phần mềm hỗ trợ giảng dạy và học tập của bộ sách:</strong> <a href="https://sachmem.vn/" target="_blank" rel="noopener">https://sachmem.vn/</a> — đã mở trực tiếp ngày 23/11/2026; trang giới thiệu xác nhận lộ trình xuyên suốt lớp 1–12 và các học liệu đi kèm (sách học sinh, sách giáo viên, sách bài tập, giáo án, bài giảng).</li><li><strong>Mua sách in:</strong> mua tại các nhà sách lớn, uy tín (nhà sách của NXB Giáo dục Việt Nam hoặc các chuỗi nhà sách lớn) và kiểm tra sách có tem, mã kích hoạt bản điện tử đầy đủ. Chúng tôi không đưa link tới một cửa hàng cụ thể vì chưa kiểm chứng được từng cửa hàng; bài viết chính thức của NXB có nhắc tới cửa hàng trực tuyến edubook.com.vn, nhưng chúng tôi đã thử mở trang này ngày 23/11/2026 và không tải được, nên không đưa làm link mua hàng đã kiểm chứng (xem mục &quot;Chưa kiểm chứng được&quot;).</li></ul>
<h2>Nguồn đã kiểm chứng</h2>
<ul><li>Bài viết chính thức của Nhà xuất bản Giáo dục Việt Nam: &quot;Global Success: Bộ sách giáo khoa tiếng Anh của người Việt Nam&quot; — <a href="https://nxbgd.vn/bai-viet/global-success-bo-sach-giao-khoa-tieng-anh-cua-nguoi-viet-nam" target="_blank" rel="noopener">https://nxbgd.vn/bai-viet/global-success-bo-sach-giao-khoa-tieng-anh-cua-nguoi-viet-nam</a> — đã mở và đọc trực tiếp ngày 23/11/2026. Xác nhận: bộ sách từ lớp 1 đến lớp 12; Tổng chủ biên GS.TS. Hoàng Văn Vân, tác giả 100% người Việt Nam; hợp tác Macmillan Education (tiểu học) và Pearson Education (THCS, THPT); hệ thống học liệu tại hoclieu.vn; Sách Mềm tại sachmem.vn; cửa hàng trực tuyến edubook.com.vn.</li><li>Trang chủ Học Liệu — <a href="https://hoclieu.vn/" target="_blank" rel="noopener">https://hoclieu.vn/</a> — đã mở trực tiếp ngày 23/11/2026, trang tải được.</li><li>Trang chủ Sách Mềm — <a href="https://sachmem.vn/" target="_blank" rel="noopener">https://sachmem.vn/</a> — đã mở trực tiếp ngày 23/11/2026; xác nhận lộ trình lớp 1–12 và các học liệu đi kèm.</li><li>Hội thảo giới thiệu sách giáo khoa lớp 3 (Sở GD&amp;ĐT Hải Phòng): <a href="http://anhp.vn/hoi-thao-gioi-thieu-sach-giao-khoa-lop-3-d46091.html" target="_blank" rel="noopener">http://anhp.vn/hoi-thao-gioi-thieu-sach-giao-khoa-lop-3-d46091.html</a> — xác nhận Tiếng Anh 3 Global Success (Hoàng Văn Vân) nằm trong danh mục sách lớp 3 được phê duyệt theo Quyết định 438 ngày 28/01/2022, dùng từ năm học 2022–2023; bộ sách theo khung năng lực ngoại ngữ 6 bậc và chương trình GDPT 2018.</li><li>Tổng quan sách Tiếng Anh 3 Global Success — <a href="https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-3" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-3</a> và <a href="https://apaxfranklin.com/sach-tieng-anh-3-global-success-pdf/" target="_blank" rel="noopener">https://apaxfranklin.com/sach-tieng-anh-3-global-success-pdf/</a> — xác nhận lớp 3 có 20 unit, hai tập, Review và Fun time sau mỗi 5 unit, cấu trúc mỗi unit gồm Getting Started, Lesson 1–3.</li><li>Tổng quan sách Tiếng Anh 6 Global Success — <a href="https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-6" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-6</a> — xác nhận lớp 6 có 12 unit, hai tập, tác giả và đối tác Pearson.</li><li>Tổng quan sách Tiếng Anh 8 Global Success — <a href="https://vus.edu.vn/blog-vus/tieng-anh-8?leadcdpid=sitemap" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/tieng-anh-8?leadcdpid=sitemap</a> và <a href="https://apaxfranklin.com/sach-tieng-anh-8-global-success-pdf/" target="_blank" rel="noopener">https://apaxfranklin.com/sach-tieng-anh-8-global-success-pdf/</a> — xác nhận lớp 8 có 12 unit, 4 phần Review, Glossary; audio nằm trên bản điện tử chính thức (hoclieu.vn và hanhtrangso.nxbgd.vn).</li><li>Tổng quan sách Tiếng Anh 10 Global Success — <a href="https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-10" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-10</a> — xác nhận lớp 10 có 10 unit, 4 phần Review, Book Map, Glossary, các phần Communication and Culture/CLIL và Looking Back &amp; Project.</li><li>Danh mục unit lớp 7, 8, 9, 12 — <a href="https://www.studywithping.com/ngu-phap" target="_blank" rel="noopener">https://www.studywithping.com/ngu-phap</a> và <a href="https://timdapan.com/sach-giao-khoa/tieng-anh-7-global-success" target="_blank" rel="noopener">https://timdapan.com/sach-giao-khoa/tieng-anh-7-global-success</a> — xác nhận lớp 7, 8, 9 mỗi lớp 12 unit, lớp 12 có 10 unit; lớp 7 có Review sau Unit 3, 6, 9, 12.</li></ul>
<h2>Chưa kiểm chứng được</h2>
<ul><li><strong>Số unit của lớp 1, 2, 4, 5 và lớp 11:</strong> chúng tôi chưa kiểm chứng riêng từng lớp này nên không ghi con số cụ thể trong bài. Chỉ ghi những lớp đã có nguồn xác nhận (lớp 3: 20 unit; lớp 6–9: 12 unit; lớp 10 và 12: 10 unit).</li><li><strong>Nền tảng hanhtrangso.nxbgd.vn:</strong> một nguồn thứ cấp cho biết đây là nền tảng sách điện tử chính thức, mở bằng mã kích hoạt dưới tem cào trong sách in. Chúng tôi đã thử mở trang này ngày 23/11/2026 nhưng trang không tải được (hết thời gian chờ), nên chưa xác nhận trực tiếp được và không đưa làm link đã kiểm chứng.</li><li><strong>Cửa hàng trực tuyến edubook.com.vn:</strong> được chính bài viết của NXB nêu là cửa hàng online, nhưng chúng tôi đã thử mở ngày 23/11/2026 và trang không tải được, nên không đưa làm link mua hàng đã kiểm chứng.</li><li><strong>Giá bán từng cuốn và giá sách điện tử:</strong> giá thay đổi theo thời điểm và nhà sách; chúng tôi không ghi giá cụ thể. Hãy xem giá tại nhà sách nơi bạn mua.</li><li><strong>Danh sách nhà sách cụ thể bán sách chính hãng (ví dụ Fahasa):</strong> chưa kiểm chứng từng nhà sách nên không liệt kê; hãy mua ở nhà sách lớn, uy tín và kiểm tra tem, mã kích hoạt.</li><li><strong>Ứng dụng di động riêng của bộ sách:</strong> chúng tôi chưa tìm thấy và chưa kiểm chứng được có ứng dụng chính thức nào mang tên Global Success trên kho ứng dụng; học liệu số chính thức hiện nay dùng qua web (hoclieu.vn, sachmem.vn).</li><li><strong>Mức độ tương ứng với khung năng lực (CEFR) của từng lớp:</strong> chưa kiểm chứng được con số chính thức cho từng lớp nên không ghi trong bài.</li></ul>
<p><a href="/sach/">← Tất cả sách học</a> · <a href="/">← Về trang chủ</a> · <a href="/tro-chuyen-ai.html?q=H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20t%C3%B4i%20h%E1%BB%8Dc%20v%E1%BB%9Bi%20s%C3%A1ch%20Global%20Success">Hỏi AI về sách này →</a></p>
"""), active="/sach/", eyebrow="Sách học",
    desc="Cách tự học hiệu quả với sách giáo khoa tiếng Anh Global Success (lớp 3–12): cấu trúc sách, cách học từng unit, kế hoạch theo tuần.")
add("/sach/american-english-file.html", "Hướng dẫn học với sách American English File", "Học tiếng Anh với sách American English File",
    guide_sections("""
<p><a href="/sach/">← Tất cả sách học</a></p>
<p class="lead">Hướng dẫn tự học American English File (Oxford) từ A1 đến C1: chọn đúng trình độ, học từng File, luyện nghe–nói và mua sách chính hãng.</p>
<h2>Sách này là gì</h2>
<p><em>American English File</em> là bộ giáo trình tiếng Anh Mỹ dành cho người lớn và thanh thiếu niên, do Nhà xuất bản Đại học Oxford (Oxford University Press) phát hành. Các tác giả chính là Christina Latham-Koenig, Clive Oxenden và Jerry Lambert (Paul Seligson đồng tác giả ở một số trình độ của các bản trước; Kate Chomacki tham gia từ bản mới nhất).</p>
<p>Điểm nổi bật của bộ sách, theo mô tả của nhà xuất bản, là mỗi bài học kết hợp cân bằng bốn yếu tố: ngữ pháp (Grammar), từ vựng (Vocabulary), phát âm (Pronunciation) và phát triển kỹ năng (Skills Development) — với mục tiêu cuối cùng là giúp người học nói được, nói tự tin, chứ không chỉ làm đúng bài tập trên giấy.</p>
<p><strong>Lưu ý về bản (edition) — rất quan trọng khi mua sách:</strong> hiện có hai bản đang lưu hành song song:</p>
<ul><li><strong>Bản thứ 3 (Third Edition, khoảng 2019–2021):</strong> đây là bản đang được bán rộng rãi tại Việt Nam và là bản mà hầu hết người học Việt Nam đang dùng.</li><li><strong>Bản thứ 4 (Fourth Edition, phát hành từ 2025–2026):</strong> bản mới nhất, đang được ra mắt theo từng trình độ. Bản này chuyển phần học trực tuyến sang nền tảng Oxford English Hub, kèm theo các gói Digital Pack (sách in + sách điện tử + tài nguyên trực tuyến). Vì bản 4 đang ra mắt theo giai đoạn, không phải trình độ nào cũng đã có đầy đủ mọi thành phần tại thời điểm viết bài này.</li></ul>
<p>Hướng dẫn này dùng được cho cả hai bản vì khung cấu trúc (File, Grammar Bank, Vocabulary Bank, Practical English, Review &amp; Check) được giữ nguyên về cơ bản. Khi mua sách, hãy kiểm tra rõ mình đang mua bản 3 hay bản 4, và mua đúng Student Book + Workbook của cùng một bản, cùng một trình độ.</p>
<p><strong>Lưu ý bản quyền:</strong> <em>American English File</em> là sách thương mại có bản quyền của Oxford University Press. Hướng dẫn này chỉ tóm tắt thông tin chung về bộ sách và đưa ra phương pháp tự học do chúng tôi tự viết — không sao chép, không đăng lại bất kỳ bài tập, đoạn hội thoại hay đoạn văn nào trong sách, và không cung cấp bản PDF hay file audio của sách. Audio và bài luyện trực tuyến chỉ đi kèm khi bạn mua sách chính hãng (mã truy cập in trong sách).</p>
<h2>Sách này dành cho ai</h2>
<p>Bộ sách gồm 6 cuốn, đi từ trình độ vỡ lòng đến nâng cao. Bảng dưới đây là mức CEFR <strong>ước chừng</strong> (các nguồn ghi hơi khác nhau ở ranh giới giữa các trình độ, ví dụ Level 1 được ghi là A1 hoặc A1–A2) — hãy dùng bảng này để định hướng, rồi tự kiểm tra trình độ thực tế của mình trước khi mua:</p>
<table><thead><tr><th>Cuốn</th><th>Trình độ ước chừng</th><th>Phù hợp với bạn nếu…</th></tr></thead><tbody><tr><td>Starter</td><td>A1</td><td>Mới bắt đầu gần như từ đầu, cần học bảng chữ cái, số đếm, câu chào hỏi và động từ <em>be</em></td></tr><tr><td>Level 1</td><td>A1–A2</td><td>Đã biết những câu giao tiếp rất cơ bản, muốn nói được về bản thân, gia đình, công việc hằng ngày</td></tr><tr><td>Level 2</td><td>A2–B1</td><td>Đã giao tiếp được ở mức đơn giản, muốn kể chuyện quá khứ, nói về kế hoạch tương lai</td></tr><tr><td>Level 3</td><td>B1–B2</td><td>Đã giao tiếp khá, muốn thảo luận ý kiến, tranh luận nhẹ và đọc–nghe các chủ đề đời sống, xã hội</td></tr><tr><td>Level 4</td><td>B2</td><td>Đã khá vững, muốn diễn đạt tinh tế hơn, dùng từ nối và cấu trúc phức tạp một cách tự nhiên</td></tr><tr><td>Level 5</td><td>C1</td><td>Đã giỏi, muốn dùng tiếng Anh linh hoạt, chính xác ở mức nâng cao trong học tập và công việc</td></tr></tbody></table>
<p>Cách chọn cuốn đúng:</p>
<ol><li><strong>Đừng chọn theo cảm tính.</strong> Nếu bạn đã học tiếng Anh ở trường nhưng lâu không dùng, hãy bắt đầu thấp hơn một nấc so với mức bạn nghĩ — học lại chắc nền tảng nhanh hơn là vật lộn ở cuốn quá khó.</li><li><strong>Làm bài kiểm tra trình độ trước khi mua.</strong> Oxford và nhiều trung tâm có bài test xếp lớp miễn phí; hoặc đơn giản hơn: mở thử vài trang đầu của cuốn bạn định mua — nếu bạn hiểu dưới 70% từ vựng và ngữ pháp trong đó, hãy xuống một trình độ.</li><li><strong>Một cuốn học trong vài tháng, không phải vài tuần.</strong> Đừng mua cả bộ 6 cuốn cùng lúc. Mua một cuốn, học xong rồi mới mua cuốn tiếp theo.</li></ol>
<p>Bộ sách phù hợp nhất với người tự học có kỷ luật, người học ở trung tâm dùng giáo trình này, và người muốn cải thiện khả năng <strong>nói</strong> tiếng Anh Mỹ. Nó không phải là sách luyện thi (không bám theo dạng đề TOEIC/IELTS), nên nếu mục tiêu duy nhất của bạn là thi lấy chứng chỉ trong thời gian ngắn, hãy dùng thêm tài liệu luyện thi chuyên biệt bên cạnh.</p>
<h2>Cấu trúc sách</h2>
<p>Mỗi cuốn Student Book được chia thành các đơn vị lớn gọi là <strong>File</strong> (tương đương với &quot;unit&quot; trong các giáo trình khác). Số File cụ thể khác nhau theo trình độ — xem mục &quot;Chưa kiểm chứng được&quot; ở cuối bài. Bên trong mỗi File thường có:</p>
<ul><li><strong>Các bài A, B, C:</strong> mỗi bài tập trung vào một chủ điểm ngữ pháp, một nhóm từ vựng và một điểm phát âm, kết hợp nghe, đọc và nói. Bài học thường bắt đầu bằng một đoạn nghe hoặc đọc ngắn, rồi mới đến phần ngữ pháp và luyện nói.</li><li><strong>Practical English:</strong> các đoạn hội thoại tình huống đời thực (ví dụ: ở khách sạn, hỏi đường, mua sắm) kèm video, giúp bạn luyện nghe hiểu và nói theo ngữ cảnh.</li><li><strong>Review &amp; Check:</strong> sau mỗi 2 File có một phần ôn tập tổng hợp — kiểm tra nhanh ngữ pháp, từ vựng và phát âm của 2 File vừa học. Đây là phần nhiều người bỏ qua nhưng lại là phần quan trọng nhất để biết mình đã nắm bài hay chưa.</li><li><strong>Video Listening:</strong> ở bản thứ 3, các File chẵn có thêm hoạt động nghe–xem video (phim tài liệu ngắn và kịch ngắn). Bản thứ 4 tăng thêm vai trò của video trong bài học.</li><li><strong>Communication:</strong> phần bài tập nói theo cặp/nhóm ở cuối sách, dùng khi luyện nói với bạn học.</li><li><strong>Writing:</strong> hướng dẫn viết từng dạng bài ngắn (ví dụ: email, đoạn mô tả) ở cuối sách.</li><li><strong>Listening:</strong> phần luyện nghe bổ sung.</li></ul>
<p>Phần tham khảo ở cuối sách gồm:</p>
<ul><li><strong>Grammar Bank:</strong> giải thích ngữ pháp của từng bài kèm bài tập — đây là &quot;sách giáo khoa ngữ pháp mini&quot; của bạn, dùng để tra cứu mỗi khi quên quy tắc.</li><li><strong>Vocabulary Bank:</strong> danh sách từ vựng theo chủ điểm, có audio mẫu để nghe và lặp lại.</li><li><strong>Sound Bank:</strong> bảng âm tiếng Anh Mỹ với ví dụ mẫu — dùng để tra cách phát âm và luyện từng âm.</li><li><strong>Irregular verbs:</strong> bảng động từ bất quy tắc.</li><li><strong>Audioscripts:</strong> lời thoại đầy đủ của các bài nghe trong sách.</li></ul>
<p>Ngoài Student Book, bộ sách còn có:</p>
<ul><li><strong>Workbook:</strong> sách bài tập làm thêm ở nhà, bám sát từng bài trong Student Book. Workbook có đáp án để tự kiểm tra (bản có key).</li><li><strong>Online Practice (bản 3) / Oxford English Hub (bản 4):</strong> bài luyện trực tuyến cho từng File, có chấm điểm và theo dõi tiến độ. Lưu ý: theo thông báo chính thức trên trang Online Practice, hệ thống này đang chuyển sang Oxford English Hub và trang cũ sẽ đóng vào ngày 25/06/2027 — người mua bản 4 dùng Oxford English Hub ngay từ đầu.</li><li><strong>Ứng dụng Say It:</strong> ứng dụng luyện phát âm của Oxford, có kèm bảng âm và danh sách từ vựng của bộ sách (tính năng cụ thể có thể khác nhau theo phiên bản ứng dụng).</li></ul>
<h2>Cách học một bài (unit)</h2>
<p>Dưới đây là quy trình gợi ý cho <strong>một bài A, B hoặc C</strong> trong một File. Quy trình này là phương pháp tự học do chúng tôi đề xuất, không phải hướng dẫn chính thức của nhà xuất bản. Thời gian gợi ý: khoảng 45–60 phút cho một bài.</p>
<p><strong>Bước 1 — Nghe/đọc trước, đoán nghĩa (10 phút).</strong> Mở bài nghe hoặc bài đọc đầu bài. Nghe một lần không nhìn chữ (hoặc đọc lướt một lần) và tự hỏi: đoạn này nói về cái gì? Đừng tra từ điển ngay. Việc đoán nghĩa trước giúp tai và mắt bạn làm việc chủ động thay vì chỉ &quot;đọc đáp án&quot;.</p>
<p><strong>Bước 2 — Học từ vựng của bài (10 phút).</strong> Mở Vocabulary Bank của bài đó. Nghe audio mẫu của từng từ, lặp lại thành tiếng, và ghi từ mới vào sổ theo nhóm chủ điểm (không ghi từ đơn lẻ, rời rạc). Với mỗi từ, ghi thêm một câu ví dụ ngắn <strong>do chính bạn đặt</strong> — câu của bạn sẽ nhớ lâu hơn câu chép trong sách.</p>
<p><strong>Bước 3 — Học ngữ pháp qua Grammar Bank (10 phút).</strong> Đọc phần giải thích ngữ pháp trong bài, sau đó mở Grammar Bank ở cuối sách để đọc quy tắc đầy đủ và làm bài tập trong đó. Quy tắc cần nhớ: hiểu quy tắc rồi mới làm bài tập; nếu làm sai quá nửa, quay lại đọc quy tắc một lần nữa thay vì cố làm tiếp.</p>
<p><strong>Bước 4 — Luyện phát âm (5–10 phút).</strong> Mở Sound Bank, nghe và lặp lại các âm được đánh dấu trong bài. Đọc to các câu ví dụ trong bài, chú ý trọng âm từ và nhịp câu. Nếu có ứng dụng Say It, dùng nó để tự kiểm tra và so sánh với mẫu.</p>
<p><strong>Bước 5 — Nói thành tiếng (10 phút).</strong> Làm phần nói cuối bài <strong>bằng miệng, thành tiếng</strong>, kể cả khi học một mình: tự trả lời câu hỏi, tự kể lại nội dung bài nghe bằng lời của mình trong 1–2 phút. Đây là bước tạo ra khác biệt giữa &quot;học xong&quot; và &quot;dùng được&quot;. Nếu có bạn học, hai người hỏi–đáp theo phần Communication ở cuối sách.</p>
<p><strong>Bước 6 — Làm Workbook ngay trong ngày (10–15 phút).</strong> Làm bài tập Workbook tương ứng với bài vừa học, rồi tự chấm bằng đáp án. Ghi lại các lỗi sai vào một trang &quot;lỗi của tôi&quot; — cuối tuần xem lại trang này trước khi làm Review &amp; Check.</p>
<p>Sau mỗi 2 File, dành một buổi riêng chỉ để làm <strong>Review &amp; Check</strong>: làm nghiêm túc như một bài kiểm tra nhỏ, không mở sách xem trước. Phần nào làm sai nhiều thì quay lại học lại File đó trước khi sang File mới.</p>
<h2>Kế hoạch học theo tuần</h2>
<p>Kế hoạch dưới đây giả định bạn học <strong>5 buổi/tuần, mỗi buổi 45–60 phút</strong>, và học <strong>một File trong khoảng 1–2 tuần</strong> tùy trình độ (trình độ thấp học chậm hơn, trình độ cao học nhanh hơn). Đây là kế hoạch gợi ý — hãy điều chỉnh theo thời gian thực tế của bạn, nhưng giữ nguyên nguyên tắc: học đều mỗi ngày tốt hơn học dồn một ngày.</p>
<table><thead><tr><th>Buổi</th><th>Việc làm</th></tr></thead><tbody><tr><td>Thứ 2</td><td>Học bài A của File mới theo 6 bước ở trên</td></tr><tr><td>Thứ 3</td><td>Học bài B của File mới theo 6 bước ở trên</td></tr><tr><td>Thứ 4</td><td>Học bài C của File mới; ôn lại từ vựng bài A và B bằng cách đặt câu mới</td></tr><tr><td>Thứ 5</td><td>Practical English + Video Listening của File đó (nghe 2–3 lần: lần 1 hiểu ý chính, lần 2 nghe chi tiết, lần 3 nói theo)</td></tr><tr><td>Thứ 6</td><td>Làm Workbook của cả File; viết một đoạn ngắn (5–8 câu) về chủ đề của File, dùng từ vựng và ngữ pháp vừa học</td></tr><tr><td>Thứ 7</td><td>Nghỉ hoặc ôn nhẹ: nghe lại các bài nghe trong tuần, đọc lại trang &quot;lỗi của tôi&quot;</td></tr><tr><td>Chủ nhật</td><td>Nghỉ. Nếu đang ở cuối File chẵn (File 2, 4, 6…), dùng buổi này làm Review &amp; Check thay cho nghỉ</td></tr></tbody></table>
<p><strong>Mốc kiểm tra theo tháng:</strong> sau mỗi 2 File (khoảng 2–4 tuần), tự đánh giá bằng 3 câu hỏi: (1) Tôi có kể lại được nội dung chính của mỗi bài bằng tiếng Anh trong 1 phút không? (2) Tôi có làm đúng ít nhất 80% phần Review &amp; Check không? (3) Tôi có phát âm đúng các âm mới trong Sound Bank không? Nếu câu nào trả lời &quot;không&quot;, hãy ôn lại trước khi sang File tiếp theo — đừng vội.</p>
<p><strong>Thời gian hoàn thành một cuốn:</strong> với nhịp 5 buổi/tuần như trên, một cuốn thường cần vài tháng. Đừng đặt mục tiêu &quot;xong một cuốn trong một tháng&quot; — học ngôn ngữ là tích lũy, không phải chạy đua.</p>
<h2>Mẹo học hiệu quả</h2>
<ol><li><strong>Nói to, đừng học thầm.</strong> Tiếng Anh là kỹ năng nói. Mọi bài tập trong sách — kể cả bài tập ngữ pháp — đều nên đọc đề và đáp án thành tiếng ít nhất một lần.</li><li><strong>Nghe lặp lại, đừng nghe một lần rồi bỏ.</strong> Một đoạn nghe nên nghe ít nhất 3 lần: hiểu ý chính, nghe chi tiết, rồi nói theo (shadowing) — nghe một câu, dừng lại, lặp lại giống ngữ điệu nhất có thể.</li><li><strong>Học từ theo cụm, không học từ đơn.</strong> Ghi &quot;make a decision&quot; thay vì chỉ ghi &quot;decision&quot;; ghi &quot;interested in&quot; thay vì chỉ ghi &quot;interested&quot;. Từ đi kèm giới từ và động từ mới là thứ bạn sẽ dùng khi nói.</li><li><strong>Dùng Sound Bank như từ điển phát âm.</strong> Mỗi khi gặp từ mới, tra cách đọc trong Sound Bank hoặc nghe audio trong Vocabulary Bank trước khi tự đoán cách đọc. Đoán sai rồi đọc sai nhiều lần sẽ rất khó sửa.</li><li><strong>Ôn theo chu kỳ, không ôn một lần.</strong> Từ mới học hôm nay nên được xem lại sau 1 ngày, sau 3 ngày và sau 1 tuần. Cách đơn giản nhất: mỗi buổi học, dành 5 phút đầu xem lại từ của 2 buổi trước.</li><li><strong>Viết ít nhưng viết thật.</strong> Một đoạn 5–8 câu dùng đúng từ vựng và ngữ pháp vừa học có giá trị hơn một bài dài chép từ mẫu. Sau khi viết, tự đọc to và sửa lỗi.</li><li><strong>Đừng bỏ phần Review &amp; Check.</strong> Đó là &quot;bài kiểm tra&quot; duy nhất của bạn khi tự học. Bỏ qua nó nghĩa là bạn không bao giờ biết mình thực sự nắm bài hay chỉ &quot;cảm thấy&quot; đã hiểu.</li><li><strong>Học cùng một người bạn nếu có thể.</strong> Phần Communication và các bài nói theo cặp trong sách được thiết kế cho hai người. Một bạn học giúp bạn buộc phải nói thật, thay vì chỉ nghĩ trong đầu.</li></ol>
<h2>Lỗi thường gặp</h2>
<ul><li><strong>Chọn sai trình độ.</strong> Mua cuốn quá khó rồi nản và bỏ sau 2 tuần là lỗi phổ biến nhất. Dấu hiệu: bạn phải tra từ điển ở gần như mọi câu. Hãy xuống một trình độ — học lại nền tảng không phải là thụt lùi.</li><li><strong>Chỉ làm Workbook, bỏ nghe và bỏ nói.</strong> Workbook dễ chấm điểm nên tạo cảm giác &quot;đang tiến bộ&quot;, nhưng nghe và nói mới là mục tiêu của bộ sách. Nếu một tuần bạn không mở audio lần nào, bạn đang học sai cách.</li><li><strong>Học từ vựng mà không học phát âm.</strong> Biết nghĩa mà đọc sai thì người nghe vẫn không hiểu. Luôn nghe mẫu trước khi học thuộc một từ mới.</li><li><strong>Bỏ qua Practical English và video.</strong> Nhiều người coi đây là phần &quot;phụ&quot; và nhảy thẳng sang bài tiếp theo. Thực ra đây là phần gần nhất với giao tiếp thật — nơi bạn học cách nói trong tình huống cụ thể.</li><li><strong>Học File mới khi File cũ chưa vững.</strong> Không làm Review &amp; Check, không ôn lại, cứ học tiếp. Hậu quả là càng về sau càng đuối vì ngữ pháp và từ vựng cũ chưa thành phản xạ.</li><li><strong>Dùng bản PDF hoặc audio lậu trôi nổi trên mạng.</strong> Ngoài việc vi phạm bản quyền của Oxford University Press, các bản này thường là bản cũ, thiếu trang, audio lỗi hoặc không khớp với sách in — và không có mã Online Practice/Oxford English Hub. Hãy mua sách chính hãng để có đủ audio, video và quyền truy cập bài luyện trực tuyến.</li><li><strong>Mua nhầm bản hoặc nhầm trình độ.</strong> Ví dụ: mua Student Book bản 3 nhưng Workbook bản 4, hoặc mua Level 3 trong khi đang cần Level 2. Luôn kiểm tra kỹ tên sách, số trình độ và chữ &quot;Third Edition&quot;/&quot;Fourth Edition&quot; trên bìa trước khi thanh toán.</li></ul>
<h2>Mua sách và nghe audio ở đâu</h2>
<p>Chỉ mua sách chính hãng — sách thật luôn kèm mã truy cập Online Practice (bản 3) hoặc Oxford English Hub (bản 4) và audio/video đầy đủ. Các liên kết dưới đây đều đã được chúng tôi mở và kiểm tra trực tiếp vào ngày 23/11/2026; nội dung và tình trạng của trang có thể thay đổi sau thời điểm đó, và giá bán không được ghi ở đây vì giá thay đổi theo thời điểm và nơi bán.</p>
<ul><li><strong>Trang chính thức của Oxford University Press (Úc) — Student Book Level 5 bản 3:</strong> mô tả đầy đủ về bản 3, gồm Online Practice, Sound Bank videos và video listening. Đã kiểm chứng bằng cách mở trực tiếp trang này. <a href="https://www.oup.com.au/books/english-language-teaching/primary-courses/9780194907088" target="_blank" rel="noopener">https://www.oup.com.au/books/english-language-teaching/primary-courses/9780194907088</a></li><li><strong>Trang chính thức của Oxford University Press (Ấn Độ) — trang giới thiệu bộ sách:</strong> xác nhận bộ sách, tác giả Christina Latham-Koenig và Clive Oxenden, và triết lý &quot;ngôn ngữ + động lực = cơ hội nói&quot;. Đã kiểm chứng bằng cách mở trực tiếp trang này. <a href="https://india.oup.com/content/series/american-english-file/" target="_blank" rel="noopener">https://india.oup.com/content/series/american-english-file/</a></li><li><strong>Trang chính thức của Oxford University Press (Argentina) — bộ sách bản 3:</strong> liệt kê đủ 6 trình độ Starter, 1, 2, 3, 4, 5 của bản 3. Đã kiểm chứng bằng cách mở trực tiếp trang này. <a href="https://argentina.oup.com/en/collections/american-english-file" target="_blank" rel="noopener">https://argentina.oup.com/en/collections/american-english-file</a></li><li><strong>English File Online Practice (trang chính thức của Oxford):</strong> nơi đăng nhập Online Practice bằng mã trong sách; trang này thông báo hệ thống đang chuyển sang Oxford English Hub và sẽ đóng vào ngày 25/06/2027, không nhận đăng ký mới sau ngày 29/01/2027. Đã kiểm chứng bằng cách mở trực tiếp trang này. <a href="https://englishfileonline.com" target="_blank" rel="noopener">https://englishfileonline.com</a></li><li><strong>Trung tâm trợ giúp Oxford English Hub (trang chính thức của Oxford):</strong> hướng dẫn bắt đầu dùng Oxford English Hub cho học viên, gồm cách tìm khóa học và dùng tài liệu. Đã kiểm chứng bằng cách mở trực tiếp trang này. <a href="https://support.englishhub.oup.com/" target="_blank" rel="noopener">https://support.englishhub.oup.com/</a></li><li><strong>Browns Books (nhà sách Anh) — Student Book Level 2 bản 4 kèm Digital Pack:</strong> xác nhận bản 4 gồm sách in + 2 năm truy cập Student e-Book, Workbook e-Book, Student Resources và Exam Confidence trên Oxford English Hub. Đã kiểm chứng bằng cách mở trực tiếp trang này. <a href="https://www.brownsbfs.co.uk/Product/Latham-Koenig-Christina/American-English-File-fourth-edition-Level-2-Student-Book-with-Digital-Pack/9780194176576" target="_blank" rel="noopener">https://www.brownsbfs.co.uk/Product/Latham-Koenig-Christina/American-English-File-fourth-edition-Level-2-Student-Book-with-Digital-Pack/9780194176576</a></li><li><strong>Fahasa (nhà sách Việt Nam) — trang sản phẩm American English File:</strong> Fahasa có bán các cuốn trong bộ sách; hãy tìm đúng tên cuốn, đúng trình độ và đúng bản (Third/Fourth Edition) trên trang Fahasa trước khi đặt mua. Đã kiểm chứng bằng cách mở trực tiếp trang sản phẩm này. <a href="https://www.fahasa.com/american-english-file-4-student-book.html" target="_blank" rel="noopener">https://www.fahasa.com/american-english-file-4-student-book.html</a></li></ul>
<p>Ngoài ra, bạn có thể tìm mua tại các nhà sách ngoại văn lớn ở Việt Nam và các sàn thương mại điện tử — nhưng chỉ mua từ gian hàng chính hãng hoặc nhà sách uy tín, kiểm tra kỹ bìa sách, chữ &quot;Third Edition&quot;/&quot;Fourth Edition&quot;, số trình độ và mã truy cập còn nguyên vẹn trong sách. Tránh các gian hàng bán &quot;bản PDF&quot;, &quot;file mềm&quot; hoặc sách photo giá rẻ bất thường — đó là hàng vi phạm bản quyền và thường thiếu audio, thiếu mã truy cập.</p>
<h2>Nguồn đã kiểm chứng</h2>
<p>Tất cả các nguồn dưới đây đã được mở trực tiếp hoặc đọc kết quả tìm kiếm trong ngày 23/11/2026. Không nguồn nào trong số này là bản PDF hay audio của sách — chúng tôi không tải xuống bất kỳ nội dung nào của sách.</p>
<ul><li><a href="https://www.oup.com.au/books/english-language-teaching/primary-courses/9780194907088" target="_blank" rel="noopener">https://www.oup.com.au/books/english-language-teaching/primary-courses/9780194907088</a> — Trang chính thức của Oxford University Press (Úc) cho Student Book Level 5 bản 3; xác nhận: bản 3, Online Practice, Sound Bank videos, video listening ở các File chẵn, cân bằng Grammar–Vocabulary–Pronunciation–Skills Development trong mỗi File.</li><li><a href="https://india.oup.com/content/series/american-english-file/" target="_blank" rel="noopener">https://india.oup.com/content/series/american-english-file/</a> — Trang chính thức của Oxford University Press (Ấn Độ) cho bộ sách; xác nhận: tên bộ sách, tác giả Christina Latham-Koenig và Clive Oxenden, mô tả &quot;grammar, vocabulary, and pronunciation practice in every lesson&quot;.</li><li><a href="https://argentina.oup.com/en/collections/american-english-file" target="_blank" rel="noopener">https://argentina.oup.com/en/collections/american-english-file</a> — Trang chính thức của Oxford University Press (Argentina); xác nhận: bản 3 gồm đủ 6 trình độ Starter, 1, 2, 3, 4, 5.</li><li><a href="https://englishfileonline.com" target="_blank" rel="noopener">https://englishfileonline.com</a> — Trang Online Practice chính thức của Oxford (đã mở trực tiếp); xác nhận: hệ thống đang chuyển sang Oxford English Hub trong tháng 7/2026, không nhận đăng ký/kích hoạt mã mới sau 29/01/2027, trang đóng ngày 25/06/2027.</li><li><a href="https://support.englishhub.oup.com/" target="_blank" rel="noopener">https://support.englishhub.oup.com/</a> — Trang trợ giúp chính thức của Oxford English Hub (đã mở trực tiếp); xác nhận: đây là nền tảng hỗ trợ học viên dùng tài liệu Oxford, có hướng dẫn bắt đầu và tìm khóa học.</li><li><a href="https://www.brownsbfs.co.uk/Product/Latham-Koenig-Christina/American-English-File-fourth-edition-Level-2-Student-Book-with-Digital-Pack/9780194176576" target="_blank" rel="noopener">https://www.brownsbfs.co.uk/Product/Latham-Koenig-Christina/American-English-File-fourth-edition-Level-2-Student-Book-with-Digital-Pack/9780194176576</a> — Nhà sách Browns Books (Anh); xác nhận: bản 4 Level 2, sách in + 2 năm truy cập Student e-Book, Workbook e-Book, Student Resources, Exam Confidence trên Oxford English Hub; ngày xuất bản 26/08/2025.</li><li><a href="https://www.fahasa.com/american-english-file-4-student-book.html" target="_blank" rel="noopener">https://www.fahasa.com/american-english-file-4-student-book.html</a> — Trang sản phẩm của Fahasa (đã mở trực tiếp); xác nhận: Fahasa có bán sách American English File tại Việt Nam.</li><li>Kết quả tìm kiếm Google Books cho American English File Level 2 (ISBN 9780194906524, Oxford University Press, xuất bản 29/08/2019) — xác nhận: nhà xuất bản Oxford University Press, mô tả &quot;proven balance of Grammar, Vocabulary, Pronunciation, and Skills Development in every File&quot;.</li><li>Trang bìa và trang bản quyền của Teacher&#x27;s Guide bản 3 (qua kết quả tìm kiếm) — xác nhận: tác giả Christina Latham-Koenig, Clive Oxenden, Jerry Lambert; Paul Seligson là đồng tác giả gốc của English File 1 và 2; cấu trúc gồm Student Book with Online Practice, Workbook, Teacher&#x27;s Guide with Teacher Resource Center, Classroom Presentation Tool.</li><li>Trang bìa và trang bản quyền của Teacher&#x27;s Guide bản 4 (qua kết quả tìm kiếm) — xác nhận: bản 4 có các tác giả Christina Latham-Koenig, Clive Oxenden, Kate Chomacki, Jerry Lambert; bản quyền © Oxford University Press 2026, xuất bản lần đầu 2026.</li><li>Kết quả tìm kiếm trên Fahasa và Tiki — xác nhận: Fahasa niêm yết Student Book Level 5 bản 3 với Online Practice; Tiki có bán các Multi-Pack bản 2 (một số đã hết hàng). Giá bán không được ghi lại vì thay đổi theo thời điểm.</li></ul>
<h2>Chưa kiểm chứng được</h2>
<ul><li><strong>Đường dẫn chính xác của trang giới thiệu bộ sách trên elt.oup.com:</strong> chúng tôi đã tìm kiếm nhưng không lấy được đường dẫn trang series <em>American English File</em> trên tên miền elt.oup.com để mở trực tiếp, nên không đưa liên kết này vào bài. Bạn có thể tự tìm trên trang Oxford ELT theo tên bộ sách.</li><li><strong>Đường dẫn đăng nhập trực tiếp của Oxford English Hub:</strong> chúng tôi chỉ mở được trang trợ giúp support.englishhub.oup.com; địa chỉ trang đăng nhập chính của Hub chưa được mở trực tiếp để kiểm chứng, nên không đưa vào bài.</li><li><strong>Số File chính xác trong từng cuốn bản 3 và bản 4:</strong> số File khác nhau theo trình độ và bản; chúng tôi chưa kiểm chứng được con số chính xác cho từng cuốn nên không ghi con số cụ thể trong bài.</li><li><strong>Mức CEFR chính xác của từng trình độ:</strong> các nguồn ghi hơi khác nhau ở ranh giới (ví dụ Level 1 là A1 hay A1–A2; Level 2 là A2 hay A2–B1). Bảng trong bài là mức ước chừng để định hướng, không phải công bố chính thức của Oxford cho từng cuốn.</li><li><strong>Tình trạng phát hành đầy đủ của bản 4:</strong> một số nhà sách ghi chú rằng trải nghiệm số đầy đủ cho Level 4 và 5 sẽ có vào đầu năm 2027; thông tin này mới chỉ thấy trên trang của nhà sách, chưa được đối chiếu với thông báo chính thức của Oxford, nên không khẳng định trong bài.</li><li><strong>Giá bán tại Việt Nam và tình trạng còn hàng:</strong> giá và hàng tồn thay đổi liên tục theo nhà sách và thời điểm; bài này không ghi giá cụ thể. Hãy kiểm tra trực tiếp trên trang nhà sách trước khi mua.</li><li><strong>Tính năng cụ thể của ứng dụng Say It ở thời điểm hiện tại:</strong> ứng dụng được nhắc trong tài liệu của Oxford, nhưng chúng tôi chưa kiểm tra ứng dụng trực tiếp nên không mô tả chi tiết tính năng của nó.</li></ul>
<p><a href="/sach/">← Tất cả sách học</a> · <a href="/">← Về trang chủ</a> · <a href="/tro-chuyen-ai.html?q=H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20t%C3%B4i%20h%E1%BB%8Dc%20v%E1%BB%9Bi%20s%C3%A1ch%20American%20English%20File">Hỏi AI về sách này →</a></p>
"""), active="/sach/", eyebrow="Sách học",
    desc="Hướng dẫn tự học American English File (Oxford) từ A1 đến C1: chọn đúng trình độ, học từng File, luyện nghe–nói và mua sách chính hãng.")
add("/sach/barrons-toeic.html", "Hướng dẫn học với sách Barron's TOEIC", "Học TOEIC với sách Barron's",
    guide_sections("""
<p><a href="/sach/">← Tất cả sách học</a></p>
<p class="lead">Hướng dẫn học TOEIC với bộ sách Barron&#x27;s của Lin Lougheed: chọn đúng cuốn, học theo tuần và luyện đề hiệu quả.</p>
<h2>Sách này là gì</h2>
<p>Barron&#x27;s TOEIC là bộ sách luyện thi TOEIC (Test of English for International Communication) của tác giả Lin Lougheed, do Barrons Educational Services xuất bản và Simon &amp; Schuster phân phối. Đây là sách thương mại có bản quyền — hướng dẫn này chỉ tóm tắt thông tin chung về sách và đưa ra cách học của riêng người viết, không sao chép nội dung, bài tập hay đề thi trong sách.</p>
<p>TOEIC là bài thi tiếng Anh dành cho người mà tiếng Anh không phải tiếng mẹ đẻ, đo khả năng dùng tiếng Anh trong môi trường làm việc quốc tế. Bài thi TOEIC Listening &amp; Reading mà bộ sách này luyện cho gồm 200 câu trắc nghiệm, chia làm hai phần tính giờ riêng: Nghe (Listening) 100 câu trong khoảng 45 phút và Đọc (Reading) 100 câu trong 75 phút, tổng cộng khoảng 2 giờ. Mỗi phần được chấm theo thang 5–495 điểm, tổng điểm hai phần là 10–990 điểm. Bài thi không có điểm đậu hay trượt, và không trừ điểm khi trả lời sai.</p>
<p>Ba cuốn chính trong bộ sách, theo trang của nhà xuất bản:</p>
<ul><li><strong>Barron&#x27;s TOEIC / TOEIC Premium</strong> — cuốn ôn tổng hợp: luyện kỹ năng nghe và đọc, ôn lại dạng bài và từ vựng thường gặp, kèm các đề thi thử (model test) có giải thích đáp án và audio nghe trực tuyến. Bản mới nhất đã kiểm chứng là <em>TOEIC Premium: 6 Practice Tests + Online Audio, Tenth Edition</em> (xuất bản ngày 7 tháng 11 năm 2023, 564 trang, ISBN 9781506288123), gồm 6 đề thi thử đầy đủ.</li><li><strong>TOEIC Practice Exams</strong> — cuốn chuyên luyện đề: 6 đề thi thử đầy đủ, bám sát độ dài, dạng câu hỏi và độ khó của bài thi thật, có giải thích đáp án cho mọi câu hỏi và audio trực tuyến cho phần Nghe. Bản mới nhất đã kiểm chứng là ấn bản thứ sáu (xuất bản ngày 7 tháng 11 năm 2023, 372 trang, ISBN 9781506288222).</li><li><strong>600 Essential Words for the TOEIC (Essential Words for the TOEIC)</strong> — cuốn từ vựng: 600 từ thường gặp trong bài thi TOEIC, dạy qua 50 bài học từ vựng, mỗi bài 12 từ, tập trung vào tiếng Anh Mỹ dùng trong kinh doanh, công nghiệp, giao tiếp và hoạt động văn hóa. Mỗi từ có định nghĩa và được đặt trong nhiều ngữ cảnh khác nhau.</li></ul>
<p>Ngoài ra còn có <strong>TOEIC Superpack</strong> — bộ gộp ba cuốn trên trong một bộ (xuất bản ngày 30 tháng 7 năm 2019, ISBN 9781506258829): cuốn TOEIC tổng hợp (4 đề thi thử kèm ôn tập), cuốn 600 từ vựng (kèm 1 đề thi thử) và cuốn Practice Exams (6 đề thi thử). Mua bộ gộp rẻ hơn mua lẻ, theo mô tả của nhà xuất bản.</p>
<p>Về cấu trúc bài thi thật, theo tài liệu chính thức của ETS (đơn vị ra đề TOEIC): phần Nghe gồm Part 1 — Photographs (6 câu), Part 2 — Question–Response (25 câu), Part 3 — Conversations (13 đoạn hội thoại, mỗi đoạn 3 câu, tổng 39 câu), Part 4 — Talks (10 bài nói ngắn, mỗi bài 3 câu, tổng 30 câu); phần Đọc gồm Part 5 — Incomplete Sentences (30 câu), Part 6 — Text Completion (16 câu), Part 7 — Reading Comprehension, gồm đoạn đơn (10 bài đọc, 29 câu) và đoạn đôi/ba (5 nhóm bài đọc, 25 câu).</p>
<h2>Sách này dành cho ai</h2>
<ul><li>Người đang chuẩn bị thi TOEIC Listening &amp; Reading và muốn có một bộ sách ôn tập có hệ thống, từ ôn kỹ năng tới luyện đề thi thử đúng giờ.</li><li>Người đã có nền tảng tiếng Anh khoảng trung cấp trở lên (đọc hiểu được đoạn văn ngắn, nghe hiểu được hội thoại chậm) và muốn nâng điểm bằng cách luyện đúng dạng bài thi.</li><li>Người đi làm hoặc sinh viên cần điểm TOEIC cho công việc, xin việc hoặc tốt nghiệp, và có thể tự học đều đặn mỗi ngày.</li><li>Người yếu từ vựng công việc (hợp đồng, marketing, nhân sự, ngân hàng, văn phòng…) sẽ hợp với cuốn <em>600 Essential Words</em> trước khi làm đề.</li></ul>
<p>Sách này ít phù hợp nếu bạn mới bắt đầu học tiếng Anh từ đầu (chưa nắm ngữ pháp cơ bản), hoặc nếu bạn thi TOEIC Speaking &amp; Writing — bộ sách này luyện hai kỹ năng Nghe và Đọc, không phải Nói và Viết.</p>
<h2>Cấu trúc sách</h2>
<p>Cấu trúc dưới đây chỉ mô tả ở mức chung, dựa trên mục lục và mô tả của nhà xuất bản đã kiểm chứng — không trích nội dung trong sách.</p>
<p><strong>Cuốn TOEIC tổng hợp (TOEIC Premium):</strong></p>
<ul><li>Phần tổng quan về bài thi TOEIC (thi gồm những gì, tính điểm ra sao).</li><li>Phần ôn tập (review): luyện kỹ năng nghe và đọc theo từng dạng bài, ôn từ vựng và chủ đề thường gặp trong bài thi.</li><li>Các đề thi thử đầy đủ (6 đề trong bản Premium mới nhất), mỗi đề mô phỏng đúng dạng bài và số câu của bài thi thật, kèm đáp án và giải thích.</li><li>Audio trực tuyến cho toàn bộ phần Nghe của các đề thi thử và bài luyện nghe.</li><li>Gợi ý hoạt động tự học trên mạng.</li></ul>
<p><strong>Cuốn TOEIC Practice Exams:</strong></p>
<ul><li>Phần giới thiệu ngắn: bài thi TOEIC Listening &amp; Reading là gì, cách dùng sách, hợp đồng tự học và hoạt động tự học.</li><li>6 đề thi thử đầy đủ, mỗi đề gồm đáp án và phần giải thích đáp án.</li><li>Audio trực tuyến cho phần Nghe của cả 6 đề.</li></ul>
<p><strong>Cuốn 600 Essential Words for the TOEIC:</strong></p>
<ul><li>50 bài học từ vựng theo chủ đề công việc và đời sống (hợp đồng, marketing, nhân sự, văn phòng, sức khỏe, du lịch…), mỗi bài 12 từ.</li><li>Các bài ôn từ (word review) sau mỗi nhóm bài học.</li><li>Phần hướng dẫn cách mở rộng vốn từ: phân tích thành tố của từ, nhận diện họ từ, làm từ điển cá nhân.</li></ul>
<h2>Cách học một bài (unit)</h2>
<p>Quy trình dưới đây là cách học do người viết đề xuất, áp dụng chung cho một bài ôn tập hoặc một bài từ vựng trong sách. Thời gian gợi ý cho một buổi học là 45–60 phút.</p>
<p><strong>1. Đọc mục tiêu trước khi làm (5 phút).</strong> Xem bài này luyện dạng bài nào (ví dụ: nghe hội thoại, điền câu, đọc đoạn văn) và ghi ra một câu: &quot;Học xong bài này, mình phải làm được gì?&quot; Nếu là bài từ vựng, đọc lướt 12 từ và đoán nghĩa trước khi xem định nghĩa.</p>
<p><strong>2. Học phần kiến thức, đừng nhảy ngay vào bài tập (10–15 phút).</strong> Đọc phần giải thích và ví dụ trong sách. Với từ vựng, học mỗi từ theo cụm: nghĩa, loại từ, một câu ví dụ do chính bạn đặt (không chép câu trong sách). Ghi tối đa 12 từ mới vào sổ — nhiều hơn sẽ không nhớ.</p>
<p><strong>3. Làm bài tập như thi thật (15–20 phút).</strong> Làm một lượt, bấm giờ, không tra từ điển giữa chừng. Với bài nghe, chỉ nghe một lần như khi thi thật, rồi mới nghe lại để kiểm tra. Ghi đáp án ra giấy riêng thay vì viết vào sách để sau này làm lại được.</p>
<p><strong>4. Chữa bài kỹ — đây là bước quan trọng nhất (15 phút).</strong> Đọc phần giải thích đáp án trong sách cho mọi câu sai và cả câu đúng mà bạn đoán mò. Với câu nghe sai, nghe lại đoạn đó kèm nhìn transcript (nếu sách có) rồi nghe lại lần nữa không nhìn chữ. Ghi lỗi vào một trang &quot;sổ lỗi&quot; duy nhất: dạng lỗi (nghe sót số, nhầm thì, không biết từ…), không ghi lại cả câu hỏi trong sách.</p>
<p><strong>5. Ôn lại sau 24 giờ (5 phút, vào hôm sau).</strong> Trước khi học bài mới, đọc lại sổ lỗi và 12 từ của bài hôm qua, tự kiểm tra bằng cách che nghĩa và nói lại nghĩa. Từ nào quên thì đánh dấu và ôn lại sau 3 ngày nữa.</p>
<h2>Kế hoạch học theo tuần</h2>
<p>Kế hoạch 8 tuần dưới đây giả định bạn học 5 buổi/tuần, mỗi buổi 60–90 phút, và đã có nền tảng trung cấp. Nếu bạn còn nhiều thời gian hơn, hãy kéo dài giai đoạn 1; nếu sắp thi, hãy rút giai đoạn 1 còn 1 tuần và dành nhiều thời gian cho giai đoạn 3.</p>
<p><strong>Tuần 1 — Làm quen và đo trình độ.</strong> Đọc phần tổng quan về bài thi trong cuốn tổng hợp. Làm 1 đề thi thử trong cuốn Practice Exams hoặc Premium trong điều kiện đúng giờ (2 giờ, không dừng) để biết điểm xuất phát và phần nào yếu nhất. Ghi lại điểm từng phần (Nghe/Đọc) và 3 dạng bài mất điểm nhiều nhất. Học 5 bài từ vựng đầu tiên trong cuốn 600 từ.</p>
<p><strong>Tuần 2–3 — Ôn kỹ năng Nghe.</strong> Mỗi tuần học 3 buổi Nghe và 2 buổi từ vựng. Buổi Nghe: ôn một dạng bài (Part 1, rồi Part 2, Part 3, Part 4), làm bài tập trong cuốn tổng hợp, nghe lại và chữa kỹ. Buổi từ vựng: mỗi buổi 1 bài (12 từ) trong cuốn 600 từ, ôn lại bài cũ trước khi học bài mới. Cuối tuần 3, làm 1 đề Nghe riêng (100 câu, bấm giờ 45 phút) nếu sách cho phép tách phần, hoặc làm 1 đề đầy đủ.</p>
<p><strong>Tuần 4–5 — Ôn kỹ năng Đọc.</strong> Mỗi tuần 3 buổi Đọc và 2 buổi từ vựng. Buổi Đọc: ôn Part 5 (ngữ pháp và từ vựng trong câu), Part 6 (điền đoạn văn), Part 7 (đọc hiểu). Luyện thói quen đọc câu hỏi trước, gạch ý chính của đoạn văn, và đặt giới hạn thời gian cho mỗi nhóm câu. Tiếp tục mỗi buổi 1 bài từ vựng; tới cuối tuần 5 bạn đã học khoảng 25 bài (300 từ).</p>
<p><strong>Tuần 6 — Luyện đề lần 1 và sửa lỗi hệ thống.</strong> Làm 2 đề thi thử đầy đủ, mỗi đề vào một ngày khác nhau, đúng giờ thi thật. Sau mỗi đề, dành một buổi chỉ để chữa: phân loại mọi câu sai theo dạng bài và nguyên nhân (thiếu từ, nghe sót, hết giờ, đọc sai ý). Cập nhật sổ lỗi và quay lại ôn đúng dạng bài yếu nhất trong cuốn tổng hợp.</p>
<p><strong>Tuần 7 — Luyện đề lần 2 và tăng tốc.</strong> Làm 2 đề thi thử nữa. Lần này đặt mục tiêu cụ thể cho từng phần: ví dụ, phần Đọc phải xong Part 5 và Part 6 trong khoảng thời gian bạn tự đặt ra để còn đủ giờ cho Part 7; phần Nghe không dừng lại suy nghĩ ở câu đã qua. Học nốt các bài từ vựng còn lại theo nhịp 1 bài/ngày, ưu tiên chủ đề của dạng bài bạn hay sai.</p>
<p><strong>Tuần 8 — Tổng ôn và thi thử cuối.</strong> Đầu tuần: ôn sổ lỗi và toàn bộ từ đã đánh dấu &quot;hay quên&quot;. Giữa tuần: làm 1 đề thi thử cuối cùng trong điều kiện thi thật, rồi chữa nhẹ — không học kiến thức mới vào 2 ngày cuối. Ngày trước thi: chỉ ôn từ vựng và xem lại sổ lỗi, ngủ đủ giấc. Không làm đề mới vào ngày trước thi.</p>
<h2>Mẹo học hiệu quả</h2>
<ul><li><strong>Nghe mỗi ngày, dù chỉ 15 phút.</strong> Ngoài giờ học trong sách, nghe tin tức hoặc hội thoại tiếng Anh về chủ đề công việc. Mục tiêu là tai quen với tốc độ nói và nhiều giọng khác nhau (sách dùng cả giọng Bắc Mỹ, Anh và Úc cho phần nghe).</li><li><strong>Học từ theo chủ đề, không học từ rời rạc.</strong> 600 từ trong sách được xếp theo chủ đề công việc; khi ôn, hãy nhớ cả nhóm từ cùng chủ đề (ví dụ: hợp đồng đi với ký kết, điều khoản, gia hạn) thay vì học từng từ riêng lẻ.</li><li><strong>Đặt giới hạn thời gian cho Part 7.</strong> Đây là phần dài nhất của bài Đọc (54 câu). Nhiều người mất điểm không phải vì không hiểu bài mà vì hết giờ. Khi luyện, hãy tập đọc lướt để tìm ý chính trước, rồi mới đọc kỹ chỗ cần trả lời.</li><li><strong>Không bỏ trống câu nào.</strong> Bài thi không trừ điểm câu sai, nên khi thi thật hãy trả lời mọi câu, kể cả câu không chắc — chọn đáp án có khả năng đúng nhất rồi đi tiếp, đừng dừng lại quá lâu ở một câu.</li><li><strong>Nghe một lần khi luyện đề.</strong> Bài nghe thi thật chỉ phát một lần. Nếu khi luyện bạn nghe đi nghe lại nhiều lần mới trả lời, điểm luyện sẽ cao hơn điểm thi thật. Hãy nghe một lần để làm bài, rồi mới nghe lại để chữa.</li><li><strong>Ghi chú bằng tiếng Việt của chính bạn.</strong> Khi chữa bài, viết lại quy tắc hoặc nghĩa từ bằng lời của bạn, ngắn gọn trong 1 dòng. Ghi chú bạn tự viết sẽ nhớ lâu hơn chép nguyên giải thích trong sách.</li><li><strong>Ôn từ theo khoảng cách.</strong> Từ học hôm nay ôn lại ngày mai, rồi sau 3 ngày, rồi sau 1 tuần. Từ nào nhớ được sau 1 tuần mới tính là thuộc.</li></ul>
<h2>Lỗi thường gặp</h2>
<ul><li><strong>Chỉ làm đề, không chữa đề.</strong> Làm nhiều đề mà không phân tích câu sai thì điểm không tăng. Mỗi đề làm xong cần ít nhất một buổi chữa kỹ bằng thời gian làm đề.</li><li><strong>Học từ vựng bằng cách chép nghĩa rồi bỏ đó.</strong> Từ chỉ nhớ khi được dùng: đặt câu của riêng bạn, ôn lại sau 1 ngày và sau 1 tuần. Học 12 từ/ngày mà không ôn lại thì cuối tuần gần như quên hết.</li><li><strong>Nghe lại nhiều lần khi luyện đề.</strong> Thói quen này làm bạn tưởng mình nghe tốt, nhưng khi thi thật chỉ nghe một lần sẽ bị hụt. Luyện đúng điều kiện thi thì kết quả luyện mới dự báo được kết quả thi.</li><li><strong>Dồn hết thời gian vào phần mình đã giỏi.</strong> Nhiều người thích làm Part 5 vì dễ thấy tiến bộ, trong khi điểm mất nhiều nhất ở Part 3, Part 4 (nghe) và Part 7 (đọc). Hãy chia thời gian theo điểm yếu, không theo sở thích.</li><li><strong>Mua sách lậu hoặc tải bản PDF/audio không rõ nguồn.</strong> Sách Barron&#x27;s là sách có bản quyền; bản lậu thường thiếu trang, audio lỗi hoặc không có quyền truy cập audio trực tuyến. Nhà xuất bản cũng cảnh báo: sản phẩm mua từ người bán bên thứ ba không được bảo đảm về chất lượng, tính xác thực hay quyền truy cập nội dung trực tuyến đi kèm. Hãy mua sách chính hãng để có đủ audio và đáp án.</li><li><strong>Đặt mục tiêu điểm không thực tế trong thời gian ngắn.</strong> Điểm TOEIC phản ánh trình độ chung, không chỉ kỹ năng làm bài. Tăng điểm cần thời gian tích lũy; nếu mục tiêu cách điểm hiện tại quá xa, hãy chia thành từng mốc nhỏ (ví dụ: tăng 50–100 điểm mỗi đợt ôn) thay vì ép mình trong 2 tuần.</li></ul>
<h2>Mua sách và nghe audio ở đâu</h2>
<p>Chỉ liệt kê các liên kết đã tự tay mở và kiểm chứng trong quá trình viết hướng dẫn này. Giá bán có thể thay đổi theo nhà bán lẻ nên không ghi giá cố định ở đây — hãy xem giá trên trang bán trước khi mua.</p>
<ul><li>Trang chính thức của nhà phân phối Simon &amp; Schuster cho cuốn <em>TOEIC Premium: 6 Practice Tests + Online Audio, Tenth Edition</em> — đã kiểm chứng bằng cách mở trang: <a href="https://www.simonandschuster.ca/books/TOEIC-Premium-6-Practice-Tests-+-Online-Audio-Tenth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288123" target="_blank" rel="noopener">https://www.simonandschuster.ca/books/TOEIC-Premium-6-Practice-Tests-+-Online-Audio-Tenth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288123</a></li><li>Trang chính thức của nhà phân phối Simon &amp; Schuster cho cuốn <em>TOEIC Practice Exams: 6 Practice Tests + Online Audio, Sixth Edition</em> — đã kiểm chứng bằng cách mở trang: <a href="https://www.simonandschuster.net/books/TOEIC-Practice-Exams-6-Practice-Tests-+-Online-Audio-Sixth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288222" target="_blank" rel="noopener">https://www.simonandschuster.net/books/TOEIC-Practice-Exams-6-Practice-Tests-+-Online-Audio-Sixth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288222</a></li><li>Trang chính thức của nhà phân phối Simon &amp; Schuster cho bộ <em>TOEIC Superpack</em> (gộp 3 cuốn) — đã kiểm chứng bằng cách mở trang: <a href="https://www.simonandschuster.co.in/books/TOEIC-Superpack/Lin-Lougheed/Barrons-Test-Prep/9781506258829" target="_blank" rel="noopener">https://www.simonandschuster.co.in/books/TOEIC-Superpack/Lin-Lougheed/Barrons-Test-Prep/9781506258829</a></li><li>Trang tài liệu chính thức của ETS về bài thi TOEIC Listening &amp; Reading (định dạng bài thi và cách tính điểm) — đã kiểm chứng bằng cách mở tài liệu: <a href="https://www.ca.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf" target="_blank" rel="noopener">https://www.ca.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf</a></li></ul>
<p>Về audio: theo mô tả của nhà xuất bản, audio nghe cho phần Nghe được cung cấp trực tuyến kèm theo sách chính hãng (bản in mới ghi &quot;Online Audio&quot;). Cách truy cập cụ thể (đường link hay mã trong sách) nằm trong cuốn sách bạn mua — hướng dẫn này không cung cấp link audio, vì audio là nội dung có bản quyền đi kèm sách. Tại Việt Nam, bạn có thể tìm mua bản in chính hãng tại các nhà sách lớn hoặc nhà sách trực tuyến uy tín; hãy kiểm tra kỹ đó là sách chính hãng và còn quyền truy cập audio trước khi mua.</p>
<h2>Nguồn đã kiểm chứng</h2>
<ul><li>Trang Simon &amp; Schuster (Canada) cho <em>TOEIC Premium: 6 Practice Tests + Online Audio, Tenth Edition</em> — <a href="https://www.simonandschuster.ca/books/TOEIC-Premium-6-Practice-Tests-+-Online-Audio-Tenth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288123" target="_blank" rel="noopener">https://www.simonandschuster.ca/books/TOEIC-Premium-6-Practice-Tests-+-Online-Audio-Tenth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288123</a> — đã mở trang và xác nhận: tác giả Lin Lougheed, nhà xuất bản Barrons Educational Services, Simon &amp; Schuster phân phối, xuất bản 7/11/2023, 564 trang, ISBN 9781506288123, 6 đề thi thử đầy đủ kèm giải thích và audio trực tuyến.</li><li>Trang Simon &amp; Schuster cho <em>TOEIC Practice Exams: 6 Practice Tests + Online Audio, Sixth Edition</em> — <a href="https://www.simonandschuster.net/books/TOEIC-Practice-Exams-6-Practice-Tests-+-Online-Audio-Sixth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288222" target="_blank" rel="noopener">https://www.simonandschuster.net/books/TOEIC-Practice-Exams-6-Practice-Tests-+-Online-Audio-Sixth-Edition/Lin-Lougheed/Barrons-Test-Prep/9781506288222</a> — đã mở trang và xác nhận: tác giả Lin Lougheed, nhà xuất bản Barrons Educational Services, xuất bản 7/11/2023, 372 trang, ISBN 9781506288222, 6 đề thi thử đầy đủ kèm giải thích và audio trực tuyến.</li><li>Trang Simon &amp; Schuster (Ấn Độ) cho <em>TOEIC Superpack</em> — <a href="https://www.simonandschuster.co.in/books/TOEIC-Superpack/Lin-Lougheed/Barrons-Test-Prep/9781506258829" target="_blank" rel="noopener">https://www.simonandschuster.co.in/books/TOEIC-Superpack/Lin-Lougheed/Barrons-Test-Prep/9781506258829</a> — đã mở trang và xác nhận: bộ 3 cuốn (TOEIC tổng hợp 4 đề thi thử, Essential Words 600 từ kèm 1 đề, Practice Exams 6 đề), xuất bản 30/7/2019, ISBN 9781506258829.</li><li>Tài liệu <em>Score User Guide — TOEIC Listening &amp; Reading Test</em> của ETS — <a href="https://www.ca.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf" target="_blank" rel="noopener">https://www.ca.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf</a> — đã mở tài liệu và xác nhận: bài thi 200 câu trắc nghiệm, Nghe 100 câu khoảng 45 phút (Part 1: 6 câu, Part 2: 25 câu, Part 3: 39 câu, Part 4: 30 câu), Đọc 100 câu 75 phút (Part 5: 30 câu, Part 6: 16 câu, Part 7: 29 + 25 câu), mỗi phần chấm 5–495 điểm (tổng 10–990), không trừ điểm câu sai, bài thi không có đậu/trượt.</li><li>Google Books, trang sách <em>600 Essential Words for the TOEIC</em> (ISBN 9781438077291, ấn bản 2017) — <a href="https://www.google.com.br/books/edition/_/k5tJvgAACAAJ" target="_blank" rel="noopener">https://www.google.com.br/books/edition/_/k5tJvgAACAAJ</a> — kết quả tìm kiếm từ nguồn của nhà xuất bản, xác nhận: tác giả Lin Lougheed, nhà xuất bản Barrons Educational Services, 600 từ dạy qua 50 bài học, mỗi bài 12 từ, tập trung vào tiếng Anh Mỹ trong kinh doanh, công nghiệp, giao tiếp và văn hóa.</li><li>Google Books, trang <em>TOEIC Superpack</em> — <a href="https://books.google.com/books?id=CFDpDwAAQBAJ" target="_blank" rel="noopener">https://books.google.com/books?id=CFDpDwAAQBAJ</a> — kết quả tìm kiếm, xác nhận: tác giả Lin Lougheed, bộ 3 cuốn, 1.456 trang, xuất bản 2019.</li></ul>
<h2>Chưa kiểm chứng được</h2>
<ul><li>Trang chính thức riêng của Barron&#x27;s tại barronseduc.com cho các cuốn TOEIC: tìm kiếm theo tên miền không trả kết quả và không mở được trang chính thức để xác nhận, nên hướng dẫn này không đưa link barronseduc.com. Các trang Simon &amp; Schuster ở trên là kênh chính thức của nhà phân phối và đã được mở kiểm chứng.</li><li>Cấu trúc chi tiết bên trong cuốn TOEIC tổng hợp (tên từng chương ôn tập, số bài luyện trong mỗi phần review): mục lục đầy đủ của cuốn này chưa được mở xem trực tiếp, nên hướng dẫn chỉ mô tả cấu trúc ở mức chung (tổng quan, ôn tập, đề thi thử) theo mô tả của nhà xuất bản.</li><li>Giá bán và nơi bán cụ thể tại Việt Nam, cũng như có hay không bản dịch/bản quyền tiếng Việt của bộ sách: chưa kiểm chứng được từ nguồn chính thức, nên không ghi giá hay tên nhà sách cụ thể trong hướng dẫn này.</li><li>Cách truy cập audio trực tuyến đi kèm từng ấn bản (đường link, mã kích hoạt hay ứng dụng): thông tin này nằm trong sách chính hãng, chưa kiểm chứng được từ nguồn công khai nên không ghi chi tiết.</li><li>Bất kỳ con số nào về tỉ lệ đậu, điểm trung bình của người dùng sách, hay lời chứng thực về hiệu quả của sách: không có nguồn đáng tin cậy nào xác nhận, nên hướng dẫn này không đưa ra các con số đó.</li></ul>
<p><a href="/sach/">← Tất cả sách học</a> · <a href="/">← Về trang chủ</a> · <a href="/tro-chuyen-ai.html?q=H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20t%C3%B4i%20h%E1%BB%8Dc%20v%E1%BB%9Bi%20s%C3%A1ch%20Barron%27s%20TOEIC">Hỏi AI về sách này →</a></p>
"""), active="/sach/", eyebrow="Sách học",
    desc="Hướng dẫn học TOEIC với bộ sách Barron's của Lin Lougheed: chọn đúng cuốn, học theo tuần và luyện đề hiệu quả.")
add("/sach/mindset-for-ielts.html", "Hướng dẫn học với sách Mindset for IELTS", "Học IELTS với sách Mindset for IELTS",
    guide_sections("""
<p><a href="/sach/">← Tất cả sách học</a></p>
<p class="lead">Hướng dẫn tự học bộ sách Mindset for IELTS theo từng cấp độ, từ Foundation đến Level 3, kèm kế hoạch tuần và mẹo thi.</p>
<h2>Sách này là gì</h2>
<p><em>Mindset for IELTS</em> là bộ giáo trình luyện thi IELTS của Cambridge University Press &amp; Assessment (tên cũ: Cambridge University Press), được giới thiệu là &quot;An Official Cambridge IELTS Course&quot; — tức là một khóa học chính thức của Cambridge về IELTS. Bản đầu tiên xuất bản năm 2017; bản cập nhật &quot;with Updated Digital Pack&quot; phát hành ngày 20 tháng 3 năm 2023.</p>
<p>Bộ sách hướng tới kỳ thi IELTS Academic. IELTS là bài thi đánh giá năng lực tiếng Anh, có hai dạng là Academic và General Training, gồm 4 kỹ năng: Listening (Nghe), Reading (Đọc), Writing (Viết) và Speaking (Nói). Tổng thời gian 4 phần thi là 2 giờ 45 phút, và điểm được báo theo thang band từ 0 đến 9 (theo hướng dẫn chính thức của IELTS, band 1 là thấp nhất có điểm, band 9 là cao nhất, band 0 nghĩa là không làm bài). Cụ thể theo hướng dẫn này: Listening 30 phút, 40 câu hỏi; Reading 60 phút, 40 câu hỏi; Writing 60 phút, gồm Task 1 tối thiểu 150 từ và Task 2 tối thiểu 250 từ; Speaking 11–14 phút, gồm 3 phần. Academic phù hợp với người muốn học đại học hoặc đăng ký hành nghề chuyên môn bằng tiếng Anh; General Training phù hợp với người muốn định cư, làm việc hoặc học dưới bậc đại học.</p>
<p>Lưu ý về bản quyền: đây là sách thương mại có bản quyền. Trang này chỉ là hướng dẫn tự học do chúng tôi tự viết, dựa trên thông tin ngắn gọn về bộ sách và kinh nghiệm học thi nói chung. Trang này không đăng, không chia sẻ và không sao chép nội dung, bài tập, đề thi hay file audio của sách. Muốn dùng sách, bạn cần mua bản chính hãng (xem mục &quot;Mua sách và nghe audio ở đâu&quot;).</p>
<h2>Sách này dành cho ai</h2>
<p>Bộ sách có 4 cấp độ. Bạn nên chọn đúng cấp độ với trình độ hiện tại của mình, thay vì nhảy thẳng lên cấp độ cao nhất:</p>
<table><thead><tr><th>Cấp độ</th><th>Trình độ (CEFR)</th><th>Band IELTS hướng tới</th></tr></thead><tbody><tr><td>Foundation</td><td>A2</td><td>Làm quen với IELTS; các nguồn thứ cấp ghi band mục tiêu khoảng 4.5 (xem mục &quot;Chưa kiểm chứng được&quot;)</td></tr><tr><td>Level 1</td><td>B1</td><td>5.5</td></tr><tr><td>Level 2</td><td>B1–B2</td><td>6.5</td></tr><tr><td>Level 3</td><td>B2–C1 (theo các nguồn thứ cấp)</td><td>7.5</td></tr></tbody></table>
<p>Cách chọn nhanh:</p>
<ul><li><strong>Bạn mới bắt đầu, vốn từ còn ít, chưa từng làm bài IELTS:</strong> bắt đầu ở Foundation. Sách này dạy theo trình tự tuyến tính, vừa nâng trình độ tiếng Anh chung vừa giới thiệu dần các yếu tố của bài thi.</li><li><strong>Bạn đã giao tiếp cơ bản được, đọc hiểu đoạn văn đơn giản, muốn đạt band 5.5:</strong> bắt đầu ở Level 1.</li><li><strong>Bạn đã ở khoảng band 5.5 và muốn lên 6.5:</strong> bắt đầu ở Level 2.</li><li><strong>Bạn đã ở khoảng band 6.5 và muốn lên 7.5:</strong> bắt đầu ở Level 3.</li></ul>
<p>Nếu bạn không chắc mình ở đâu, hãy làm một bài thi thử IELTS chính thức (hoặc bài kiểm tra trình độ của một trung tâm uy tín) trước khi mua sách, rồi chọn cấp độ thấp hơn band mục tiêu của bạn một nấc. Học sách quá khó so với trình độ chỉ làm bạn nản; học sách quá dễ thì bạn không tiến bộ.</p>
<p>Một số tác giả đã kiểm chứng được: Foundation gồm Greg Archer, Lucy Passmore và Jishan Uddin (một số bản ghi ISBN viết &quot;Lucy Pasmore&quot;); Level 1 gồm Peter Crosthwaite, Susan Hutchison, Claire Wijayatilake và Natasha De Souza. Tác giả của Level 2 và Level 3 chưa được kiểm chứng từ nguồn chính thức trong lần nghiên cứu này — xem mục &quot;Chưa kiểm chứng được&quot;.</p>
<h2>Cấu trúc sách</h2>
<p>Mỗi cấp độ có một cuốn Student&#x27;s Book (sách học sinh) kèm phần học trực tuyến (Digital Pack / online modules). Cấu trúc chung, theo tài liệu giới thiệu của chính Cambridge:</p>
<ul><li><strong>Foundation: 10 unit theo chủ đề</strong>, sắp xếp theo kỹ năng, tương đương 60–90 giờ học trên lớp cho một cấp độ. Sách có đáp án (answer key) và bản ghi âm bài nghe (listening scripts) ở cuối sách.</li><li><strong>Level 1, 2 và 3: mỗi cấp độ 8 unit theo chủ đề</strong>, cũng sắp xếp theo kỹ năng, tương đương 60–90 giờ học cho một cấp độ.</li><li><strong>Mỗi unit gồm 4 phần kỹ năng:</strong> Reading, Writing, Listening và Speaking, kèm phần từ vựng và ngữ pháp lồng trong quá trình luyện kỹ năng. Mỗi bài học đều ghi rõ mục tiêu cần đạt (&quot;In this unit you will learn how to…&quot;).</li><li><strong>Học trực tuyến đi kèm:</strong> các module luyện từng kỹ năng (Reading, Writing, Listening, Speaking, cộng thêm Grammar and Vocabulary), mỗi kỹ năng khoảng 8 giờ luyện tập cho một cấp độ; module Academic Study Skills (kỹ năng học thuật, khoảng 6 giờ) giúp chuẩn bị cho việc học đại học bằng tiếng Anh; và các bài thi thử trực tuyến (ở bản 2017 gọi là Testbank; ở bản 2023 gọi là Digital Pack, truy cập bằng mã code trong sách qua nền tảng Cambridge One).</li><li><strong>Teacher&#x27;s Book:</strong> có sách giáo viên riêng cho từng cấp độ, dành cho giáo viên đứng lớp — người tự học không cần mua cuốn này.</li></ul>
<p>Điểm khác biệt đáng chú ý của bộ sách là tính linh hoạt: bạn có thể học lần lượt từng unit theo chủ đề, hoặc học theo kỹ năng (ví dụ chỉ tập trung vào Writing trong một thời gian). Sách cũng nhấn mạnh các chiến lược làm bài (learning strategies), luyện kỹ năng (skills practice) và luyện thi (exam practice), chứ không chỉ cung cấp bài tập.</p>
<h2>Cách học một bài (unit)</h2>
<p>Dưới đây là quy trình tự học một unit mà chúng tôi đề xuất. Đây là lời khuyên của chúng tôi, không phải hướng dẫn trong sách. Một unit nên học trong khoảng 5–7 ngày, mỗi ngày 60–90 phút, thay vì học dồn một buổi.</p>
<p><strong>Ngày 1 — Đọc lướt và nắm chủ đề (khoảng 60 phút)</strong></p>
<ul><li>Đọc mục tiêu của unit (&quot;In this unit you will learn how to…&quot;) và ghi ra 3 điều bạn muốn đạt được sau unit này.</li><li>Đọc lướt toàn bộ unit: xem các tiêu đề, từ in đậm, hình ảnh. Ghi lại các từ mới theo chủ đề vào một sổ từ vựng riêng, kèm một câu ví dụ do chính bạn đặt.</li><li>Đừng tra từ điển cho mọi từ lạ. Chỉ tra những từ lặp lại nhiều lần hoặc chặn bạn hiểu ý chính.</li></ul>
<p><strong>Ngày 2 — Reading (khoảng 60–90 phút)</strong></p>
<ul><li>Đọc kỹ thuật: đọc câu hỏi trước, gạch chân từ khóa trong câu hỏi, rồi mới đọc bài.</li><li>Làm bài tập theo đúng hướng dẫn trong sách, bấm giờ như đi thi. Làm xong mới mở đáp án ở cuối sách để kiểm tra.</li><li>Với mỗi câu sai, viết ra lý do: bạn hiểu sai từ, đọc sót chi tiết, hay bị từ đồng nghĩa đánh lừa? Ghi lý do vào sổ lỗi (xem mục &quot;Mẹo học hiệu quả&quot;).</li></ul>
<p><strong>Ngày 3 — Listening (khoảng 60–90 phút)</strong></p>
<ul><li>Nghe lần 1 không dừng, không xem bản ghi âm (listening scripts), làm bài như đi thi thật — trong bài thi thật bạn chỉ được nghe một lần.</li><li>Nghe lần 2 có dừng, kiểm tra lại các chỗ chưa nghe được.</li><li>Chỉ sau đó mới mở bản ghi âm ở cuối sách để đối chiếu. Gạch chân những từ bạn nghe sai hoặc nghe không ra, và nghe lại riêng những đoạn đó.</li><li>Đọc to theo bản ghi âm 2–3 lần để luyện phát âm và ngữ điệu.</li></ul>
<p><strong>Ngày 4 — Writing (khoảng 90 phút)</strong></p>
<ul><li>Đọc kỹ yêu cầu đề bài, gạch chân các từ khóa: dạng bài là gì, cần viết bao nhiêu từ, thời gian bao nhiêu.</li><li>Lập dàn ý trong 5–10 phút trước khi viết. Với Task 2, dàn ý gồm: quan điểm của bạn là gì, 2 luận điểm chính, mỗi luận điểm có một ví dụ hoặc giải thích.</li><li>Viết đủ số từ tối thiểu (Task 1 ít nhất 150 từ, Task 2 ít nhất 250 từ) và bấm giờ: Task 1 khoảng 20 phút, Task 2 khoảng 40 phút.</li><li>Để bài qua một đêm rồi đọc lại vào hôm sau với con mắt mới. Tự kiểm tra: bài có trả lời đúng câu hỏi không, đoạn văn có câu chủ đề rõ ràng không, có lỗi ngữ pháp lặp lại không?</li></ul>
<p><strong>Ngày 5 — Speaking (khoảng 60 phút)</strong></p>
<ul><li>Luyện nói một mình: trả lời to thành tiếng, ghi âm lại bằng điện thoại, rồi nghe lại.</li><li>Với dạng nói dài (Part 2), tập đúng khung thời gian: 1 phút chuẩn bị, nói tối đa 2 phút. Dùng đồng hồ bấm giờ.</li><li>Khi nghe lại bản ghi âm của mình, chú ý 3 điều: bạn có ngập ngừng quá nhiều không, bạn có dùng được từ vựng theo chủ đề của unit không, câu của bạn có đủ dài và đa dạng không?</li><li>Nếu có bạn học cùng hoặc giáo viên, hãy nhờ họ nghe và nhận xét. Nếu không, bạn có thể viết ra dàn ý câu trả lời rồi nói lại lần hai trôi chảy hơn.</li></ul>
<p><strong>Ngày 6 — Ngữ pháp, từ vựng và ôn lại (khoảng 60 phút)</strong></p>
<ul><li>Làm phần Grammar and Vocabulary của unit và các module trực tuyến đi kèm (nếu bạn có mã Digital Pack).</li><li>Ôn lại sổ từ vựng của unit: che nghĩa tiếng Việt, tự nhắc lại nghĩa và đặt câu mới.</li><li>Xem lại sổ lỗi: các lỗi Reading và Listening bạn đã ghi trong tuần.</li></ul>
<p><strong>Ngày 7 — Kiểm tra nhanh và nghỉ</strong></p>
<ul><li>Làm lại 5–10 câu bạn đã làm sai trong unit, không xem đáp án trước.</li><li>Tự chấm: nếu vẫn sai cùng một dạng lỗi, đó là điểm yếu cần tập trung ở unit sau.</li><li>Nghỉ ngơi. Học liên tục 7 ngày không nghỉ làm bạn kiệt sức và nhớ kém hơn.</li></ul>
<h2>Kế hoạch học theo tuần</h2>
<p>Kế hoạch dưới đây áp dụng cho một cấp độ (Foundation: 10 tuần; Level 1, 2, 3: 8 tuần), với giả định bạn học 5–6 ngày mỗi tuần, mỗi ngày 60–90 phút. Đây là kế hoạch gợi ý của chúng tôi; bạn hãy điều chỉnh theo thời gian thực tế của mình, nhưng giữ nguyên nguyên tắc: một unit mỗi tuần, không bỏ qua kỹ năng yếu.</p>
<p><strong>Tuần 0 — Chuẩn bị (trước khi bắt đầu)</strong></p>
<ul><li>Làm một bài thi thử để biết band hiện tại và kỹ năng yếu nhất của bạn.</li><li>Mua sách chính hãng đúng cấp độ, kích hoạt mã Digital Pack (xem mục &quot;Mua sách và nghe audio ở đâu&quot;).</li><li>Chuẩn bị: một sổ từ vựng, một sổ lỗi, điện thoại để ghi âm phần Speaking, đồng hồ bấm giờ.</li></ul>
<p><strong>Tuần 1–8 (hoặc 1–10 với Foundation) — Học từng unit</strong></p>
<ul><li>Mỗi tuần một unit, theo quy trình 7 ngày ở mục trên.</li><li>Cuối mỗi tuần, dành 30 phút viết tổng kết: 10 từ mới quan trọng nhất của tuần, 2 lỗi thường gặp nhất, và 1 điều bạn làm tốt hơn tuần trước.</li></ul>
<p><strong>Tuần giữa khóa (sau unit 4 hoặc 5) — Ôn tập giữa kỳ</strong></p>
<ul><li>Dành trọn một tuần không học unit mới. Ôn lại từ vựng của các unit đã học, làm lại các câu đã sai, và làm một bài thi thử ngắn (chỉ 2 kỹ năng, ví dụ Reading + Listening) để đo tiến bộ.</li><li>Nếu một kỹ năng vẫn yếu rõ rệt (ví dụ Writing luôn dưới band mục tiêu), hãy dành thêm 2 buổi trong tuần này chỉ cho kỹ năng đó.</li></ul>
<p><strong>Tuần cuối — Thi thử đầy đủ</strong></p>
<ul><li>Làm một bài thi thử đầy đủ 4 kỹ năng trong điều kiện gần giống thi thật: đúng thời gian, không tra từ điển, không dừng giữa chừng.</li><li>Chấm điểm và so sánh với band mục tiêu. Nếu đã đạt band mục tiêu ở bài thi thử, bạn có thể đăng ký thi thật hoặc chuyển lên cấp độ tiếp theo. Nếu chưa đạt, hãy xem kỹ năng nào kéo điểm xuống và học lại các unit liên quan, thay vì học tiếp lên cấp độ cao hơn.</li></ul>
<p><strong>Nếu bạn chỉ có 4 tuần:</strong> hãy chọn 4 unit có chủ đề bạn yếu nhất, học mỗi unit trong 5 ngày thay vì 7 ngày, và bỏ ngày nghỉ giữa các unit. Đừng cố học hết 8–10 unit trong 4 tuần — học vội mà không ôn thì nhớ rất ít.</p>
<p><strong>Nếu bạn có 6 tháng:</strong> học xong một cấp độ trong 8–10 tuần, nghỉ 1 tuần, rồi học tiếp cấp độ sau. Giữa hai cấp độ, hãy đọc thêm tiếng Anh ngoài sách (báo, truyện ngắn) để từ vựng có thời gian &quot;ngấm&quot;.</p>
<h2>Mẹo học hiệu quả</h2>
<ul><li><strong>Học từ vựng theo chủ đề, không học từ rời rạc.</strong> Mỗi unit xoay quanh một chủ đề. Hãy học từ theo nhóm chủ đề đó, kèm collocation (cụm từ đi cùng nhau) và một câu ví dụ của chính bạn. Mười từ học kỹ tốt hơn năm mươi từ học lướt.</li><li><strong>Luyện nghe bằng tai, không bằng mắt.</strong> Đừng vừa nghe vừa đọc bản ghi âm. Nghe trước, đoán trước, rồi mới đối chiếu. Trong bài thi thật bạn chỉ nghe một lần, nên thói quen nghe lại nhiều lần sẽ không giúp bạn vào ngày thi.</li><li><strong>Viết tay khi luyện Writing.</strong> Nếu bạn thi IELTS trên giấy, hãy luyện viết tay để quen tốc độ và kiểm soát số từ. Nếu bạn thi trên máy tính, hãy luyện gõ và kiểm tra số từ bằng công cụ đếm từ.</li><li><strong>Ghi âm phần Speaking của chính bạn.</strong> Hầu hết người học đều ngạc nhiên khi nghe lại giọng mình: những chỗ ngập ngừng, lặp từ &quot;uh&quot;, &quot;um&quot; hay câu quá ngắn đều lộ rõ. Ghi âm là cách rẻ nhất để tự sửa.</li><li><strong>Giữ một sổ lỗi.</strong> Mỗi lỗi chỉ ghi một dòng: ngày, kỹ năng, lỗi gì, và cách sửa. Cuối tuần đọc lại sổ lỗi mất 10 phút nhưng giúp bạn không lặp lại cùng một lỗi trong nhiều tuần.</li><li><strong>Đừng chỉ học sách.</strong> Sách là khung xương; bạn cần thêm &quot;thịt&quot;: nghe tin tức tiếng Anh 15 phút mỗi ngày, đọc một bài báo ngắn mỗi tuần, và nói tiếng Anh với ai đó ít nhất một lần mỗi tuần, dù chỉ 10 phút.</li><li><strong>Học đều cả 4 kỹ năng.</strong> Điểm IELTS tổng là trung bình cộng của 4 kỹ năng, nên một kỹ năng rất yếu sẽ kéo điểm tổng xuống dù 3 kỹ năng còn lại tốt. Đừng bỏ qua kỹ năng bạn ghét nhất — đó thường chính là kỹ năng cần luyện nhất.</li></ul>
<h2>Lỗi thường gặp</h2>
<ul><li><strong>Nhảy thẳng lên Level 3 khi mới ở band 5.0.</strong> Sách Level 3 được thiết kế cho người đã ở khoảng band 6.5. Học sách quá khó khiến bạn không hiểu bài, đoán mò đáp án, và tưởng mình tiến bộ trong khi thực ra chỉ đang đoán. Hãy chọn đúng cấp độ.</li><li><strong>Chỉ làm bài tập mà không xem lại đáp án và lý do sai.</strong> Làm xong rồi xem đáp án là chưa đủ. Bạn cần hiểu vì sao đáp án đúng và vì sao lựa chọn của bạn sai. Nếu không, bạn sẽ lặp lại cùng lỗi ở bài sau.</li><li><strong>Nghe đi nghe lại nhiều lần rồi mới làm bài.</strong> Thói quen này tạo cảm giác &quot;nghe hiểu&quot; giả tạo. Trong bài thi thật bạn chỉ nghe một lần, vì vậy hãy luyện đúng như thi thật ngay từ đầu.</li><li><strong>Viết Task 2 không lập dàn ý.</strong> Nhiều người viết ngay khi đọc đề, viết được nửa bài mới nhận ra luận điểm lộn xộn. Dành 5–10 phút lập dàn ý sẽ tiết kiệm thời gian sửa bài sau đó.</li><li><strong>Học từ vựng bằng cách ghi nghĩa tiếng Việt rồi học thuộc lòng.</strong> Cách này giúp bạn nhận ra từ khi đọc, nhưng không giúp bạn dùng từ khi viết và nói. Hãy học từ kèm câu ví dụ và tự đặt câu mới.</li><li><strong>Học dồn trước ngày thi.</strong> Nhồi nhét 8 unit trong 2 tuần cuối không hiệu quả bằng học đều 8 tuần. Trí nhớ cần thời gian và giấc ngủ để củng cố. Nếu chỉ còn ít ngày, hãy ôn lại những gì đã học thay vì học thêm unit mới.</li><li><strong>Dùng bản sao lậu của sách hoặc file audio trôi nổi trên mạng.</strong> Ngoài vấn đề bản quyền, các bản này thường thiếu trang, sai đáp án, thiếu mã Digital Pack, hoặc chứa file độc hại. Hãy mua sách chính hãng từ nhà sách uy tín (xem mục dưới đây).</li></ul>
<h2>Mua sách và nghe audio ở đâu</h2>
<p>Chỉ liệt kê các liên kết đã được kiểm chứng bằng cách mở trực tiếp trong lần nghiên cứu này. Giá bán có thể thay đổi theo thời gian và khu vực — chúng tôi không ghi giá cụ thể trong bài này vì giá sẽ lỗi thời nhanh.</p>
<ul><li><strong>Cửa hàng trực tuyến chính thức của Cambridge — trang tổng hợp cả bộ Mindset for IELTS with Updated Digital Pack:</strong> liệt kê Student&#x27;s Book và Teacher&#x27;s Book của cả 4 cấp độ (Foundation, Level 1, 2, 3). Link đã được mở và kiểm chứng: <a href="https://shop.cambridge.org/english/family/2100096324" target="_blank" rel="noopener">https://shop.cambridge.org/english/family/2100096324</a></li><li><strong>Cửa hàng trực tuyến chính thức của Cambridge — Student&#x27;s Book Level 2 with Digital Pack:</strong> trang sản phẩm ghi rõ sách hướng tới Band 6.5 (Academic), CEFR B1–B2, nhà xuất bản Cambridge University Press &amp; Assessment, phát hành 20/03/2023. Link đã được mở và kiểm chứng: <a href="https://shop.cambridge.org/english/product/2700233493" target="_blank" rel="noopener">https://shop.cambridge.org/english/product/2700233493</a></li><li><strong>Trang Cambridge Tây Ban Nha — thành phần của bộ Mindset for IELTS with Updated Digital Pack:</strong> ghi rõ mã trong sách cho quyền truy cập Digital Pack trên Cambridge One, bao gồm audio, hoạt động trực tuyến và bài kiểm tra. Link đã được mở và kiểm chứng: <a href="https://www.cambridge.es/en/catalogue/exams/courses/mindset-for-ielts-with-updated-digital-pack/components" target="_blank" rel="noopener">https://www.cambridge.es/en/catalogue/exams/courses/mindset-for-ielts-with-updated-digital-pack/components</a></li><li><strong>Hướng dẫn chính thức cho thí sinh IELTS (IELTS.org):</strong> tài liệu PDF chính thức giải thích dạng thi Academic/General Training, 4 kỹ năng, thời gian và thang điểm. Link đã được mở và kiểm chứng: <a href="https://ielts.org/cdn/ielts-downloadable-assets/ielts-guidance-and-support/ielts-guides/ielts-guide-for-test-takers.pdf" target="_blank" rel="noopener">https://ielts.org/cdn/ielts-downloadable-assets/ielts-guidance-and-support/ielts-guides/ielts-guide-for-test-takers.pdf</a></li></ul>
<p><strong>Nghe audio như thế nào:</strong> Ở bản Updated Digital Pack (2023), audio nằm trong Digital Pack và được truy cập bằng mã code in trong sách, qua nền tảng Cambridge One. Ở bản 2017, audio được tải bằng mã in ở bìa trong của sách. Bạn cần mua sách chính hãng còn nguyên mã chưa kích hoạt thì mới dùng được audio và bài tập trực tuyến. Đừng mua sách đã qua sử dụng nếu mã đã bị kích hoạt, vì bạn sẽ không nghe được audio chính thức.</p>
<p><strong>Mua sách ở Việt Nam:</strong> chúng tôi chưa kiểm chứng được liên kết mua hàng cụ thể của nhà sách nào tại Việt Nam trong lần nghiên cứu này, nên không liệt kê ở đây. Bạn hãy tìm mua tại các nhà sách lớn, uy tín, và kiểm tra kỹ: sách có logo Cambridge, có mã Digital Pack còn nguyên, và có hóa đơn. Nếu nhà sách bán bản in lại không có mã, đó có thể không phải bản chính hãng.</p>
<h2>Nguồn đã kiểm chứng</h2>
<ul><li><a href="https://shop.cambridge.org/english/family/2100096324" target="_blank" rel="noopener">https://shop.cambridge.org/english/family/2100096324</a> — Cửa hàng chính thức của Cambridge; đã mở trực tiếp. Xác nhận: bộ Mindset for IELTS with Updated Digital Pack có Student&#x27;s Book và Teacher&#x27;s Book cho cả 4 cấp độ Foundation, Level 1, 2, 3.</li><li><a href="https://shop.cambridge.org/english/product/2700233493" target="_blank" rel="noopener">https://shop.cambridge.org/english/product/2700233493</a> — Cửa hàng chính thức của Cambridge; đã mở trực tiếp. Xác nhận: Student&#x27;s Book Level 2 hướng tới Band 6.5 (Academic), CEFR B1–B2, nhà xuất bản Cambridge University Press &amp; Assessment, phát hành 20/03/2023.</li><li><a href="https://www.cambridge.es/en/catalogue/exams/courses/mindset-for-ielts-with-updated-digital-pack/components" target="_blank" rel="noopener">https://www.cambridge.es/en/catalogue/exams/courses/mindset-for-ielts-with-updated-digital-pack/components</a> — Trang Cambridge Tây Ban Nha; đã mở trực tiếp. Xác nhận: mã trong sách cho quyền truy cập Digital Pack trên Cambridge One, bao gồm audio, hoạt động trực tuyến và bài kiểm tra.</li><li><a href="https://ielts.org/cdn/ielts-downloadable-assets/ielts-guidance-and-support/ielts-guides/ielts-guide-for-test-takers.pdf" target="_blank" rel="noopener">https://ielts.org/cdn/ielts-downloadable-assets/ielts-guidance-and-support/ielts-guides/ielts-guide-for-test-takers.pdf</a> — Hướng dẫn chính thức cho thí sinh IELTS (ielts.org); đã mở trực tiếp. Xác nhận: hai dạng thi Academic và General Training; 4 kỹ năng Listening, Reading, Writing, Speaking; tổng thời gian 2 giờ 45 phút; Listening 30 phút / 40 câu, Reading 60 phút / 40 câu, Writing 60 phút (Task 1 tối thiểu 150 từ, Task 2 tối thiểu 250 từ), Speaking 11–14 phút / 3 phần; thang điểm 0–9.</li><li><a href="https://assets.cambridge.org/97813166/40050/frontmatter/9781316640050_frontmatter.pdf" target="_blank" rel="noopener">https://assets.cambridge.org/97813166/40050/frontmatter/9781316640050_frontmatter.pdf</a> — Tài liệu frontmatter chính thức của Cambridge (xuất hiện trong kết quả tìm kiếm trên tên miền cambridge.org). Xác nhận: Level 1 gồm các tác giả Peter Crosthwaite, Susan Hutchison, Claire Wijayatilake, Natasha De Souza; mỗi unit gồm Reading, Writing, Listening, Speaking; Level 1 hướng tới Band 5.5; mỗi cấp độ 60–90 giờ học; có Answer Key và Listening Scripts ở cuối sách.</li><li><a href="https://assets.cambridge.org/97810092/80280/frontmatter/9781009280280_frontmatter.pdf" target="_blank" rel="noopener">https://assets.cambridge.org/97810092/80280/frontmatter/9781009280280_frontmatter.pdf</a> — Tài liệu frontmatter chính thức của Cambridge (bản Refresh with Digital Pack, Foundation, 2023; xuất hiện trong kết quả tìm kiếm trên tên miền cambridge.org). Xác nhận: Foundation gồm các tác giả Greg Archer, Lucy Passmore, Jishan Uddin; Foundation dành cho người ở trình độ A2; Foundation có 10 unit theo chủ đề.</li><li><a href="https://assets.cambridge.org/97810092/80334/excerpt/9781009280334_excerpt.pdf" target="_blank" rel="noopener">https://assets.cambridge.org/97810092/80334/excerpt/9781009280334_excerpt.pdf</a> — Tài liệu excerpt chính thức của Cambridge (Teacher&#x27;s Book Level 1, bản Refresh; xuất hiện trong kết quả tìm kiếm trên tên miền cambridge.org). Xác nhận: Level 1 dành cho người ở trình độ B1 muốn đạt Band 5 hoặc 5.5; sách thiết kế cho tối đa 90 giờ học trên lớp.</li></ul>
<h2>Chưa kiểm chứng được</h2>
<ul><li><strong>Band mục tiêu của Foundation:</strong> Sơ đồ chính thức của Cambridge chỉ ghi band mục tiêu cho Level 1 (5.5), Level 2 (6.5) và Level 3 (7.5), không ghi con số cho Foundation. Con số &quot;khoảng 4.5&quot; trong bài này lấy từ các nguồn thứ cấp (ví dụ PrepEdu, YesLearn), chưa được kiểm chứng từ Cambridge. Vì vậy hãy coi Foundation là cấp độ &quot;làm quen với IELTS ở trình độ A2&quot; thay vì tin chắc vào một con số cụ thể.</li><li><strong>CEFR của Level 3:</strong> Một số nguồn thứ cấp ghi Level 3 là B2–C1. Chúng tôi chưa kiểm chứng được con số này từ trang chính thức của Cambridge trong lần nghiên cứu này.</li><li><strong>Tác giả của Level 2 và Level 3:</strong> Chưa kiểm chứng được đầy đủ từ nguồn chính thức của Cambridge. Một nguồn thứ cấp (Open Library) ghi Level 3 gồm Greg Archer và Claire Wijayatilake, nhưng đây chưa phải nguồn chính thức nên chúng tôi không đưa vào phần chính của bài.</li><li><strong>Số unit chính xác của Level 2 và Level 3:</strong> Foundation có 10 unit và Level 1 có 8 unit đã được kiểm chứng từ tài liệu của Cambridge. Số unit của Level 2 và Level 3 (các nguồn thứ cấp ghi là 8 unit mỗi cấp độ) chưa được kiểm chứng trực tiếp từ tài liệu chính thức trong lần nghiên cứu này.</li><li><strong>Liên kết mua sách tại Việt Nam:</strong> Chưa kiểm chứng được liên kết của nhà sách cụ thể nào tại Việt Nam (ví dụ Fahasa hay các nhà sách khác), nên bài này không liệt kê. Người đọc nên tự kiểm tra nhà sách uy tín và xác nhận sách có mã Digital Pack còn nguyên trước khi mua.</li><li><strong>Liên kết trực tiếp tới nền tảng Cambridge One:</strong> Chưa kiểm chứng được URL đăng nhập/kích hoạt cụ thể của Cambridge One trong lần nghiên cứu này, nên bài này không đưa liên kết đó. Thông tin duy nhất đã kiểm chứng là: mã trong sách cho quyền truy cập Digital Pack trên Cambridge One (theo trang Cambridge Tây Ban Nha và cửa hàng Cambridge).</li><li><strong>Giá bán:</strong> Giá bán thay đổi theo thời gian, khu vực và nhà sách, nên bài này không ghi giá cụ thể. Giá 79.50 USD cho Student&#x27;s Book và 47.75 USD cho Teacher&#x27;s Book xuất hiện trên cửa hàng Cambridge tại thời điểm kiểm tra, nhưng đó là giá của cửa hàng quốc tế, chưa chắc áp dụng tại Việt Nam.</li><li><strong>Không có nội dung nào trong bài này được sao chép từ sách:</strong> Chúng tôi không tải, không đọc toàn văn và không trích dẫn bài tập, đề thi hay đoạn văn nào từ bộ sách. Mọi lời khuyên học tập trong bài đều do chúng tôi tự viết.</li></ul>
<p><a href="/sach/">← Tất cả sách học</a> · <a href="/">← Về trang chủ</a> · <a href="/tro-chuyen-ai.html?q=H%C6%B0%E1%BB%9Bng%20d%E1%BA%ABn%20t%C3%B4i%20h%E1%BB%8Dc%20v%E1%BB%9Bi%20s%C3%A1ch%20Mindset%20for%20IELTS">Hỏi AI về sách này →</a></p>
"""), active="/sach/", eyebrow="Sách học",
    desc="Hướng dẫn tự học bộ sách Mindset for IELTS theo từng cấp độ, từ Foundation đến Level 3, kèm kế hoạch tuần và mẹo thi.")

if __name__ == "__main__":
    for path, title, h1, body, active, desc, eyebrow, hero in PAGES:
        full = page(path, title, h1, body, active, desc, eyebrow, hero)
        print("wrote", path, os.path.getsize(full), "B")
    print("total pages:", len(PAGES))
