#!/usr/bin/env python3
import argparse, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode

BG       = (12,14,18)      # dark
PANEL    = (20,24,32)
ACCENT   = (0,173,239)
FG       = (225,235,245)
FG_MUTED = (170,190,210)

def font(size=36, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def qr_img(text):
    qr = qrcode.QRCode(border=1, box_size=6)
    qr.add_data(text); qr.make(fit=True)
    return qr.make_image(fill_color="white", back_color="black").convert("RGBA")

def render_index(entries, w=2550, h=3300, cols=2, pad=60, prefix=""):
    rows = math.ceil(len(entries)/cols)
    cell_w = (w - (cols+1)*pad)//cols
    cell_h = 220
    page = Image.new("RGB", (w,h), BG)
    d = ImageDraw.Draw(page)
    ft = font(54, True); fs = font(36, False)
    d.rectangle([0,0,w,180], fill=PANEL)
    d.rectangle([0,176,w,184], fill=ACCENT)
    d.text((pad, 70), "Appendix — Wiring Diagram Index", font=ft, fill=FG)
    y = 230
    i = 0
    for name, page_no, slug in entries:
        c = i % cols; r = i // cols
        x0 = pad + c*(cell_w + pad)
        y0 = y + r*(cell_h + 18)
        d.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], outline=ACCENT, width=3)
        d.text((x0+24, y0+24), f"{page_no:03d} — {name}", font=fs, fill=FG_MUTED)
        qr = qr_img(prefix + slug)
        page.paste(qr, (x0 + cell_w - qr.size[0] - 20, y0 + 20), qr)
        i += 1
    return page

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-out", required=True)
    ap.add_argument("--entries", nargs="+", help="triplets name:page:slug")
    ap.add_argument("--qr-prefix", default="")
    A = ap.parse_args()
    entries = []
    if A.entries:
        for e in A.entries:
            name, page, slug = e.split(":", 2)
            entries.append((name, int(page), slug))
    else:
        entries = [("GM 44-pin Main", 112, "gm44pin.pdf"),
                   ("Rear Cam Power", 118, "rear_cam_power.pdf")]
    page = render_index(entries, prefix=A.qr_prefix)
    out = Path(A.index_out); out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out)
    print("✅ index image (dark)", out)

if __name__ == "__main__":
    main()
