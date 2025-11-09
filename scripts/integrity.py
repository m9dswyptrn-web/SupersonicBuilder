#!/usr/bin/env python3
"""
Computes SHA256 hashes for artifacts and signs them with cosign if available.
"""
import hashlib, subprocess, os
from pathlib import Path

ARTIFACTS = list(Path(".").glob("*.zip")) + list(Path(".").glob("*.tar.gz"))
SUMFILE = Path("SHA256SUMS.txt")

def sha256sum(fname):
    h = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def write_sums():
    lines = []
    for f in ARTIFACTS:
        digest = sha256sum(f)
        lines.append(f"{digest}  {f.name}")
    SUMFILE.write_text("\n".join(lines))
    print(f"[OK] Checksums written to {SUMFILE}")

def cosign_sign():
    key = os.getenv("SUP_SIGN_KEY", "cosign.key")
    if not Path(key).exists():
        print("[skip] No cosign key found; skipping signing.")
        return
    for f in ARTIFACTS + [SUMFILE]:
        try:
            subprocess.run(["cosign", "sign-blob", "--key", key, str(f)], check=False)
        except Exception as e:
            print(f"[warn] cosign sign failed for {f}: {e}")

if __name__ == "__main__":
    write_sums()
    cosign_sign()
