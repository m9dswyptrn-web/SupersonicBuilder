#!/usr/bin/env python3
"""
NextGen Engineering Appendix Builder
Converts docs/nextgen markdown files to professional PDF with FULL content including code
"""
import argparse
import sys
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parent.parent
NEXTGEN_DIR = ROOT / "docs" / "nextgen"
OUT = ROOT / "out"

def ensure_out():
    OUT.mkdir(exist_ok=True)

def parse_markdown(text):
    """Parse markdown into structured content blocks"""
    blocks = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Code blocks (fenced)
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            blocks.append(('code', '\n'.join(code_lines)))
            i += 1
            continue
        
        # Headers
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            blocks.append(('header', level, text))
            i += 1
            continue
        
        # Horizontal rule
        if re.match(r'^[-*_]{3,}$', line.strip()):
            blocks.append(('rule', None))
            i += 1
            continue
        
        # Regular text
        if line.strip():
            # Remove inline formatting
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)  # Bold
            clean_line = re.sub(r'\*(.+?)\*', r'\1', clean_line)  # Italic
            clean_line = re.sub(r'`(.+?)`', r'\1', clean_line)  # Inline code
            clean_line = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean_line)  # Links
            blocks.append(('text', clean_line))
        else:
            blocks.append(('blank', None))
        
        i += 1
    
    return blocks

def render_to_pdf(md_files, theme="dark", output_path=None):
    """Render markdown files to PDF with full content including code blocks"""
    if output_path is None:
        output_path = OUT / "NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf"
    pdf_path = Path(output_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter
    
    # Color scheme
    if theme == "dark":
        bg_color = colors.HexColor("#0c0e12")
        title_color = colors.HexColor("#00adff")
        text_color = colors.HexColor("#e6f0fa")
        header_color = colors.HexColor("#0099dd")
        code_bg = colors.HexColor("#1a1d23")
        code_text = colors.HexColor("#a0e0ff")
    else:
        bg_color = colors.white
        title_color = colors.HexColor("#0078b4")
        text_color = colors.black
        header_color = colors.HexColor("#0099dd")
        code_bg = colors.HexColor("#f5f5f5")
        code_text = colors.HexColor("#333333")
    
    margin_x = 0.75 * inch
    margin_y = inch
    line_height = 12
    
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        blocks = parse_markdown(content)
        
        # New page with background
        c.setFillColor(bg_color)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        
        # Document title
        c.setFillColor(title_color)
        c.setFont("Helvetica-Bold", 20)
        title = md_file.stem.replace("_", " ").replace("-", " ").title()
        c.drawCentredString(w/2, h - margin_y, title)
        
        y = h - margin_y - 40
        
        for block in blocks:
            if y < margin_y + 20:  # Need new page
                c.showPage()
                c.setFillColor(bg_color)
                c.rect(0, 0, w, h, fill=1, stroke=0)
                c.setFillColor(header_color)
                c.setFont("Helvetica", 8)
                c.drawString(margin_x, h - 0.5*inch, f"NextGen Appendix - {title}")
                y = h - margin_y
            
            if block[0] == 'header':
                level, text = block[1], block[2]
                c.setFillColor(header_color)
                font_size = max(16 - level * 2, 10)
                c.setFont("Helvetica-Bold", font_size)
                c.drawString(margin_x, y, text)
                y -= font_size + 8
                c.setFillColor(text_color)
            
            elif block[0] == 'text':
                text_line = block[1]
                c.setFillColor(text_color)
                c.setFont("Helvetica", 9)
                # Wrap long lines
                max_chars = 95
                if len(text_line) > max_chars:
                    words = text_line.split()
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if len(test_line) > max_chars and current_line:
                            c.drawString(margin_x, y, ' '.join(current_line))
                            y -= line_height
                            current_line = [word]
                        else:
                            current_line.append(word)
                    if current_line:
                        c.drawString(margin_x, y, ' '.join(current_line))
                        y -= line_height
                else:
                    c.drawString(margin_x, y, text_line)
                    y -= line_height
            
            elif block[0] == 'code':
                code_text_val = block[1]
                code_lines = code_text_val.split('\n')
                
                # Calculate code block height
                code_height = len(code_lines) * line_height + 20
                
                # Check if we need a new page for the code block
                if y - code_height < margin_y:
                    c.showPage()
                    c.setFillColor(bg_color)
                    c.rect(0, 0, w, h, fill=1, stroke=0)
                    y = h - margin_y
                
                # Draw code background
                c.setFillColor(code_bg)
                c.rect(margin_x - 5, y - code_height + 10, w - 2*margin_x + 10, code_height, fill=1, stroke=0)
                
                # Draw code text
                c.setFillColor(code_text)
                c.setFont("Courier", 8)
                code_y = y - 10
                for code_line in code_lines:
                    if code_y > margin_y:
                        # Truncate very long lines
                        if len(code_line) > 105:
                            code_line = code_line[:102] + "..."
                        c.drawString(margin_x, code_y, code_line)
                        code_y -= line_height
                
                y = code_y - 15
                c.setFillColor(text_color)
            
            elif block[0] == 'rule':
                c.setStrokeColor(header_color)
                c.line(margin_x, y, w - margin_x, y)
                y -= 15
            
            elif block[0] == 'blank':
                y -= line_height / 2
        
        # Page break after each document
        c.showPage()
    
    c.save()
    
    # Stamp metadata
    try:
        import pikepdf
        from pikepdf import Pdf, String
        with Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            info = pdf.docinfo
            info["/Title"] = String("SonicBuilder NextGen Engineering Appendix")
            info["/Author"] = String("SonicBuilder NextGen Engineering")
            info["/Subject"] = String("Teensy 4.1 / CANable Dual-Bus CAN Bridge - Complete Technical Documentation")
            info["/Keywords"] = String("SonicBuilder,NextGen,Teensy,CANable,GMLAN,CAN,Firmware")
            info["/Creator"] = String("SonicBuilder Pipeline")
            info["/Producer"] = String("pikepdf + reportlab")
            pdf.save(pdf_path)
    except Exception as e:
        print("Metadata stamp warning:", e)
    
    print("Built:", pdf_path)
    return pdf_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_dir", default=str(NEXTGEN_DIR))
    ap.add_argument("--out", dest="output_file", default=str(OUT / "NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf"))
    ap.add_argument("--theme", default="dark", choices=["dark", "light"])
    ap.add_argument("--verify", action="store_true")
    A = ap.parse_args()
    
    ensure_out()
    
    # Find markdown files
    md_files = sorted(Path(A.input_dir).glob("*.md"))
    if not md_files:
        print(f"Error: No markdown files found in {A.input_dir}")
        sys.exit(1)
    
    # Override global output path
    global OUTPUT_PATH
    OUTPUT_PATH = Path(A.output_file)
    
    pdf_path = render_to_pdf(md_files, theme=A.theme, output_path=OUTPUT_PATH)
    
    if A.verify:
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_docs.py"), str(pdf_path)])

if __name__ == "__main__":
    main()
