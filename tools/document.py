"""Shared access to the reconstructed document.

The book's own table of contents survived the extraction and is the backbone of
everything downstream, so it has to be found reliably rather than at a fixed
offset: the reconstruction may place a few stray paragraphs in between.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# "12.8.9Hagelunwetter1886523" - number, title and page number all run together
TOC_LINE = re.compile(r"^\d+(?:\.\d+)*[^\s\d].{0,90}\d{1,4}$")
GAP = 20          # stray items tolerated inside the table of contents


def load_stream():
    return json.loads((DATA / "stream.json").read_text(encoding="utf-8"))


def split_toc(stream):
    """Return (toc_items, body_items).

    The table of contents starts at the paragraph "Inhalt" and runs until its
    lines stop coming; anything that looks like one of its lines is kept out of
    the body wherever it turns up.
    """
    start = next(
        (i for i, it in enumerate(stream)
         if it["type"] == "p" and it["text"].strip() == "Inhalt"),
        0,
    )
    toc_idx, misses = [], 0
    for i in range(start + 1, len(stream)):
        it = stream[i]
        if it["type"] == "p" and TOC_LINE.match(it["text"].strip()):
            toc_idx.append(i)
            misses = 0
        else:
            misses += 1
            if misses > GAP:
                break
    end = toc_idx[-1] if toc_idx else start
    # stray table-of-contents lines before "Inhalt" belong to it as well
    for i in range(0, start):
        it = stream[i]
        if it["type"] == "p" and TOC_LINE.match(it["text"].strip()):
            toc_idx.append(i)

    skip = set(toc_idx) | {start}
    toc = [stream[i] for i in sorted(toc_idx)]
    body = [it for i, it in enumerate(stream) if i not in skip]
    return toc, body, end
