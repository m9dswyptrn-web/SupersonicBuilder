#!/usr/bin/env python3
"""Generate Simple SonicBuilder Parts Sheet"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

def make_parts_sheet():
    OUT.mkdir(exist_ok=True)
    pdf_path = OUT / "SonicBuilder_Parts_Sheet.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter
    
    c.setTitle("SonicBuilder Parts & Tools Reference")
    
    # Header
    c.setFillColorRGB(0, 0.68, 0.94)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(72, h-72, "Parts & Tools Reference")
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(72, h-92, "Complete bill of materials for 2014 Chevy Sonic LTZ Android head unit installation")
    
    # Required Parts
    y = h - 140
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, "Required Parts")
    y -= 25
    
    parts = [
        ("EOENKK Android Head Unit", "10.1\" Android 13, ~$250 USD"),
        ("Maestro RR2 GM5 Interface", "Steering wheel control retention, ~$150 USD"),
        ("44-Pin Harness Adapter", "Sonic-to-aftermarket radio harness, ~$20 USD"),
        ("Dash Kit", "2-DIN mounting bracket for Sonic, ~$30 USD"),
        ("Teensy 4.1 (Optional)", "Dual-bus CAN bridge, ~$27 USD"),
        ("CANable Pro (Alternative)", "USB-to-CAN adapter, ~$45 USD"),
        ("MCP2551 Transceivers (2x)", "For Teensy CAN buses, ~$5 USD"),
        ("Wire Kit", "22-24 AWG stranded, heat shrink, ~$15 USD")
    ]
    
    c.setFont("Helvetica", 10)
    for part, desc in parts:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(80, y, part)
        c.setFont("Helvetica", 9)
        c.drawString(100, y-12, desc)
        y -= 30
    
    # Tools
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, "Required Tools")
    y -= 25
    
    tools = [
        "Panel removal tools (plastic trim tools)",
        "Socket set (7mm, 10mm)",
        "Wire strippers / crimpers",
        "Multimeter (voltage & continuity testing)",
        "Soldering iron (for Teensy wiring)",
        "Heat gun (for heat shrink tubing)"
    ]
    
    c.setFont("Helvetica", 10)
    for tool in tools:
        c.drawString(80, y, "• " + tool)
        y -= 18
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(72, 50, "For detailed specifications, see: docs/SonicBuilder_ToolsAndDocs_v1/")
    
    c.save()
    print(f"✓ Created: {pdf_path}")

if __name__ == "__main__":
    make_parts_sheet()
