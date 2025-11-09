from pathlib import Path
DOCS = Path("docs")
PREV = DOCS / "_fixed_preview"
PREV.mkdir(parents=True, exist_ok=True)
src = DOCS / "Supersonic_Dashboard.html"
html = "<!doctype html><title>Preview</title><h1>Auto-Fix Preview</h1>"
if src.exists():
    try:
        text = src.read_text(encoding="utf-8", errors="ignore")
        html = text.replace("</body>", "<div style='position:fixed;bottom:8px;right:8px;padding:6px 10px;background:#ff0;color:#000;font-weight:700'>Auto-Fix Preview</div></body>")
    except Exception:
        pass
(PREV / "Supersonic_Dashboard.html").write_text(html, encoding="utf-8")
print("Wrote docs/_fixed_preview/Supersonic_Dashboard.html")
