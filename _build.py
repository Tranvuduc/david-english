# _build.py — sinh khung sườn HTML cho David English (v1, skeleton).
# Chạy: python3 _build.py  (ghi đè các file HTML trong thư mục này)
# KHÔNG đưa nội dung bài học nào vào đây — chỉ khung + mô tả "sắp có".
# Markup theo design system v2 (xem DESIGN-SYSTEM.md): hero, page-head,
# section/section-alt, card theo loại + icon SVG, badge-soon, level-chip.
# Chỉ đổi markup trình bày — không đổi chữ, link hay cấu trúc nội dung.
import datetime
import html as htmlmod
import json
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://davidenglish.vercel.app"

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
    "chat": _svg('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'),
    "dice": _svg('<rect x="4" y="4" width="16" height="16" rx="3"/>'
                 '<circle cx="9" cy="9" r="1" fill="currentColor" stroke="none"/>'
                 '<circle cx="15" cy="9" r="1" fill="currentColor" stroke="none"/>'
                 '<circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/>'
                 '<circle cx="9" cy="15" r="1" fill="currentColor" stroke="none"/>'
                 '<circle cx="15" cy="15" r="1" fill="currentColor" stroke="none"/>'),
    "listen": _svg('<path d="M4 14v-2a8 8 0 0 1 16 0v2"/>'
                   '<rect x="3" y="14" width="4" height="6" rx="1.5"/>'
                   '<rect x="17" y="14" width="4" height="6" rx="1.5"/>'),
    "mic": _svg('<rect x="9" y="3" width="6" height="11" rx="3"/>'
                '<path d="M5 11a7 7 0 0 0 14 0"/><path d="M12 18v3"/>'),
    "write": _svg('<path d="M4 20l1-4L16.5 4.5a2.1 2.1 0 0 1 3 3L8 19l-4 1z"/>'
                  '<path d="M14.5 6.5l3 3"/>'),
    "flag": _svg('<path d="M5 21V4"/><path d="M5 4h13l-2.5 4L18 12H5"/>'),
    "cap": _svg('<path d="M2.5 9.5L12 5l9.5 4.5L12 14 2.5 9.5z"/>'
                '<path d="M6.5 11.5V16c0 1.5 2.5 3 5.5 3s5.5-1.5 5.5-3v-4.5"/>'
                '<path d="M21.5 9.5V15"/>'),
    "trophy": _svg('<path d="M8 4h8v5a4 4 0 0 1-8 0V4z"/>'
                   '<path d="M8 5H4.5a3 3 0 0 0 3 4"/><path d="M16 5h3.5a3 3 0 0 1-3 4"/>'
                   '<path d="M12 13v4"/><path d="M8.5 20h7"/><path d="M10 17h4"/>'),
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
    ("Trò chơi & Công cụ", "/tro-choi/"),
    ("Trò chuyện AI", "/tro-chuyen-ai.html"),
    ("Học với David", "/hoc-voi-david.html"),
]

STYLE = "/assets/style.css?v=20261124-tutor"  # versioned: busts stale phone caches (tutor-page CSS fix 24/11)
CHAT_CSS = "/chat/de-chat.css"
CHAT_JS = "/chat/de-chat.js"
PROGRESS_JS = "/assets/progress.js"


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


def _fmt_vn_date(ts):
    """Định dạng timestamp (giây) thành dd/mm/yyyy theo giờ Việt Nam (+07).
    Dùng offset cố định thay vì zoneinfo để không phụ thuộc tzdata trên máy build."""
    tz7 = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.fromtimestamp(ts, tz=tz7).strftime("%d/%m/%Y")


def _date_vn(path):
    """Ngày cập nhật (dd/mm/yyyy) từ mtime của file nguồn, hoặc None nếu
    file không tồn tại — trang đó không hiện ngày (không bịa ngày)."""
    try:
        return _fmt_vn_date(os.path.getmtime(path))
    except OSError:
        return None


def _newest_date(paths):
    """Ngày mới nhất (dd/mm/yyyy) trong các file nguồn, hoặc None."""
    best = None
    for p in paths:
        try:
            ts = os.path.getmtime(p)
        except OSError:
            continue
        if best is None or ts > best:
            best = ts
    return _fmt_vn_date(best) if best is not None else None


def _pretty_url(path):
    """Dạng URL đẹp dùng cho canonical / og:url / sitemap: bỏ hậu tố
    '/index.html' (giữ '/' cho trang chủ, giữ nguyên .html còn lại)."""
    if path == "/":
        return "/"
    if path.endswith("/index.html"):
        return path[: -len("index.html")]
    return path


GA4_ID = "G-6WKB00FR9G"  # GA4 thật — property "David English", tạo 23/11 dưới reformedvn@gmail.com.

# Nhãn breadcrumb cho trang trung gian không có trong NAV (vd /trinh-do/a1.html).
CRUMB_LABELS = {
    "/trinh-do/a1.html": "Trình độ A1",
    "/trinh-do/a2.html": "Trình độ A2",
}


def _breadcrumb_jsonld(path, title, active):
    """BreadcrumbList JSON-LD: Trang chủ → hub (theo nav active) →
    trang trung gian (nếu có) → trang hiện tại. Trang chủ không cần."""
    if path == "/":
        data = {"@context": "https://schema.org", "@type": "WebSite",
                "name": "David English", "url": SITE_URL, "inLanguage": "vi"}
        return ('<script type="application/ld+json">\n'
                + json.dumps(data, ensure_ascii=False) + '\n</script>')
    pretty = _pretty_url(path)
    items = [("Trang chủ", "/")]
    for label, href in NAV:
        if href == active and href != "/":
            items.append((label, href))
            break
    parent_page = os.path.dirname(pretty) + ".html"
    if parent_page in CRUMB_LABELS and all(u != parent_page for _, u in items):
        items.append((CRUMB_LABELS[parent_page], parent_page))
    if all(u != pretty for _, u in items):
        items.append((title, pretty))
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name,
                 "item": SITE_URL + url}
                for i, (name, url) in enumerate(items)]}
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False) + '\n</script>')


# Consent Mode v2 (basic): mặc định analytics_storage: denied; gtag.js CHỈ
# tải/chạy sau khi khách bấm "Đồng ý". Xem PLAN.md §6.
CONSENT_HEAD = """<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {'analytics_storage': 'denied'});
</script>"""

COOKIE_STYLE = """<style>
.cookie-banner{position:fixed;left:0;right:0;bottom:0;z-index:100;background:#fff;color:#1a1a1a;border-top:3px solid #123a6d;box-shadow:0 -4px 24px rgba(0,0,0,.18);padding:16px 0}
.cookie-banner p{margin:0 0 12px}
.cookie-actions{display:flex;gap:12px;flex-wrap:wrap}
.cookie-actions .btn{flex:1 1 160px;margin-top:0}
</style>"""

COOKIE_BANNER = """<div id="cookie-banner" class="cookie-banner" role="dialog" aria-label="Thông báo về cookie" hidden>
  <div class="wrap">
    <p>Trang này dùng Google Analytics để biết nội dung nào hữu ích cho bạn — chỉ khi bạn đồng ý. Không có cookie quảng cáo, không bán dữ liệu. Bạn có thể đổi ý bất cứ lúc nào qua “Cài đặt cookie” ở chân trang. Xem <a href="/quyen-rieng-tu.html">Chính sách quyền riêng tư</a>.</p>
    <div class="cookie-actions">
      <button type="button" id="cookie-accept" class="btn">Đồng ý</button>
      <button type="button" id="cookie-decline" class="btn">Từ chối</button>
    </div>
  </div>
</div>"""

COOKIE_SCRIPT = """<script>
(function(){
  var KEY='de-consent';
  var banner=document.getElementById('cookie-banner');
  function loadGA(){
    if(document.querySelector('script[src*="googletagmanager.com/gtag/js"]')){return;}
    var s=document.createElement('script');
    s.async=true;
    s.src='https://www.googletagmanager.com/gtag/js?id=__GA4_ID__';
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', '__GA4_ID__');
  }
  function eraseGaCookies(){
    document.cookie.split(';').forEach(function(c){
      var name=c.split('=')[0].trim();
      if(name.indexOf('_ga')===0){
        document.cookie=name+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
      }
    });
  }
  function showBanner(){banner.hidden=false;}
  function hideBanner(){banner.hidden=true;}
  function accept(){
    try{localStorage.setItem(KEY,'granted');}catch(e){}
    gtag('consent','update',{'analytics_storage':'granted'});
    loadGA();
    hideBanner();
  }
  function decline(){
    try{localStorage.setItem(KEY,'denied');}catch(e){}
    gtag('consent','update',{'analytics_storage':'denied'});
    eraseGaCookies();
    hideBanner();
  }
  document.getElementById('cookie-accept').addEventListener('click',accept);
  document.getElementById('cookie-decline').addEventListener('click',decline);
  var settings=document.getElementById('cookie-settings');
  if(settings){settings.addEventListener('click',function(e){e.preventDefault();showBanner();});}
  var stored=null;
  try{stored=localStorage.getItem(KEY);}catch(e){}
  if(stored==='granted'){
    gtag('consent','update',{'analytics_storage':'granted'});
    loadGA();
  }else if(stored==='denied'){
    /* Da tu choi: khong tai gtag.js, khong hien lai banner. */
  }else{
    showBanner();
  }
})();
</script>"""


def page(path, title, h1, body_html, active="/", desc=None, eyebrow=None, hero=None, noindex=False, updated=None):
    d = desc or derive_desc(body_html)
    desc_esc = htmlmod.escape(d, quote=True)
    title_esc = htmlmod.escape(title, quote=True)
    pretty = _pretty_url(path)
    robots_meta = ('<meta name="robots" content="noindex, follow">\n'
                   if noindex else "")
    updated_html = (f'    <p class="muted">Cập nhật lần cuối: {updated}</p>\n'
                    if updated else "")
    breadcrumb = _breadcrumb_jsonld(path, title, active)
    cookie_script = COOKIE_SCRIPT.replace("__GA4_ID__", GA4_ID)
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
{CONSENT_HEAD}
{breadcrumb}
{COOKIE_STYLE}
<title>{title_esc} | David English</title>
<meta name="description" content="{desc_esc}">
{robots_meta}<meta property="og:title" content="{title_esc} | David English">
<meta property="og:description" content="{desc_esc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}{pretty}">
<meta property="og:image" content="{SITE_URL}/assets/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_esc} | David English">
<meta name="twitter:image" content="{SITE_URL}/assets/og-default.png">
<link rel="canonical" href="{SITE_URL}{pretty}">
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
      <nav class="site-nav" aria-label="Điều hướng di động">
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
    <p><a href="/">Trang chủ</a> · <a href="/tro-chuyen-ai.html">Trò chuyện AI</a> · <a href="/bai-xep-lop.html">Bài xếp lớp</a> · <a href="/tai-nguyen.html">Tài nguyên miễn phí</a> · <a href="/cong-cu/tu-vung.html">Tra từ</a> · <a href="/cong-cu/viet.html">Chữa bài viết</a> · <a href="/quyen-rieng-tu.html">Quyền riêng tư</a> · <a href="#" id="cookie-settings">Cài đặt cookie</a></p>
    <p class="muted">Bài học, trò chơi và sách học miễn phí — nội dung mới thêm dần.</p>
{updated_html}  </div>
</footer>
<script src="{CHAT_JS}" defer></script>
<script src="{PROGRESS_JS}" defer></script>
{COOKIE_BANNER}
{cookie_script}
</body>
</html>
"""
    rel = "index.html" if path == "/" else path.lstrip("/")
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    return full


def soon(title, lines, extra="", parent=None, prev=None, next=None, ai_question=None, chip=None,
         lead=None, do_now=None):
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
    lead_html = f'<p class="lead">{lead}</p>\n' if lead else ""
    do_now_html = ""
    if do_now:
        pairs = do_now if isinstance(do_now, list) else [do_now]
        do_now_html = ('<p><strong>Làm ngay trong lúc chờ:</strong> '
                       + " · ".join(f'<a href="{h}">{t}</a>' for t, h in pairs)
                       + "</p>\n")
    return f"""
<section class="section">
<p><span class="badge badge-soon">Sắp có</span></p>
{chip_html}{lead_html}<p>{title}</p>
<ul>{lis}</ul>
{extra}
{do_now_html}<p class="muted">Dự kiến ra mắt trong những tuần tới — nội dung đang được biên soạn.</p>
{sib_html}<p>{" · ".join(links)}</p>
</section>
"""


PAGES = []


def add(path, title, h1, body, active="/", desc=None, eyebrow=None, hero=None, noindex=False, updated=None):
    PAGES.append((path, title, h1, body, active, desc, eyebrow, hero, noindex, updated))


# ---------------- Trang chủ ----------------
add("/", "Học tiếng Anh miễn phí", "Học tiếng Anh miễn phí, từ đầu tới giỏi",
    f"""
<p>Trang đang được xây dựng dần: bài học A1–B2, trò chơi và sách học đã có — các mục còn lại sẽ thêm sau.</p>
<div class="de-progress-box" data-de-progress-box></div>
<section class="section">
<div class="cards">
  <article class="card card-tool">{card_icon("place")}<h2><a href="/bai-xep-lop.html">Bài xếp lớp</a></h2><p>Bản demo với 3 câu mẫu — thử giao diện xếp lớp rồi gợi ý lộ trình học phù hợp.</p></article>
  <article class="card card-level">{card_icon("level")}<h2><a href="/trinh-do/">Theo trình độ (A1–C2)</a></h2><p>Đã có bài học A1, A2 kèm PDF + audio miễn phí, và B1, B2 (Kingdom English) kèm PDF + audio miễn phí, cùng hướng dẫn học cho các cấp C1–C2.</p></article>
  <article class="card card-skill">{card_icon("skill")}<h2><a href="/ky-nang/">Theo kỹ năng</a></h2><p>Nghe, nói, đọc, viết — luyện từng kỹ năng riêng, có giải thích tiếng Việt.</p></article>
  <article class="card card-exam">{card_icon("exam")}<h2><a href="/luyen-thi/">Luyện thi</a></h2><p>IELTS · TOEIC · PTE · TOEFL · VSTEP — cấu trúc bài thi, mẹo làm bài từng phần và bài luyện.</p></article>
  <article class="card card-kids">{card_icon("kids")}<h2><a href="/tre-em.html">Trẻ em</a></h2><p>Tiếng Anh cho trẻ em: từ vựng theo chủ đề, bài hát, trò chơi, truyện ngắn.</p></article>
  <article class="card card-work">{card_icon("work")}<h2><a href="/cong-viec.html">Tiếng Anh công việc</a></h2><p>Tiếng Anh cho từng ngành nghề: kinh doanh, y tế, công nghệ, du lịch, và hơn nữa.</p></article>
  <article class="card card-abroad">{card_icon("abroad")}<h2><a href="/du-hoc.html">Du học</a></h2><p>Chuẩn bị tiếng Anh đi du học: học bổng, hồ sơ, phỏng vấn, đời sống ở nước ngoài.</p></article>
  <article class="card card-resource">{card_icon("resource")}<h2><a href="/tai-nguyen.html">Tài nguyên miễn phí</a></h2><p>Link tới tài nguyên học tiếng Anh miễn phí chất lượng cao trên mạng (British Council, BBC, Cambridge…).</p></article>
  <article class="card card-book">{card_icon("book")}<h2><a href="/sach/">Sách học</a></h2><p>Hướng dẫn tự học với các sách tiếng Anh phổ biến: Global Success, American English File, Barron's TOEIC, Mindset for IELTS.</p></article>
  <article class="card card-tool">{card_icon("dice")}<h2><a href="/tro-choi/">Trò chơi &amp; Công cụ</a></h2><p>Học tiếng Anh bằng trò chơi: luyện TOEIC, PTE, IELTS, kiểm tra trình độ, trò chơi theo lớp 4, 9, 10 và công cụ cho giáo viên.</p></article>
  <article class="card card-skill">{card_icon("cap")}<h2><a href="/hoc-voi-david.html">Học với David</a></h2><p>Học tiếng Anh 1 kèm 1 với David — giao tiếp, tiếng Anh công việc, IELTS / TOEIC, trình độ A1–B1, học online và trực tiếp.</p></article>
</div>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Công cụ AI</h2></div>
<div class="cards">
  <article class="card card-tool">{card_icon("chat")}<h2><a href="/tro-chuyen-ai.html">Trò chuyện AI</a></h2><p>Hỏi bất cứ gì về tiếng Anh — ngữ pháp, từ vựng, phát âm, luyện thi. Trả lời bằng tiếng Việt.</p></article>
  <article class="card card-tool">{card_icon("tool")}<h2><a href="/cong-cu/tu-vung.html">Tra từ bằng AI</a></h2><p>Gõ một từ tiếng Anh, AI giải nghĩa bằng tiếng Việt, kèm ví dụ và cách phát âm.</p></article>
  <article class="card card-tool">{card_icon("tool")}<h2><a href="/cong-cu/viet.html">Chữa bài viết bằng AI</a></h2><p>Dán đoạn văn tiếng Anh của bạn, AI sửa lỗi và gợi ý cách viết hay hơn.</p></article>
</div>
</section>
<p class="muted">Mọi câu trả lời của AI đều ghi rõ “AI, chưa duyệt”.</p>
""", desc="David English đang xây dựng thư viện học tiếng Anh miễn phí cho người Việt, giải thích bằng tiếng Việt — đã có bài học A1–B2, trò chơi và sách học; các mục còn lại đang được xây dựng dần.",
    hero={
        "eyebrow": TAGLINE,
        "title_html": "Học tiếng Anh <strong>miễn phí</strong>, từ đầu tới giỏi",
        "lead": "David English đang xây dựng thư viện học tiếng Anh miễn phí cho người Việt — không cần đăng ký, giải thích bằng tiếng Việt. Đã có bài học A1–B2, trò chơi và sách học; các mục còn lại đang được xây dựng dần.",
        "cta_primary": ("Bắt đầu học", "/trinh-do/"),
        "cta_secondary": ("Kiểm tra trình độ", "/tro-choi/english-level-check.html"),
    })

# ---------------- Bài xếp lớp (stub tương tác) ----------------
add("/bai-xep-lop.html", "Bài xếp lớp", "Bài xếp lớp",
    """
<p class="lead">Bản demo giao diện bài xếp lớp — 3 câu mẫu để thử, chưa phải bài kiểm tra thật. 3 câu hỏi không thể đo trình độ của bạn, vì vậy trang này không đưa ra kết quả xếp lớp.</p>
<p>Muốn kiểm tra thật? Làm bài <a href="/tro-choi/english-level-check.html">English Level Check</a> — bài kiểm tra tự thích ứng, ước lượng trình độ A1–C2 (chỉ có đọc/viết/ngữ pháp, chưa có nghe/nói), rồi gợi ý lộ trình học phù hợp.</p>
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
  <button type="button" class="btn ghost" id="placementReset">Làm lại từ đầu</button>
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
    var expl = [
      '<strong>Câu 1:</strong> “She doesn\\'t like coffee.” — ngôi thứ ba số ít (she) dùng <em>doesn\\'t</em> + động từ nguyên mẫu. “She don\\'t…” sai trợ động từ; “She not like…” thiếu trợ động từ.',
      '<strong>Câu 2:</strong> “book” là <em>danh từ</em> — tên một vật, ở đây làm tân ngữ của động từ “read” (đọc sách).',
      '<strong>Câu 3:</strong> “Could you help me, please?” là cách nhờ giúp đỡ lịch sự nhất — <em>could</em> + <em>please</em>. “Help me now.” là mệnh lệnh, nghe thô và thiếu lịch sự.'
    ];
    out.hidden = false;
    out.innerHTML = '<p><strong>Kết quả demo: bạn trả lời đúng ' + score + '/3 câu mẫu.</strong></p>'
      + '<p><strong>3 câu hỏi không thể đo trình độ của bạn.</strong> Đây không phải kết quả xếp lớp — chỉ là bản demo để thử giao diện. Bộ câu hỏi chính thức (nhiều câu, đủ 4 kỹ năng, chấm theo khung CEFR) đang được hoàn thiện.</p>'
      + '<p><strong>Giải thích từng câu:</strong></p><ul><li>' + expl.join('</li><li>') + '</li></ul>'
      + '<p><a href="/trinh-do/">Xem lộ trình theo trình độ →</a></p>';
  });
  var resetBtn = document.getElementById('placementReset');
  resetBtn.addEventListener('click', function () {
    form.reset();
    out.hidden = true;
    out.innerHTML = '';
  });
})();
</script>
""", active="/bai-xep-lop.html", eyebrow="Bài xếp lớp", desc="Bài xếp lớp demo: 3 câu mẫu để thử giao diện. Trang này không xếp lớp được — muốn kiểm tra thật, làm bài English Level Check.")


# ETA "sắp bổ sung" cho 15 trang hướng dẫn đã có nội dung đầy đủ
# (lead đã có trên cả 15 trang; ETA là kế hoạch cập nhật tiếp theo, không phải ngày ra mắt).
GUIDE_ETA = {
    "/trinh-do/b2.html": ("bài tập ôn B2 theo chủ đề và đề thi thử ngắn", "15/12/2026"),
    "/trinh-do/c1.html": ("bài tập nâng cao C1 và đề thi thử ngắn", "18/12/2026"),
    "/trinh-do/c2.html": ("bài đọc nâng cao và đề thi thử ngắn", "20/12/2026"),
    "/ky-nang/nghe.html": ("bài nghe mới có phụ đề và bài tập nghe – điền từ", "12/12/2026"),
    "/ky-nang/noi.html": ("mẫu câu giao tiếp theo tình huống và bài luyện nói có ghi âm", "14/12/2026"),
    "/ky-nang/doc.html": ("bài đọc mới theo chủ đề kèm câu hỏi đọc hiểu", "16/12/2026"),
    "/ky-nang/viet.html": ("mẫu đoạn văn và bài tập viết có chữa mẫu", "18/12/2026"),
    "/luyen-thi/ielts.html": ("đề thi thử mẫu kèm đáp án giải thích", "15/12/2026"),
    "/luyen-thi/toeic.html": ("đề thi thử mẫu kèm đáp án giải thích", "17/12/2026"),
    "/luyen-thi/toefl.html": ("đề thi thử mẫu kèm đáp án giải thích", "19/12/2026"),
    "/luyen-thi/pte.html": ("đề thi thử mẫu kèm đáp án giải thích", "21/12/2026"),
    "/luyen-thi/vstep.html": ("đề thi thử mẫu kèm đáp án giải thích", "22/12/2026"),
    "/tre-em.html": ("bài hát và truyện ngắn mới có audio", "13/12/2026"),
    "/cong-viec.html": ("mẫu email và câu phỏng vấn theo ngành", "19/12/2026"),
    "/du-hoc.html": ("cập nhật hạn nộp học bổng năm 2027 và checklist hồ sơ", "21/12/2026"),
}


def _eta_html(path):
    eta = GUIDE_ETA.get(path)
    if not eta:
        return ""
    return f'<p class="muted">Sắp bổ sung: {eta[0]} — dự kiến {eta[1]}.</p>\n'

# ---------------- Theo trình độ ----------------
LEVELS = [
    ("a1", "A1 — Mới bắt đầu", "Người chưa biết gì hoặc biết rất ít tiếng Anh: bảng chữ cái, chào hỏi, giới thiệu bản thân, số đếm, ngày giờ."),
    ("a2", "A2 — Sơ cấp", "Giao tiếp được trong các tình huống quen thuộc hằng ngày: gia đình, mua sắm, đi lại, công việc đơn giản."),
    ("b1", "B1 — Trung cấp", "Tự xử lý được hầu hết tình huống khi đi du lịch, kể chuyện, bày tỏ ý kiến, đọc hiểu văn bản quen thuộc."),
    ("b2", "B2 — Trung cấp cao", "Giao tiếp trôi chảy với người bản xứ, hiểu ý chính của văn bản phức tạp, viết luận và tranh luận."),
    ("c1", "C1 — Nâng cao", "Dùng tiếng Anh linh hoạt trong học thuật và công việc: đọc tài liệu chuyên ngành, thuyết trình, viết báo cáo."),
    ("c2", "C2 — Thành thạo", "Gần như người bản xứ: hiểu mọi thứ đọc/nghe được, diễn đạt tinh tế, viết văn bản phức tạp."),
]

# ---------------- Bài học A1–A2 (tạo từ tai-lieu/src/*.json) ----------------
# Trang bài học và trang hub A1/A2 được sinh từ cùng JSON làm PDF
# (build_de_pdf.py) để nội dung trang và PDF luôn khớp nhau.
import json as _json

LESSON_FILES = [
    ("a1", "a1-chao-hoi-gioi-thieu.json"),
    ("a1", "a1-so-dem-ngay-gio.json"),
    ("a1", "a1-gia-dinh-cua-toi.json"),
    ("a1", "a1-mon-an-va-do-uong.json"),
    ("a1", "a1-nha-cua-toi.json"),
    ("a2", "a2-everyday-english.json"),
    ("a2", "a2-mua-sam-hoi-gia.json"),
    ("a2", "a2-du-lich-va-ky-nghi.json"),
    ("a2", "a2-suc-khoe-va-co-the.json"),
    ("a2", "a2-thoi-tiet-va-mua.json"),
]
LESSONS = []  # mỗi mục: dict JSON + level + path + pdf_href
LESSONS_BY_LEVEL = {"a1": [], "a2": [], "b1": [], "b2": []}
for _lv, _fn in LESSON_FILES:
    with open(os.path.join(ROOT, "tai-lieu", "src", _fn), encoding="utf-8") as _f:
        _d = _json.load(_f)
    _d["_level"] = _lv
    _d["_path"] = f"/trinh-do/{_lv}/{_d['slug']}.html"
    _d["_pdf"] = f"/tai-lieu/{_lv}/{_d['slug']}.pdf"
    _d["_src"] = os.path.join(ROOT, "tai-lieu", "src", _fn)
    LESSONS.append(_d)
    LESSONS_BY_LEVEL[_lv].append(_d)

AI_NOTE = ('<p><span class="badge">AI, chưa duyệt</span> Bài học do AI soạn thảo, '
           'chưa được giáo viên duyệt — hãy đối chiếu với sách và giáo viên của bạn.</p>')

# Dòng giới thiệu English Level Check dùng chung ở các trang hub: trung thực —
# bài kiểm tra tự thích ứng, ước lượng A1–C2, chỉ đọc/viết/ngữ pháp.
LEVEL_CHECK_LINE = ('Chưa biết mình ở trình độ nào? Làm bài '
    '<a href="/tro-choi/english-level-check.html">English Level Check</a>'
    ' — bài kiểm tra tự thích ứng, ước lượng trình độ A1–C2 '
    '(chỉ có đọc/viết/ngữ pháp, chưa có nghe/nói).')


def _done_button(path):
    # Nút "Đánh dấu đã học xong" trên trang bài học — trạng thái do
    # assets/progress.js điền từ localStorage (data-de-done).
    return (f'<p><button type="button" class="btn de-done-btn" '
            f'data-de-done="{path}" aria-pressed="false">'
            'Đánh dấu đã học xong</button></p>')


def _esc(s):
    return htmlmod.escape(str(s), quote=False)


def _mmss(secs):
    return f"{int(secs) // 60}:{int(secs) % 60:02d}"


def lesson_body(d, prev_lesson, next_lesson):
    vocab_rows = "".join(
        f"<tr><td><strong>{_esc(v['word'])}</strong></td>"
        f"<td>{_esc(v.get('pos', ''))}</td>"
        f"<td>/{_esc(v.get('ipa', ''))}/</td>"
        f"<td>{_esc(v.get('vi', ''))}</td>"
        f"<td><em>{_esc(v.get('ex', ''))}</em></td></tr>"
        for v in d.get("vocabulary", []))
    grammar_html = ""
    for g in d.get("grammar", []):
        exs = "".join(f"<li><em>{_esc(e)}</em></li>" for e in g.get("examples", []))
        grammar_html += (f"<h3>{_esc(g['title'])}</h3>\n"
                         f"<p>{_esc(g['explain'])}</p>\n<ul>{exs}</ul>\n")
    dlg = d.get("dialogue")
    dlg_html = ""
    if dlg:
        lines = "".join(f"<p><strong>{_esc(w)}:</strong> {_esc(t)}</p>"
                        for w, t in dlg.get("lines", []))
        dlg_audio = ""
        if d.get("audio"):
            dlg_audio = (f'<p>Nghe hội thoại ({_mmss(d.get("audio_duration_secs", 0))}):</p>\n'
                         f'<audio controls preload="none" src="{d["audio"]}"></audio>\n')
        dlg_html = (f'<section class="section section-alt">\n'
                    f"<div class=\"section-head\"><h2>Hội thoại mẫu</h2>"
                    f"<p class=\"section-sub\">{_esc(dlg.get('title', ''))}</p></div>\n"
                    f"{dlg_audio}{lines}</section>\n")
    quiz = d.get("quiz", [])[:3]
    practice = ""
    for i, q in enumerate(quiz, 1):
        opts = "".join(f"<li>{chr(65 + j)}. {_esc(o)}</li>"
                       for j, o in enumerate(q["options"]))
        correct = f"{chr(65 + q['answer'])}. {_esc(q['options'][q['answer']])}"
        practice += (f"<details><summary><strong>Câu {i}.</strong> "
                     f"{_esc(q['q'])}</summary><ul>{opts}</ul>"
                     f"<p>Đáp án: <strong>{correct}</strong></p></details>\n")
    mistakes = "".join(f"<li>{_esc(m)}</li>" for m in d.get("common_mistakes", []))
    nav = []
    if prev_lesson:
        nav.append(f'<a href="{prev_lesson["_path"]}">← {prev_lesson["title"]}</a>')
    if next_lesson:
        nav.append(f'<a href="{next_lesson["_path"]}">{next_lesson["title"]} →</a>')
    nav.append(f'<a href="/trinh-do/{d["_level"]}.html">← Về trình độ {d["_level"].upper()}</a>')
    nav.append('<a href="/">← Về trang chủ</a>')
    vocab_audio_html = ""
    if d.get("vocab_audio"):
        vocab_audio_html = (f'<p>Nghe phát âm từ vựng ({_mmss(d.get("vocab_audio_duration_secs", 0))}):</p>\n'
                            f'<audio controls preload="none" src="{d["vocab_audio"]}"></audio>\n')
    return f"""
<p class="lead">{_esc(d.get("subtitle", ""))}</p>
{AI_NOTE}
{_done_button(d["_path"])}
<section class="section">
<div class="section-head"><h2>Mục tiêu bài học</h2></div>
<ul>{''.join(f"<li>{_esc(o)}</li>" for o in d.get("objectives", []))}</ul>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Từ vựng</h2><p class="section-sub">Học thuộc các từ dưới đây trước khi đọc phần ngữ pháp — mỗi từ có phiên âm IPA, nghĩa tiếng Việt và câu ví dụ.</p></div>
{vocab_audio_html}<div class="table-wrap"><table><thead><tr><th>Từ</th><th>Loại</th><th>IPA</th><th>Nghĩa</th><th>Ví dụ</th></tr></thead><tbody>{vocab_rows}</tbody></table></div>
</section>
<section class="section">
<div class="section-head"><h2>Ngữ pháp</h2><p class="section-sub">Giải thích bằng tiếng Việt, ví dụ song ngữ Anh – Việt.</p></div>
{grammar_html}</section>
{dlg_html}<section class="section">
<div class="section-head"><h2>Luyện tập nhanh</h2><p class="section-sub">Thử 3 câu trắc nghiệm — bấm vào từng câu để xem đáp án. Bài tập đầy đủ và 10 câu trắc nghiệm nằm trong file PDF dưới đây.</p></div>
{practice}</section>
<section class="section section-alt">
<div class="section-head"><h2>Lỗi thường gặp</h2><p class="section-sub">Những lỗi người Việt hay mắc ở bài này — tránh ngay từ đầu.</p></div>
<ul>{mistakes}</ul>
</section>
<p><a class="btn btn-primary" href="{d['_pdf']}">Tải PDF bài học (miễn phí)</a></p>
<p>{' · '.join(nav)}</p>
"""


for _i, _d in enumerate(LESSONS):
    _prev = LESSONS[_i - 1] if _i > 0 else None
    _next = LESSONS[_i + 1] if _i < len(LESSONS) - 1 else None
    add(_d["_path"], _d["title"], _d["title"],
        lesson_body(_d, _prev, _next),
        active="/trinh-do/", eyebrow=f"Trình độ {_d['_level'].upper()}",
        desc=_d.get("subtitle", ""), updated=_date_vn(_d["_src"]))


# ---------------- Bài học B1 — Kingdom English (tạo từ tai-lieu/src/b1-*.json) ----------------
# JSON do convert_b1.py sinh từ teaching/b1/content/*.json (nguồn duy nhất).
# Schema B1 khác A1/A2 (có Kinh Thánh, phát âm, bài nghe, đọc hiểu, bài tập
# về nhà) nên dùng renderer riêng b1_lesson_body thay vì lesson_body.
# Đáp án đầy đủ của 6 bài tập nằm trong PDF — trang chỉ liệt kê tên bài +
# hướng dẫn, không chép đáp án lên trang.
import glob as _glob

B1_FILES = sorted(
    os.path.basename(p) for p in _glob.glob(
        os.path.join(ROOT, "tai-lieu", "src", "b1-lesson-*.json")))
B1_LESSONS = []
for _fn in B1_FILES:
    with open(os.path.join(ROOT, "tai-lieu", "src", _fn), encoding="utf-8") as _f:
        _d = _json.load(_f)
    _d["_level"] = "b1"
    _d["_path"] = f"/trinh-do/b1/{_d['slug']}.html"
    _d["_pdf"] = f"/tai-lieu/b1/{_d['slug']}.pdf"
    _d["_src"] = os.path.join(ROOT, "tai-lieu", "src", _fn)
    B1_LESSONS.append(_d)
    LESSONS_BY_LEVEL["b1"].append(_d)


def _paras(text):
    """Split '\n\n'-separated teaching text into paragraphs."""
    return [p.strip() for p in (text or "").split("\n\n") if p.strip()]


def _hw_list(items):
    """Render homework items as a numbered list.

    Strings render as-is. {'q': ..., 'a': ...} dicts render the question
    only; the answer key goes into a collapsed <details> "Đáp án" block so
    it is never visible in the page text. A leading "1. " in the question
    is stripped because the <ol> already numbers the items.
    """
    qs, ans = [], []
    for x in items or []:
        if isinstance(x, dict):
            qs.append(re.sub(r"^\d+\.\s*", "", x.get("q", "")))
            ans.append(x.get("a", ""))
        else:
            qs.append(str(x))
    out = ""
    q_html = "".join(f"<li>{_esc(q)}</li>" for q in qs if q)
    if q_html:
        out += f"<ol>{q_html}</ol>\n"
    if any(ans):
        a_html = "".join(f"<li>{_esc(a)}</li>" for a in ans if a)
        out += ("<details><summary><strong>Đáp án</strong> "
                "(bấm để xem)</summary>\n"
                f"<ol>{a_html}</ol></details>\n")
    return out


def b1_lesson_body(d, prev_lesson, next_lesson):
    vocab_rows = "".join(
        f"<tr><td><strong>{_esc(v['word'])}</strong></td>"
        f"<td>{_esc(v.get('pos', ''))}</td>"
        f"<td>/{_esc(v.get('ipa', ''))}/</td>"
        f"<td>{_esc(v.get('vi', ''))}</td>"
        f"<td><em>{_esc(v.get('ex', ''))}</em></td></tr>"
        for v in d.get("vocabulary", []))
    grammar_html = ""
    for g in d.get("grammar", []):
        exs = "".join(f"<li><em>{_esc(e)}</em></li>" for e in g.get("examples", []))
        paras = "".join(f"<p>{_esc(p)}</p>\n" for p in _paras(g.get("explain", "")))
        grammar_html += f"<h3>{_esc(g['title'])}</h3>\n{paras}"
        if exs:
            grammar_html += f"<ul>{exs}</ul>\n"
        if g.get("note"):
            grammar_html += f"<p><em>{_esc(g['note'])}</em></p>\n"
    lis = d.get("listening", {})
    audio_html = ""
    if lis.get("audio"):
        audio_html = (
            f'<audio controls preload="none" src="{lis["audio"]}"></audio>\n'
            f"<p>Thời lượng: {_mmss(lis.get('duration_secs', 0))} · "
            f"{lis.get('words', 0)} từ · "
            f"<a href=\"{lis.get('script', '')}\">Xem transcript (TXT)</a></p>\n")
    rc = "".join(
        f"<details><summary><strong>Câu {i}.</strong> {_esc(r['q'])}</summary>"
        f"<p>Đáp án: {_esc(r['a'])}</p></details>\n"
        for i, r in enumerate(d.get("reading_comprehension", []), 1))
    lq = "".join(
        f"<details><summary><strong>Câu {i}.</strong> {_esc(r['q'])}</summary>"
        f"<p>Đáp án: {_esc(r['a'])}</p></details>\n"
        for i, r in enumerate(d.get("listening_questions", []), 1))
    exs_html = "".join(
        f"<li><strong>{_esc(e['title'])}.</strong> {_esc(e['instruction'])} "
        f"({e['items']} câu)</li>"
        for e in d.get("exercises", []))
    hw = d.get("homework", {})
    hw_html = ""
    if hw:
        written = hw.get("written", "")
        listening = hw.get("listening", "")
        verse = hw.get("memory_verse", "")
        verse_vi = hw.get("memory_verse_vi", "")
        hw_html = ("<section class=\"section section-alt\">\n"
                   "<div class=\"section-head\"><h2>Bài tập về nhà</h2></div>\n"
                   + (f"<p><strong>Viết:</strong></p>\n{_hw_list(written)}"
                      if isinstance(written, list) and written else "")
                   + (f"<p><strong>Viết:</strong> {_esc(written)}</p>\n"
                      if isinstance(written, str) and written else "")
                   + (f"<p><strong>Nghe:</strong></p>\n{_hw_list(listening)}"
                      if isinstance(listening, list) and listening else "")
                   + (f"<p><strong>Nghe:</strong> {_esc(listening)}</p>\n"
                      if isinstance(listening, str) and listening else "")
                   + (f"<p><strong>Câu ghi nhớ:</strong> <em>{_esc(verse)}</em></p>\n" if verse else "")
                   + (f"<p><em>{_esc(verse_vi)}</em></p>\n" if verse_vi else "")
                   + "</section>\n")
    extra = ""
    if d.get("reading_passage"):
        passage_paras = "".join(
            f"<p>{_esc(p)}</p>\n" for p in _paras(d["reading_passage"]))
        extra += ("<section class=\"section\">\n<div class=\"section-head\">"
                  "<h2>Bài đọc</h2></div>\n"
                  f"{passage_paras}</section>\n")
    if d.get("speaking_task"):
        extra += ("<section class=\"section section-alt\">\n<div class=\"section-head\">"
                  "<h2>Nói</h2></div>\n"
                  f"<p>{_esc(d['speaking_task'])}</p></section>\n")
    if d.get("writing_task"):
        extra += ("<section class=\"section\">\n<div class=\"section-head\">"
                  "<h2>Viết</h2></div>\n"
                  f"<p>{_esc(d['writing_task'])}</p></section>\n")
    n_lq = len(d.get("listening_questions", []))
    if n_lq:
        listen_sub = (f"Nghe toàn bộ bài, rồi trả lời {n_lq} câu hỏi bên dưới. "
                      "Giọng đọc: Casper (người dẫn) và Aria (đối thoại).")
    else:
        listen_sub = ("Nghe toàn bộ bài. Giọng đọc: Casper (người dẫn) "
                      "và Aria (đối thoại).")
    pron_paras = "".join(
        f"<p>{_esc(p)}</p>\n" for p in _paras(d.get("pronunciation_detail", "")))
    if not pron_paras:
        pron_paras = ("<p>Phần luyện phát âm chi tiết nằm trong "
                      "file PDF bài học.</p>\n")
    nav = []
    if prev_lesson:
        nav.append(f"<a href=\"{prev_lesson['_path']}\">← {prev_lesson['title']}</a>")
    else:
        nav.append("<a href=\"/trinh-do/a2/thoi-tiet-va-mua.html\">← Ôn lại A2: Thời tiết và mùa</a>")
    if next_lesson:
        nav.append(f"<a href=\"{next_lesson['_path']}\">{next_lesson['title']} →</a>")
    else:
        nav.append("<a href=\"/trinh-do/b2.html\">Lên trình độ B2 →</a>")
    nav.append("<a href=\"/trinh-do/b1.html\">← Về trình độ B1</a>")
    nav.append("<a href=\"/\">← Về trang chủ</a>")
    return f"""
