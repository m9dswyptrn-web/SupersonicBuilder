#!/usr/bin/env python3
"""Insert badge strip overlay onto PDF cover page. Supports PNG, SVG, and other image formats."""
import argparse, os, sys
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

def overlay_page(width, height, image_path):
    """Create overlay page with badge strip image."""
    if not os.path.exists(image_path):
        print(f"[error] Badge strip asset not found: {image_path}")
        sys.exit(1)
    
    # Handle SVG files by converting to PNG using svglib
    actual_path = image_path
    temp_file = None
    
    if image_path.lower().endswith('.svg'):
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
            import tempfile
            
            # Convert SVG to ReportLab drawing
            drawing = svg2rlg(image_path)
            if drawing is None:
                raise ValueError(f"Failed to load SVG: {image_path}")
            
            # Render to temporary PNG file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.close()
            renderPM.drawToFile(drawing, temp_file.name, fmt='PNG', dpi=300)
            actual_path = temp_file.name
            
        except ImportError:
            print("[error] SVG support requires 'svglib' package. Install with: pip install svglib")
            print("[hint] Alternatively, use PNG format for badge strips")
            sys.exit(1)
        except Exception as e:
            print(f"[error] Failed to process SVG {image_path}: {e}")
            print("[hint] Use PNG format for badge strips instead")
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            sys.exit(1)
    
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    strip_height = 1.0*inch
    
    try:
        c.drawImage(actual_path, 0, height - strip_height, width=width, height=strip_height, 
                   preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"[error] Failed to draw badge strip image: {e}")
        if image_path.lower().endswith('.svg'):
            print("[hint] For SVG files, ensure 'svglib' is installed or use PNG format instead")
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        sys.exit(1)
    
    c.save()
    buf.seek(0)
    
    # Clean up temporary file if created
    if temp_file and os.path.exists(temp_file.name):
        os.unlink(temp_file.name)
    
    return PdfReader(buf).pages[0]

def insert_badge_strip_cover(input_pdf, output_pdf, image_path):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i == 0:
            overlay = overlay_page(float(page.mediabox.width), float(page.mediabox.height), image_path)
            page.merge_page(overlay)
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)
    print(f"[ok] Badge strip added to {output_pdf}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--strip", required=True)
    args = ap.parse_args()
    insert_badge_strip_cover(args.input, args.output, args.strip)
