#!/usr/bin/env python3
import csv, argparse, os, math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.lib.colors import black, white, HexColor

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV with columns: name,qty,sku,url,notes")
    ap.add_argument("-o","--output", required=True)
    ap.add_argument("--theme", default="dark", choices=["dark","light"])
    args = ap.parse_args()

    bg = HexColor("#0e0f12") if args.theme=="dark" else HexColor("#ffffff")
    fg = white if args.theme=="dark" else black
    grid = HexColor("#2c2f36") if args.theme=="dark" else HexColor("#d0d4da")

    rows = []
    with open(args.csv, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows.append(r)

    c = canvas.Canvas(args.output, pagesize=letter)
    c.setTitle("Parts & Tools")
    c.setAuthor("Sonic Builder")
    c.setSubject("Parts and tools list with QR codes for installation manual")

    def header(page):
        c.setFillColor(bg); c.rect(0,0,*letter, stroke=0, fill=1)
        c.setFillColor(fg); c.setFont("Helvetica-Bold", 18)
        c.drawString(0.75*inch, letter[1]-0.85*inch, "Parts & Tools (with QR)")

    per_page = 6  # 6 rows per page (2 columns layout)
    w = letter[0]-1.0*inch
    x0 = 0.5*inch
    y = letter[1]-1.2*inch
    cell_h = 1.2*inch

    for idx, r in enumerate(rows):
        if idx % per_page == 0:
            if idx>0: c.showPage()
            header(idx//per_page + 1)
            y = letter[1]-1.2*inch

        # border
        c.setStrokeColor(grid); c.rect(x0, y-cell_h+0.1*inch, w, cell_h, stroke=1, fill=0)
        # QR
        url = (r.get("url") or "").strip()
        qrsize = 0.95*inch
        if url:
            code = qr.QrCodeWidget(url)
            b = code.getBounds()
            sx = qrsize/(b[2]-b[0]); sy = qrsize/(b[3]-b[1])
            from reportlab.graphics.shapes import Drawing
            d = Drawing(int(qrsize), int(qrsize)); d.add(code)
            from reportlab.graphics import renderPDF
            renderPDF.draw(d, c, x0+0.15*inch, y-qrsize-0.05*inch)
        else:
            c.setFillColor(fg)
            c.rect(x0+0.15*inch, y-qrsize-0.05*inch, qrsize, qrsize, stroke=1, fill=0)

        # Text
        c.setFillColor(fg)
        c.setFont("Helvetica-Bold", 12)
        name = r.get("name","").strip()
        c.drawString(x0+1.3*inch, y-0.35*inch, name[:80])
        c.setFont("Helvetica", 10)
        meta = f"Qty: {r.get('qty','1')}   SKU: {r.get('sku','-')}"
        c.drawString(x0+1.3*inch, y-0.6*inch, meta[:100])
        notes = r.get("notes","").strip()
        if notes:
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(x0+1.3*inch, y-0.85*inch, notes[:95])

        y -= cell_h

    c.showPage(); c.save()

if __name__ == "__main__":
    main()
