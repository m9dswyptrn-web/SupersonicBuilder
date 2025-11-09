
# Drop-in replacement for the annotations portion of scripts/render_pages.py
# Adds support for types: "label", "box", "arrow".
#
# How to use:
# 1) In your existing scripts/render_pages.py, replace the old annotations
#    drawing logic with the draw_annotations() and page_photos_annotated()
#    functions from this file, or just import these helpers.
#
# 2) Point annotations_json to a file that contains entries of the form:
#    {"type":"arrow", "from_x":0.1, "from_y":0.2, "to_x":0.2, "to_y":0.9, "label":"GMLAN Low"}
#
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from pathlib import Path
import io, json

def _to_page(xn, yn, margin, W, H):
    "Normalize (0..1) to page coords inside inner panel."
    return margin + xn * (W - 2*margin), margin + yn * (H - 2*margin)

def _arrowhead(c, x, y, angle_deg=0, size=7, color=(1,1,1)):
    from math import cos, sin, radians
    a = radians(angle_deg)
    p1 = (x, y)
    p2 = (x - size*cos(a) + size*0.6*sin(a), y - size*sin(a) - size*0.6*cos(a))
    p3 = (x - size*cos(a) - size*0.6*sin(a), y - size*sin(a) + size*0.6*cos(a))
    c.setFillColorRGB(*color); c.setStrokeColorRGB(*color)
    c.line(p2[0], p2[1], p1[0], p1[1])
    c.line(p3[0], p3[1], p1[0], p1[1])

def draw_annotations(c, data, margin, W, H):
    accent = (0.95,0.65,0.20)  # warm gold/orange
    white  = (1,1,1)
    c.setLineWidth(1.2)
    for a in data.get("annotations", []):
        t = a.get("type","label")
        if t == "label":
            x,y = _to_page(a["x"], a["y"], margin, W, H)
            c.setFillColorRGB(*white); c.circle(x, y, 3, fill=1, stroke=0)
            c.setFillColorRGB(*white); c.setFont("Helvetica", 9)
            c.drawString(x+5, y+2, a.get("label",""))
        elif t == "box":
            x,y = _to_page(a["x"], a["y"], margin, W, H)
            w,h = a.get("w", 120), a.get("h", 20)
            c.setFillColorRGB(0,0,0,); c.setFillAlpha(0.55); c.setStrokeAlpha(0.9)
            c.setStrokeColorRGB(*accent)
            c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
            c.setFillAlpha(1.0); c.setStrokeAlpha(1.0)
            c.setFillColorRGB(*white); c.setFont("Helvetica", 9)
            c.drawString(x+6, y+6, a.get("label",""))
        elif t == "arrow":
            # arrow from (from_x,from_y) -> (to_x,to_y); place label near head
            fx,fy = _to_page(a["from_x"], a["from_y"], margin, W, H)
            tx,ty = _to_page(a["to_x"], a["to_y"], margin, W, H)
            c.setStrokeColorRGB(*accent)
            c.setFillColorRGB(*accent)
            c.circle(fx, fy, 2.2, fill=1, stroke=0)
            c.line(fx, fy, tx, ty)
            # arrowhead
            import math
            ang = math.degrees(math.atan2(ty-fy, tx-fx))
            _arrowhead(c, tx, ty, angle_deg=ang, size=a.get("arrow_size", 8), color=accent)
            # label near head (offset a bit)
            lbl = a.get("label","")
            if lbl:
                offx = a.get("label_dx", 6); offy = a.get("label_dy", 6)
                c.setFillColorRGB(*white); c.setFont("Helvetica", 9)
                c.drawString(tx+offx, ty+offy, lbl)

def page_photos_annotated(c, assets_root, annotations_json, page_num, total_pages):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    from pathlib import Path
    import io, json

    # Use your existing draw_dark_frame; we assume it's already defined in the caller file.
    draw_dark_frame(c, "Annotated Harness Photos", page_num, total_pages)
    W,H = letter
    margin = 0.8*inch
    box_w = W - 2*margin
    box_h = (H - 2*margin) * 0.40
    p1 = Path(assets_root) / "pinout_harness_closeup.jpg"
    p2 = Path(assets_root) / "rr2_gm2_primary_photo.jpg"

    # draw_image_box expected in the caller file.
    draw_image_box(c, str(p1), margin, H - margin - box_h, box_w, box_h)
    draw_image_box(c, str(p2), margin, margin, box_w, box_h)

    # annotations
    if annotations_json and Path(annotations_json).exists():
        with open(annotations_json, "r", encoding="utf-8") as f:
            ann = json.load(f)
        draw_annotations(c, ann, margin, W, H)
