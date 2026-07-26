#!/usr/bin/env python3
"""Runs the whole data preparation and prints the quality report.

    python3 tools/pipeline.py

1. reconstruct.py   raw extraction  -> data/stream.json   (document order)
2. build_outline.py stream          -> data/outline.json  (the book's structure)
3. build_content.py stream+outline  -> data/content.json  (clean, typed content)
4. evaluate.py      quality metrics

Images are handled separately by site/scripts/optimize-images.mjs, because they
need sharp.
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ["reconstruct.py", "build_outline.py", "build_content.py", "evaluate.py"]


def main():
    for step in STEPS:
        print(f"\n=== {step} " + "=" * (60 - len(step)))
        result = subprocess.run([sys.executable, str(ROOT / step)])
        if result.returncode:
            sys.exit(result.returncode)
    print("\nNow run, in site/:  npm run images && npm run build")


if __name__ == "__main__":
    main()
