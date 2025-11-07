#!/usr/bin/env python3
"""
tools/make_release_zip.py
Creates a timestamped release ZIP containing PDFs, VERSION, and index.html
"""
import zipfile
import time
from pathlib import Path

def main():
    build = Path("build")
    build.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    zip_name = build / f"Sonic_Builder_Release_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add PDFs
        for pdf in build.glob("*.pdf"):
            zf.write(pdf, pdf.name)
        
        # Add VERSION if exists
        version_file = Path("VERSION")
        if version_file.exists():
            zf.write(version_file, "VERSION")
        
        # Add index.html if exists
        index = build / "index.html"
        if index.exists():
            zf.write(index, "index.html")
        
        # Add RELEASE_NOTES.txt if exists
        notes = build / "RELEASE_NOTES.txt"
        if notes.exists():
            zf.write(notes, "RELEASE_NOTES.txt")
    
    print(f"📦 Created {zip_name}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
