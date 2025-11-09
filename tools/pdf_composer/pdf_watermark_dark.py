#!/usr/bin/env python3
import argparse
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def font(size=260, bold=True):
    try:
        from PIL import ImageFont
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def apply_watermark(imgs, text):
    out = []
    for im in imgs:
        W,H = im.size
        overlay = Image.new("RGBA", (W,H), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        ft = font()
        tw, th = d.textsize(text, font=ft)
        # diagonal
        d.text(((W-tw)//2, (H-th)//2), text, font=ft, fill=(255,255,255,28))
        out.append(Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB"))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", default="DRAFT")
    A = ap.parse_args()
    images = convert_from_path(A.src, dpi=200)
    wm = apply_watermark(images, A.text)
    out = Path(A.out); out.parent.mkdir(parents=True, exist_ok=True)
    wm[0].save(out, save_all=True, append_images=wm[1:], quality=92)
    print("✅ watermark applied", out)

if __name__ == "__main__":
    main()
