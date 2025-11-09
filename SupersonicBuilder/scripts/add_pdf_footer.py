#!/usr/bin/env python3
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from io import BytesIO
import argparse, os
def gen_overlay(w,h,lines,qr_png=None,qr_size_mm=12):
    buf = BytesIO(); c = canvas.Canvas(buf, pagesize=(w,h))
    margin = 10*mm; y = margin+8
    c.setFont("Helvetica", 8)
    for i, line in enumerate(lines[::-1]):
        c.drawCentredString(w/2, y + i*10, line)
    if qr_png and os.path.exists(qr_png):
        try:
            size = qr_size_mm*mm
            c.drawImage(qr_png, w - margin - size, margin, width=size, height=size, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print("[warn] QR draw:", e)
    c.save(); buf.seek(0); 
    return PdfReader(buf).pages[0]
def add_footer(i,o,lines,qr_png=None,qr_size_mm=12):
    r=PdfReader(i); w=PdfWriter()
    for pg in r.pages:
        ov=gen_overlay(float(pg.mediabox.width), float(pg.mediabox.height), lines, qr_png, qr_size_mm)
        pg.merge_page(ov); w.add_page(pg)
    with open(o,"wb") as f: w.write(f)
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("-o","--output",required=True)
    ap.add_argument("--line",action="append",required=True)
    ap.add_argument("--qr"); ap.add_argument("--qr-size-mm",type=int,default=12)
    a=ap.parse_args(); add_footer(a.input,a.output,a.line,a.qr,a.qr_size_mm)
    print("[ok] footer applied ->", a.output)
