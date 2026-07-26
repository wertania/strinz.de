"""Parse the chronicle's own table of contents.

Its lines survived the extraction as one run-together string each:

    "12.8.9Hagelunwetter1886523"   ->  12.8.9 | Hagelunwetter 1886 | page 523

Neither the section number nor the page number is separated from the title, and
titles may themselves begin or end with a year.  The split is resolved by
requiring the section numbers to form a valid outline and the page numbers to
increase along it.
"""
from __future__ import annotations
import re

MAX_PAGE = 800


def parse_toc(toc_items):
    entries = {}
    accepted = []
    for it in toc_items:
        text = it["text"].strip() if isinstance(it, dict) else str(it).strip()
        best = _best_split(text, accepted, entries)
        if best is None:
            continue
        number, title, page = best
        entries[number] = {"number": number, "title": title, "page": page}
        accepted.append(_key(number))
    return _drop_outliers(entries)


def _best_split(text, accepted, taken):
    m = re.match(r"^(\d+(?:\.\d+)*)(.*)$", text)
    if not m:
        return None
    digits, rest = m.group(1), m.group(2)
    best, best_score = None, 0
    for number in _candidate_numbers(digits):
        leftover = digits[len(number):].lstrip(".")
        title = (leftover + rest).strip()
        pm = re.search(r"(\d+)$", title)
        if not pm:
            continue
        page = int(pm.group(1))
        title = title[: pm.start()].strip()
        if not title or not (0 < page <= MAX_PAGE):
            continue
        score = _score(_key(number), accepted, number in taken)
        if not leftover:
            score += 1.5                    # the number consumed all its digits
        if re.match(r"^\d+\.\d", title):
            score -= 2.5                    # the "title" is really another number
        score += 0.1 / len(number)          # prefer the shorter reading
        if score > best_score:
            best, best_score = (number, title, page), score
    return best


def _candidate_numbers(digits):
    parts = digits.split(".")
    out = []
    for k in range(1, len(parts) + 1):
        head = parts[:k]
        tail = head[-1]
        for cut in range(1, len(tail) + 1):     # only a prefix of the last group
            out.append(".".join(head[:-1] + [tail[:cut]]))
    return out


def _key(number):
    return tuple(int(x) for x in number.split("."))


def _score(nums, accepted, already_taken):
    if already_taken:
        return 0
    if not accepted:
        return 3 if nums in ((1,), (2,)) else 0.5
    if _follows(nums, accepted[-1]):
        return 4
    if any(_follows(nums, prev) for prev in accepted):
        return 2
    if len(nums) > 1 and any(prev == nums[:-1] for prev in accepted):
        return 1.5
    return 0.2


def _follows(nums, prev):
    if len(nums) == len(prev) and nums[:-1] == prev[:-1] and nums[-1] > prev[-1]:
        return True
    if len(nums) == len(prev) + 1 and nums[:-1] == prev and nums[-1] == 1:
        return True
    if len(nums) < len(prev) and nums[:-1] == prev[: len(nums) - 1] and nums[-1] > prev[len(nums) - 1]:
        return True
    return False


def _drop_outliers(entries):
    """Along the outline, page numbers must not go backwards."""
    ordered = sorted(entries.values(), key=lambda e: _key(e["number"]))
    keep = _longest_non_decreasing([e["page"] for e in ordered])
    return [ordered[i] for i in keep]


def _longest_non_decreasing(values):
    if not values:
        return []
    tails, tail_idx, prev = [], [], [-1] * len(values)
    for k, v in enumerate(values):
        lo, hi = 0, len(tails)
        while lo < hi:
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
    out, k = [], tail_idx[-1]
    while k != -1:
        out.append(k)
        k = prev[k]
    return sorted(out)
