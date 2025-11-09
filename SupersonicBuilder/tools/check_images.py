
#!/usr/bin/env python3
# tools/check_images.py — preflight scanner to report missing/unused images.
import sys, json, yaml, os
from pathlib import Path

ASSETS = Path("assets")

def list_images():
    imgs = []
    for p in ASSETS.rglob("*"):
        if p.suffix.lower() in {".png",".jpg",".jpeg",".webp",".svg"}:
            imgs.append(p.relative_to(ASSETS).as_posix())
    return set(imgs)

def scan_yaml_for_images():
    refs = set()
    cfg = Path("config")
    for y in cfg.glob("**/*.y*ml"):
        try:
            data = yaml.safe_load(y.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        # naive search for 'image' keys
        def walk(obj):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    if isinstance(k, str) and k.lower() in {"image","img","icon","diagram"} and isinstance(v, str):
                        refs.add(v)
                    walk(v)
            elif isinstance(obj, list):
                for it in obj:
                    walk(it)
        walk(data)
    return refs

def main():
    imgs = list_images()
    refs = scan_yaml_for_images()
    missing = sorted([r for r in refs if r not in imgs])
    unused  = sorted([i for i in imgs if i not in refs])
    print(f"Found {len(imgs)} asset image(s); {len(refs)} referenced.")
    if missing:
        print("Missing asset files (referenced but not found in assets/):")
        for m in missing:
            print("  -", m)
        print("TIP: Put files under assets/<name> exactly matching the YAML reference.")
    else:
        print("No missing images referenced in YAML. ✅")
    if unused:
        print("\nImages in assets/ not referenced by YAML (optional cleanup):")
        for u in unused[:50]:
            print("  -", u)
        if len(unused) > 50:
            print(f"  ... and {len(unused)-50} more")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
