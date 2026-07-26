#!/usr/bin/env python3
"""Step 4: turn the classified document into data/content.json for the site.

Uses exactly the same classification as the Markdown export, so the website and
content/*.md always say the same thing.
"""
from __future__ import annotations
import importlib.util, json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

spec = importlib.util.spec_from_file_location("wm", ROOT / "tools/write_markdown.py")
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)

CHRONICLE = "Chronik nach Jahren"
OFFICE_RE = re.compile(
    r"^(Pfarrer|Lehrer|Bürgermeister|Schultheiß|Ortsvorsteher|Schulmeister|Küster|"
    r"Hebamme|Nachtwächter|Ortsdiener|Gemeinderechner|Landesherr|Herrschaft|"
    r"Amtmann|Vogt|Kaiser|Verwalter|Zentgraf)\s*:\s*(\S.*)$")
NAME_RE = re.compile(r"^[A-ZÄÖÜ][\w äöüß.'\-()]{1,46}$")
POP_RE = re.compile(r"^(?:Einwohner|Familien|Seelen|Häuser|Wohngebäude|Haushalte)\b\s*:?\s*(\d+)")


def flush(buffer, blocks):
    if buffer:
        blocks.append({"type": "verse", "lines": list(buffer)})
        buffer.clear()


def render(items):
    """The block list a page renders, in document order."""
    blocks, verse, after_image = [], [], False
    for kind, block, _section in items:
        if kind != "verse":
            flush(verse, blocks)
        text = wm.clean(block.get("text", ""))

        if kind in ("skip", "stanza-break"):
            continue
        if kind == "glossary":
            blocks.append({"type": "glossary",
                           "pairs": [{"term": t, "form": f} for t, f in wm.glossary_pairs(block)]})
            after_image = False
            continue
        if kind == "table":
            rows = [[wm.clean(c["text"]) for c in row] for row in block["rows"]]
            rows = [r for r in rows if any(r)]
            if rows:
                blocks.append({"type": "table", "head": rows[0], "rows": rows[1:]})
            after_image = False
            continue
        if kind == "heading":
            blocks.append({"type": "heading", "level": block["level"], "text": text})
            after_image = False
            continue
        if kind in ("year", "rubric"):
            blocks.append({"type": kind, "text": text})
            after_image = False
            continue
        if kind == "source":
            m = wm.SOURCE_RE.match(text)
            blocks.append({"type": "source", "label": m.group(1), "text": m.group(2)})
            after_image = False
            continue
        if kind == "verse":
            verse.append(text)
            after_image = False
            continue

        if text:
            if after_image and len(text) <= wm.CAPTION_MAX and "\n" not in text \
                    and not text.endswith("."):
                if blocks and blocks[-1]["type"] == "image":
                    blocks[-1]["caption"] = text
                    after_image = False
                    continue
            body, source = wm.split_trailing_source(text)
            entry = {"type": "listitem" if kind == "listitem" else "paragraph", "text": body}
            if block.get("list") is not None:
                entry["type"] = "listitem"
            blocks.append(entry)
            if source:
                label, _, rest = source.partition(": ")
                blocks.append({"type": "source", "label": label, "text": rest})
        after_image = False
        for image in block.get("images", []):
            blocks.append({"type": "image", "file": image})
            after_image = True
    flush(verse, blocks)
    return blocks


def split_years(blocks):
    """Cut the chronicle into epochs, years and rubrics."""
    epochs, epoch, year, rubric = [], None, None, None
    for block in blocks:
        if block["type"] == "heading" and block["level"] == 2:
            epoch = {"title": block["text"], "slug": wm.slugify(block["text"]), "years": []}
            epochs.append(epoch)
            year = rubric = None
            continue
        if epoch is None:
            continue
        if block["type"] == "year":
            year = {"year": int(block["text"]), "groups": []}
            epoch["years"].append(year)
            rubric = None
            continue
        if year is None:
            year = {"year": None, "groups": []}
            epoch["years"].append(year)
        if block["type"] == "rubric":
            rubric = {"rubric": block["text"], "blocks": []}
            year["groups"].append(rubric)
            continue
        if rubric is None:
            rubric = {"rubric": None, "blocks": []}
            year["groups"].append(rubric)
        rubric["blocks"].append(block)
    for e in epochs:
        e["years"] = [y for y in e["years"]
                      if y["year"] and any(g["blocks"] for g in y["groups"])]
        for y in e["years"]:
            y["groups"] = [g for g in y["groups"] if g["blocks"]]
    return [e for e in epochs if e["years"]]


