#!/usr/bin/env python3
"""build_de_pdf.py — David English lesson PDF builder (Phase 1).

Lesson JSON -> one PDF pack (vocab sheet + grammar + dialogue +
exercises + quiz, answer key on the LAST page only).
Extends the team's proven teaching/make_package.py pattern:
  - reportlab Platypus, Noto Sans (full Vietnamese + IPA)
  - EVERY table cell is a Paragraph (raw strings render Helvetica/Latin-1
    and Vietnamese diacritics vanish silently)
  - never use the arrow char (not in Noto Sans); write "to"/"then"
Usage: python3 build_de_pdf.py <lesson.json> ... [--out DIR]
       python3 build_de_pdf.py --all [--out DIR]   (all JSONs in tai-lieu/src/)
"""
import json
import os
import sys
from collections import Counter

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "tai-lieu", "src")
DEFAULT_OUT = os.path.join(ROOT, "tai-lieu")

FONT_DIR = "/usr/share/fonts/truetype/noto"
pdfmetrics.registerFont(TTFont("Noto", f"{FONT_DIR}/NotoSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoB", f"{FONT_DIR}/NotoSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("NotoI", f"{FONT_DIR}/NotoSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("NotoBI", f"{FONT_DIR}/NotoSans-BoldItalic.ttf"))

NAVY = HexColor("#123a6d")
TEAL = HexColor("#0e7c6b")
TEAL_LT = HexColor("#e6f4f1")
GOLD = HexColor("#7a5200")
GRAY_DK = HexColor("#1f2937")
GRAY = HexColor("#6b7280")
LINE = HexColor("#d1d5db")
CREAM = HexColor("#f7f5ef")


def styles():
    return {
        "title": ParagraphStyle("title", fontName="NotoB", fontSize=22,
                                leading=28, textColor=NAVY,
                                spaceAfter=2 * mm, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", fontName="Noto", fontSize=11,
                                   leading=15, textColor=GRAY,
                                   spaceAfter=3 * mm, alignment=TA_CENTER),
        "badge": ParagraphStyle("badge", fontName="Noto", fontSize=9,
                                leading=12, textColor=GOLD,
                                spaceAfter=6 * mm, alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", fontName="NotoB", fontSize=15,
                             leading=19, textColor=NAVY,
                             spaceBefore=7 * mm, spaceAfter=3 * mm),
        "h2": ParagraphStyle("h2", fontName="NotoB", fontSize=12,
                             leading=16, textColor=TEAL,
                             spaceBefore=5 * mm, spaceAfter=2 * mm),
        "body": ParagraphStyle("body", fontName="Noto", fontSize=10.5,
                               leading=15.5, spaceAfter=2 * mm),
        "cell": ParagraphStyle("cell", fontName="Noto", fontSize=9,
                               leading=12.5),
        "cellb": ParagraphStyle("cellb", fontName="NotoB", fontSize=9,
                                leading=12.5),
        "example": ParagraphStyle("example", fontName="NotoI", fontSize=10,
                                  leading=14.5, textColor=GRAY_DK,
                                  leftIndent=8 * mm, spaceAfter=2 * mm),
        "dialogue": ParagraphStyle("dialogue", fontName="Noto", fontSize=10.5,
                                   leading=15.5, leftIndent=6 * mm,
                                   spaceAfter=1.5 * mm),
        "quizq": ParagraphStyle("quizq", fontName="Noto", fontSize=10.5,
                                leading=15, spaceBefore=3 * mm,
                                spaceAfter=1 * mm),
        "quizo": ParagraphStyle("quizo", fontName="Noto", fontSize=10.5,
                                leading=14.5, leftIndent=8 * mm),
        "key": ParagraphStyle("key", fontName="Noto", fontSize=10.5,
                              leading=16),
    }


def vocab_table(vocab, st):
    data = [[Paragraph("<b>Từ</b>", st["cellb"]),
             Paragraph("<b>Loại</b>", st["cellb"]),
             Paragraph("<b>IPA</b>", st["cellb"]),
             Paragraph("<b>Nghĩa</b>", st["cellb"]),
             Paragraph("<b>Ví dụ</b>", st["cellb"])]]
    for v in vocab:
        data.append([
            Paragraph(f"<b>{v['word']}</b>", st["cell"]),
            Paragraph(v.get("pos", ""), st["cell"]),
            Paragraph(f"/{v.get('ipa', '')}/", st["cell"]),
            Paragraph(v.get("vi", ""), st["cell"]),
            Paragraph(f"<i>{v.get('ex', '')}</i>", st["cell"]),
        ])
    t = Table(data, colWidths=[26 * mm, 18 * mm, 26 * mm, 38 * mm, 72 * mm],
              repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TEAL_LT]),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def check_balance(quiz, slug):
    """Quiz answers must be balanced A/B/C/D (no letter 0 or >40%)."""
    counts = Counter("ABCD"[q["answer"]] for q in quiz)
    n = len(quiz)
    problems = []
    for letter in "ABCD":
        c = counts.get(letter, 0)
        if c == 0:
            problems.append(f"no {letter} answer")
        if n and c / n > 0.4:
            problems.append(f"{letter}={c}/{n} (>40%)")
    return problems


