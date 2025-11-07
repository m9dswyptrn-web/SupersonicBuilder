
# Advanced annotations with per-item styling.
# Supported keys (optional on each annotation):
#   - line_width: float (default 1.2)
#   - arrow_color / box_stroke / text_color: hex "#RRGGBB" or [r,g,b] 0..1
#   - box_fill: hex with alpha "#RRGGBBAA" or [r,g,b,a] 0..1
#   - font_size: int (default 9)
#   - label_dx / label_dy: floats (offset from arrow tip)
#   - w / h for box size (defaults 120x20)
#
# Types: "label", "box", "arrow"

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def _parse_color(c, default=(1,1,1), allow_alpha=False):
    if c is None:
        return default if not allow_alpha else (*default, 1.0) if len(default)==3 else default
    if isinstance(c, (list,tuple)):
        vals = list(c)
        if not allow_alpha and len(vals)==4:
            vals = vals[:3]
        return tuple(vals)
    if isinstance(c, str):
        s = c.strip()
        if s.startswith('#'):
            s = s[1:]
            if len(s)==6:
                r = int(s[0:2],16)/255.0; g=int(s[2:4],16)/255.0; b=int(s[4:6],16)/255.0
                return (r,g,b) if not allow_alpha else (r,g,b,1.0)
            if len(s)==8 and allow_alpha:
                r=int(s[0:2],16)/255.0; g=int(s[2:4],16)/255.0; b=int(s[4:6],16)/255.0; a=int(s[6:8],16)/255.0
                return (r,g,b,a)
    return default if not allow_alpha else (*default, 1.0) if len(default)==3 else default

def _to_page(xn, yn, margin, W, H):
    return margin + xn * (W - 2*margin), margin + yn * (H - 2*margin)

def _arrowhead(c, x, y, angle_deg=0, size=7, color=(1,1,1)):
    from math import cos, sin, radians
    a = radians(angle_deg)
    p1 = (x, y)
    p2 = (x - size*cos(a) + size*0.6*sin(a), y - size*sin(a) - size*0.6*cos(a))
    p3 = (x - size*cos(a) - size*0.6*sin(a), y - size*sin(a) + size*0.6*cos(a))
    c.setFillColorRGB(*color[:3]); c.setStrokeColorRGB(*color[:3])
    c.line(p2[0], p2[1], p1[0], p1[1])
    c.line(p3[0], p3[1], p1[0], p1[1])

def draw_annotations_styled(c, data, margin, W, H, default_accent=(0.95,0.65,0.20)):
    white  = (1,1,1)
    for a in data.get("annotations", []):
        t = a.get("type","label")
        lw = float(a.get("line_width", 1.2))
        fs = int(a.get("font_size", 9))
        c.setLineWidth(lw)

        if t == "label":
            x,y = _to_page(a["x"], a["y"], margin, W, H)
            text_color = _parse_color(a.get("text_color"), white)
            c.setFillColorRGB(*text_color[:3]); c.circle(x, y, 3, fill=1, stroke=0)
            c.setFillColorRGB(*text_color[:3]); c.setFont("Helvetica", fs)
            c.drawString(x+5, y+2, a.get("label",""))

        elif t == "box":
            x,y = _to_page(a["x"], a["y"], margin, W, H)
            w,h = a.get("w", 120), a.get("h", 22)
            fill = _parse_color(a.get("box_fill"), (0,0,0), allow_alpha=True)
            stroke = _parse_color(a.get("box_stroke"), default_accent)
            text_color = _parse_color(a.get("text_color"), white)
            # emulate alpha by setFillAlpha if available
            try:
                c.setFillAlpha(fill[3])
            except Exception:
                pass
            c.setFillColorRGB(*fill[:3]); c.setStrokeColorRGB(*stroke[:3])
            c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
            try:
                c.setFillAlpha(1.0)
            except Exception:
                pass
            c.setFillColorRGB(*text_color[:3]); c.setFont("Helvetica", fs)
            c.drawString(x+6, y+(h-fs)/2, a.get("label",""))

        elif t == "arrow":
            fx,fy = _to_page(a["from_x"], a["from_y"], margin, W, H)
            tx,ty = _to_page(a["to_x"], a["to_y"], margin, W, H)
            color = _parse_color(a.get("arrow_color"), default_accent)
            text_color = _parse_color(a.get("text_color"), white)
            size = float(a.get("arrow_size", 8))
            c.setStrokeColorRGB(*color[:3]); c.setFillColorRGB(*color[:3])
            c.line(fx, fy, tx, ty)
            # head
            import math
            ang = math.degrees(math.atan2(ty-fy, tx-fx))
            _arrowhead(c, tx, ty, angle_deg=ang, size=size, color=color)
            # tail dot
            c.circle(fx, fy, max(1.8, lw), fill=1, stroke=0)
            # label
            lbl = a.get("label","")
            if lbl:
                dx = float(a.get("label_dx", 6)); dy = float(a.get("label_dy", 6))
                c.setFillColorRGB(*text_color[:3]); c.setFont("Helvetica", fs)
                c.drawString(tx+dx, ty+dy, lbl)
