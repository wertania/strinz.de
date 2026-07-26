#!/usr/bin/env python3
"""Step 2a: recover the chronicle's outline from its own table of contents.

The TOC survived the extraction, but section numbers, titles and page numbers
are glued together ('12.8.9Hagelunwetter1886523') and the entries for 7.3-7.15
plus chapter 8 were scattered into other category files.  This script repairs
all of that and writes data/outline.json - the authoritative structure of the
774-page book.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from toc import parse_toc  # noqa: E402
from document import load_stream, split_toc  # noqa: E402

# Entries whose number/title/page split cannot be recovered mechanically,
# because the title itself begins or ends with a year.
PATCHES = {
    "7.2": ("Chronik von 0 – 999", 36),
    "8": ("Strinzer Chronisten", 405),
    "8.1": ("Pfarrer Ludwig Schmidtborn", 405),
    "8.1.1": ("Schmidtborns Thesen unter der Lupe", 407),
    "10.16": ("1. Mai", 454),
    "12.4.4": ("Strinzer Bürger des Jahres 1499", 479),
    "12.6.8": ("Die Strinzer von 1681", 491),
    "12.7.2": ("Strinz im Jahre 1782", 502),
    "12.8.9": ("Hagelunwetter 1886", 523),
    "12.8.14": ("Patriotische Feiern 1871", 531),
    "12.11.1": ("Die Gemeinde im Jahre 1935", 632),
    "12.11.15": ("Das Sonder Kfz", 666),
}

# The year-chronicle sub-chapters were scattered into other files by the
# keyword categoriser; they are re-inserted verbatim here.
CHRONIK_PARTS = [
    ("7.1", "Chronik vor Christi Geburt", 35, None, 0),
    ("7.2", "Chronik von 0 – 999", 36, 0, 999),
    ("7.3", "Chronik von 1000 – 1199", 40, 1000, 1199),
    ("7.4", "Chronik von 1200 – 1299", 41, 1200, 1299),
    ("7.5", "Chronik von 1300 – 1399", 42, 1300, 1399),
    ("7.6", "Chronik von 1400 – 1499", 46, 1400, 1499),
    ("7.7", "Chronik von 1500 – 1599", 60, 1500, 1599),
    ("7.8", "Chronik von 1600 – 1699", 75, 1600, 1699),
    ("7.9", "Chronik von 1700 – 1799", 105, 1700, 1799),
    ("7.10", "Chronik von 1800 – 1899", 140, 1800, 1899),
    ("7.11", "Chronik von 1900 – 1914", 220, 1900, 1914),
    ("7.12", "Der Erste Weltkrieg 1914 – 1918", 238, 1915, 1918),
    ("7.13", "Von 1918 bis 1933", 263, 1919, 1933),
    ("7.14", "Von 1933 bis 1945", 294, 1934, 1945),
    ("7.15", "Von 1946 bis 2000", 316, 1946, 2100),
]

PARTS = {
    "1": ("vorwort", "Vorwort"),
    "2": ("ortsname", "Der Ortsname"),
    "3": ("begriffe", "Begriffsbestimmungen"),
    "4": ("mundart", "Die heimatliche Mundart"),
    "5": ("namenskunde", "Namenskunde"),
    "6": ("wappen", "Wappen und Siegel"),
    "7": ("chronik", "Chronik nach Jahren"),
    "8": ("chronisten", "Strinzer Chronisten"),
    "9": ("gemarkung", "Strinzer Gemarkung"),
    "10": ("brauchtum", "Strinzer Brauchtum"),
    "11": ("liedgut", "Liedgut"),
    "12": ("geschichten", "Strinzer Geschichten"),
    "13": ("berufe", "Alte Strinzer Berufe"),
    "14": ("baeuerliches-leben", "Bäuerliches Leben"),
    "15": ("zinkenmuehle", "Die Zinkenmühle"),
    "16": ("dank", "Dank"),
}


def sort_key(number):
    return tuple(int(x) for x in number.split("."))


def main():
    toc_items, _, _ = split_toc(load_stream())
    print(f"table of contents: {len(toc_items)} lines")
    entries = {}
    for e in parse_toc(toc_items):
        entries[e["number"]] = {"number": e["number"], "title": e["title"], "page": e["page"]}
    for num, (title, page) in PATCHES.items():
        entries[num] = {"number": num, "title": title, "page": page}
    for num, title, page, *_ in CHRONIK_PARTS:
        entries[num] = {"number": num, "title": title, "page": page}

    outline = []
    for num in sorted(entries, key=sort_key):
        e = entries[num]
        e["level"] = num.count(".") + 1
        e["part"] = num.split(".")[0]
        outline.append(e)

    data = {
        "parts": [{"number": n, "slug": s, "title": t} for n, (s, t) in
                  sorted(PARTS.items(), key=lambda kv: int(kv[0]))],
        "outline": outline,
        "chronikParts": [{"number": n, "title": t, "page": p, "from": a, "to": b}
                         for n, t, p, a, b in CHRONIK_PARTS],
    }
    (ROOT / "data/outline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"outline: {len(outline)} entries, {len(PARTS)} parts")
    bad = [e for e in outline if not e["title"] or e["page"] is None]
    print("incomplete entries:", bad)


if __name__ == "__main__":
    main()
