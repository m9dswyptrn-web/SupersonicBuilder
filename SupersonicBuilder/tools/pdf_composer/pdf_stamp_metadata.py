#!/usr/bin/env python3
import argparse
from pathlib import Path
from pikepdf import Pdf, String

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--subject", default=None)
    ap.add_argument("--keywords", default=None)
    ap.add_argument("--creator", default="SonicBuilder PDF Composer (Dark)")
    ap.add_argument("--producer", default="pikepdf")
    A = ap.parse_args()

    src = Path(A.src); out = Path(A.out); out.parent.mkdir(parents=True, exist_ok=True)
    with Pdf.open(src) as pdf:
        info = pdf.docinfo
        if A.title: info["/Title"] = String(A.title)
        if A.author: info["/Author"] = String(A.author)
        if A.subject: info["/Subject"] = String(A.subject)
        if A.keywords: info["/Keywords"] = String(A.keywords)
        info["/Creator"]  = String(A.creator)
        info["/Producer"] = String(A.producer)
        pdf.save(out)
    print("✅ stamped", out)

if __name__ == "__main__":
    main()
