#!/usr/bin/env python3
# ids_watch.py — Re-run ids-flow when CAN logs change
# Usage:
#   python tools/can/ids_watch.py --csv out/can_log.csv --jsonl out/teensy_raw.jsonl
# Requires: watchdog  (pip install watchdog)
import argparse, time, subprocess, sys
from pathlib import Path

def run_ids_flow(csv, jsonl):
    cmd = None
    if csv and Path(csv).exists():
        cmd = ["make", "ids-flow", f"IDS_LOG={csv}"]
    elif jsonl and Path(jsonl).exists():
        cmd = ["make", "ids-flow", f"IDS_JSONL={jsonl}"]
    if cmd:
        print("[*] Running:", " ".join(cmd))
        subprocess.call(cmd)

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
            if event.is_directory:
                return
            p = Path(event.src_path)
            if p.name in (Path(A.csv).name, Path(A.jsonl).name):
                run_ids_flow(A.csv, A.jsonl)

    paths = set([str(Path(A.csv).parent), str(Path(A.jsonl).parent)])
    obs = Observer()
    handler = Handler()
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
