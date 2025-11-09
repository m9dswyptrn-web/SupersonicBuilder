#!/usr/bin/env python3
"""
Generate Parts & Tools Image Table
Script #03 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python generate_parts_table_image.py --out out/{stem}.png
python generate_parts_table_image.py --items 'ADS-MRR2,HRN-RR-GM5,EOENKK HU' --out out/parts.png

Install deps once:
  pip install -r requirements.txt
"""
import argparse, io, math, os, sys
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

DARK_BG = (12, 14, 18, 255)
PANEL_BG = (20, 24, 32, 255)
ACCENT   = (0, 173, 239, 255)
FG       = (225, 235, 245, 255)
FG_MUTED = (170, 190, 210, 255)
LINE     = (60, 70, 90, 255)

def font(size=36, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

def save(img: Image.Image, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"✅ Wrote: {out}  size={img.size}")

def canvas(w=1920, h=1080, bg=DARK_BG):
    return Image.new("RGBA", (w, h), bg)

def render(items, cols=2, cell_w=1200, cell_h=360, pad=30):
    cols = max(1, cols)
    rows = (len(items)+cols-1)//cols
    w = cols*cell_w + (cols+1)*pad
    h = rows*cell_h + (rows+1)*pad
    img = canvas(w, h, DARK_BG)
    d = ImageDraw.Draw(img)
    ft = font(38, False)
    for idx, text in enumerate(items):
        r = idx//cols; c = idx%cols
        x0 = pad + c*(cell_w+pad)
        y0 = pad + r*(cell_h+pad)
        d.rectangle([x0, y0, x0+cell_w, y0+cell_h], outline=ACCENT, width=4)
        d.text((x0+24, y0+24), f"{idx+1:02d}. {text}", font=ft, fill=FG)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--items', help='comma-separated', required=True)
    ap.add_argument('--cols', type=int, default=2)
    ap.add_argument('--out', required=True)
    A = ap.parse_args()
    items = [s.strip() for s in A.items.split(',') if s.strip()]
    save(render(items, A.cols), Path(A.out))

if __name__ == '__main__':
    main()
