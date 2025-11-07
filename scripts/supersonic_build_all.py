#!/usr/bin/env python3
import argparse, os, sys, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "out"
DOCS = ROOT / "docs"
COMPOSER = ROOT / "SonicBuilder_PDF_Composer_Kit_v1_dark" / "tools"

def ensure_out():
    OUT.mkdir(parents=True, exist_ok=True)

def have_composer():
    return (COMPOSER / "compose_images_to_pdf.py").exists()

def render_markdown_to_images():
    from PIL import Image, ImageDraw, ImageFont
    IMG_DIR = ROOT / "imgs"
    IMG_DIR.mkdir(exist_ok=True)
    font = ImageFont.load_default()
    n = 1
    for md in sorted(DOCS.glob("*.md")):
        text = md.read_text()[:2000]
        img = Image.new("RGB", (2550,3300), (12,14,18))
        d = ImageDraw.Draw(img)
        d.text((120,120), md.name, font=font, fill=(0,173,239))
        d.text((120,220), text, font=font, fill=(230,240,250))
        img.save(IMG_DIR / f"{n:03d}_{md.stem}.png")
        n += 1
    return IMG_DIR

def compose_via_composer(img_dir, out_pdf):
    cmd = [sys.executable, str(COMPOSER / "compose_images_to_pdf.py"),
           "--in", str(img_dir / "*.png"),
           "--out", str(out_pdf),
           "--page", "Letter",
           "--margin", "24"]
    subprocess.check_call(cmd)

def fallback_reportlab(out_pdf):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(out_pdf), pagesize=letter)
    c.setTitle("SonicBuilder Manual (Placeholder)")
    c.drawString(72, 720, "SonicBuilder Manual")
    c.drawString(72, 700, "Placeholder build - provide images or PDF composer kit for full render.")
    c.showPage(); c.save()

def stamp_metadata(pdf_path, title="SonicBuilder v2.1.0-SB-4P", author="SonicBuilder", subject="Docs", keywords="SonicBuilder,Docs"):
    try:
        import pikepdf
        from pikepdf import Pdf, String
        with Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            info = pdf.docinfo
            info["/Title"]   = String(title)
            info["/Author"]  = String(author)
            info["/Subject"] = String(subject)
            info["/Keywords"]= String(keywords)
            info["/Creator"] = String("Supersonic Builder")
            info["/Producer"]= String("pikepdf")
            pdf.save(pdf_path)
    except Exception as e:
        print("Metadata stamp skipped:", e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v2.1.0-SB-4P")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--push", action="store_true")
    A = ap.parse_args()

    ensure_out()
    out_pdf = OUT / f"SonicBuilder_Supersonic_Manual_{A.version}.pdf"

    if have_composer():
        img_dir = render_markdown_to_images()
        compose_via_composer(img_dir, out_pdf)
    else:
        fallback_reportlab(out_pdf)

    stamp_metadata(out_pdf, title=f"SonicBuilder {A.version}")
    print("Built:", out_pdf)

if __name__ == "__main__":
    main()
