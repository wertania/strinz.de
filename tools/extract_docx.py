#!/usr/bin/env python3
"""Step 1: read the original Word document losslessly into data/document.json.

Unlike the earlier extraction this keeps everything the docx actually says
about structure — paragraph styles, outline levels, tables, list levels, run
formatting and the exact position of every image — and changes not a single
character of the text. Interpretation happens later; this step only transcribes.
"""
from __future__ import annotations
import json, re, unicodedata, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "assets/quelle/file"
DATA = ROOT / "data"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

HEADING_STYLE = re.compile(r"^(?:berschrift|Heading|Überschrift)(\d)$")
TOC_STYLE = re.compile(r"^(?:Verzeichnis|TOC)(\d)$")


def open_docx():
    """The document is committed as a split zip to stay under the file size cap."""
    volumes = sorted(PARTS.glob("*.zip.0*"))
    if volumes:
        blob = b"".join(v.read_bytes() for v in volumes)
        tmp = DATA / "_chronik.zip"
        DATA.mkdir(exist_ok=True)
        tmp.write_bytes(blob)
        outer = zipfile.ZipFile(tmp)
        name = next(n for n in outer.namelist() if n.lower().endswith(".docx"))
        inner = DATA / "_chronik.docx"
        inner.write_bytes(outer.read(name))
        tmp.unlink()
        return zipfile.ZipFile(inner), inner
    docx = next(PARTS.glob("*.docx"))
    return zipfile.ZipFile(docx), None


def text_of(node) -> str:
    """Concatenate a paragraph's text exactly as Word stores it."""
    out = []
    for el in node.iter():
        tag = el.tag
        if tag == W + "t":
            out.append(el.text or "")
        elif tag == W + "tab":
            out.append("\t")
        elif tag in (W + "br", W + "cr"):
            out.append("\n")
        elif tag == W + "noBreakHyphen":
            out.append("-")
    return "".join(out)


def runs_of(node):
    """Text runs with the formatting that carries meaning for structure."""
    runs = []
    for run in node.iter(W + "r"):
        text = text_of(run)
        if not text:
            continue
        props = run.find(W + "rPr")
        style = {
            "b": props is not None and props.find(W + "b") is not None,
            "i": props is not None and props.find(W + "i") is not None,
            "u": props is not None and props.find(W + "u") is not None,
        }
        if runs and runs[-1]["b"] == style["b"] and runs[-1]["i"] == style["i"] \
                and runs[-1]["u"] == style["u"]:
            runs[-1]["text"] += text
        else:
            runs.append({"text": text, **style})
    return runs


def images_of(node, rels):
    out = []
    for blip in node.iter(A + "blip"):
        rid = blip.get(R + "embed")
        if rid and rid in rels:
            out.append(rels[rid])
    return out


def paragraph(node, rels, index):
    props = node.find(W + "pPr")
    style = None
    outline = None
    list_level = None
    numbered = False
    if props is not None:
        ps = props.find(W + "pStyle")
        style = ps.get(W + "val") if ps is not None else None
        ol = props.find(W + "outlineLvl")
        if ol is not None:
            outline = int(ol.get(W + "val"))
        num = props.find(W + "numPr")
        if num is not None:
            numbered = True
            lvl = num.find(W + "ilvl")
            list_level = int(lvl.get(W + "val")) if lvl is not None else 0

    text = text_of(node)
    imgs = images_of(node, rels)
    kind = "paragraph"
    level = None
    if style:
        m = HEADING_STYLE.match(style)
        if m:
            kind, level = "heading", int(m.group(1))
        elif TOC_STYLE.match(style):
            kind = "toc"
        elif style == "Inhaltsverzeichnisberschrift":
            kind = "toc-heading"
    if kind == "paragraph" and outline is not None and outline < 9:
        kind, level = "heading", outline + 1

    block = {"i": index, "type": kind, "text": text, "style": style}
    if level:
        block["level"] = level
    if numbered:
        block["list"] = list_level or 0
    if imgs:
        block["images"] = imgs
    runs = runs_of(node)
    if len(runs) > 1 or (runs and (runs[0]["b"] or runs[0]["i"] or runs[0]["u"])):
        block["runs"] = runs
    return block


def table(node, rels, index):
    rows = []
    for tr in node.findall(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            paras = [text_of(p) for p in tc.findall(W + "p")]
            imgs = images_of(tc, rels)
            cells.append({"text": "\n".join(paras).strip(), **({"images": imgs} if imgs else {})})
        rows.append(cells)
    return {"i": index, "type": "table", "rows": rows,
            "cols": max((len(r) for r in rows), default=0)}


def main():
    z, tmp = open_docx()
    rels = {}
    root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    for rel in root.findall(REL + "Relationship"):
        target = rel.get("Target", "")
        if target.startswith("media/"):
            rels[rel.get("Id")] = target[len("media/"):]

    body = ET.fromstring(z.read("word/document.xml")).find(W + "body")
    blocks = []
    for node in body:
        if node.tag == W + "p":
            block = paragraph(node, rels, len(blocks))
            if block["text"].strip() or "images" in block:
                blocks.append(block)
        elif node.tag == W + "tbl":
            blocks.append(table(node, rels, len(blocks)))
        elif node.tag == W + "sdt":
            # Word's auto-generated table of contents. We rebuild it from the
            # real headings, so it is noted and skipped rather than transcribed.
            entries = sum(1 for _ in node.iter(W + "p"))
            blocks.append({"i": len(blocks), "type": "auto-toc", "text": "",
                           "entries": entries})

    media = DATA / "media"
    media.mkdir(parents=True, exist_ok=True)
    written = 0
    for name in z.namelist():
        if name.startswith("word/media/"):
            target = media / Path(name).name
            if not target.exists():
                target.write_bytes(z.read(name))
            written += 1
    z.close()
    if tmp and tmp.exists():
        tmp.unlink()

    DATA.mkdir(exist_ok=True)
    (DATA / "document.json").write_text(
        json.dumps(blocks, ensure_ascii=False), encoding="utf-8")

    kinds = {}
    for b in blocks:
        key = b["type"] + (f"{b['level']}" if b.get("level") else "")
        kinds[key] = kinds.get(key, 0) + 1
    chars = sum(len(b.get("text", "")) for b in blocks)
    print(f"{len(blocks)} blocks, {chars:,} characters, {written} media files")
    for k in sorted(kinds):
        print(f"  {k:16s} {kinds[k]}")


if __name__ == "__main__":
    main()
