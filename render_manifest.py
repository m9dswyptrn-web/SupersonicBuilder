#!/usr/bin/env python3
"""
render_manifest.py — SonicBuilder v5 Series
Generates Certified Manifest PDFs (dark + light themes), Field Cards, Certificates,
and bundles them into a master FULL zip.

Usage examples:
  python3 render_manifest.py --version 5.0.0 --release-zip /path/to/SonicBuilder_2025-10-31_v5.0.0.zip --out ./dist --all
  python3 render_manifest.py --version 5.0.0 --out ./dist --dark-only
  python3 render_manifest.py --version 5.0.0 --out ./dist --light-only

Integrating with builder.py:
  - Add a flag like --render-manifest that shells out to:
      python3 render_manifest.py --version <ver> --release-zip <zip> --out <builder-output-dir> --all
"""

import argparse, hashlib, datetime, textwrap, zipfile, os
from pathlib import Path

# ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

def sha256_of(p: Path) -> str:
    h=hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def page_footer(c: canvas.Canvas, color, page_w, page_h, text):
    c.setFillColor(color)
    c.setFont("Helvetica", 8)
    c.drawRightString(page_w - 0.5*inch, 0.4*inch, text)

def draw_grid(c: canvas.Canvas, color, page_w, page_h, step=0.5*inch, line_w=0.25):
    c.saveState()
    c.setStrokeColor(color); c.setLineWidth(line_w)
    y=0
    while y<page_h:
        c.line(0, y, page_w, y); y += step
    x=0
    while x<page_w:
        c.line(x, 0, x, page_h); x += step
    c.restoreState()

def cover_title(c, fg, accent, page_w, page_h, title, subtitle):
    c.setFillColor(fg); c.setFont("Helvetica-Bold", 26)
    c.drawString(0.8*inch, page_h-1.2*inch, title)
    c.setFillColor(accent); c.setFont("Helvetica", 14)
    c.drawString(0.8*inch, page_h-1.6*inch, subtitle)

def draw_section(c, fg, accent, x, y, w, h, heading, body_lines):
    c.saveState()
    c.setFillColor(fg); c.setStrokeColor(accent); c.setLineWidth(1)
    c.roundRect(x, y, w, h, 10, stroke=1, fill=0)
    c.setFillColor(accent); c.setFont("Helvetica-Bold", 14)
    c.drawString(x+12, y+h-18, heading)
    c.setFillColor(fg); c.setFont("Helvetica", 10)
    ty = y+h-36
    for line in body_lines:
        c.drawString(x+12, ty, line); ty -= 14
        if ty < y+16: break
    c.restoreState()

def add_qr(c, x, y, size, data_text):
    code = qr.QrCodeWidget(data_text)
    b = code.getBounds()
    w = b[2]-b[0]; h=b[3]-b[1]
    d = Drawing(size, size, transform=[size/w,0,0,size/h,0,0])
    d.add(code)
    renderPDF.draw(d, c, x, y)

DARK_THEMES = {
    "Industrial_DarkMetal": {
        "bg": colors.black,
        "fg": colors.HexColor("#E6E6E6"),
        "accent": colors.HexColor("#00D2FF"),
        "sub": colors.HexColor("#9AA0A6"),
        "grid": colors.HexColor("#202225"),
    },
    "Retro_Blueprint": {
        "bg": colors.HexColor("#0D1B3D"),
        "fg": colors.white,
        "accent": colors.HexColor("#36F9A0"),
        "sub": colors.HexColor("#CFE3FF"),
        "grid": colors.HexColor("#132753"),
    },
    "OEM_ShopManual": {
        "bg": colors.HexColor("#1C1C1C"),
        "fg": colors.HexColor("#E7D8A7"),
        "accent": colors.HexColor("#E53935"),
        "sub": colors.HexColor("#B0B0B0"),
        "grid": colors.HexColor("#2A2A2A"),
    },
}

LIGHT_THEMES = {
    "Industrial_LightSteel": {
        "bg": colors.whitesmoke,
        "fg": colors.HexColor("#1F2933"),
        "accent": colors.HexColor("#0EA5E9"),
        "sub": colors.HexColor("#6B7280"),
        "grid": colors.HexColor("#E5E7EB"),
    },
    "Retro_Draftsheet": {
        "bg": colors.HexColor("#FAF7F2"),
        "fg": colors.HexColor("#0B4F6C"),
        "accent": colors.HexColor("#22C55E"),
        "sub": colors.HexColor("#64748B"),
        "grid": colors.HexColor("#E2E8F0"),
    },
    "OEM_ServiceWhite": {
        "bg": colors.HexColor("#FFFFFF"),
        "fg": colors.HexColor("#1F1F1F"),
        "accent": colors.HexColor("#E53935"),
        "sub": colors.HexColor("#6D6D6D"),
        "grid": colors.HexColor("#EFEFEF"),
    },
}

