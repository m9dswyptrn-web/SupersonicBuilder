
import os, json, imghdr, subprocess
from pathlib import Path

def _warn(msg): print("[assets] ⚠", msg)
def _info(msg): print("[assets] •", msg)
def _ok(msg): print("[assets] ✅", msg)
def _bad(msg): print("[assets] ❌", msg)

VALID_IMG = {".png",".jpg",".jpeg"}

def check_assets_dir(assets_dir: str) -> bool:
    p = Path(assets_dir)
    if not p.exists():
        _bad(f"assets directory not found: {assets_dir}")
        return False
    _ok(f"found assets dir: {assets_dir}")
    return True

def check_manifest(manifest_path: str) -> bool:
    p = Path(manifest_path)
    if not p.exists():
        _warn(f"manifest not found (optional): {manifest_path}")
        return True
    try:
        data = json.loads(p.read_text())
        if not isinstance(data, dict):
            _bad("manifest JSON should be an object at top-level")
            return False
        # minimal sanity checks
        if "title" not in data:
            _warn("manifest: 'title' missing")
        if "pages" not in data or not isinstance(data["pages"], list):
            _warn("manifest: 'pages' missing or not a list")
        _ok("manifest parsed")
        return True
    except Exception as e:
        _bad(f"manifest parse error: {e}")
        return False

def check_images(assets_dir: str) -> bool:
    ok = True
    for p in Path(assets_dir).rglob("*"):
        if p.suffix.lower() in VALID_IMG:
            kind = imghdr.what(p)
            if kind not in ("png","jpeg"):
                _warn(f"suspect image encoding: {p.name} -> {kind}")
            if p.stat().st_size == 0:
                _bad(f"empty image: {p}")
                ok = False
            else:
                _ok(f"image OK: {p.name} ({p.stat().st_size//1024} KB)")
    return ok

def _cairosvg_exists():
    try:
        import cairosvg  # type: ignore
        return True
    except Exception:
        return False

def check_svgs(assets_dir: str) -> bool:
    ok = True
    if not _cairosvg_exists():
        _warn("cairosvg not installed; skipping SVG rasterization test")
        return ok
    import cairosvg  # type: ignore
    tmp = Path("output/.svg_check"); tmp.mkdir(parents=True, exist_ok=True)
    for p in Path(assets_dir).rglob("*.svg"):
        out_png = tmp / (p.stem + ".png")
        try:
            cairosvg.svg2png(url=str(p), write_to=str(out_png))
            _ok(f"svg rasterized: {p.name}")
        except Exception as e:
            _bad(f"svg failed to rasterize: {p} -> {e}")
            ok = False
    return ok
