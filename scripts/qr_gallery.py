#!/usr/bin/env python3
"""
qr_gallery.py — SonicBuilder
Generate a printable gallery sheet of QR codes for common project links.
By default uses SB_REPO_URL as the base.
Usage:
  python scripts/qr_gallery.py --out Parts_Index/QR_Gallery.pdf \
      --links manuals=/releases latest=/releases/latest parts=/tree/main/Parts_Index
Env:
  SB_REPO_URL  (falls back to Replit URL if unset)
"""
import os, argparse, textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

DEFAULT_BASE = os.environ.get("SB_REPO_URL","https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="SonicBuilder — QR Gallery")
    ap.add_argument("--links", nargs="*", default=[
        "manuals=/releases",
        "latest=/releases/latest",
        "parts=/tree/main/Parts_Index",
        "wiring=/tree/main/Wiring_Diagrams",
        "firmware=/tree/main/Firmware_Notes"
    ], help="name=path pairs appended to base URL")
    ap.add_argument("--base", default=DEFAULT_BASE)
    args = ap.parse_args()

    W,H = letter
    c = canvas.Canvas(args.out, pagesize=letter)

    # header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.75*inch, H-1.0*inch, args.title)
    c.setFont("Helvetica", 9)
    c.drawString(0.75*inch, H-1.2*inch, f"Base: {args.base}")

    # grid 3x3
    try:
        import qrcode
        from PIL import Image
        use_qr = True
    except Exception:
        use_qr = False

    cols, rows = 3, 3
    cell_w = (W - 1.5*inch) / cols
    cell_h = (H - 2.0*inch) / rows
    x0 = 0.75*inch; y0 = H-1.6*inch

    idx = 0
    for r in range(rows):
        for col in range(cols):
            if idx >= len(args.links): break
            name, path = args.links[idx].split("=",1)
            url = args.base.rstrip("/") + "/" + path.lstrip("/")

            x = x0 + col*cell_w
            y = y0 - r*cell_h

            # label
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x+6, y-16, name.upper())

            if use_qr:
                qr = qrcode.QRCode(box_size=4, border=1)
                qr.add_data(url); qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                c.drawImage(ImageReader(img.get_image()), x+6, y-16-1.45*inch, width=1.4*inch, height=1.4*inch, mask='auto')
            else:
                # fallback box + URL
                c.setStrokeColor(colors.black)
                c.rect(x+6, y-16-1.45*inch, 1.4*inch, 1.4*inch, stroke=1, fill=0)
                c.setFont("Helvetica", 7)
                c.drawString(x+10, y-16-1.45*inch+1.4*inch-12, url[:42] + ("..." if len(url)>42 else ""))

            # URL text
            c.setFont("Helvetica", 8)
            wrapped = textwrap.wrap(url, 60)
            for i, line in enumerate(wrapped[:2]):
                c.drawString(x+6, y-16-1.45*inch-10 - i*10, line)

            idx += 1

    # footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2.0, 0.6*inch, f"SonicBuilder • QR Gallery • Base {args.base}")
    c.showPage(); c.save()

if __name__ == "__main__":
    main()
