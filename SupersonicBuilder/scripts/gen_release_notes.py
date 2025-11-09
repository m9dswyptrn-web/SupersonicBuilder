#!/usr/bin/env python3
import os, glob, hashlib, argparse

def sha256sum(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def generate_notes(dist_dir):
    lines = ["# 🚀 SonicBuilder Auto‑Generated Release Notes", ""]
    for f in sorted(glob.glob(os.path.join(dist_dir, "*.pdf"))):
        fn = os.path.basename(f)
        h = sha256sum(f)
        lines.append(f"- **[{fn}](./{fn})**  \\`SHA256: {h}\`")
    return "\n".join(lines)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--out", default="dist/RELEASE_NOTES.md")
    a = ap.parse_args()
    txt = generate_notes(a.dist)
    with open(a.out, "w") as f:
        f.write(txt)
    print(f"[ok] Wrote release notes -> {a.out}")
