#!/usr/bin/env python3
"""
SonicBuilder CoA Generator — QR‑Ready Drop-in
---------------------------------------------
- Auto-incrementing serials (CoA_Log.csv)
- PDF certificate with founder seal and QR (if available)
- URL/QR fallback chain:
    1) CLI --qr
    2) env SB_REPO_URL
    3) env GITHUB_REPOSITORY -> https://github.com/<slug>
    4) Replit app default (EDIT BELOW if needed)
"""

import os
import csv
import argparse
import datetime as dt
from pathlib import Path

# PDF deps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

# Optional QR
_QR_OK = True
try:
    import qrcode
except Exception:
    _QR_OK = False

DEFAULT_REPLIT_URL = "https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev"

def resolve_repo_url(cli_qr: str | None) -> str:
    if cli_qr:
        return cli_qr
    env = os.environ.get("SB_REPO_URL")
    if env:
        return env
    gh = os.environ.get("GITHUB_REPOSITORY")
    if gh:
        return f"https://github.com/{gh}"
    return DEFAULT_REPLIT_URL

def next_serial(log_csv: Path) -> int:
    if not log_csv.exists():
        return 1
    try:
        with log_csv.open("r", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return 1
        last = rows[-1].get("serial", "").strip().lstrip("#").lstrip("0")
        return (int(last) if last.isdigit() else len(rows)) + 1
    except Exception:
        return 1

def pad_serial(n: int) -> str:
    return f"{n:04d}"

def draw_founder_seal(c: canvas.Canvas, W, H, founder, version, alpha=0.08, y_factor=0.62):
    c.saveState()
    try:
        c.setFillGray(1, alpha=alpha)
    except TypeError:
        c.setFillColorRGB(1,1,1)
    x, y, r = W/2.0, H*y_factor, 140
    c.setStrokeColorRGB(0.75,0.75,0.8)
    c.circle(x,y,r,stroke=1,fill=0)
    c.circle(x,y,r-36,stroke=1,fill=0)
    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x, y+r-20, "SONICBUILDER PLATFORM — OFFICIAL BUILD PROJECT")
    c.setFont("Helvetica", 10)
    c.drawCentredString(x, y-(r-20), f"{founder} | Founder | {version} | CERT #0001")
    c.restoreState()

def gen_pdf(outfile: Path, serial: str, version: str, installer: str, customer: str, qr_url: str):
    W, H = letter
    c = canvas.Canvas(str(outfile), pagesize=letter)
    # dark background
    c.setFillColorRGB(0.1,0.1,0.12)
    c.rect(0,0,W,H,stroke=0,fill=1)

    # title
    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(1.0*inch, H-1.2*inch, "Certificate of Authenticity")
    c.setFont("Helvetica", 12)
    c.drawString(1.0*inch, H-1.55*inch, f"SonicBuilder Serial: #{serial}  •  Version: {version}")

    # seal
    draw_founder_seal(c, W, H, "Christopher Elgin", version)

    # body
    c.setFont("Helvetica", 11)
    y = H-2.0*inch
    info = [
        f"Issued: {dt.date.today().isoformat()}",
        f"Installer: {installer or '—'}",
        f"Customer/Project: {customer or '—'}",
        f"Repository / Link: {qr_url}",
    ]
    for line in info:
        c.drawString(1.0*inch, y, line); y -= 16

    # QR
    if _QR_OK:
        try:
            img = qrcode.make(qr_url)
            from reportlab.lib.utils import ImageReader
            c.drawImage(ImageReader(img.get_image()), W-2.2*inch, 1.6*inch, width=1.4*inch, height=1.4*inch, mask='auto')
            c.setFont("Helvetica", 7.5)
            c.setFillColorRGB(0.8,0.8,0.86)
            c.drawCentredString(W-1.5*inch, 1.4*inch, "Scan for release / repo")
        except Exception:
            pass

    # footer
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.75,0.75,0.8)
    c.drawCentredString(W/2.0, 0.55*inch, f"SonicBuilder • Founder: Christopher Elgin • {dt.date.today().isoformat()} • Serial #{serial}")
    c.showPage(); c.save()

def append_log(log_csv: Path, serial: str, version: str, installer: str, customer: str, qr_url: str, fn: str):
    header = ["serial","date","version","installer","customer","qr","filename"]
    exists = log_csv.exists()
    with log_csv.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        w.writerow({
            "serial": f"#{serial}",
            "date": dt.date.today().isoformat(),
            "version": version,
            "installer": installer,
            "customer": customer,
            "qr": qr_url,
            "filename": fn
        })

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--serial", help="Manual serial number (e.g., 0005)")
    p.add_argument("--auto-increment", action="store_true", help="Take next serial from CoA_Log.csv")
    p.add_argument("--version", default="v2.0.9")
    p.add_argument("--installer", default="Christopher Elgin")
    p.add_argument("--customer", default="SonicBuilder")
    p.add_argument("--qr", help="URL for QR code / metadata")
    p.add_argument("--output-dir", default="output")
    p.add_argument("--log", default="CoA_Log.csv")
    a = p.parse_args()

    qr_url = resolve_repo_url(a.qr)
    outdir = Path(a.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    log_csv = Path(a.log)

    if a.serial:
        serial_num = a.serial
    else:
        serial_num = pad_serial(next_serial(log_csv)) if a.auto_increment else pad_serial(1)

    out_name = f"SonicBuilder_CoA_#{serial_num}.pdf"
    out_path = outdir / out_name

    gen_pdf(out_path, serial_num, a.version, a.installer, a.customer, qr_url)
    append_log(log_csv, serial_num, a.version, a.installer, a.customer, qr_url, out_name)

    print(f"Created {out_path} with QR → {qr_url}")
    print(f"Logged to {log_csv}")

if __name__ == "__main__":
    main()
