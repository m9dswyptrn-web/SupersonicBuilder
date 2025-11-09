
# PATCH: add --post to call scripts/postprocess.py after successful build
import argparse, os, time, subprocess, sys
from pathlib import Path

def safe_run(cmd: list[str]) -> int:
    print("[build] >", " ".join(cmd))
    return subprocess.call(cmd)

def main():
    p = argparse.ArgumentParser(description="SonicBuilder build orchestrator (patched)")
    p.add_argument("--theme", default="dark", choices=["dark","light"])
    p.add_argument("--assets", default="assets")
    p.add_argument("--output", default="output")
    p.add_argument("--config", default="config/manual.manifest.json")
    p.add_argument("--post", action="store_true")
    args = p.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # delegate
    entry = "main.py" if Path("main.py").exists() else None
    if entry is None:
        print("main.py not found. Please wire your PDF generation entrypoint here.")
        sys.exit(1)

    rc = safe_run([sys.executable, entry, "--theme", args.theme, "--assets", args.assets, "--output", args.output, "--config", args.config])
    if rc != 0:
        sys.exit(rc)

    if args.post:
        if Path("scripts/postprocess.py").exists():
            safe_run([sys.executable, "scripts/postprocess.py", "--output", args.output, "--basename", "sonic_manual_dark.pdf"])
        else:
            print("[post] scripts/postprocess.py not found; skipping")

if __name__ == "__main__":
    main()
