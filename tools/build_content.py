#!/usr/bin/env python3
"""Step 2: turn the reconstructed paragraph stream into clean, typed content.

Writes data/content.json:
    parts[]    - the 16 top-level parts of the book, each with its sections
    sections[] - one entry per outline heading, with cleaned content blocks
    years[]    - the year-by-year chronicle (part 7), grouped by rubric
    images[]   - every image, with the section or year it belongs to
"""
from __future__ import annotations
import json, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "tools"))
from match_headings import match, norm, YEAR_RE  # noqa: E402
from document import load_stream, split_toc  # noqa: E402

# ---------------------------------------------------------------- cleaning ---

DEHYPHEN = {
    "Wies-baden": "Wiesbaden", "Zusammen-künfte": "Zusammenkünfte",
    "Besoldungs-angriffe": "Besoldungsangriffe", "Pfarr-zehnt": "Pfarrzehnt",
    "Mittel-und": "Mittel- und", "Fünf-bis": "Fünf- bis", "Ersatz-u": "Ersatz- u",
}
SOURCE_RE = re.compile(r"\(\s*(?:Quelle|Foto|Bild)\s*[:.]\s*(.+?)\s*\)\s*$", re.S | re.I)
# the chronicle also cites without the word "Quelle", e.g. "(HStAW 403 Nr. 420)"
CITATION_RE = re.compile(r"\(([^()]{6,140})\)\s*$")
CITATION_HINT = re.compile(
    r"\b(Quelle|Chronik|Archiv|Staatsarchiv|HStA|HHStA|HStAW|Annalen|Analen|Seite|S\.|"
    r"Bd\.|Band|Nr\.|Festschrift|Wikipedia|Überlieferung|Gemeindearchiv|Kirchenbuch)\b", re.I)
TOC_LEFTOVER_RE = re.compile(r"^\d+(?:\.\d+)*[A-ZÄÖÜ][^\n]{0,80}\d{2,4}$")
RUBRICS = ["Obrigkeiten", "Allgemeine Ereignisse", "Ereignisse", "Statistik",
           "Wahlen", "Aus der Kirchenchronik", "Aus der Schulchronik",
           "Bekannte Namensformen", "Reichstagswahl"]
RUBRIC_SET = set(RUBRICS)
BLOCKS_PER_PAGE = 11        # 8.5k content blocks spread over 774 book pages
OVERFLOW_FACTOR = 3         # generous, so real sections are never truncated
YEAR_REACH = 60             # how far a year marker still claims following text
OFFICE_RE = re.compile(
    r"^(Pfarrer|Lehrer|Bürgermeister|Schultheiß|Ortsvorsteher|Schulmeister|Küster|"
    r"Hebamme|Nachtwächter|Ortsdiener|Gemeinderechner|Landesherr|Herrschaft|"
    r"Amtmann|Vogt|Kaiser|Landesherren|Verwalter|Zentgraf)\s*:\s*\S")
POP_RE = re.compile(r"^\d{1,4}\s*(Familien|Einwohner|Seelen|Häuser|Feuerstellen)\b")
STAT_RE = re.compile(
    r"^(Einwohner|Familien|Haushalte|Häuser|Feuerstellen|Seelen|Wohnhäuser|Gebäude|"
    r"Fläche|Viehbestand|Schüler|Konfession|Geburten|Sterbefälle|Trauungen)\b", re.I)


def slugify(text: str) -> str:
    text = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", text)).strip("-") or "abschnitt"


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace(" ", " ")
    for a, b in DEHYPHEN.items():
        text = text.replace(a, b)
    text = re.sub(r"(?<=[a-zäöüß0-9.,;!?“\"'\)])\((Quelle|Foto|Bild):", r" (\1:", text)
    text = text.replace("\u0301", "'").replace(" ́", "'").replace("´", "'")
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def split_source(text: str):
    m = SOURCE_RE.search(text)
    if m:
        return text[: m.start()].strip(), m.group(1).strip()
    m = CITATION_RE.search(text)
    if m and CITATION_HINT.search(m.group(1)):
        return text[: m.start()].strip(), m.group(1).strip()
    return text.strip(), None


