# Chronik Strinz-Margarethä

A pre-rendered website for the Ortschronik of Strinz-Margarethä (Gemeinde
Hohenstein, Taunus) — 774 book pages, 150.727 words, 691 plates, and a
year-by-year chronicle from 1100 to 2000.

```
assets/quelle/file/  the original Word document, committed as a split zip
tools/               the pipeline that turns it into content
content/             the chronicle as Markdown, one file per chapter
data/                the same content as JSON, for the site
site/                the Astro site; `npm run build` writes site/dist
```

## The rule

**The wording is never changed.** Only the structure is worked out. Every run of
the pipeline verifies this by comparing all 150.727 words of the Markdown with
those of the Word document; the build fails if a single one differs.

## Running it

Needs Node.js 22.23.4 or newer (Node 24 LTS recommended) and Python 3.

```bash
cd site && npm install
npm run dev                  # or: npm run build  -> site/dist
```

`content/*.md` and `data/*.json` are committed, so a clone builds right away.
The 714 plates are not committed twice — the first build unpacks them from the
Word document, which needs Python once. Rebuilding the content after a change
to the source document:

```bash
python3 tools/pipeline.py
cd site && npm test          # builds, then runs data + browser tests
```

| step | script | what it does |
| --- | --- | --- |
| 1 | `tools/extract_docx.py` | reads the docx verbatim into `data/document.json`: paragraph styles, outline levels, tables, list levels, run formatting and the position of every image. |
| 2 | `tools/write_markdown.py` | decides what each block *is* and writes `content/*.md`. |
| 3 | `tools/verify_markdown.py` | compares every word of the Markdown with the docx. |
| 4 | `tools/build_site_data.py` | the same classification, emitted as `data/content.json`. |
| 5 | `site/scripts/optimize-images.mjs` | 113 MB of mixed scans → WebP in two sizes. |
| 6 | `astro build` | 34 static pages, no client framework. |

## What the structural work consists of

The Word file carries its own outline — 26 chapter headings, 96 sections, 112
subsections, 27 tables — and that is used as-is. What it does not mark up is
decided in `tools/write_markdown.py`, each decision taken by reading the chapter
it applies to:

* **The year chronicle** marks its years by bold type and its rubrics
  (Obrigkeiten, Ereignisse, Statistik, Wahlen, Kirchenchronik) as bare
  paragraphs. Both become real headings.
* **The dialect dictionary** is a set of tables with two term/translation pairs
  per row and a spacer column between them. The pairs are resolved, so each word
  keeps exactly the dialect form standing next to it in the source.
* **Songs, poems and rhymes** are stored as one paragraph per line, typographically
  indistinguishable from prose. They are set as stanzas; the prose sentence
  introducing a song stays prose.
* **Enumerations** — name forms, currency tables, livestock counts, trade
  directories — were never marked up as lists and now are.
* **Source notes** are lifted out of the running text and attached to the
  paragraph they belong to, keeping their original label (Quelle, Foto, Bild).
* **Captions** — a short line directly below a plate.
* Nine paragraphs in „Keine ‚Aarstraße‘ für StM“ carry the Heading-1 style by
  mistake in the Word file and are put back to running text.

`/ueber/` explains all of this to the reader as well.

## The site

Astro, static output, no client-side framework. One inline script for the
light/dark toggle, one for the search, which loads `/suchindex.json` and runs
entirely in the browser.

```
/                            Startseite
/chronik/                    the epochs of the year chronicle
/chronik/chronik-von-1800-1899/   one page per epoch
/kapitel/                    all chapters and the full table of contents
/kapitel/strinzer-geschichten/    one page per chapter
/register/                   office holders and population figures
/bilder/                     all plates
/suche/                      full-text search
/ueber/                      editorial note on sources and method
```

## Tests

`site/tests/data.test.mjs` guards the pipeline — wording identical to the docx,
chronology intact, no export artefacts, sources separated, songs set as verse,
the dictionary paired correctly, every image present.
`site/tests/site.test.mjs` drives the built site in Chromium: every internal
link resolves, no console errors, no broken images, search works, no horizontal
scrolling on a phone, dark mode applies, metadata present.

## Deployment

`site/dist` is a plain directory of static files. The `Dockerfile` in the repo
root builds everything from the Word document and serves the result with nginx.

## Maintenance

Dependabot opens a monthly PR for npm packages, GitHub Actions and the Docker
base images; CI builds and runs the full test suite on each one. nginx serves
the site with `server_tokens off` and the security headers in
`site/security-headers.conf` (CSP, `nosniff`, no framing, referrer policy).

## License

The code — pipeline, site, tests and configuration — is released under the
[MIT License](LICENSE). The chronicle itself (text in `content/`, `data/` and
the Word document in `assets/`, and all plates) is not covered by it; its rights
stay with the authors and the respective sources.
