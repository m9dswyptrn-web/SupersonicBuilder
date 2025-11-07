
#!/usr/bin/env python3
import re, sys, subprocess
from pathlib import Path

ROOT = Path(".")
MK = ROOT / "Makefile"
SNIPPET = Path("docs/Makefile_SNIPPET.txt").read_text(encoding="utf-8")

def ensure_pillow():
    try:
        import PIL  # noqa
    except Exception:
        print("📦 Installing Pillow (PIL)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        except Exception as e:
            print("⚠️ Could not install Pillow automatically:", e)

def patch_makefile():
    if not MK.exists():
        print("❌ Makefile not found in project root.")
        return 2
    mk = MK.read_text(encoding="utf-8")
    if "OPTIMIZER PATCH v2.1" in mk:
        print("✅ Optimizer already patched into Makefile.")
        return 0
    # Append at end
    mk = mk.rstrip() + "\n\n" + SNIPPET
    MK.write_text(mk, encoding="utf-8")
    print("✅ Appended optimizer targets to Makefile.")
    return 0

def main():
    ensure_pillow()
    rc = patch_makefile()
    if rc==0:
        print("\nNext: run\n  make release-all\n")
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