<p class="lead">{_esc(d.get("subtitle", ""))}</p>
{AI_NOTE}
{_done_button(d["_path"])}
<section class="section">
<div class="section-head"><h2>Mục tiêu bài học</h2><p class="section-sub">Mục tiêu rút từ chính nội dung bài: ngữ pháp, phát âm và đoạn Kinh Thánh của bài.</p></div>
<ul>{''.join(f"<li>{_esc(o)}</li>" for o in d.get("objectives", []))}</ul>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Từ vựng</h2><p class="section-sub">{len(d.get("vocabulary", []))} từ — mỗi từ có phiên âm IPA, nghĩa tiếng Việt và câu ví dụ.</p></div>
<div class="table-wrap"><table><thead><tr><th>Từ</th><th>Loại</th><th>IPA</th><th>Nghĩa</th><th>Ví dụ</th></tr></thead><tbody>{vocab_rows}</tbody></table></div>
</section>
<section class="section">
<div class="section-head"><h2>Ngữ pháp</h2><p class="section-sub">Giải thích và ví dụ từ chính bài học.</p></div>
{grammar_html}</section>
<section class="section section-alt">
<div class="section-head"><h2>Phát âm</h2><p class="section-sub">Luyện phát âm theo bài — nghe audio và đọc to theo.</p></div>
<p><strong>{_esc(d.get("pronunciation", ""))}</strong></p>
{pron_paras}<p>Đoạn Kinh Thánh của bài: <strong>{_esc(d.get("scripture", ""))}</strong></p>
</section>
<section class="section">
<div class="section-head"><h2>Bài nghe</h2><p class="section-sub">{listen_sub}</p></div>
{audio_html}</section>
{f'<section class="section section-alt"><div class="section-head"><h2>Câu hỏi nghe hiểu</h2></div>{lq}</section>' if lq else ""}
{extra}
{f'<section class="section"><div class="section-head"><h2>Đọc hiểu</h2></div>{rc}</section>' if rc else ""}
<section class="section section-alt">
<div class="section-head"><h2>Bài tập</h2><p class="section-sub">6 bài tập trong file PDF — đáp án đầy đủ nằm ở cuối PDF.</p></div>
<ul>{exs_html}</ul>
</section>
{hw_html}
<p><a class="btn btn-primary" href="{d['_pdf']}">Tải PDF bài học (miễn phí, 9 trang)</a></p>
<p>{' · '.join(nav)}</p>
"""


for _i, _d in enumerate(B1_LESSONS):
    _prev = B1_LESSONS[_i - 1] if _i > 0 else None
    _next = B1_LESSONS[_i + 1] if _i < len(B1_LESSONS) - 1 else None
    add(_d["_path"], _d["title"], _d["title"],
        b1_lesson_body(_d, _prev, _next),
        active="/trinh-do/", eyebrow="Trình độ B1 — Kingdom English",
        desc=_d.get("subtitle", ""), updated=_date_vn(_d["_src"]))

# ---------------- Bài học B2 — Kingdom English (tạo từ tai-lieu/src/b2-*.json) ----------------
# JSON do convert_b2.py sinh từ teaching/b2/content/*.json (nguồn duy nhất).
# Song song với B1: renderer riêng b2_lesson_body (bản sao của b1_lesson_body
# hiện hành, chỉ đổi nav mặc định và liên kết về hub B2). Grammar và
# pronunciation đầy đủ nằm ngay trên trang (không chỉ trỏ sang PDF).
B2_FILES = sorted(
    os.path.basename(p) for p in _glob.glob(
        os.path.join(ROOT, "tai-lieu", "src", "b2-lesson-*.json")))
B2_LESSONS = []
for _fn in B2_FILES:
    with open(os.path.join(ROOT, "tai-lieu", "src", _fn), encoding="utf-8") as _f:
        _d = _json.load(_f)
    _d["_level"] = "b2"
    _d["_path"] = f"/trinh-do/b2/{_d['slug']}.html"
    _d["_pdf"] = f"/tai-lieu/b2/{_d['slug']}.pdf"
    _d["_src"] = os.path.join(ROOT, "tai-lieu", "src", _fn)
    B2_LESSONS.append(_d)
    LESSONS_BY_LEVEL["b2"].append(_d)


def b2_lesson_body(d, prev_lesson, next_lesson):
    vocab_rows = "".join(
        f"<tr><td><strong>{_esc(v['word'])}</strong></td>"
        f"<td>{_esc(v.get('pos', ''))}</td>"
        f"<td>/{_esc(v.get('ipa', ''))}/</td>"
        f"<td>{_esc(v.get('vi', ''))}</td>"
        f"<td><em>{_esc(v.get('ex', ''))}</em></td></tr>"
        for v in d.get("vocabulary", []))
    grammar_html = ""
    for g in d.get("grammar", []):
        exs = "".join(f"<li><em>{_esc(e)}</em></li>" for e in g.get("examples", []))
        paras = "".join(f"<p>{_esc(p)}</p>\n" for p in _paras(g.get("explain", "")))
        grammar_html += f"<h3>{_esc(g['title'])}</h3>\n{paras}"
        if exs:
            grammar_html += f"<ul>{exs}</ul>\n"
        if g.get("note"):
            grammar_html += f"<p><em>{_esc(g['note'])}</em></p>\n"
    lis = d.get("listening", {})
    audio_html = ""
    if lis.get("audio"):
        audio_html = (
            f'<audio controls preload="none" src="{lis["audio"]}"></audio>\n'
            f"<p>Thời lượng: {_mmss(lis.get('duration_secs', 0))} · "
            f"{lis.get('words', 0)} từ · "
            f"<a href=\"{lis.get('script', '')}\">Xem transcript (TXT)</a></p>\n")
    rc = "".join(
        f"<details><summary><strong>Câu {i}.</strong> {_esc(r['q'])}</summary>"
        f"<p>Đáp án: {_esc(r['a'])}</p></details>\n"
        for i, r in enumerate(d.get("reading_comprehension", []), 1))
    lq = "".join(
        f"<details><summary><strong>Câu {i}.</strong> {_esc(r['q'])}</summary>"
        f"<p>Đáp án: {_esc(r['a'])}</p></details>\n"
        for i, r in enumerate(d.get("listening_questions", []), 1))
    exs_html = "".join(
        f"<li><strong>{_esc(e['title'])}.</strong> {_esc(e['instruction'])} "
        f"({e['items']} câu)</li>"
        for e in d.get("exercises", []))
    hw = d.get("homework", {})
    hw_html = ""
    if hw:
        written = hw.get("written", "")
        listening = hw.get("listening", "")
        verse = hw.get("memory_verse", "")
        verse_vi = hw.get("memory_verse_vi", "")
        hw_html = ("<section class=\"section section-alt\">\n"
                   "<div class=\"section-head\"><h2>Bài tập về nhà</h2></div>\n"
                   + (f"<p><strong>Viết:</strong></p>\n{_hw_list(written)}"
                      if isinstance(written, list) and written else "")
                   + (f"<p><strong>Viết:</strong> {_esc(written)}</p>\n"
                      if isinstance(written, str) and written else "")
                   + (f"<p><strong>Nghe:</strong></p>\n{_hw_list(listening)}"
                      if isinstance(listening, list) and listening else "")
                   + (f"<p><strong>Nghe:</strong> {_esc(listening)}</p>\n"
                      if isinstance(listening, str) and listening else "")
                   + (f"<p><strong>Câu ghi nhớ:</strong> <em>{_esc(verse)}</em></p>\n" if verse else "")
                   + (f"<p><em>{_esc(verse_vi)}</em></p>\n" if verse_vi else "")
                   + "</section>\n")
    extra = ""
    if d.get("reading_passage"):
        passage_paras = "".join(
            f"<p>{_esc(p)}</p>\n" for p in _paras(d["reading_passage"]))
        extra += ("<section class=\"section\">\n<div class=\"section-head\">"
                  "<h2>Bài đọc</h2></div>\n"
                  f"{passage_paras}</section>\n")
    if d.get("speaking_task"):
        extra += ("<section class=\"section section-alt\">\n<div class=\"section-head\">"
                  "<h2>Nói</h2></div>\n"
                  f"<p>{_esc(d['speaking_task'])}</p></section>\n")
    if d.get("writing_task"):
        extra += ("<section class=\"section\">\n<div class=\"section-head\">"
                  "<h2>Viết</h2></div>\n"
                  f"<p>{_esc(d['writing_task'])}</p></section>\n")
    n_lq = len(d.get("listening_questions", []))
    if n_lq:
        listen_sub = (f"Nghe toàn bộ bài, rồi trả lời {n_lq} câu hỏi bên dưới. "
                      "Giọng đọc: Casper (người dẫn) và Aria (đối thoại).")
    else:
        listen_sub = ("Nghe toàn bộ bài. Giọng đọc: Casper (người dẫn) "
                      "và Aria (đối thoại).")
    pron_paras = "".join(
        f"<p>{_esc(p)}</p>\n" for p in _paras(d.get("pronunciation_detail", "")))
    if not pron_paras:
        pron_paras = ("<p>Phần luyện phát âm chi tiết nằm trong "
                      "file PDF bài học.</p>\n")
    nav = []
    if prev_lesson:
        nav.append(f"<a href=\"{prev_lesson['_path']}\">← {prev_lesson['title']}</a>")
    else:
        nav.append("<a href=\"/trinh-do/b1/b1-lesson-12-revelation-hope.html\">← Ôn lại B1: Khải Huyền và Hy Vọng</a>")
    if next_lesson:
        nav.append(f"<a href=\"{next_lesson['_path']}\">{next_lesson['title']} →</a>")
    else:
        nav.append("<a href=\"/trinh-do/c1.html\">Lên trình độ C1 →</a>")
    nav.append("<a href=\"/trinh-do/b2.html\">← Về trình độ B2</a>")
    nav.append("<a href=\"/\">← Về trang chủ</a>")
    return f"""
<p class="lead">{_esc(d.get("subtitle", ""))}</p>
{AI_NOTE}
{_done_button(d["_path"])}
<section class="section">
<div class="section-head"><h2>Mục tiêu bài học</h2><p class="section-sub">Mục tiêu rút từ chính nội dung bài: ngữ pháp, phát âm và đoạn Kinh Thánh của bài.</p></div>
<ul>{''.join(f"<li>{_esc(o)}</li>" for o in d.get("objectives", []))}</ul>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Từ vựng</h2><p class="section-sub">{len(d.get("vocabulary", []))} từ — mỗi từ có phiên âm IPA, nghĩa tiếng Việt và câu ví dụ.</p></div>
<div class="table-wrap"><table><thead><tr><th>Từ</th><th>Loại</th><th>IPA</th><th>Nghĩa</th><th>Ví dụ</th></tr></thead><tbody>{vocab_rows}</tbody></table></div>
</section>
<section class="section">
<div class="section-head"><h2>Ngữ pháp</h2><p class="section-sub">Giải thích và ví dụ từ chính bài học.</p></div>
{grammar_html}</section>
<section class="section section-alt">
<div class="section-head"><h2>Phát âm</h2><p class="section-sub">Luyện phát âm theo bài — nghe audio và đọc to theo.</p></div>
<p><strong>{_esc(d.get("pronunciation", ""))}</strong></p>
{pron_paras}<p>Đoạn Kinh Thánh của bài: <strong>{_esc(d.get("scripture", ""))}</strong></p>
</section>
<section class="section">
<div class="section-head"><h2>Bài nghe</h2><p class="section-sub">{listen_sub}</p></div>
{audio_html}</section>
{f'<section class="section section-alt"><div class="section-head"><h2>Câu hỏi nghe hiểu</h2></div>{lq}</section>' if lq else ""}
{extra}
{f'<section class="section"><div class="section-head"><h2>Đọc hiểu</h2></div>{rc}</section>' if rc else ""}
<section class="section section-alt">
<div class="section-head"><h2>Bài tập</h2><p class="section-sub">6 bài tập trong file PDF — đáp án đầy đủ nằm ở cuối PDF.</p></div>
<ul>{exs_html}</ul>
</section>
{hw_html}
<p><a class="btn btn-primary" href="{d['_pdf']}">Tải PDF bài học (miễn phí, 9 trang)</a></p>
<p>{' · '.join(nav)}</p>
"""

for _i, _d in enumerate(B2_LESSONS):
    _prev = B2_LESSONS[_i - 1] if _i > 0 else None
    _next = B2_LESSONS[_i + 1] if _i < len(B2_LESSONS) - 1 else None
    add(_d["_path"], _d["title"], _d["title"],
        b2_lesson_body(_d, _prev, _next),
        active="/trinh-do/", eyebrow="Trình độ B2 — Kingdom English",
        desc=_d.get("subtitle", ""), updated=_date_vn(_d["_src"]))


def b2_hub_lessons_html():
    items = "".join(
        f"<li><a href=\"{l['_path']}\">Bài {l['lesson_no']}: {l['title_en']}</a> — "
        f"{l.get('subtitle', '')} · "
        f"<a href=\"{l['_pdf']}\">PDF</a> · "
        f"<a href=\"{l['listening']['audio']}\">Nghe ({_mmss(l['listening'].get('duration_secs', 0))})</a></li>"
        for l in B2_LESSONS)
    total_vocab = sum(len(l.get("vocabulary", [])) for l in B2_LESSONS)
    total_secs = sum(l["listening"].get("duration_secs", 0) for l in B2_LESSONS)
    return f"""
<section class="section">
<div class="section-head"><h2>Bài học B2 — Kingdom English</h2><p class="section-sub">6 bài học tiếng Anh trung cấp cao theo chủ đề Kinh Thánh — mỗi bài có từ vựng, ngữ pháp, phát âm đầy đủ trên trang, bài nghe (audio + transcript) và file PDF 9 trang miễn phí.</p></div>
{AI_NOTE}
<p>Tổng cộng: 6 bài · {total_vocab} từ vựng · {_mmss(total_secs)} bài nghe. Học theo thứ tự từ Bài 1 tới Bài 6 — tiếp nối mạch B1 (từ Bài Giảng Trên Núi tới Khải Huyền và Hy Vọng) ở mức sâu hơn: sống như khách lạ, đau khổ và hy vọng, khôn ngoan khi quyết định, đổi mới tâm trí, lãnh đạo phục vụ, và truyền giáo trong thế giới đa nguyên. Giọng đọc: Casper (người dẫn) và Aria (đối thoại).</p>
<ol>{items}</ol>
<p><strong>Lộ trình gợi ý:</strong> 1 bài/tuần trong 6 tuần (mỗi buổi 45–60 phút). Mỗi bài: học từ vựng → nghe 2 lần (lần 1 không nhìn transcript, lần 2 đối chiếu) → làm bài tập trong PDF → học thuộc câu ghi nhớ.</p>
<p>{LEVEL_CHECK_LINE}</p>
</section>
"""



def b1_hub_lessons_html():
    items = "".join(
        f"<li><a href=\"{l['_path']}\">Bài {l['lesson_no']}: {l['title_en']}</a> — "
        f"{l.get('subtitle', '')} · "
        f"<a href=\"{l['_pdf']}\">PDF</a> · "
        f"<a href=\"{l['listening']['audio']}\">Nghe ({_mmss(l['listening'].get('duration_secs', 0))})</a></li>"
        for l in B1_LESSONS)
    total_vocab = sum(len(l.get("vocabulary", [])) for l in B1_LESSONS)
    total_secs = sum(l["listening"].get("duration_secs", 0) for l in B1_LESSONS)
    return f"""
<section class="section">
<div class="section-head"><h2>Bài học B1 — Kingdom English</h2><p class="section-sub">12 bài học tiếng Anh trung cấp theo chủ đề Kinh Thánh — mỗi bài có từ vựng, ngữ pháp, bài nghe (audio + transcript) và file PDF 9 trang miễn phí.</p></div>
{AI_NOTE}
<p>Tổng cộng: 12 bài · {total_vocab} từ vựng · {_mmss(total_secs)} bài nghe. Học theo thứ tự từ Bài 1 tới Bài 12 — Bài 12 là bài tổng kết toàn khóa. Giọng đọc: Casper (người dẫn) và Aria (đối thoại).</p>
<ol>{items}</ol>
<p><strong>Lộ trình gợi ý:</strong> 1 bài/tuần trong 12 tuần (mỗi buổi 45–60 phút). Mỗi bài: học từ vựng → nghe 2 lần (lần 1 không nhìn transcript, lần 2 đối chiếu) → làm bài tập trong PDF → học thuộc câu ghi nhớ.</p>
<p>{LEVEL_CHECK_LINE}</p>
</section>
"""


LEVEL_ICONS = {"a1": "flag", "a2": "book", "b1": "chat",
               "b2": "abroad", "c1": "cap", "c2": "trophy"}


def level_cards():
    out = []
    for slug, name, desc in LEVELS:
        if slug in ("a1", "a2"):
            badge = ""
            note = " Đã có 5 bài học và tài liệu PDF miễn phí."
        elif slug == "b1":
            badge = ""
            note = " Đã có 12 bài học Kingdom English kèm PDF + audio miễn phí."
        elif slug == "b2":
            badge = ""
            note = " Đã có 6 bài học Kingdom English kèm PDF + audio miễn phí."
        else:
            badge = ""
            note = " Đã có hướng dẫn học đầy đủ."
        out.append(
            f'<article class="card card-level">{card_icon(LEVEL_ICONS[slug])}'
            f'<span class="level-chip lv-{slug}">{slug.upper()}</span>'
            f'<h2><a href="/trinh-do/{slug}.html">{name}</a></h2>'
            f'{badge}<p>{desc}{note}</p></article>')
    return "".join(out)


def level_hub_body(slug, name, desc):
    lessons = LESSONS_BY_LEVEL[slug]
    items = "".join(
        f'<li><a href="{l["_path"]}">{l["title"]}</a> — {l["subtitle"]}</li>'
        for l in lessons)
    pdfs = "".join(
        f'<li><a href="{l["_pdf"]}">{l["title"]} (PDF, miễn phí)</a></li>'
        for l in lessons)
    extra = ""
    if slug == "a2":
        extra = """
