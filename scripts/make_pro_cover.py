#!/usr/bin/env python3
"""Generate SonicBuilder PRO Cover Page"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

def make_pro_cover():
    OUT.mkdir(exist_ok=True)
    pdf_path = OUT / "SonicBuilder_Pro_Cover.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter
    
    # Dark background
    c.setFillColorRGB(0.047, 0.055, 0.071)  # Dark blue-gray
    c.rect(0, 0, w, h, fill=1, stroke=0)
    
    # Title
    c.setFillColorRGB(0, 0.68, 0.94)  # Bright blue
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(w/2, h-200, "SonicBuilder")
    
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(w/2, h-260, "Professional Installation Manual")
    
    # Subtitle
    c.setFillColorRGB(0.9, 0.94, 0.98)  # Light text
    c.setFont("Helvetica", 18)
    c.drawCentredString(w/2, h-320, "2014 Chevrolet Sonic LTZ")
    c.drawCentredString(w/2, h-350, "Android Head Unit Integration")
    
    # Version
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, h-420, "Complete Edition")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h-445, "Includes Supersonic 4-Pack + NextGen Engineering Appendix")
    
    # Components list
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.7, 0.8, 0.9)
    y = h/2 - 50
    components = [
        "• EOENKK 10.1\" Android 13 Head Unit",
        "• Maestro RR2 GM5 Interface Module",
        "• Teensy 4.1 / CANable Dual-Bus CAN Bridge",
        "• GMLAN HS-CAN (500 kbps) + SW-CAN (33.333 kbps)",
        "• Electrical Validation & Wiring Expansion",
        "• Complete Parts List & Tools Reference"
    ]
    for comp in components:
        c.drawString(100, y, comp)
        y -= 20
    
    # Footer
    c.setFillColorRGB(0, 0.68, 0.94)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(w/2, 80, "SonicBuilder Engineering")
    c.setFont("Helvetica", 9)
    c.drawCentredString(w/2, 65, "Professional-Grade Installation Documentation")
    c.drawCentredString(w/2, 50, "v2.2.0-SB-NEXTGEN")
    
    c.save()
    print(f"✓ Created: {pdf_path}")

if __name__ == "__main__":
    make_pro_cover()
