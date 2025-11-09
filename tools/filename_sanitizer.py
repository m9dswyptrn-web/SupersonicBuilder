
#!/usr/bin/env python3
import argparse, re
from pathlib import Path

def sanitize(name: str) -> str:
    # Remove spaces and common duplicate suffixes like (1), (2)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"\(\d+\)", "", name)
    name = re.sub(r"__+", "_", name)
    return name

def walk(root: Path):
    renamed = 0
    for p in sorted(root.rglob("*"), key=lambda x: -len(x.name)):
        if not p.is_file(): continue
        new = p.with_name(sanitize(p.name))
        if new.name != p.name:
            if new.exists():
                # Skip if target exists
                print(f"⚠️  Skip rename (exists): {new.name}")
                continue
            p.rename(new)
            print(f"✏️  Renamed: {p.name} -> {new.name}")
            renamed += 1
    print(f"\nRenamed {renamed} file(s).")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="assets")
    args = ap.parse_args()
    return walk(Path(args.root))

if __name__ == "__main__":
    raise SystemExit(main())