def manifest_pages(version, zip_checksum, theme_name, theme, out_dir: Path, light=False):
    folder = out_dir/theme_name
    folder.mkdir(parents=True, exist_ok=True)
    pdf = folder/("Manifest_Full.pdf")
    c = canvas.Canvas(str(pdf), pagesize=letter)
    W,H = letter

    # Cover
    c.setFillColor(theme["bg"]); c.rect(0,0,W,H, stroke=0, fill=1)
    draw_grid(c, theme["grid"], W, H, step=0.5*inch, line_w=0.25 if light else 0.35)
    cover_title(c, theme["fg"], theme["accent"], W, H, f"SonicBuilder v{version}",
                f"Certified Manifest — Full Manual ({'Light' if light else 'Dark'})")

    # Sections
    sections = [
        ("Version Timeline", [
            "v4.0 → v4.7: builder chain, ADB selector, dry-run, checksums, HTML reports, diff",
            "v4.8: Mode presets (tuning, release, compare) + defaults",
            "v4.9: Persistent sonicbuilder.toml (default_mode, dark, bands)",
            "v5.0: Release default, certified package"
        ]),
        ("CLI Command Map", [
            "./build.sh --mode tuning/release/compare",
            "--html-report --html-dark --html-bands --diff A,B",
            "--export-schema --lint --autofix --no-pdf",
            "--adb-group <name> --zip-group-only --select-adb",
            "--adb-alias <name> --set-adb-alias <name>"
        ]),
        ("Workflows", [
            "Tuning: report + bands + diff; per-group pushes, quick zip.",
            "Release: schema + lint + autofix + PDFs + dark report.",
            "Compare: dark + diff; optional auto-pair."
        ]),
        ("Config", [
            "sonicbuilder.toml: default_mode, html_dark, html_bands, no_pdf, select_adb, adb_alias, adb_group",
            "Env: ANDROID_USE_ADB, ANDROID_ADB_PATH, ANDROID_DST"
        ]),
    ]
    y = H-2.2*inch
    for (head, body) in sections:
        draw_section(c, theme["fg"], theme["accent"], 0.7*inch, y-1.7*inch, W-1.4*inch, 1.5*inch, head, body)
        y -= 1.8*inch
        if y < 2.0*inch:
            page_footer(c, theme["sub"], W, H, f"v{version}  |  SHA256(zip) {zip_checksum[:16]}…  |  {datetime.date.today().isoformat()}")
            c.showPage()
            c.setFillColor(theme["bg"]); c.rect(0,0,W,H, stroke=0, fill=1)
            draw_grid(c, theme["grid"], W, H, step=0.5*inch, line_w=0.25 if light else 0.35)
            y = H-1.2*inch

    # Screens placeholder
    draw_section(c, theme["fg"], theme["accent"], 0.7*inch, 1.4*inch, W-1.4*inch, 1.8*inch, "Report Screens", [
        "Embed report.html screenshots here (band plots, tables, diffs).",
        "Open output/report.html for interactive view."
    ])

    page_footer(c, theme["sub"], W, H, f"v{version}  |  SHA256(zip) {zip_checksum[:32]}…  |  {datetime.date.today().isoformat()}")
    c.showPage(); c.save()
    return pdf

