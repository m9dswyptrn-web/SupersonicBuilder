#!/usr/bin/env python3
import sys, os, importlib.util

REQUIRED = [
    "reportlab",  # PDF (ReportLab)
    "PIL",        # Pillow
    "yaml",       # PyYAML
    "pypdf"       # PDF post ops
]

def have(mod):
    return importlib.util.find_spec(mod) is not None

def main():
    ok = True
    print("== Checking Python dependencies ==")
    for m in REQUIRED:
        if not have(m):
            print(f"[x] missing: {m}")
            ok = False
        else:
            print(f"[✓] {m}")
    print("\n== Checking key files ==")
    for p in ["outline.yml", "scripts/builder.py"]:
        if not os.path.exists(p):
            print(f"[x] missing file: {p}"); ok = False
        else:
            print(f"[✓] {p}")
    print("\n== Result ==")
    if ok:
        print("[OK] Environment looks good.")
        sys.exit(0)
    else:
        print("[WARN] Fix issues above then re-run.")
        sys.exit(1)

if __name__ == "__main__":
    main()
