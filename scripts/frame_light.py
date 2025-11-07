
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def draw_light_frame(c, title: str, page_num: int, total_pages: int):
    W, H = letter
    # background (subtle warm gray)
    c.setFillColorRGB(0.98,0.98,0.98); c.rect(0,0,W,H, fill=1, stroke=0)
    # inner panel
    c.setFillColorRGB(1.0,1.0,1.0); c.roundRect(0.5*inch, 0.75*inch, W-1.0*inch, H-1.25*inch, 12, fill=1, stroke=0)
    # header divider
    c.setStrokeColorRGB(0.75,0.75,0.78); c.setLineWidth(1)
    c.line(0.7*inch, H-1.1*inch, W-0.7*inch, H-1.1*inch)
    # title
    c.setFillColorRGB(0.18,0.18,0.20); c.setFont("Helvetica-Bold", 16)
    c.drawString(0.8*inch, H-0.9*inch, title)
    # footer
    c.setFillColorRGB(0.30,0.30,0.33); c.setFont("Helvetica", 8)
    from datetime import datetime
    stamp = datetime.now().strftime("Build: %Y-%m-%d %H:%M:%S")
    c.drawRightString(W-0.8*inch, 0.55*inch, stamp)
    c.drawString(0.8*inch, 0.55*inch, f"Page {page_num} of {total_pages}")
