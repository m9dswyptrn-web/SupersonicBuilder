#!/usr/bin/env python3
"""
Generate badges/version.json for shields.io endpoint.
"""
import json, os, subprocess
from pathlib import Path

def get_version():
    vf = Path("VERSION")
    if vf.exists():
        txt = vf.read_text(encoding="utf-8").strip()
        if txt: return txt
    ref = os.getenv("GITHUB_REF") or ""
    name = os.getenv("GITHUB_REF_NAME") or ""
    if ref.startswith("refs/tags/"):
        return ref.split("/", 2)[-1]
    if name and os.getenv("GITHUB_REF_TYPE") == "tag":
        return name
    try:
        out = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
        return out.decode().strip()
    except Exception:
        return "v0.0.0"

def to_color(ver: str) -> str:
    if ver.startswith("v0."): return "lightgrey"
    if "-" in ver or "rc" in ver or "beta" in ver: return "orange"
    return "brightgreen"

ver = get_version()
badge = {"schemaVersion":1, "label":"version", "message":ver, "color":to_color(ver)}
Path("badges").mkdir(exist_ok=True, parents=True)
Path("badges/version.json").write_text(json.dumps(badge), encoding="utf-8")
print("Wrote badges/version.json ->", badge)
