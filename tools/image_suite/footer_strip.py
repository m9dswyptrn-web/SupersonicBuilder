#!/usr/bin/env python3
"""
Generate Footer Strip
Script #06 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python footer_strip.py --out out/{stem}.png
python footer_strip.py --text '© SonicBuilder' --out out/footer.png

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

def render(text: str, w=1920, h=480):
    img = canvas(w, h, PANEL_BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, h-8, w, h], fill=ACCENT)
    ft = font(64, True)
    tw, th = d.textsize(text, font=ft)
    d.text(((w-tw)//2, (h-th)//2-10), text, font=ft, fill=FG)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--w', type=int, default=1920)
    ap.add_argument('--h', type=int, default=480)
    A = ap.parse_args()
    save(render(A.text, A.w, A.h), Path(A.out))

if __name__ == '__main__':
    main()
