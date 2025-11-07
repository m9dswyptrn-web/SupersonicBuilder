# scripts/pdf_meta_stamp.py
"""
Stamp PDF metadata fields with canonical URL, version, and date.
Usage:
  python scripts/pdf_meta_stamp.py --in input.pdf --out output.pdf --version v2.0.9 [--url ...]
If --out omitted, overwrite input.
"""
import argparse, sys, os, datetime as dt
from pypdf import PdfReader, PdfWriter
from repo_url import resolve

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", default=None)
    ap.add_argument("--version", required=True)
    ap.add_argument("--url", default=None)
    args = ap.parse_args()

    url = resolve(args.url)
    date = dt.date.today().isoformat()

    reader = PdfReader(args.inp)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)

    # Merge metadata
    md = reader.metadata or {}
    md = {k: v for k, v in md.items() if v is not None}
    md["/Title"] = md.get("/Title", "SonicBuilder Manual")
    md["/Author"] = "Christopher Elgin"
    md["/Producer"] = "SonicBuilder PDF Tooling"
    md["/Creator"] = "SonicBuilder PDF Tooling"
    md["/Subject"] = f"SonicBuilder — {args.version}"
    md["/Keywords"] = f"SonicBuilder,{args.version},{url}"
    md["/SonicBuilderURL"] = url
    md["/SonicBuilderVersion"] = args.version
    md["/SonicBuilderDate"] = date
    writer.add_metadata(md)

    outp = args.outp or args.inp
    with open(outp, "wb") as f:
        writer.write(f)

    print(f"Stamped {outp} with version={args.version} url={url} date={date}")

if __name__ == "__main__":
    main()
