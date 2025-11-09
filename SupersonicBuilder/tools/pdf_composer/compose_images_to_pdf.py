#!/usr/bin/env python3
import argparse, glob
from pathlib import Path
from PIL import Image

PAPER_SIZES = {"Letter": (2550,3300), "A4": (2480,3508)}  # 300dpi

def fit_and_center(img: Image.Image, page_size, margin):
    W,H = page_size; box_w = W-2*margin; box_h = H-2*margin
    img = img.convert("RGB")
    iw, ih = img.size
    scale = min(box_w/iw, box_h/ih)
    new = img.resize((int(iw*scale), int(ih*scale)), Image.LANCZOS)
    page = Image.new("RGB", (W,H), "white")
    page.paste(new, ((W-new.size[0])//2, (H-new.size[1])//2))
    return page

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inputs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--page", default="Letter", choices=PAPER_SIZES.keys())
    ap.add_argument("--margin", type=int, default=48)
    A = ap.parse_args()
    paths = []
    for pat in A.inputs:
        paths += glob.glob(pat)
    if not paths:
        raise SystemExit("No input images found.")
    pages = [fit_and_center(Image.open(p), PAPER_SIZES[A.page], A.margin) for p in paths]
    out = Path(A.out); out.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out, save_all=True, append_images=pages[1:], quality=95)
    print("✅ wrote", out)

if __name__ == "__main__":
    main()
