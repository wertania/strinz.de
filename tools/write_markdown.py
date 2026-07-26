#!/usr/bin/env python3
"""Step 2: write the document out as one Markdown file per chapter.

The wording is passed through verbatim. This step only decides *what a block is*
— heading, year, rubric, verse line, table, figure, caption, source — and gives
it the right Markdown shape.

Every decision below was made by reading the chapter it applies to; the ones
that cannot be read off the docx markup directly are named explicitly rather
than guessed by a general heuristic.
"""
from __future__ import annotations
import json, re, unicodedata
from itertools import zip_longest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "content"

# --- corrections to the Word file's own markup -------------------------------

# The body of "Keine ‚Aarstraße‘ für StM" carries the Heading-1 style, which
# would otherwise tear the chapter apart. Nine paragraphs, verified by reading.
MIS_STYLED_HEADINGS = set(range(7619, 7628))

# --- structure that the docx encodes, but not as styles ----------------------

YEAR_RE = re.compile(r"^(1[0-9]{3}|20[0-2][0-9])$")
RUBRICS = {
    "Obrigkeiten", "Ereignisse", "Allgemeine Ereignisse", "Statistik", "Wahlen",
    "Aus der Kirchenchronik", "Aus der Schulchronik", "Bekannte Namensform",
    "Bekannte Namensformen", "Reichstagswahl", "Landtagswahl", "Kommunalwahl",
    "Bundestagswahl",
}
SOURCE_RE = re.compile(r"^\(\s*(Quelle|Foto|Bild|Fotos|Bilder)\s*[:.]\s*(.+?)\s*\)$", re.S | re.I)

# Sections whose paragraphs are single verse lines rather than prose. Word
# styles them exactly like running text, so this list comes from reading them.
# "Das Strinzer Lied" is deliberately absent: it only reproduces the song as a
# scan, its paragraphs are prose about the song.
VERSE_SECTIONS = {
    "Ehestandslieder", "Das Lied vom Wanderer", "Das Lied vom verlorenen Bruder",
    "Das Leben ist ein Würfelspiel", "Mundartproben", "Gedicht",
    "Der Schuss", "Die Strinzer Eisenbahn", "Fastnacht", "Kerb", "Weihnachten",
    "Strinzer Heckeflämmser",
}
# Inside those sections a line introducing the song is still prose.
VERSE_INTRO_RE = re.compile(r":\s*$")
STANZA_BREAK_RE = re.compile(r"^[-–—_\s]{5,}$")

# A run of short paragraphs in a row is never running text: in the song and
# rhyme sections it is a stanza, everywhere else an enumeration that Word never
# marked up as a list (name forms, currency tables, livestock counts, …).
RUN_MIN = 4
RUN_MAX_CHARS = 70

CAPTION_MAX = 95


def slugify(text: str) -> str:
    text = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", text)).strip("-") or "kapitel"


def clean(text: str) -> str:
    """Whitespace and typographic artefacts only — never the wording."""
    text = unicodedata.normalize("NFKC", text).replace(" ", " ")
    text = text.replace("\u0301", "'").replace("´", "'")
    text = "\n".join(re.sub(r"[ \t]{2,}", " ", line).strip() for line in text.split("\n"))
    return text.strip()


def is_bold(block) -> bool:
    runs = block.get("runs")
    return bool(runs) and all(r["b"] for r in runs if r["text"].strip())


def classify(block, chapter, section):
    """What is this block, really?"""
    if block["type"] == "auto-toc":
        return "skip"
    if block["type"] == "table":
        return "glossary" if block["cols"] == 5 and chapter == "Die heimatliche Mundart" else "table"
    if block["type"] == "heading" and block["i"] not in MIS_STYLED_HEADINGS:
        return "heading"

    text = clean(block.get("text", ""))
    if not text:
        return "figure" if block.get("images") else "skip"
    if YEAR_RE.match(text) and is_bold(block):
        return "year"
    if text in RUBRICS:
        return "rubric"
    if SOURCE_RE.match(text):
        return "source"
    if STANZA_BREAK_RE.match(text) and section in VERSE_SECTIONS:
        return "stanza-break"
    return "paragraph"


def mark_runs(items):
    """Second pass: reshape runs of short paragraphs into verse or a list."""
    out = list(items)
    start = None
    for pos in range(len(out) + 1):
        kind, block, section = (out[pos] + (None,))[:3] if pos < len(out) else (None, None, None)
        short = (
            pos < len(out)
            and kind == "paragraph"
            and block.get("images") is None
            and block.get("list") is None
            and 0 < len(clean(block.get("text", ""))) <= RUN_MAX_CHARS
            and "\n" not in clean(block.get("text", ""))
        )
        if short:
            start = pos if start is None else start
            continue
        if start is not None and pos - start >= RUN_MIN:
            begin = start
            if out[start][2] in VERSE_SECTIONS:
                # A rhyme's lines rarely end in a full stop; a sentence that does
                # and sits in front of the stanza is the prose leading into it.
                texts = [clean(out[k][1].get("text", "")) for k in range(start, pos)]
                if sum(t.endswith(".") for t in texts) * 2 < len(texts):
                    while begin < pos - RUN_MIN and texts[begin - start].endswith("."):
                        begin += 1
                target = "verse"
            else:
                target = "listitem"
            for k in range(begin, pos):
                out[k] = (target,) + out[k][1:]
        start = None
    return out


TRAILING_SOURCE_RE = re.compile(
    r"\s*\(\s*(Quelle|Foto|Bild|Fotos|Bilder)\s*[:.]\s*([^()]{2,200})\)\s*$", re.I)


