#!/usr/bin/env python3
import os, csv, json, argparse, time, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from repo_url import resolve
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="Appendix/C_I2S_Integration")
    args = ap.parse_args()
    base = Path(args.root)
    pcb = base / "PCB_Photos"; taps = base / "Tap_Diagrams"
    pcb.mkdir(parents=True, exist_ok=True); taps.mkdir(parents=True, exist_ok=True)
    rows = []
    for kind, folder in [("pcb", pcb), ("tap", taps)]:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                rel = p.relative_to(base).as_posix()
                rows.append({"type": kind, "file": rel, "name": p.stem.replace("_", " "), "ext": p.suffix.lower(), "bytes": p.stat().st_size})
    idx = base / "03_Photo_Index.csv"
    with idx.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["type","file","name","ext","bytes"]); w.writeheader()
        for r in rows: w.writerow(r)
    meta = {"count": len(rows), "generated_at": int(time.time()), "base_url": resolve(None)}
    (base / "metadata.json").write_text(json.dumps(meta, indent=2))
    (base / "Auto_Notes.txt").write_text("Appendix C index regenerated.\n")
    print(f"Indexed {len(rows)} files into {idx}")
if __name__ == "__main__":
    main()
