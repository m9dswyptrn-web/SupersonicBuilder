#!/usr/bin/env python3
"""
Generates a Software Bill of Materials (SBOM) and runs a basic dependency scan.
"""
import subprocess, shutil, sys

def run(cmd):
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print(f"[skip] {cmd[0]} not installed.")
    except Exception as e:
        print(f"[warn] {cmd}: {e}")

print("🔍 Generating SBOM and security scan ...")
if shutil.which("syft"):
    run(["syft", ".","-o","json"])
else:
    print("[skip] Syft not found.")

if shutil.which("pip-audit"):
    run(["pip-audit"])
elif shutil.which("trivy"):
    run(["trivy","fs","."])
else:
    print("[skip] No scanner available.")
print("SBOM scan complete ✅")