def split_trailing_source(text):
    """A source note closing an otherwise normal paragraph, on its own line or
    appended to the last sentence."""
    if "\n" in text:
        head, _, last = text.rpartition("\n")
        m = SOURCE_RE.match(last.strip())
        if m:
            return head.strip(), f"{m.group(1)}: {m.group(2).strip()}"
    m = TRAILING_SOURCE_RE.search(text)
    if m and text[: m.start()].strip():
        return text[: m.start()].strip(), f"{m.group(1)}: {m.group(2).strip()}"
    return text, None


def glossary_pairs(block):
    """The dialect tables are two term/translation pairs per row, with a spacer
    column in between; some cells stack several entries on their own lines."""
    pairs = []
    for row in block["rows"]:
        cells = [clean(c["text"]) for c in row]
        for left, right in ((0, 1), (3, 4)):
            if left >= len(cells) or right >= len(cells):
                continue
            terms, forms = cells[left].split("\n"), cells[right].split("\n")
            # a cell may stack more entries than its partner; keep them all
            for term, form in zip_longest(terms, forms, fillvalue=""):
                term, form = term.strip(), form.strip()
                if term or form:
                    pairs.append((term, form))
    return pairs


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")


def render_table(block, lines):
    rows = [[clean(c["text"]) for c in row] for row in block["rows"]]
    rows = [r for r in rows if any(r)]
    if not rows:
        return
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    if width == 1:
        for row in rows:
            lines += [row[0], ""]
        return
    head, body = rows[0], rows[1:]
    lines.append("| " + " | ".join(escape(c) or " " for c in head) + " |")
    lines.append("|" + "|".join([" --- "] * width) + "|")
    for row in body:
        lines.append("| " + " | ".join(escape(c) or " " for c in row) + " |")
    lines.append("")


def collect_chapters(blocks):
    """Split the document into chapters of classified (kind, block, section)."""
    chapters, current, section = [], None, None
    for block in blocks:
        if block["type"] == "heading" and block.get("level") == 1 \
                and block["i"] not in MIS_STYLED_HEADINGS:
            current = {"title": clean(block["text"]), "blocks": []}
            chapters.append(current)
            section = None
            continue
        if current is None:
            current = {"title": "Titelei", "blocks": [], "synthetic": True}
            chapters.append(current)
        if block["type"] == "heading" and block["i"] not in MIS_STYLED_HEADINGS:
            section = clean(block["text"])
        current["blocks"].append(
            (classify(block, current["title"], section), block, section))
    for chapter in chapters:
        chapter["blocks"] = mark_runs(chapter["blocks"])
    return chapters


def main():
    blocks = json.loads((DATA / "document.json").read_text(encoding="utf-8"))
    chapters = collect_chapters(blocks)

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()

    index, stats = [], {}
    for n, chapter in enumerate(chapters):
        slug = slugify(chapter["title"])
        lines = ["---", f'title: "{chapter["title"]}"', f"number: {n}",
                 f"slug: {slug}", "---", ""]
        if not chapter.get("synthetic"):
            lines += [f"# {chapter['title']}", ""]
        verse, after_image = [], False

        def flush_verse():
            if verse:
                lines.append("  \n".join(verse))
                lines.append("")
                verse.clear()

        for kind, block, _section in chapter["blocks"]:
            stats[kind] = stats.get(kind, 0) + 1
            if kind not in ("verse",):
                flush_verse()
            text = clean(block.get("text", ""))

            if kind == "skip":
                continue
            if kind == "glossary":
                for term, form in glossary_pairs(block):
                    lines.append(f"- **{term}** — {form}" if form else f"- **{term}**")
                lines.append("")
                after_image = False
                continue
            if kind == "table":
                render_table(block, lines)
                after_image = False
                continue
            if kind == "heading":
                lines += ["#" * block["level"] + " " + text, ""]
                after_image = False
                continue
            if kind == "year":
                lines += [f"### {text}", ""]
                after_image = False
                continue
            if kind == "rubric":
                lines += [f"#### {text}", ""]
                after_image = False
                continue
            if kind == "source":
                m = SOURCE_RE.match(text)
                lines += [f"> {m.group(1)}: {m.group(2)}", ""]
                after_image = False
                continue
            if kind == "verse":
                verse.append(text.replace("\n", "  \n"))
                after_image = False
                continue
            if kind == "stanza-break":
                after_image = False
                continue
            if kind == "listitem":
                lines.append("- " + text)
                after_image = False
                continue

            if kind == "figure" and not text:
                pass
            elif text:
                # a short line right after a plate is its caption
                if after_image and len(text) <= CAPTION_MAX and "\n" not in text \
                        and not text.endswith("."):
                    lines += [f"*{text}*", ""]
                    stats["caption"] = stats.get("caption", 0) + 1
                    after_image = False
                    continue
                body, source = split_trailing_source(text)
                if block.get("list") is not None:
                    lines.append("  " * block["list"] + "- " + body.replace("\n", "\n  "))
                else:
                    lines.append(body)
                lines.append("")
                if source:
                    lines += [f"> {source}", ""]
                    stats["inline-source"] = stats.get("inline-source", 0) + 1
            after_image = False

            for image in block.get("images", []):
                lines += [f"![](images/{image})", ""]
                after_image = True
        flush_verse()

        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).rstrip() + "\n"
        (OUT / f"{n:02d}-{slug}.md").write_text(text, encoding="utf-8")
        index.append({"file": f"{n:02d}-{slug}.md", "title": chapter["title"],
                      "slug": slug, "number": n, "chars": len(text)})

    (DATA / "chapters.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(index)} Kapitel")
    for k in sorted(stats):
        print(f"  {k:16s} {stats[k]}")


if __name__ == "__main__":
    main()
