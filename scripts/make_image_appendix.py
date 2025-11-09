#!/usr/bin/env python3
import argparse, glob, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def add_plate(c, img, caption):
    w, h = letter
    margin = 0.5*inch
    iw = w - 2*margin
    ih = h - 2*margin - 0.4*inch
    y0 = margin + 0.4*inch
    try:
        c.drawImage(img, margin, y0, width=iw, height=ih, preserveAspectRatio=True, anchor='c', mask='auto')
    except Exception as e:
        c.rect(margin, y0, iw, ih, stroke=1, fill=0)
        c.drawString(margin+12, y0+ih/2, f"[image error: {e}]")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, margin, caption)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-o","--output", required=True)
    p.add_argument("--globs", nargs="+", default=["assets/pinout_*.*","assets/*rr2_gm2*.*","assets/trigger_*.*"])
    args = p.parse_args()

    imgs = []
    for g in args.globs:
        imgs.extend(sorted(glob.glob(g)))
    if not imgs:
        print("No images found for appendix.")
    c = canvas.Canvas(args.output, pagesize=letter)
    c.setTitle("Appendix: Wiring Diagrams")
    c.setAuthor("Sonic Builder")
    c.setSubject("Wiring diagrams and pinout reference appendix")
    for img in imgs:
        cap = os.path.basename(img)
        add_plate(c, img, cap)
        c.showPage()
    c.save()

if __name__ == "__main__":
    main()
