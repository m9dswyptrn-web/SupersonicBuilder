#!/usr/bin/env python3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from pypdf import PdfReader
from io import BytesIO
import argparse, sys
W, H = letter; HALF = H/2; MARGIN = 0.25*inch; CROP = 0.20*inch
def draw_crop_marks(c, x0, y0, w, h):
    c.setStrokeColor(black); c.setLineWidth(0.7)
    c.line(x0, y0, x0+CROP, y0); c.line(x0, y0, x0, y0+CROP)
    c.line(x0+w, y0, x0+w-CROP, y0); c.line(x0+w, y0, x0+w, y0+CROP)
    c.line(x0, y0+h, x0+CROP, y0+h); c.line(x0, y0+h, x0, y0+h-CROP)
    c.line(x0+w, y0+h, x0+w-CROP, y0+h); c.line(x0+w, y0+h, x0+w, y0+h-CROP)
def place_frame(c, y_bottom, sw, sh):
    target_w = W - 2*MARGIN; target_h = HALF - 2*MARGIN
    scale = min(target_w/sw, target_h/sh)
    pw, ph = sw*scale, sh*scale
    x = (W - pw)/2; y = y_bottom + (HALF - ph)/2
    c.setLineWidth(0.5); c.setStrokeGray(0.55); c.rect(x, y, pw, ph, stroke=1, fill=0)
    draw_crop_marks(c, (W-target_w)/2, y_bottom + (HALF - target_h)/2, target_w, target_h)
    return x, y, pw, ph
def rasterize_page_to_png(pdf_path, page_index=0, dpi=300):
    try:
        import fitz
    except Exception:
        print("[error] rasterize requested but PyMuPDF not installed. pip install pymupdf", file=sys.stderr); sys.exit(2)
    doc = fitz.open(pdf_path); page = doc.load_page(page_index)
    mat = fitz.Matrix(dpi/72, dpi/72); pix = page.get_pixmap(matrix=mat, alpha=False)
    buf = pix.tobytes("png"); w, h = pix.width, pix.height; doc.close()
    return buf, w, h
def make_two_up(inp, outp, rasterize=False, dpi=300):
    r = PdfReader(open(inp, "rb")); src = r.pages[0]
    sw = float(src.mediabox.width); sh = float(src.mediabox.height)
    c = canvas.Canvas(outp, pagesize=letter)
    c.setDash(3,3); c.setLineWidth(0.6); c.setStrokeGray(0.35); c.line(MARGIN, H/2, W-MARGIN, H/2); c.setDash()
    png_bytes = None
    if rasterize:
        png_bytes, _, _ = rasterize_page_to_png(inp, 0, dpi=dpi)
        from reportlab.lib.utils import ImageReader
        img = ImageReader(BytesIO(png_bytes))
    # bottom
    x,y,pw,ph = place_frame(c, 0, sw, sh)
    if rasterize and png_bytes: c.drawImage(img, x, y, width=pw, height=ph, preserveAspectRatio=True, mask='auto')
    # top
    x,y,pw,ph = place_frame(c, H/2, sw, sh)
    if rasterize and png_bytes: c.drawImage(img, x, y, width=pw, height=ph, preserveAspectRatio=True, mask='auto')
    c.showPage(); c.save(); print("[ok] wrote", outp, "(rasterized)" if rasterize else "")
if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--output", required=True)
    ap.add_argument("--rasterize", action="store_true"); ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args(); make_two_up(a.input, a.output, rasterize=a.rasterize, dpi=a.dpi)
