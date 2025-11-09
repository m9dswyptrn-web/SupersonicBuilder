
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def draw_footer_watermark(c, text="LTZ RR2 GRZ", pos="right", opacity=0.55):
    W,H = letter
    try:
        c.setFillAlpha(opacity)
    except Exception:
        pass
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.8,0.8,0.82)
    y = 0.40*inch
    if pos == "center":
        c.drawCentredString(W/2, y, text)
    elif pos == "left":
        c.drawString(0.8*inch, y, text)
    else:
        c.drawRightString(W-0.8*inch, y, text)
    try:
        c.setFillAlpha(1.0)
    except Exception:
        pass

def draw_diagonal_watermark(c, text="LTZ RR2 GRZ", opacity=0.07, size=58):
    W,H = letter
    try:
        c.setFillAlpha(opacity)
    except Exception:
        pass
    c.setFont("Helvetica-Bold", size)
    c.setFillColorRGB(0.7,0.7,0.75)
    c.saveState()
    c.translate(W/2, H/2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    try:
        c.setFillAlpha(1.0)
    except Exception:
        pass
