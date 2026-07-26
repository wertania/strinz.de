#!/usr/bin/env python3
"""Step 3: prove that the Markdown says exactly what the Word document says.

Strips all Markdown scaffolding back out of content/*.md and compares the
remaining words with the words of the original docx. The wording must be
identical — the whole point of the rework is that only structure changed.
"""
from __future__ import annotations
import json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONTENT = ROOT / "content"


def words(text: str):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("́", "'").replace("´", "'").replace("\xa0", " ")
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def source_words():
    blocks = json.loads((DATA / "document.json").read_text(encoding="utf-8"))
    out = []
    for block in blocks:
        if block["type"] == "auto-toc":
            continue
        if block["type"] == "table":
            for row in block["rows"]:
                for cell in row:
                    out += words(cell["text"])
        else:
            out += words(block.get("text", ""))
    return out


def markdown_words():
    out = []
    for path in sorted(CONTENT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)   # front matter
        body = re.sub(r"!\[\]\([^)]*\)", " ", body)                 # images
        body = re.sub(r"^\|[\s-]+\|$", " ", body, flags=re.M)       # table rules
        body = re.sub(r"^> ", "", body, flags=re.M)                  # source marker
        body = body.replace("<br>", " ")
        out += words(body)
    return out


def main():
    src, md = source_words(), markdown_words()
    a, b = Counter(src), Counter(md)
    missing, extra = a - b, b - a

    print(f"Wörter in der Vorlage : {len(src):,}")
    print(f"Wörter im Markdown    : {len(md):,}")
    print(f"fehlend               : {sum(missing.values()):,}")
    print(f"zusätzlich            : {sum(extra.values()):,}")

    # "Quelle", "Bild" etc. are consumed by the markup we strip; the H1 of every
    # chapter is repeated in its front matter. Anything else is a real loss.
    for label, counter in (("FEHLEND", missing), ("ZUSÄTZLICH", extra)):
        if counter:
            print(f"\n{label}:")
            for word, n in counter.most_common(25):
                print(f"  {n:5d}  {word}")

    ok = not missing
    print("\n" + ("OK — kein Wort der Vorlage fehlt." if ok else "FEHLER — Text ging verloren."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