VERSE_PARTS = {"11"}
VERSE_SECTIONS = {"4.2"}


def group_verses(blocks):
    """Songs and dialect samples came through as one paragraph per line."""
    out, run = [], []
    for b in blocks:
        if b["type"] == "paragraph" and "source" not in b and len(b["text"]) <= 90:
            run.append(b["text"])
            continue
        if len(run) >= 3:
            out.append({"type": "verse", "lines": run})
        else:
            out.extend({"type": "paragraph", "text": t} for t in run)
        run = []
        out.append(b)
    if len(run) >= 3:
        out.append({"type": "verse", "lines": run})
    else:
        out.extend({"type": "paragraph", "text": t} for t in run)
    return out


def build_blocks(items, seen=None):
    """Turn a run of stream items into typed content blocks."""
    blocks, last = [], None
    seen = set() if seen is None else seen
    for it in items:
        if it["type"] == "img":
            blocks.append({"type": "image", "file": it["file"]})
            continue
        text = clean_text(it["text"])
        if not text or TOC_LEFTOVER_RE.match(text):
            continue
        if text == last or text in seen:
            continue
        last = text
        if len(text) < 200:          # only short lines repeat verbatim in the source
            seen.add(text)
        if text in RUBRIC_SET:
            continue                       # rubrics only matter inside year blocks
        body, src = split_source(text)
        if not body and src:
            if blocks and blocks[-1]["type"] == "paragraph" and "source" not in blocks[-1]:
                blocks[-1]["source"] = src
            else:
                blocks.append({"type": "source", "text": src})
            continue
        block = {"type": "paragraph", "text": body}
        if src:
            block["source"] = src
        blocks.append(block)
    return blocks


# ------------------------------------------------------------------ layout ---

def find_markers(body, outline):
    """Every position that starts a new unit: an outline heading or a year."""
    hits, _ = match(body, outline)
    markers = [(i, "section", k) for k, i in hits.items()]
    taken = {i for _, _, i in ((0, 0, i) for i in hits.values())}
    for i, it in enumerate(body):
        if it["type"] == "p" and i not in taken and YEAR_RE.match(it["text"].strip()):
            markers.append((i, "year", int(it["text"].strip().rstrip("."))))
    markers.sort()
    return markers


def year_groups(items):
    """Split a year's items into its rubrics and repair misfiled entries."""
    groups, current = [], {"rubric": None, "items": []}
    for it in items:
        if it["type"] == "p" and clean_text(it["text"]) in RUBRIC_SET:
            if current["items"] or current["rubric"]:
                groups.append(current)
            current = {"rubric": clean_text(it["text"]), "items": []}
        else:
            current["items"].append(it)
    if current["items"] or current["rubric"]:
        groups.append(current)

    # "Obrigkeiten" holds office holders; anything else in there is an event.
    fixed = defaultdict(list)
    order = []
    for g in groups:
        for it in g["items"]:
            rub = g["rubric"] or "Ereignisse"
            if it["type"] == "p":
                text = clean_text(it["text"])
                if rub == "Obrigkeiten" and not OFFICE_RE.match(text):
                    rub = "Statistik" if STAT_RE.match(text) else "Ereignisse"
                elif rub != "Obrigkeiten" and OFFICE_RE.match(text):
                    rub = "Obrigkeiten"
            if rub not in fixed:
                order.append(rub)
            fixed[rub].append(it)

    priority = {"Obrigkeiten": 0, "Statistik": 1, "Allgemeine Ereignisse": 2,
                "Ereignisse": 3, "Wahlen": 4, "Reichstagswahl": 5,
                "Aus der Kirchenchronik": 6, "Aus der Schulchronik": 7}
    order.sort(key=lambda r: (priority.get(r, 9), r))
    out, seen = [], set()
    for rub in order:
        blocks = build_blocks(fixed[rub], seen)
        if blocks:
            out.append({"rubric": rub, "blocks": blocks})
    return out


def group_by_key(pairs):
    out = defaultdict(list)
    for k, v in pairs:
        out[k].append(v)
    return sorted(out.items())


