#!/usr/bin/env python3
import re, sys, pathlib, argparse, subprocess

MK = pathlib.Path("Makefile").read_text(encoding="utf-8")

def read_version():
    # look for VERSION=... (with or without spaces)
    m = re.search(r'^\s*VERSION\s*[:?+]?=\s*([vV]?\d+\.\d+\.\d+)\s*$', MK, re.M)
    if not m:
        print("ERROR: VERSION not found in Makefile")
        sys.exit(2)
    v = m.group(1)
    if not v.startswith("v"): v = "v"+v
    return v

def write_version(newv):
    txt = re.sub(r'(^\s*VERSION\s*[:?+]?=\s*)([vV]?\d+\.\d+\.\d+)(\s*$)',
                 lambda m: m.group(1)+newv+m.group(3), MK, flags=re.M)
    pathlib.Path("Makefile").write_text(txt, encoding="utf-8")

def bump(v, kind):
    major, minor, patch = map(int, v.lstrip("v").split("."))
    if kind=="patch": patch+=1
    elif kind=="minor": minor, patch = minor+1, 0
    elif kind=="major": major, minor, patch = major+1, 0, 0
    else: raise ValueError("bad kind")
    return f"v{major}.{minor}.{patch}"

ap = argparse.ArgumentParser()
ap.add_argument("--level", choices=["patch","minor","major"], help="bump type")
ap.add_argument("--set", dest="setver", help="set exact version, e.g. v1.2.3")
args = ap.parse_args()

cur = read_version()

if args.setver:
    newv = args.setver if args.setver.startswith("v") else "v"+args.setver
elif args.level:
    newv = bump(cur, args.level)
else:
    # default patch bump
    newv = bump(cur, "patch")

if newv == cur:
    print(f"Version unchanged: {cur}")
else:
    write_version(newv)
    print(f"Bumped {cur} → {newv}")
