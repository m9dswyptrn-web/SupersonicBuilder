# QR Glyph + Back-to-Index — Micro Patch

- Adds a tiny **QR glyph** next to each Wiring Diagram Index entry
- Adds a clickable **“↩ Back to Index”** link on every diagram page (internal bookmark)
- Keeps QR stamp on each diagram page and page numbers in the index

Apply:
1) Replace `scripts/builder.py` in your repo with this one.
2) Rebuild:
```bash
pip install -r requirements.txt
make build_dark
```
