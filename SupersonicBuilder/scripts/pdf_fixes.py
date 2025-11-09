
# pdf_fixes.py — robust helpers for the Sonic PDF generator
from pathlib import Path
from typing import Optional, Tuple
import io, os

from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import utils

# Optional imports for SVG
def _have_svglib():
    try:
        import svglib.svglib  # noqa: F401
        from reportlab.graphics import renderPDF  # noqa: F401
        return True
    except Exception:
        return False

def _have_cairosvg():
    try:
        import cairosvg  # noqa: F401
        return True
    except Exception:
        return False

class AssetResolver:
    def __init__(self, root: str = "assets"):
        self.root = Path(root)

    def find(self, rel: str) -> Optional[Path]:
        p = Path(rel)
        if p.exists():
            return p
        cand = self.root / rel
        if cand.exists():
            return cand
        # Try case-insensitive lookup in assets
        lower = rel.lower()
        for path in self.root.rglob("*"):
            if path.is_file() and path.name.lower() == Path(lower).name:
                return path
        return None

def ensure_fonts(font_dir: str = "assets/fonts"):
    """Register DejaVuSans if present (full Unicode coverage)."""
    fd = Path(font_dir)
    if not fd.exists():
        return
    for name, file in (
        ("DejaVuSans", "DejaVuSans.ttf"),
        ("DejaVuSans-Bold", "DejaVuSans-Bold.ttf"),
        ("DejaVuSansMono", "DejaVuSansMono.ttf"),
    ):
        fp = fd / file
        if fp.exists():
            try:
                pdfmetrics.registerFont(TTFont(name, str(fp)))
            except Exception:
                pass

def aspect_fit(width: float, height: float, max_w: float, max_h: float) -> Tuple[float,float]:
    r = min(max_w/width, max_h/height)
    return (width*r, height*r)

def make_image(resolver: AssetResolver, rel: str, max_w: float, max_h: Optional[float]=None) -> Flowable:
    """
    Robust raster loader that resolves from assets/, scales to fit, and
    won't crash if missing (draws a placeholder box).
    """
    max_h = max_h if max_h is not None else max_w * 0.75
    path = resolver.find(rel)
    if not path:
        return _placeholder(rel, max_w, max_h, note="missing image")
    try:
        img = utils.ImageReader(str(path))
        iw, ih = img.getSize()
        tw, th = aspect_fit(iw, ih, max_w, max_h)
        return Image(str(path), width=tw, height=th)
    except Exception:
        return _placeholder(rel, max_w, max_h, note="failed to load")

def make_svg(resolver: AssetResolver, rel: str, max_w: float, max_h: Optional[float]=None) -> Flowable:
    """
    SVG loader with two strategies:
      1) svglib -> Flowable (best: stays vector)
      2) cairosvg -> PNG bytes -> Image (fallback)
    """
    max_h = max_h if max_h is not None else max_w * 0.75
    path = resolver.find(rel)
    if not path:
        return _placeholder(rel, max_w, max_h, note="missing svg")
    # Strategy 1: svglib
    if _have_svglib():
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF
            drawing = svg2rlg(str(path))
            # scale to fit
            iw, ih = drawing.minWidth(), drawing.height
            tw, th = aspect_fit(iw, ih, max_w, max_h)
            sx, sy = tw/iw, th/ih
            class SVGFlow(Flowable):
                def __init__(self, d, sx, sy, w, h):
                    Flowable.__init__(self)
                    self._d, self._sx, self._sy = d, sx, sy
                    self.width, self.height = w, h
                def draw(self):
                    from reportlab.graphics import renderPDF
                    self.canv.saveState()
                    self.canv.scale(self._sx, self._sy)
                    renderPDF.draw(self._d, self.canv, 0, 0)
                    self.canv.restoreState()
            return SVGFlow(drawing, sx, sy, tw, th)
        except Exception:
            pass
    # Strategy 2: cairosvg -> PNG
    if _have_cairosvg():
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(url=str(path))
            bio = io.BytesIO(png_bytes)
            img = ImageReader(bio)
            iw, ih = img.getSize()
            tw, th = aspect_fit(iw, ih, max_w, max_h)
            return Image(bio, width=tw, height=th)
        except Exception:
            pass
    # Fallback
    return _placeholder(rel, max_w, max_h, note="no svg backend")

def _placeholder(label: str, w: float, h: float, note: str="missing"):
    from reportlab.platypus import Flowable
    from reportlab.lib.colors import red, black, Color
    class Box(Flowable):
        def __init__(self, text, w, h, note):
            Flowable.__init__(self)
            self.width, self.height = w, h
            self.text, self.note = text, note
        def draw(self):
            c = self.canv
            c.saveState()
            c.setStrokeColor(red)
            c.rect(0, 0, self.width, self.height)
            c.setFont("Helvetica", 8)
            c.drawString(3, self.height-12, f"[{self.note}] {self.text}")
            c.restoreState()
    return Box(label, w, h, note)
