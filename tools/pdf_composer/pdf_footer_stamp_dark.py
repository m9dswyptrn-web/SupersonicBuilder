#!/usr/bin/env python3
import argparse, io
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

BG   = (12,14,18)
PANEL= (20,24,32)
ACC  = (0,173,239)
FG   = (225,235,245)
MUTED= (170,190,210)

def font(size=28, bold=False):
    try:
        from PIL import ImageFont
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def stamp_images(imgs, left, center, right, h=90):
    out = []
    for im in imgs:
        W,H = im.size
        page = im.convert("RGBA")
        bar = Image.new("RGBA", (W,h), PANEL+(255,))
        d = ImageDraw.Draw(bar)
        d.rectangle([0,h-6,W,h], fill=ACC+(255,))
        fl = font(28, True); fs = font(24, False)
        d.text((30, 22), left, font=fl, fill=FG)
        twc, thc = d.textsize(center, font=fs)
        d.text(((W-twc)//2, 24), center, font=fs, fill=MUTED)
        twr, thr = d.textsize(right, font=fs)
        d.text((W - twr - 30, 24), right, font=fs, fill=MUTED)
        page.paste(bar, (0, H-h), bar)
        out.append(page.convert("RGB"))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--left", default="SonicBuilder • CERT #0001")
    ap.add_argument("--center", default="v0.0.0")
    ap.add_argument("--right", default="© SonicBuilder")
    A = ap.parse_args()
    images = convert_from_path(A.src, dpi=200)
    stamped = stamp_images(images, A.left, A.center, A.right)
    out = Path(A.out); out.parent.mkdir(parents=True, exist_ok=True)
    stamped[0].save(out, save_all=True, append_images=stamped[1:], quality=92)
    print("✅ footer-stamped", out)

if __name__ == "__main__":
    main()
