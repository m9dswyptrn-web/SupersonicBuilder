#!/usr/bin/env python3
import sys, os, re, datetime, json
VER_FILE = "version.txt"
def read_ver():
    if not os.path.exists(VER_FILE): return (1,0,0)
    t = open(VER_FILE,"r").read().strip()
    try: major,minor,patch = map(int, t.split(".")); return (major,minor,patch)
    except: return (1,0,0)
def write_ver(v):
    open(VER_FILE,"w").write(".".join(map(str,v)))
def bump():
    major,minor,patch = read_ver()
    patch += 1
    write_ver((major,minor,patch))
    print(f"Bumped version → {major}.{minor}.{patch}")
def stamp():
    v = ".".join(map(str, read_ver()))
    print(f"Stamping build with version {v} @ {datetime.datetime.now().isoformat(timespec='minutes')}")
if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="bump": bump()
    else: stamp()
