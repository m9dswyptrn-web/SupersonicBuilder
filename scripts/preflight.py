#!/usr/bin/env python3
import os, sys

required_dirs = ["assets", "config"]
missing = [d for d in required_dirs if not os.path.isdir(d)]
if missing:
    print("⚠️ Missing directories:", ", ".join(missing))
    sys.exit(1)

yaml_files = [f for f in os.listdir("config") if f.endswith(".yaml")]
if not yaml_files:
    print("⚠️ No .yaml files found in config directory")
    sys.exit(1)

print("✅ Preflight check passed — assets and config look good!")
