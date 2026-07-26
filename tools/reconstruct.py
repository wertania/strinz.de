#!/usr/bin/env python3
"""Step 1: reconstruct the original paragraph stream of the chronicle.

The upstream extraction (assets/quelle/final_docx_parser.py) walked the docx
paragraph by paragraph and dropped every paragraph into one of 20 keyword-picked
files.  Order *within* a file survived; order *between* files did not.

Two signals let us merge the 20 streams back together:

  * the docx media files are numbered in document order, so every image
    reference is an exact global anchor;
  * the year chronicle - roughly half the book - labels itself with bare year
    paragraphs that run from the middle ages to 2000.

We start from the image anchors, derive a global "year -> position" curve from
the resulting order, feed those years back in as extra anchors and repeat.  A
handful of passes is enough for the curve to stop moving.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/quelle/final_markdown"
OUT = ROOT / "data"

IMG_RE = re.compile(r"!\[Image\]\(images/(image(\d+)\.[a-zA-Z]+)\)")
YEAR_RE = re.compile(r"^(1[0-9]{3}|20[0-2][0-9])\.?$")
PASSES = 6


def parse_file(path: Path):
    raw = re.sub(r"\A#\s+.*\n", "", path.read_text(encoding="utf-8"))
    blocks = []
    for chunk in raw.split("\n---\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        paras, images = [], []
        for para in chunk.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            m = IMG_RE.fullmatch(para)
            if m:
                images.append((m.group(1), int(m.group(2))))
                continue
            para = re.sub(r"\A#+\s*", "", para).strip()
            if para:
                paras.append(para)
        if paras or images:
            year = None
            for p in paras:
                if YEAR_RE.match(p.strip()):
                    year = int(p.strip().rstrip("."))
                    break
            blocks.append({"paras": paras, "images": images, "year": year})
    return blocks


def make_monotonic(anchors):
    """Keep the largest subset of anchors whose values never decrease.

    A greedy sweep throws away far too much here, so this is a proper longest
    non-decreasing subsequence (patience sorting with back-pointers).
    """
    if not anchors:
        return []
    tails, tail_idx, prev = [], [], [-1] * len(anchors)
    for k, (_, v) in enumerate(anchors):
        lo, hi = 0, len(tails)
        while lo < hi:                       # first tail strictly greater than v
            mid = (lo + hi) // 2
            if tails[mid] <= v:
                lo = mid + 1
            else:
                hi = mid
        if lo:
            prev[k] = tail_idx[lo - 1]
        if lo == len(tails):
            tails.append(v)
            tail_idx.append(k)
        else:
            tails[lo] = v
            tail_idx[lo] = k
    keep, k = [], tail_idx[-1]
    while k != -1:
        keep.append(anchors[k])
        k = prev[k]
    keep.reverse()
    out = {}
    for i, v in keep:
        out.setdefault(i, v)                 # one anchor per block index
    return sorted(out.items())


LO, HI = 0.0, 720.0          # the image numbering runs 1..714


def interpolate(n, anchors, default_slope=0.5):
    """Give every index 0..n-1 a float position from sparse (index, pos) anchors."""
    pos = [None] * n
    if not anchors:
        return pos
    for i, v in anchors:
        pos[i] = float(v)
    for (i0, v0), (i1, v1) in zip(anchors, anchors[1:]):
        for k in range(i0 + 1, i1):
            pos[k] = v0 + (v1 - v0) * (k - i0) / (i1 - i0)
    (fi, fv), (li, lv) = anchors[0], anchors[-1]
    slope = (lv - fv) / (li - fi) if li > fi else default_slope
    slope = max(slope, 1e-3)
    # head and tail: keep the local slope but never leave the scale, and never
    # collapse into a tie - squeeze into the remaining room instead
    if fi:
        step = min(slope, (fv - LO) / fi) if fv > LO else 1e-4
        for k in range(fi):
            pos[k] = fv - step * (fi - k)
    if li + 1 < n:
        step = min(slope, (HI - lv) / (n - li)) if HI > lv else 1e-4
        for k in range(li + 1, n):
            pos[k] = lv + step * (k - li)
    return pos


def year_curve(files, positions):
    """Median global position of every year marker, forced monotonic."""
    seen = {}
    for name, blocks in files.items():
        for i, b in enumerate(blocks):
            if b["year"] is not None and positions[name][i] is not None:
                seen.setdefault(b["year"], []).append(positions[name][i])
    curve = []
    for y in sorted(seen):
        vals = sorted(seen[y])
        curve.append((y, vals[len(vals) // 2]))
    # enforce monotonicity in the year -> position direction
    clean = []
    for y, p in curve:
        while clean and clean[-1][1] > p:
            clean.pop()
        clean.append((y, p))
    return clean


def lookup(curve, year):
    """Position of a year on the curve; outside its range we do not guess."""
    if len(curve) < 2:
        return None
    if year < curve[0][0] or year > curve[-1][0]:
        return None
    for (y0, p0), (y1, p1) in zip(curve, curve[1:]):
        if y0 <= year <= y1:
            if y1 == y0:
                return p0
            return p0 + (p1 - p0) * (year - y0) / (y1 - y0)
    return None


def main():
    files = {p.stem: parse_file(p) for p in sorted(SRC.glob("*.md")) if p.name != "README.md"}

    # pass 0: image anchors only
    positions = {}
    for name, blocks in files.items():
        anchors = make_monotonic([(i, n) for i, b in enumerate(blocks) for _, n in b["images"]])
        positions[name] = interpolate(len(blocks), anchors)

    for p in range(PASSES):
        curve = year_curve(files, positions)
        moved = 0.0
        for name, blocks in files.items():
            raw = []
            for i, b in enumerate(blocks):
                for _, n in b["images"]:
                    raw.append((i, float(n)))
                if b["year"] is not None:
                    v = lookup(curve, b["year"])
                    if v is not None:
                        raw.append((i, v))
            raw.sort()
            anchors = make_monotonic(raw)
            new = interpolate(len(blocks), anchors)
            for a, b_ in zip(positions[name], new):
                if a is not None and b_ is not None:
                    moved += abs(a - b_)
            positions[name] = new
        print(f"  pass {p + 1}: year anchors {len(curve)}, total movement {moved:,.0f}")

    merged = []
    for name, blocks in files.items():
        for i, b in enumerate(blocks):
            merged.append({
                "pos": positions[name][i] if positions[name][i] is not None else 1e9,
                "src": name, "idx": i,
                "paras": b["paras"], "images": [im for im, _ in b["images"]],
            })
    merged.sort(key=lambda b: (b["pos"], b["src"], b["idx"]))

    stream = []
    for b in merged:
        for para in b["paras"]:
            stream.append({"type": "p", "text": para, "src": b["src"], "pos": round(b["pos"], 3)})
        for im in b["images"]:
            stream.append({"type": "img", "file": im, "src": b["src"], "pos": round(b["pos"], 3)})

    OUT.mkdir(exist_ok=True)
    (OUT / "stream.json").write_text(json.dumps(stream, ensure_ascii=False), encoding="utf-8")

    years = [int(it["text"].strip().rstrip(".")) for it in stream
             if it["type"] == "p" and YEAR_RE.match(it["text"].strip())]
    inv = sum(1 for a, b in zip(years, years[1:]) if b < a)
    print(f"{len(merged)} blocks -> {len(stream)} items; "
          f"{len(years)} year markers, {inv} inversions")


if __name__ == "__main__":
    main()
