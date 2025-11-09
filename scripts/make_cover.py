#!/usr/bin/env python3
import argparse, datetime, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white, HexColor

def draw_centered(c, text, y, size=24, color=white):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", size)
    w = c.stringWidth(text, "Helvetica-Bold", size)
    c.drawString((letter[0]-w)/2.0, y, text)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-o","--output", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--subtitle", default="")
    p.add_argument("--brand", default="Sonic Builder")
    p.add_argument("--version", default="v0.0.0")
    p.add_argument("--theme", default="dark", choices=["dark","light"])
    p.add_argument("--hero", required=True, help="Path to hero image (jpg/png)")
    args = p.parse_args()

    bg = HexColor("#0e0f12") if args.theme=="dark" else HexColor("#ffffff")
    fg = white if args.theme=="dark" else black

    c = canvas.Canvas(args.output, pagesize=letter)
    c.setTitle(f"{args.title} – {args.subtitle}" if args.subtitle else args.title)
    c.setAuthor(args.brand)
    c.setSubject(f"Installation manual cover for {args.title}")
    c.setFillColor(bg); c.rect(0,0, *letter, stroke=0, fill=1)

    # Hero image boxed
    img_w = letter[0]-1.5*inch
    img_h = 4.5*inch
    x = (letter[0]-img_w)/2.0
    y = letter[1]-img_h-1.25*inch
    try:
        c.drawImage(args.hero, x, y, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        # draw placeholder
        c.setFillColor(fg); c.rect(x, y, img_w, img_h, stroke=1, fill=0)
        c.drawString(x+12, y+img_h/2, f"[hero missing: {e}]")

    draw_centered(c, args.title, y-0.75*inch, size=28, color=fg)
    if args.subtitle:
        draw_centered(c, args.subtitle, y-1.15*inch, size=16, color=fg)

    # Brand/version footer
    c.setFont("Helvetica", 10); c.setFillColor(fg)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    footer = f"{args.brand} • {args.version} • built {date}"
    w = c.stringWidth(footer, "Helvetica", 10)
    c.drawString((letter[0]-w)/2.0, 0.6*inch, footer)

    c.showPage(); c.save()

if __name__ == "__main__":
    main()
