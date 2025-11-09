#!/usr/bin/env python3
"""
Generate Manual Cover (Dark / Pro)
Script #01 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python generate_cover.py --out out/{stem}.png
python generate_cover.py --title 'Chevy Sonic LTZ' --subtitle 'EOENKK + Maestro RR2' --out out/cover.png

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

def render(title: str, subtitle: str, w=2550, h=3300):
    img = canvas(w, h, DARK_BG)
    d = ImageDraw.Draw(img)
    stripe_h = int(h*0.22)
    d.rectangle([0, 0, w, stripe_h], fill=PANEL_BG)
    d.rectangle([0, stripe_h-10, w, stripe_h], fill=ACCENT)
    ft = font(150, True); fs = font(64, False)
    tw, th = d.textsize(title, font=ft)
    d.text(((w-tw)//2, int(stripe_h*0.40)-th//2), title, font=ft, fill=FG)
    sw, sh = d.textsize(subtitle, font=fs)
    d.text(((w-sw)//2, int(stripe_h*0.75)-sh//2), subtitle, font=fs, fill=FG_MUTED)
    foot = "SonicBuilder • Founder Seal • CERT #0001"
    fw, fh = d.textsize(foot, font=fs)
    d.text(((w-fw)//2, h - fh - 80), foot, font=fs, fill=FG_MUTED)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True)
    ap.add_argument('--subtitle', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--w', type=int, default=2550)
    ap.add_argument('--h', type=int, default=3300)
    A = ap.parse_args()
    save(render(A.title, A.subtitle, A.w, A.h), Path(A.out))

if __name__ == '__main__':
    main()
