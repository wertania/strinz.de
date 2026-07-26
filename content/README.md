# Die Chronik als Markdown

Dieser Ordner ist ein vollständiger, eigenständiger Export der Ortschronik von
Strinz-Margarethä: je eine Markdown-Datei pro Kapitel, dazu in `images/` alle
714 Bildtafeln des Originals. Die Bildverweise sind relativ, der Ordner lässt
sich also so wie er ist kopieren, weitergeben oder in einem beliebigen
Markdown-Betrachter öffnen.

| Datei | Kapitel |
| --- | --- |
| `00-titelei.md` | Titelseite |
| `01-vorwort.md` | Vorwort |
| `02-woher-strinz-margarethae-seinen-namen-hat.md` | Woher Strinz-Margarethä seinen Namen hat |
| `03-begriffsbestimmungen.md` | Begriffsbestimmungen |
| `04-die-heimatliche-mundart.md` | Die heimatliche Mundart |
| `05-namenskunde.md` | Namenskunde |
| `06-wappen-und-siegel.md` | Wappen und Siegel |
| `07-chronik-nach-jahren.md` | Chronik nach Jahren |
| `08-strinzer-chronisten.md` | Strinzer Chronisten |
| `09-strinzer-gemarkung.md` | Strinzer Gemarkung |
| `10-strinzer-brauchtum.md` | Strinzer Brauchtum |
| `11-liedgut.md` | Liedgut |
| `12-strinzer-geschichten.md` | Strinzer Geschichten |
| `13-alte-strinzer-berufe.md` | Alte Strinzer Berufe |
| `14-baeuerliches-leben.md` | Bäuerliches Leben |
| `15-die-zinkenmuehle.md` | Die Zinkenmühle |
| `16-presseartikel.md` | Presseartikel |
| `17-dank.md` | Dank |

## Herkunft

Erzeugt aus `assets/quelle/file/` — der Word-Datei „Strinzer Chronik
überarbeitet.docx", Stand 02.12.2020, von Frank Schwarzer.

**Am Wortlaut wurde nichts geändert.** Rechtschreibung, Zeichensetzung und die
Eigenheiten der zitierten älteren Quellen stehen unverändert. Bearbeitet wurde
nur die Struktur, und nur dort, wo die Word-Datei sie nicht selbst mitbringt —
Jahreszahlen und Rubriken der Jahreschronik, die Wortpaare des
Mundart-Wörterbuchs, Strophen, Aufzählungen, Quellenangaben und
Bildunterschriften. Was genau, steht im
[README des Projekts](../README.md#what-the-structural-work-consists-of).

`tools/verify_markdown.py` vergleicht nach jedem Lauf sämtliche Wörter dieses
Exports mit denen der Word-Datei — 150.727 zu 150.727, ohne Abweichung.

## Neu erzeugen

```bash
python3 tools/pipeline.py
```

Die Dateien in diesem Ordner werden dabei überschrieben; Änderungen gehören
deshalb in die Word-Datei oder in `tools/write_markdown.py`, nicht hierher.
