import os, sys, shutil, importlib.util

def ok(label): print(f"✅ {label}")
def warn(label): print(f"⚠️  {label}")
def bad(label): print(f"❌ {label}")

root = os.getcwd()

# Basic folders
for d in ["assets","config","build"]:
    p = os.path.join(root,d)
    (ok if os.path.isdir(p) else warn)(f"folder: {d} {'OK' if os.path.isdir(p) else 'missing'}")

# Python deps (best-effort)
for mod in ["reportlab","svglib","tinycss2","cssselect2","PIL"]:
    found = importlib.util.find_spec(mod) is not None
    (ok if found else warn)(f"python module: {mod} {'OK' if found else 'not found'}")

# Key files
for f in ["main.py","serve_build.py","Makefile","VERSION"]:
    exists = os.path.exists(os.path.join(root,f))
    (ok if exists else warn)(f"file: {f} {'OK' if exists else 'missing'}")

print("\nPreflight done.")
