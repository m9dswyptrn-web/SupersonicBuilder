import os, yaml
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter

# ---------- ICON SUPPORT ----------
def _load_icon(logical_name: str, size_pt: float):
    """
    Load assets/icons/<logical_name>.png (preferred) or .jpg/.jpeg.
    Returns (ImageReader, width_pt, height_pt) scaled to size_pt square.
    """
    base = f"assets/icons/{logical_name}"
    for ext in (".png", ".jpg", ".jpeg"):
        p = base + ext
        if os.path.isfile(p):
            ir = ImageReader(p)
            return (ir, size_pt, size_pt)
    # Minimal placeholder if not found
    return (None, size_pt, size_pt)

def draw_icon(c: rl_canvas.Canvas, logical_name: str, x: float, y: float, size: float=14):
    ir, w, h = _load_icon(logical_name, size)
    if ir:
        c.drawImage(ir, x, y, width=w, height=h, mask='auto')
    else:
        c.setStrokeColor(colors.grey)
        c.rect(x, y, size, size, stroke=1, fill=0)

# ---------- TOC & BOOKMARKS ----------
class PdfToc:
    def __init__(self, canvas: rl_canvas.Canvas, sections):
        """
        sections: list of dicts with at least:
          - title: str
          - page: int (1-based)
          - anchor: str (unique slug)
        """
        self.c = canvas
        self.sections = sections or []

    def write_bookmarks(self):
        """
        Writes PDF outline/bookmarks. Call at end of build pass,
        after all pages created.
        """
        for s in self.sections:
            title = s.get("title", "Section")
            key = s.get("anchor", title.lower().replace(" ", "-"))
            # Named destination on that page top (bookmarkPage uses current page)
            self.c.bookmarkPage(key, fit="FitH", top=750)
            # Outline entry
            self.c.addOutlineEntry(title, key, level=0, closed=False)

    def draw_toc_page(self, title="Table of Contents"):
        """
        Adds a new page with a click-to-jump TOC.
        Call this right after the cover page.
        """
        self.c.showPage()
        width, height = letter
        margin = 48
        y = height - margin
        self.c.setFont("Helvetica-Bold", 22)
        self.c.drawString(margin, y, title)
        y -= 30
        self.c.setFont("Helvetica", 12)
        for s in self.sections:
            t = s.get("title", "Section")
            page = s.get("page", 1)
            key = s.get("anchor", t.lower().replace(" ", "-"))
            line = f"{t}  .......  {page}"
            self.c.drawString(margin, y, line)
            w = self.c.stringWidth(line, "Helvetica", 12)
            self.c.linkAbsolute("",
                                key,
                                Rect=(margin, y-2, margin+w, y+12),
                                thickness=0,
                                dashArray=None,
                                color=colors.transparent)
            y -= 18
            if y < margin + 40:
                self.c.showPage()
                y = height - margin

# ---------- JOB CARDS ----------
def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_job_cards(c: rl_canvas.Canvas, job_cards_cfg, icon_map="config/signal_icons.yaml"):
    """
    Render one or more single-page job cards after main content.
    job_cards_cfg: dict loaded from config/job_cards.yaml
    icon_map: yaml mapping logical types to icon names (without ext)
    """
    icon_cfg = _load_yaml(icon_map) if os.path.isfile(icon_map) else {"types": {}}
    types = icon_cfg.get("types", {})

    cards = job_cards_cfg.get("cards", [])
    for card in cards:
        c.showPage()
        width, height = letter
        margin = 36
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(margin, height - margin - 8, card.get("title", "Job Card"))
        # Badges
        y = height - margin - 32
        c.setFont("Helvetica", 10)
        if card.get("vehicle"):
            c.drawString(margin, y, f"Vehicle: {card['vehicle']}")
            y -= 14
        if card.get("est_time"):
            c.drawString(margin, y, f"Est. Time: {card['est_time']}")
            y -= 14
        if card.get("tools"):
            tools = ", ".join(card["tools"][:6]) + (" ..." if len(card["tools"])>6 else "")
            c.drawString(margin, y, "Tools: " + tools)
            y -= 16

        # Steps
        y -= 6
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Steps")
        y -= 14
        c.setFont("Helvetica", 11)
        for i, step in enumerate(card.get("steps", []), 1):
            txt = f"{i}. {step.get('text','')}"
            c.drawString(margin, y, txt[:110])
            # optional icon
            t = step.get("type")
            if t and t in types:
                draw_icon(c, types[t], width - margin - 14, y-2, size=12)
            y -= 16
            if y < 120:
                c.showPage()
                y = height - margin - 40
                c.setFont("Helvetica", 11)

        # Notes
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Notes")
        y -= 14
        c.setFont("Helvetica", 10)
        for note in card.get("notes", []):
            c.drawString(margin, y, u"\u2022 " + note[:120])
            y -= 14
            if y < 72:
                c.showPage()
                y = height - margin - 40
                c.setFont("Helvetica", 10)

        # Optional QR
        qr = card.get("qr")
        if qr:
            try:
                import qrcode
                from io import BytesIO
                qr_img = qrcode.make(qr)
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                c.drawImage(ImageReader(BytesIO(buf.getvalue())),
                            width - margin - 72, margin, width=72, height=72, mask=None)
            except Exception:
                pass
