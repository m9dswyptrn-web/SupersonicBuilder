#!/usr/bin/env python3
import os, re, unicodedata
from pathlib import Path

DIAGRAM_DIR = Path("manual/04-Appendix/Wiring_Diagrams")
INDEX_MD    = DIAGRAM_DIR / "00_index.md"

def titleize(s: str) -> str:
    s = os.path.splitext(s)[0]
    s = s.replace("_", " ").replace("-", " ").strip()
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s)
    words = s.split(" ")
    titled = " ".join(w.upper() if w.isupper() and len(w) <= 4 else w.capitalize() for w in words)
    return titled

def group_key(filename: str) -> str:
    base = os.path.splitext(filename)[0]
    if "_" in base: return base.split("_", 1)[0].upper()
    if "-" in base: return base.split("-", 1)[0].upper()
    return "MISC"

def collect_files():
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    exts = (".png",".jpg",".jpeg",".svg",".pdf")
    files = [f for f in sorted(DIAGRAM_DIR.iterdir()) if f.suffix.lower() in exts]
    return files

def build_index(files):
    groups = {}
    for f in files:
        groups.setdefault(group_key(f.name), []).append(f)
    for g in groups:
        groups[g].sort(key=lambda p: titleize(p.name))

    lines = []
    lines.append("# Wiring Diagram Index")
    lines.append("")
    lines.append("> Legend: Prefix groups speed lookup — AUDIO (Audio), CAN (CAN/GMLAN), POWER (Power/Fusing), MISC (General).")
    lines.append("> Final page numbers & QR icons are added during PDF build.")
    lines.append("")

    for g in sorted(groups.keys()):
        lines.append(f"## {g.title()}")
        lines.append("")
        for f in groups[g]:
            lines.append(f"- {titleize(f.name)}  — `{f.name}`")
        lines.append("")

    lines.append("---\n\n## A–Z Index\n")
    flat = sorted(files, key=lambda p: titleize(p.name))
    for f in flat:
        lines.append(f"- {titleize(f.name)}")
    return "\n".join(lines) + "\n"

def main():
    files = collect_files()
    INDEX_MD.write_text(build_index(files), encoding="utf-8")
    print(f"[ok] Wrote legend index -> {INDEX_MD} (entries: {len(files)})")

if __name__ == "__main__":
    main()
