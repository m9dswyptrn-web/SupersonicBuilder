
import argparse, csv, json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch

# Half-letter size (8.5x5.5). We'll use landscape half-letter for card layout.
HALF_LETTER = (8.5*inch, 5.5*inch)

def draw_card_frame(c, title="Quick Reference (Dark)"):
    W,H = HALF_LETTER
    c.setFillColorRGB(0.06,0.06,0.08); c.rect(0,0,W,H, fill=1, stroke=0)
    c.setFillColorRGB(0.10,0.10,0.12); c.roundRect(0.3*inch, 0.3*inch, W-0.6*inch, H-0.6*inch, 10, fill=1, stroke=0)
    c.setStrokeColorRGB(0.35,0.35,0.40); c.line(0.45*inch, H-0.85*inch, W-0.45*inch, H-0.85*inch)
    c.setFillColorRGB(0.95,0.65,0.20); c.setFont("Helvetica-Bold", 13); c.drawString(0.5*inch, H-0.65*inch, title)

def add_lines(c, lines, x=0.5*inch, y_start=5.5*inch-1.2*inch, leading=12):
    c.setFillColorRGB(0.95,0.95,0.96); c.setFont("Helvetica", 9)
    y = y_start
    for ln in lines:
        c.drawString(x, y, ln); y -= leading

def make_cards(out_path: Path, assets_root="assets"):
    # Read speakers table if present
    rows = []
    csv_path = Path(assets_root) / "tables" / "speakers.csv"
    if csv_path.exists():
        import csv as _csv
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(_csv.reader(f))

    c = canvas.Canvas(str(out_path / "field_cards_dark_single.pdf"), pagesize=HALF_LETTER)

    # Card 1: Harness essentials
    draw_card_frame(c, "Harness Essentials")
    add_lines(c, [
        "Power (B+): Red   •  Ground: Black",
        "ACC/Illum: Orange •  GMLAN Low: Green",
        "Mic: shielded silver/black to HU",
        "Steering controls via CAN module",
    ])
    c.showPage()

    # Card 2: Speaker map (from CSV)
    draw_card_frame(c, "Speaker Map")
    if rows:
        header, *data = rows
        y = 5.5*inch - 1.2*inch
        c.setFillColorRGB(0.7,0.7,0.75); c.setFont("Helvetica-Bold", 9); c.drawString(0.5*inch, y, "Location   +     -     Level"); y -= 14
        c.setFillColorRGB(0.95,0.95,0.96); c.setFont("Helvetica", 9)
        for r in data:
            loc, pos, neg, lvl = (r + ["","","",""])[:4]
            c.drawString(0.5*inch, y, f"{loc:16} {pos:8} {neg:10} {lvl}")
            y -= 12
    else:
        add_lines(c, ["(Add assets/tables/speakers.csv for auto table)"])
    c.showPage()

    # Card 3: Triggers & grounds
    draw_card_frame(c, "Triggers & Grounds")
    add_lines(c, [
        "Reverse trigger → HU cam input",
        "Ground star point near chassis",
        "Camera +12V feed fused (1A)",
        "RCA: Front/Rear/Sub as labeled",
    ])
    c.showPage()

    c.save()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="output")
    ap.add_argument("--assets", default="assets")
    args = ap.parse_args()
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    make_cards(out, assets_root=args.assets)

if __name__ == "__main__":
    main()
