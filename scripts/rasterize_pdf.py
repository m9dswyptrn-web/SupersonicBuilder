#!/usr/bin/env python3
import argparse, os, sys
from pdf2image import convert_from_path

def main():
    ap = argparse.ArgumentParser(description="Rasterize a PDF to page PNGs")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    pages = convert_from_path(args.pdf, dpi=args.dpi)
    for i, img in enumerate(pages, start=1):
        fn = os.path.join(args.outdir, f"page_{i:04d}.png")
        img.save(fn, "PNG")
    print(f"[ok] Rasterized {len(pages)} pages -> {args.outdir}")

if __name__ == "__main__":
    main()