def build_register(overflow, year_list):
    """Split the annalistic leftovers into an office register and real prose.

    Lines like 'Pfarrer: Ludwig Schmidtborn' or '74 Familien / 327 Einwohner'
    are chronicle rubrics that lost their year.  As prose they are noise; as a
    register of who held which office they are one of the most useful things in
    the book.  Years are filled in from the entries the chronicle *could* place.
    """
    known = defaultdict(set)
    for y in year_list:
        for g in y["groups"]:
            for b in g["blocks"]:
                if b["type"] == "paragraph":
                    m = OFFICE_RE.match(b["text"])
                    if m:
                        for name in split_names(b["text"].split(":", 1)[1]):
                            known[(m.group(1), name)].add(y["year"])

    offices = defaultdict(lambda: defaultdict(set))
    for (office, name), yrs in known.items():
        offices[office][name] |= yrs

    rest = []
    for key, it in overflow:
        if it["type"] == "p":
            text = clean_text(it["text"])
            m = OFFICE_RE.match(text)
            if m:
                for name in split_names(text.split(":", 1)[1]):
                    offices[m.group(1)].setdefault(name, set())
                continue
            if POP_RE.match(text):
                continue
        rest.append((key, it))

    register = []
    for office in sorted(offices, key=lambda o: (-len(offices[o]), o)):
        holders = []
        for name, yrs in offices[office].items():
            years_sorted = sorted(yrs)
            holders.append({"name": name, "years": years_sorted,
                            "from": years_sorted[0] if years_sorted else None,
                            "to": years_sorted[-1] if years_sorted else None})
        holders.sort(key=lambda h: (h["from"] is None, h["from"] or 0, h["name"]))
        register.append({"office": office, "holders": holders})
    return register, rest


NAME_RE = re.compile(r"^[A-ZÄÖÜ][\wäöüß.'\-]*(?: [A-ZÄÖÜ(][\wäöüß.'\-)]*){0,3}$")


def split_names(raw):
    # never split inside a parenthesis - the chronicle writes variants there
    parts = re.split(r"[;/]| und ", raw) if "(" in raw else re.split(r"[;,/]| und ", raw)
    for part in parts:
        name = part.strip(" .,;")
        if not (2 < len(name) < 48) or not NAME_RE.match(name):
            continue
        if name.count("(") != name.count(")"):
            continue
        yield name


def blocks_for(entry, blocks):
    if entry["part"] in VERSE_PARTS or entry["number"] in VERSE_SECTIONS:
        return group_verses(blocks)
    return blocks