def split_sections(blocks, chapter_title):
    """Cut an ordinary chapter into its H2 sections (with H3 kept inline)."""
    sections, current = [], None
    lead = []
    for block in blocks:
        if block["type"] == "heading" and block["level"] == 2:
            current = {"title": block["text"], "slug": wm.slugify(block["text"]), "blocks": []}
            sections.append(current)
            continue
        (current["blocks"] if current else lead).append(block)
    if lead:
        sections.insert(0, {"title": chapter_title, "slug": "einleitung",
                            "blocks": lead, "lead": True})
    return [s for s in sections if s["blocks"]]


def build_register(epochs):
    offices, population = defaultdict(lambda: defaultdict(set)), []
    for epoch in epochs:
        for year in epoch["years"]:
            for group in year["groups"]:
                for block in group["blocks"]:
                    if block["type"] not in ("paragraph", "listitem"):
                        continue
                    for line in block["text"].split("\n"):
                        m = OFFICE_RE.match(line.strip())
                        if m:
                            for name in re.split(r"[;/]| und ", m.group(2)):
                                name = name.strip(" .,;")
                                if NAME_RE.match(name):
                                    offices[m.group(1)][name].add(year["year"])
                        p = POP_RE.match(line.strip())
                        if p:
                            population.append({"year": year["year"],
                                               "label": line.strip()})
    register = []
    for office in sorted(offices, key=lambda o: (-len(offices[o]), o)):
        holders = [{"name": n, "years": sorted(y)} for n, y in offices[office].items()]
        holders.sort(key=lambda h: (h["years"][0] if h["years"] else 9999, h["name"]))
        register.append({"office": office, "holders": holders})
    return register, population


def main():
    blocks = json.loads((DATA / "document.json").read_text(encoding="utf-8"))
    chapters = wm.collect_chapters(blocks)

    out_chapters, epochs = [], []
    for n, chapter in enumerate(chapters):
        rendered = render(chapter["blocks"])
        if chapter["title"] == CHRONICLE:
            epochs = split_years(rendered)
            continue
        if chapter.get("synthetic"):
            continue
        out_chapters.append({
            "number": n,
            "title": chapter["title"],
            "slug": wm.slugify(chapter["title"]),
            "sections": split_sections(rendered, chapter["title"]),
        })

    register, population = build_register(epochs)

    def images(blocks):
        return [b["file"] for b in blocks if b["type"] == "image"]

    plates = []
    seen = set()
    for epoch in epochs:
        for year in epoch["years"]:
            for group in year["groups"]:
                for b in group["blocks"]:
                    if b["type"] == "image" and b["file"] not in seen:
                        seen.add(b["file"])
                        plates.append({"file": b["file"], "caption": b.get("caption"),
                                       "context": str(year["year"]),
                                       "href": f"/chronik/{epoch['slug']}/#jahr-{year['year']}"})
    for chapter in out_chapters:
        for section in chapter["sections"]:
            for b in section["blocks"]:
                if b["type"] == "image" and b["file"] not in seen:
                    seen.add(b["file"])
                    plates.append({"file": b["file"], "caption": b.get("caption"),
                                   "context": section["title"],
                                   "href": f"/kapitel/{chapter['slug']}/#{section['slug']}"})

    years_all = [y["year"] for e in epochs for y in e["years"]]
    data = {
        "chapters": out_chapters,
        "epochs": epochs,
        "register": register,
        "population": population,
        "plates": plates,
        "stats": {
            "chapters": len(out_chapters),
            "epochs": len(epochs),
            "years": len(years_all),
            "yearFrom": min(years_all) if years_all else None,
            "yearTo": max(years_all) if years_all else None,
            "plates": len(plates),
            "entries": sum(len(g["blocks"]) for e in epochs for y in e["years"]
                           for g in y["groups"])
                       + sum(len(s["blocks"]) for c in out_chapters for s in c["sections"]),
        },
    }
    (DATA / "content.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data["stats"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
