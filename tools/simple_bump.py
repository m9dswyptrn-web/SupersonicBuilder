#!/usr/bin/env python3
import re, sys
from pathlib import Path

p = Path("VERSION")
v = p.read_text().strip() if p.exists() else "v0.1.0"
m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", v)
if not m:
    print(f"Bad VERSION format: {v}", file=sys.stderr)
    sys.exit(2)

maj, minor, patch = map(int, m.groups())
kind = (sys.argv[1] if len(sys.argv) > 1 else "patch").lower()

if kind == "major":
    maj, minor, patch = maj+1, 0, 0
elif kind == "minor":
    minor, patch = minor+1, 0
else:
    patch += 1

nv = f"v{maj}.{minor}.{patch}"
p.write_text(nv)
print(nv)
