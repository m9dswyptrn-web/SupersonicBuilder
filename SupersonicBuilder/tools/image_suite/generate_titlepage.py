#!/usr/bin/env python3
"""
Generate Title Page
Script #02 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python generate_titlepage.py --out out/{stem}.png
python generate_titlepage.py --title 'SonicBuilder Manual' --version 'v2.0.9' --out out/title.png

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

def render(title: str, version: str, w=2550, h=3300):
    img = canvas(w, h, (10,12,16,255))
    d = ImageDraw.Draw(img)
    ft = font(120, True); fs = font(60, False)
    tw, th = d.textsize(title, font=ft)
    d.text(((w-tw)//2, h//3 - th//2), title, font=ft, fill=FG)
    vw, vh = d.textsize(version, font=fs)
    d.text(((w-vw)//2, h//3 + th), version, font=fs, fill=FG_MUTED)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--w', type=int, default=2550)
    ap.add_argument('--h', type=int, default=3300)
    A = ap.parse_args()
    save(render(A.title, A.version, A.w, A.h), Path(A.out))

if __name__ == '__main__':
    main()
