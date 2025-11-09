# stamp_utils.py
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors

def get_version() -> str:
    vf = Path("VERSION")
    try:
        val = vf.read_text(encoding="utf-8").strip()
        return val if val else "v0.0.0"
    except Exception:
        return "v0.0.0"

def build_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M")

def on_page_footer(canvas, doc, project_name: str, version: str, ts_utc: str, enabled: bool=True):
    if not enabled:
        return
    canvas.saveState()
    footer_text = f"{project_name} • {version} • Generated {ts_utc} UTC • Page {canvas.getPageNumber()}"
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    y = 18
    canvas.drawString(doc.leftMargin, y, footer_text)
    canvas.restoreState()

def draw_title_stamp(canvas, doc, version: str, ts_utc: str, enabled: bool=True):
    if not enabled:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 28, f"{version} • {ts_utc} UTC")
    canvas.restoreState()

def set_pdf_metadata(canvas, title: str, author: str = "Sonic Builder"):
    try:
        canvas.setTitle(title)
        canvas.setAuthor(author)
        canvas.setSubject("Automotive Installation Manual")
        canvas.setCreator("Sonic Builder – PDF Generator")
        try:
            canvas._doc.info.keywords = "Chevy Sonic, RR2, GRZ, Installation, Wiring, Manual"
        except Exception:
            pass
    except Exception:
        pass
