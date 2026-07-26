"""Step 2b: locate the outline's headings inside the reconstructed stream."""
from __future__ import annotations
import re, unicodedata

TOLERANCE = 400          # positions; the page axis is only roughly linear

YEAR_RE = re.compile(r"^(1[0-9]{3}|20[0-2][0-9])\.?$")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    for a, b in (("„", '"'), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9äöüß]+", "", text)


def year_mask(body, titles):
    """True for every item that sits inside a year block of the chronicle."""
    mask = [False] * len(body)
    inside = False
    for i, it in enumerate(body):
        if it["type"] == "p":
            t = it["text"].strip()
            if YEAR_RE.match(t):
                inside = True
                mask[i] = True
                continue
            if norm(t) in titles:
                inside = False
        mask[i] = inside
    return mask


def longest_increasing_match(cands):
    """Pick a strictly increasing position for as many entries as possible."""
    front = [(0, -1, None)]          # (matched so far, position, backpointer)
    for k, hits in enumerate(cands):
        added = []
        for h in hits:
            prev = max((d for d in front if d[1] < h), key=lambda d: d[0], default=None)
            if prev is not None:
                added.append((prev[0] + 1, h, (k, prev)))
        merged = {}
        for d in front + added:
            if d[1] not in merged or d[0] > merged[d[1]][0]:
                merged[d[1]] = d
        pruned, best = [], -1
        for d in sorted(merged.values(), key=lambda d: d[1]):
            if d[0] > best:
                pruned.append(d)
                best = d[0]
        front = pruned
    chosen = [None] * len(cands)
    node = max(front, key=lambda d: d[0])
    while node and node[2] is not None:
        k, prev = node[2]
        chosen[k] = node[1]
        node = prev
    return chosen


def expected_index(anchors, page):
    """Where a given book page should sit, from the anchors already trusted."""
    if len(anchors) < 2 or page is None:
        return None
    if page <= anchors[0][1]:
        return anchors[0][0]
    if page >= anchors[-1][1]:
        return anchors[-1][0]
    for (i0, p0), (i1, p1) in zip(anchors, anchors[1:]):
        if p0 <= page <= p1:
            if p1 == p0:
                return i0
            return i0 + (i1 - i0) * (page - p0) / (p1 - p0)
    return None


def second_pass(chosen, cands, outline, thematic):
    """Place the remaining headings using the page axis of the trusted ones.

    The first pass only keeps headings that are in book order, which is strict
    but leaves many out.  Those anchors give us a page-to-position curve; a
    heading that occurs several times is then resolved to the occurrence that
    lands where its page says it should.
    """
    anchors = sorted((thematic[c], outline[k]["page"])
                     for k, c in enumerate(chosen) if c is not None and outline[k]["page"])
    # keep the anchor list monotone in page order
    trimmed = []
    for i, p in anchors:
        if not trimmed or p >= trimmed[-1][1]:
            trimmed.append((i, p))
    placed = {c for c in chosen if c is not None}
    added = 0
    for k, hits in enumerate(cands):
        if chosen[k] is not None or not hits:
            continue
        want = expected_index(trimmed, outline[k]["page"])
        if want is None:
            continue
        free = [h for h in hits if h not in placed]
        if not free:
            continue
        best = min(free, key=lambda h: abs(thematic[h] - want))
        if abs(thematic[best] - want) <= TOLERANCE:
            chosen[k] = best
            placed.add(best)
            added += 1
    return chosen, added


def match(body, outline):
    """Return {outline index: body index} for the headings we can place."""
    titles = {norm(e["title"]) for e in outline if len(norm(e["title"])) >= 5}
    mask = year_mask(body, titles)
    thematic = [i for i in range(len(body)) if not mask[i]]

    occ = {}
    for k, i in enumerate(thematic):
        it = body[i]
        if it["type"] == "p":
            occ.setdefault(norm(it["text"]), []).append(k)

    cands = [occ.get(norm(e["title"]), []) if len(norm(e["title"])) >= 5 else []
             for e in outline]
    chosen = longest_increasing_match(cands)
    chosen, added = second_pass(chosen, cands, outline, thematic)
    return {k: thematic[c] for k, c in enumerate(chosen) if c is not None}, mask