def build(data, outpath):
    st = styles()
    level = data.get("level", "")
    title = data["title"]
    doc = SimpleDocTemplate(
        outpath, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=18 * mm,
        title=f"{title} — David English ({level})",
        author="David English",
        subject=f"Bài học tiếng Anh {level}: {data.get('title_en', '')}",
        creator="David English — build_de_pdf.py",
    )
    doc.lesson_title = title

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Noto", 8)
        canvas.setFillColor(GRAY)
        canvas.drawCentredString(A4[0] / 2, 12 * mm,
                                 f"{doc.lesson_title} — David English")
        canvas.drawRightString(A4[0] - 15 * mm, 12 * mm, str(doc.page))
        canvas.drawCentredString(A4[0] / 2, 7 * mm,
                                 "AI, chưa duyệt — nội dung do AI soạn, "
                                 "chưa được giáo viên duyệt.")
        canvas.restoreState()

    story = []
    story.append(Paragraph(title, st["title"]))
    story.append(Paragraph(data.get("subtitle", ""), st["subtitle"]))
    story.append(Paragraph(f"Trình độ {level} · David English — "
                           "Học tiếng Anh miễn phí", st["badge"]))
    story.append(Paragraph("Mục tiêu bài học", st["h1"]))
    for o in data.get("objectives", []):
        story.append(Paragraph(f"• {o}", st["body"]))

    story.append(Paragraph("I. Từ vựng", st["h1"]))
    story.append(vocab_table(data.get("vocabulary", []), st))

    story.append(Paragraph("II. Ngữ pháp", st["h1"]))
    for g in data.get("grammar", []):
        story.append(Paragraph(g["title"], st["h2"]))
        story.append(Paragraph(g["explain"], st["body"]))
        for ex in g.get("examples", []):
            story.append(Paragraph(f"• {ex}", st["example"]))

    dlg = data.get("dialogue")
    if dlg:
        story.append(Paragraph("III. Hội thoại mẫu", st["h1"]))
        story.append(Paragraph(dlg.get("title", ""), st["h2"]))
        for who, line in dlg.get("lines", []):
            story.append(Paragraph(f"<b>{who}:</b> {line}", st["dialogue"]))
        section_no = "IV"
    else:
        section_no = "III"

    story.append(Paragraph(f"{section_no}. Bài tập", st["h1"]))
    for ei, ex in enumerate(data.get("exercises", []), 1):
        story.append(Paragraph(f"<b>Bài {ei}: {ex['title']}</b>", st["h2"]))
        story.append(Paragraph(ex["instruction"], st["body"]))
        for qi, q in enumerate(ex.get("questions", []), 1):
            story.append(Paragraph(f"{qi}. {q}", st["body"]))
        story.append(Spacer(1, 2 * mm))

    quiz = data.get("quiz", [])
    q_no = "V" if section_no == "IV" else "IV"
    story.append(Paragraph(f"{q_no}. Trắc nghiệm", st["h1"]))
    story.append(Paragraph("Chọn một đáp án đúng cho mỗi câu. "
                           "Đáp án ở trang cuối.", st["body"]))
    for i, q in enumerate(quiz, 1):
        story.append(Paragraph(f"<b>Câu {i}.</b> {q['q']}", st["quizq"]))
        for j, opt in enumerate(q["options"]):
            story.append(Paragraph(f"{'ABCD'[j]}. {opt}", st["quizo"]))

    story.append(Paragraph("Lỗi thường gặp", st["h1"]))
    for m in data.get("common_mistakes", []):
        story.append(Paragraph(f"• {m}", st["body"]))

    # Answer key — LAST page only.
    story.append(PageBreak())
    story.append(Paragraph("Đáp án", st["h1"]))
    for ei, ex in enumerate(data.get("exercises", []), 1):
        ans = "; ".join(f"{i + 1}. {a}"
                        for i, a in enumerate(ex.get("answers", [])))
        story.append(Paragraph(f"<b>Bài {ei} ({ex['title']}):</b> {ans}",
                               st["key"]))
        story.append(Spacer(1, 2 * mm))
    q_ans = "  ".join(f"{i + 1}{'ABCD'[q['answer']]}"
                      for i, q in enumerate(quiz))
    story.append(Paragraph(f"<b>Trắc nghiệm:</b> {q_ans}", st["key"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Học thêm tại davidenglish.vercel.app — "
                           "miễn phí, giải thích bằng tiếng Việt.",
                           st["body"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return outpath


def main():
    args = sys.argv[1:]
    out_dir = DEFAULT_OUT
    if "--out" in args:
        i = args.index("--out")
        out_dir = args[i + 1]
        args = args[:i] + args[i + 2:]
    if "--all" in args:
        files = sorted(os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR)
                       if f.endswith(".json"))
    else:
        files = args
    if not files:
        print("usage: build_de_pdf.py <lesson.json> ... [--out DIR] | --all")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    ok = True
    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        level = data.get("level", "").lower()
        slug = data["slug"]
        sub = os.path.join(out_dir, level)
        os.makedirs(sub, exist_ok=True)
        outpath = os.path.join(sub, f"{slug}.pdf")
        problems = check_balance(data.get("quiz", []), slug)
        if problems:
            print(f"  !! {slug}: answer balance: {'; '.join(problems)}")
            ok = False
        build(data, outpath)
        size = os.path.getsize(outpath)
        flag = "OVER 500KB!" if size > 500 * 1024 else (
            "over 150KB target" if size > 150 * 1024 else "ok")
        print(f"  {slug}.pdf: {size} B ({flag})")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
