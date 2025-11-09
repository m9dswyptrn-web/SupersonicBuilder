# Generates a quick PDF of field continuity cards
import os, datetime
out_dir = os.path.join("output","field_cards")
os.makedirs(out_dir, exist_ok=True)
pdf_path = os.path.join(out_dir, "sonic_field_cards.pdf")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
except Exception as e:
    # fallback: simple text file if reportlab isn't present
    txt = os.path.join(out_dir, "sonic_field_cards.txt")
    with open(txt,"w") as f:
        f.write("Sonic Field Cards (install reportlab for PDF output)\n")
        f.write(f"Generated: {datetime.datetime.now()}\n")
        f.write("\nUSB & AUX continuity quick checks\n")
    print(f"⚠️  reportlab missing; wrote {txt}")
else:
    c = canvas.Canvas(pdf_path, pagesize=letter)
    w,h = letter
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    def card(title, bullets):
        c.setFont("Helvetica-Bold", 16); c.drawString(0.7*inch, h-1*inch, title)
        c.setFont("Helvetica", 11); y = h-1.4*inch
        for b in bullets:
            c.drawString(0.9*inch, y, f"• {b}"); y -= 0.26*inch
        c.setFont("Helvetica-Oblique", 8)
        c.drawRightString(w-0.7*inch, 0.6*inch, f"Generated {ts} — v2.0.2")
        c.showPage()

    card("USB Continuity – Head Unit → Console Hub", [
        "5V present on VBUS (red)",
        "Ground continuity (black)",
        "D+ / D- twisted pair intact",
        "Shield tied to chassis only at one end",
        "No shorts between data lines and ground",
    ])
    card("AUX Continuity – Head Unit → OEM Breakout", [
        "L / R channels continuity",
        "Common ground continuity",
        "No cross‑talk (L↔R)",
        "Shield only terminated one end if required",
        "Wiggle test with tone generator",
    ])
    c.save()
    print(f"✅ Wrote {pdf_path}")
