#!/usr/bin/env python3
"""
Generate DANGER Callout
Script #12 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python callout_danger.py --out out/{stem}.png
python callout_danger.py --head 'Danger' --body 'High voltage area' --out out/danger.png

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

def render(head: str, body: str, w=1600, h=600):
    img = canvas(w, h, PANEL_BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 16, h], fill=(220,53,69,255))
    ft = font(56, True); fs = font(34, False)
    d.text((48, 40), "DANGER — " + head, font=ft, fill=FG)
    import textwrap
    y = 130
    for ln in textwrap.wrap(body, width=70):
        d.text((48, y), ln, font=fs, fill=FG_MUTED); y += 46
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--head', required=True)
    ap.add_argument('--body', required=True)
    ap.add_argument('--out', required=True)
    A = ap.parse_args()
    save(render(A.head, A.body), Path(A.out))

if __name__ == '__main__':
    main()
