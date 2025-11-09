#!/usr/bin/env python3
"""
SonicBuilder Fusion Appendix Injector v4.2
Automatically appends system-health summary to generated PDFs.
"""

import os
from fpdf import FPDF

APPENDIX_PATH = "docs/appendix_system_health.md"
OUTPUT_PDF = "output/SonicBuilder_Manual_Final.pdf"
FINAL_PDF = "output/SonicBuilder_Manual_With_Health.pdf"

class FusionPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "SonicBuilder System Health Appendix", 0, 1, "C")
        self.ln(5)

def append_health_report(base_pdf=OUTPUT_PDF, appendix=APPENDIX_PATH):
    if not os.path.exists(base_pdf):
        print(f"❌ Base PDF not found: {base_pdf}")
        return
    if not os.path.exists(appendix):
        print(f"⚠️ No appendix file found: {appendix}")
        return

    # Copy base pages
    fusion = FusionPDF()
    fusion.set_auto_page_break(auto=True, margin=15)

    # Merge the existing manual first
    from PyPDF2 import PdfReader
    reader = PdfReader(base_pdf)
    for p in reader.pages:
        fusion.add_page()
        txt = p.extract_text()
        if txt:
            fusion.set_font("Helvetica", "", 12)
            fusion.multi_cell(0, 8, txt)

    # Append live appendix
    with open(appendix, "r") as f:
        appendix_text = f.read()

    fusion.add_page()
    fusion.set_font("Courier", "", 12)
    for line in appendix_text.splitlines():
        fusion.multi_cell(0, 8, line)

    os.makedirs(os.path.dirname(FINAL_PDF), exist_ok=True)
    fusion.output(FINAL_PDF)
    print(f"✅ Fusion Appendix attached → {FINAL_PDF}")

if __name__ == "__main__":
    append_health_report()