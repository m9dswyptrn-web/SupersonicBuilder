#!/usr/bin/env python3
"""Generate SonicBuilder Appendix Wiring Diagrams"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

def make_appendix_wiring():
    OUT.mkdir(exist_ok=True)
    pdf_path = OUT / "SonicBuilder_Appendix_Wiring.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter
    
    c.setTitle("SonicBuilder Wiring Diagrams Appendix")
    
    # Header
    c.setFillColorRGB(0, 0.68, 0.94)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(72, h-72, "Wiring Diagrams Appendix")
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(72, h-92, "Comprehensive wiring diagrams for EOENKK + Maestro RR2 GM5 integration")
    
    # Diagrams list
    y = h - 140
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, "Included Diagrams")
    y -= 25
    
    diagrams = [
        "1. EOENKK 44-Pin Harness Pinout",
        "2. Maestro RR2 GM5 Connection Diagram",
        "3. 2014 Sonic 11-Pin Radio Connector Pinout",
        "4. HS-GMLAN / SW-GMLAN Bus Architecture",
        "5. Teensy 4.1 Dual-Bus CAN Wiring",
        "6. Power Distribution (ACC, BAT+, GND)",
        "7. Speaker Wire Routing (Front/Rear)",
        "8. Steering Wheel Control Integration",
        "9. Backup Camera Input Wiring",
        "10. Chime Reroute Configuration"
    ]
    
    c.setFont("Helvetica", 11)
    for diagram in diagrams:
        c.drawString(80, y, diagram)
        y -= 22
    
    # Reference note
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "Reference Documentation")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(80, y, "• See docs/SonicBuilder_WiringExpansion_v1/ for detailed wiring guides")
    y -= 18
    c.drawString(80, y, "• See docs/nextgen/gmlan_pinout_reference.md for complete GMLAN pinouts")
    y -= 18
    c.drawString(80, y, "• See docs/nextgen/teensy41_firmware.md for Teensy wiring specifications")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(72, 50, "For full wiring expansion details, refer to the Supersonic 4-Pack documentation.")
    
    c.save()
    print(f"✓ Created: {pdf_path}")

if __name__ == "__main__":
    make_appendix_wiring()
