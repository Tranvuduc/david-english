#!/usr/bin/env python3
"""adopt_artifacts.py — Batch 2: adopt David's 18 HTML artifacts into tro-choi/.

Minimal clean only:
  - repoint https://claude.ai/artifact/<id> links to local /tro-choi/<slug>.html
    (every referenced artifact is one of the 18 adopted files)
  - drop target="_blank" on repointed internal links
  - reword 2 plain-text mentions of claude.ai (error/note strings, not links)
  - everything else byte-identical: titles, localStorage keys, fonts, JS.
Usage: python3 adopt_artifacts.py  (reads ~/workspace/user-files-inspect/artifacts-html/)
"""
import os
import re
import sys

SRC = os.path.expanduser("~/workspace/user-files-inspect/artifacts-html")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tro-choi")

# source filename -> slug
ADOPT = {
    "TOEIC Arcade.html": "toeic-arcade",
    "PTE Arcade.html": "pte-arcade",
    "Workplace English Arcade.html": "workplace-english-arcade",
    "English Level Check.html": "english-level-check",
    "Level Map.html": "level-map",
    "Band Climb.html": "band-climb",
    "Speaking Booth.html": "speaking-booth",
    "Starter Quest.html": "starter-quest",
    "Intermediate Quest.html": "intermediate-quest",
    "Grade 4 Quest.html": "grade-4-quest",
    "Grade 9 Quest.html": "grade-9-quest",
    "Grade 10 Quest.html": "grade-10-quest",
    "Teacher Quest.html": "teacher-quest",
    "Game Room Lobby.html": "game-room-lobby",
    "AI Workbench.html": "ai-workbench",
    "EFEC Helper.html": "efec-helper",
    "Open Shelf.html": "open-shelf",
    "Bible English Adventure.html": "bible-english-adventure",
}

# claude.ai artifact id -> local slug (verified against Level Map data,
# English Level Check constants and Game Room Lobby card order)
ID_MAP = {
    "5oGtuAJWyr2cvK3Qxdn6QW": "english-level-check",
    "6q7ikhBSvVmhBoNQ6VXdzM": "band-climb",
    "6jgfWjJ4d2NW8NkD9tkFXG": "grade-9-quest",
    "DtVv55zFTtPg3HbxX4g1yd": "grade-4-quest",
    "DzDpS6NZ8dHADhuP6YGJmq": "speaking-booth",
    "EcoA58ua7ypgzU6ACZDHS6": "bible-english-adventure",
    "EjJXQFeFKMqDx22sbHEoYu": "starter-quest",
    "H1U3iDicdLWnhQZx7RGhNP": "pte-arcade",
    "JvfeEZahgAiteDJaMjjsfH": "workplace-english-arcade",
    "LZsPibDEkJTsxGvnv6Yybt": "level-map",
    "LmYfwnbxLcPvYfnDntbsDV": "toeic-arcade",
    "PT52W8b8jpYU1DPT7i1v5c": "intermediate-quest",
    "Qx6RJzGB9qo6oNsH9KoJuL": "grade-10-quest",
    "YFQscGyTAPw2tTSq5x8kKJ": "game-room-lobby",
}

TEXT_REWORDS = [
    # AI Workbench error string (not a link): drop the claude.ai direction.
    (" Try opening the artifact directly on claude.ai.",
     ""),
    # Workplace note (not a link): keep the meaning, drop the domain.
    ("opened in the Claude app or on claude.ai while signed in",
     "opened in the Claude app while signed in"),
]


def clean(text, src):
    n_links = 0

    def _rep(m):
        nonlocal n_links
        n_links += 1
        return "/tro-choi/" + ID_MAP[m.group(1)] + ".html"

    text = re.sub(r"(?:https://)?claude\.ai/artifact/([A-Za-z0-9]+)", _rep, text)
    # drop new-tab on repointed internal anchors
    text = re.sub(
        r'(<a[^>]*href="/tro-choi/[^"]*"[^>]*) target="_blank" rel="noopener"',
        r"\1", text)
    for old, new in TEXT_REWORDS:
        if old in text:
            text = text.replace(old, new)
    return text, n_links


def main():
    os.makedirs(DST, exist_ok=True)
    total_links = 0
    for src_name, slug in sorted(ADOPT.items()):
        src = os.path.join(SRC, src_name)
        dst = os.path.join(DST, slug + ".html")
        with open(src, encoding="utf-8") as f:
            text = f.read()
        orig_title = re.search(r"<title>(.*?)</title>", text, re.S).group(1)
        cleaned, n = clean(text, src_name)
        assert "claude.ai" not in cleaned, f"claude.ai remains in {slug}"
        assert orig_title in cleaned, f"title changed in {slug}"
        with open(dst, "w", encoding="utf-8") as f:
            f.write(cleaned)
        total_links += n
        print(f"  {slug}.html: {os.path.getsize(dst)} B "
              f"(src {os.path.getsize(src)} B, {n} links repointed)")
    print(f"total repointed links: {total_links}")
    print("claude.ai check: none remain in tro-choi/")


if __name__ == "__main__":
    main()
