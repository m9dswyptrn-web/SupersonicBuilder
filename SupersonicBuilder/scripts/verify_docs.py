#!/usr/bin/env python3
import sys
from pathlib import Path
try:
    from pikepdf import Pdf
except Exception:
    Pdf = None

def main():
    if len(sys.argv) < 2:
        print("usage: verify_docs.py <pdf>"); return 1
    p = Path(sys.argv[1])
    if not p.exists():
        print("missing:", p); return 2
    print("File:", p, "size:", p.stat().st_size, "bytes")
    if Pdf:
        with Pdf.open(p) as pdf:
            print("Pages:", len(pdf.pages))
            print("DocInfo keys:", list(pdf.docinfo.keys()))
    print("✅ verify ok")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
