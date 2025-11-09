# Minimal canvas helpers (fallback). If you already have this, keep your version.
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

class AssetResolver:
    def __init__(self, root='assets'):
        self.root = root
    def path(self, rel):
        from pathlib import Path
        return str(Path(self.root) / rel)

def draw_image_fit(c, RES, rel, x, y, width, height):
    p = RES.path(rel)
    img = ImageReader(p)
    c.drawImage(img, x, y, width=width, height=height, preserveAspectRatio=True, anchor='sw')

def draw_svg_fit(c, RES, rel, x, y, max_w, max_h):
    p = RES.path(rel)
    drawing = svg2rlg(p)
    # Scale to fit
    sx = max_w / (drawing.minWidth() or 1)
    sy = max_h / (drawing.height or 1)
    s = min(sx, sy)
    drawing.width *= s
    drawing.height *= s
    drawing.scale(s, s)
    renderPDF.draw(drawing, c, x, y)
