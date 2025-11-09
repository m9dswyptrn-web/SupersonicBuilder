#!/usr/bin/env python3
"""
Generate 4x4 Grid Sheet
Script #40 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python grid_4x4.py --out out/{stem}.png
python grid_4x4.py --out out/grid4x4.png

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

def render(items, cols=4, rows=4, cell_w=900, cell_h=600, pad=30):
    n = len(items); w = cols*cell_w + (cols+1)*pad; h = rows*cell_h + (rows+1)*pad
    img = canvas(w, h, DARK_BG); d = ImageDraw.Draw(img); ft = font(42, True)
    for i in range(min(n, cols*rows)):
        r = i//cols; c = i%cols
        x0 = pad + c*(cell_w+pad); y0 = pad + r*(cell_h+pad)
        d.rectangle([x0, y0, x0+cell_w, y0+cell_h], outline=LINE, width=3)
        d.text((x0+24, y0+24), f"{i+1:02d}. {items[i]}", font=ft, fill=FG)
        d.rectangle([x0, y0+cell_h-10, x0+cell_w, y0+cell_h], fill=ACCENT)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--items', required=True, help='comma-separated')
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--rows', type=int, default=4)
    ap.add_argument('--out', required=True)
    A = ap.parse_args()
    items = [s.strip() for s in A.items.split(',') if s.strip()]
    save(render(items, A.cols, A.rows), Path(A.out))

if __name__ == '__main__':
    main()
