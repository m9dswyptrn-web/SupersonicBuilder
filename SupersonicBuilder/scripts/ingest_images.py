#!/usr/bin/env python3
import argparse, os, shutil, csv, glob
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter-id", required=True)
    ap.add_argument("--target-dir", required=True)
    ap.add_argument("--pattern", default="*.jpg")
    ap.add_argument("--caption", default="")
    a = ap.parse_args()
    os.makedirs(a.target_dir, exist_ok=True)
    src_dir = "assets/images/import_drop_here"; os.makedirs(src_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src_dir, a.pattern)))
    if not files:
        print("[warn] No files matched", a.pattern, "in", src_dir); return
    manifest = "assets/images/manifest.csv"
    with open(manifest, "a", newline="") as f:
        w = csv.writer(f)
        for i, fpath in enumerate(files, start=1):
            base = os.path.basename(fpath); dst = os.path.join(a.target_dir, base)
            shutil.copy2(fpath, dst); w.writerow([dst, a.caption, a.chapter_id, i])
    print("[ok] Ingested", len(files), "files into", a.target_dir)
if __name__ == "__main__": main()
