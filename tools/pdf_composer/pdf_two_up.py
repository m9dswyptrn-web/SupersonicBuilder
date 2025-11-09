#!/usr/bin/env python3
import argparse, os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image, ImageOps

def two_up_images(imgs, page_size=(2550,3300), margin=36):
    W,H = page_size
    card_w = (W - 3*margin)//2
    card_h = H - 2*margin
    pages = []
    for i in range(0, len(imgs), 2):
        page = Image.new("RGB", (W,H), "white")
        left = ImageOps.contain(imgs[i], (card_w, card_h))
        page.paste(left, (margin, (H-left.size[1])//2))
        if i+1 < len(imgs):
            right = ImageOps.contain(imgs[i+1], (card_w, card_h))
            page.paste(right, (2*margin+card_w, (H-right.size[1])//2))
        pages.append(page)
    return pages

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rasterize", action="store_true", help="Always rasterize pages (recommended)")
    A = ap.parse_args()
    # We rasterize via pdf2image for robust two-up output
    images = convert_from_path(A.src, dpi=200)
    pages = two_up_images(images)
    out = Path(A.out); out.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out, save_all=True, append_images=pages[1:], quality=92)
    print("✅ two-up", out)

if __name__ == "__main__":
    main()
