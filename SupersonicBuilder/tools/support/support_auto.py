#!/usr/bin/env python3
# support_auto.py — watch CAN logs and run ids-flow + support-bundle on changes
# Usage:
#   python tools/support/support_auto.py --csv out/can_log.csv --jsonl out/teensy_raw.jsonl
# Requires: watchdog (pip install watchdog)
import argparse, time, subprocess, sys
from pathlib import Path

def run(cmd):
    print("[*] Running:", " ".join(cmd), flush=True)
    return subprocess.call(cmd)

def trigger(csv, jsonl):
    # Try CSV first, then JSONL
    if csv and Path(csv).exists():
        run(["make","ids-flow",f"IDS_LOG={csv}"])
    elif jsonl and Path(jsonl).exists():
        run(["make","ids-flow",f"IDS_JSONL={jsonl}"])
    else:
        print("[!] No CAN logs found; skipping ids-flow.")
        return
    run(["make","support-bundle"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="out/can_log.csv")
    ap.add_argument("--jsonl", default="out/teensy_raw.jsonl")
    A = ap.parse_args()

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Install watchdog: pip install watchdog")
        sys.exit(2)

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory: return
            p = Path(event.src_path)
            if p.name in (Path(A.csv).name, Path(A.jsonl).name):
                print(f"[*] Change detected: {p}")
                trigger(A.csv, A.jsonl)

    # Initial run once (optional)
    print("[*] Initial run...")
    trigger(A.csv, A.jsonl)

    # Watch for changes
    paths = {str(Path(A.csv).parent), str(Path(A.jsonl).parent)}
    obs = Observer(); handler = Handler()
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)
        obs.schedule(handler, p, recursive=False)
    obs.start()
    print("[*] Watching for changes in:", ", ".join(paths))
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    main()
