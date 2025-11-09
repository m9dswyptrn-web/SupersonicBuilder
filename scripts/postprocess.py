
import argparse, shutil, time
from pathlib import Path
import subprocess, sys

def timestamp():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def run(cmd):
    print("[post] >", " ".join(cmd))
    return subprocess.call(cmd)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="output")
    ap.add_argument("--basename", default="sonic_manual_dark.pdf")
    args = ap.parse_args()

    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    base = out / args.basename
    if not base.exists():
        print("[post] base PDF not found:", base)
        sys.exit(1)

    ts = timestamp()
    versioned = out / f"{base.stem}_{ts}.pdf"
    shutil.copy2(base, versioned)
    print("[post] versioned:", versioned.name)

    # Generate cards single (half-letter) then impose two-up PRO
    run([sys.executable, "scripts/cards_make.py", "--output", str(out)])
    run([sys.executable, "scripts/impose_two_up_pro.py", "--input", str(out / "field_cards_dark_single.pdf"), "--output", str(out / f"field_cards_dark_two_up_PRO_{ts}.pdf")])

if __name__ == "__main__":
    main()
