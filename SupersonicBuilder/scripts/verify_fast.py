
#!/usr/bin/env python3
"""
verify_fast.py — quick preflight + smoke build

What it does fast:
1) JSON sanity: manifest + annotations + themes (json.tool)
2) Python imports: reportlab, pypdf (and optional: cairosvg, pdfrw, watchdog)
3) Assets presence: basic checks for common files/dirs
4) Quick smoke build (optional): runs main_glue.py with ANNOTATION_MODE=photo-only
5) Open the produced PDF with pypdf (if installed)

Exit codes:
- 0 = OK
- 1/2+ = Issue detected
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

def sh(cmd, env=None):
    print(">", " ".join(cmd))
    return subprocess.call(cmd, env=env or os.environ.copy())

def check_json(path: Path) -> bool:
    if not path.exists():
        print(f"[json] ❌ missing: {path}")
        return False
    rc = sh([sys.executable, "-m", "json.tool", str(path)])
    if rc == 0:
        print(f"[json] ✅ valid: {path.name}")
        return True
    print(f"[json] ❌ invalid: {path.name}")
    return False

def try_import(name: str, required: bool) -> bool:
    try:
        __import__(name)
        print(f"[py] ✅ import ok: {name}")
        return True
    except Exception as e:
        if required:
            print(f"[py] ❌ import failed (required): {name} -> {e}")
        else:
            print(f"[py] ⚠ import failed (optional): {name} -> {e}")
        return not required

def check_assets(assets: Path) -> bool:
    ok = True
    if not assets.exists():
        print(f"[assets] ❌ missing dir: {assets}")
        return False
    # common expected files if following our packs
    for rel in [
        "pinout_44pin.svg",
        "rr2_gm2_primary.svg",
        "pinout_harness_closeup.jpg",
        "rr2_gm2_primary_photo.jpg",
        "dsp_amp_stack.svg",
        "grz_overlay.svg",
    ]:
        if not (assets/rel).exists():
            print(f"[assets] ⚠ missing (ok if not used yet): {rel}")
        else:
            print(f"[assets] ✅ found: {rel}")
    return ok

def pdf_openable(pdf: Path) -> bool:
    try:
        from pypdf import PdfReader
    except Exception:
        print("[pdf] ⚠ pypdf not installed; skipping open test")
        return True
    try:
        _ = PdfReader(str(pdf))
        print(f"[pdf] ✅ opened: {pdf.name}")
        return True
    except Exception as e:
        print(f"[pdf] ❌ not openable: {pdf.name} -> {e}")
        return False

def smoke_build(theme: str, assets: Path, output: Path, config: Path) -> bool:
    if not Path("scripts/main_glue.py").exists():
        print("[build] ⚠ scripts/main_glue.py not found; skipping smoke build")
        return True
    env = os.environ.copy()
    env["ANNOTATION_MODE"] = env.get("ANNOTATION_MODE","photo-only")
    rc = sh([sys.executable, "scripts/main_glue.py", "--theme", theme, "--assets", str(assets), "--output", str(output), "--config", str(config)], env=env)
    if rc != 0:
        print("[build] ❌ main_glue.py returned error")
        return False
    out_pdf = output / ("sonic_manual_light.pdf" if theme=="light" else "sonic_manual_dark.pdf")
    if not out_pdf.exists():
        print("[build] ❌ expected PDF not found:", out_pdf)
        return False
    return pdf_openable(out_pdf)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="assets")
    ap.add_argument("--output", default="output")
    ap.add_argument("--config", default="config/manual.manifest.json")
    ap.add_argument("--annotations", default="templates/annotations.sonic.json")
    ap.add_argument("--theme_json", default="templates/theme.sonic.json")
    ap.add_argument("--theme", default="dark", choices=["dark","light"])
    ap.add_argument("--skip_build", action="store_true")
    args = ap.parse_args()

    ok = True

    # 1) JSON sanity
    ok &= check_json(Path(args.config))
    if Path(args.annotations).exists():
        ok &= check_json(Path(args.annotations))
    if Path(args.theme_json).exists():
        ok &= check_json(Path(args.theme_json))

    # 2) Python imports
    ok &= try_import("reportlab", required=True)
    ok &= try_import("pypdf", required=False)
    ok &= try_import("cairosvg", required=False)
    ok &= try_import("pdfrw", required=False)
    ok &= try_import("watchdog", required=False)

    # 3) Assets presence
    ok &= check_assets(Path(args.assets))

    # 4/5) Smoke build + open
    if not args.skip_build:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        ok &= smoke_build(args.theme, Path(args.assets), Path(args.output), Path(args.config))

    if not ok:
        print("\n[verify_fast] ❌ Issues detected.")
        sys.exit(2)
    print("\n[verify_fast] ✅ All good.")
    sys.exit(0)

if __name__ == "__main__":
    main()