def field_cards(version, zip_checksum, theme_name, theme, out_dir: Path, light=False):
    folder = out_dir/theme_name; folder.mkdir(parents=True, exist_ok=True)
    pdf = folder/"FieldCards.pdf"
    page = (5.5*inch, 8.5*inch)
    c = canvas.Canvas(str(pdf), pagesize=page)
    W,H = page
    cards = [
        ("Tuning Card", [
            "--mode tuning",
            "--html-report --html-dark --html-bands",
            "--diff group/A.json,group/B.json",
            "--adb-group <name> --zip-group-only"
        ]),
        ("Release Card", [
            "--mode release",
            "--export-schema --lint --autofix",
            "PDFs on, HTML report dark",
            "Versioned outputs, checksums"
        ]),
        ("Compare Card", [
            "--mode compare",
            "--diff group/A.json,group/B.json",
            "Auto-pair if omitted"
        ]),
    ]
    for (title, lines) in cards:
        c.setFillColor(theme["bg"]); c.rect(0,0,W,H, stroke=0, fill=1)
        draw_grid(c, theme["grid"], W, H, step=0.4*inch, line_w=0.25 if light else 0.35)
        c.setFillColor(theme["accent"]); c.setFont("Helvetica-Bold", 16)
        c.drawString(0.4*inch, H-0.8*inch, title)
        c.setFillColor(theme["fg"]); c.setFont("Helvetica", 10)
        y = H-1.2*inch
        for ln in lines:
            c.drawString(0.4*inch, y, ln); y -= 0.22*inch
        page_footer(c, theme["sub"], W, H, f"v{version}  |  SHA256(zip) {zip_checksum[:16]}…")
        c.showPage()
    c.save()
    return pdf