def main():
    meta = json.loads((DATA / "outline.json").read_text(encoding="utf-8"))
    outline, parts_meta = meta["outline"], meta["parts"]
    _, body, _ = split_toc(load_stream())

    markers = find_markers(body, outline)
    print(f"markers: {len(markers)} "
          f"({sum(1 for m in markers if m[1] == 'year')} years, "
          f"{sum(1 for m in markers if m[1] == 'section')} headings)")

    # a monotone index -> year map, used to re-home overflowing runs
    year_at = [None] * len(body)
    last, last_at = None, None
    for i in range(len(body)):
        hit = next((m for m in markers if m[0] == i and m[1] == "year"), None)
        if hit:
            last, last_at = hit[2], i
        # a year only claims the text that still follows it closely; further out
        # the chronology is no longer trustworthy
        year_at[i] = last if last_at is not None and i - last_at <= YEAR_REACH else None

    # how much text a section may plausibly hold, from its page span in the book
    page_of = {k: e["page"] for k, e in enumerate(outline)}
    budget = {}
    for k, e in enumerate(outline):
        nxt = next((page_of[j] for j in range(k + 1, len(outline))
                    if page_of[j] and page_of[j] > (e["page"] or 0)), None)
        span = max(1, (nxt - e["page"]) if (nxt and e["page"]) else 2)
        budget[k] = max(12, int(span * BLOCKS_PER_PAGE * OVERFLOW_FACTOR))

    runs, overflow, homed = [], [], []
    for n, (pos, kind, key) in enumerate(markers):
        end = markers[n + 1][0] if n + 1 < len(markers) else len(body)
        items = body[pos + 1:end]
        if kind == "section" and len(items) > budget[key]:
            keep = items[: budget[key]]
            for offset, it in enumerate(items[budget[key]:]):
                y = year_at[min(pos + 1 + budget[key] + offset, len(body) - 1)]
                if y is None:
                    overflow.append((key, it))   # no year to re-home it to
                else:
                    homed.append((y, it))
            items = keep
        runs.append((kind, key, items))
    front = body[: markers[0][0]] if markers else body

    # ---- year chronicle
    years = defaultdict(list)
    for kind, key, items in runs:
        if kind == "year":
            years[key].extend(items)
    # overflow keeps the chronology it was found in
    for y, it in homed:
        years[y].append(it)
    print(f"re-homed {len(homed)} items into the year chronicle, "
          f"{len(overflow)} into the appendix")
    year_list = []
    for y in sorted(years):
        groups = year_groups(years[y])
        if groups:
            year_list.append({"year": y, "groups": groups})

    # ---- thematic sections
    sec_items = defaultdict(list)
    for kind, key, items in runs:
        if kind == "section":
            sec_items[key].extend(items)

    sections, used_slugs = [], set()
    for k, e in enumerate(outline):
        if e["part"] == "7" and e["number"] != "7":
            continue                       # the year chronicle is rendered separately
        slug = slugify(e["title"])
        base, n = slug, 2
        while slug in used_slugs:
            slug = f"{base}-{n}"
            n += 1
        used_slugs.add(slug)
        sections.append({
            "number": e["number"], "title": e["title"], "page": e["page"],
            "level": e["level"], "part": e["part"], "slug": slug,
            "blocks": blocks_for(e, build_blocks(sec_items.get(k, []))),
        })

    # ---- office holders: the annalistic leftovers turn into a register
    register, appendix = build_register(overflow, year_list)

    # ---- appendix: everything a chapter could not plausibly hold
    app_sections = []
    for k, items in group_by_key(appendix):
        e = outline[k]
        blocks = build_blocks(items)
        if not blocks:
            continue
        app_sections.append({
            "number": "A." + e["number"], "title": e["title"], "page": e["page"],
            "level": 2, "part": "17", "slug": "anhang-" + slugify(e["title"]),
            "blocks": blocks, "origin": e["number"],
        })
    app_sections.sort(key=lambda s: -len(s["blocks"]))

    # ---- assemble parts
    parts = []
    for p in parts_meta:
        own = [s for s in sections if s["part"] == p["number"]]
        own.sort(key=lambda s: tuple(int(x) for x in s["number"].split(".")))
        parts.append({**p, "sections": own,
                      "page": min((s["page"] for s in own), default=None)})
    if app_sections:
        parts.append({"number": "17", "slug": "anhang", "title": "Anhang",
                      "sections": app_sections, "page": None})
    sections = sections + app_sections

    covered = sum(len(s["blocks"]) for s in sections)
    covered += sum(len(g["blocks"]) for y in year_list for g in y["groups"])
    images = [b["file"] for s in sections for b in s["blocks"] if b["type"] == "image"]
    images += [b["file"] for y in year_list for g in y["groups"]
               for b in g["blocks"] if b["type"] == "image"]

    data = {
        "parts": parts,
        "years": year_list,
        "front": build_blocks(front),
        "register": register,
        "stats": {
            "streamItems": len(body), "blocks": covered,
            "years": len(year_list), "sections": len(sections),
            "images": len(images), "distinctImages": len(set(images)),
            "officeHolders": sum(len(o["holders"]) for o in register),
            "yearFrom": year_list[0]["year"] if year_list else None,
            "yearTo": year_list[-1]["year"] if year_list else None,
        },
    }
    (DATA / "content.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data["stats"], indent=2, ensure_ascii=False))
    empty = [s["number"] for s in sections if not s["blocks"]]
    print(f"sections without content: {len(empty)} -> {' '.join(empty)}")


if __name__ == "__main__":
    main()
