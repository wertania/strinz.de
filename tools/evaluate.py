#!/usr/bin/env python3
"""Quality metrics for the reconstruction.

The single most telling check: the chronicle's own table of contents gives a
page number for every heading.  If the reconstruction is faithful, headings
found in the stream must appear in page order.
"""
import json, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from match_headings import match, YEAR_RE  # noqa: E402
from document import load_stream, split_toc  # noqa: E402


def kendall(pairs):
    """Fraction of anchor pairs that are in the right order."""
    ok = bad = 0
    for a in range(len(pairs)):
        for b in range(a + 1, len(pairs)):
            if pairs[a][1] == pairs[b][1]:
                continue
            if pairs[a][1] < pairs[b][1]:
                ok += 1
            else:
                bad += 1
    return ok / max(1, ok + bad)


def main():
    meta = json.loads((ROOT / "data/outline.json").read_text(encoding="utf-8"))
    _, body, _ = split_toc(load_stream())
    outline = meta["outline"]

    hits, _ = match(body, outline)
    pairs = sorted((i, outline[k]["page"]) for k, i in hits.items())
    years = [int(it["text"].strip().rstrip(".")) for it in body
             if it["type"] == "p" and YEAR_RE.match(it["text"].strip())]
    inv = sum(1 for a, b in zip(years, years[1:]) if b < a)
    ties = Counter(round(it["pos"], 2) for it in body).most_common(1)[0]

    print(f"headings located          : {len(hits)}/{len(outline)}")
    print(f"heading order vs book page: {kendall(pairs):.1%} of pairs correct")
    print(f"year markers              : {len(years)}, {inv} inversions "
          f"({inv / max(1, len(years)):.1%})")
    print(f"largest tie group         : {ties[1]} items at pos {ties[0]}")


if __name__ == "__main__":
    main()
