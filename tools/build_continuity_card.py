#!/usr/bin/env python3
import os, argparse, yaml
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from datetime import datetime

CFG = Path("assets/config/continuity_map.yaml")
OUT = Path("output/USB_AUX_Continuity_Field_Card.pdf")

def page_setup(cfg):
    size = cfg.get("page", {}).get("size", "letter").lower()
    orient = cfg.get("page", {}).get("orientation", "landscape").lower()
    ps = A4 if size == "a4" else letter
    if orient == "landscape":
        ps = landscape(ps)
    margins = int(cfg.get("page", {}).get("margins_pt", 36))
    return ps, margins

def draw_svg(c, path, x, y, max_w, max_h):
    drawing = svg2rlg(str(path))
    # scale to fit
    sx = max_w / (drawing.minWidth() or 1)
    sy = max_h / (drawing.height or 1)
    s = min(sx, sy)
    drawing.width *= s
    drawing.height *= s
    drawing.scale(s, s)
    renderPDF.draw(drawing, c, x, y)

def header(c, theme, W, H, rev_text):
    title = "USB / AUX Continuity Field Card"
    sub = "Chevy Sonic LTZ — Android HU Retrofit (USB/AUX)"
    ver = rev_text or datetime.now().strftime("Built %Y-%m-%d %H:%M")
    c.setFillColor(colors.HexColor("#FFFFFF") if theme=="dark" else colors.black)
    c.setFont("Helvetica-Bold", 18); c.drawString(36, H-36, title)
    c.setFont("Helvetica", 12); c.drawString(36, H-54, sub)
    c.setFont("Helvetica-Oblique", 9); c.drawRightString(W-36, H-36, ver)

def aux_block(c, cfg, x, y, w, h, theme):
    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#5A5A5A") if theme=="dark" else colors.HexColor("#333333"))
    c.setFillColor(colors.HexColor("#121212") if theme=="dark" else colors.HexColor("#F7F7F7"))
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#FFFFFF") if theme=="dark" else colors.black)
    c.setFont("Helvetica-Bold", 12); c.drawString(x+12, y+h-22, "AUX (3.5mm TRS) — Probe Map & Expectations")
    # Diagram
    draw_svg(c, Path("assets/diagrams/trs_overview.svg"), x+12, y+10, w*0.55, h-36)
    # Labels / expectations
    lx = x + w*0.55 + 24
    ly = y + h - 40
    lab = cfg.get("labels", {}).get("aux", {})
    exp = cfg.get("expected", {}).get("aux", {})
    c.setFont("Helvetica", 11)
    c.drawString(lx, ly, f"• {lab.get('tip','TIP')}: {exp.get('tip_to_hu','')}"); ly -= 18
    c.drawString(lx, ly, f"• {lab.get('ring','RING')}: {exp.get('ring_to_hu','')}"); ly -= 18
    c.drawString(lx, ly, f"• {lab.get('sleeve','SLEEVE')}: {exp.get('sleeve_to_chassis','')}"); ly -= 28
    c.setFont("Helvetica-Oblique", 9); c.drawString(lx, ly, "Tip=Left(+), Ring=Right(+), Sleeve=Ground"); ly -= 12

