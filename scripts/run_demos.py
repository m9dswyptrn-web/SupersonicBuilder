
#!/usr/bin/env python3
"""
scripts/run_demos.py
Build several permutations and bundle them to dist/ for QA.
Requires:
  - scripts/main_glue.py
  - scripts/postprocess.py
  - scripts/impose_two_up_pro.py (optional; if missing, standard post still runs)
Usage:
  python scripts/run_demos.py --assets assets --output output --config config/manual.manifest.json
"""
import os, sys, shutil, subprocess, datetime
from pathlib import Path

def sh(cmd, env=None):
    print(">", " ".join(cmd))
    return subprocess.call(cmd, env=env or os.environ.copy())

def ensure_dirs(out_dir, dist_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    Path(dist_dir).mkdir(parents=True, exist_ok=True)

def build_variant(theme, mode, assets, output, config):
    env = os.environ.copy()
    env["ANNOTATION_MODE"] = mode
    cmd = [sys.executable, "scripts/main_glue.py", "--theme", theme, "--assets", assets, "--output", output, "--config", config]
    rc = sh(cmd, env=env)
    if rc != 0:
        raise SystemExit(rc)

def post(output):
    if Path("scripts/postprocess.py").exists():
        sh([sys.executable, "scripts/postprocess.py", "--output", output, "--basename", "sonic_manual_dark.pdf"])
    # PRO two-up (if available)
    if Path("scripts/impose_two_up_pro.py").exists():
        sh([sys.executable, "scripts/impose_two_up_pro.py", "--input", str(Path(output)/"field_cards_dark_single.pdf"), "--output", str(Path(output)/"field_cards_dark_two_up_PRO.pdf")])

def bundle(output, dist_dir):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_root = Path(output)
    zip_name = Path(dist_dir)/f"DEMO_Bundle_{ts}"
    shutil.make_archive(str(zip_name), "zip", root_dir=str(bundle_root))
    print("[bundle] wrote", f"{zip_name}.zip")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="assets")
    ap.add_argument("--output", default="output")
    ap.add_argument("--config", default="config/manual.manifest.json")
    ap.add_argument("--dist", default="dist")
    args = ap.parse_args()

    ensure_dirs(args.output, args.dist)

    # Matrix of builds
    matrix = [
        ("dark",  "themed"),
        ("dark",  "photo-only"),
        ("light", "themed"),
        ("light", "photo-only"),
    ]

    for theme, mode in matrix:
        print(f"\n=== Building THEME={theme} MODE={mode} ===")
        os.environ["ANNOTATION_MODE"] = mode
        build_variant(theme, mode, args.assets, args.output, args.config)

    print("\n=== Post-process ===")
    post(args.output)

    print("\n=== Bundle artifacts ===")
    bundle(args.output, args.dist)

if __name__ == "__main__":
    main()