<section class="section section-alt">
<div class="section-head"><h2>Sách bài tập của thầy David (miễn phí)</h2></div>
<p>Hai bộ sách bài tập do chính thầy David biên soạn cho lớp học của mình — tải miễn phí tại đây:</p>
<ul>
<li><a href="/tai-lieu/a2/On-tap-tieng-Anh-Unit-9-12.pdf">Ôn tập tiếng Anh — Units 9–12 (PDF, 21 trang)</a> — bài tập ôn tập từ vựng và ngữ pháp Units 9–12.</li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-01-Creation-Fall-and-Promise.pdf">Kingdom English A2 — Unit 1: Creation, Fall, and Promise (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-02-The-Covenant-with-Abraham.pdf">Kingdom English A2 — Unit 2: The Covenant with Abraham (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-03-The-Parables-Compassion-of-Jesus.pdf">Kingdom English A2 — Unit 3: The Parables & Compassion of Jesus (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-04-The-Cross-Resurrection.pdf">Kingdom English A2 — Unit 4: The Cross & Resurrection (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-05-Pentecost-The-Early-Church.pdf">Kingdom English A2 — Unit 5: Pentecost & The Early Church (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-06-The-Reformation-The-Bible-in-Our-Heart-Language.pdf">Kingdom English A2 — Unit 6: The Reformation & The Bible in Our Heart Language (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-07-Saved-by-Grace-Through-Faith.pdf">Kingdom English A2 — Unit 7: Saved by Grace Through Faith (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-08-The-Fruit-of-the-Spirit-Abiding-in-Christ.pdf">Kingdom English A2 — Unit 8: The Fruit of the Spirit & Abiding in Christ (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-09-Prayer.pdf">Kingdom English A2 — Unit 9: Prayer (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-10-Church-Baptism-Lords-Supper.pdf">Kingdom English A2 — Unit 10: Church, Baptism, Lord's Supper (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-11-Evangelism-Missions.pdf">Kingdom English A2 — Unit 11: Evangelism, Missions (PDF)</a></li>
<li><a href="/tai-lieu/a2/Kingdom-English-A2-Unit-12-Second-Coming-Eternal-Hope.pdf">Kingdom English A2 — Unit 12: Second Coming, Eternal Hope (PDF)</a></li>
</ul>
<p class="muted">Kingdom English A2 là bộ sách bài tập tiếng Anh theo chủ đề Kinh Thánh, trình độ A2 — mỗi unit có từ vựng, bài đọc, ngữ pháp và bài tập.</p>
</section>"""
    nxt = {"a1": ("A2", "/trinh-do/a2.html"), "a2": ("B1", "/trinh-do/b1.html")}[slug]
    # Trang A2 có thêm mục sách bài tập (section-alt) ngay sau mục PDF —
    # để PDF dùng section thường, tránh hai section-alt kề nhau tạo vệt đôi.
    pdf_cls = "section" if extra else "section section-alt"
    return f"""
<p class="lead">{desc}</p>
<section class="section">
<div class="section-head"><h2>Bài học</h2></div>
{AI_NOTE}
<ul>{items}</ul>
</section>
<section class="{pdf_cls}">
<div class="section-head"><h2>Tài liệu PDF miễn phí</h2></div>
<ul>{pdfs}</ul>
</section>
{extra}<p>{LEVEL_CHECK_LINE}</p>
<p><a href="{nxt[1]}">{nxt[0]} →</a> · <a href="/trinh-do/">← Tất cả trình độ</a> · <a href="/tro-choi/english-level-check.html">Làm bài English Level Check →</a> · <a href="/tro-chuyen-ai.html?q={quote(f"Cho tôi lộ trình học tiếng Anh trình độ {slug.upper()}.", safe="")}">Hỏi AI về lộ trình học →</a></p>
"""


add("/trinh-do/index.html", "Theo trình độ", "Học theo trình độ (A1–C2)",
    """
<p class="lead">Chọn trình độ của bạn để đi đúng lộ trình — mỗi cấp độ sẽ có từ vựng, ngữ pháp, bài đọc, bài nghe và bài tập riêng.</p>
<p>Chưa biết mình ở trình độ nào? Làm bài <a href="/tro-choi/english-level-check.html">English Level Check</a> — bài kiểm tra tự thích ứng, ước lượng trình độ A1–C2 (chỉ có đọc/viết/ngữ pháp, chưa có nghe/nói).</p>
<div class="de-progress-box" data-de-progress-box></div>
<p><a href="/ke-hoach-hoc.html">Xem kế hoạch học →</a> · Bạn cũng có thể thử <a href="/bai-xep-lop.html">bản demo 3 câu mẫu</a> (chỉ để thử giao diện, không xếp lớp được).</p>
<section class="section">
<div class="cards">
""" + level_cards() + """
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
""", active="/trinh-do/", eyebrow="Theo trình độ", desc="Học tiếng Anh theo trình độ A1–C2: chọn cấp độ của bạn để xem lộ trình, từ vựng, ngữ pháp và bài tập — đã có bài học A1, A2, B1 và B2 kèm PDF + audio miễn phí.")
# ---------------- Kế hoạch học ----------------
add("/ke-hoach-hoc.html", "Kế hoạch học", "Kế hoạch học tiếng Anh của bạn",
    guide_sections("""
<p class="lead">Bạn không cần học lan man: làm bài kiểm tra trình độ trước, bắt đầu đúng chỗ, học theo thứ tự, rồi theo dõi tiến độ ngay trên trang này. Trang này chỉ dẫn đường — mọi bài học đều nằm ở các trang đã có, bấm vào là tới.</p>
<h2>Bước 1 — Làm bài English Level Check trước</h2>
<p>Chưa biết mình ở trình độ nào? Làm bài <a href="/tro-choi/english-level-check.html">English Level Check</a> — bài kiểm tra tự thích ứng, ước lượng trình độ A1–C2 (chỉ có đọc/viết/ngữ pháp, chưa có nghe/nói). Bài kiểm tra gợi ý bạn nên bắt đầu ở trình độ nào, rồi quay lại trang này để xem bước tiếp theo.</p>
<p>Trang <a href="/bai-xep-lop.html">Bài xếp lớp</a> chỉ là bản demo 3 câu mẫu để thử giao diện — trang đó không xếp lớp được, đừng dùng kết quả demo để chọn trình độ.</p>
<h2>Bước 2 — Đọc kết quả, bắt đầu ở đâu</h2>
<p>Tùy kết quả English Level Check, bạn bắt đầu ở đây:</p>
<div class="table-wrap"><table><thead><tr><th>Kết quả kiểm tra</th><th>Bắt đầu ở đâu</th></tr></thead><tbody>
<tr><td>A1</td><td><a href="/trinh-do/a1/chao-hoi-gioi-thieu.html">A1 Bài 1: Chào hỏi và giới thiệu bản thân</a></td></tr>
<tr><td>A2</td><td>Ôn nhanh <a href="/trinh-do/a1.html">A1</a> rồi bắt đầu <a href="/trinh-do/a2/everyday-english.html">A2 Bài 1: Everyday English — Tiếng Anh hằng ngày</a></td></tr>
<tr><td>B1</td><td><a href="/trinh-do/b1/b1-lesson-01-sermon-on-the-mount.html">B1 Bài 1: Bài Giảng Trên Núi</a></td></tr>
<tr><td>B2</td><td><a href="/trinh-do/b2/b2-lesson-01-living-as-exiles.html">B2 Bài 1: Sống Như Khách Lạ Trên Đất</a></td></tr>
<tr><td>C1 / C2</td><td><a href="/trinh-do/c1.html">Hướng dẫn tự học C1</a> và <a href="/trinh-do/c2.html">hướng dẫn tự học C2</a> — chưa có bài học theo bài, học theo lộ trình gợi ý trên các trang đó</td></tr>
</tbody></table></div>
<h2>Bước 3 — Thứ tự học</h2>
<p>Học theo thứ tự <a href="/trinh-do/a1.html">A1</a> → <a href="/trinh-do/a2.html">A2</a> → <a href="/trinh-do/b1.html">B1</a> → <a href="/trinh-do/b2.html">B2</a>, hết bài này mới sang bài sau trong cùng một trình độ. Song song với bài học theo trình độ, luyện riêng từng kỹ năng ở <a href="/ky-nang/">Theo kỹ năng (nghe, nói, đọc, viết)</a>. Khi học tới B1, bắt đầu làm quen với <a href="/luyen-thi/">Luyện thi (IELTS, TOEIC, PTE, TOEFL, VSTEP)</a> nếu bạn có mục tiêu thi chứng chỉ.</p>
<h2>Nhịp học — xem kế hoạch có sẵn của từng trình độ</h2>
<p>Trang này không đặt ra nhịp học mới — mỗi trình độ đã có kế hoạch của riêng nó, bạn cứ theo đó:</p>
<ul>
<li><a href="/trinh-do/b1.html">Trình độ B1</a> — mục “Lộ trình học 8 tuần lên B1 vững”.</li>
<li><a href="/trinh-do/c1.html">Trình độ C1</a> — mục “Lộ trình học 12 tuần lên C1 vững”.</li>
<li>Trang <a href="/trinh-do/b1.html">B1</a> và <a href="/trinh-do/b2.html">B2</a> cũng ghi lộ trình gợi ý theo từng bài (1 bài/tuần).</li>
</ul>
<h2>Cách theo dõi tiến độ</h2>
<p>Trang này không cần tài khoản — tiến độ chỉ lưu trên chính trình duyệt của bạn:</p>
<ul>
<li><strong>Đánh dấu bài đã học:</strong> mỗi trang bài học (28 bài A1–B2) đều có nút “Đánh dấu đã học xong” ở đầu bài. Bấm một lần để đánh dấu, bấm lại để bỏ đánh dấu; bài đã học xong hiện dấu ✓.</li>
<li><strong>Hộp “Tiến độ của bạn”:</strong> trên <a href="/">trang chủ</a> và <a href="/trinh-do/">trang Theo trình độ</a> — cho biết bạn đã học xong mấy trên 28 bài, từng trình độ được mấy bài, chuỗi ngày học của bạn, và bài tiếp theo nên học (“Tiếp tục”).</li>
<li><strong>Chuỗi ngày học:</strong> mỗi ngày bạn đánh dấu xong một bài, chuỗi tăng thêm 1; bỏ cách một ngày thì chuỗi tính lại từ đầu.</li>
<li><strong>Ôn từ vựng:</strong> dùng <a href="/tro-choi/flashcards.html">Flashcards — ôn từ vựng</a> để ôn lại từ của các bài đã học; từ nào bạn đã thuộc hay chưa thuộc cũng được lưu cùng một chỗ với tiến độ bài học.</li>
</ul>
<p>Xóa dữ liệu trình duyệt là xóa luôn tiến độ — trang không giữ bản sao nào trên máy chủ.</p>
<h2>Kiểm tra lại</h2>
<p>Học xong một trình độ (ví dụ hết 5 bài A1), làm lại bài <a href="/tro-choi/english-level-check.html">English Level Check</a> để xem mình có lên trình độ mới chưa, rồi bắt đầu Bài 1 của trình độ tiếp theo theo bảng ở Bước 2.</p>
<p><a href="/trinh-do/">← Tất cả trình độ</a> · <a href="/tro-choi/english-level-check.html">Làm bài English Level Check →</a> · <a href="/">← Về trang chủ</a></p>
"""), active="/trinh-do/", eyebrow="Theo trình độ",
    desc="Kế hoạch học tiếng Anh: làm bài English Level Check trước, bắt đầu đúng trình độ, học theo thứ tự A1 → A2 → B1 → B2, và theo dõi tiến độ ngay trên trang.")

# ---------------- Học với David (học 1 kèm 1) ----------------
# Trang giới thiệu lớp học 1 kèm 1 với David — KHÔNG thay trang chủ (thư viện
# tự học miễn phí vẫn là cửa chính). Chỉ ghi sự thật đã kiểm chứng: 10 năm dạy,
# TOEFL iBT 97, trình độ A1–B1, học 1 kèm 1 online (Zoom) và trực tiếp.
# Đã kiểm chứng (David 24/11): TESOL + du học Mỹ đúng; học phí 200k (giao tiếp/
# công việc) + 300k (IELTS)/giờ; Zalo 0902821991; lịch trao đổi qua Zalo.
# Học 1 kèm 1, KHÔNG "tối đa 3 học viên". Khoảng trắng giữa </b> và <span>
# (trust items) và giữa các chip <span> là BẮT BUỘC — không có CSS thì
# chữ vẫn phải đọc được (lỗi David báo 24/11: "10 nămKinh nghiệm").
add("/hoc-voi-david.html", "Học với David", "Học tiếng Anh 1 kèm 1 với David",
    guide_sections(f"""
<p class="lead">Trang này là lớp học 1 kèm 1 với David — khác với thư viện tự học miễn phí của trang web. Bạn học trực tiếp với giáo viên, theo lộ trình riêng của mình, trình độ A1–B1, online qua Zoom và trực tiếp.</p>
<div class="tutor-trust">
<div class="tutor-trust-item"><b>10 năm</b> <span>Kinh nghiệm<br>giảng dạy tiếng Anh</span></div>
<div class="tutor-trust-item"><b>TOEFL 97</b> <span>TOEFL iBT 97/120<br>tương đương IELTS 7.0–7.5</span></div>
<div class="tutor-trust-item"><b>1 kèm 1</b> <span>Học riêng với giáo viên<br>không học theo lớp đông</span></div>
<div class="tutor-trust-item"><b>A1–B1</b> <span>Trình độ học viên<br>học 1 kèm 1</span></div>
</div>
<h2>Học cùng ai</h2>
<p>David — 10 năm kinh nghiệm giảng dạy tiếng Anh, chứng chỉ TESOL, TOEFL iBT 97/120 (tương đương IELTS 7.0–7.5), và từng du học tại Hoa Kỳ. Dạy học viên trình độ A1–B1, học 1 kèm 1, online qua Zoom và trực tiếp. Phương pháp tập trung vào sự rõ ràng, thực hành và tiến bộ bền vững.</p>
<p class="tutor-chips"><span>10 năm kinh nghiệm</span> <span>TESOL</span> <span>TOEFL iBT 97</span> <span>Du học Hoa Kỳ</span></p>
<h2>Chọn mục tiêu của bạn</h2>
<p>Không học dàn trải. Tập trung vào kỹ năng và mục tiêu bạn cần sử dụng.</p>
<div class="cards">
<article class="card card-skill">{card_icon("chat")}<h3>Giao tiếp tiếng Anh</h3><p>Xây nền tảng nghe — nói và phản xạ trong những tình huống đời sống.</p><ul><li>Trình độ A1 đến B1</li><li>Phát âm và phản xạ</li><li>Chủ đề đời sống hằng ngày</li></ul></article>
<article class="card card-work">{card_icon("work")}<h3>English for Work</h3><p>Dùng tiếng Anh tự tin hơn trong môi trường làm việc và giao tiếp chuyên nghiệp.</p><ul><li>Email và trao đổi công việc</li><li>Họp và thuyết trình</li><li>Tình huống nghề nghiệp</li></ul></article>
<article class="card card-exam">{card_icon("exam")}<h3>IELTS / TOEIC</h3><p>Ôn luyện có chiến lược, củng cố nền tảng và luyện kỹ năng theo mục tiêu.</p><ul><li>Đánh giá đầu vào</li><li>Chiến lược làm bài</li><li>Bài tập và phản hồi</li></ul></article>
</div>
<h2>Vì sao học 1 kèm 1</h2>
<div class="cards">
<article class="card"><h3>01 · Đánh giá đầu vào</h3><p>Xác định trình độ, điểm mạnh và khoảng trống cần cải thiện — bắt đầu bằng bài English Level Check.</p></article>
<article class="card"><h3>02 · Mục tiêu rõ ràng</h3><p>Thống nhất mục tiêu học tập và cách theo dõi tiến độ, theo trình độ và nhu cầu thật của bạn.</p></article>
<article class="card"><h3>03 · Thực hành chủ động</h3><p>Thời lượng học dành cho giao tiếp, bài tập và phản hồi — vì chỉ có một học viên, bạn được nói nhiều.</p></article>
<article class="card"><h3>04 · Theo dõi tiến bộ</h3><p>Đánh giá định kỳ theo tiến độ của bạn; kết quả tùy nền tảng đầu vào và mức độ luyện tập.</p></article>
</div>
<h2>Lịch học</h2>
<p>Lịch học trao đổi qua Zalo — sau khi đánh giá trình độ và thống nhất mục tiêu, bạn và David xếp lịch phù hợp với thời gian của bạn. Không có khung giờ cố định chung.</p>
<h2>Học phí minh bạch</h2>
<p>Học phí tính theo giờ học và mỗi học viên. Ưu đãi áp dụng theo thời lượng đăng ký.</p>
<div class="cards">
<article class="card"><h3>Giao tiếp &amp; tiếng Anh công việc</h3><p class="tutor-amount">200.000đ <small>/ giờ / học viên</small></p><p>Học 1 kèm 1.</p><ul><li>Giảm 10% khi đăng ký 3 tháng</li><li>Giảm 15% khi đăng ký 6 tháng</li><li>Giáo trình Oxford &amp; Cambridge phù hợp trình độ</li></ul></article>
<article class="card tutor-featured"><h3>IELTS</h3><p class="tutor-amount">300.000đ <small>/ giờ / học viên</small></p><p>Lộ trình luyện thi theo trình độ và mục tiêu.</p><ul><li>Đánh giá đầu vào và định hướng</li><li>Luyện kỹ năng có chiến lược</li><li>Phản hồi và bài tập theo tiến độ</li></ul></article>
</div>
<h2>Câu hỏi thường gặp</h2>
<div class="tutor-faq">
<details><summary>Lớp học có bao nhiêu học viên?</summary><p>Học 1 kèm 1 — chỉ có bạn và giáo viên, để đảm bảo thời gian thực hành và phản hồi cho từng buổi học.</p></details>
<details><summary>Tôi chưa biết trình độ của mình thì sao?</summary><p>Làm bài <a href="/tro-choi/english-level-check.html">English Level Check</a> trước để được đánh giá trình độ, rồi trao đổi về lớp phù hợp.</p></details>
<details><summary>Học bao lâu thì đạt A2, B1 hoặc IELTS 6.5?</summary><p>Thời gian phụ thuộc trình độ đầu vào, thời lượng tự học, mức độ tham gia và năng lực từng người. Các mốc trình độ là mục tiêu tham khảo, không phải cam kết kết quả.</p></details>
<details><summary>Lớp học diễn ra ở đâu?</summary><p>Học online qua Zoom và trực tiếp. Hình thức học và lịch cụ thể được thống nhất sau khi đánh giá trình độ.</p></details>
</div>
<h2>Bắt đầu như thế nào</h2>
<div class="tutor-cta">
<h3>Bắt đầu bằng một cuộc trò chuyện.</h3>
<p>Chia sẻ trình độ hiện tại và mục tiêu của bạn để được tư vấn lớp phù hợp — hoặc làm bài English Level Check trước rồi nhắn kết quả qua Zalo. Học phí và lịch học được trao đổi riêng sau khi đánh giá trình độ.</p>
<p><a class="btn" href="https://zalo.me/0902821991" target="_blank" rel="noopener">Liên hệ qua Zalo · 0902821991 ↗</a></p>
<p><a href="/tro-choi/english-level-check.html">Làm bài English Level Check trước →</a></p>
</div>
<p><a href="/trinh-do/">← Tự học miễn phí theo trình độ</a> · <a href="/ke-hoach-hoc.html">Xem kế hoạch học →</a> · <a href="/">← Về trang chủ</a></p>
"""), active="/hoc-voi-david.html", eyebrow="Học 1 kèm 1",
    desc="Học tiếng Anh 1 kèm 1 với David — giao tiếp, tiếng Anh công việc, IELTS / TOEIC, trình độ A1–B1, học online qua Zoom và trực tiếp. Bắt đầu bằng bài English Level Check.",
    hero={
        "eyebrow": "Học 1 kèm 1 · Online và trực tiếp",
        "title_html": "Tiếng Anh thực tế.<br><span class=\"tutor-lime\">Tiến bộ có định hướng.</span>",
        "lead": "Học giao tiếp, tiếng Anh công việc, IELTS hoặc TOEIC cùng David — học 1 kèm 1, có lộ trình, có phản hồi và có người đồng hành.",
        "cta_primary": ("Làm bài English Level Check", "/tro-choi/english-level-check.html"),
        "cta_secondary": ("Tự học miễn phí trước", "/trinh-do/"),
    })

# ---------------- Nội dung đầy đủ cho B1–C2, kỹ năng, luyện thi, trẻ em, công việc, du học ----------------
# Các trang dưới đây từng là stub "Sắp có" (noindex). Nội dung do AI soạn, gắn nhãn
# "AI, chưa duyệt" (AI_NOTE) — chưa được giáo viên duyệt. Bài tập là câu hỏi tự biên
# soạn để luyện tập, không sao chép đề thi thật. Số liệu về định dạng kỳ thi được
# đối chiếu với trang chính thức của đơn vị tổ chức thi (ghi rõ nguồn ở từng trang).

def _guide_nav(prev=None, next=None, parent=None, ai_question=None):
    """Dòng liên kết cuối trang hướng dẫn: bài trước/sau, trang cha, trang chủ, hỏi AI."""
    parts = []
    if prev:
        parts.append(f'<a href="{prev[1]}">← {prev[0]}</a>')
    if next:
        parts.append(f'<a href="{next[1]}">{next[0]} →</a>')
    if parent:
        parts.append(f'<a href="{parent[1]}">← {parent[0]}</a>')
    parts.append('<a href="/">← Về trang chủ</a>')
    if ai_question:
        parts.append(f'<a href="/tro-chuyen-ai.html?q={quote(ai_question, safe="")}">Hỏi AI về chủ đề này →</a>')
    return "<p>" + " · ".join(parts) + "</p>"


LEVEL_BODIES = {
"b1": """
<p class="lead">B1 là trình độ trung cấp — bạn đã qua giai đoạn "mới bắt đầu" và bắt đầu dùng tiếng Anh một cách độc lập: tự xử lý hầu hết tình huống khi đi du lịch, kể chuyện, bày tỏ ý kiến và đọc hiểu văn bản quen thuộc.</p>
""" + AI_NOTE + """
<h2>B1 nghĩa là gì?</h2>
<p>Theo Khung tham chiếu chung châu Âu (CEFR), B1 còn gọi là "Threshold" — ngưỡng độc lập. Người ở trình độ B1 có thể hiểu ý chính của văn bản rõ ràng về các chủ đề quen thuộc (công việc, học tập, giải trí), xử lý được hầu hết tình huống phát sinh khi đi du lịch ở nơi nói tiếng Anh, viết được văn bản đơn giản, có liên kết về chủ đề quen thuộc, và kể được về trải nghiệm, ước mơ, kế hoạch của mình, đồng thời nêu ngắn gọn lý do và giải thích cho ý kiến của mình.</p>
<p>Nói ngắn gọn: ở A2 bạn "sống sót" được bằng tiếng Anh; ở B1 bạn bắt đầu "sống" được bằng tiếng Anh.</p>
<h2>Bạn cần học gì ở B1?</h2>
<p><strong>Ngữ pháp trọng tâm.</strong> Đây là những cấu trúc làm nên "xương sống" của B1 — nếu chưa chắc, hãy ôn lại trước khi học thêm từ mới:</p>
<ul>
<li><strong>Hiện tại hoàn thành (present perfect) và phân biệt với quá khứ đơn:</strong> <em>I have lived here for five years</em> (vẫn đang sống) khác với <em>I lived here for five years</em> (đã chuyển đi rồi). Đây là điểm ngữ pháp người Việt hay nhầm nhất ở B1, vì tiếng Việt không chia thì.</li>
<li><strong>Quá khứ tiếp diễn + quá khứ đơn:</strong> <em>While I was walking home, it started to rain.</em> — hành động đang diễn ra thì bị hành động khác xen vào.</li>
<li><strong>Tương lai: will / going to / hiện tại tiếp diễn:</strong> <em>I will help you</em> (quyết định ngay lúc nói), <em>I am going to travel in June</em> (đã có kế hoạch), <em>I am meeting Lan tomorrow</em> (đã hẹn cụ thể).</li>
<li><strong>Câu điều kiện loại 1:</strong> <em>If it rains, we will stay at home.</em></li>
<li><strong>Câu bị động ở thì hiện tại và quá khứ đơn:</strong> <em>The house was built in 1990.</em></li>
<li><strong>So sánh hơn, so sánh nhất và so sánh bằng:</strong> <em>as … as, more … than, the most …</em></li>
<li><strong>Động từ khuyết thiếu:</strong> <em>must, have to, should, might, could</em> để diễn đạt nghĩa vụ, lời khuyên và khả năng.</li>
<li><strong>Mệnh đề quan hệ với who / which / that:</strong> <em>The book that I bought yesterday is very interesting.</em></li>
</ul>
<p><strong>Từ vựng.</strong> Ở B1, bạn mở rộng từ vựng theo chủ đề thay vì học từ rời rạc: du lịch và giao thông, sức khỏe, công việc, giáo dục, môi trường, công nghệ, tiền bạc và mua sắm. Với mỗi chủ đề, học cả cụm từ (collocation) — ví dụ không học riêng từ <em>decision</em> mà học <em>make a decision</em>; không học riêng <em>mistake</em> mà học <em>make a mistake</em>. Học từ theo cụm giúp bạn nói tự nhiên hơn nhiều so với việc ghép từng từ đơn lại.</p>
<p><strong>Bốn kỹ năng.</strong> Nghe: hiểu được hội thoại hằng ngày ở tốc độ gần tự nhiên và nắm ý chính của bản tin ngắn. Nói: kể một câu chuyện có đầu có cuối, diễn đạt ý kiến trong 1–2 phút mà không cần chuẩn bị quá lâu. Đọc: đọc được truyện ngắn, email, bài báo đơn giản và tìm được thông tin cụ thể. Viết: viết được email, đoạn văn 120–150 từ có mở bài, thân bài, kết bài rõ ràng.</p>
<h2>Checklist: bạn đã đạt B1 chưa?</h2>
<p>Tự đánh dấu những điều bạn làm được. Nếu làm được ít nhất 8/9, bạn đang ở B1 vững:</p>
<ul>
<li>☐ Kể lại một bộ phim hoặc chuyến đi trong 2 phút bằng tiếng Anh, người nghe hiểu được cốt truyện.</li>
<li>☐ Viết email xin nghỉ phép hoặc hỏi thông tin mà không cần tra từ điển từng câu.</li>
<li>☐ Nghe hiểu ý chính của một đoạn hội thoại nhanh giữa hai người bản xứ.</li>
<li>☐ Phân biệt và dùng đúng <em>have been</em> và <em>went</em>, <em>since</em> và <em>for</em>.</li>
<li>☐ Đưa ra ý kiến và bảo vệ nó bằng 2–3 lý do: <em>I think … because …</em></li>
<li>☐ Đọc một bài báo ngắn trên BBC Learning English và tóm tắt lại bằng lời của mình.</li>
<li>☐ Hỏi đường, đặt phòng khách sạn, gọi món và giải quyết rắc rối nhỏ khi đi du lịch.</li>
<li>☐ Hiểu và dùng được câu điều kiện loại 1 và câu bị động đơn giản.</li>
<li>☐ Viết đoạn văn 120 từ về chủ đề quen thuộc mà không mắc lỗi thì cơ bản.</li>
</ul>
<h2>Lộ trình học 8 tuần lên B1 vững</h2>
<p>Giả định bạn đã xong A2 và học 5 buổi/tuần, mỗi buổi 45 phút:</p>
<ul>
<li><strong>Tuần 1–2:</strong> Ôn chắc A2 và học thì hiện tại hoàn thành. Mỗi ngày viết 5 câu về bản thân dùng <em>have/has + V3</em>.</li>
<li><strong>Tuần 3–4:</strong> Câu điều kiện loại 1, câu bị động, so sánh. Luyện đọc truyện ngắn và tóm tắt lại.</li>
<li><strong>Tuần 5–6:</strong> Từ vựng theo 4 chủ đề (du lịch, sức khỏe, công việc, môi trường). Luyện nói: mỗi ngày kể một chuyện 2 phút, ghi âm lại và nghe lại.</li>
<li><strong>Tuần 7–8:</strong> Viết email và đoạn văn 120–150 từ. Làm bài kiểm tra tổng hợp: nghe một đoạn hội thoại, đọc một bài báo ngắn, viết một đoạn văn.</li>
</ul>
<p>Muốn kiểm tra mình đang ở đâu? Hãy làm bài <a href="/tro-choi/english-level-check.html">English Level Check</a> — bài kiểm tra tự thích ứng, ước lượng trình độ A1–C2 (chỉ có đọc/viết/ngữ pháp, chưa có nghe/nói) — hoặc chơi <a href="/tro-choi/intermediate-quest.html">Intermediate Quest — trò chơi trình độ trung cấp</a> để ôn từ vựng và ngữ pháp B1.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Dịch từng từ từ tiếng Việt sang tiếng Anh:</strong> <em>"I very like it"</em> — sai, vì <em>very</em> không bổ nghĩa cho động từ. Viết đúng: <em>I like it very much.</em> Quy tắc: <em>very + tính từ/trạng từ</em>, còn động từ thì dùng <em>very much / a lot</em>.</li>
<li><strong>Quên "s" ở ngôi thứ ba số ít:</strong> <em>He go to work</em> — sai. Viết đúng: <em>He goes to work.</em> Lỗi này nhỏ nhưng xuất hiện trong mọi bài thi viết.</li>
<li><strong>Dùng quá khứ đơn thay cho hiện tại hoàn thành:</strong> <em>I live here since 2020</em> — sai. Viết đúng: <em>I have lived here since 2020.</em> Nhớ: <em>since/for</em> đi với hiện tại hoàn thành khi hành động còn kéo dài tới hiện tại.</li>
<li><strong>Nhầm <em>borrow</em> và <em>lend</em>:</strong> <em>borrow</em> là mượn (về phía mình), <em>lend</em> là cho mượn. <em>Can you lend me your book?</em> / <em>Can I borrow your book?</em></li>
<li><strong>Nhầm <em>fun</em> và <em>funny</em>:</strong> <em>fun</em> là vui (thú vị), <em>funny</em> là buồn cười. <em>The party was fun</em>, không phải <em>funny</em> — trừ khi bữa tiệc làm bạn cười.</li>
<li><strong>Dịch "tôi 20 tuổi" thành <em>I have 20 years old</em>:</strong> sai. Tiếng Anh dùng động từ <em>be</em>: <em>I am 20 years old.</em></li>
<li><strong>Nói quá nhanh khi chưa chắc:</strong> ở B1, nói chậm mà đúng tốt hơn nói nhanh mà sai. Người nghe đánh giá cao câu rõ ràng hơn câu nhanh.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<p>Thử 3 câu trắc nghiệm — bấm vào từng câu để xem đáp án và giải thích.</p>
<details><summary><strong>Câu 1.</strong> Chọn câu đúng: (a) I have lived in Hanoi since five years. (b) I have lived in Hanoi for five years. (c) I live in Hanoi since five years.</summary><p>Đáp án: <strong>(b)</strong>. <em>For + khoảng thời gian</em> (for five years), <em>since + mốc thời gian</em> (since 2020). Và hành động kéo dài tới hiện tại nên dùng hiện tại hoàn thành.</p></details>
<details><summary><strong>Câu 2.</strong> Chọn câu đúng: (a) If it will rain, we stay at home. (b) If it rains, we will stay at home. (c) If it rains, we stay at home tomorrow.</summary><p>Đáp án: <strong>(b)</strong>. Câu điều kiện loại 1: mệnh đề <em>if</em> dùng hiện tại đơn, mệnh đề chính dùng <em>will</em>.</p></details>
<details><summary><strong>Câu 3.</strong> Chọn câu đúng: (a) She is more tall than her sister. (b) She is taller than her sister. (c) She is the more tall in her class.</summary><p>Đáp án: <strong>(b)</strong>. Tính từ ngắn (1 âm tiết) thêm <em>-er</em>: <em>tall → taller</em>, không dùng <em>more</em>.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Chưa chắc A2? Hãy <a href="/trinh-do/a2.html">ôn lại bài học A2</a> trước. Đã vững B1? Lên <a href="/trinh-do/b2.html">trình độ B2</a>. Nếu bạn cần chứng chỉ ở mức B1, xem <a href="/luyen-thi/vstep.html">hướng dẫn luyện thi VSTEP</a> (bậc 3 tương đương B1) hoặc <a href="/luyen-thi/toeic.html">luyện thi TOEIC</a> để dùng tiếng Anh trong công việc. Muốn luyện nghe nói? Xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a> và <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>.</p>
""",
"b2": """
<p class="lead">B2 là trình độ trung cấp cao — bạn giao tiếp trôi chảy với người bản xứ mà không khiến đôi bên căng thẳng, hiểu ý chính của văn bản phức tạp và viết được luận, email công việc và bài tranh luận có lập luận rõ ràng.</p>
""" + AI_NOTE + """
<h2>B2 nghĩa là gì?</h2>
<p>Theo CEFR, B2 còn gọi là "Vantage" — lợi thế. Người ở trình độ B2 có thể hiểu ý chính của văn bản phức tạp, cả về chủ đề cụ thể lẫn trừu tượng, kể cả các cuộc thảo luận chuyên môn trong lĩnh vực của mình; giao tiếp trôi chảy và tự nhiên tới mức cuộc trò chuyện với người bản xứ diễn ra thoải mái cho cả hai bên; và viết được văn bản rõ ràng, chi tiết về nhiều chủ đề, trình bày quan điểm về một vấn đề với ưu điểm và nhược điểm của các phương án khác nhau.</p>
<p>Điểm khác biệt lớn nhất giữa B1 và B2 không phải là số từ bạn biết, mà là <strong>độ tự nhiên</strong>: ở B1 bạn phải nghĩ rồi mới nói; ở B2 bạn nghĩ bằng tiếng Anh trong lúc nói. Đây cũng là mức mà nhiều trường đại học và nhà tuyển dụng yêu cầu.</p>
<h2>Bạn cần học gì ở B2?</h2>
<p><strong>Ngữ pháp trọng tâm.</strong> B2 đào sâu và kết hợp những gì bạn đã biết:</p>
<ul>
<li><strong>Các thì hoàn thành và hoàn thành tiếp diễn:</strong> <em>I had been working there for two years before I quit.</em> — quá khứ hoàn thành tiếp diễn diễn tả hành động kéo dài rồi kết thúc trước một mốc trong quá khứ.</li>
<li><strong>Câu điều kiện loại 2 và loại 3:</strong> <em>If I had more time, I would learn French</em> (loại 2 — giả định trái hiện tại); <em>If I had studied harder, I would have passed</em> (loại 3 — tiếc nuối về quá khứ). Phân biệt rõ 3 loại câu điều kiện là dấu hiệu của B2.</li>
<li><strong>Câu bị động ở mọi thì, kể cả bị động với động từ khuyết thiếu:</strong> <em>The report should have been finished yesterday.</em></li>
<li><strong>Câu tường thuật (reported speech):</strong> <em>She said she was tired</em> — lùi thì, đổi đại từ và trạng từ chỉ thời gian.</li>
<li><strong>Mệnh đề quan hệ không xác định và rút gọn:</strong> <em>Ha Long Bay, which is in northern Vietnam, is very beautiful.</em> / <em>The man standing over there is my teacher.</em></li>
<li><strong>Động từ khuyết thiếu suy luận:</strong> <em>He must be tired</em> (chắc chắn), <em>He might be busy</em> (có thể), <em>He can't be at home</em> (chắc chắn không).</li>
<li><strong>Cấu trúc nhấn mạnh và đảo ngữ nhẹ:</strong> <em>Not only did she win, but she also broke the record.</em></li>
<li><strong>Danh động từ và động từ nguyên mẫu sau các động từ đặc biệt:</strong> <em>I enjoy swimming</em> nhưng <em>I decided to swim</em> — nhớ theo từng động từ, không có quy tắc chung.</li>
</ul>
<p><strong>Từ vựng.</strong> Ở B2, bạn học từ theo <strong>ngữ cảnh học thuật và công việc</strong>: giáo dục, kinh tế, môi trường, công nghệ, xã hội. Quan trọng hơn số lượng là <strong>collocation và từ đồng nghĩa theo sắc thái</strong>: <em>big</em> → <em>enormous, massive, considerable</em> — mỗi từ dùng trong ngữ cảnh khác nhau. Bạn cũng cần học cụm động từ (phrasal verbs) thông dụng: <em>look into, carry out, put off, come up with, deal with</em>, vì người bản xứ dùng chúng hằng ngày.</p>
<p><strong>Bốn kỹ năng.</strong> Nghe: hiểu bài giảng, podcast và phim không phụ đề ở mức khá. Nói: tranh luận, thuyết trình 5 phút, kể chuyện có chi tiết và cảm xúc. Đọc: đọc báo, bài luận và tài liệu chuyên ngành, phân biệt được quan điểm của tác giả và sự thật. Viết: viết luận 250 từ có lập luận, email công việc trang trọng, báo cáo ngắn.</p>
<h2>Checklist: bạn đã đạt B2 chưa?</h2>
<ul>
<li>☐ Tranh luận về một chủ đề (ví dụ: có nên cấm xe máy ở trung tâm thành phố?) trong 3 phút, đưa ra được cả hai mặt của vấn đề.</li>
<li>☐ Viết bài luận 250 từ có mở bài, hai luận điểm và kết luận, dùng được từ nối như <em>however, furthermore, on the other hand</em>.</li>
<li>☐ Nghe một podcast 10 phút và tóm tắt lại ý chính mà không cần nghe lại.</li>
<li>☐ Dùng đúng câu điều kiện loại 2 và loại 3 trong cùng một đoạn nói.</li>
<li>☐ Đọc một bài báo trên BBC News và phân biệt được đâu là sự thật, đâu là ý kiến của tác giả.</li>
<li>☐ Viết email công việc trang trọng: xin việc, khiếu nại, đề xuất — dùng đúng giọng văn (register).</li>
<li>☐ Giải thích một khái niệm chuyên môn trong ngành của bạn bằng tiếng Anh cho người ngoài ngành hiểu.</li>
<li>☐ Hiểu và dùng được ít nhất 30 cụm động từ thông dụng.</li>
<li>☐ Đọc một cuốn sách tiếng Anh cấp độ B2 (graded reader) mà không cần tra từ điển quá 5 từ mỗi trang.</li>
</ul>
<h2>Lộ trình học 12 tuần lên B2 vững</h2>
<ul>
<li><strong>Tuần 1–3:</strong> Củng cố B1: ôn lại hiện tại hoàn thành, câu bị động, câu điều kiện loại 1. Bắt đầu đọc báo ngắn mỗi ngày 15 phút.</li>
<li><strong>Tuần 4–6:</strong> Câu điều kiện loại 2–3, câu tường thuật, mệnh đề quan hệ. Viết 2 bài luận 250 từ/tuần, nhờ <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> góp ý rồi tự sửa lại.</li>
<li><strong>Tuần 7–9:</strong> Từ vựng học thuật và cụm động từ. Luyện nghe podcast 20 phút/ngày, tập tóm tắt bằng lời của mình. Luyện nói: thuyết trình 5 phút về một chủ đề mỗi tuần.</li>
<li><strong>Tuần 10–12:</strong> Luyện đề tổng hợp: làm thử đề <a href="/luyen-thi/ielts.html">IELTS</a> hoặc <a href="/luyen-thi/vstep.html">VSTEP</a> (bậc 4 tương đương B2), chữa kỹ từng lỗi, ôn lại điểm yếu.</li>
</ul>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Dùng từ "rất hay" nhưng sai ngữ cảnh:</strong> <em>actual</em> không có nghĩa là "thực sự hay" mà là "thực tế, đúng sự thật": <em>the actual cost</em> (chi phí thực tế). Muốn nói "thực sự" thì dùng <em>really</em> hoặc <em>actually</em>.</li>
<li><strong>Nhầm <em>say</em> và <em>tell</em>:</strong> <em>say something</em> (nói điều gì) nhưng <em>tell someone something</em> (nói với ai điều gì). <em>She told me that she was busy</em> — không nói <em>She said me that…</em></li>
<li><strong>Dịch "tôi đồng ý với bạn" thành <em>I agree with you</em> thì đúng, nhưng nhiều người viết <em>I am agree</em> — sai.</strong> <em>Agree</em> là động từ, không cần <em>am</em>.</li>
<li><strong>Quên lùi thì trong câu tường thuật:</strong> <em>He said he is happy</em> — sai khi câu gốc nói trong quá khứ. Viết đúng: <em>He said he was happy.</em></li>
<li><strong>Dùng <em>very</em> cho mọi thứ:</strong> ở B2, hãy thay <em>very tired</em> bằng <em>exhausted</em>, <em>very good</em> bằng <em>excellent</em>, <em>very big</em> bằng <em>huge</em>. Từ mạnh làm bài viết của bạn khác hẳn.</li>
<li><strong>Viết luận chỉ liệt kê ý kiến mà không có ví dụ:</strong> mỗi luận điểm cần một ví dụ cụ thể hoặc giải thích. Luận điểm không có chứng cứ chỉ là ý kiến suông.</li>
<li><strong>Phát âm trọng âm sai ở từ dài:</strong> <em>PHOtograph</em> nhưng <em>phoTOgraphy</em> — trọng âm đổi khi thêm hậu tố. Nghe và lặp lại từng từ mới ngay khi học.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Chọn câu đúng: (a) If I would have money, I would travel. (b) If I had money, I would travel. (c) If I have money, I would travel.</summary><p>Đáp án: <strong>(b)</strong>. Câu điều kiện loại 2: <em>If + quá khứ đơn, would + động từ nguyên mẫu</em>. Không dùng <em>would</em> trong mệnh đề <em>if</em>.</p></details>
<details><summary><strong>Câu 2.</strong> Chọn câu đúng: (a) She said that she has finished her work. (b) She said that she had finished her work. (c) She said that she has finish her work.</summary><p>Đáp án: <strong>(b)</strong>. Câu tường thuật lùi thì: hiện tại hoàn thành (<em>has finished</em>) lùi thành quá khứ hoàn thành (<em>had finished</em>).</p></details>
<details><summary><strong>Câu 3.</strong> Chọn từ phù hợp: "The company decided to ___ the project because it cost too much." (a) look into (b) carry out (c) call off</summary><p>Đáp án: <strong>(c) call off</strong> (hủy bỏ). <em>Look into</em> là điều tra, <em>carry out</em> là thực hiện.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Chưa vững B1? Quay lại <a href="/trinh-do/b1.html">trình độ B1</a>. Đã vững B2? Lên <a href="/trinh-do/c1.html">trình độ C1</a>. B2 là mức cần cho nhiều mục tiêu thực tế: <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> (mục tiêu band 6.0–6.5), <a href="/luyen-thi/vstep.html">luyện thi VSTEP</a> (bậc 4 tương đương B2), <a href="/cong-viec.html">tiếng Anh công việc</a>, hoặc chơi <a href="/tro-choi/workplace-english-arcade.html">Workplace English Arcade — tiếng Anh công việc trình độ B2</a>. Học từ vựng theo sách? Xem <a href="/sach/american-english-file.html">hướng dẫn học với sách American English File</a> (tới C1).</p>
""",

"c1": """
<p class="lead">C1 là trình độ nâng cao — bạn dùng tiếng Anh linh hoạt và hiệu quả trong học thuật và công việc: đọc tài liệu chuyên ngành, thuyết trình, viết báo cáo và tranh luận mà ít khi phải dừng lại tìm từ.</p>
""" + AI_NOTE + """
<h2>C1 nghĩa là gì?</h2>
<p>Theo CEFR, C1 còn gọi là "Effective Operational Proficiency" — sử dụng hiệu quả. Người ở trình độ C1 có thể hiểu nhiều loại văn bản dài, phức tạp và nhận ra ý nghĩa hàm ẩn; diễn đạt trôi chảy, tự nhiên mà không phải tìm từ một cách rõ rệt; dùng tiếng Anh linh hoạt và hiệu quả cho mục đích xã hội, học thuật và nghề nghiệp; và viết được văn bản rõ ràng, cấu trúc tốt, chi tiết về chủ đề phức tạp, thể hiện được cách dùng có kiểm soát của các cấu trúc tổ chức, từ nối và liên kết.</p>
<p>Điểm khác biệt giữa B2 và C1 là <strong>sự tinh tế</strong>: ở B2 bạn nói đúng; ở C1 bạn nói đúng <em>và</em> đúng giọng — biết khi nào nói trang trọng, khi nào nói thân mật, khi nào nói giảm, khi nào nói thẳng. Bạn cũng bắt đầu hiểu được hài hước, châm biếm và ý nghĩa ẩn sau lời nói.</p>
<h2>Bạn cần học gì ở C1?</h2>
<p><strong>Ngữ pháp trọng tâm.</strong> Ở C1, ngữ pháp không còn là "thì mới" mà là cách dùng nâng cao:</p>
<ul>
<li><strong>Đảo ngữ để nhấn mạnh:</strong> <em>Rarely have I seen such dedication.</em> / <em>Not only is it expensive, it is also unreliable.</em></li>
<li><strong>Câu điều kiện hỗn hợp:</strong> <em>If I had saved more money, I would be travelling now.</em> — quá khứ giả định, kết quả ở hiện tại.</li>
<li><strong>Mệnh đề phân từ và mệnh đề rút gọn:</strong> <em>Having finished the report, she went home.</em> / <em>The results, published last year, show a clear trend.</em></li>
<li><strong>Câu bị động nâng cao và cấu trúc bị động với hai tân ngữ:</strong> <em>She was given the award.</em></li>
<li><strong>Câu chẻ (cleft sentences) để nhấn mạnh:</strong> <em>It was Lan who suggested the idea.</em> / <em>What I need is more time.</em></li>
<li><strong>Động từ khuyết thiếu ở thì hoàn thành để suy luận về quá khứ:</strong> <em>He must have forgotten.</em> / <em>She can't have left already.</em> / <em>They should have told us earlier.</em></li>
<li><strong>Danh từ hóa (nominalisation) trong văn viết học thuật:</strong> <em>We analysed the data</em> → <em>The analysis of the data shows…</em> — viết học thuật dùng danh từ nhiều hơn động từ.</li>
</ul>
<p><strong>Từ vựng.</strong> Ở C1, bạn học <strong>collocation học thuật</strong> (ví dụ: <em>draw a conclusion, raise concerns, play a crucial role, take something into account</em>), <strong>từ nối tinh tế</strong> (<em>nevertheless, consequently, albeit, notwithstanding</em> — và quan trọng hơn, biết khi nào <em>không</em> nên dùng chúng vì nghe quá cứng), và <strong>thành ngữ cùng cách nói giảm</strong> (<em>hedging</em>): <em>It seems that…, There is a tendency to…, This suggests that…</em> — cách diễn đạt thận trọng là dấu hiệu của văn viết trình độ cao.</p>
<p><strong>Bốn kỹ năng.</strong> Nghe: hiểu bài giảng đại học, tranh luận trên truyền hình và nhiều giọng khác nhau (Anh, Mỹ, Úc). Nói: thuyết trình 10 phút, trả lời câu hỏi phản biện, đàm phán và thuyết phục. Đọc: đọc sách chuyên ngành, bài nghiên cứu và nhận ra lập trường của tác giả. Viết: viết luận học thuật, báo cáo, đề xuất dự án với cấu trúc chặt chẽ.</p>
<h2>Checklist: bạn đã đạt C1 chưa?</h2>
<ul>
<li>☐ Đọc một bài báo học thuật 3.000 từ và tóm tắt luận điểm chính cùng bằng chứng của tác giả.</li>
<li>☐ Viết bài luận 500 từ với lập luận chặt chẽ, dùng được danh từ hóa và từ nối học thuật.</li>
<li>☐ Thuyết trình 10 phút về chủ đề chuyên môn và trả lời câu hỏi phản biện mà không lúng túng.</li>
<li>☐ Nghe một cuộc tranh luận trên đài và phân biệt được quan điểm của từng bên, kể cả khi họ nói hàm ý.</li>
<li>☐ Viết email thương lượng (đàm phán giá, thời hạn) bằng giọng văn lịch sự nhưng kiên quyết.</li>
<li>☐ Dùng đúng đảo ngữ, câu chẻ và câu điều kiện hỗn hợp trong bài viết của mình.</li>
<li>☐ Hiểu truyện cười hoặc châm biếm bằng tiếng Anh mà không cần ai giải thích.</li>
<li>☐ Chuyển giọng văn linh hoạt: viết email cho sếp khác với nhắn tin cho bạn bè.</li>
<li>☐ Đọc một cuốn sách tiếng Anh không phải sách giáo khoa (tiểu thuyết hoặc sách chuyên môn) và hiểu được 95% nội dung.</li>
<li>☐ Diễn đạt cùng một ý bằng 3 cách khác nhau, từ trang trọng tới thân mật.</li>
</ul>
<h2>Lộ trình học 12 tuần lên C1 vững</h2>
<ul>
<li><strong>Tuần 1–3:</strong> Đọc sâu: mỗi tuần đọc 2 bài báo dài (The Economist, BBC News, hoặc bài nghiên cứu trong ngành của bạn), ghi lại 20 collocation mới và đặt câu với chúng.</li>
<li><strong>Tuần 4–6:</strong> Viết học thuật: học danh từ hóa và hedging, viết 1 bài luận 500 từ/tuần, nhờ <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> góp ý rồi tự sửa lại.</li>
<li><strong>Tuần 7–9:</strong> Nghe và nói nâng cao: nghe podcast học thuật 30 phút/ngày, tập thuyết trình và ghi âm lại, chú ý ngữ điệu và nhịp ngắt câu.</li>
<li><strong>Tuần 10–12:</strong> Luyện đề: làm thử đề <a href="/luyen-thi/ielts.html">IELTS</a> mục tiêu band 7.0–7.5, hoặc đề <a href="/luyen-thi/toefl.html">TOEFL iBT</a> nếu bạn định <a href="/du-hoc.html">đi du học</a>. Chữa kỹ từng lỗi và ôn lại điểm yếu.</li>
</ul>
<p>Học từ vựng theo sách? Xem <a href="/sach/mindset-for-ielts.html">hướng dẫn học với sách Mindset for IELTS</a> (tới band 7.5) và <a href="/sach/american-english-file.html">hướng dẫn học với sách American English File</a> (Level 5 tương đương C1).</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Dùng từ nối học thuật một cách máy móc:</strong> nhồi <em>moreover, furthermore, nevertheless</em> vào mọi đoạn văn khiến bài viết nghe giả tạo. Ở C1, từ nối phải phục vụ lập luận, không phải để "khoe" từ. Một đoạn văn tốt đôi khi không cần từ nối nào.</li>
<li><strong>Dịch thành ngữ Việt sang tiếng Anh:</strong> <em>"water flows, stone wears"</em> không có nghĩa gì với người bản xứ. Học thành ngữ tiếng Anh từ nguồn tiếng Anh, đừng dịch thành ngữ Việt.</li>
<li><strong>Nhầm <em>actually</em> và <em>currently</em>:</strong> <em>actually</em> nghĩa là "thực ra", <em>currently</em> mới là "hiện tại". <em>I am currently working in Hanoi</em> — không dùng <em>actually</em>.</li>
<li><strong>Dùng <em>very</em> + từ mạnh:</strong> <em>very excellent, very perfect</em> đều sai — từ mạnh (excellent, perfect, unique) đã mang nghĩa tuyệt đối, không cần <em>very</em>.</li>
<li><strong>Viết câu quá dài:</strong> câu 40–50 từ với 3 mệnh đề phụ rất dễ sai ngữ pháp và khó đọc. Ở C1, câu hay là câu rõ ràng — tách câu dài thành 2 câu ngắn thường tốt hơn.</li>
<li><strong>Nhầm <em>economic</em> và <em>economical</em>:</strong> <em>economic</em> là thuộc về kinh tế (<em>economic growth</em>), <em>economical</em> là tiết kiệm (<em>an economical car</em>).</li>
<li><strong>Nói quá trang trọng trong giao tiếp thường ngày:</strong> dùng <em>I would like to inquire whether…</em> với bạn bè nghe kỳ cục. C1 là biết chọn đúng giọng văn cho đúng hoàn cảnh.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Chọn câu đúng: (a) Rarely I have seen such a beautiful sunset. (b) Rarely have I seen such a beautiful sunset. (c) Rarely have seen I such a beautiful sunset.</summary><p>Đáp án: <strong>(b)</strong>. Khi trạng từ phủ định đứng đầu câu (<em>rarely, never, hardly</em>), câu phải đảo ngữ: trợ động từ đứng trước chủ ngữ.</p></details>
<details><summary><strong>Câu 2.</strong> Chọn câu đúng: (a) If I had known about the traffic, I would leave earlier. (b) If I had known about the traffic, I would have left earlier. (c) If I knew about the traffic, I would have left earlier.</summary><p>Đáp án: <strong>(b)</strong>. Câu điều kiện loại 3 (cả điều kiện và kết quả đều trong quá khứ): <em>If + had + V3, would have + V3</em>.</p></details>
<details><summary><strong>Câu 3.</strong> Chọn cách diễn đạt thận trọng (hedging) phù hợp cho bài luận: (a) This proves that the policy failed. (b) This suggests that the policy may have failed. (c) The policy failed, everyone knows it.</summary><p>Đáp án: <strong>(b)</strong>. Văn viết học thuật tránh khẳng định tuyệt đối khi bằng chứng chưa đủ mạnh; <em>suggests / may have</em> là cách diễn đạt thận trọng chuẩn.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Chưa vững B2? Quay lại <a href="/trinh-do/b2.html">trình độ B2</a>. Đã vững C1? Lên <a href="/trinh-do/c2.html">trình độ C2</a>. C1 là mức cần cho <a href="/du-hoc.html">du học</a> bậc sau đại học và nhiều công việc quốc tế — xem <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> (mục tiêu band 7.0–7.5), <a href="/luyen-thi/toefl.html">luyện thi TOEFL iBT</a> và <a href="/luyen-thi/pte.html">luyện thi PTE Academic</a>. Muốn luyện đọc sách tiếng Anh thật? Xem <a href="/tro-choi/open-shelf.html">Open Shelf — đọc sách tiếng Anh miễn phí</a>.</p>
""",
"c2": """
<p class="lead">C2 là trình độ thành thạo — gần như người bản xứ: bạn hiểu mọi thứ mình đọc và nghe được, diễn đạt tinh tế, viết văn bản phức tạp và chuyển giọng văn linh hoạt theo từng hoàn cảnh.</p>
""" + AI_NOTE + """
<h2>C2 nghĩa là gì?</h2>
<p>Theo CEFR, C2 còn gọi là "Mastery" — thành thạo. Người ở trình độ C2 có thể hiểu dễ dàng mọi thứ nghe hoặc đọc được; tóm tắt thông tin từ nhiều nguồn nói và viết khác nhau, tái cấu trúc lập luận và trình bày lại một cách mạch lạc; và diễn đạt một cách tự nhiên, trôi chảy, chính xác, phân biệt được những sắc thái ý nghĩa tinh tế ngay cả trong tình huống phức tạp.</p>
<p>Nói thật: rất ít người học tiếng Anh — kể cả người dạy tiếng Anh — đạt C2 toàn diện, và đa số không cần tới C2. C1 đã đủ cho học thuật và công việc quốc tế. C2 là mục tiêu cho người muốn dạy tiếng Anh ở trình độ cao, dịch thuật, làm việc hoàn toàn bằng tiếng Anh trong môi trường học thuật, hoặc đơn giản là yêu ngôn ngữ và muốn chạm tới đỉnh của nó. Trang này giúp bạn hiểu C2 là gì và duy trì, nâng cao trình độ nếu bạn đã ở gần đó.</p>
<h2>Bạn cần học gì ở C2?</h2>
<p>Ở C2, bạn không học "thêm ngữ pháp" nữa — bạn học <strong>sự chính xác và phong cách</strong>:</p>
<ul>
<li><strong>Phân biệt từ gần nghĩa theo sắc thái:</strong> <em>slim, slender, thin, skinny</em> đều chỉ "gầy" nhưng sắc thái khác nhau hoàn toàn — <em>slim</em> là khen, <em>skinny</em> gần như chê. <em>Stubborn</em> (bướng bỉnh, tiêu cực) khác <em>determined</em> (kiên quyết, tích cực) dù cùng chỉ "không bỏ cuộc".</li>
<li><strong>Thành ngữ, tục ngữ và cách nói cố định:</strong> <em>to beat around the bush, to cut corners, the tip of the iceberg, to be in the same boat</em> — và quan trọng hơn, biết khi nào dùng (văn nói thân mật) và khi nào không (luận văn học thuật).</li>
<li><strong>Ngôn ngữ hàm ý và châm biếm:</strong> hiểu khi người ta nói <em>"Oh, great — another meeting"</em> mà ý là chán ngán, không phải vui mừng. Hiểu hài hước đòi hỏi hiểu cả văn hóa, không chỉ từ vựng.</li>
<li><strong>Phong cách viết (style):</strong> viết được nhiều thể loại — luận văn, truyện ngắn, bài phê bình, email ngoại giao — mỗi thể loại một giọng văn riêng. Biết dùng câu ngắn để tạo nhịp, câu dài để xây lập luận, và biết khi nào phá vỡ quy tắc một cách có chủ ý.</li>
<li><strong>Từ vựng chuyên ngành sâu:</strong> trong ngành của bạn, bạn dùng được thuật ngữ chính xác như người trong nghề, kể cả từ viết tắt và cách nói riêng của ngành.</li>
<li><strong>Phát âm gần như bản xứ:</strong> không nhất thiết phải "giống người Anh" — mà là phát âm rõ ràng, trọng âm và ngữ điệu tự nhiên tới mức người nghe không phải cố gắng để hiểu bạn.</li>
</ul>
<h2>Checklist: bạn đã ở gần C2 chưa?</h2>
<ul>
<li>☐ Đọc tiểu thuyết tiếng Anh (không phải sách luyện thi) và hiểu được cả chơi chữ, châm biếm và hàm ý văn hóa.</li>
<li>☐ Xem phim không phụ đề, kể cả phim có nhiều tiếng lóng và giọng địa phương.</li>
<li>☐ Viết bài luận mà giáo viên hoặc đồng nghiệp bản xứ đọc xong không nhận ra người viết không phải bản xứ.</li>
<li>☐ Tranh luận về chủ đề trừu tượng (triết học, chính trị, nghệ thuật) và diễn đạt được quan điểm tinh tế, có sắc thái.</li>
<li>☐ Dịch một đoạn văn tiếng Việt sang tiếng Anh mà vẫn giữ được giọng văn và hàm ý của bản gốc.</li>
<li>☐ Hiểu và dùng được ít nhất 100 thành ngữ thông dụng trong đúng ngữ cảnh.</li>
<li>☐ Nghe được sự khác biệt giữa giọng Anh-Anh, Anh-Mỹ, Anh-Úc và hiểu được cả ba.</li>
<li>☐ Nhận ra lỗi sai trong bài viết của người khác và giải thích được vì sao sai.</li>
<li>☐ Nói chuyện về bất cứ chủ đề gì trong 10 phút mà không bí từ.</li>
</ul>
<h2>Lộ trình duy trì và nâng cao trình độ C2</h2>
<p>Ở C2, mục tiêu không còn là "học thêm" mà là <strong>không để mất trình độ</strong> và mài giũa sự tinh tế:</p>
<ul>
<li><strong>Đọc mỗi ngày, đọc thứ khó:</strong> tiểu thuyết, bài nghiên cứu, báo chất lượng cao (The Economist, The Guardian, Nature). Mỗi tuần ghi lại 10 từ hoặc cụm từ mới theo sắc thái, không phải theo nghĩa đơn thuần.</li>
<li><strong>Viết có người đọc thật:</strong> viết blog, viết bài cho tạp chí, dịch tài liệu — viết cho người đọc thật buộc bạn phải chính xác hơn viết bài tập.</li>
<li><strong>Nói với người bản xứ thường xuyên:</strong> tham gia câu lạc bộ, hội thảo, nhóm thảo luận bằng tiếng Anh. Nếu không có môi trường, hãy <a href="/tro-chuyen-ai.html">trò chuyện với AI</a> về chủ đề khó và yêu cầu AI phản biện lại ý kiến của bạn.</li>
<li><strong>Học qua dạy:</strong> giải thích ngữ pháp hoặc sửa bài cho người khác là cách nhanh nhất để phát hiện lỗ hổng của chính mình.</li>
<li><strong>Chấp nhận rằng C2 không có "xong":</strong> ngay cả người bản xứ cũng học từ mới mỗi ngày. Mục tiêu là tiến bộ đều, không phải hoàn hảo.</li>
</ul>
<p>Muốn kiểm tra trình độ hiện tại? Chơi <a href="/tro-choi/english-level-check.html">English Level Check — kiểm tra trình độ của bạn</a>. Muốn đọc sách tiếng Anh thật? Xem <a href="/tro-choi/open-shelf.html">Open Shelf — đọc sách tiếng Anh miễn phí</a>.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Dùng từ "sang" nhưng sai ngữ cảnh:</strong> <em>utilize</em> không hay hơn <em>use</em> — người bản xứ dùng <em>use</em> trong hầu hết trường hợp. Dùng từ dài một cách không cần thiết là dấu hiệu của người học, không phải người giỏi.</li>
<li><strong>Dịch sát văn phong Việt:</strong> câu văn Việt hay dùng nhiều từ nối và lặp ý; câu văn Anh hay chuộng ngắn gọn, trực tiếp. Viết tiếng Anh hay nghĩa là viết theo tư duy Anh, không phải dịch tư duy Việt.</li>
<li><strong>Nhầm <em>imply</em> và <em>infer</em>:</strong> người nói <em>implies</em> (hàm ý), người nghe <em>infers</em> (suy ra). <em>Are you implying that I lied?</em> — không nói <em>inferring</em>.</li>
<li><strong>Dùng thành ngữ sai ngữ cảnh:</strong> <em>It's raining cats and dogs</em> là thành ngữ đúng nhưng người bản xứ hiện đại hiếm khi dùng; dùng nó trong bài luận học thuật thì sai hoàn toàn. Thành ngữ có "tuổi thọ" và "nơi chốn" riêng.</li>
<li><strong>Quá tự tin vào "cảm giác ngôn ngữ":</strong> ở C2, cảm giác đúng 90% nhưng 10% còn lại vẫn cần tra cứu. Người giỏi là người biết tra từ điển, không phải người không bao giờ tra.</li>
<li><strong>Nhầm <em>historic</em> và <em>historical</em>:</strong> <em>historic</em> là có tầm quan trọng lịch sử (<em>a historic day</em>), <em>historical</em> là thuộc về lịch sử (<em>historical records</em>).</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Chọn từ phù hợp: "Her ___ refusal to admit she was wrong cost her the job." (a) stubborn (b) determined (c) strong</summary><p>Đáp án: <strong>(a) stubborn</strong>. Cả ba từ đều gần nghĩa "kiên quyết", nhưng <em>stubborn</em> mang sắc thái tiêu cực — phù hợp với hậu quả "mất việc". <em>Determined</em> mang sắc thái tích cực.</p></details>
<details><summary><strong>Câu 2.</strong> Người nói hàm ý gì? "Oh, wonderful. Another Monday morning meeting." (a) Họ rất thích họp sáng thứ Hai. (b) Họ đang châm biếm — thực ra họ chán họp. (c) Họ khen buổi họp được tổ chức tốt.</summary><p>Đáp án: <strong>(b)</strong>. Đây là châm biếm (irony): từ tích cực (<em>wonderful</em>) dùng với ngữ điệu và ngữ cảnh ngược lại để diễn tả sự chán ngán.</p></details>
<details><summary><strong>Câu 3.</strong> Chọn câu viết tốt nhất cho bài luận học thuật: (a) This essay will talk about pollution. (b) This essay examines the causes and consequences of air pollution in urban areas. (c) In this essay, I want to tell you about pollution, which is a very big problem nowadays.</summary><p>Đáp án: <strong>(b)</strong>. Câu (b) chính xác, cụ thể và dùng động từ học thuật (<em>examines</em>). Câu (a) quá chung chung, câu (c) quá thân mật cho văn viết học thuật.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Chưa vững C1? Quay lại <a href="/trinh-do/c1.html">trình độ C1</a>. Đã ở C2? Hãy dùng tiếng Anh vào việc thật: <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> mục tiêu band 8.0+, <a href="/du-hoc.html">chuẩn bị du học</a>, hoặc <a href="/cong-viec.html">tiếng Anh công việc</a> ở cấp độ chuyên nghiệp. Và nhớ: ở C2, cách học tốt nhất là dạy lại cho người khác — hãy <a href="/tro-chuyen-ai.html">hỏi AI</a> những câu hỏi khó nhất bạn từng gặp, rồi tự trả lời chúng bằng lời của mình.</p>
""",
}

for i, (slug, name, desc) in enumerate(LEVELS):
    prev = (LEVELS[i - 1][0].upper(), f"/trinh-do/{LEVELS[i - 1][0]}.html") if i > 0 else None
    next_ = (LEVELS[i + 1][0].upper(), f"/trinh-do/{LEVELS[i + 1][0]}.html") if i < len(LEVELS) - 1 else None
    if slug in ("a1", "a2"):
        # Đã có nội dung thật: hub bài học + PDF, không còn là stub.
        # Ngày cập nhật = ngày mới nhất của các JSON bài học trong cấp độ.
        add(f"/trinh-do/{slug}.html", name, name,
            level_hub_body(slug, name, desc),
            active="/trinh-do/", eyebrow="Theo trình độ", desc=desc,
            updated=_newest_date([_d["_src"] for _d in LESSONS_BY_LEVEL[slug]]))
        continue
    _body = guide_sections(LEVEL_BODIES[slug])
    if slug == "b1":
        # B1 đã có bài học thật: đặt danh sách bài lên đầu trang hướng dẫn.
        _body = b1_hub_lessons_html() + _body
    if slug == "b2":
        # B2 đã có bài học thật: đặt danh sách bài lên đầu trang hướng dẫn.
        _body = b2_hub_lessons_html() + _body
    add(f"/trinh-do/{slug}.html", name, name,
        _body + _eta_html(f"/trinh-do/{slug}.html") + _guide_nav(
            prev, next_, ("Tất cả trình độ", "/trinh-do/"),
            f"Cho tôi lộ trình học tiếng Anh trình độ {slug.upper()}."),
        active="/trinh-do/", eyebrow="Theo trình độ", desc=desc,
        updated=_newest_date([_d["_src"] for _d in LESSONS_BY_LEVEL[slug]])
        if slug in ("b1", "b2") else None)

# ---------------- Theo kỹ năng ----------------
SKILLS = [
    ("nghe", "Nghe", "Luyện nghe hiểu: nghe hội thoại, tin tức, bài giảng — từ chậm tới tốc độ thật, có phụ đề và giải thích."),
    ("noi", "Nói", "Luyện nói: phát âm, ngữ điệu, mẫu câu giao tiếp, luyện nói theo chủ đề, mẹo trả lời phỏng vấn."),
    ("doc", "Đọc", "Luyện đọc hiểu: đọc truyện ngắn, báo, tài liệu — kèm từ vựng và câu hỏi kiểm tra."),
    ("viet", "Viết", "Luyện viết: viết câu, đoạn văn, email, luận — có AI chữa bài và gợi ý cách viết hay hơn."),
]
SKILL_ICONS = {"nghe": "listen", "noi": "mic", "doc": "book", "viet": "write"}
add("/ky-nang/index.html", "Theo kỹ năng", "Luyện từng kỹ năng",
    """
<p class="lead">Bốn kỹ năng nghe — nói — đọc — viết, luyện riêng từng kỹ năng với bài tập và giải thích bằng tiếng Việt.</p>
<section class="section">
<div class="cards">
""" + "".join(
        f'<article class="card card-skill">{card_icon(SKILL_ICONS[slug])}<h2><a href="/ky-nang/{slug}.html">{name}</a></h2><p>{desc}</p></article>'
        for slug, name, desc in SKILLS
    ) + """
</div>
</section>
<p>Muốn AI chữa bài viết? <a href="/cong-cu/viet.html">Dùng công cụ chữa bài viết →</a></p>
""", active="/ky-nang/", eyebrow="Theo kỹ năng", desc="Luyện từng kỹ năng nghe, nói, đọc, viết tiếng Anh với bài tập và giải thích bằng tiếng Việt.")

SKILL_BODIES = {
"nghe": """
<p class="lead">Nghe là kỹ năng khó nhất với đa số người Việt — không phải vì tai bạn kém, mà vì bạn chưa được luyện nghe đúng cách. Trang này dạy bạn nghe theo 3 bước: đoán trước, nghe ý chính, rồi mới nghe chi tiết.</p>
""" + AI_NOTE + """
<h2>Vì sao bạn nghe không hiểu?</h2>
<p>Có 3 lý do phổ biến. Thứ nhất, <strong>bạn cố dịch từng từ</strong>: nghe tới từ nào thì dịch từ đó trong đầu, nên khi dịch xong từ thứ nhất thì người ta đã nói tới câu thứ ba. Thứ hai, <strong>bạn học từ qua mắt, không qua tai</strong>: bạn biết mặt chữ <em>comfortable</em> nhưng chưa bao giờ nghe nó đọc là /ˈkʌmftəbəl/ (3 âm tiết, không phải 4), nên khi nghe thấy thì không nhận ra. Thứ ba, <strong>bạn nghe quá ít</strong>: nghe là kỹ năng của thói quen — tai cần hàng trăm giờ tiếp xúc mới quen với tốc độ và cách nối âm của người bản xứ.</p>
<p>Tin tốt: cả 3 lý do đều sửa được. Nghe giỏi không cần năng khiếu — cần phương pháp và thời gian nghe đều đặn mỗi ngày.</p>
<h2>Kỹ thuật nghe 3 bước</h2>
<p><strong>Bước 1 — Đoán trước (30 giây).</strong> Trước khi bấm play, đọc câu hỏi hoặc tiêu đề và tự hỏi: đoạn này sẽ nói về cái gì? Ai nói với ai? Bạn sẽ nghe thấy những từ nào? Đoán trước giúp não "mở sẵn" từ vựng cần thiết, nên khi nghe thấy từ đó bạn nhận ra ngay.</p>
<p><strong>Bước 2 — Nghe ý chính (lần 1).</strong> Nghe một lượt không dừng, không tra từ điển. Chỉ cần trả lời: đoạn này nói về cái gì? Thái độ của người nói là gì (vui, buồn, phàn nàn, thuyết phục)? Đừng lo nếu bạn chỉ hiểu 50% — mục tiêu của lần 1 là khung xương, không phải từng từ.</p>
<p><strong>Bước 3 — Nghe chi tiết (lần 2–3).</strong> Nghe lại và ghi chép: số liệu, tên riêng, lý do, trình tự sự việc. Nghe lần 3 vừa nghe vừa đọc transcript (nếu có) để bắt những chỗ mình nghe sót — đặc biệt là từ nối âm và từ rút gọn.</p>
<p><strong>Kỹ thuật bổ sung — nghe chép chính tả (dictation):</strong> nghe một câu, dừng lại, viết ra đúng từng từ, rồi đối chiếu với transcript. Mỗi ngày 5 câu, sau 1 tháng khả năng bắt âm của bạn thay đổi rõ rệt. <strong>Kỹ thuật shadowing (nghe và nói theo):</strong> nghe một câu rồi lặp lại ngay với cùng ngữ điệu, không cần hiểu hết — cách này luyện cả tai lẫn miệng.</p>
<h2>Ví dụ luyện nghe</h2>
<p>Hãy đọc đoạn hội thoại dưới đây như một "bản transcript" — đây là ví dụ tự biên soạn để bạn tập kỹ thuật đoán trước và nghe ý chính (không phải đề thi thật):</p>
<p><em>Anna: Hi, Tom! Did you enjoy the trip to Da Lat?<br>
Tom: It was amazing! The weather was cool, and the flowers were beautiful.<br>
Anna: Did you visit the night market?<br>
Tom: Yes, we did. We tried a lot of street food, but the grilled corn was the best.<br>
Anna: How long did you stay there?<br>
Tom: Three days. I wish we could have stayed longer, but I had to come back for work.</em></p>
<p><strong>Câu hỏi luyện tập:</strong> (1) Tom đi đâu? (2) Anh ấy thích món ăn nào nhất? (3) Vì sao anh ấy không ở lại lâu hơn? — Đáp án: (1) Đà Lạt. (2) Bắp nướng (grilled corn). (3) Vì phải về đi làm.</p>
<p><strong>Điểm cần chú ý:</strong> <em>I wish we could have stayed longer</em> — đây là câu ước về quá khứ (wish + could have + V3), nghĩa là "ước gì đã ở lại lâu hơn (nhưng thực tế không ở lại)". Nhiều người nghe nhầm thành "đã ở lại lâu". Khi nghe, hãy chú ý các cấu trúc <em>wish</em> và <em>would have</em> — chúng luôn diễn tả điều trái với thực tế.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Dịch từng từ trong đầu:</strong> nghe là nghe ý, không phải dịch. Khi bạn nghe thấy <em>How are you doing?</em>, đừng dịch "Bạn đang làm thế nào?" — hãy hiểu ngay đó là lời chào. Luyện phản xạ: nghe câu quen thuộc thì hiểu ngay, không dịch.</li>
<li><strong>Nghe không ra từ nối âm:</strong> người bản xứ nói <em>What do you want to do?</em> nghe như <em>"Whaddaya wanna do?"</em> — các từ nối vào nhau. Học các dạng nối âm thông dụng: <em>want to → wanna, going to → gonna, got to → gotta, did you → didja</em>. Biết trước các dạng này thì nghe ra ngay.</li>
<li><strong>Nhầm từ đồng âm:</strong> <em>their / there / they're</em> nghe giống nhau — phải dựa vào ngữ cảnh. Nghe câu hoàn chỉnh, đừng nghe từng từ rời rạc.</li>
<li><strong>Bỏ cuộc khi không hiểu một từ:</strong> không hiểu 1 từ trong 20 từ vẫn hiểu được 95% câu. Người nghe giỏi là người bỏ qua từ lạ và bám theo ý chính, không phải người hiểu 100% từ.</li>
<li><strong>Chỉ nghe giọng Mỹ:</strong> thi IELTS và đời thực có cả giọng Anh, Úc, Canada. Hãy nghe nhiều giọng: BBC (Anh), VOA (Mỹ), ABC Australia — mỗi tuần đổi một nguồn.</li>
<li><strong>Nghe mà không ghi chép:</strong> với bài nghe dài (bài giảng, podcast), không ghi chép thì nghe xong quên ngay. Ghi từ khóa, không ghi câu đầy đủ.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Nghe câu: "I could have helped you if you had told me." — Người nói có giúp không? (a) Có, đã giúp. (b) Không, vì không được báo trước. (c) Sẽ giúp sau.</summary><p>Đáp án: <strong>(b)</strong>. Đây là câu điều kiện loại 3: điều kiện trong quá khứ không xảy ra (bạn đã không nói cho tôi biết), nên kết quả cũng không xảy ra (tôi đã không giúp).</p></details>
<details><summary><strong>Câu 2.</strong> Từ nào được nhấn mạnh trong câu "I didn't say you stole the money"? (Giả sử nhấn vào <em>I</em>.) (a) Người khác nói, không phải tôi. (b) Tôi không nói gì cả. (c) Tiền không bị lấy trộm.</summary><p>Đáp án: <strong>(a)</strong>. Trọng âm câu thay đổi nghĩa: nhấn vào <em>I</em> nghĩa là "người khác nói, không phải tôi"; nhấn vào <em>stole</em> nghĩa là "tôi không nói là bạn lấy trộm (có thể là mượn)". Nghe trọng âm là nghe ý.</p></details>
<details><summary><strong>Câu 3.</strong> "Gonna" là dạng rút gọn của cụm nào? (a) going to (b) got to (c) going on</summary><p>Đáp án: <strong>(a) going to</strong>. <em>I'm gonna call you tonight</em> = <em>I'm going to call you tonight</em>.</p></details>
<h2>Kế hoạch luyện nghe 30 ngày</h2>
<ul>
<li><strong>Ngày 1–10:</strong> Mỗi ngày 15 phút: nghe một đoạn ngắn (2–3 phút) theo 3 bước trên. Nguồn: BBC Learning English, VOA Learning English (đọc chậm, rõ ràng).</li>
<li><strong>Ngày 11–20:</strong> Tăng lên 20 phút/ngày, thêm nghe chép chính tả 5 câu/ngày. Bắt đầu nghe podcast tốc độ tự nhiên.</li>
<li><strong>Ngày 21–30:</strong> 30 phút/ngày: nghe phim không phụ đề 10 phút + podcast 20 phút. Thử <a href="/tro-choi/toeic-arcade.html">luyện nghe TOEIC qua trò chơi TOEIC Arcade</a> hoặc <a href="/tro-choi/pte-arcade.html">chơi thử PTE Arcade</a> để luyện nghe trong áp lực thời gian.</li>
</ul>
<h2>Học tiếp ở đâu?</h2>
<p>Muốn luyện nghe theo kỳ thi? Xem <a href="/luyen-thi/toeic.html">luyện thi TOEIC</a> (phần Listening chiếm một nửa bài thi), <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> (Listening 40 câu, nghe một lần duy nhất) và <a href="/luyen-thi/pte.html">luyện thi PTE Academic</a> (nghe và viết lại câu — Write From Dictation). Muốn luyện nói song song với nghe? Xem <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a> — kỹ thuật shadowing luyện cả hai kỹ năng cùng lúc.</p>
""",
"noi": """
<p class="lead">Nói là kỹ năng khiến người học sợ nhất — không phải vì bạn không biết từ, mà vì bạn sợ sai. Sự thật: người bản xứ không đánh giá bạn qua lỗi sai, họ đánh giá qua việc bạn có truyền đạt được ý mình không. Trang này dạy bạn nói trôi chảy trước, chính xác sau.</p>
""" + AI_NOTE + """
<h2>Vì sao bạn nói không trôi chảy?</h2>
<p>Có 3 nguyên nhân chính. Thứ nhất, <strong>bạn dịch từ tiếng Việt sang tiếng Anh trong đầu rồi mới nói</strong> — quá trình này chậm và cho ra câu tiếng Anh mang cấu trúc Việt. Thứ hai, <strong>bạn cố nói hoàn hảo</strong>: dừng lại sửa từng lỗi nhỏ, nên câu nói đứt quãng. Thứ ba, <strong>bạn thiếu "cụm từ sẵn"</strong> (chunks): người bản xứ không ghép từng từ mà dùng cụm có sẵn — <em>to be honest, as far as I know, let me think about it</em>. Khi bạn có sẵn 50–100 cụm như vậy, bạn nói nhanh hơn hẳn vì không phải "xây" từng câu từ đầu.</p>
<h2>Kỹ thuật luyện nói</h2>
<p><strong>1. Nói theo cụm, không nói theo từ.</strong> Học và dùng các cụm mở đầu: <em>In my opinion…</em> (ý kiến), <em>First of all… / On top of that…</em> (liệt kê), <em>To be honest…</em> (thú nhận), <em>What I mean is…</em> (giải thích lại), <em>Let me put it this way…</em> (diễn đạt lại). Mỗi cụm là một "viên gạch" — có sẵn gạch thì xây câu nhanh.</p>
<p><strong>2. Kỹ thuật 4-3-2.</strong> Chọn một chủ đề, nói về nó trong 4 phút. Nói lại chủ đề đó trong 3 phút. Nói lại lần nữa trong 2 phút. Mỗi lần rút ngắn, bạn buộc phải nói gọn và trôi chảy hơn — đây là kỹ thuật luyện trôi chảy nổi tiếng, chỉ cần một chủ đề và một chiếc đồng hồ.</p>
<p><strong>3. Ghi âm và nghe lại.</strong> Nói 1–2 phút về một chủ đề, ghi âm lại, nghe lại và tự chấm: chỗ nào ngập ngừng? Chỗ nào sai thì? Chỗ nào phát âm chưa rõ? Sửa một lỗi mỗi lần, không sửa tất cả cùng lúc.</p>
<p><strong>4. Shadowing.</strong> Nghe một câu tiếng Anh rồi lặp lại ngay với cùng ngữ điệu và tốc độ. Bắt đầu với câu ngắn, tốc độ chậm; tăng dần. Shadowing luyện cả phát âm, ngữ điệu và phản xạ cùng lúc — xem thêm ở <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>.</p>
<p><strong>5. Phát âm: trọng âm quan trọng hơn từng âm.</strong> Người Việt thường phát âm từng âm khá tốt nhưng sai trọng âm từ và trọng âm câu. Nhớ: <em>PHOtograph</em> nhưng <em>phoTOgraphy</em>; trong câu, từ mang thông tin chính được nhấn mạnh (<em>I bought a RED car</em> — nhấn RED vì màu xe là thông tin mới). Nói đúng trọng âm thì người nghe hiểu bạn ngay cả khi vài âm chưa chuẩn.</p>
<h2>Ví dụ: trả lời câu hỏi giới thiệu bản thân</h2>
<p>Câu hỏi: <em>"Tell me about yourself."</em> — câu hỏi mở đầu của hầu hết buổi phỏng vấn và phần thi nói. Đừng trả lời bằng danh sách (<em>I am 25. I live in Hanoi. I like music.</em>). Hãy trả lời bằng một câu chuyện ngắn có cấu trúc: hiện tại → quá khứ → tương lai.</p>
<p><em>"I'm Linh, and I currently work as a nurse at a hospital in Hanoi. I became a nurse because I have always wanted to help people — my grandmother was ill when I was young, and the nurses who cared for her inspired me. In the next few years, I hope to improve my English so I can work with international patients and maybe study abroad."</em></p>
<p><strong>Vì sao câu trả lời này tốt?</strong> Có cấu trúc rõ ràng (hiện tại → lý do quá khứ → kế hoạch tương lai), có chi tiết cụ thể (bà ngoại, bệnh viện), và có cảm xúc thật. Giám khảo nhớ câu chuyện, không nhớ danh sách.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Dịch "tôi tên là…" thành <em>My name is…</em> thì đúng, nhưng nhiều người nói <em>I am name…</em> — sai.</strong> <em>Name</em> là danh từ: <em>My name is Linh</em> hoặc <em>I'm Linh</em>.</li>
<li><strong>Nhầm <em>fun</em> và <em>funny</em> khi nói:</strong> <em>The trip was fun</em> (chuyến đi vui), không phải <em>funny</em> (buồn cười) — trừ khi chuyến đi làm bạn cười.</li>
<li><strong>Nói "I am agree" — sai.</strong> <em>Agree</em> là động từ: <em>I agree with you.</em></li>
<li><strong>Phát âm âm cuối:</strong> người Việt hay bỏ âm cuối (<em>like</em> đọc thành <em>lai</em> thiếu /k/). Âm cuối phân biệt nghĩa: <em>rice / rise, back / bag, work / word</em>. Luyện đọc to âm cuối của mỗi từ.</li>
<li><strong>Nói quá nhanh khi hồi hộp:</strong> khi lo lắng, ai cũng nói nhanh hơn. Mẹo: hít một hơi trước khi trả lời, nói câu đầu tiên thật chậm — nhịp sẽ ổn định lại.</li>
<li><strong>Dùng "ừm" tiếng Việt khi ngập ngừng:</strong> thay bằng <em>well… / let me think… / that's a good question…</em> — những cụm này cho bạn 2–3 giây suy nghĩ mà vẫn nghe tự nhiên.</li>
<li><strong>Chỉ trả lời "Yes/No" rồi im lặng:</strong> trong thi nói, câu trả lời 1 từ gần như không được điểm. Luôn thêm lý do hoặc ví dụ: <em>Yes, I do. I like it because…</em></li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Câu nào tự nhiên nhất khi bạn cần thời gian suy nghĩ? (a) Ummm… (im lặng 10 giây) (b) Well, let me think about it for a moment. (c) I don't know.</summary><p>Đáp án: <strong>(b)</strong>. Cụm <em>let me think</em> cho bạn thời gian mà vẫn giữ cuộc trò chuyện chạy tiếp. Im lặng dài khiến người nghe lúng túng; <em>I don't know</em> thì đóng cuộc trò chuyện lại.</p></details>
<details><summary><strong>Câu 2.</strong> Chọn cách nói đúng trọng âm từ: "photography" nhấn âm nào? (a) PHO-to-gra-phy (b) pho-TO-gra-phy (c) pho-to-GRA-phy</summary><p>Đáp án: <strong>(b) pho-TO-gra-phy</strong>. Khi thêm hậu tố <em>-y</em>, trọng âm chuyển về âm tiết trước nó. So sánh: <em>PHO-to-graph</em> nhưng <em>pho-TO-gra-phy</em>.</p></details>
<details><summary><strong>Câu 3.</strong> Sửa câu sau: "I am very like football."</summary><p>Đáp án: <em>I like football very much.</em> — <em>very</em> không bổ nghĩa cho động từ; dùng <em>very much</em> hoặc <em>a lot</em> sau động từ.</p></details>
<h2>Kế hoạch luyện nói 30 ngày</h2>
<ul>
<li><strong>Ngày 1–10:</strong> Mỗi ngày nói 5 phút: tự giới thiệu, kể về ngày hôm nay, mô tả một bức ảnh. Ghi âm lại và nghe lại.</li>
<li><strong>Ngày 11–20:</strong> Thêm kỹ thuật 4-3-2 (2 chủ đề/tuần) và shadowing 10 phút/ngày. Học 5 cụm từ mới mỗi ngày và dùng chúng trong câu nói của mình.</li>
<li><strong>Ngày 21–30:</strong> Luyện nói theo chủ đề thi: trả lời câu hỏi IELTS Speaking Part 1–2, hoặc tập thuyết trình 3–5 phút. Thử <a href="/tro-choi/speaking-booth.html">Speaking Booth — luyện nói theo chủ đề</a> và <a href="/tro-chuyen-ai.html">trò chuyện với AI</a> để luyện phản xạ trả lời.</li>
</ul>
<h2>Học tiếp ở đâu?</h2>
<p>Muốn luyện nói theo kỳ thi? Xem <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> (Speaking 3 phần, thi với giám khảo thật) và <a href="/luyen-thi/pte.html">luyện thi PTE Academic</a> (nói vào micro, máy chấm). Muốn luyện nghe song song? Xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>. Muốn luyện phát âm theo chủ đề công việc? Chơi <a href="/tro-choi/workplace-english-arcade.html">Workplace English Arcade</a>.</p>
""",

"doc": """
<p class="lead">Đọc là kỹ năng dễ luyện nhất — vì bạn kiểm soát được tốc độ của mình. Nhưng đọc giỏi không có nghĩa là hiểu từng từ; nghĩa là tìm được thông tin mình cần, nhanh hay chậm tùy mục đích. Trang này dạy bạn đọc theo mục đích: lướt, quét và đọc sâu.</p>
""" + AI_NOTE + """
<h2>3 cách đọc — dùng sai cách là mất thời gian</h2>
<p><strong>Skimming (đọc lướt lấy ý chính):</strong> đọc tiêu đề, câu đầu mỗi đoạn và câu cuối bài trong 1–2 phút để nắm bài nói về cái gì. Dùng khi bạn cần quyết định bài này có đáng đọc kỹ không, hoặc khi làm bài thi đọc cần nắm ý chính trước.</p>
<p><strong>Scanning (quét tìm thông tin):</strong> mắt chạy nhanh qua bài để tìm một thông tin cụ thể — một con số, một cái tên, một ngày tháng. Không đọc từng từ; chỉ tìm "mục tiêu". Dùng khi câu hỏi thi yêu cầu tìm chi tiết cụ thể.</p>
<p><strong>Đọc sâu (intensive reading):</strong> đọc chậm, từng câu, tra từ mới, phân tích cấu trúc — dùng khi học từ vựng từ một bài ngắn, hoặc khi bài thi yêu cầu suy luận ý kiến của tác giả.</p>
<p>Lỗi lớn nhất của người học: dùng <strong>một cách đọc cho mọi tình huống</strong> — đọc sâu cả bài báo 1.000 từ chỉ để tìm một con số, hoặc đọc lướt một bài luận rồi than không hiểu tác giả muốn nói gì. Trước khi đọc, hãy hỏi: <em>mình đọc để làm gì?</em></p>
<h2>Ví dụ luyện đọc</h2>
<p>Đọc đoạn văn tự biên soạn dưới đây (không phải đề thi thật), rồi trả lời câu hỏi — tập kỹ thuật skimming trước (đọc trong 30 giây để nắm ý chính), rồi scanning (tìm con số cụ thể):</p>
<p><em>Learning a language takes time, but the way you practise matters more than the number of hours you spend. A student who studies for 30 minutes every day will usually make faster progress than a student who studies for five hours once a week. Short, regular practice helps your brain remember new words, because each time you return to a word, the memory becomes stronger. Experts call this "spaced repetition": reviewing something just before you forget it. The best time to review a new word is one day after you first learn it, then three days later, then one week later.</em></p>
<p><strong>Câu hỏi:</strong> (1) Ý chính của đoạn văn là gì? (2) Theo đoạn văn, nên ôn từ mới lần đầu sau bao lâu? (3) "Spaced repetition" nghĩa là gì theo đoạn văn?</p>
<p><strong>Đáp án:</strong> (1) Cách luyện tập quan trọng hơn số giờ học — học ngắn và đều đặn hiệu quả hơn học dồn. (2) Một ngày sau khi học từ mới. (3) Ôn lại kiến thức ngay trước khi bạn quên nó — ôn lặp lại theo khoảng thời gian tăng dần.</p>
<p><strong>Điểm cần chú ý:</strong> câu <em>"A student who studies for 30 minutes every day will usually make faster progress than…"</em> chứa từ <em>usually</em> — tác giả không khẳng định tuyệt đối. Trong bài thi đọc, những từ như <em>usually, often, sometimes, may, might</em> rất quan trọng: chúng phân biệt câu đúng với câu "gần đúng nhưng sai". Dạng câu True/False/Not Given của IELTS đánh đúng vào chỗ này.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Tra từ điển từng từ lạ:</strong> gặp 10 từ lạ thì tra cả 10 — đọc 1 trang mất 30 phút và quên mất nội dung bài. Quy tắc: chỉ tra từ nào xuất hiện nhiều lần, hoặc từ nào làm bạn không hiểu cả câu. Từ còn lại, đoán nghĩa từ ngữ cảnh.</li>
<li><strong>Đọc bằng miệng (đọc thầm thành tiếng trong đầu):</strong> đọc từng từ thành tiếng làm tốc độ đọc của bạn bằng tốc độ nói (khoảng 150 từ/phút). Đọc bằng mắt theo cụm từ có thể đạt 250–300 từ/phút. Luyện đọc theo cụm: nhìn một cụm 3–4 từ mỗi lần dừng mắt, không nhìn từng từ.</li>
<li><strong>Đọc lại câu vừa đọc:</strong> thói quen quay lại đọc lại câu trước làm tốc độ chậm một nửa. Tin vào lần đọc đầu tiên; chỉ quay lại khi bạn thực sự không hiểu.</li>
<li><strong>Nhầm ý kiến tác giả với sự thật:</strong> <em>"Many people believe that…"</em> là ý kiến của "nhiều người", không phải quan điểm của tác giả. Trong bài thi, câu hỏi thường hỏi "tác giả nghĩ gì" — phải phân biệt ai nói câu nào.</li>
<li><strong>Bỏ qua từ nối:</strong> <em>however, therefore, for example, in contrast</em> là "biển chỉ đường" của bài đọc — chúng cho biết câu sau là đối lập, kết luận hay ví dụ của câu trước. Đọc mà bỏ qua từ nối thì mất mạch lập luận.</li>
<li><strong>Dịch từng câu sang tiếng Việt:</strong> giống như nghe, đọc cũng cần phản xạ trực tiếp bằng tiếng Anh. Dịch làm bạn chậm lại và hiểu sai những chỗ tiếng Anh diễn đạt khác tiếng Việt.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Bạn cần tìm năm thành lập của một công ty trong bài báo dài 800 từ. Nên dùng cách đọc nào? (a) Đọc sâu từng câu từ đầu tới cuối. (b) Scanning — quét tìm con số/năm. (c) Skimming — đọc lướt ý chính.</summary><p>Đáp án: <strong>(b) Scanning</strong>. Bạn tìm một thông tin cụ thể (năm) — quét nhanh để tìm số, không cần hiểu toàn bài.</p></details>
<details><summary><strong>Câu 2.</strong> Đoạn văn viết: "Some scientists argue that coffee is good for health." — Câu nào sau đây ĐÚNG? (a) Tác giả khẳng định cà phê tốt cho sức khỏe. (b) Một số nhà khoa học cho rằng cà phê tốt cho sức khỏe. (c) Cà phê chắc chắn tốt cho sức khỏe.</summary><p>Đáp án: <strong>(b)</strong>. <em>Some scientists argue that…</em> là ý kiến của một nhóm nhà khoa học, không phải khẳng định của tác giả, và <em>argue</em> nghĩa là "cho rằng", không phải "chứng minh".</p></details>
<details><summary><strong>Câu 3.</strong> Từ "it" trong câu "Spaced repetition works because it helps your brain remember" chỉ cái gì? (a) Your brain (b) Spaced repetition (c) Remember</summary><p>Đáp án: <strong>(b) Spaced repetition</strong>. Đại từ <em>it</em> chỉ danh từ chính của mệnh đề trước. Bài thi đọc hay hỏi về đại từ thay thế — luôn tìm danh từ gần nhất phù hợp về số và nghĩa.</p></details>
<h2>Kế hoạch luyện đọc 30 ngày</h2>
<ul>
<li><strong>Ngày 1–10:</strong> Mỗi ngày đọc 1 bài ngắn (200–300 từ) trên BBC Learning English hoặc VOA Learning English. Đọc lướt lấy ý chính trước, rồi đọc kỹ và ghi 5 từ mới.</li>
<li><strong>Ngày 11–20:</strong> Tăng lên bài 500 từ (BBC News). Luyện scanning: đặt 3 câu hỏi tìm chi tiết trước khi đọc, rồi tìm câu trả lời trong 3 phút.</li>
<li><strong>Ngày 21–30:</strong> Đọc truyện ngắn hoặc sách graded reader 15 phút/ngày. Thử <a href="/tro-choi/open-shelf.html">Open Shelf — đọc sách tiếng Anh miễn phí</a> để chọn sách đúng trình độ của bạn, và xem <a href="/luyen-thi/ielts.html">hướng dẫn luyện thi IELTS</a> để luyện dạng True/False/Not Given.</li>
</ul>
<h2>Học tiếp ở đâu?</h2>
<p>Muốn luyện đọc theo kỳ thi? Xem <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> (Reading 40 câu, 60 phút), <a href="/luyen-thi/toeic.html">luyện thi TOEIC</a> (Part 7 — đọc hiểu văn bản công việc) và <a href="/luyen-thi/vstep.html">luyện thi VSTEP</a> (4 bài đọc, 40 câu). Muốn đọc sách thật? Xem <a href="/tro-choi/open-shelf.html">Open Shelf</a> và <a href="/sach/global-success.html">hướng dẫn học với sách Global Success</a>.</p>
""",
"viet": """
<p class="lead">Viết là kỹ năng "lộ" trình độ thật của bạn — vì khi viết, lỗi sai nằm lại trên giấy, không trôi đi như khi nói. Nhưng viết giỏi không phải tài năng bẩm sinh; nó là một quy trình: nghĩ ý → xếp ý → viết → sửa. Trang này dạy bạn quy trình đó.</p>
""" + AI_NOTE + """
<h2>Quy trình viết 4 bước</h2>
<p><strong>Bước 1 — Nghĩ ý (5 phút).</strong> Trước khi viết một chữ nào, hãy trả lời 3 câu hỏi: Tôi viết cho ai? Tôi muốn họ làm gì hoặc nghĩ gì sau khi đọc? Tôi có những ý nào? Viết các ý ra dưới dạng gạch đầu dòng, chưa cần thành câu. Người viết dở thường bỏ qua bước này và viết tới đâu nghĩ tới đó — bài viết vì vậy lan man.</p>
<p><strong>Bước 2 — Xếp ý thành dàn bài.</strong> Một đoạn văn tốt có 1 ý chính, 2–3 ý phụ và 1 ví dụ. Một bài luận tốt có mở bài (nêu vấn đề + quan điểm), thân bài (2–3 đoạn, mỗi đoạn 1 luận điểm) và kết bài (tóm tắt + nhấn mạnh quan điểm). Dàn bài càng rõ, viết càng nhanh.</p>
<p><strong>Bước 3 — Viết bản nháp, đừng sửa khi viết.</strong> Viết liền một mạch theo dàn bài, kể cả khi bạn chưa chắc từ hay ngữ pháp. Sửa trong lúc viết làm bạn mất mạch suy nghĩ. Bản nháp được phép xấu — nhiệm vụ của nó là "có chữ trên giấy".</p>
<p><strong>Bước 4 — Sửa theo checklist.</strong> Đọc lại bài và kiểm tra theo thứ tự: (1) đủ ý chưa? (2) câu nào khó hiểu? (3) ngữ pháp: thì, "s" ngôi thứ ba, mạo từ a/the? (4) chính tả và dấu câu? Sửa theo thứ tự này — đừng sửa chính tả trước khi sửa ý.</p>
<h2>Ví dụ: viết một đoạn văn tốt</h2>
<p>Đề bài tự biên soạn: <em>"Do you think students should wear uniforms at school? Give reasons."</em> (Học sinh có nên mặc đồng phục không? Nêu lý do.)</p>
<p><strong>Bản viết yếu (chỉ liệt kê):</strong> <em>"I think students should wear uniforms. Uniforms are good. They are cheap. Students look the same. I like uniforms."</em> — Các câu ngắn, rời rạc, không có lập luận, không có ví dụ.</p>
<p><strong>Bản viết tốt (cùng ý, viết lại):</strong> <em>"I believe students should wear uniforms at school. First, uniforms reduce the pressure to follow fashion trends, so students from poorer families do not feel embarrassed about their clothes. Second, uniforms create a sense of belonging: when everyone wears the same clothes, students feel they are part of one school community. For these reasons, I think uniforms are a good idea."</em></p>
<p><strong>Vì sao bản thứ hai tốt hơn?</strong> Có từ nối dẫn dắt (<em>First, Second, For these reasons</em>), mỗi luận điểm có giải thích (<em>so students… do not feel…</em>), và có câu kết tóm tắt quan điểm. Cùng một ý tưởng — khác nhau ở cách tổ chức.</p>
<p><strong>Từ nối nên dùng:</strong> thêm ý — <em>furthermore, in addition, moreover</em>; đối lập — <em>however, on the other hand, although</em>; nguyên nhân — <em>because, as a result, therefore</em>; ví dụ — <em>for example, for instance, such as</em>; kết luận — <em>in conclusion, to sum up, overall</em>. Nhưng nhớ: dùng từ nối để phục vụ lập luận, không phải để khoe từ — xem thêm lỗi này ở <a href="/trinh-do/c1.html">trình độ C1</a>.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Quên mạo từ a/an/the:</strong> tiếng Việt không có mạo từ nên người Việt hay bỏ. <em>I am student</em> — sai. Viết đúng: <em>I am a student.</em> Quy tắc nhanh: danh từ đếm được số ít cần có mạo từ hoặc từ sở hữu/từ chỉ định đi kèm.</li>
<li><strong>Viết câu quá dài:</strong> một câu 40 từ với 3 mệnh đề phụ rất dễ sai và khó đọc. Tách thành 2 câu ngắn thường tốt hơn — giám khảo chấm ý, không chấm độ dài câu.</li>
<li><strong>Dùng "very" cho mọi thứ:</strong> <em>very good, very big, very tired</em> trong cả bài luận nghe nghèo nàn. Thay bằng từ mạnh: <em>excellent, huge, exhausted</em>.</li>
<li><strong>Viết tắt trong văn viết trang trọng:</strong> <em>don't, can't, isn't</em> không dùng trong luận văn và email trang trọng — viết đầy đủ: <em>do not, cannot, is not</em>.</li>
<li><strong>Dịch câu tiếng Việt sang tiếng Anh từng chữ:</strong> <em>"The weather today is very beautiful, I go out to play"</em> — sai dấu câu và cấu trúc. Viết đúng: <em>The weather is beautiful today, so I went out.</em> (Hai mệnh đề cần từ nối hoặc tách thành 2 câu; dấu phẩy không nối được 2 câu độc lập — lỗi "comma splice" rất phổ biến.)</li>
<li><strong>Không có câu chủ đề (topic sentence):</strong> mỗi đoạn văn cần một câu đầu nêu ý chính của đoạn. Không có câu chủ đề, người đọc không biết đoạn này nói về cái gì cho tới khi đọc hết đoạn.</li>
<li><strong>Viết xong không đọc lại:</strong> 90% lỗi chính tả và lỗi thì sẽ lộ ra khi đọc lại sau 10 phút. Luôn dành 5 phút cuối để đọc lại bài của mình.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Sửa câu sau: "I am student at Hanoi University."</summary><p>Đáp án: <em>I am <strong>a</strong> student at Hanoi University.</em> — Danh từ đếm được số ít (<em>student</em>) cần mạo từ <em>a</em>.</p></details>
<details><summary><strong>Câu 2.</strong> Sửa câu sau: "She likes coffee, she drinks it every morning."</summary><p>Đáp án: <em>She likes coffee, <strong>and</strong> she drinks it every morning.</em> (hoặc tách thành 2 câu: <em>She likes coffee. She drinks it every morning.</em>) — Dấu phẩy không nối được 2 câu độc lập (lỗi comma splice).</p></details>
<details><summary><strong>Câu 3.</strong> Chọn từ nối phù hợp: "It was raining. ___, we decided to stay at home." (a) Furthermore (b) Therefore (c) For example</summary><p>Đáp án: <strong>(b) Therefore</strong> (vì vậy) — câu sau là kết quả của câu trước. <em>Furthermore</em> dùng để thêm ý, <em>For example</em> dùng để nêu ví dụ.</p></details>
<h2>Kế hoạch luyện viết 30 ngày</h2>
<ul>
<li><strong>Ngày 1–10:</strong> Mỗi ngày viết 5 câu về một chủ đề quen thuộc (ngày hôm nay, món ăn yêu thích, bộ phim vừa xem). Tập viết đúng thì và mạo từ.</li>
<li><strong>Ngày 11–20:</strong> Viết đoạn văn 120–150 từ, 3 đoạn/tuần, theo dàn bài: câu chủ đề → 2 ý phụ → ví dụ → câu kết. Dán bài vào <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> để xem lỗi, rồi tự sửa lại bằng tay.</li>
<li><strong>Ngày 21–30:</strong> Viết email và bài luận 250 từ. Tra từ vựng bằng <a href="/cong-cu/tu-vung.html">công cụ tra từ bằng AI</a> khi cần từ chính xác hơn. Xem <a href="/luyen-thi/ielts.html">hướng dẫn luyện thi IELTS</a> (Writing Task 2) để luyện viết luận theo chuẩn thi.</li>
</ul>
<h2>Học tiếp ở đâu?</h2>
<p>Muốn luyện viết theo kỳ thi? Xem <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> (Writing Task 1 và Task 2), <a href="/luyen-thi/vstep.html">luyện thi VSTEP</a> (viết thư 120 từ và luận 250 từ) và <a href="/luyen-thi/toefl.html">luyện thi TOEFL iBT</a> (viết email và bài thảo luận). Muốn luyện đọc để lấy ý cho bài viết? Xem <a href="/ky-nang/doc.html">hướng dẫn luyện đọc</a>. Muốn tra từ và chữa bài ngay? Dùng <a href="/cong-cu/tu-vung.html">công cụ tra từ bằng AI</a> và <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a>.</p>
""",
}

for i, (slug, name, desc) in enumerate(SKILLS):
    prev = (SKILLS[i - 1][1], f"/ky-nang/{SKILLS[i - 1][0]}.html") if i > 0 else None
    next_ = (SKILLS[i + 1][1], f"/ky-nang/{SKILLS[i + 1][0]}.html") if i < len(SKILLS) - 1 else None
    add(f"/ky-nang/{slug}.html", name, f"Luyện {name.lower()}",
        guide_sections(SKILL_BODIES[slug]) + _eta_html(f"/ky-nang/{slug}.html") + _guide_nav(
            prev, next_, ("Tất cả kỹ năng", "/ky-nang/"),
            f"Làm sao để luyện {name.lower()} tiếng Anh hiệu quả?"),
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
<p class="lead">Chuẩn bị cho kỳ thi của bạn: hướng dẫn từng phần thi, bài tập tự biên soạn để luyện tập và mẹo làm bài, kèm giải thích bằng tiếng Việt.</p>
<p class="muted">Bài tập trên trang là câu hỏi tự biên soạn để luyện tập — điểm chỉ là ước lượng, không phải điểm thi thật.</p>
<section class="section">
<div class="cards">
""" + "".join(
        f'<article class="card card-exam">{card_icon("exam")}<h2><a href="/luyen-thi/{slug}.html">{name}</a></h2><p>{desc}</p></article>'
        for slug, name, desc in TESTS
    ) + """
</div>
</section>
<p>Đã có hướng dẫn học với sách cho hai kỳ thi: <a href="/sach/barrons-toeic.html">học TOEIC với sách Barron's</a> · <a href="/sach/mindset-for-ielts.html">học IELTS với sách Mindset for IELTS</a>.</p>
""", active="/luyen-thi/", eyebrow="Luyện thi", desc="Luyện thi IELTS, TOEIC, PTE, TOEFL và VSTEP: bài tập tự biên soạn, mẹo làm bài từng phần, giải thích bằng tiếng Việt.")

TEST_BODIES = {
"ielts": """
<p class="lead">IELTS là kỳ thi tiếng Anh phổ biến nhất cho du học và định cư. Bài thi có 4 kỹ năng — Nghe, Đọc, Viết, Nói — thang điểm từ 1 đến 9, không có "đậu" hay "rớt": mỗi trường hoặc cơ quan yêu cầu một mức điểm khác nhau. Trang này dạy bạn cấu trúc bài thi, chiến thuật từng phần và bài tập tự biên soạn để luyện tập.</p>
""" + AI_NOTE + """
<h2>Cấu trúc bài thi (đã đối chiếu ielts.org)</h2>
<p>IELTS có 2 dạng: <strong>Academic</strong> (cho người đi học đại học, sau đại học hoặc đăng ký hành nghề chuyên môn) và <strong>General Training</strong> (cho người định cư hoặc học nghề). Nghe và Nói giống nhau ở cả 2 dạng; Đọc và Viết thì khác nhau. Ba phần Nghe, Đọc, Viết thi liên tục trong một buổi, không nghỉ giữa các phần; phần Nói có thể thi cùng ngày hoặc khác ngày, tùy trung tâm.</p>
<div class="table-wrap"><table><thead><tr><th>Phần thi</th><th>Thời gian</th><th>Nội dung</th><th>Cách chấm</th></tr></thead><tbody>
<tr><td>Listening</td><td>Khoảng 30 phút</td><td>40 câu hỏi, 4 phần; mỗi đoạn ghi âm chỉ nghe 1 lần</td><td>Mỗi câu đúng 1 điểm; điểm thô /40 quy ra band 1–9</td></tr>
<tr><td>Reading</td><td>60 phút</td><td>40 câu hỏi, 3 bài đọc (Academic: 3 đoạn văn; General: nhiều đoạn ngắn hơn)</td><td>Mỗi câu đúng 1 điểm; điểm thô /40 quy ra band 1–9 (bảng quy đổi khác nhau giữa 2 dạng)</td></tr>
<tr><td>Writing</td><td>60 phút</td><td>2 bài: Task 1 tối thiểu 150 từ (Academic: mô tả biểu đồ; General: viết thư), Task 2 tối thiểu 250 từ (bài luận)</td><td>4 tiêu chí mỗi bài; Task 2 chiếm gấp đôi điểm so với Task 1</td></tr>
<tr><td>Speaking</td><td>11–14 phút</td><td>3 phần, phỏng vấn trực tiếp với giám khảo, có ghi âm</td><td>4 tiêu chí: trôi chảy, từ vựng, ngữ pháp, phát âm</td></tr>
</tbody></table></div>
<p>Tổng thời gian thi khoảng 2 giờ 45 phút. Điểm tổng (Overall Band) là trung bình cộng của 4 kỹ năng, làm tròn tới nửa band gần nhất. <strong>Chưa kiểm chứng được:</strong> lệ phí thi và lịch thi cụ thể tại Việt Nam thay đổi theo thời điểm và trung tâm — hãy xem trên trang của trung tâm tổ chức thi (British Council hoặc IDP) trước khi đăng ký. Trang này không ghi lệ phí hay ngày thi cụ thể vì các thông tin đó thay đổi thường xuyên.</p>
<h2>Chiến thuật từng phần</h2>
<p><strong>Listening — nghe 1 lần duy nhất.</strong> Đây là điểm khó nhất: không có lần nghe thứ hai. Trước mỗi phần, dùng thời gian chuẩn bị để đọc câu hỏi và gạch chân từ khóa (tên, số, từ mang thông tin). Khi nghe, viết đáp án ngay khi nghe thấy — đừng đợi nghe hết rồi mới viết. Chú ý bẫy: người nói thường nhắc tới đáp án sai trước rồi mới sửa lại (<em>"The meeting is on Tuesday… no, sorry, Wednesday"</em> — đáp án là Wednesday). Thi trên giấy có 10 phút chuyển đáp án sang phiếu trả lời; thi trên máy tính thì gõ đáp án trực tiếp. Luyện tập: xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>.</p>
<p><strong>Reading — 60 phút cho 40 câu, không có thời gian chuyển đáp án.</strong> Đừng đọc toàn bài từ đầu tới cuối rồi mới làm câu hỏi — làm vậy sẽ hết giờ. Đọc câu hỏi trước, gạch chân từ khóa, rồi quét (scan) bài để tìm vị trí thông tin. Dạng True/False/Not Given là dạng gây mất điểm nhiều nhất: <em>False</em> nghĩa là bài viết nói điều ngược lại; <em>Not Given</em> nghĩa là bài viết không nhắc tới — nếu bạn không tìm thấy thông tin, đáp án thường là Not Given, đừng đoán thành False. Dạng Matching Headings: đọc câu đầu và câu cuối mỗi đoạn để nắm ý chính của đoạn, đừng đọc kỹ từng câu. Luyện tập: xem <a href="/ky-nang/doc.html">hướng dẫn luyện đọc</a>.</p>
<p><strong>Writing Task 1 (Academic) — mô tả biểu đồ trong 20 phút, tối thiểu 150 từ.</strong> Cấu trúc: mở bài (diễn đạt lại đề bằng lời của mình) → tổng quan (nêu 2–3 xu hướng chính, không có số liệu) → thân bài (mô tả số liệu theo nhóm, có so sánh). Lỗi phổ biến: liệt kê số liệu mà không có tổng quan, hoặc viết ý kiến cá nhân vào Task 1 (không được phép — Task 1 chỉ mô tả, không bình luận). Task 1 General Training là viết thư: chú ý giọng văn (trang trọng hay thân mật) tùy người nhận.</p>
<p><strong>Writing Task 2 — bài luận 250 từ trong 40 phút, chiếm gấp đôi điểm.</strong> Dàn bài chuẩn: mở bài (diễn đạt lại vấn đề + nêu quan điểm) → thân bài 2 đoạn (mỗi đoạn 1 luận điểm + giải thích/ví dụ) → kết bài (tóm tắt quan điểm). Luôn trả lời đúng câu hỏi: đề hỏi "do you agree?" thì phải nêu rõ đồng ý hay không; đề hỏi "discuss both views" thì phải trình bày cả hai phía rồi mới nêu quan điểm của mình. Luyện tập: xem <a href="/ky-nang/viet.html">hướng dẫn luyện viết</a> và dùng <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a>.</p>
<p><strong>Speaking — 3 phần, 11–14 phút.</strong> Part 1 (4–5 phút): hỏi đáp về bản thân, gia đình, công việc, sở thích — trả lời 2–3 câu mỗi câu hỏi, đừng trả lời 1 từ. Part 2 (3–4 phút): nhận một chủ đề, chuẩn bị 1 phút, nói liên tục 1–2 phút — dùng 1 phút chuẩn bị để viết dàn ý (mở đầu, 2–3 ý, kết), đừng viết câu đầy đủ. Part 3 (4–5 phút): thảo luận sâu về chủ đề của Part 2 — đây là phần phân biệt band 6 và band 7: bạn cần đưa ra ý kiến trừu tượng, so sánh, dự đoán. Luyện tập: xem <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a> và chơi <a href="/tro-choi/speaking-booth.html">Speaking Booth</a>.</p>
<h2>Bài tập tự biên soạn (không phải đề thi thật)</h2>
<p><strong>Listening — dạng điền từ.</strong> Đọc đoạn hội thoại tự biên soạn dưới đây như một transcript, rồi điền từ còn thiếu (tưởng tượng bạn vừa nghe đoạn này một lần):</p>
<p><em>Receptionist: Good morning. How can I help you?<br>
Student: I'd like to book a room for two nights, please. From the 15th to the 17th of June.<br>
Receptionist: Certainly. A single room or a double room?<br>
Student: A double room, please. How much is it per night?<br>
Receptionist: It's 850,000 dong per night, including breakfast.<br>
Student: That's fine. Can I pay by card?<br>
Receptionist: Yes, of course.</em></p>
<p>Câu hỏi: (1) Khách đặt phòng mấy đêm? (2) Từ ngày nào tới ngày nào? (3) Giá phòng bao nhiêu một đêm, đã bao gồm gì? — Đáp án: (1) 2 đêm. (2) Từ 15 tới 17 tháng 6. (3) 850.000 đồng/đêm, đã bao gồm bữa sáng.</p>
<p><strong>Reading — dạng True/False/Not Given.</strong> Đọc đoạn văn tự biên soạn dưới đây:</p>
<p><em>Most people check their phones many times a day. A recent study found that the average person looks at their phone more than 90 times a day. However, the study did not say whether this habit is harmful. Some experts believe that frequent phone use can reduce concentration, while others argue that phones are useful tools for learning and communication.</em></p>
<p>Câu hỏi: (1) The average person checks their phone more than 90 times a day. (True / False / Not Given) (2) The study proved that checking phones is harmful. (True / False / Not Given) (3) All experts agree that phones reduce concentration. (True / False / Not Given) — Đáp án: (1) True — đoạn văn nói rõ con số này. (2) False — đoạn văn nói nghiên cứu <em>không</em> kết luận thói quen này có hại hay không. (3) False — đoạn văn nói <em>một số</em> chuyên gia tin vậy, trong khi số khác không đồng ý.</p>
<p><strong>Writing Task 2 — đề tự biên soạn.</strong> <em>"Some people think that children should learn a foreign language at primary school. Others think it is better to start later. Discuss both views and give your opinion."</em> — Hãy viết dàn bài (không cần viết cả bài): mở bài nêu quan điểm của bạn; đoạn 1: lý do nên học sớm (trẻ học phát âm dễ hơn, có nhiều thời gian hơn); đoạn 2: lý do nên học muộn (trẻ cần vững tiếng mẹ đẻ trước, học muộn vẫn đạt được nếu có động lực); kết bài: tóm tắt và khẳng định quan điểm của bạn. Sau đó viết bài 250 từ và nhờ <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> góp ý.</p>
<p><strong>Speaking Part 1 — câu hỏi tự biên soạn.</strong> <em>"Do you like reading books?"</em> — Câu trả lời yếu: <em>"Yes."</em> Câu trả lời tốt: <em>"Yes, I do. I usually read before bed — mostly novels, because they help me relax after a long day. At the moment I'm reading a book about Vietnamese history, and I'm really enjoying it."</em> — Trả lời 2–3 câu, có lý do và ví dụ cụ thể.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Listening: nghe thấy từ trong câu hỏi thì chọn ngay.</strong> Bài nghe cố tình nhắc tới từ khóa của đáp án sai trước. Nghe cả câu, hiểu nghĩa rồi mới chọn.</li>
<li><strong>Reading: đoán Not Given thành False.</strong> Không tìm thấy thông tin ≠ thông tin sai. Chỉ chọn False khi bài viết nói điều ngược lại rõ ràng.</li>
<li><strong>Writing Task 1: không có phần tổng quan (overview).</strong> Thiếu overview là lỗi trừ điểm nặng nhất ở Task 1. Luôn viết 2–3 câu tổng quan ngay sau mở bài, trước khi mô tả số liệu.</li>
<li><strong>Writing Task 2: viết dưới 250 từ.</strong> Bài dưới số từ tối thiểu bị trừ điểm dù viết hay. Đếm từ khi luyện tập; khi thi thật, hãy viết khoảng 270–290 từ để chắc chắn đủ.</li>
<li><strong>Writing: dùng từ nối một cách máy móc.</strong> Nhồi <em>moreover, furthermore, nevertheless</em> vào mọi đoạn khiến bài nghe giả tạo — xem lỗi này ở <a href="/trinh-do/c1.html">trình độ C1</a>.</li>
<li><strong>Speaking Part 2: nói chưa tới 1 phút rồi dừng.</strong> Nói dưới 1 phút bị trừ điểm nặng. Luyện nói đủ 2 phút bằng kỹ thuật 4-3-2 ở <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>.</li>
<li><strong>Speaking: học thuộc câu trả lời mẫu.</strong> Giám khảo nhận ra ngay câu học thuộc và có thể trừ điểm. Học dàn ý và cụm từ, không học thuộc lòng cả bài.</li>
</ul>
<h2>Kế hoạch ôn 8 tuần (mục tiêu band 6.0–6.5)</h2>
<ul>
<li><strong>Tuần 1–2:</strong> Làm quen format: đọc kỹ trang này, làm 1 đề Listening + 1 đề Reading (đề tự biên soạn hoặc sách luyện thi), chấm và ghi lại dạng câu hay sai.</li>
<li><strong>Tuần 3–4:</strong> Tập trung vào điểm yếu nhất (thường là Writing hoặc Speaking). Viết 3 bài Task 2/tuần; luyện nói Part 2 mỗi ngày 10 phút.</li>
<li><strong>Tuần 5–6:</strong> Luyện đề có bấm giờ: Listening + Reading trong 90 phút liên tục như thi thật. Chữa kỹ từng câu sai — hiểu vì sao sai quan trọng hơn làm nhiều đề.</li>
<li><strong>Tuần 7–8:</strong> Làm 2 đề thi thử đầy đủ (4 kỹ năng) trong điều kiện thi thật. Tuần cuối: ôn lại lỗi cũ, nghỉ ngơi trước ngày thi 1 ngày.</li>
</ul>
<p>Muốn chơi mà vẫn ôn IELTS? Chơi <a href="/tro-choi/band-climb.html">Band Climb — luyện IELTS qua trò chơi</a>. Học theo sách? Xem <a href="/sach/mindset-for-ielts.html">hướng dẫn học với sách Mindset for IELTS</a> (từ Foundation tới Level 3, band 7.5). Cần band 6.5 để du học? Xem <a href="/du-hoc.html">chuẩn bị tiếng Anh đi du học</a>. Chưa rõ mình ở band nào? Hãy làm bài <a href="/tro-choi/english-level-check.html">English Level Check</a> (chỉ có đọc/viết/ngữ pháp, chưa có nghe/nói) hoặc xem <a href="/trinh-do/b2.html">trình độ B2</a> và <a href="/trinh-do/c1.html">trình độ C1</a>.</p>
""",
"toeic": """
<p class="lead">TOEIC là kỳ thi tiếng Anh công việc phổ biến nhất tại Việt Nam — nhiều công ty dùng điểm TOEIC để tuyển dụng và xét thăng chức. Bài thi Listening & Reading có 200 câu trắc nghiệm, làm trong 2 giờ, thang điểm 10–990. Trang này dạy bạn cấu trúc 7 phần thi, chiến thuật từng phần và bài tập tự biên soạn để luyện tập.</p>
""" + AI_NOTE + """
<h2>Cấu trúc bài thi (đã đối chiếu ETS)</h2>
<p>Bài thi TOEIC Listening & Reading gồm 2 phần, 7 nhỏ (Part 1–7), tổng cộng 200 câu trắc nghiệm, làm trong khoảng 2 giờ. Listening 100 câu (khoảng 45 phút), Reading 100 câu (75 phút). Mỗi kỹ năng chấm riêng từ 5 tới 495 điểm; tổng điểm từ 10 tới 990. Không có điểm trừ cho câu sai — vì vậy không bao giờ bỏ trống câu nào. Ngoài ra còn có bài thi TOEIC Speaking & Writing riêng (thi trên máy tính) — trang này tập trung vào bài Listening & Reading, vì đó là bài thi phổ biến nhất tại Việt Nam.</p>
<div class="table-wrap"><table><thead><tr><th>Phần</th><th>Nội dung</th><th>Số câu</th><th>Thời gian</th></tr></thead><tbody>
<tr><td>Listening Part 1</td><td>Mô tả hình ảnh: chọn câu mô tả đúng nhất bức ảnh</td><td>6</td><td rowspan="4">Khoảng 45 phút</td></tr>
<tr><td>Listening Part 2</td><td>Hỏi – đáp: chọn câu trả lời phù hợp nhất cho câu hỏi hoặc câu nói</td><td>25</td></tr>
<tr><td>Listening Part 3</td><td>Hội thoại: 13 đoạn hội thoại, mỗi đoạn 3 câu hỏi</td><td>39</td></tr>
<tr><td>Listening Part 4</td><td>Bài nói ngắn: 10 bài nói, mỗi bài 3 câu hỏi</td><td>30</td></tr>
<tr><td>Reading Part 5</td><td>Điền câu chưa hoàn chỉnh: ngữ pháp và từ vựng</td><td>30</td><td rowspan="3">75 phút</td></tr>
<tr><td>Reading Part 6</td><td>Điền từ vào đoạn văn: email, thông báo, bài báo ngắn</td><td>16</td></tr>
<tr><td>Reading Part 7</td><td>Đọc hiểu: đoạn văn đơn và đoạn văn đôi, trả lời câu hỏi</td><td>54</td></tr>
</tbody></table></div>
<p>Điểm TOEIC không quy đổi cố định từ số câu đúng sang điểm — ETS dùng phương pháp quy đổi thống kê riêng cho từng đề thi, nên cùng số câu đúng có thể cho điểm hơi khác nhau giữa các lần thi. Vì vậy đừng tin các "bảng quy đổi" lan truyền trên mạng là chính xác tuyệt đối; hãy dùng chúng làm ước lượng. <strong>Chưa kiểm chứng được:</strong> lệ phí thi và lịch thi tại Việt Nam thay đổi theo thời điểm — hãy xem trên trang của IIG Vietnam (đơn vị tổ chức thi TOEIC tại Việt Nam) trước khi đăng ký.</p>
<h2>Chiến thuật từng phần</h2>
<p><strong>Part 1 — Mô tả hình ảnh (6 câu).</strong> Nghe 4 câu mô tả, chọn câu đúng nhất về bức ảnh. Chiến thuật: nhìn ảnh trước khi nghe (5 giây), tự mô tả ảnh bằng tiếng Anh trong đầu (ai đang làm gì? ở đâu?). Bẫy phổ biến: câu dùng đúng từ vựng trong ảnh nhưng sai hành động (<em>a man is reading a book</em> trong khi ảnh là người đàn ông đang viết). Chú ý thì: ảnh mô tả hành động đang diễn ra nên đáp án đúng thường ở thì hiện tại tiếp diễn.</p>
<p><strong>Part 2 — Hỏi đáp (25 câu).</strong> Nghe một câu hỏi hoặc câu nói, chọn câu trả lời phù hợp trong 3 lựa chọn. Đây là phần "bẫy" nhiều nhất: đáp án sai thường lặp lại từ trong câu hỏi (nghe thấy từ quen thì chọn ngay là sai). Chiến thuật: nghe từ hỏi đầu câu (Who/When/Where/Why/How) để biết loại thông tin cần tìm. Câu hỏi Yes/No không nhất thiết trả lời Yes/No — <em>"Did you finish the report?" — "I'll send it to you this afternoon."</em> là câu trả lời đúng (hàm ý: chưa xong, chiều sẽ gửi).</p>
<p><strong>Part 3 — Hội thoại (39 câu).</strong> Mỗi đoạn hội thoại 3 câu hỏi. Chiến thuật: đọc trước 3 câu hỏi trong lúc nghe hướng dẫn, gạch chân từ khóa. Nghe và ghi nhanh đáp án; đừng dừng lại suy nghĩ một câu quá lâu — sẽ lỡ câu tiếp theo. Câu hỏi thường theo thứ tự nội dung hội thoại, nên đáp án câu 1 thường ở đầu đoạn, câu 3 ở cuối đoạn.</p>
<p><strong>Part 4 — Bài nói ngắn (30 câu).</strong> Thông báo, tin nhắn thoại, bài giới thiệu. Chiến thuật giống Part 3, nhưng bài nói chỉ có 1 người nên phải tập trung hơn. Chú ý các câu hỏi dạng "người nói sẽ làm gì tiếp theo?" — đáp án thường ở cuối bài nói.</p>
<p><strong>Part 5 — Điền câu (30 câu, khoảng 30 giây/câu).</strong> Đây là phần ngữ pháp + từ vựng. Chiến thuật: đọc câu, xác định loại từ cần điền (danh từ, động từ, tính từ hay trạng từ) trước khi nhìn đáp án. Câu về từ vựng: học collocation công việc (<em>make a decision, take responsibility, meet a deadline</em>). Đừng dành quá 30 giây cho 1 câu — câu khó thì đánh dấu, làm câu dễ trước, quay lại sau nếu còn giờ.</p>
<p><strong>Part 6 — Điền từ vào đoạn văn (16 câu).</strong> 4 đoạn văn, mỗi đoạn 4 chỗ trống. Có 1 câu mỗi đoạn là chọn câu hoàn chỉnh để điền vào (dạng mới) — cần đọc cả đoạn để hiểu mạch văn, không chỉ nhìn câu trống.</p>
<p><strong>Part 7 — Đọc hiểu (54 câu).</strong> Phần dài nhất và dễ hết giờ nhất. Chiến thuật: làm đoạn văn đơn trước, đoạn văn đôi sau (vì đoạn đôi dài hơn). Đọc câu hỏi trước, quét bài tìm thông tin. Câu hỏi "từ X trong bài có nghĩa gần nhất với…" — đừng đoán nghĩa từ điển, hãy xem ngữ cảnh trong câu. Quản lý thời gian: Part 5–6 nên xong trong 25 phút, để lại 50 phút cho Part 7.</p>
<h2>Bài tập tự biên soạn (không phải đề thi thật)</h2>
<p><strong>Part 2 — Hỏi đáp.</strong> Chọn câu trả lời phù hợp nhất:</p>
<p>Câu hỏi: <em>"When will the new office open?"</em> (a) <em>Yes, it will.</em> (b) <em>Next Monday, I think.</em> (c) <em>It's on the second floor.</em> — Đáp án: <strong>(b)</strong>. Câu hỏi When cần câu trả lời về thời gian. (a) trả lời Yes/No cho câu hỏi When là sai; (c) trả lời về địa điểm, không phải thời gian.</p>
<p>Câu hỏi: <em>"Would you like me to send you the report?"</em> (a) <em>Yes, please. That would be great.</em> (b) <em>The report is on my desk.</em> (c) <em>I sent it yesterday.</em> — Đáp án: <strong>(a)</strong>. Đây là lời đề nghị giúp đỡ — câu trả lời đúng là chấp nhận hoặc từ chối một cách lịch sự.</p>
<p><strong>Part 5 — Điền câu.</strong> Chọn từ phù hợp:</p>
<p>Câu 1: <em>"The company will announce the results ___ Friday."</em> (a) in (b) on (c) at — Đáp án: <strong>(b) on</strong>. <em>On + ngày/thứ</em> (on Friday, on 15 June); <em>in + tháng/năm</em> (in June, in 2026); <em>at + giờ</em> (at 9 a.m.).</p>
<p>Câu 2: <em>"Please send the invoice to the accounting ___ as soon as possible."</em> (a) department (b) departmental (c) depart — Đáp án: <strong>(a) department</strong> (danh từ). Sau <em>the</em> + tính từ sở hữu cần danh từ; <em>departmental</em> là tính từ, <em>depart</em> là động từ.</p>
<p><strong>Part 7 — Đọc hiểu.</strong> Đọc email tự biên soạn dưới đây:</p>
<p><em>From: Hoa Nguyen (HR Department)<br>
To: All staff<br>
Subject: New working hours from next month<br>
Dear colleagues,<br>
From 1 December, our office hours will change. The office will now open at 8:30 a.m. and close at 5:30 p.m., from Monday to Friday. The lunch break will be from 12:00 to 1:00 p.m. Please note that the office will be closed on Saturday, as before. If you have any questions, please contact the HR Department.</em></p>
<p>Câu hỏi: (1) Giờ làm việc mới bắt đầu lúc mấy giờ? (2) Văn phòng có mở cửa thứ Bảy không? (3) Ai gửi email này? — Đáp án: (1) 8:30 sáng. (2) Không — văn phòng đóng cửa thứ Bảy như trước. (3) Hoa Nguyễn, phòng Nhân sự (HR Department).</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Part 1: chọn câu có từ vựng đúng nhưng hành động sai.</strong> Thấy ảnh có "book" thì chọn câu có từ <em>book</em> — nhưng người trong ảnh đang viết, không phải đang đọc. Nghe hành động, không nghe từ lẻ.</li>
<li><strong>Part 2: bị bẫy "từ lặp lại".</strong> Câu hỏi nhắc tới <em>meeting</em>, đáp án sai cũng nhắc tới <em>meeting</em> nhưng trả lời lạc đề. Nghe nghĩa, không nghe từ.</li>
<li><strong>Part 5: không xác định loại từ trước khi chọn.</strong> Nhìn 4 đáp án giống nhau về gốc từ (<em>department / departmental / depart / departure</em>) mà không xem vị trí cần điền là danh từ hay tính từ. Xác định loại từ trước, loại được 2 đáp án ngay.</li>
<li><strong>Part 7: đọc hết bài mới đọc câu hỏi.</strong> Mất thời gian và quên chi tiết. Đọc câu hỏi trước, quét tìm thông tin sau — xem kỹ thuật ở <a href="/ky-nang/doc.html">hướng dẫn luyện đọc</a>.</li>
<li><strong>Hết giờ ở Part 7.</strong> Dành quá nhiều thời gian cho Part 5–6 (câu khó) nên không còn giờ làm Part 7 (54 câu — hơn một phần tư bài thi). Quản lý thời gian: Part 5 tối đa 12 phút, Part 6 tối đa 10 phút.</li>
<li><strong>Bỏ trống câu không biết.</strong> TOEIC không trừ điểm câu sai — câu nào không biết thì đoán và chuyển sang câu tiếp theo, không bao giờ để trống.</li>
<li><strong>Dịch "tôi 20 tuổi" trong Part 2 thành câu trả lời sai:</strong> câu hỏi <em>"How old are you?"</em> — đáp án đúng dạng <em>"I'm twenty."</em> Lỗi này nhỏ nhưng xuất hiện trong cả Listening và Speaking.</li>
</ul>
<h2>Kế hoạch ôn 8 tuần (mục tiêu 600–750)</h2>
<ul>
<li><strong>Tuần 1–2:</strong> Làm quen format: làm 1 đề Listening + 1 đề Reading (đề tự biên soạn hoặc sách luyện thi), chấm và ghi lại phần hay sai nhất. Học 30 từ vựng công việc mỗi tuần theo chủ đề (email, họp, hợp đồng, du lịch công tác).</li>
<li><strong>Tuần 3–4:</strong> Tập trung vào điểm yếu: Listening yếu thì luyện nghe Part 2–3 mỗi ngày 30 phút (xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>); Reading yếu thì luyện Part 5 (ngữ pháp) và Part 7 (đọc hiểu).</li>
<li><strong>Tuần 5–6:</strong> Luyện đề có bấm giờ: Listening 45 phút + Reading 75 phút liên tục. Chữa kỹ từng câu sai — hiểu vì sao sai quan trọng hơn làm nhiều đề.</li>
<li><strong>Tuần 7–8:</strong> Làm 2 đề thi thử đầy đủ trong điều kiện thi thật. Tuần cuối: ôn lại từ vựng và lỗi cũ, nghỉ ngơi trước ngày thi 1 ngày.</li>
</ul>
<p>Muốn luyện TOEIC qua trò chơi? Chơi <a href="/tro-choi/toeic-arcade.html">TOEIC Arcade — luyện TOEIC qua trò chơi</a>. Học theo sách? Xem <a href="/sach/barrons-toeic.html">hướng dẫn học với sách Barron's TOEIC</a> (kế hoạch 8 tuần). Cần TOEIC để xin việc? Xem <a href="/cong-viec.html">tiếng Anh công việc</a> và <a href="/trinh-do/b1.html">trình độ B1</a> (mức nền tảng cho mục tiêu 600) hoặc <a href="/trinh-do/b2.html">trình độ B2</a> (mức nền tảng cho mục tiêu 750+).</p>
""",

"pte": """
<p class="lead">PTE Academic là kỳ thi tiếng Anh trên máy tính, chấm bằng AI — bạn nói vào micro, gõ bài viết trên máy, kết quả thường có trong khoảng 2 ngày. Bài thi có 3 phần, thang điểm 10–90, dùng cho du học và định cư (đặc biệt phổ biến cho Úc). Trang này dạy bạn cấu trúc bài thi, chiến thuật từng dạng câu hỏi và bài tập tự biên soạn để luyện tập.</p>
""" + AI_NOTE + """
<h2>Cấu trúc bài thi (đã đối chiếu pearsonpte.com)</h2>
<p>PTE Academic thi hoàn toàn trên máy tính tại trung tâm thi được ủy quyền, trong một buổi khoảng 2 giờ. Bài thi có 3 phần với tổng cộng 22 dạng câu hỏi. Điểm tổng và điểm từng kỹ năng (Nghe, Nói, Đọc, Viết) đều theo thang 10–90. Một điểm đặc biệt: một số dạng câu hỏi được chấm cho cả 2 kỹ năng cùng lúc (ví dụ: Read Aloud chấm cả Nói và Đọc; Write From Dictation chấm cả Nghe và Viết), nên chiến thuật luyện tập khác với IELTS hay TOEFL.</p>
<div class="table-wrap"><table><thead><tr><th>Phần thi</th><th>Thời gian</th><th>Dạng câu hỏi chính</th></tr></thead><tbody>
<tr><td>Phần 1: Nói &amp; Viết</td><td>76–84 phút</td><td>Giới thiệu bản thân (không chấm điểm), Read Aloud (đọc to), Repeat Sentence (nghe và nhắc lại câu), Describe Image (mô tả hình ảnh), Retell Lecture (nghe bài giảng và kể lại), Answer Short Question (trả lời câu hỏi ngắn), Summarize Written Text (tóm tắt đoạn văn), Write Essay (viết luận), cùng 2 dạng mới từ tháng 8/2025: Summarize Group Discussion và Respond to a Situation</td></tr>
<tr><td>Phần 2: Đọc</td><td>22–30 phút</td><td>Điền từ vào chỗ trống (chọn từ cho sẵn và kéo-thả), trắc nghiệm nhiều đáp án và một đáp án, sắp xếp lại đoạn văn (Reorder Paragraphs)</td></tr>
<tr><td>Phần 3: Nghe</td><td>31–39 phút</td><td>Tóm tắt bài nói, trắc nghiệm, điền từ vào chỗ trống khi nghe, chọn tóm tắt đúng, chọn từ còn thiếu, tô sáng từ sai, Write From Dictation (nghe và viết lại câu)</td></tr>
</tbody></table></div>
<p>Lưu ý: Pearson đã cập nhật định dạng bài thi (rút ngắn thời gian và thêm 2 dạng câu hỏi nói mới từ tháng 8/2025). Các nguồn cũ hơn có thể vẫn ghi bài thi dài khoảng 3 giờ với 7 dạng câu hỏi nói — đó là định dạng cũ. <strong>Chưa kiểm chứng được:</strong> lệ phí thi và lịch thi cụ thể tại Việt Nam thay đổi theo thời điểm — hãy xem trên trang pearsonpte.com trước khi đăng ký. Trang này không ghi lệ phí hay ngày thi cụ thể.</p>
<h2>Chiến thuật từng dạng câu hỏi quan trọng</h2>
<p><strong>Read Aloud — đọc to đoạn văn (chấm cả Nói và Đọc).</strong> Bạn có vài giây chuẩn bị trước khi micro mở. Dùng thời gian đó đọc lướt đoạn văn, chú ý từ khó và dấu câu. Khi đọc, nói rõ ràng, tốc độ tự nhiên, ngắt nghỉ ở dấu phẩy và dấu chấm. Đừng đọc quá nhanh để "cho xong" — máy chấm cả độ trôi chảy và phát âm, đọc nhanh mà vấp thì mất điểm cả hai.</p>
<p><strong>Repeat Sentence — nghe 1 câu và nhắc lại (chấm cả Nói và Nghe).</strong> Đây là dạng câu "ăn điểm" lớn nhất của PTE vì xuất hiện nhiều lần. Chiến thuật: nghe và hiểu ý chính của câu, đừng cố nhớ từng từ. Nhắc lại ngay khi micro mở, giữ đúng 50–70% từ quan trọng của câu gốc theo đúng thứ tự. Nếu quên một từ, bỏ qua và nói tiếp — dừng lại im lặng trừ điểm nhiều hơn nói thiếu 1 từ. Luyện tập: nghe một câu tiếng Anh, nhắc lại ngay không nhìn chữ — xem kỹ thuật shadowing ở <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>.</p>
<p><strong>Describe Image — mô tả hình ảnh trong 40 giây.</strong> Đừng cố mô tả mọi chi tiết. Dùng khung cố định: mở đầu (<em>The image shows…</em>) → xu hướng chính / điểm cao nhất / điểm thấp nhất → kết luận (<em>In conclusion…</em>). Nói liên tục, không im lặng quá 3 giây — im lặng lâu máy sẽ tự ngắt ghi âm.</p>
<p><strong>Write From Dictation — nghe 1 câu và gõ lại (chấm cả Nghe và Viết, xuất hiện nhiều lần).</strong> Đây là dạng câu quan trọng bậc nhất: mỗi câu đúng từng từ được điểm cao. Chiến thuật: nghe lần đầu và gõ ngay những từ đầu tiên bạn nghe được, sau đó điền nốt phần còn lại từ trí nhớ. Kiểm tra chính tả và dấu câu trước khi sang câu tiếp theo. Luyện tập: nghe chép chính tả mỗi ngày 10 câu — xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>.</p>
<p><strong>Reading — Fill in the Blanks (kéo-thả).</strong> Đọc cả câu, xác định loại từ cần điền (danh từ, động từ, tính từ) và nghĩa phù hợp trước khi kéo từ vào. Collocation là chìa khóa: <em>make a decision, play a role, draw attention</em> — học cụm từ giúp bạn chọn đúng ngay cả khi không biết hết nghĩa của từ.</p>
<p><strong>Reorder Paragraphs — sắp xếp lại đoạn văn.</strong> Tìm câu mở đầu (thường là câu giới thiệu chủ đề chung, không có từ nối như <em>however, therefore</em> hay đại từ <em>this, they</em> chỉ về trước). Sau đó nối các câu bằng từ nối và đại từ thay thế: câu nào có <em>this problem</em> thì phải đứng sau câu nêu ra "problem" đó.</p>
<p><strong>Write Essay — viết luận 200–300 từ trong 20 phút.</strong> Dùng khung cố định 4 đoạn: mở bài (nêu vấn đề + quan điểm) → 2 đoạn thân bài (mỗi đoạn 1 luận điểm + ví dụ) → kết bài. Máy chấm cả ngữ pháp, chính tả, từ vựng và cấu trúc — vì vậy viết đúng và rõ ràng quan trọng hơn viết "hay". Luyện tập: xem <a href="/ky-nang/viet.html">hướng dẫn luyện viết</a>.</p>
<h2>Bài tập tự biên soạn (không phải đề thi thật)</h2>
<p><strong>Repeat Sentence — luyện tập.</strong> Đọc to câu sau đây một lần, che đi, rồi nhắc lại từ trí nhớ (tự biên soạn, không phải câu thi thật): <em>"The library will be closed on Monday for maintenance work."</em> — Kiểm tra: bạn nhớ được bao nhiêu từ theo đúng thứ tự? Mục tiêu: nhớ ít nhất 8/10 từ. Luyện mỗi ngày 10 câu như vậy, tăng dần độ dài câu.</p>
<p><strong>Describe Image — luyện tập.</strong> Tưởng tượng một biểu đồ cột cho thấy số lượng sinh viên quốc tế tại một trường đại học tăng từ 500 (năm 2020) lên 1.200 (năm 2024). Hãy nói trong 40 giây theo khung: <em>"The image shows… The most noticeable trend is… In 2020, the number was… By 2024, it had risen to… In conclusion…"</em> — Ghi âm lại và nghe: bạn có nói liên tục không? Có ngập ngừng quá 3 giây không?</p>
<p><strong>Reading — Fill in the Blanks (kéo-thả).</strong> Điền từ phù hợp vào chỗ trống (chọn từ danh sách: <em>role, decision, attention, growth</em>): <em>"The new policy will play an important ___ in reducing traffic in the city centre."</em> — Đáp án: <strong>role</strong> (<em>play a role in…</em> là collocation cố định). Câu 2: <em>"Before you make a ___, please read the contract carefully."</em> — Đáp án: <strong>decision</strong> (<em>make a decision</em>).</p>
<p><strong>Write From Dictation — luyện tập.</strong> Nhờ một người đọc to câu sau đây một lần, bạn gõ lại chính xác từng từ (tự biên soạn): <em>"Students must submit their assignments before Friday afternoon."</em> — Kiểm tra: chính tả từng từ, dấu chấm cuối câu, và từ <em>must</em> (không viết thành <em>most</em>).</p>
<p><strong>Answer Short Question — luyện tập.</strong> Trả lời ngắn gọn (1–2 từ) các câu hỏi sau: (1) <em>What do you call a person who writes books?</em> (2) <em>What season comes after summer?</em> (3) <em>How many days are there in a week?</em> — Đáp án: (1) A writer / an author. (2) Autumn (fall). (3) Seven.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Im lặng quá 3 giây khi nói.</strong> Trong các dạng câu nói, micro sẽ tự ngắt sau khoảng 3 giây im lặng. Nói liên tục quan trọng hơn nói đúng — nếu bí ý, hãy nói câu đệm: <em>Let me think… / In my opinion…</em></li>
<li><strong>Đọc Read Aloud quá nhanh.</strong> Đọc nhanh để "cho xong" làm máy chấm trừ điểm trôi chảy và phát âm. Đọc tốc độ tự nhiên, ngắt nghỉ ở dấu câu.</li>
<li><strong>Cố nhớ từng từ trong Repeat Sentence.</strong> Não không nhớ được 15 từ rời rạc — hãy nhớ ý chính và cụm từ. Nhắc lại 70% từ đúng thứ tự vẫn được điểm khá; im lặng thì được 0.</li>
<li><strong>Viết essay quá dài hoặc quá ngắn.</strong> Bài luận PTE yêu cầu 200–300 từ. Viết dưới 200 từ bị trừ điểm; viết quá 300 từ tốn thời gian mà không thêm điểm. Luyện viết đúng 220–280 từ.</li>
<li><strong>Không kiểm tra chính tả trong Write From Dictation.</strong> Một từ sai chính tả là mất điểm của cả câu. Dành 5 giây cuối kiểm tra lại các từ khó trước khi sang câu tiếp theo.</li>
<li><strong>Đoán mò trong Reading mà không dùng collocation.</strong> Dạng điền từ của PTE chấm cả kiến thức collocation — học cụm từ cố định là cách tăng điểm nhanh nhất ở phần này.</li>
<li><strong>Nhầm lẫn giữa thi trên máy và thi với người.</strong> PTE thi hoàn toàn với máy — không có giám khảo người để "cứu" bạn khi bạn ngập ngừng. Luyện nói với máy (ghi âm và nghe lại) thay vì chỉ luyện nói với bạn học.</li>
</ul>
<h2>Kế hoạch ôn 8 tuần</h2>
<ul>
<li><strong>Tuần 1–2:</strong> Làm quen format: đọc kỹ trang này, thử từng dạng câu hỏi 1 lần để biết mình yếu ở đâu. Học 30 collocation mỗi tuần.</li>
<li><strong>Tuần 3–4:</strong> Tập trung vào 2 dạng "ăn điểm" lớn nhất: Repeat Sentence và Write From Dictation — mỗi ngày 20 phút nghe và nhắc lại/gõ lại câu.</li>
<li><strong>Tuần 5–6:</strong> Luyện đề có bấm giờ: làm trọn 1 phần thi (Nói & Viết, hoặc Đọc, hoặc Nghe) trong thời gian thật. Chữa kỹ từng lỗi.</li>
<li><strong>Tuần 7–8:</strong> Làm 2 bài thi thử đầy đủ (dùng đề luyện thi chính thức hoặc sách luyện thi). Tuần cuối: ôn lại lỗi cũ, luyện nói mỗi ngày 15 phút để giữ phản xạ.</li>
</ul>
<p>Muốn luyện PTE qua trò chơi? Chơi <a href="/tro-choi/pte-arcade.html">PTE Arcade — luyện PTE qua trò chơi</a>. Cần PTE để du học Úc? Xem <a href="/du-hoc.html">chuẩn bị tiếng Anh đi du học</a> và so sánh với <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> để chọn kỳ thi phù hợp. Chưa rõ trình độ của mình? Xem <a href="/trinh-do/b2.html">trình độ B2</a> (mức nền tảng thường cần cho mục tiêu PTE 50–65).</p>
""",
"toefl": """
<p class="lead">TOEFL iBT là kỳ thi tiếng Anh học thuật phổ biến nhất cho du học Mỹ và quốc tế. Từ ngày 21/01/2026, ETS đã cập nhật định dạng bài thi: ngắn hơn (khoảng 90 phút làm bài), thêm dạng câu hỏi mới ở cả 4 kỹ năng, và thang điểm mới 1–6. Trang này dạy bạn định dạng mới, chiến thuật từng phần và bài tập tự biên soạn để luyện tập.</p>
""" + AI_NOTE + """
<h2>Cấu trúc bài thi mới từ 21/01/2026 (đã đối chiếu ETS và IIG Vietnam)</h2>
<p>Bài thi TOEFL iBT mới thi hoàn toàn trên máy tính, gồm 4 phần với tổng thời gian làm bài khoảng 90 phút (cộng thêm thời gian hướng dẫn, tổng buổi thi khoảng 2 giờ). Reading và Listening có tính thích ứng (adaptive): phần đầu đánh giá trình độ của bạn, phần sau điều chỉnh độ khó theo kết quả đó. Thang điểm mới là 1–6 cho từng kỹ năng và điểm tổng; bảng điểm cũng hiển thị điểm tương đương theo thang cũ 0–120 và trình độ CEFR tới tháng 01/2028 để các trường quen dần.</p>
<div class="table-wrap"><table><thead><tr><th>Phần thi</th><th>Số câu / nhiệm vụ</th><th>Thời gian</th><th>Nội dung chính</th></tr></thead><tbody>
<tr><td>Reading</td><td>Khoảng 50 câu</td><td>Khoảng 30 phút</td><td>Hoàn thành từ trong câu, đọc hiểu đời sống hằng ngày, đọc đoạn văn học thuật</td></tr>
<tr><td>Listening</td><td>Khoảng 47 câu</td><td>Khoảng 29 phút</td><td>Nghe và chọn câu trả lời, nghe hội thoại, nghe thông báo, nghe bài giảng học thuật</td></tr>
<tr><td>Writing</td><td>12 nhiệm vụ</td><td>Khoảng 23 phút</td><td>Xây dựng câu, viết email, viết bài thảo luận học thuật</td></tr>
<tr><td>Speaking</td><td>11 nhiệm vụ</td><td>Khoảng 8 phút</td><td>Nghe và lặp lại, trả lời phỏng vấn</td></tr>
</tbody></table></div>
<p>Định dạng cũ (trước 21/01/2026) có Reading 20 câu/35 phút, Listening 28 câu/36 phút, Speaking 4 nhiệm vụ/16 phút, Writing 2 nhiệm vụ/29 phút, thang điểm 0–30 mỗi kỹ năng và tổng 0–120. Nếu bạn đang ôn theo tài liệu cũ, hãy đối chiếu với định dạng mới ở trên — dạng câu hỏi và cách chấm đã thay đổi. <strong>Chưa kiểm chứng được:</strong> lệ phí thi và lịch thi cụ thể tại Việt Nam thay đổi theo thời điểm — hãy xem trên trang của ETS hoặc IIG Vietnam trước khi đăng ký. Trang này không ghi lệ phí hay ngày thi cụ thể.</p>
<h2>Chiến thuật từng phần (định dạng mới)</h2>
<p><strong>Reading — 50 câu, 30 phút, có tính thích ứng.</strong> Phần đầu gồm các câu hoàn thành từ (Complete the Words) và đọc hiểu đời sống — làm nhanh và chính xác để phần sau nhận được câu khó hơn (và điểm cao hơn). Đừng dành quá 1 phút cho 1 câu đọc học thuật: đọc câu hỏi trước, quét đoạn văn tìm thông tin, chọn đáp án rồi đi tiếp. Chú ý dạng "hoàn thành từ": chính tả và dạng từ (danh từ/động từ/tính từ) đều được chấm. Luyện tập: xem <a href="/ky-nang/doc.html">hướng dẫn luyện đọc</a> và học từ vựng học thuật ở <a href="/trinh-do/c1.html">trình độ C1</a>.</p>
<p><strong>Listening — 47 câu, 29 phút, có tính thích ứng.</strong> Nghe hội thoại trong trường (đăng ký môn học, hỏi thư viện), thông báo và bài giảng ngắn. Chiến thuật: nghe và ghi chép từ khóa (tên, số, thái độ người nói), đừng ghi câu đầy đủ. Câu hỏi "người nói sẽ làm gì tiếp theo?" thường có đáp án ở cuối đoạn nghe. Vì bài thi có tính thích ứng, hãy tập trung tối đa ở những câu đầu — chúng quyết định độ khó của phần sau. Luyện tập: xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>.</p>
<p><strong>Writing — 12 nhiệm vụ, 23 phút.</strong> Phần viết mới gồm 3 dạng: xây dựng câu (Build a Sentence — sắp xếp từ thành câu đúng), viết email (Write an Email — trả lời email trong tình huống cho sẵn), và viết bài thảo luận học thuật (Write for an Academic Discussion — nêu quan điểm về một chủ đề học thuật). Chiến thuật: dạng xây dựng câu chấm chính tả và dạng từ — kiểm tra kỹ từng từ trước khi gửi. Viết email: chú ý giọng văn trang trọng và cấu trúc (chào hỏi → nội dung → kết thúc lịch sự). Viết thảo luận: nêu quan điểm rõ ràng, có 1–2 lý do, dùng từ nối học thuật. Luyện tập: xem <a href="/ky-nang/viet.html">hướng dẫn luyện viết</a>.</p>
<p><strong>Speaking — 11 nhiệm vụ, 8 phút.</strong> Phần nói mới gồm nghe và lặp lại (Listen and Repeat — nhắc lại câu nghe được, chấm phát âm và độ chính xác) và trả lời phỏng vấn (Take an Interview — trả lời câu hỏi về bản thân và quan điểm). Chiến thuật: dạng lặp lại — nghe kỹ ngữ điệu và trọng âm, nhắc lại ngay với cùng nhịp điệu. Dạng phỏng vấn — trả lời 2–3 câu mỗi câu hỏi, có lý do hoặc ví dụ; đừng trả lời 1 từ. Luyện tập: xem <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a> và kỹ thuật shadowing.</p>
<h2>Bài tập tự biên soạn (không phải đề thi thật)</h2>
<p><strong>Reading — hoàn thành từ.</strong> Điền từ phù hợp vào chỗ trống (tự biên soạn): <em>"The university library is open from 8 a.m. to 10 p.m. Students can borrow up to five books at a ___."</em> (a) time (b) timer (c) timely — Đáp án: <strong>(a) time</strong> (<em>at a time</em> là cụm cố định — "cùng một lúc").</p>
<p><strong>Listening — nghe hội thoại (đọc transcript tự biên soạn như bài tập nghe hiểu).</strong></p>
<p><em>Student: Excuse me, I'd like to change my class schedule. My biology class is at the same time as my chemistry lab.<br>
Advisor: I see. The biology class is also offered on Thursday afternoon. Would that work for you?<br>
Student: Yes, Thursday afternoon is fine. Thank you so much.</em></p>
<p>Câu hỏi: (1) Vì sao sinh viên muốn đổi lịch học? (2) Cô cố vấn đề xuất giải pháp gì? (3) Sinh viên có đồng ý không? — Đáp án: (1) Vì lớp sinh học trùng giờ với giờ thực hành hóa học. (2) Chuyển sang lớp sinh học chiều thứ Năm. (3) Có — chiều thứ Năm phù hợp với bạn ấy.</p>
<p><strong>Writing — viết email (đề tự biên soạn).</strong> <em>Bạn nhận được email từ giáo viên yêu cầu nộp bài tập muộn nhất là thứ Sáu. Bạn bị ốm và cần xin gia hạn thêm 3 ngày. Viết email trả lời (khoảng 80–100 từ).</em> — Khung gợi ý: chào hỏi trang trọng (<em>Dear Professor Smith,</em>) → giải thích lý do (<em>I am writing to ask for… because…</em>) → đề xuất cụ thể (<em>Could I please submit… by Monday?</em>) → cảm ơn và kết thúc (<em>Thank you for your understanding. Best regards,</em>). Nhớ: viết email học thuật thì không dùng từ viết tắt (<em>don't, can't</em>) và không dùng giọng văn thân mật.</p>
<p><strong>Speaking — trả lời phỏng vấn (câu hỏi tự biên soạn).</strong> <em>"What is your favourite subject at school, and why?"</em> — Câu trả lời yếu: <em>"Maths."</em> Câu trả lời tốt: <em>"My favourite subject is maths, because I enjoy solving problems — it feels like a puzzle, and I like the feeling when I finally find the answer. I also think maths is useful for everyday life, for example when I need to calculate prices or plan a budget."</em> — Trả lời 2–3 câu, có lý do và ví dụ.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Ôn theo tài liệu cũ mà không biết định dạng đã đổi.</strong> Từ 21/01/2026, dạng câu hỏi, thời gian và thang điểm TOEFL iBT đều mới. Ôn theo sách cũ (Reading 20 câu, Speaking 4 nhiệm vụ, thang 0–120) sẽ khiến bạn bỡ ngỡ trong phòng thi. Luôn đối chiếu với trang chính thức của ETS trước khi thi.</li>
<li><strong>Nghe không ghi chép.</strong> Bài giảng và hội thoại dài, không ghi chép thì nghe xong quên ngay. Ghi từ khóa, không ghi câu đầy đủ — xem kỹ thuật ở <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>.</li>
<li><strong>Viết email bằng giọng văn thân mật.</strong> <em>"Hi, I want more time for my homework!!!"</em> — sai hoàn toàn trong ngữ cảnh học thuật. Email cho giáo viên phải trang trọng, rõ ràng và lịch sự.</li>
<li><strong>Trả lời Speaking quá ngắn.</strong> Trả lời 1 từ hoặc 1 câu ngắn không đủ dữ liệu để máy chấm phát âm và độ trôi chảy. Luôn trả lời 2–3 câu với lý do hoặc ví dụ.</li>
<li><strong>Sai chính tả trong dạng "hoàn thành từ".</strong> Dạng câu này chấm chính tả từng từ — <em>recieve</em> thay vì <em>receive</em> là mất điểm ngay. Học chính tả các từ học thuật thông dụng.</li>
<li><strong>Làm câu đầu qua loa.</strong> Vì Reading và Listening có tính thích ứng, những câu đầu tiên ảnh hưởng tới độ khó (và điểm tối đa) của phần sau. Tập trung tối đa ngay từ câu đầu tiên.</li>
<li><strong>Dịch từng từ khi đọc đoạn văn học thuật.</strong> Đọc để nắm ý chính và cấu trúc lập luận, không dịch từng từ — xem <a href="/ky-nang/doc.html">hướng dẫn luyện đọc</a>.</li>
</ul>
<h2>Kế hoạch ôn 8 tuần</h2>
<ul>
<li><strong>Tuần 1–2:</strong> Làm quen định dạng mới: đọc kỹ trang này, thử từng dạng câu hỏi 1 lần. Ôn từ vựng học thuật (30 từ/tuần) và chính tả các từ thông dụng.</li>
<li><strong>Tuần 3–4:</strong> Tập trung vào điểm yếu nhất. Nghe yếu thì luyện nghe hội thoại trường học 30 phút/ngày; viết yếu thì luyện viết email và bài thảo luận 3 bài/tuần.</li>
<li><strong>Tuần 5–6:</strong> Luyện đề có bấm giờ theo đúng thời gian thật (Reading 30 phút, Listening 29 phút, Writing 23 phút, Speaking 8 phút). Chữa kỹ từng lỗi.</li>
<li><strong>Tuần 7–8:</strong> Làm 2 bài thi thử đầy đủ trong điều kiện thi thật. Tuần cuối: ôn lại lỗi cũ, luyện nói mỗi ngày 15 phút để giữ phản xạ.</li>
</ul>
<p>Cần TOEFL để du học Mỹ? Xem <a href="/du-hoc.html">chuẩn bị tiếng Anh đi du học</a> và so sánh với <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> và <a href="/luyen-thi/pte.html">luyện thi PTE Academic</a> để chọn kỳ thi phù hợp với trường bạn nộp đơn. Chưa rõ trình độ của mình? Xem <a href="/trinh-do/b2.html">trình độ B2</a> và <a href="/trinh-do/c1.html">trình độ C1</a>.</p>
""",
"vstep": """
<p class="lead">VSTEP là kỳ thi đánh giá năng lực tiếng Anh theo Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam — kỳ thi chuẩn hóa của Bộ Giáo dục và Đào tạo, dùng cho xét tốt nghiệp, thi công chức, xét tuyển sau đại học và nhiều mục đích khác trong nước. Bài thi VSTEP.3-5 đánh giá 3 bậc (B1, B2, C1) trong một đề thi chung duy nhất. Trang này dạy bạn cấu trúc bài thi, cách tính điểm, chiến thuật từng phần và bài tập tự biên soạn để luyện tập.</p>
""" + AI_NOTE + """
<h2>Cấu trúc bài thi (đã đối chiếu Quyết định 729/QĐ-BGDĐT và các trường đại học tổ chức thi)</h2>
<p>Bài thi VSTEP.3-5 gồm 4 kỹ năng, làm liên tục trong một ca thi khoảng 180 phút (chưa kể thời gian nghỉ chuyển phần). Mỗi kỹ năng chấm trên thang 10; điểm trung bình của 4 kỹ năng quyết định bậc đạt được. Định dạng này được ban hành theo Quyết định 729/QĐ-BGDĐT ngày 11/3/2015 của Bộ Giáo dục và Đào tạo và vẫn giữ nguyên cấu trúc tới nay. Ngoài ra còn có bài thi VSTEP.2 (chỉ đánh giá bậc 2, tương đương A2) — trang này tập trung vào VSTEP.3-5 vì đó là bài thi phổ biến nhất.</p>
<div class="table-wrap"><table><thead><tr><th>Kỹ năng</th><th>Thời gian</th><th>Nội dung</th><th>Cách tính bậc</th></tr></thead><tbody>
<tr><td>Nghe (Listening)</td><td>Khoảng 40 phút (đã gồm 7 phút chuyển đáp án)</td><td>35 câu trắc nghiệm, 3 phần: thông báo – hướng dẫn ngắn, hội thoại, bài nói chuyện – bài giảng</td><td rowspan="4">Điểm trung bình 4 kỹ năng (làm tròn tới 0,5): từ 4,0 tới 5,5 đạt bậc 3 (B1); từ 6,0 tới 8,0 đạt bậc 4 (B2); từ 8,5 tới 10 đạt bậc 5 (C1). Dưới 4,0 không đạt bậc nào.</td></tr>
<tr><td>Đọc (Reading)</td><td>60 phút</td><td>40 câu trắc nghiệm, 4 bài đọc (tổng khoảng 1.900–2.050 từ), độ khó tương đương bậc 3–5</td></tr>
<tr><td>Viết (Writing)</td><td>60 phút</td><td>Bài 1: viết thư/thư điện tử khoảng 120 từ (chiếm 1/3 điểm phần Viết). Bài 2: viết luận khoảng 250 từ (chiếm 2/3 điểm phần Viết)</td></tr>
<tr><td>Nói (Speaking)</td><td>Khoảng 12 phút</td><td>3 phần: trả lời câu hỏi, trình bày về một chủ đề (thường có 2 chủ đề), thảo luận. Thi trên máy tính (ghi âm qua micro) hoặc với giám khảo trực tiếp, tùy đơn vị tổ chức thi</td></tr>
</tbody></table></div>
<p>Điểm Nghe và Đọc được quy đổi từ số câu đúng sang thang 10 theo bảng quy đổi chuẩn (không phải chia tỷ lệ đơn giản). Điểm Viết và Nói do giám khảo chấm theo tiêu chí. <strong>Chưa kiểm chứng được:</strong> danh sách đơn vị tổ chức thi, lịch thi và lệ phí cụ thể thay đổi theo thời điểm — hãy xem trên trang của đơn vị bạn định đăng ký thi (ví dụ: các trường đại học được Bộ Giáo dục và Đào tạo cho phép tổ chức thi VSTEP) trước khi đăng ký. Trang này không ghi danh sách nơi thi, lịch thi hay lệ phí cụ thể.</p>
<h2>Chiến thuật từng phần</h2>
<p><strong>Nghe — 35 câu, 40 phút, 3 phần với độ khó tăng dần.</strong> Phần 1 (thông báo, hướng dẫn ngắn): nghe và chọn đáp án đúng — tập trung vào số liệu (giờ, ngày, số tiền, địa điểm). Phần 2 (hội thoại): nghe 2 người nói chuyện, chú ý ai nói gì và thái độ của họ. Phần 3 (bài giảng, bài nói chuyện): dài nhất và khó nhất — ghi chép từ khóa trong lúc nghe, đừng cố ghi câu đầy đủ. Mẹo: 7 phút chuyển đáp án cuối giờ là để kiểm tra lại, không phải để làm bài — hãy ghi đáp án ngay trong lúc nghe. Luyện tập: xem <a href="/ky-nang/nghe.html">hướng dẫn luyện nghe</a>.</p>
<p><strong>Đọc — 40 câu, 60 phút, 4 bài đọc.</strong> Độ khó tăng dần: bài 1–2 ở mức B1, bài 3–4 ở mức B2–C1. Chiến thuật: làm bài 1–2 trước để "lấy điểm chắc", dành nhiều thời gian cho bài 3–4. Đọc câu hỏi trước, quét bài tìm thông tin. Dạng câu hỏi phổ biến: tìm ý chính, tìm chi tiết, suy ra thái độ/quan điểm của tác giả, đoán nghĩa của từ trong ngữ cảnh. Chú ý từ nối và từ mang sắc thái (<em>however, surprisingly, unfortunately</em>) — chúng thường là chìa khóa của câu hỏi suy luận. Luyện tập: xem <a href="/ky-nang/doc.html">hướng dẫn luyện đọc</a>.</p>
<p><strong>Viết Bài 1 — thư/email khoảng 120 từ, 20 phút.</strong> Đọc kỹ yêu cầu: viết cho ai? (bạn bè hay người lạ? — quyết định giọng văn thân mật hay trang trọng). Thư phải có đủ 3 phần: mở đầu (nêu lý do viết thư), thân bài (trả lời đủ các ý yêu cầu), kết thúc (câu chào phù hợp). Lỗi phổ biến: thiếu 1 ý trong yêu cầu (mỗi ý thiếu là mất điểm), hoặc viết quá dài (trên 140 từ tốn thời gian của Bài 2 mà không thêm điểm).</p>
<p><strong>Viết Bài 2 — luận khoảng 250 từ, 40 phút, chiếm 2/3 điểm phần Viết.</strong> Dàn bài chuẩn: mở bài (nêu vấn đề + quan điểm) → thân bài 2 đoạn (mỗi đoạn 1 luận điểm + giải thích/ví dụ) → kết bài. Vì Bài 2 chiếm 2/3 điểm, hãy dành đủ 40 phút cho nó — đừng viết Bài 1 quá kỹ rồi không còn giờ viết Bài 2. Luyện tập: xem <a href="/ky-nang/viet.html">hướng dẫn luyện viết</a> và dùng <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a>.</p>
<p><strong>Nói — 3 phần, 12 phút.</strong> Phần 1: trả lời 3–6 câu hỏi ngắn về 2 chủ đề quen thuộc (gia đình, sở thích, công việc) — trả lời 2–3 câu mỗi câu hỏi, đừng trả lời 1 từ. Phần 2: trình bày về một chủ đề cho sẵn (thường có gợi ý) — dùng thời gian chuẩn bị để viết dàn ý, nói có mở đầu, 2–3 ý, kết luận. Phần 3: thảo luận sâu hơn — đưa ra ý kiến, so sánh, nêu ưu/nhược điểm. Nếu thi trên máy tính, nói rõ ràng vào micro và đừng im lặng quá lâu. Luyện tập: xem <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>.</p>
<h2>Bài tập tự biên soạn (không phải đề thi thật)</h2>
<p><strong>Nghe — hội thoại (đọc transcript tự biên soạn như bài tập nghe hiểu).</strong></p>
<p><em>Nam: Hi, Lan. Have you finished the report for Mr. Tuan?<br>
Lan: Not yet. I need one more day. The data from the sales team arrived late.<br>
Nam: That's okay. The deadline is Friday, so you still have time.<br>
Lan: Thanks. I'll send it to you on Thursday morning.</em></p>
<p>Câu hỏi: (1) Vì sao Lan chưa xong báo cáo? (2) Hạn nộp báo cáo là khi nào? (3) Lan sẽ gửi báo cáo cho Nam khi nào? — Đáp án: (1) Vì dữ liệu từ đội bán hàng tới muộn. (2) Thứ Sáu. (3) Sáng thứ Năm.</p>
<p><strong>Đọc — đoán nghĩa từ trong ngữ cảnh.</strong> Đọc câu tự biên soạn: <em>"The new shopping centre has attracted a large number of visitors since it opened last month. Many shops in the area have benefited from the increase in customers."</em> — Từ <em>benefited from</em> trong câu có nghĩa gần nhất với: (a) bị ảnh hưởng xấu bởi (b) được lợi từ (c) phàn nàn về — Đáp án: <strong>(b) được lợi từ</strong>. <em>Benefit from</em> nghĩa là "được lợi từ cái gì".</p>
<p><strong>Viết Bài 1 — thư (đề tự biên soạn).</strong> <em>Bạn vừa chuyển tới một thành phố mới. Viết thư cho một người bạn (khoảng 120 từ) kể về thành phố mới, nơi ở mới và công việc/học tập mới của bạn.</em> — Khung gợi ý: mở đầu (<em>I'm writing to tell you about…</em>) → 3 ý (thành phố, nơi ở, công việc/học tập) → kết thúc (<em>Write back soon! / Hope to see you soon!</em>). Giọng văn thân mật vì viết cho bạn bè.</p>
<p><strong>Viết Bài 2 — luận (đề tự biên soạn).</strong> <em>"Some people think that students should use mobile phones at school. Others think phones should be banned. Discuss both views and give your opinion."</em> — Hãy viết dàn bài: đoạn 1 (ủng hộ: tra cứu thông tin, liên lạc với gia đình); đoạn 2 (phản đối: mất tập trung, gian lận trong thi); kết bài (quan điểm của bạn). Sau đó viết bài 250 từ và nhờ <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> góp ý.</p>
<p><strong>Nói — trả lời câu hỏi (tự biên soạn).</strong> <em>"Do you prefer studying alone or with friends? Why?"</em> — Câu trả lời yếu: <em>"With friends."</em> Câu trả lời tốt: <em>"I prefer studying with friends, because we can discuss difficult topics together and explain things to each other. When I study alone, I sometimes feel sleepy and lose motivation. However, for exams I usually study alone in the last few days, because I need quiet time to review everything."</em> — Trả lời có lý do, ví dụ và cả mặt đối lập.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Nghe: không ghi đáp án ngay.</strong> Đợi nghe hết bài mới ghi đáp án thì quên mất. Ghi đáp án ngay khi nghe thấy, dùng 7 phút cuối để kiểm tra lại.</li>
<li><strong>Đọc: làm bài khó trước.</strong> Bài 3–4 (B2–C1) khó hơn nhưng cùng điểm mỗi câu với bài 1–2. Làm bài dễ trước để lấy điểm chắc, rồi mới làm bài khó.</li>
<li><strong>Viết Bài 1: thiếu ý trong yêu cầu.</strong> Đề yêu cầu trả lời 3 ý mà bạn chỉ trả lời 2 ý là mất điểm dù viết hay. Đọc kỹ đề, gạch chân từng ý yêu cầu, kiểm tra lại trước khi nộp bài.</li>
<li><strong>Viết Bài 2: viết dưới 250 từ.</strong> Bài luận dưới số từ yêu cầu bị trừ điểm. Luyện viết 260–280 từ để chắc chắn đủ.</li>
<li><strong>Viết: dùng từ viết tắt và giọng văn thân mật trong bài luận.</strong> <em>don't, can't, gonna</em> không dùng trong bài luận trang trọng — viết đầy đủ: <em>do not, cannot, going to</em>.</li>
<li><strong>Nói: trả lời 1 từ.</strong> <em>"Yes."</em> hoặc <em>"No."</em> gần như không được điểm. Luôn thêm lý do hoặc ví dụ — xem <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>.</li>
<li><strong>Tính điểm sai:</strong> nhiều bạn tưởng điểm trung bình 5,5 là B2 — sai. Theo quy đổi chính thức: 4,0–5,5 là B1; 6,0–8,0 là B2; 8,5–10 là C1. Muốn đạt B2 thì điểm trung bình phải từ 6,0 trở lên — nghĩa là không thể "kéo" bằng 1 kỹ năng giỏi nếu 3 kỹ năng còn lại yếu. Học đều 4 kỹ năng.</li>
</ul>
<h2>Kế hoạch ôn 8 tuần (mục tiêu bậc 4 – B2)</h2>
<ul>
<li><strong>Tuần 1–2:</strong> Làm quen format: đọc kỹ trang này, làm 1 đề Nghe + 1 đề Đọc (đề tự biên soạn hoặc sách luyện thi VSTEP), chấm và ghi lại phần hay sai nhất. Ôn lại ngữ pháp nền tảng ở <a href="/trinh-do/b1.html">trình độ B1</a>.</li>
<li><strong>Tuần 3–4:</strong> Tập trung vào điểm yếu nhất. Viết yếu thì viết 3 bài/tuần (1 thư + 2 luận); nói yếu thì luyện trả lời câu hỏi mỗi ngày 15 phút.</li>
<li><strong>Tuần 5–6:</strong> Luyện đề có bấm giờ: Nghe 40 phút + Đọc 60 phút + Viết 60 phút liên tục như thi thật. Chữa kỹ từng câu sai.</li>
<li><strong>Tuần 7–8:</strong> Làm 2 đề thi thử đầy đủ (4 kỹ năng) trong điều kiện thi thật. Tuần cuối: ôn lại từ vựng và lỗi cũ, nghỉ ngơi trước ngày thi 1 ngày.</li>
</ul>
<p>Muốn đạt bậc 3 (B1)? Ôn chắc <a href="/trinh-do/b1.html">trình độ B1</a>. Muốn đạt bậc 4 (B2)? Ôn chắc <a href="/trinh-do/b2.html">trình độ B2</a>. Muốn đạt bậc 5 (C1)? Ôn chắc <a href="/trinh-do/c1.html">trình độ C1</a>. So sánh với kỳ thi quốc tế? Xem <a href="/luyen-thi/ielts.html">luyện thi IELTS</a> và <a href="/luyen-thi/toeic.html">luyện thi TOEIC</a>.</p>
""",
}

for i, (slug, name, desc) in enumerate(TESTS):
    prev = (TESTS[i - 1][1], f"/luyen-thi/{TESTS[i - 1][0]}.html") if i > 0 else None
    next_ = (TESTS[i + 1][1], f"/luyen-thi/{TESTS[i + 1][0]}.html") if i < len(TESTS) - 1 else None
    extra = LUYEN_THI_GUIDE_EXTRA.get(slug, "")
    add(f"/luyen-thi/{slug}.html", name, f"Luyện thi {name}",
        guide_sections(TEST_BODIES[slug]) + (f"<section class=\"section\">{extra}</section>\n" if extra else "") + _eta_html(f"/luyen-thi/{slug}.html") + _guide_nav(
            prev, next_, ("Tất cả kỳ thi", "/luyen-thi/"),
            f"Lộ trình luyện thi {name} như thế nào?"),
        active="/luyen-thi/", eyebrow="Luyện thi", desc=desc)

# ---------------- Các mục còn lại ----------------
add("/tre-em.html", "Trẻ em", "Tiếng Anh cho trẻ em",
    guide_sections("""
<p class="lead">Tiếng Anh cho trẻ em: từ vựng theo chủ đề, bài hát, truyện ngắn và trò chơi — bài học ngắn, hình ảnh lớn, học qua chơi chứ không học thuộc lòng. Trang này dành cho cả trẻ em và phụ huynh cùng học với con.</p>
""" + AI_NOTE + """
<h2>Trẻ em học tiếng Anh khác người lớn như thế nào?</h2>
<p>Trẻ em không học tiếng Anh bằng cách học ngữ pháp — trẻ học bằng cách <strong>nghe, lặp lại và chơi</strong>. Một đứa trẻ 6 tuổi nghe bài hát tiếng Anh 20 lần sẽ thuộc lời mà không cần ai giải thích nghĩa từng từ. Vì vậy, cách học hiệu quả nhất cho trẻ là: nghe nhiều, nói theo, chơi trò chơi và đọc truyện có hình ảnh — mỗi ngày một ít (15–20 phút), đều đặn, vui vẻ. Ép trẻ ngồi học 1 giờ với sách ngữ pháp là cách nhanh nhất khiến trẻ ghét tiếng Anh.</p>
<p><strong>Theo độ tuổi:</strong> trẻ mầm non (3–5 tuổi) học qua bài hát, trò chơi vận động và flashcards hình ảnh — mục tiêu chỉ là làm quen với âm thanh tiếng Anh và 50–100 từ đơn giản (màu sắc, con vật, bộ phận cơ thể). Trẻ tiểu học (6–10 tuổi) học từ vựng theo chủ đề ở trường, câu giao tiếp đơn giản, truyện ngắn và bài hát có lời — mục tiêu là nói được câu đơn giản và đọc được truyện ngắn. Trẻ 11 tuổi trở lên có thể bắt đầu học ngữ pháp cơ bản và viết đoạn văn ngắn — lúc này mới nên dùng sách giáo khoa như <a href="/sach/global-success.html">Global Success</a> một cách có hệ thống.</p>
<h2>Từ vựng theo chủ đề cho trẻ</h2>
<p>Học từ theo chủ đề, mỗi chủ đề 10–15 từ, kèm hình ảnh và hành động. Dưới đây là 4 chủ đề đầu tiên nên học:</p>
<ul>
<li><strong>Gia đình (Family):</strong> mother, father, sister, brother, grandmother, grandfather, baby. Câu mẫu: <em>This is my mother. She is a teacher.</em></li>
<li><strong>Con vật (Animals):</strong> dog, cat, bird, fish, elephant, lion, monkey. Câu mẫu: <em>The elephant is big. The bird can fly.</em> — Trò chơi: bắt chước tiếng kêu và dáng đi của con vật, đoán tên bằng tiếng Anh.</li>
<li><strong>Màu sắc (Colours):</strong> red, blue, green, yellow, orange, purple, pink, brown, black, white. Câu mẫu: <em>What colour is this? It's red.</em> — Trò chơi: đi quanh nhà tìm đồ vật màu đỏ, rồi màu xanh.</li>
<li><strong>Trường học (School):</strong> book, pen, pencil, bag, desk, chair, teacher, student. Câu mẫu: <em>This is my bag. I have two pencils.</em></li>
</ul>
<p><strong>Cách học từ với trẻ:</strong> mỗi từ học kèm 3 thứ — hình ảnh, âm thanh và hành động. Ví dụ: học từ <em>jump</em> thì vừa nói vừa nhảy; học từ <em>apple</em> thì cầm quả táo thật hoặc xem hình quả táo. Trẻ nhớ qua tay và mắt, không nhớ qua chép từ 10 lần vào vở.</p>
<h2>Bài hát, truyện và trò chơi</h2>
<p><strong>Bài hát:</strong> hát mỗi ngày 1 bài, hát đi hát lại trong 1 tuần. Các bài hát kinh điển cho trẻ học tiếng Anh: <em>Head, Shoulders, Knees and Toes</em> (học bộ phận cơ thể qua vận động), <em>The Wheels on the Bus</em> (học từ về xe buýt và hành động), <em>If You're Happy and You Know It</em> (học cảm xúc và hành động), <em>Old MacDonald Had a Farm</em> (học tên con vật và tiếng kêu). Mẹo: hát chậm lần đầu, làm động tác theo lời hát — trẻ thuộc lời nhanh hơn khi cơ thể cùng tham gia.</p>
<p><strong>Truyện ngắn:</strong> đọc truyện có hình ảnh lớn, ít chữ mỗi trang. Cách đọc: phụ huynh đọc to, chỉ vào hình, hỏi trẻ bằng tiếng Anh đơn giản (<em>What is this? What colour is the dog?</em>). Đọc cùng một truyện 3–4 lần trong tuần — lần đầu nghe, lần sau trẻ bắt đầu nhớ và nói theo, lần thứ ba trẻ có thể kể lại. Đừng đổi truyện mới mỗi ngày; trẻ học qua lặp lại.</p>
<p><strong>Trò chơi:</strong> chơi <a href="/tro-choi/grade-4-quest.html">Grade 4 Quest — từ vựng và ngữ pháp theo sách lớp 4</a> và <a href="/tro-choi/starter-quest.html">Starter Quest — trò chơi cho người mới bắt đầu</a> trên trang này. Ở nhà, chơi trò "Simon Says" bằng tiếng Anh (<em>Simon says touch your nose!</em>), trò đoán từ qua hình vẽ, và trò tìm đồ vật theo màu sắc.</p>
<h2>Bài học mẫu: "My Family" (15 phút)</h2>
<p><strong>Phút 0–3 — Khởi động:</strong> hát bài <em>Finger Family</em> (gia đình ngón tay) cùng con, chỉ vào từng ngón tay: <em>Daddy finger, daddy finger, where are you?</em></p>
<p><strong>Phút 3–8 — Học từ mới:</strong> dùng flashcards hoặc hình vẽ: mother, father, sister, brother, grandmother, grandfather. Mỗi từ: chỉ hình, đọc to 3 lần, trẻ lặp lại. Hỏi: <em>Who is this? — This is my mother.</em></p>
<p><strong>Phút 8–12 — Chơi:</strong> trò "Ai đây?" — phụ huynh miêu tả một thành viên trong gia đình bằng tiếng Anh (<em>She cooks dinner. She is my…?</em>), trẻ đoán: <em>Mother!</em></p>
<p><strong>Phút 12–15 — Ôn lại:</strong> trẻ vẽ gia đình mình và giới thiệu bằng tiếng Anh: <em>This is my family. This is my father. He is a driver. This is my sister. She is 5 years old.</em></p>
<h2>Hướng dẫn cho phụ huynh</h2>
<ul>
<li><strong>Học cùng con, đừng chỉ giao bài cho con.</strong> Trẻ học tốt nhất khi phụ huynh cùng hát, cùng chơi, cùng đọc truyện. Bạn không cần giỏi tiếng Anh — bạn chỉ cần học cùng con, sai cùng con, sửa cùng con.</li>
<li><strong>15–20 phút mỗi ngày tốt hơn 2 giờ cuối tuần.</strong> Đều đặn là chìa khóa. Gắn giờ học tiếng Anh vào một thói quen có sẵn: sau bữa tối, trước giờ đi ngủ.</li>
<li><strong>Khen nỗ lực, không chê lỗi sai.</strong> Trẻ nói <em>"I is happy"</em> thì đừng sửa ngay thành "sai rồi, phải nói I am happy" — hãy lặp lại đúng một cách tự nhiên: <em>"Yes! You ARE happy!"</em> Trẻ sẽ tự sửa dần mà không sợ nói.</li>
<li><strong>Cho trẻ nghe tiếng Anh thụ động mỗi ngày:</strong> bật nhạc, phim hoạt hình tiếng Anh (có phụ đề tiếng Anh, không phải tiếng Việt) trong lúc chơi. Tai trẻ cần quen với âm thanh tiếng Anh trước khi miệng nói được.</li>
</ul>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Ép trẻ học ngữ pháp quá sớm:</strong> trẻ 6 tuổi không cần biết "hiện tại đơn" là gì — trẻ cần biết nói <em>I like apples</em>. Ngữ pháp chỉ nên học từ khoảng 10–11 tuổi trở lên.</li>
<li><strong>Dịch mọi từ sang tiếng Việt:</strong> hỏi trẻ <em>"Apple nghĩa là gì?"</em> rồi chờ trẻ trả lời "quả táo" là cách học chậm. Thay vào đó, chỉ vào quả táo và nói <em>apple</em> — trẻ hiểu trực tiếp bằng hình ảnh, không qua dịch.</li>
<li><strong>Cho trẻ xem phim có phụ đề tiếng Việt:</strong> trẻ sẽ đọc phụ đề Việt và bỏ qua tiếng Anh. Dùng phụ đề tiếng Anh hoặc không phụ đề — trẻ nghe và đoán nghĩa qua hình ảnh.</li>
<li><strong>Học từ rời rạc, không theo chủ đề:</strong> học 10 từ ngẫu nhiên mỗi ngày thì quên 9 từ sau 1 tuần. Học theo chủ đề và dùng từ trong câu, trong trò chơi thì nhớ lâu hơn nhiều.</li>
<li><strong>Phụ huynh phát âm sai rồi dạy con theo:</strong> nếu bạn không chắc cách đọc một từ, hãy tra bằng <a href="/cong-cu/tu-vung.html">công cụ tra từ bằng AI</a> để nghe phát âm mẫu, hoặc mở từ điển có audio. Phát âm sai học từ nhỏ rất khó sửa sau này.</li>
</ul>
<h2>Luyện tập nhanh (cùng con)</h2>
<details><summary><strong>Câu 1.</strong> Hỏi con: "What colour is the sky?" — Câu trả lời đúng là gì?</summary><p>Đáp án: <em>The sky is blue.</em> — Luyện mẫu câu <em>What colour is…? — It's…</em> với nhiều đồ vật trong nhà.</p></details>
<details><summary><strong>Câu 2.</strong> Điền từ: "This is my ___. She cooks dinner for our family." (mother / teacher / dog)</summary><p>Đáp án: <strong>mother</strong>. — Luyện đoán từ qua ngữ cảnh, không học thuộc lòng.</p></details>
<details><summary><strong>Câu 3.</strong> Sắp xếp thành câu đúng: "name / My / is / Lan / ."</summary><p>Đáp án: <em>My name is Lan.</em> — Đây là câu giới thiệu bản thân đầu tiên mọi trẻ em nên học.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Chơi cùng con: <a href="/tro-choi/grade-4-quest.html">Grade 4 Quest — từ vựng, ngữ pháp theo sách lớp 4</a>, <a href="/tro-choi/starter-quest.html">Starter Quest — trò chơi cho người mới bắt đầu</a>. Học theo sách giáo khoa trên lớp: <a href="/sach/global-success.html">hướng dẫn học với sách Global Success</a> (lớp 3–12). Khi con lớn hơn và cần học có hệ thống, xem <a href="/trinh-do/a1.html">trình độ A1 — mới bắt đầu</a> và <a href="/trinh-do/a2.html">trình độ A2 — sơ cấp</a>.</p>
""") + _eta_html("/tre-em.html") + _guide_nav(None, ("Tiếng Anh công việc", "/cong-viec.html"), None, "Cho tôi lộ trình dạy tiếng Anh cho trẻ em."),
    active="/tre-em.html", eyebrow="Trẻ em",
    desc="Tiếng Anh cho trẻ em: từ vựng theo chủ đề, bài hát, truyện ngắn và trò chơi — bài học ngắn, hình ảnh lớn.")

add("/cong-viec.html", "Tiếng Anh công việc", "Tiếng Anh cho công việc",
    guide_sections("""
<p class="lead">Tiếng Anh công việc không phải là tiếng Anh "khó hơn" — nó là tiếng Anh "đúng hoàn cảnh hơn": email trang trọng, họp bằng tiếng Anh, thuyết trình, phỏng vấn xin việc và từ vựng theo từng ngành nghề. Trang này dạy bạn mẫu câu dùng được ngay, theo từng tình huống công việc thật.</p>
""" + AI_NOTE + """
<h2>Tiếng Anh công việc khác tiếng Anh thường ngày ở điểm nào?</h2>
<p>Khác ở <strong>giọng văn (register)</strong>: cùng một ý, nói với bạn bè thì dùng một kiểu, viết email cho sếp hoặc khách hàng thì dùng kiểu khác. Ví dụ: muốn xin thêm thời gian, nói với bạn thì <em>"I need more time"</em> là đủ; viết email cho sếp thì phải viết <em>"Could I please have an extension until Friday? I would really appreciate it."</em> — lịch sự hơn, gián tiếp hơn, và có lý do. Người Việt hay mắc lỗi nói quá thẳng trong email công việc (<em>"Give me the report now"</em>), khiến người đọc cảm thấy bị ra lệnh.</p>
<p>Khác ở <strong>từ vựng chuyên ngành</strong>: mỗi ngành có bộ từ riêng — kế toán có <em>invoice, budget, revenue</em>; công nghệ có <em>deploy, bug, deadline</em>; y tế có <em>diagnosis, treatment, patient</em>. Bạn không cần biết hết — chỉ cần biết từ của ngành mình, và học chúng trong câu, không học danh sách từ rời rạc.</p>
<h2>Mẫu email công việc (tự biên soạn, dùng được ngay)</h2>
<p><strong>Email 1 — Xin nghỉ phép:</strong></p>
<p><em>Subject: Annual Leave Request — 15–17 December<br>
Dear Ms. Lan,<br>
I am writing to request annual leave from 15 to 17 December. I have completed all urgent tasks, and my colleague Hung will cover my work during my absence.<br>
Please let me know if this is possible. Thank you for your understanding.<br>
Best regards,<br>
Minh</em></p>
<p><strong>Email 2 — Hỏi thông tin / nhắc việc lịch sự:</strong></p>
<p><em>Subject: Follow-up — Contract for Project Alpha<br>
Dear Mr. Smith,<br>
I hope you are well. I am writing to follow up on the contract for Project Alpha, which we discussed last week. Could you please let me know when we can expect the signed copy?<br>
Thank you for your time. I look forward to hearing from you.<br>
Kind regards,<br>
Hoa</em></p>
<p><strong>Cấu trúc chung của email công việc:</strong> tiêu đề rõ ràng (nêu việc + thời gian nếu có) → chào hỏi trang trọng (<em>Dear Mr./Ms. + họ</em>) → câu mở đầu nêu mục đích (<em>I am writing to…</em>) → nội dung chính (ngắn gọn, mỗi đoạn 1 ý) → câu kết lịch sự (<em>Please let me know… / I look forward to hearing from you.</em>) → chữ ký (<em>Best regards / Kind regards + tên</em>). Nhớ: không dùng từ viết tắt (<em>don't, can't</em>) trong email trang trọng, và không dùng dấu chấm than (!!!).</p>
<h2>Tiếng Anh trong cuộc họp</h2>
<p><strong>Mở đầu cuộc họp:</strong> <em>Let's get started. The purpose of today's meeting is to discuss… / First, let's review…</em></p>
<p><strong>Đưa ra ý kiến:</strong> <em>In my opinion… / I think we should… / From my point of view… / One option is to…</em></p>
<p><strong>Đồng ý:</strong> <em>I agree with you. / That's a good point. / Exactly.</em></p>
<p><strong>Không đồng ý một cách lịch sự:</strong> <em>I see your point, but… / I'm not sure I agree, because… / That's an interesting idea. Have we considered…?</em> — Đừng bao giờ nói <em>"You're wrong"</em> trong cuộc họp; nói <em>"I see it differently"</em> thì lịch sự hơn nhiều.</p>
<p><strong>Hỏi lại khi không hiểu:</strong> <em>Could you explain that again, please? / Sorry, I didn't catch that. Could you repeat it? / Do you mean…?</em></p>
<p><strong>Kết thúc cuộc họp:</strong> <em>To sum up, we agreed to… / So, the next step is… / Thank you, everyone. Let's meet again next Monday.</em></p>
<h2>Phỏng vấn xin việc bằng tiếng Anh</h2>
<p><strong>Câu hỏi kinh điển: "Tell me about yourself."</strong> Trả lời bằng cấu trúc hiện tại → quá khứ → tương lai (xem ví dụ đầy đủ ở <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>). Đừng kể lại CV; hãy kể câu chuyện: bạn là ai, bạn đã làm gì, và vì sao bạn muốn công việc này.</p>
<p><strong>"What are your strengths?"</strong> — Nêu 2 điểm mạnh, mỗi điểm kèm 1 ví dụ cụ thể: <em>"One of my strengths is problem-solving. For example, in my last job, I found a way to reduce delivery time by 20% by reorganising our schedule."</em></p>
<p><strong>"What is your weakness?"</strong> — Nêu 1 điểm yếu thật nhưng đã có cách khắc phục: <em>"I used to be nervous when speaking in public, so I joined a speaking club. Now I can present to a group of 30 people confidently."</em> Đừng nói <em>"I have no weaknesses"</em> (không ai tin) và đừng nói <em>"I am a perfectionist"</em> (câu trả lời sáo rỗng mà nhà tuyển dụng nghe hàng trăm lần).</p>
<p><strong>"Why do you want to work here?"</strong> — Chứng tỏ bạn đã tìm hiểu về công ty: <em>"I admire your company's work in… and I believe my experience in… would be a good fit."</em> Đừng nói <em>"Because I need a job"</em> dù đó là sự thật.</p>
<p><strong>"Do you have any questions for us?"</strong> — Luôn hỏi 1–2 câu: <em>"What does a typical day in this role look like?"</em> hoặc <em>"What are the opportunities for training and development?"</em> Không hỏi gì là dấu hiệu bạn không quan tâm.</p>
<h2>Từ vựng theo ngành nghề</h2>
<ul>
<li><strong>Kinh doanh – văn phòng:</strong> <em>meeting, deadline, budget, report, colleague, client, invoice, contract, profit, target</em>. Cụm từ: <em>meet a deadline, sign a contract, set a target, send an invoice</em>.</li>
<li><strong>Công nghệ thông tin:</strong> <em>software, hardware, bug, update, password, database, server, user</em>. Cụm từ: <em>fix a bug, update the software, back up data</em>.</li>
<li><strong>Y tế:</strong> <em>patient, doctor, nurse, treatment, medicine, appointment, symptom, diagnosis</em>. Cụm từ: <em>make an appointment, take medicine, run a test</em>.</li>
<li><strong>Du lịch – nhà hàng – khách sạn:</strong> <em>guest, reservation, check-in, check-out, menu, bill, room service</em>. Cụm từ: <em>make a reservation, check in, take an order</em>.</li>
</ul>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Viết email quá thẳng:</strong> <em>"Send me the file."</em> — nghe như ra lệnh. Viết đúng: <em>"Could you please send me the file?"</em> Thêm <em>please</em> và câu hỏi gián tiếp làm email lịch sự hơn rất nhiều.</li>
<li><strong>Dùng <em>Dear Sir</em> khi biết tên người nhận:</strong> nếu biết tên, hãy dùng <em>Dear Mr. Nguyen</em> hoặc <em>Dear Ms. Lan</em>. <em>Dear Sir/Madam</em> chỉ dùng khi không biết tên người nhận.</li>
<li><strong>Nhầm <em>borrow</em> và <em>lend</em> trong công việc:</strong> <em>Can I borrow your laptop?</em> (tôi mượn) / <em>Can you lend me your laptop?</em> (bạn cho tôi mượn).</li>
<li><strong>Nói <em>"I will do it tomorrow"</em> khi không chắc làm được:</strong> trong công việc, hứa mà không làm được tệ hơn nói không làm được. Hãy nói: <em>"I'll try my best to finish it by tomorrow, and I'll update you if there is any delay."</em></li>
<li><strong>Dùng tiếng lóng trong email công việc:</strong> <em>gonna, wanna, yeah, cool</em> không dùng trong email và báo cáo. Dùng <em>going to, want to, yes, good</em>.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Chọn email lịch sự nhất để nhắc khách hàng thanh toán: (a) "Pay now." (b) "Could you please arrange payment at your earliest convenience?" (c) "Why haven't you paid yet?"</summary><p>Đáp án: <strong>(b)</strong>. Câu (b) lịch sự, gián tiếp và chuyên nghiệp. Câu (a) là ra lệnh; câu (c) nghe như trách móc.</p></details>
<details><summary><strong>Câu 2.</strong> Sửa câu sau: "I am agree with your idea, it's very good."</summary><p>Đáp án: <em>I agree with your idea. It's very good.</em> — <em>Agree</em> là động từ, không cần <em>am</em>.</p></details>
<details><summary><strong>Câu 3.</strong> Trong cuộc họp, bạn không đồng ý với đồng nghiệp. Câu nào lịch sự nhất? (a) "You're wrong." (b) "I see your point, but have we considered the cost?" (c) "No."</summary><p>Đáp án: <strong>(b)</strong>. Câu (b) công nhận ý kiến của người khác trước (<em>I see your point</em>) rồi mới nêu quan ngại của mình — cách không đồng ý lịch sự chuẩn trong môi trường công việc.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Muốn luyện tiếng Anh công việc qua trò chơi? Chơi <a href="/tro-choi/workplace-english-arcade.html">Workplace English Arcade — tiếng Anh công việc trình độ B2</a>. Cần chứng chỉ TOEIC để xin việc? Xem <a href="/luyen-thi/toeic.html">luyện thi TOEIC</a> (mục tiêu 600–750 cho đa số vị trí). Muốn luyện viết email tốt hơn? Xem <a href="/ky-nang/viet.html">hướng dẫn luyện viết</a> và dùng <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> để kiểm tra email của bạn trước khi gửi. Chưa vững ngữ pháp nền tảng? Xem <a href="/trinh-do/b1.html">trình độ B1</a> và <a href="/trinh-do/b2.html">trình độ B2</a>.</p>
""") + _eta_html("/cong-viec.html") + _guide_nav(("Trẻ em", "/tre-em.html"), ("Du học", "/du-hoc.html"), None, "Tôi muốn học tiếng Anh cho công việc, bắt đầu từ đâu?"),
    active="/cong-viec.html", eyebrow="Tiếng Anh công việc",
    desc="Tiếng Anh cho công việc theo từng ngành nghề: mẫu email, họp, thuyết trình và phỏng vấn xin việc bằng tiếng Anh.")

add("/du-hoc.html", "Du học", "Chuẩn bị tiếng Anh đi du học",
    guide_sections("""
<p class="lead">Chuẩn bị tiếng Anh đi du học không chỉ là thi lấy chứng chỉ — bạn cần tiếng Anh để viết luận xin học bổng, phỏng vấn visa, nghe giảng trên lớp và sống tự lập ở nước ngoài. Trang này hướng dẫn cả 4 việc đó, theo thứ tự bạn sẽ gặp chúng.</p>
""" + AI_NOTE + """
<h2>Bước 1 — Chọn kỳ thi tiếng Anh phù hợp</h2>
<p>Ba kỳ thi phổ biến nhất cho du học là IELTS, TOEFL iBT và PTE Academic. Kỳ thi nào phù hợp tùy thuộc vào nước bạn tới và yêu cầu của trường:</p>
<ul>
<li><strong><a href="/luyen-thi/ielts.html">IELTS</a>:</strong> phổ biến nhất, được chấp nhận rộng rãi ở Anh, Úc, Canada, châu Âu và nhiều trường tại Mỹ. Thi 4 kỹ năng, thang điểm 1–9, có thi trên giấy và trên máy tính, phần Nói thi trực tiếp với giám khảo.</li>
<li><strong><a href="/luyen-thi/toefl.html">TOEFL iBT</a>:</strong> phổ biến nhất cho du học Mỹ. Từ 21/01/2026 thi theo định dạng mới (khoảng 90 phút làm bài, thang điểm 1–6). Thi hoàn toàn trên máy tính.</li>
<li><strong><a href="/luyen-thi/pte.html">PTE Academic</a>:</strong> thi trên máy tính, chấm bằng AI, kết quả nhanh (thường trong khoảng 2 ngày), thang điểm 10–90. Đặc biệt phổ biến cho du học Úc.</li>
</ul>
<p><strong>Nguyên tắc chọn:</strong> xem yêu cầu của trường bạn nộp đơn trước — trường yêu cầu kỳ thi nào và mức điểm bao nhiêu thì thi kỳ thi đó. Về mức điểm: mỗi trường, mỗi ngành yêu cầu khác nhau — hãy xem trên trang của trường, đừng tin con số lan truyền trên mạng. Nhìn chung, bạn cần trình độ khoảng <a href="/trinh-do/b2.html">B2</a> trở lên để học đại học bằng tiếng Anh, và <a href="/trinh-do/c1.html">C1</a> cho bậc sau đại học.</p>
<h2>Bước 2 — Viết luận xin học bổng và hồ sơ</h2>
<p><strong>Luận xin học (Statement of Purpose / Personal Statement)</strong> là bài viết quan trọng nhất trong hồ sơ du học, sau điểm thi. Cấu trúc chuẩn:</p>
<ul>
<li><strong>Mở đầu (1 đoạn):</strong> một câu chuyện hoặc khoảnh khắc cụ thể khiến bạn chọn ngành này — không mở đầu bằng <em>"I have always wanted to…"</em> (câu mở đầu sáo rỗng mà hội đồng tuyển sinh đọc hàng nghìn lần).</li>
<li><strong>Thân bài (2–3 đoạn):</strong> những gì bạn đã làm (học tập, dự án, công việc) và chúng chuẩn bị cho bạn như thế nào; vì sao bạn chọn trường này, chương trình này (nêu tên giáo sư, phòng lab, khóa học cụ thể — chứng tỏ bạn đã tìm hiểu kỹ).</li>
<li><strong>Kết bài (1 đoạn):</strong> kế hoạch sau khi học xong và đóng góp của bạn — trường muốn biết bạn sẽ làm gì với tấm bằng, không chỉ muốn biết bạn giỏi thế nào.</li>
</ul>
<p><strong>Lỗi phổ biến:</strong> viết chung chung mà không có bằng chứng, kể lại CV bằng câu dài, hoặc sao chép mẫu trên mạng — hội đồng tuyển sinh nhận ra ngay. Hãy viết bằng lời của mình, rồi nhờ người giỏi tiếng Anh sửa giúp; bạn có thể dùng <a href="/cong-cu/viet.html">công cụ chữa bài viết bằng AI</a> để kiểm tra ngữ pháp.</p>
<p><strong>Học bổng toàn phần:</strong> một số chương trình học bổng toàn phần nổi tiếng mà sinh viên Việt Nam hay nộp đơn gồm <a href="https://www.chevening.org/" target="_blank" rel="noopener">Chevening</a> (Anh), Fulbright (Mỹ), Australia Awards (Úc), <a href="https://www.daad.de/en/" target="_blank" rel="noopener">DAAD</a> (Đức), <a href="https://www.studyinkorea.go.kr/en/main.do" target="_blank" rel="noopener">GKS</a> (Hàn Quốc), <a href="https://www.studyinjapan.go.jp/en/" target="_blank" rel="noopener">MEXT</a> (Nhật Bản) và <a href="https://erasmus-plus.ec.europa.eu/opportunities/opportunities-for-individuals/students/erasmus-mundus-joint-masters" target="_blank" rel="noopener">Erasmus Mundus</a> (châu Âu). Mỗi chương trình có điều kiện và hạn nộp riêng, thay đổi theo năm — hãy xem trực tiếp trên trang chính thức của từng chương trình trước khi nộp đơn. Hai chương trình Fulbright (Mỹ) và Australia Awards (Úc) chưa có liên kết đã kiểm chứng ở đây, nên chúng tôi không gắn link — hãy tìm trang chính thức của chương trình để xem điều kiện và hạn nộp mới nhất.</p>
<h2>Bước 3 — Phỏng vấn visa và phỏng vấn trường</h2>
<p><strong>Phỏng vấn visa</strong> thường ngắn (3–5 phút) và tập trung vào 3 câu hỏi: Bạn đi học cái gì, ở đâu? Ai trả tiền? Bạn có quay về sau khi học xong không? Trả lời ngắn gọn, trung thực, nhất quán với hồ sơ đã nộp. Đừng học thuộc lòng câu trả lời — viên chức lãnh sự nhận ra ngay. Chuẩn bị bằng cách trả lời các câu hỏi sau bằng tiếng Anh, mỗi câu 2–3 câu trả lời:</p>
<ul>
<li><em>Why did you choose this university?</em> — Nêu lý do cụ thể về trường và chương trình, không nói chung chung.</li>
<li><em>How will you pay for your studies?</em> — Nêu rõ nguồn tài chính (gia đình, học bổng, tiết kiệm) với con số nếu có.</li>
<li><em>What will you do after graduation?</em> — Nêu kế hoạch quay về Việt Nam làm việc (đây là câu hỏi quan trọng nhất với nhiều nước).</li>
</ul>
<p>Luyện phỏng vấn: xem kỹ thuật trả lời ở <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a> và chơi <a href="/tro-choi/speaking-booth.html">Speaking Booth — luyện nói theo chủ đề</a>.</p>
<h2>Bước 4 — Tiếng Anh cho đời sống ở nước ngoài</h2>
<p>Thi xong chưa phải là xong — bạn còn cần tiếng Anh để sống. Những tình huống bạn sẽ gặp trong tuần đầu tiên:</p>
<ul>
<li><strong>Nhà ở:</strong> <em>I'd like to rent a room near the university. Is the rent per week or per month? Does it include electricity and internet?</em> — Học từ: <em>rent, deposit, landlord, lease, bills included</em>.</li>
<li><strong>Trường học:</strong> <em>Excuse me, where is the lecture hall? Could you explain the assignment again, please?</em> — Học từ: <em>lecture, seminar, tutorial, assignment, deadline, plagiarism</em> (đạo văn — tuyệt đối tránh).</li>
<li><strong>Giao tiếp hằng ngày:</strong> <em>Could I have a coffee, please? How much is it? Can I pay by card?</em> — Học cách nói lịch sự: <em>Could I…? / Would you mind…? / Excuse me…</em></li>
</ul>
<p><strong>Lưu ý:</strong> ở nước ngoài, sinh viên được kỳ vọng phát biểu trong lớp và làm việc nhóm — khác với lớp học ở Việt Nam. Luyện trước khi đi: xem <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>.</p>
<h2>Lỗi thường gặp</h2>
<ul>
<li><strong>Chỉ luyện thi, không luyện tiếng Anh thật:</strong> đạt IELTS 7.0 nhưng không nghe được bài giảng, không viết được email cho giáo viên — vì luyện thi chỉ dạy làm bài thi. Hãy luyện cả tiếng Anh đời sống: xem phim, đọc báo, nói chuyện với người bản xứ.</li>
<li><strong>Chọn trường theo "nghe nói" thay vì yêu cầu chính thức:</strong> mỗi trường có yêu cầu điểm và hồ sơ riêng. Xem trực tiếp trên trang của trường — đừng tin con số lan truyền.</li>
<li><strong>Viết luận xin học bổng bằng mẫu có sẵn trên mạng:</strong> hội đồng tuyển sinh đọc hàng nghìn bài mỗi năm và nhận ra mẫu sao chép ngay. Viết bằng câu chuyện thật của bạn.</li>
<li><strong>Không chuẩn bị câu trả lời phỏng vấn visa:</strong> trả lời ấp úng, mâu thuẫn với hồ sơ là lý do trượt visa phổ biến. Luyện trả lời 4 câu hỏi ở mục Bước 3 cho tới khi trôi chảy.</li>
</ul>
<h2>Luyện tập nhanh</h2>
<details><summary><strong>Câu 1.</strong> Bạn muốn hỏi đường tới thư viện trong trường đại học. Câu nào lịch sự nhất? (a) "Where is the library?" (b) "Excuse me, could you tell me where the library is, please?" (c) "Library where?"</summary><p>Đáp án: <strong>(b)</strong>. Câu (b) có <em>Excuse me</em>, câu hỏi gián tiếp (<em>could you tell me where…</em>) và <em>please</em> — cách hỏi lịch sự chuẩn. Câu (a) không sai nhưng kém lịch sự hơn; câu (c) sai ngữ pháp.</p></details>
<details><summary><strong>Câu 2.</strong> Sửa câu sau (viết email cho giáo viên): "Hi, I want more time for my assignment!!!"</summary><p>Đáp án: <em>Dear Professor Smith, I am writing to ask if I could please have an extension for my assignment, as I have been unwell this week. Thank you for your understanding. Best regards, Lan.</em> — Email học thuật cần chào hỏi trang trọng, câu hỏi gián tiếp, lý do rõ ràng và không dùng dấu chấm than.</p></details>
<details><summary><strong>Câu 3.</strong> Trả lời câu hỏi phỏng vấn visa: "What will you do after graduation?" — Câu trả lời nào tốt nhất? (a) "I don't know." (b) "I will stay and find a job." (c) "I plan to return to Vietnam and work as a software engineer, because the tech industry there is growing fast and I want to contribute to it."</summary><p>Đáp án: <strong>(c)</strong>. Câu trả lời tốt nêu kế hoạch cụ thể (quay về Việt Nam, làm nghề gì) và lý do (ngành công nghệ đang phát triển, muốn đóng góp). Câu (a) và (b) đều yếu — (b) còn có thể gây nghi ngờ về ý định ở lại.</p></details>
<h2>Học tiếp ở đâu?</h2>
<p>Chọn kỳ thi: <a href="/luyen-thi/ielts.html">luyện thi IELTS</a>, <a href="/luyen-thi/toefl.html">luyện thi TOEFL iBT</a>, <a href="/luyen-thi/pte.html">luyện thi PTE Academic</a>. Học theo sách: <a href="/sach/mindset-for-ielts.html">hướng dẫn học với sách Mindset for IELTS</a> (tới band 7.5). Nâng trình độ nền tảng: <a href="/trinh-do/b2.html">trình độ B2</a> và <a href="/trinh-do/c1.html">trình độ C1</a>. Luyện nói và viết: <a href="/ky-nang/noi.html">hướng dẫn luyện nói</a>, <a href="/ky-nang/viet.html">hướng dẫn luyện viết</a>. Sau khi đi du học, bạn vẫn cần <a href="/cong-viec.html">tiếng Anh công việc</a> — học trước cũng không thừa.</p>
""") + _eta_html("/du-hoc.html") + _guide_nav(("Tiếng Anh công việc", "/cong-viec.html"), None, None, "Tôi muốn đi du học, cần chuẩn bị tiếng Anh như thế nào?"),
    active="/du-hoc.html", eyebrow="Du học",
    desc="Chuẩn bị tiếng Anh đi du học: thi IELTS/TOEFL/PTE, học bổng toàn phần, phỏng vấn visa và đời sống ở nước ngoài.")

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
_TRO_CHUYEN_AI_EXAMPLES = [
    "Phân biệt “a” và “the” như thế nào?",
    "Học từ vựng thế nào cho nhớ lâu?",
    "IELTS Speaking Part 1 thường hỏi gì?",
    "Cho tôi lộ trình học tiếng Anh trình độ A1.",
]
_TRO_CHUYEN_AI_CHIPS = " ".join(
    f'<a class="de-chat-chip" style="display:inline-block;text-decoration:none" href="/tro-chuyen-ai.html?q={quote(q, safe="")}">{q}</a>'
    for q in _TRO_CHUYEN_AI_EXAMPLES)
add("/tro-chuyen-ai.html", "Trò chuyện AI", "Trò chuyện AI",
    f"""
<p class="lead">Hỏi bất cứ gì về tiếng Anh — ngữ pháp, từ vựng, phát âm, luyện thi, lộ trình học. AI trả lời bằng tiếng Việt.</p>
<p><span class="badge">AI, chưa duyệt</span> Mọi câu trả lời do AI soạn, chưa được giáo viên duyệt — hãy đối chiếu với sách và giáo viên của bạn.</p>
<section class="section">
<div class="section-head"><h2>AI có thể giúp gì</h2></div>
<ul>
<li>Giải thích ngữ pháp bằng tiếng Việt, kèm ví dụ song ngữ.</li>
<li>Giải nghĩa từ vựng, phân biệt từ gần nghĩa, gợi ý cách dùng đúng.</li>
<li>Gợi ý lộ trình học theo trình độ (A1–C2) và mục tiêu của bạn.</li>
<li>Mẹo làm bài thi IELTS, TOEIC, PTE — và chữa bài viết ngắn của bạn.</li>
</ul>
<p><strong>Thử một câu hỏi mẫu — bấm để gửi ngay:</strong></p>
<p class="de-chat-suggest">{_TRO_CHUYEN_AI_CHIPS}</p>
</section>
<section class="section">
<div id="deChatPage"><noscript><p>Trò chuyện AI cần bật JavaScript để hiển thị. Bạn vẫn có thể xem các mục khác của trang, hoặc bật JavaScript rồi tải lại trang.</p></noscript></div>
</section>
<p class="muted">Chat dùng cùng hệ thống với khung chat góc màn hình. Nếu tính năng chưa sẵn sàng (chưa có key hoặc đã hết lượt miễn phí trong ngày), khung chat sẽ báo rõ — bạn vẫn có thể dùng các mục khác của trang trong lúc chờ.</p>
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
  <p class="muted" id="vocabCount">0/100 ký tự</p>
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
  var count = document.getElementById('vocabCount');
  input.addEventListener('input', function () {
    if (input.value.length > 100) { input.value = input.value.slice(0, 100); }
    count.textContent = input.value.length + '/100 ký tự' + (input.value.length >= 100 ? ' — đã đạt giới hạn 100 ký tự, hãy tra từ hoặc cụm từ ngắn hơn.' : '');
  });
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
<button type="button" class="btn ghost" id="copyWriting" hidden>Sao chép kết quả</button>
</section>
<p class="muted">Nếu công cụ chưa sẵn sàng, trang sẽ báo “đang được chuẩn bị” — bạn thử lại sau.</p>
<script>
(function () {
  var form = document.getElementById('writingForm');
  var input = document.getElementById('writingText');
  var out = document.getElementById('writingResult');
  var count = document.getElementById('writingCount');
  var copyBtn = document.getElementById('copyWriting');
  copyBtn.addEventListener('click', function () {
    var text = out.innerText || out.textContent || '';
    function done() { copyBtn.textContent = 'Đã sao chép!'; setTimeout(function () { copyBtn.textContent = 'Sao chép kết quả'; }, 2000); }
    function fallbackCopy() {
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { copyBtn.textContent = 'Không sao chép được'; }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(); });
    } else { fallbackCopy(); }
  });
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
    copyBtn.hidden = true;
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
          copyBtn.hidden = false;
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
<section class="section">
<div class="section-head"><h2>Chọn sách nào?</h2><p class="section-sub">Chọn theo trình độ và mục tiêu của bạn.</p></div>
<ul>
<li><strong>Học sinh lớp 3–12, học theo chương trình trên lớp:</strong> <a href="/sach/global-success.html">Global Success</a> — sách giáo khoa tiếng Anh theo chương trình GDPT 2018.</li>
<li><strong>Người mới bắt đầu đến C1, muốn học tiếng Anh Mỹ tổng quát:</strong> <a href="/sach/american-english-file.html">American English File</a> — giáo trình của Oxford, từ A1 đến C1.</li>
<li><strong>Mục tiêu thi TOEIC (Listening &amp; Reading):</strong> <a href="/sach/barrons-toeic.html">Barron's TOEIC</a> — luyện thi TOEIC với bộ sách của Lin Lougheed.</li>
<li><strong>Mục tiêu thi IELTS Academic, tới band 7.5:</strong> <a href="/sach/mindset-for-ielts.html">Mindset for IELTS</a> — theo từng cấp độ, từ Foundation đến Level 3.</li>
</ul>
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
<p>Mỗi lớp có sách học sinh riêng. Lớp 3 và lớp 6 chia thành hai tập, một tập cho mỗi học kỳ (đã kiểm chứng — xem mục "Nguồn đã kiểm chứng"). Số unit đã kiểm chứng được:</p>
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
<div class="table-wrap"><table><thead><tr><th>Buổi</th><th>Nội dung</th><th>Thời gian</th></tr></thead><tbody><tr><td>Thứ 2</td><td>Buổi 1: mở đầu + từ vựng + phát âm + ngữ pháp</td><td>40 phút</td></tr><tr><td>Thứ 4</td><td>Buổi 2: đọc hiểu + nghe</td><td>40 phút</td></tr><tr><td>Thứ 6</td><td>Buổi 3: nói + viết</td><td>40 phút</td></tr><tr><td>Chủ nhật</td><td>Buổi 4: ôn lại + dự án + Sách bài tập</td><td>45 phút</td></tr></tbody></table></div>
<p><strong>Tuần có phần Review (sau mỗi 3–5 unit tùy lớp):</strong></p>
<div class="table-wrap"><table><thead><tr><th>Buổi</th><th>Nội dung</th><th>Thời gian</th></tr></thead><tbody><tr><td>Thứ 2</td><td>Làm toàn bộ phần Review, tính giờ như kiểm tra thật</td><td>40 phút</td></tr><tr><td>Thứ 4</td><td>Chữa lỗi: ôn lại chỉ những unit có câu sai, làm lại các câu sai</td><td>40 phút</td></tr><tr><td>Thứ 6</td><td>Ôn từ vựng của cả nhóm unit bằng thẻ học; viết lại một đoạn văn cũ cho hay hơn</td><td>30 phút</td></tr><tr><td>Chủ nhật</td><td>Nghỉ hoặc nghe lại audio của các unit đã học như nghe thụ động</td><td>Tùy ý</td></tr></tbody></table></div>
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
<ul><li>Bài viết chính thức của Nhà xuất bản Giáo dục Việt Nam: &quot;Global Success: Bộ sách giáo khoa tiếng Anh của người Việt Nam&quot; — <a href="https://nxbgd.vn/bai-viet/global-success-bo-sach-giao-khoa-tieng-anh-cua-nguoi-viet-nam" target="_blank" rel="noopener">https://nxbgd.vn/bai-viet/global-success-bo-sach-giao-khoa-tieng-anh-cua-nguoi-viet-nam</a> — đã mở và đọc trực tiếp ngày 23/11/2026. Xác nhận: bộ sách từ lớp 1 đến lớp 12; Tổng chủ biên GS.TS. Hoàng Văn Vân, tác giả 100% người Việt Nam; hợp tác Macmillan Education (tiểu học) và Pearson Education (THCS, THPT); hệ thống học liệu tại hoclieu.vn; Sách Mềm tại sachmem.vn; cửa hàng trực tuyến edubook.com.vn.</li><li>Trang chủ Học Liệu — <a href="https://hoclieu.vn/" target="_blank" rel="noopener">https://hoclieu.vn/</a> — đã mở trực tiếp ngày 23/11/2026, trang tải được.</li><li>Trang chủ Sách Mềm — <a href="https://sachmem.vn/" target="_blank" rel="noopener">https://sachmem.vn/</a> — đã mở trực tiếp ngày 23/11/2026; xác nhận lộ trình lớp 1–12 và các học liệu đi kèm.</li><li>Hội thảo giới thiệu sách giáo khoa lớp 3 (Sở GD&amp;ĐT Hải Phòng): <a href="http://anhp.vn/hoi-thao-gioi-thieu-sach-giao-khoa-lop-3-d46091.html" target="_blank" rel="noopener">http://anhp.vn/hoi-thao-gioi-thieu-sach-giao-khoa-lop-3-d46091.html</a> — xác nhận Tiếng Anh 3 Global Success (Hoàng Văn Vân) nằm trong danh mục sách lớp 3 được phê duyệt theo Quyết định 438 ngày 28/01/2022, dùng từ năm học 2022–2023; bộ sách theo khung năng lực ngoại ngữ 6 bậc và chương trình GDPT 2018.</li><li>Tổng quan sách Tiếng Anh 3 Global Success — <a href="https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-3" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-3</a> — xác nhận lớp 3 có 20 unit, hai tập, Review và Fun time sau mỗi 5 unit, cấu trúc mỗi unit gồm Getting Started, Lesson 1–3.</li><li>Tổng quan sách Tiếng Anh 6 Global Success — <a href="https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-6" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-6</a> — xác nhận lớp 6 có 12 unit, hai tập, tác giả và đối tác Pearson.</li><li>Tổng quan sách Tiếng Anh 8 Global Success — <a href="https://vus.edu.vn/blog-vus/tieng-anh-8?leadcdpid=sitemap" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/tieng-anh-8?leadcdpid=sitemap</a> — xác nhận lớp 8 có 12 unit, 4 phần Review, Glossary; audio nằm trên bản điện tử chính thức (hoclieu.vn và hanhtrangso.nxbgd.vn).</li><li>Tổng quan sách Tiếng Anh 10 Global Success — <a href="https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-10" target="_blank" rel="noopener">https://vus.edu.vn/blog-vus/sach-tieng-anh-lop-10</a> — xác nhận lớp 10 có 10 unit, 4 phần Review, Book Map, Glossary, các phần Communication and Culture/CLIL và Looking Back &amp; Project.</li><li>Danh mục unit lớp 7, 8, 9, 12 — <a href="https://www.studywithping.com/ngu-phap" target="_blank" rel="noopener">https://www.studywithping.com/ngu-phap</a> — xác nhận lớp 7, 8, 9 mỗi lớp 12 unit, lớp 12 có 10 unit; lớp 7 có Review sau Unit 3, 6, 9, 12.</li></ul>
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
<div class="table-wrap"><table><thead><tr><th>Cuốn</th><th>Trình độ ước chừng</th><th>Phù hợp với bạn nếu…</th></tr></thead><tbody><tr><td>Starter</td><td>A1</td><td>Mới bắt đầu gần như từ đầu, cần học bảng chữ cái, số đếm, câu chào hỏi và động từ <em>be</em></td></tr><tr><td>Level 1</td><td>A1–A2</td><td>Đã biết những câu giao tiếp rất cơ bản, muốn nói được về bản thân, gia đình, công việc hằng ngày</td></tr><tr><td>Level 2</td><td>A2–B1</td><td>Đã giao tiếp được ở mức đơn giản, muốn kể chuyện quá khứ, nói về kế hoạch tương lai</td></tr><tr><td>Level 3</td><td>B1–B2</td><td>Đã giao tiếp khá, muốn thảo luận ý kiến, tranh luận nhẹ và đọc–nghe các chủ đề đời sống, xã hội</td></tr><tr><td>Level 4</td><td>B2</td><td>Đã khá vững, muốn diễn đạt tinh tế hơn, dùng từ nối và cấu trúc phức tạp một cách tự nhiên</td></tr><tr><td>Level 5</td><td>C1</td><td>Đã giỏi, muốn dùng tiếng Anh linh hoạt, chính xác ở mức nâng cao trong học tập và công việc</td></tr></tbody></table></div>
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
<div class="table-wrap"><table><thead><tr><th>Buổi</th><th>Việc làm</th></tr></thead><tbody><tr><td>Thứ 2</td><td>Học bài A của File mới theo 6 bước ở trên</td></tr><tr><td>Thứ 3</td><td>Học bài B của File mới theo 6 bước ở trên</td></tr><tr><td>Thứ 4</td><td>Học bài C của File mới; ôn lại từ vựng bài A và B bằng cách đặt câu mới</td></tr><tr><td>Thứ 5</td><td>Practical English + Video Listening của File đó (nghe 2–3 lần: lần 1 hiểu ý chính, lần 2 nghe chi tiết, lần 3 nói theo)</td></tr><tr><td>Thứ 6</td><td>Làm Workbook của cả File; viết một đoạn ngắn (5–8 câu) về chủ đề của File, dùng từ vựng và ngữ pháp vừa học</td></tr><tr><td>Thứ 7</td><td>Nghỉ hoặc ôn nhẹ: nghe lại các bài nghe trong tuần, đọc lại trang &quot;lỗi của tôi&quot;</td></tr><tr><td>Chủ nhật</td><td>Nghỉ. Nếu đang ở cuối File chẵn (File 2, 4, 6…), dùng buổi này làm Review &amp; Check thay cho nghỉ</td></tr></tbody></table></div>
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
<p><strong>Tuần 4–5 — Ôn kỹ năng Đọc.</strong> Mỗi tuần 3 buổi Đọc và 2 buổi từ vựng. Buổi Đọc: ôn Part 5 (ngữ pháp và từ vựng trong câu), Part 6 (điền đoạn văn), Part 7 (đọc hiểu). Luyện thói quen đọc câu hỏi trước, gạch ý chính của đoạn văn, và đặt giới hạn thời gian cho mỗi nhóm câu. Tiếp tục mỗi buổi 1 bài từ vựng; tới cuối tuần 5 bạn đã học khoảng 13 bài (156 từ).</p>
<p><strong>Tuần 6 — Luyện đề lần 1 và sửa lỗi hệ thống.</strong> Làm 2 đề thi thử đầy đủ, mỗi đề vào một ngày khác nhau, đúng giờ thi thật. Sau mỗi đề, dành một buổi chỉ để chữa: phân loại mọi câu sai theo dạng bài và nguyên nhân (thiếu từ, nghe sót, hết giờ, đọc sai ý). Cập nhật sổ lỗi và quay lại ôn đúng dạng bài yếu nhất trong cuốn tổng hợp. Bắt đầu nhịp học từ vựng tăng tốc để kịp hoàn thành 50 bài: mỗi ngày học nhanh 3 bài (36 từ, khoảng 45 phút, chỉ học nghĩa + 1 câu ví dụ mỗi từ) ngoài các buổi làm đề — tới cuối tuần 6 bạn đã học 34/50 bài.</p>
<p><strong>Tuần 7 — Luyện đề lần 2 và tăng tốc.</strong> Làm 2 đề thi thử nữa. Lần này đặt mục tiêu cụ thể cho từng phần: ví dụ, phần Đọc phải xong Part 5 và Part 6 trong khoảng thời gian bạn tự đặt ra để còn đủ giờ cho Part 7; phần Nghe không dừng lại suy nghĩ ở câu đã qua. Giữ nhịp học nhanh 3 bài từ vựng mỗi ngày: 16 bài còn lại sau tuần 6 xong trong khoảng 6 ngày, tới cuối tuần này bạn hoàn thành đủ 50 bài (600 từ). Ưu tiên chủ đề của dạng bài bạn hay sai.</p>
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
<div class="table-wrap"><table><thead><tr><th>Cấp độ</th><th>Trình độ (CEFR)</th><th>Band IELTS hướng tới</th></tr></thead><tbody><tr><td>Foundation</td><td>A2</td><td>Làm quen với IELTS; các nguồn thứ cấp ghi band mục tiêu khoảng 4.5 (xem mục &quot;Chưa kiểm chứng được&quot;)</td></tr><tr><td>Level 1</td><td>B1</td><td>5.5</td></tr><tr><td>Level 2</td><td>B1–B2</td><td>6.5</td></tr><tr><td>Level 3</td><td>B2–C1 (theo các nguồn thứ cấp)</td><td>7.5</td></tr></tbody></table></div>
<p>Cách chọn nhanh:</p>
<ul><li><strong>Bạn mới bắt đầu, vốn từ còn ít, chưa từng làm bài IELTS:</strong> bắt đầu ở Foundation. Sách này dạy theo trình tự tuyến tính, vừa nâng trình độ tiếng Anh chung vừa giới thiệu dần các yếu tố của bài thi.</li><li><strong>Bạn đã giao tiếp cơ bản được, đọc hiểu đoạn văn đơn giản, muốn đạt band 5.5:</strong> bắt đầu ở Level 1.</li><li><strong>Bạn đã ở khoảng band 5.5 và muốn lên 6.5:</strong> bắt đầu ở Level 2.</li><li><strong>Bạn đã ở khoảng band 6.5 và muốn lên 7.5:</strong> bắt đầu ở Level 3.</li></ul>
<p>Nếu bạn không chắc mình ở đâu, hãy làm một bài thi thử IELTS chính thức (hoặc bài kiểm tra trình độ của một trung tâm uy tín) trước khi mua sách, rồi chọn cấp độ thấp hơn band mục tiêu của bạn một nấc. Học sách quá khó so với trình độ chỉ làm bạn nản; học sách quá dễ thì bạn không tiến bộ.</p>
<p>Một số tác giả đã kiểm chứng được: Foundation gồm Greg Archer, Lucy Passmore và Jishan Uddin (một số bản ghi ISBN viết &quot;Lucy Pasmore&quot;); Level 1 gồm Peter Crosthwaite, Susan Hutchison, Claire Wijayatilake và Natasha De Souza. Tác giả của Level 2 và Level 3 chưa được kiểm chứng từ nguồn chính thức trong lần nghiên cứu này — xem mục &quot;Chưa kiểm chứng được&quot;.</p>
<h2>Cấu trúc sách</h2>
<p>Mỗi cấp độ có một cuốn Student&#x27;s Book (sách học sinh) kèm phần học trực tuyến (Digital Pack / online modules). Cấu trúc chung, theo tài liệu giới thiệu của chính Cambridge:</p>
<ul><li><strong>Foundation: 10 unit theo chủ đề</strong>, sắp xếp theo kỹ năng, tương đương 60–90 giờ học trên lớp cho một cấp độ. Sách có đáp án (answer key) và bản ghi âm bài nghe (listening scripts) ở cuối sách.</li><li><strong>Level 1: 8 unit theo chủ đề</strong>, sắp xếp theo kỹ năng, tương đương 60–90 giờ học cho một cấp độ.</li><li><strong>Level 2 và 3: 8 unit theo chủ đề theo các nguồn thứ cấp</strong> — con số này chưa được kiểm chứng trực tiếp từ tài liệu chính thức của Cambridge (xem mục "Chưa kiểm chứng được" ở cuối bài). Ngoài số unit, cấu trúc hai cấp độ này giống Level 1: sắp xếp theo kỹ năng, tương đương 60–90 giờ học cho một cấp độ.</li><li><strong>Mỗi unit gồm 4 phần kỹ năng:</strong> Reading, Writing, Listening và Speaking, kèm phần từ vựng và ngữ pháp lồng trong quá trình luyện kỹ năng. Mỗi bài học đều ghi rõ mục tiêu cần đạt (&quot;In this unit you will learn how to…&quot;).</li><li><strong>Học trực tuyến đi kèm:</strong> các module luyện từng kỹ năng (Reading, Writing, Listening, Speaking, cộng thêm Grammar and Vocabulary), mỗi kỹ năng khoảng 8 giờ luyện tập cho một cấp độ; module Academic Study Skills (kỹ năng học thuật, khoảng 6 giờ) giúp chuẩn bị cho việc học đại học bằng tiếng Anh; và các bài thi thử trực tuyến (ở bản 2017 gọi là Testbank; ở bản 2023 gọi là Digital Pack, truy cập bằng mã code trong sách qua nền tảng Cambridge One).</li><li><strong>Teacher&#x27;s Book:</strong> có sách giáo viên riêng cho từng cấp độ, dành cho giáo viên đứng lớp — người tự học không cần mua cuốn này.</li></ul>
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

# ---------------- Trò chơi & Công cụ (batch 2) ----------------
# 18 trò chơi/công cụ HTML độc lập do David gửi (file gốc trong
# ~/workspace/user-files-inspect/artifacts-html/), đã dọn link claude.ai
# bằng adopt_artifacts.py và đặt tại tro-choi/<slug>.html. Trang hub này
# là trang duy nhất do _build.py sinh ra trong mục tro-choi; các file trò
# chơi giữ nguyên giao diện riêng, không ép theo design system navy.
TRO_CHOI = [
    ("toeic-arcade", "TOEIC Arcade", "exam",
     "Luyện TOEIC Listening & Reading dạng trò chơi, chủ đề công việc và đời sống."),
    ("pte-arcade", "PTE Arcade", "exam",
     "Trò chơi luyện PTE Academic: đọc, nghe, ngữ pháp và từ vựng."),
    ("workplace-english-arcade", "Workplace English Arcade", "work",
     "Trò chơi tiếng Anh công việc trình độ B2: từ vựng, ngữ pháp, 4 kỹ năng và bài thi thử Linguaskill Business."),
    ("english-level-check", "English Level Check", "level",
     "Bài kiểm tra trình độ tiếng Anh (A1–C2) rồi gợi ý công cụ luyện phù hợp."),
    ("level-map", "Level Map", "level",
     "Bản đồ tất cả công cụ luyện tập theo trình độ — chưa biết mình ở đâu thì bắt đầu từ đây."),
    ("band-climb", "Band Climb", "level",
     "Luyện IELTS theo band hiện tại của bạn: ngữ pháp, nghe, đọc — bấm giờ như thi thật."),
    ("speaking-booth", "Speaking Booth", "skill",
     "Luyện nói: gõ lại những gì bạn nói theo gợi ý IELTS, TOEIC, PTE."),
    ("starter-quest", "Starter Quest", "kids",
     "Trò chơi từ vựng và ngữ pháp cho người mới bắt đầu: chào hỏi, số đếm, gia đình, động từ hằng ngày."),
    ("intermediate-quest", "Intermediate Quest", "level",
     "Luyện B1: ngữ pháp, từ vựng, đọc, nghe, viết theo từng unit."),
    ("grade-4-quest", "Grade 4 Quest", "kids",
     "Trò chơi từ vựng, ngữ pháp theo sách Global Success lớp 4 (20 unit)."),
    ("grade-9-quest", "Grade 9 Quest", "kids",
     "Trò chơi từ vựng, ngữ pháp theo từng unit sách lớp 9."),
    ("grade-10-quest", "Grade 10 Quest", "kids",
     "Trò chơi từ vựng, ngữ pháp theo từng unit sách lớp 10."),
    ("teacher-quest", "Teacher Quest", "tool",
     "Trò chơi ngữ pháp nâng cao cho giáo viên: thì hoàn thành, câu điều kiện, mệnh đề quan hệ."),
    ("game-room-lobby", "Game Room Lobby", "tool",
     "Sảnh trò chơi: chọn lớp 4, 9 hoặc 10 để vào Grade Quest."),
    ("ai-workbench", "AI Workbench", "tool",
     "Học cách dùng AI (ChatGPT, Claude, Gemini…) để học và dạy tiếng Anh: 15 bài học ngắn, thư viện prompt mẫu."),
    ("efec-helper", "EFEC Helper", "work",
     "Tiếng Anh cho điều dưỡng: chào hỏi bệnh nhân, giao tiếp trong bệnh viện — giải thích bằng tiếng Việt."),
    ("open-shelf", "Open Shelf", "book",
     "Kệ sách mở: đọc sách tiếng Anh miễn phí từ Project Gutenberg, LibriVox, Archive.org — lưu sách bạn đang đọc."),
    ("bible-english-adventure", "Bible English Adventure", "book",
     "Học tiếng Anh sơ cấp qua các đoạn Kinh Thánh ngắn: từ vựng, ngữ pháp, viết."),
    ("flashcards", "Flashcards — Ôn từ vựng", "tool",
     "Ôn từ vựng các bài học A1–B2 bằng thẻ lật: lật thẻ xem nghĩa, đánh dấu đã biết hay chưa biết, ôn lại từ chưa biết."),
    ("toeic-mini-mock", "TOEIC Mini-Mock", "exam",
     "Đề thi thử TOEIC mini 20 câu, 20 phút: ngữ pháp, hội thoại và cụm từ — chép từ ngân hàng câu hỏi TOEIC Arcade."),
]
add("/tro-choi/index.html", "Trò chơi & Công cụ", "Trò chơi & Công cụ",
    """
<p class="lead">Học tiếng Anh bằng trò chơi và công cụ tương tác — miễn phí, chơi ngay trên trình duyệt, tiến độ được lưu trên máy của bạn.</p>
<p class="muted">Mọi trò chơi đều chơi đầy đủ ngay trên trình duyệt, không cần đăng nhập — tiến độ được lưu trên máy của bạn.</p>
<section class="section">
<div class="cards">
""" + "".join(
        f'<article class="card card-{kind}">{card_icon(kind)}<h2><a href="/tro-choi/{slug}.html">{name}</a></h2><p>{desc}</p></article>'
        for slug, name, kind, desc in TRO_CHOI
    ) + """
</div>
</section>
<p>Chưa biết mình ở đâu? <a href="/tro-choi/english-level-check.html">Làm bài kiểm tra trình độ →</a> · <a href="/tro-choi/level-map.html">Xem bản đồ công cụ theo trình độ →</a></p>
""", active="/tro-choi/", eyebrow="Trò chơi & Công cụ",
    desc="Trò chơi và công cụ học tiếng Anh miễn phí: luyện TOEIC, PTE, IELTS, kiểm tra trình độ, trò chơi theo lớp 4, 9, 10 và công cụ cho giáo viên.")

# ---------------- Quyền riêng tư ----------------
add("/quyen-rieng-tu.html", "Quyền riêng tư", "Quyền riêng tư",
    f"""
<p class="lead">Trang này giải thích David English thu thập dữ liệu gì, dùng để làm gì, và cách bạn kiểm soát dữ liệu của mình.</p>
<section class="section">
<div class="section-head"><h2>Chúng tôi dùng Google Analytics (GA4)</h2></div>
<p>David English dùng Google Analytics 4 (GA4) — công cụ phân tích của Google — để biết nội dung nào hữu ích: ví dụ trang nào được đọc nhiều, bài học nào được mở tới cuối. GA4 chỉ chạy khi bạn bấm “Đồng ý” trên banner cookie. Nếu bạn bấm “Từ chối” hoặc chưa chọn gì, GA4 không chạy và không thu thập gì cả. Theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15, chúng tôi chỉ thu thập dữ liệu phân tích khi bạn đồng ý rõ ràng. Mã đo lường (Measurement ID) của trang là {GA4_ID}.</p>
</section>
<section class="section section-alt">
<div class="section-head"><h2>GA4 thu thập gì</h2></div>
<p>Khi bạn đã đồng ý, GA4 thu thập: trang bạn xem, thời gian xem, loại thiết bị và trình duyệt bạn dùng, và khu vực chung (quốc gia/thành phố) suy ra từ địa chỉ IP. Địa chỉ IP của bạn được Google ẩn danh mặc định — chúng tôi không thấy địa chỉ IP đầy đủ của bạn.</p>
<p>GA4 không thu thập tên, email, số điện thoại hay bất kỳ thông tin nào cho biết bạn là ai. Trang này không dùng cookie quảng cáo và không bán dữ liệu cho bất kỳ ai.</p>
</section>
<section class="section">
<div class="section-head"><h2>Dùng để làm gì</h2></div>
<p>Dữ liệu phân tích chỉ dùng để cải thiện nội dung: viết thêm bài học ở chủ đề được đọc nhiều, sửa bài học ít người đọc tới cuối. Dữ liệu được xem ở dạng tổng hợp (ví dụ: “500 lượt xem trang này trong tháng”), không theo dõi từng người.</p>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Lưu trữ bao lâu</h2></div>
<p>Dữ liệu phân tích trong GA4 được lưu tối đa 14 tháng rồi tự xóa. Cookie GA4 trên trình duyệt của bạn (_ga) có hạn tối đa 2 năm, nhưng sẽ bị xóa ngay khi bạn rút lại sự đồng ý (xem bên dưới).</p>
</section>
<section class="section">
<div class="section-head"><h2>Trò chuyện AI và chữa bài viết: dữ liệu gửi cho nhà cung cấp AI</h2></div>
<p>Khi bạn dùng Trò chuyện AI, Tra từ bằng AI, Chữa bài viết bằng AI hoặc bài kiểm tra English Level Check, nội dung bạn gửi được chuyển tới nhà cung cấp AI để tạo câu trả lời: câu hỏi của bạn, đoạn văn bạn gửi để chữa, và tối đa 2 lượt trao đổi gần nhất (lịch sử trò chuyện) để AI trả lời đúng ngữ cảnh. Bài viết gửi để chấm có thể dài tới 3.000 ký tự.</p>
<p>Nhà cung cấp là <strong>Groq</strong> (chính) và <strong>Google Gemini</strong> (dự phòng khi Groq hết lượt miễn phí). Dữ liệu chỉ dùng để tạo câu trả lời hoặc chấm bài — không dùng để quảng cáo. Cách các nhà cung cấp xử lý và lưu dữ liệu này tuân theo chính sách riêng của họ (<a href="https://groq.com/privacy-policy/">Groq</a>, <a href="https://policies.google.com/privacy">Google</a>), không thuộc chính sách này.</p>
<p>Để chống lạm dụng, địa chỉ IP của bạn được xử lý (băm một chiều, không lưu địa chỉ gốc) nhằm giới hạn lượt dùng: tối đa khoảng 10 tin/giờ và 50 tin/ngày cho mỗi IP. Giới hạn này là xấp xỉ — máy chủ chạy nhiều phiên bản song song, mỗi phiên bản đếm riêng, nên một IP có thể vượt nhẹ giới hạn khi các yêu cầu rơi vào nhiều phiên bản khác nhau.</p>
<p>Trang không ghi lại (không log) câu hỏi hay bài viết của bạn trên máy chủ của mình. Mọi câu trả lời của AI đều ghi rõ “AI, chưa duyệt” — chưa được giáo viên duyệt.</p>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Rút lại sự đồng ý và xóa dữ liệu</h2></div>
<p>Bạn có thể rút lại sự đồng ý bất cứ lúc nào: bấm liên kết “Cài đặt cookie” ở chân trang, rồi bấm “Từ chối”. Thao tác này xóa cookie Google Analytics khỏi trình duyệt của bạn và dừng mọi thu thập tiếp theo ngay lập tức. Dữ liệu đã gửi trước đó được ẩn danh và tự xóa sau tối đa 14 tháng.</p>
<p>Ngoài GA4, trang chỉ lưu dữ liệu trên chính máy của bạn: tiến độ bài học (bài nào bạn đã đánh dấu học xong), từ vựng đã biết/chưa biết, tiến độ trò chơi và bài kiểm tra được lưu trong trình duyệt của bạn (localStorage), không gửi về máy chủ của chúng tôi. Xóa dữ liệu trình duyệt là xóa luôn các dữ liệu này.</p>
</section>
<section class="section section-alt">
<div class="section-head"><h2>Yêu cầu xóa dữ liệu</h2></div>
<p>Hiện trang chưa có hộp thư liên hệ riêng, nên cách nhanh nhất để yêu cầu dừng và xóa dữ liệu phân tích liên quan tới bạn là dùng liên kết “Cài đặt cookie” ở chân trang như hướng dẫn ở trên — có hiệu lực ngay, không cần chờ ai xử lý. Địa chỉ liên hệ để gửi yêu cầu xóa dữ liệu sẽ được bổ sung tại đây khi trang có hộp thư liên hệ chính thức.</p>
</section>
""", active="/", eyebrow="David English",
    desc="Chính sách quyền riêng tư của David English: Google Analytics thu thập gì, dữ liệu gửi cho nhà cung cấp AI (Groq, Google Gemini) gồm những gì, lưu bao lâu, và cách rút lại sự đồng ý.")

if __name__ == "__main__":
    for path, title, h1, body, active, desc, eyebrow, hero, noindex, updated in PAGES:
        full = page(path, title, h1, body, active, desc, eyebrow, hero, noindex, updated)
        print("wrote", path, os.path.getsize(full), "B")
    print("total pages:", len(PAGES))
    # Sitemap: chỉ các trang được index (không noindex), trang chủ trước.
    # Các file trò chơi tro-choi/*.html không qua page() nên cộng thêm tay.
    indexed = [p[0] for p in PAGES if not p[8]]
    indexed += [f"/tro-choi/{slug}.html" for slug, _, _, _ in TRO_CHOI]
    indexed.sort(key=lambda u: (0, "") if u == "/" else (1, u))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in indexed:
        lines.append(f"  <url><loc>{SITE_URL}{_pretty_url(u)}</loc></url>")
    lines.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("sitemap urls:", len(indexed),
          "(noindex excluded:", sum(1 for p in PAGES if p[8]), ")")
    # site-manifest.json + api/site-context.js: nguồn dữ liệu chung về các mục
    # của trang, sinh từ dữ liệu thật (sitemap + số bài học) để AI chat
    # (api/chat.js) luôn biết mục nào đã có, mục nào chỉ là demo/hướng dẫn.
    # KHÔNG ghi tay số bài học ở đây — lấy từ LESSONS_BY_LEVEL / B1 / B2.
    manifest_sections = [
        {"name": "Trang chủ", "url": "/", "status": "available"},
        {"name": "Bài xếp lớp (bản demo 3 câu mẫu)", "url": "/bai-xep-lop.html", "status": "available", "note": "demo, không phải bài kiểm tra thật"},
        {"name": "English Level Check — kiểm tra trình độ", "url": "/tro-choi/english-level-check.html", "status": "available"},
        {"name": "Trình độ A1", "url": "/trinh-do/a1.html", "status": "available", "lessons": len(LESSONS_BY_LEVEL["a1"])},
        {"name": "Trình độ A2", "url": "/trinh-do/a2.html", "status": "available", "lessons": len(LESSONS_BY_LEVEL["a2"])},
        {"name": "Trình độ B1", "url": "/trinh-do/b1.html", "status": "available", "lessons": len(B1_LESSONS)},
        {"name": "Trình độ B2", "url": "/trinh-do/b2.html", "status": "available", "lessons": len(B2_LESSONS)},
        {"name": "Trình độ C1 (hướng dẫn học)", "url": "/trinh-do/c1.html", "status": "available", "note": "hướng dẫn học, chưa có bài học theo bài"},
        {"name": "Trình độ C2 (hướng dẫn học)", "url": "/trinh-do/c2.html", "status": "available", "note": "hướng dẫn học, chưa có bài học theo bài"},
        {"name": "Kế hoạch học", "url": "/ke-hoach-hoc.html", "status": "available"},
        {"name": "Học với David (học 1 kèm 1)", "url": "/hoc-voi-david.html", "status": "available", "note": "lớp học 1 kèm 1 với David; học phí và lịch học trao đổi sau khi đánh giá trình độ"},
        {"name": "Theo kỹ năng (Nghe, Nói, Đọc, Viết)", "url": "/ky-nang/", "status": "available"},
        {"name": "Luyện thi (IELTS, TOEIC, PTE, TOEFL, VSTEP)", "url": "/luyen-thi/", "status": "available"},
        {"name": "Trẻ em", "url": "/tre-em.html", "status": "available"},
        {"name": "Tiếng Anh công việc", "url": "/cong-viec.html", "status": "available"},
        {"name": "Du học", "url": "/du-hoc.html", "status": "available"},
        {"name": "Tài nguyên miễn phí", "url": "/tai-nguyen.html", "status": "available"},
        {"name": "Sách học", "url": "/sach/", "status": "available"},
        {"name": "Trò chơi & Công cụ", "url": "/tro-choi/", "status": "available", "tools": len(TRO_CHOI)},
        {"name": "Trò chuyện AI", "url": "/tro-chuyen-ai.html", "status": "available"},
        {"name": "Tra từ bằng AI", "url": "/cong-cu/tu-vung.html", "status": "available"},
        {"name": "Chữa bài viết bằng AI", "url": "/cong-cu/viet.html", "status": "available"},
    ]
    manifest = {"site": "David English", "sections": manifest_sections}
    with open(os.path.join(ROOT, "site-manifest.json"), "w", encoding="utf-8") as f:
        f.write(_json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    with open(os.path.join(ROOT, "api", "site-context.js"), "w", encoding="utf-8") as f:
        f.write("// api/site-context.js — SINH TỰ ĐỘNG bởi _build.py từ dữ liệu thật\n"
                "// (sitemap + số bài học). KHÔNG sửa tay — sửa _build.py rồi chạy lại.\n"
                "// chat.js import danh sách này để AI luôn biết mục nào đã có.\n"
                "export const SITE_SECTIONS = " + _json.dumps(manifest_sections, ensure_ascii=False, indent=2) + ";\n")
    print("site-manifest sections:", len(manifest_sections))
