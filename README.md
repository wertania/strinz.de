# Chronik Strinz-Margarethä

A pre-rendered website for the Ortschronik of Strinz-Margarethä (Gemeinde
Hohenstein, Taunus) — 774 book pages, ~8.300 content entries, 657 plates,
and a year-by-year chronicle from 1100 to 2000.

```
assets/quelle/   the raw material: the machine dump of the original Word file
tools/           the data pipeline (Python) that turns it into usable content
data/            the prepared content (committed, regenerate with the pipeline)
site/            the Astro site; `npm run build` writes static HTML to site/dist
```

## Why there is a pipeline

The chronicle was only available as a keyword-sorted dump of a Word document
(`assets/quelle/final_docx_parser.py` produced it). That dump is unusable as a
source for a website:

* almost every **paragraph had become its own `##` heading**, so the text reads
  as 4.685 disconnected fragments;
* the paragraphs were **scattered across 20 files** by keyword matching, which
  destroyed the reading order of the book;
* sources, rubrics and images were mixed into the running text.

Two signals survived and make a reconstruction possible:

1. the **image files are numbered in document order**, so every one of the 657
   plates is an exact anchor into the original text flow;
2. the **year chronicle labels itself** — bare year paragraphs in ascending
   order across roughly half the book;
3. the book's **own table of contents** survived, giving all 215 headings with
   their page numbers.

## The pipeline

```bash
cd site && npm install
npm run dev                        # or: npm run build  -> site/dist
```

`data/*.json` is committed, so a clone builds straight away; the image
derivatives are not, so `dev` and `build` regenerate them first (~15 s once,
skipped afterwards). Only a change to the source material needs the Python
side:

```bash
python3 tools/pipeline.py          # steps 1-4 below, then the quality report
cd site && npm test                # builds, then runs data + browser tests
```

| step | script | what it does |
| --- | --- | --- |
| 1 | `tools/reconstruct.py` | merges the 20 files back into one paragraph stream. Image numbers are the initial anchors; the resulting order yields a global year→position curve, which is fed back as further anchors until it converges. |
| 2 | `tools/build_outline.py` + `tools/toc.py` | recovers the book's outline from its own table of contents, splitting `12.8.9Hagelunwetter1886523` into number, title and page. |
| 3 | `tools/build_content.py` + `tools/match_headings.py` | locates the headings in the stream, cuts the stream into sections and year entries, separates sources from prose, groups the chronicle rubrics, builds the office-holder register. |
| 4 | `tools/evaluate.py` | quality metrics (see below). |
| 5 | `site/scripts/optimize-images.mjs` | 113 MB of mixed scans → 43 MB of WebP in two sizes. |
| 6 | `astro build` | 37 static pages, no client framework. |

## How good is the reconstruction

`tools/evaluate.py` reports, on the current data:

```
headings located          : 182/215
heading order vs book page: 98.6% of pairs correct
year markers              : 525, 8 inversions (1.5%)
```

The second line is the meaningful one: the table of contents gives an
independent page number for every heading, so if the reconstructed order were
wrong, the located headings would not come out in page order.

Nothing is discarded. Text that could not be attached to a chapter with
confidence goes to `/kapitel/anhang/`; office holders and population figures
that lost their year go to `/register/`, where years are only shown when they
are internally consistent. `/ueber/` explains all of this to the reader.

## The site

Astro, static output, no client-side framework. One small inline script for the
light/dark toggle and one for the search, which loads `/suchindex.json` and runs
entirely in the browser.

```
/                     Startseite
/chronik/             the 15 epochs of the year chronicle
/chronik/1800-1899/   one page per epoch
/kapitel/             all chapters plus the full table of contents
/kapitel/geschichten/ one page per part of the book
/register/            office holders and population figures
/bilder/              all 657 plates
/suche/               full-text search
/ueber/               editorial note on sources and method
```

## Tests

`site/tests/data.test.mjs` guards the pipeline — chronology, no extraction
artefacts, no duplicates, every referenced image present, nothing silently
dropped. `site/tests/site.test.mjs` drives the built site in Chromium: every
internal link resolves, no console errors, no broken images, search works, no
horizontal scrolling on a phone, dark mode applies, metadata present.

## Deployment

`site/dist` is a plain directory of static files. The `Dockerfile` in the repo
root builds everything from source and serves the result with nginx.
