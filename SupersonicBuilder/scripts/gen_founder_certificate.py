#!/usr/bin/env python3
"""
Generate SonicBuilder Founder Certificate
Certificate #0001 - Christopher Elgin
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def read_version():
    """Read version from VERSION.txt"""
    if os.path.exists("VERSION.txt"):
        with open("VERSION.txt", "r") as f:
            first_line = f.readline().strip()
            if ":" in first_line:
                return first_line.split(":", 1)[1].strip()
            return first_line
    return "v2.5.0"

def generate_certificate(output_path, print_version=False):
    """Generate founder certificate PDF"""
    
    # Page setup
    c = canvas.Canvas(output_path, pagesize=letter)
    page_width, page_height = letter
    
    # Colors
    dark_gray = HexColor('#1a1a1a')
    medium_gray = HexColor('#333333')
    light_gray = HexColor('#666666')
    gold = HexColor('#DAA520')
    
    # Version and date
    version = read_version()
    build_date = datetime.now().strftime("%B %d, %Y")
    
    # Print version gets heavier border and better printing specs
    if print_version:
        # Decorative border for print
        c.setStrokeColor(gold)
        c.setLineWidth(4)
        c.rect(0.5*inch, 0.5*inch, page_width - 1*inch, page_height - 1*inch)
        
        c.setStrokeColor(dark_gray)
        c.setLineWidth(1)
        c.rect(0.6*inch, 0.6*inch, page_width - 1.2*inch, page_height - 1.2*inch)
    else:
        # Simple border for digital
        c.setStrokeColor(dark_gray)
        c.setLineWidth(2)
        c.rect(0.5*inch, 0.5*inch, page_width - 1*inch, page_height - 1*inch)
    
    # Add seal/badge watermark (centered, subtle)
    seal_path = "Founder_Seal/SonicBuilder_Seal.png"
    if os.path.exists(seal_path):
        c.saveState()
        c.setFillAlpha(0.08)
        seal_size = 400
        c.drawImage(
            seal_path,
            (page_width - seal_size) / 2,
            (page_height - seal_size) / 2 - 50,
            width=seal_size,
            height=seal_size,
            mask='auto',
            preserveAspectRatio=True
        )
        c.restoreState()
    
    # Header seal (top right)
    if os.path.exists(seal_path):
        seal_size = 100
        c.drawImage(
            seal_path,
            page_width - seal_size - 0.75*inch,
            page_height - seal_size - 0.75*inch,
            width=seal_size,
            height=seal_size,
            mask='auto'
        )
    
    # Title
    c.setFillColor(dark_gray)
    c.setFont("Helvetica-Bold", 24)
    title = "SONICBUILDER PLATFORM"
    c.drawCentredString(page_width / 2, page_height - 1.5*inch, title)
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width / 2, page_height - 1.9*inch, "OFFICIAL FOUNDER CERTIFICATE")
    
    # Certificate number
    c.setFont("Helvetica", 10)
    c.setFillColor(light_gray)
    c.drawCentredString(page_width / 2, page_height - 2.2*inch, "Certificate No. #0001")
    
    # Decorative line
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.line(2*inch, page_height - 2.5*inch, page_width - 2*inch, page_height - 2.5*inch)
    
    # Recognition text
    c.setFillColor(dark_gray)
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_width / 2, page_height - 3.2*inch, "This is to formally recognize")
    
    # Medal/trophy icon and founder name
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width / 2, page_height - 3.7*inch, "🥇  CHRISTOPHER ELGIN")
    
    # Title
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_width / 2, page_height - 4.1*inch, "as the Official Founder and Original Architect")
    c.drawCentredString(page_width / 2, page_height - 4.4*inch, "of the SonicBuilder Platform")
    
    # Decorative line
    c.setStrokeColor(gold)
    c.setLineWidth(1)
    c.line(2*inch, page_height - 4.8*inch, page_width - 2*inch, page_height - 4.8*inch)
    
    # Details section
    y_pos = page_height - 5.5*inch
    c.setFillColor(medium_gray)
    c.setFont("Helvetica-Bold", 11)
    
    details = [
        f"Platform Version: {version}",
        "Project Origin: EOENKK Android 15 + Maestro RR2 GM5 Integration",
        f"Date of Inception: {build_date}",
        "Certificate Issued: Certificate #0001"
    ]
    
    for detail in details:
        c.drawCentredString(page_width / 2, y_pos, detail)
        y_pos -= 0.3*inch
    
    # Signature section
    y_pos = page_height - 7.5*inch
    
    # Signature line
    c.setStrokeColor(dark_gray)
    c.setLineWidth(0.5)
    sig_line_width = 2.5*inch
    sig_x = page_width / 2 - sig_line_width / 2
    c.line(sig_x, y_pos, sig_x + sig_line_width, y_pos)
    
    c.setFillColor(medium_gray)
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_width / 2, y_pos - 0.25*inch, "Christopher Elgin — Founder")
    c.drawCentredString(page_width / 2, y_pos - 0.5*inch, "SonicBuilder Platform")
    
    # Footer seal/badge
    badge_path = "Founder_Seal/SonicBuilder_Badge.png"
    if os.path.exists(badge_path):
        c.saveState()
        c.setFillAlpha(0.6)
        badge_size = 60
        c.drawImage(
            badge_path,
            page_width / 2 - badge_size / 2,
            0.75*inch,
            width=badge_size,
            height=badge_size,
            mask='auto'
        )
        c.restoreState()
    
    # Footer text
    c.setFillColor(light_gray)
    c.setFont("Helvetica", 8)
    footer_y = 1.5*inch
    c.drawCentredString(page_width / 2, footer_y, f"CHRISTOPHER ELGIN | FOUNDER | {version} | CERT #0001")
    c.drawCentredString(page_width / 2, footer_y - 0.15*inch, "This certificate authenticates the founding and original architecture of SonicBuilder")
    
    # Print version note
    if print_version:
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(HexColor('#999999'))
        c.drawString(0.6*inch, 0.4*inch, "Print Edition — Optimized for Matte Finish Plaque Printing")
    
    c.save()
    print(f"[ok] Generated {output_path}")

def main():
    """Generate both digital and print certificates"""
    
    # Create output directory
    os.makedirs("certificates", exist_ok=True)
    
    # Generate digital version
    generate_certificate("certificates/Founder_Certificate_#0001.pdf", print_version=False)
    
    # Generate print version
    generate_certificate("certificates/Founder_Certificate_#0001_Print.pdf", print_version=True)
    
    print("[ok] Founder certificates generated")

if __name__ == "__main__":
    main()