def certificate(version, zip_checksum, package_name, out_dir: Path, light=False):
    pdf = out_dir/("Version_Certificate_Light.pdf" if light else "Version_Certificate.pdf")
    c = canvas.Canvas(str(pdf), pagesize=letter)
    W,H = letter
    if light:
        bg, fg, border = colors.whitesmoke, colors.HexColor("#1F2937"), colors.HexColor("#0EA5E9")
        c.setFillColor(bg); c.rect(0,0,W,H, stroke=0, fill=1)
        c.setFillColor(colors.white); c.rect(0.4*inch,0.4*inch,W-0.8*inch,H-0.8*inch, stroke=0, fill=1)
        c.setStrokeColor(border); c.setLineWidth(3)
        c.roundRect(0.5*inch,0.5*inch,W-1.0*inch,H-1.0*inch, 16, stroke=1, fill=0)
        c.setFillColor(fg); c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(W/2, H-1.0*inch, "SonicBuilder Certified Manifest")
        c.setFont("Helvetica", 12)
        c.drawCentredString(W/2, H-1.3*inch, f"Version v{version}  •  {datetime.date.today().isoformat()}")
        left = 1.0*inch; top = H-2.0*inch; c.setFont("Helvetica", 11)
        for ln in [f"Primary Package: {package_name}",
                   f"SHA-256: {zip_checksum}",
                   "Scope: Triple-theme documentation set with full manuals and field cards (Light Edition).",
                   "Source of truth: SonicBuilder release build."]:
            c.drawString(left, top, ln); top -= 14
        add_qr(c, W-2.3*inch, 1.2*inch, 1.6*inch, f"SonicBuilder v{version} | SHA256 {zip_checksum}")
        c.setFont("Helvetica-Oblique", 9); c.setFillColor(colors.HexColor("#6B7280"))
        c.drawRightString(W-0.6*inch, 0.6*inch, "Generated by SonicBuilder Manifest Engine (Light)")
    else:
        bg, fg, border = colors.black, colors.HexColor("#E6E6E6"), colors.HexColor("#00D2FF")
        c.setFillColor(bg); c.rect(0,0,W,H, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#111316")); c.rect(0.4*inch,0.4*inch,W-0.8*inch,H-0.8*inch, stroke=0, fill=1)
        c.setStrokeColor(border); c.setLineWidth(3)
        c.roundRect(0.5*inch,0.5*inch,W-1.0*inch,H-1.0*inch, 16, stroke=1, fill=0)
        c.setFillColor(fg); c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(W/2, H-1.0*inch, "SonicBuilder Certified Manifest")
        c.setFont("Helvetica", 12)
        c.drawCentredString(W/2, H-1.3*inch, f"Version v{version}  •  {datetime.date.today().isoformat()}")
        left = 1.0*inch; top = H-2.0*inch; c.setFont("Helvetica", 11)
        for ln in [f"Primary Package: {package_name}",
                   f"SHA-256: {zip_checksum}",
                   "Scope: Triple-theme documentation set with full manuals and field cards.",
                   "Source of truth: SonicBuilder release build."]:
            c.drawString(left, top, ln); top -= 14
        add_qr(c, W-2.3*inch, 1.2*inch, 1.6*inch, f"SonicBuilder v{version} | SHA256 {zip_checksum}")
        c.setFont("Helvetica-Oblique", 9); c.setFillColor(colors.HexColor("#9AA0A6"))
        c.drawRightString(W-0.6*inch, 0.6*inch, "Generated by SonicBuilder Manifest Engine")
    c.showPage(); c.save()
    return pdf

def build_theme_set(version, zip_checksum, out_dir: Path, themes: dict, light=False):
    for name, theme in themes.items():
        manifest_pages(version, zip_checksum, name, theme, out_dir, light=light)
        field_cards(version, zip_checksum, name, theme, out_dir, light=light)

def write_readme_checksums(version, zip_checksum, package_name, out_dir: Path, light=False):
    readme = out_dir/"README.txt"
    title = "Certified Manifest Package (Light Edition)" if light else "Certified Manifest Package"
    readme.write_text(textwrap.dedent(f"""
    SonicBuilder v{version} — {title}
    ---------------------------------------------
    This archive contains three themed documentation sets.
    Each set includes:
      - Manifest_Full.pdf   (8.5x11 manual)
      - FieldCards.pdf      (5.5x8.5 laminated reference)

    Version: v{version}
    Primary ZIP checksum:
      SHA-256  {package_name}
      {zip_checksum}

    Rendered: {datetime.datetime.now().isoformat()}
    """).strip()+"\n")

    checks = []
    for f in sorted(out_dir.rglob("*.pdf")):
        h = sha256_of(f)
        rel = f.relative_to(out_dir)
        checks.append(f"{h}  {rel}")
    (out_dir/"CHECKSUMS.txt").write_text("\n".join(checks)+"\n")

def build_all(version: str, release_zip: str, out_root: Path, dark: bool, light: bool, make_full_zip: bool):
    out_root.mkdir(parents=True, exist_ok=True)
    
    # Derive package name from release_zip path, or use default
    if release_zip and Path(release_zip).exists():
        zip_checksum = sha256_of(Path(release_zip))
        package_name = Path(release_zip).name
    else:
        zip_checksum = "(zip not found)"
        package_name = f"SonicBuilder_v{version}.zip"
    
    dark_dir = out_root/"ManifestPackage"
    light_dir = out_root/"ManifestPackage_Light"

    if dark:
        dark_dir.mkdir(exist_ok=True)
        build_theme_set(version, zip_checksum, dark_dir, DARK_THEMES, light=False)
        certificate(version, zip_checksum, package_name, dark_dir, light=False)
        write_readme_checksums(version, zip_checksum, package_name, dark_dir, light=False)

    if light:
        light_dir.mkdir(exist_ok=True)
        build_theme_set(version, zip_checksum, light_dir, LIGHT_THEMES, light=True)
        certificate(version, zip_checksum, package_name, light_dir, light=True)
        write_readme_checksums(version, zip_checksum, package_name, light_dir, light=True)

    full_zip = None
    if make_full_zip:
        full_zip = out_root/f"SonicBuilder_Manifest_Package_v{version}_FULL.zip"
        with zipfile.ZipFile(full_zip, "w", zipfile.ZIP_DEFLATED) as z:
            if dark and dark_dir.exists():
                for p in dark_dir.rglob("*"):
                    z.write(p, p.relative_to(out_root))
            if light and light_dir.exists():
                for p in light_dir.rglob("*"):
                    z.write(p, p.relative_to(out_root))
    return full_zip

def parse_args():
    p = argparse.ArgumentParser(description="Render SonicBuilder certified manifest PDFs and zip")
    p.add_argument("--version", required=True, help="Version string, e.g., 5.0.0")
    p.add_argument("--release-zip", default="", help="Path to the SonicBuilder release .zip for checksum")
    p.add_argument("--out", default="./dist", help="Output directory root")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--all", action="store_true", help="Render both dark and light and produce FULL.zip")
    g.add_argument("--dark-only", action="store_true", help="Render only dark set")
    g.add_argument("--light-only", action="store_true", help="Render only light set")
    return p.parse_args()

def main():
    args = parse_args()
    out_root = Path(args.out)
    # decide modes
    dark = light = False
    make_full = False
    if args.all or (not args.dark_only and not args.light_only):
        dark = True; light = True; make_full = True
    elif args.dark_only:
        dark = True
    elif args.light_only:
        light = True
    full_zip = build_all(args.version, args.release_zip, out_root, dark, light, make_full_zip=make_full)
    if full_zip:
        print(f"[✓] Built FULL zip → {full_zip}")
    else:
        print(f"[✓] Rendered {'dark' if dark else ''}{' and ' if dark and light else ''}{'light' if light else ''} sets in {out_root}")

if __name__ == "__main__":
    main()
