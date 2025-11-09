#!/usr/bin/env python3
"""Stamp commit metadata into PDF files."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import os, sys

commit = os.environ.get("SB_COMMIT", "unknown")
version = os.environ.get("SB_VERSION", "unknown")
repo = os.environ.get("SB_REPO", "unknown")
bdate = os.environ.get("SB_BUILD_DATE", "unknown")

def stamp_pdf(src: Path):
    """Add commit metadata to a PDF file."""
    out = PdfWriter()
    r = PdfReader(str(src))
    for p in r.pages:
        out.add_page(p)
    
    md = {
        "/Producer": "SonicBuilder",
        "/Creator": "SonicBuilder PDF Pipeline",
        "/Title": src.stem,
        "/Subject": f"SonicBuilder docs {version}",
        "/Keywords": f"sonicbuilder, {version}, {commit}",
        "/Version": version,
        "/Commit": commit,
        "/Repository": repo,
        "/BuildDate": bdate
    }
    
    # Merge with existing metadata
    info = r.metadata or {}
    info.update(md)
    out.add_metadata(info)
    
    tmp = src.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as f:
        out.write(f)
    tmp.replace(src)

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "release_assets")
    stamped = 0
    for p in root.rglob("*.pdf"):
        try:
            stamp_pdf(p)
            print(f"[stamp] {p.name}")
            stamped += 1
        except Exception as e:
            print(f"[warn] {p}: {e}", file=sys.stderr)
    print(f"Stamped {stamped} PDF(s)")

if __name__ == "__main__":
    main()
