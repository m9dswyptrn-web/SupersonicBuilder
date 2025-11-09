
import argparse, json, os, sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.assets_checks import check_assets_dir, check_images, check_svgs, check_manifest
from utils.pdf_checks import check_existing_pdfs, check_pdf_openable

def main():
    p = argparse.ArgumentParser(description="SonicBuilder preflight & validation")
    p.add_argument("--assets", default="assets")
    p.add_argument("--output", default="output")
    p.add_argument("--config", default="config/manual.manifest.json")
    args = p.parse_args()

    ok = True
    ok &= check_assets_dir(args.assets)
    ok &= check_manifest(args.config)
    ok &= check_images(args.assets)
    ok &= check_svgs(args.assets)
    # If there are already PDFs in output/, verify they open
    ok &= check_existing_pdfs(args.output, open_test=True)

    if not ok:
        print("\n[validate] ❌ Issues detected. See logs above.")
        sys.exit(2)
    print("\n[validate] ✅ All checks passed.")
    return 0

if __name__ == "__main__":
    main()
