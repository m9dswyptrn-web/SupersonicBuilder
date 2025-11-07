#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, os, sys
from pathlib import Path
from glob import glob

def human(n:int)->str:
    units=["B","KB","MB","GB","TB"]; i=0
    f=float(n)
    while f>=1024 and i<len(units)-1: f/=1024; i+=1
    return f"{f:.2f} {units[i]}"

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""): h.update(chunk)
    return h.hexdigest()

def expand_globs(lines:list[str])->list[Path]:
    inc, exc = [], []
    for raw in lines:
        s=raw.strip()
        if not s: continue
        (exc if s.startswith("!") else inc).append(s[1:] if s.startswith("!") else s)
    files=set()
    for p in inc:
        for m in glob(p, recursive=True):
            q=Path(m)
            if q.is_file(): files.add(q.resolve())
    ex=set()
    for p in exc:
        for m in glob(p, recursive=True):
            q=Path(m)
            if q.is_file(): ex.add(q.resolve())
    return sorted([p for p in files if p not in ex])

def main():
    ap=argparse.ArgumentParser(description="Budget-check artifacts + write SHA256SUMS.txt")
    ap.add_argument("--globs", required=True, help="newline-separated glob patterns; use ! for excludes")
    ap.add_argument("--max-per-mb", type=float, default=float(os.getenv("ART_MAX_PER_MB", "300")))
    ap.add_argument("--max-total-mb", type=float, default=float(os.getenv("ART_MAX_TOTAL_MB", "1200")))
    ap.add_argument("--out", default="SHA256SUMS.txt")
    args=ap.parse_args()

    patterns=[s for s in args.globs.splitlines()]
    files=expand_globs(patterns)
    if not files:
        print("No artifacts matched patterns; nothing to sign.")
        Path(args.out).write_text("", encoding="utf-8")
        return

    per_limit=int(args.max_per_mb*1024*1024)
    total_limit=int(args.max_total_mb*1024*1024)

    total=0
    lines=[]
    fail_reasons=[]
    for p in files:
        sz=p.stat().st_size; total+=sz
        if sz>per_limit:
            fail_reasons.append(f"{p} size {human(sz)} exceeds per-file limit {args.max_per_mb:.0f} MB")
        digest=sha256(p)
        rel=p.relative_to(Path.cwd())
        lines.append(f"{digest}  {rel.as_posix()}")

    if total>total_limit:
        fail_reasons.append(f"Total size {human(total)} exceeds total limit {args.max_total_mb:.0f} MB")

    Path(args.out).write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"Wrote {args.out} ({len(files)} files, total {human(total)})")

    if fail_reasons:
        print("Artifact budget FAILED:")
        for r in fail_reasons: print(" -", r)
        sys.exit(42)

if __name__=="__main__":
    main()
