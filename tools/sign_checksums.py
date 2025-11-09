#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, subprocess, sys
from pathlib import Path
import tempfile

def run(cmd, **kw):
    print("$", " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)

def main():
    ap = argparse.ArgumentParser(description="Import GPG key from env and sign SHA256SUMS.txt")
    ap.add_argument("--input", default="SHA256SUMS.txt")
    ap.add_argument("--output", default="SHA256SUMS.txt.asc")
    ap.add_argument("--key-env", default="GPG_PRIVATE_KEY")
    ap.add_argument("--pass-env", default="GPG_PASSPHRASE")
    args = ap.parse_args()

    key_ascii = os.getenv(args.key_env)
    if not key_ascii:
        print(f"Missing env {args.key_env}", file=sys.stderr); sys.exit(44)
    passphrase = os.getenv(args.pass_env, "")

    gnupg = Path(".gnupg-ci")
    gnupg.mkdir(exist_ok=True)
    os.environ["GNUPGHOME"] = str(gnupg)

    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write(key_ascii)
        keyfile = tf.name
    try:
        run(["gpg", "--batch", "--yes", "--import", keyfile])
    finally:
        Path(keyfile).unlink(missing_ok=True)

    keyid = os.getenv("GPG_KEYID")
    base_cmd = ["gpg", "--batch", "--yes", "--armor", "--detach-sign", "--pinentry-mode", "loopback"]
    if passphrase:
        base_cmd += ["--passphrase", passphrase]
    if keyid:
        base_cmd += ["-u", keyid]

    inp = Path(args.input)
    if not inp.exists():
        print(f"{args.input} not found", file=sys.stderr); sys.exit(45)
    out = Path(args.output)
    run(base_cmd + ["-o", str(out), str(inp)])
    print(f"✅ Wrote {out}")

if __name__ == "__main__":
    main()
