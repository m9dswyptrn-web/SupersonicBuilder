#!/usr/bin/env python3
import json, os, subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER_FILE = ROOT / "supersonic_version.json"

def sh(cmd, cwd=None, check=True):
    try:
        out = subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT)
        return out.decode("utf-8","ignore")
    except subprocess.CalledProcessError as e:
        if check: raise
        return e.output.decode("utf-8","ignore")

def current_version():
    if VER_FILE.exists():
        try:
            data = json.loads(VER_FILE.read_text(encoding="utf-8"))
            v = data.get("version", "0.1.0")
            return v
        except Exception:
            return "0.1.0"
    return "0.1.0"

def parse_semver(v):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", v.strip())
    if not m: return (0,1,0)
    return tuple(map(int, m.groups()))

def bump(v, mode):
    M,m,p = parse_semver(v)
    if mode=="major": M+=1; m=0; p=0
    elif mode=="minor": m+=1; p=0
    else: p+=1
    return f"{M}.{m}.{p}"

def last_tag():
    out = sh(["git","describe","--tags","--abbrev=0"], check=False).strip()
    return out if out else ""

def commits_since(tag):
    if tag:
        rng = f"{tag}..HEAD"
        out = sh(["git","log",rng,"--pretty=%s"], check=False)
    else:
        out = sh(["git","log","--pretty=%s"], check=False)
    return [l.strip() for l in out.splitlines() if l.strip()]

def decide_bump(msgs):
    mode = "patch"
    for s in msgs:
        low = s.lower()
        if "breaking:" in low or "feat!: " in low or "feat!:" in low:
            return "major"
        if low.startswith("feat:"):
            mode = "minor"
        elif low.startswith("fix:") and mode!="minor":
            mode = "patch"
    return mode

def autocommit_and_tag(new_v, autopush=True):
    # write file
    VER_FILE.write_text(json.dumps({"version": new_v}, indent=2)+"\n", encoding="utf-8")
    # commit & tag
    try:
        sh(["git","add", str(VER_FILE)])
        sh(["git","commit","-m", f"chore: bump version to v{new_v} [autobot]"], check=False)
        sh(["git","tag", f"v{new_v}"], check=False)
        if autopush:
            sh(["git","push"], check=False)
            sh(["git","push","--tags"], check=False)
        print(f"[version] v{new_v} (autopush={'ON' if autopush else 'OFF'})")
    except Exception as e:
        print(f"[warn] tagging failed: {e}")

def main():
    base = current_version()
    tag = last_tag()
    msgs = commits_since(tag)
    mode = decide_bump(msgs) if msgs else "patch"
    new_v = bump(base, mode)
    autopush = os.getenv("SUP_AUTOPUSH","1") == "1"
    autocommit_and_tag(new_v, autopush=autopush)

if __name__=="__main__":
    main()
