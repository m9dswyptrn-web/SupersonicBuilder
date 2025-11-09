#!/usr/bin/env python3
from pypdf import PdfReader, PdfWriter
import argparse
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o","--output", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", default="Sonic Builder")
    ap.add_argument("--subject", default="")
    ap.add_argument("--keywords", default="")
    a = ap.parse_args()
    r = PdfReader(a.input); w = PdfWriter()
    for p in r.pages: w.add_page(p)
    meta = {"/Title": a.title, "/Author": a.author, "/Subject": a.subject}
    if a.keywords: meta["/Keywords"] = a.keywords
    w.add_metadata(meta)
    with open(a.output, "wb") as f: w.write(f)
    print("[ok] metadata stamped ->", a.output)
if __name__=="__main__": main()