def usb_block(c, cfg, x, y, w, h, theme):
    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#5A5A5A") if theme=="dark" else colors.HexColor("#333333"))
    c.setFillColor(colors.HexColor("#121212") if theme=="dark" else colors.HexColor("#F7F7F7"))
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#FFFFFF") if theme=="dark" else colors.black)
    c.setFont("Helvetica-Bold", 12); c.drawString(x+12, y+h-22, "USB 2.0 — Pinout & Continuity Expectations")
    # Diagram
    draw_svg(c, Path("assets/diagrams/usb_overview.svg"), x+12, y+10, w*0.55, h-36)
    # Labels / expectations
    lx = x + w*0.55 + 24
    ly = y + h - 40
    lab = cfg.get("labels", {}).get("usb", {})
    exp = cfg.get("expected", {}).get("usb", {})
    c.setFont("Helvetica", 11)
    c.drawString(lx, ly, f"• {lab.get('dplus','D+')}:  {exp.get('dplus_pair','')}"); ly -= 18
    c.drawString(lx, ly, f"• {lab.get('dminus','D-')}: {exp.get('dminus_pair','')}"); ly -= 18
    c.drawString(lx, ly, f"• {lab.get('vbus','VBUS')}: {exp.get('vbus','')}"); ly -= 18
    c.drawString(lx, ly, f"• {lab.get('gnd','GND')}:  {exp.get('gnd','')}"); ly -= 18
    c.drawString(lx, ly, f"• {lab.get('shield','Shield')}: {exp.get('shield','')}"); ly -= 28
    c.setFont("Helvetica-Oblique", 9); c.drawString(lx, ly, "Twist D+/D-, isolate from shield; verify shells/strain reliefs."); ly -= 12

def checklist_block(c, cfg, x, y, w, h, theme):
    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#5A5A5A") if theme=="dark" else colors.HexColor("#333333"))
    c.setFillColor(colors.HexColor("#121212") if theme=="dark" else colors.HexColor("#F7F7F7"))
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#FFFFFF") if theme=="dark" else colors.black)
    c.setFont("Helvetica-Bold", 12); c.drawString(x+12, y+h-22, "Quick Triage")
    items = [
        "AUX silent? Probe TIP/RING/SLEEVE continuity to HU inputs; verify sleeve only grounded at HU.",
        "CarPlay/AA drops? Verify D+/D- continuity and not shorted to shield; re-seat USB couplers.",
        "Crackle/noise? Move mic cable away from USB; one-end drain grounding.",
        "No rear cam on shift? Check reverse trigger, then confirm USB accessory power not sagging.",
    ]
    c.setFont("Helvetica", 10)
    yy = y + h - 42
    for it in items:
        c.drawString(x+16, yy, f"□ {it}")
        yy -= 16

def notes_block(c, cfg, x, y, w, h, theme):
    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#5A5A5A") if theme=="dark" else colors.HexColor("#333333"))
    c.setFillColor(colors.HexColor("#121212") if theme=="dark" else colors.HexColor("#F7F7F7"))
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#FFFFFF") if theme=="dark" else colors.black)
    c.setFont("Helvetica-Bold", 12); c.drawString(x+12, y+h-22, "Notes")
    c.setFont("Helvetica", 10)
    yy = y + h - 42
    for line in cfg.get("notes", []):
        c.drawString(x+16, yy, f"• {line}")
        yy -= 14

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="", help="version/build stamp to show in header")
    args = ap.parse_args()

    # Prefer Makefile exports if present
    version = os.environ.get("SONIC_VERSION", "").strip()
    build_dt = os.environ.get("SONIC_BUILD_DT", "").strip()
    rev_text = args.rev or (f"{version} • {build_dt}" if version or build_dt else "")

    cfg = yaml.safe_load(CFG.read_text(encoding='utf-8'))
    theme = cfg.get("theme", "dark").lower()
    (W,H), M = page_setup(cfg)
    c = canvas.Canvas(str(OUT), pagesize=(W,H))

    # Background
    if theme == "dark":
        c.setFillColor(colors.HexColor("#0E0E0E")); c.rect(0,0,W,H,fill=1,stroke=0)
    else:
        c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)

    # Header with rev stamp
    header(c, theme, W, H, rev_text)

    # Layout grid
    col = (W - 2*M)
    row = (H - 2*M)

    # Upper blocks (AUX / USB)
    aux_block(c, cfg, M, H - M - row*0.52, col*0.49, row*0.52 - 8, theme)
    usb_block(c, cfg, M + col*0.51, H - M - row*0.52, col*0.49, row*0.52 - 8, theme)

    # Lower blocks (Checklist / Notes)
    checklist_block(c, cfg, M, M, col*0.62, row*0.44, theme)
    notes_block(c, cfg, M + col*0.64, M, col*0.35, row*0.44, theme)

    c.showPage(); c.save()
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
