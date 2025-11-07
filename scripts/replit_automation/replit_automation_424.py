#!/usr/bin/env python3
"""
supervisor.py — minimal cross-platform restarter for your app.

Usage:
  python supervisor.py -- python scripts/run_offline_llm.py
  # or specify a module:
  python supervisor.py -m scripts.run_offline_llm
"""
import argparse, os, sys, time, subprocess, threading, queue, shlex, signal

def _reader(stream, q, name):
    for line in iter(stream.readline, b''):
        q.put((name, line.decode(errors='replace')))
    stream.close()

def run_once(cmd, env):
    if isinstance(cmd, list):
        popen_cmd = cmd
    else:
        popen_cmd = shlex.split(cmd)
    proc = subprocess.Popen(
        popen_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    q = queue.Queue()
    t1 = threading.Thread(target=_reader, args=(proc.stdout, q, "OUT"), daemon=True)
    t2 = threading.Thread(target=_reader, args=(proc.stderr, q, "ERR"), daemon=True)
    t1.start(); t2.start()
    return proc, q

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--debounce", type=float, default=1.5, help="minimum seconds between restarts")
    ap.add_argument("-m", "--module", help="run as python -m <module>")
    ap.add_argument("sep", nargs="?", help="-- separator", default=None)
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="command after -- (if not using -m)")
    args = ap.parse_args()

    if args.module and args.cmd:
        print("Use either -m or -- <cmd>, not both.", file=sys.stderr)
        sys.exit(2)

    if args.module:
        child_cmd = [sys.executable, "-u", "-m", args.module]
    else:
        if not args.cmd:
            # default to your runner
            child_cmd = [sys.executable, "-u", "scripts/run_offline_llm.py"]
        else:
            # strip leading '--' if present
            child_cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd

    env = os.environ.copy()
    print(f"[supervisor] starting: {' '.join(child_cmd)}")
    last_start = 0.0
    stop_requested = False
    kill_on_second_sigint = [False]

    def sigint_handler(signum, frame):
        if kill_on_second_sigint[0]:
            print("[supervisor] force kill requested")
            os._exit(130)
        kill_on_second_sigint[0] = True
        print("[supervisor] Ctrl-C received — stopping child gracefully… (press again to force)")
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, sigint_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, sigint_handler)

    while True:
        if stop_requested:
            print("[supervisor] exiting loop")
            sys.exit(0)

        # debounce to avoid rapid restart storms
        now = time.time()
        if now - last_start < args.debounce:
            time.sleep(args.debounce - (now - last_start))

        last_start = time.time()
        proc, q = run_once(child_cmd, env)

        # print child output with prefixes
        exit_code = None
        while exit_code is None:
            try:
                src, line = q.get(timeout=0.2)
                prefix = "│"
                if src == "OUT":
                    sys.stdout.write(f"[child]{prefix} {line}")
                    sys.stdout.flush()
                else:
                    sys.stderr.write(f"[child!]{prefix} {line}")
                    sys.stderr.flush()
            except queue.Empty:
                pass
            exit_code = proc.poll()

        # drain remaining
        while True:
            try:
                src, line = q.get_nowait()
                prefix = "│"
                if src == "OUT":
                    sys.stdout.write(f"[child]{prefix} {line}")
                else:
                    sys.stderr.write(f"[child!]{prefix} {line}")
            except queue.Empty:
                break

        if stop_requested:
            print(f"[supervisor] child exited ({exit_code}); stop requested → done.")
            sys.exit(exit_code if exit_code is not None else 0)

        # Child exited on its own: restart.
        # This includes your /api/reload → os._exit(0) case.
        if exit_code == 0:
            print("[supervisor] child exited cleanly (code 0) → restarting by policy")
        else:
            print(f"[supervisor] child crashed (code {exit_code}) → restarting after debounce")
        # loop continues to restart

if __name__ == "__main__":
    main()