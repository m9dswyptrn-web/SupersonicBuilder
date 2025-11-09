#!/usr/bin/env python3
"""
Generate QR Code Label
Script #04 — SonicBuilder Image Suite (Dark)
Generated: 2025-10-29 13:56:20 UTC

Usage:
  python generate_qr_label.py --out out/{stem}.png
python generate_qr_label.py --text 'https://github.com/m9dswyptrn-web/SonicBuilder' --label 'Repo' --out out/qr_repo.png

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

import qrcode
def render(text: str, label: str=None, size=800):
    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(text); qr.make(fit=True)
    img_qr = qr.make_image(fill_color='white', back_color='black').convert('RGBA')
    pad = 40
    w = img_qr.size[0] + pad*2
    h = img_qr.size[1] + (pad*2 if not label else pad*3)
    img = canvas(w, h, PANEL_BG)
    img.paste(img_qr, (pad, pad), img_qr)
    if label:
        d = ImageDraw.Draw(img)
        ft = font(28, False)
        tw, th = d.textsize(label, font=ft)
        d.text(((w-tw)//2, h - th - pad//2), label, font=ft, fill=FG_MUTED)
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--label', default=None)
    ap.add_argument('--out', required=True)
    A = ap.parse_args()
    save(render(A.text, A.label), Path(A.out))

if __name__ == '__main__':
    main()
