#!/usr/bin/env python3
"""Runs the whole preparation, from the Word document to the site data.

    python3 tools/pipeline.py

1. extract_docx.py     the original .docx -> data/document.json (verbatim)
2. write_markdown.py   -> content/*.md, one file per chapter
3. verify_markdown.py  proves the Markdown says exactly what the docx says
4. build_site_data.py  -> data/content.json for the website

Images are handled by site/scripts/optimize-images.mjs, which needs sharp and
therefore runs from the site directory.
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ["extract_docx.py", "write_markdown.py", "verify_markdown.py", "build_site_data.py"]


def main():
    for step in STEPS:
        print(f"\n=== {step} " + "=" * (58 - len(step)))
        if subprocess.run([sys.executable, str(ROOT / step)]).returncode:
            sys.exit(f"\n{step} fehlgeschlagen")
    print("\nNun in site/:  npm run build")


if __name__ == "__main__":
    main()
