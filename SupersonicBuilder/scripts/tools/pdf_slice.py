#!/usr/bin/env python3
import sys, os, glob
from PyPDF2 import PdfReader, PdfWriter

def slice_pdf(in_path, out_path, max_pages):
    try:
        r = PdfReader(in_path)
        w = PdfWriter()
        for i in range(min(max_pages, len(r.pages))):
            w.add_page(r.pages[i])
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            w.write(f)
        print(f"[OK] {os.path.basename(in_path)} -> {out_path} ({max_pages}p)")
    except Exception as e:
        print(f"[WARN] skip {in_path}: {e}")

def main():
    if len(sys.argv) < 4:
        print("Usage: pdf_slice.py <src_dir> <max_pages> <dst_dir>")
        sys.exit(2)
    src = sys.argv[1]
    max_pages = int(sys.argv[2])
    dst = sys.argv[3]
    os.makedirs(dst, exist_ok=True)
    pdfs = glob.glob(os.path.join(src, "*.pdf")) + glob.glob(os.path.join(src, "*/*.pdf"))
    if not pdfs:
        print("[INFO] No PDFs found in dist/. That's OK if CI-only builds; run a local build first.")
        return
    for p in pdfs:
        name = os.path.splitext(os.path.basename(p))[0]
        out = os.path.join(dst, f"{name}_preview.pdf")
        slice_pdf(p, out, max_pages)

if __name__ == "__main__":
    main()
