from pathlib import Path
dst = Path("docs/_fixed_preview"); dst.mkdir(parents=True, exist_ok=True)
(dst / "Supersonic_Dashboard.html").write_text("<!doctype html><h1>Auto-Fix Preview ✔</h1>", encoding="utf-8")
print("Wrote docs/_fixed_preview/Supersonic_Dashboard.html")
