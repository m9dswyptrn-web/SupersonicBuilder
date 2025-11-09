#!/usr/bin/env python3
"""
two_up_raster.py — SonicBuilder
Renders a 2-up sheet by rasterizing a source PDF page into two card slots.
Adds footer with SB_REPO_URL and optional QR.
Usage:
  python scripts/two_up_raster.py --in input.pdf --out output_two_up.pdf [--qr]
Env:
  SB_REPO_URL  (falls back to Replit URL if unset)
"""
import os, argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_path

DEFAULT_URL = os.environ.get("SB_REPO_URL","https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--qr", action="store_true", help="draw QR in footer")
    args = ap.parse_args()

    # Rasterize first page
    images = convert_from_path(args.inp, dpi=args.dpi, first_page=1, last_page=1)
    if not images:
        raise SystemExit("No pages rendered")
    im = images[0]

    W,H = letter
    c = canvas.Canvas(args.outp, pagesize=letter)

    # layout: two cards stacked (2-up portrait)
    margins = 0.5*inch
    card_h = (H - 3*margins) / 2.0
    card_w = W - 2*margins

    # draw top card
    c.drawImage(ImageReader(im), margins, margins+card_h+margins, width=card_w, height=card_h, preserveAspectRatio=True, mask='auto')
    # draw bottom card
    c.drawImage(ImageReader(im), margins, margins, width=card_w, height=card_h, preserveAspectRatio=True, mask='auto')

    # footers with SB_REPO_URL & optional QR code (bottom card only)
    c.setFont("Helvetica", 8); c.setFillColor(colors.black)
    c.drawCentredString(W/2.0, margins-10, f"SonicBuilder • {DEFAULT_URL}")

    if args.qr:
        try:
            import qrcode
            qr = qrcode.make(DEFAULT_URL)
            c.drawImage(ImageReader(qr.get_image()), W-1.2*inch, margins-1.1*inch, width=0.8*inch, height=0.8*inch, mask='auto')
        except Exception:
            pass

    c.showPage(); c.save()

if __name__ == "__main__":
    main()
