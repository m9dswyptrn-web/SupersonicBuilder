#!/usr/bin/env python3
import os, yaml, qrcode, io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def draw_row(c, y, name, sku, url, notes, theme="dark"):
    fg = colors.white if theme=="dark" else colors.black
    c.setFont("Helvetica-Bold", 11); c.setFillColor(fg); c.drawString(1*inch, y, name)
    c.setFont("Helvetica", 10); c.drawString(1*inch, y-12, f"SKU: {sku}")
    if notes:
        c.setFont("Helvetica-Oblique", 9); c.drawString(1*inch, y-24, notes[:90])
    try:
        img = qrcode.make(url); buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        c.drawImage(buf, 6.3*inch, y-28, width=0.9*inch, height=0.9*inch, mask='auto')
    except Exception:
        pass
    c.setLineWidth(0.5); c.setStrokeColor(fg); c.line(1*inch, y-34, 7.6*inch, y-34)

def build_parts_pdf(out_pdf, yaml_path, theme="dark"):
    cfg = yaml.safe_load(open(yaml_path, "r", encoding="utf-8")).copy()
    c = canvas.Canvas(out_pdf, pagesize=letter)
    fg = colors.white if theme=="dark" else colors.black
    c.setFillColor(colors.black if theme=="dark" else colors.white); w,h = letter; c.rect(0,0,w,h,0,1)
    c.setFillColor(fg); c.setFont("Helvetica-Bold", 18); c.drawString(1*inch, h-1.2*inch, "Parts & Tools — QR Sourcing")
    y = h-1.6*inch
    for sec in cfg.get("sections", []):
        c.setFillColor(fg); c.setFont("Helvetica-Bold", 14); c.drawString(1*inch, y, sec.get("title", "Section"))
        y -= 18
        for it in sec.get("items", []):
            draw_row(c, y, it.get("name", "Item"), it.get("sku", ""),
                     it.get("url", "#"), it.get("notes", ""),
                     theme=theme)
            y -= 52
            if y < 1.2*inch:
                c.showPage(); c.setFillColor(colors.black if theme=="dark" else colors.white); c.rect(0,0,w,h,0,1)
                y = h-1.0*inch
    c.save(); print("[ok] Parts & Tools ->", out_pdf)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaml", default="parts_tools.yaml")
    ap.add_argument("--out", default="output/parts_tools_dark.pdf")
    ap.add_argument("--light", action="store_true")
    a = ap.parse_args()
    theme = "light" if a.light else "dark"
    os.makedirs("output", exist_ok=True)
    build_parts_pdf(a.out, a.yaml, theme=theme)
