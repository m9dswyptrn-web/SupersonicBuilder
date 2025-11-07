#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import html

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "docs" / "images" / "mobo_back"
THUMBS_DIR = IMAGES_DIR / ".thumbs"
OUT_HTML = IMAGES_DIR / "gallery.html"
CSS_PATH = ROOT / "docs" / "styles" / "gallery_dark.css"
LB_CSS = ROOT / "docs" / "web_gallery" / "lightbox.css"
LB_JS = ROOT / "docs" / "web_gallery" / "lightbox.js"

VALID = {".jpg",".jpeg",".png",".webp"}

def rel_from_docs(p: Path) -> str:
    docs_root = ROOT / "docs"
    return p.resolve().as_posix().split(docs_root.as_posix() + "/", 1)[-1]

def thumb_for(p: Path) -> Path:
    t = THUMBS_DIR / p.name
    return t if t.exists() else p

def group_key(p: Path) -> str:
    try:
        parts = p.relative_to(IMAGES_DIR).parts
        return parts[0]
    except Exception:
        return "Ungrouped"

def build():
    if not IMAGES_DIR.exists():
        print("No images dir:", IMAGES_DIR)
        return 0
    imgs = sorted([p for p in IMAGES_DIR.rglob("*") if p.is_file() and p.suffix.lower() in VALID and ".thumbs" not in p.as_posix()])
    groups = {}
    for p in imgs:
        groups.setdefault(group_key(p), []).append(p)

    head = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Mobo Backside Gallery</title>
<link rel="stylesheet" href="/{rel_from_docs(CSS_PATH)}"/>
<link rel="stylesheet" href="/{rel_from_docs(LB_CSS)}"/>
</head><body>
<div class="container"><div class="header">
  <div class="title">Motherboard Backside Gallery</div>
  <div><span class="badge">Dark</span> <span class="badge">{html.escape(datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'))}</span></div>
</div>'''

    body = []
    for gname in sorted(groups.keys()):
        body.append(f'<div class="group"><h2>{html.escape(gname)}</h2><div class="grid">')
        for p in groups[gname]:
            t = thumb_for(p)
            full_href = "/" + rel_from_docs(p)
            thumb_href = "/" + rel_from_docs(t)
            cap = html.escape(p.stem.replace("_"," "))
            card = f'''<a class="card" href="{full_href}" data-lightbox-src="{full_href}" data-caption="{cap}">
  <img src="{thumb_href}" alt="{cap}"/><div class="meta">{cap}</div></a>'''
            body.append(card)
        body.append("</div></div>")

    tail = f'''
  <div class="footer">Generated automatically by SonicBuilder • <a href="/{rel_from_docs(IMAGES_DIR / 'index.md')}">Index</a></div>
</div>
<div class="lightbox-backdrop"><div class="lightbox-close" title="Close">✕</div>
  <div class="lightbox-stage"></div><div class="lightbox-caption"></div></div>
<script src="/{rel_from_docs(LB_JS)}"></script>
</body></html>'''

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(head + "\n".join(body) + tail, encoding="utf-8")
    print("✅ Wrote", OUT_HTML)
    return 0

if __name__ == "__main__":
    raise SystemExit(build())
