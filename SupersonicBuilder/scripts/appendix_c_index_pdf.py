#!/usr/bin/env python3
import csv, argparse, textwrap, sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
sys.path.insert(0, 'scripts')
from repo_url import resolve

def make_dark_page(c):
    W,H = letter
    c.setFillColorRGB(0.1,0.1,0.12); c.rect(0,0,W,H,stroke=0,fill=1)
    return W,H

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="Appendix/C_I2S_Integration/03_Photo_Index.csv")
    ap.add_argument("--out", default="Appendix/C_I2S_Integration/Appendix_C_I2S_Index.pdf")
    ap.add_argument("--title", default="Appendix C — I²S Integration: Photo & Diagram Index")
    ap.add_argument("--version", default="v2.0.9")
    ap.add_argument("--url", default=None)
    args = ap.parse_args()

    link = resolve(args.url)
    c = canvas.Canvas(args.out, pagesize=letter)
    W,H = make_dark_page(c)
    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 18); c.drawString(1*inch, H-1.2*inch, args.title)
    c.setFont("Helvetica", 10); c.drawString(1*inch, H-1.5*inch, f"Version {args.version} • {link}")
    y = H-1.9*inch
    try:
        with open(args.csv, "r", newline="") as f:
            r = csv.DictReader(f)
            for i,row in enumerate(r, start=1):
                line = f"{i:02d}. [{row['type'].upper()}] {row['name']}  —  {row['file']}"
                for seg in textwrap.wrap(line, 110):
                    c.drawString(0.9*inch, y, seg); y -= 14
                    if y < 1.2*inch:
                        c.setFont("Helvetica", 8); c.setFillColorRGB(0.75,0.75,0.8)
                        c.drawCentredString(W/2.0, 0.6*inch, f"SonicBuilder {args.version} • {link}")
                        c.showPage(); W,H = make_dark_page(c)
                        c.setFillColor(colors.whitesmoke); c.setFont("Helvetica", 10)
                        y = H-1.0*inch
    except FileNotFoundError:
        c.setFont("Helvetica", 12); c.drawString(1*inch, y, "No index CSV found. Run i2s_index first.")
    c.setFont("Helvetica", 8); c.setFillColorRGB(0.75,0.75,0.8)
    c.drawCentredString(W/2.0, 0.6*inch, f"SonicBuilder {args.version} • {link}")
    c.showPage(); c.save()
    print(f"Wrote {args.out}")
if __name__ == "__main__":
    main()
