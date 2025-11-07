
import argparse
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Imposes two HALF-LETTER (8.5x5.5) pages per US LETTER sheet (portrait).
# Adds light crop marks and center guides.
#
# Requirements:
#   pip install pdfrw reportlab
#
# Usage:
#   python scripts/impose_two_up_pro.py --input output/field_cards_dark_single.pdf --output output/field_cards_dark_two_up_PRO.pdf

PAGE_W, PAGE_H = letter

def draw_crop_marks(can, margin=0.35*inch):
    can.setStrokeColorRGB(0.6,0.6,0.6)
    can.setLineWidth(0.5)
    # vertical center guide
    can.line(PAGE_W/2, 0.4*inch, PAGE_W/2, PAGE_H-0.4*inch)
    # outer crop marks (short lines near corners)
    L = 12  # pts
    # bottom left
    can.line(margin, margin, margin+L, margin)
    can.line(margin, margin, margin, margin+L)
    # bottom right
    can.line(PAGE_W-margin, margin, PAGE_W-margin-L, margin)
    can.line(PAGE_W-margin, margin, PAGE_W-margin, margin+L)
    # top left
    can.line(margin, PAGE_H-margin, margin+L, PAGE_H-margin)
    can.line(margin, PAGE_H-margin, margin, PAGE_H-margin-L)
    # top right
    can.line(PAGE_W-margin, PAGE_H-margin, PAGE_W-margin-L, PAGE_H-margin)
    can.line(PAGE_W-margin, PAGE_H-margin, PAGE_W-margin, PAGE_H-margin-L)

def make_overlay_pdf(tmp_overlay_path):
    from reportlab.pdfgen import canvas as _canvas
    can = _canvas.Canvas(tmp_overlay_path, pagesize=letter)
    draw_crop_marks(can)
    can.showPage()
    can.save()

def impose_two_up(input_pdf, output_pdf, scale_factor=0.94, top_gap=0.28*inch, bottom_gap=0.28*inch):
    """
    Place first half-letter page on top half, second on bottom half.
    `scale_factor` slightly shrinks to leave margin for crop marks.
    """
    src = PdfReader(input_pdf)
    writer = PdfWriter()

    # Compute placement boxes
    half_h = PAGE_H/2
    target_w = PAGE_W * scale_factor
    target_h = half_h - top_gap - bottom_gap

    # Source page size (points). Assume 8.5x5.5in but read boxes to be safe.
    # pdfrw uses mediabox [x0, y0, x1, y1]
    def page_size(p):
        mb = [float(x) for x in p.MediaBox]
        return mb[2]-mb[0], mb[3]-mb[1]

    overlay_tmp = output_pdf + ".overlay.pdf"
    make_overlay_pdf(overlay_tmp)
    overlay = PdfReader(overlay_tmp).pages[0]

    pages = src.pages
    i = 0
    while i < len(pages):
        top_page = pages[i]
        bottom_page = pages[i+1] if i+1 < len(pages) else None

        # Create a blank US Letter page starting from overlay (crop marks)
        merger = PageMerge()
        merger.add(overlay)
        base_page = merger.render()

        # Create new merger for content placement
        content_merger = PageMerge(base_page)

        # Place TOP
        pw, ph = page_size(top_page)
        sx = target_w / pw
        sy = target_h / ph
        s = min(sx, sy)
        tw = pw * s
        th = ph * s
        x = (PAGE_W - tw)/2
        y_top = PAGE_H - top_gap - th
        content_merger.add(top_page)
        content_merger[-1].scale(s)
        content_merger[-1].x = x
        content_merger[-1].y = y_top

        # Place BOTTOM
        if bottom_page is not None:
            pw, ph = page_size(bottom_page)
            sx = target_w / pw
            sy = target_h / ph
            s = min(sx, sy)
            tw = pw * s
            th = ph * s
            x = (PAGE_W - tw)/2
            y_bot = bottom_gap
            content_merger.add(bottom_page)
            content_merger[-1].scale(s)
            content_merger[-1].x = x
            content_merger[-1].y = y_bot

        writer.addpage(content_merger.render())
        i += 2

    writer.write(output_pdf)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="half-letter cards PDF")
    ap.add_argument("--output", required=True, help="two-up letter PDF")
    args = ap.parse_args()
    impose_two_up(args.input, args.output)

if __name__ == "__main__":
    main()
