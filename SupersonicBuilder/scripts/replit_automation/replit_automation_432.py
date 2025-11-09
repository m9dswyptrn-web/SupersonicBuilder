#!/usr/bin/env python3
"""
supervisor.py — minimal cross-platform restarter for your app with optional file watching.

Usage examples:
  # Default: supervise your runner, restart when the child exits (e.g., via /api/reload)
  python supervisor.py

  # Run explicit command:
  python supervisor.py -- python scripts/run_offline_llm.py

  # Run module:
  python supervisor.py -m scripts.run_offline_llm

  # Watch the repo for changes and restart on edit:
  python supervisor.py --watch . -- python scripts/run_offline_llm.py
"""

import argparse, os, sys, time, subprocess, threading, queue, shlex, signal
from pathlib import Path
from fnmatch import fnmatch

# ---------------- Logging helpers ----------------

def _reader(stream, q, name):
    for line in iter(stream.readline, b''):
        q.put((name, line.decode(errors='replace')))
    stream.close()

def _log_child(q):
    try:
        src, line = q.get(timeout=0.2)
        prefix = "│"
        if src == "OUT":
            sys.stdout.write(f"[child]{prefix} {line}")
            sys.stdout.flush()
        else:
            sys.stderr.write(f"[child!]{prefix} {line}")
            sys.stderr.flush()
        return True
    except queue.Empty:
        return False

# ---------------- File watching (no deps) ----------------

DEFAULT_INCLUDE = ["**/*.py", ".env"]
DEFAULT_EXCLUDE = [".git/**", "**/__pycache__/**", ".supersonic_cache/**"]

def _is_hidden_path(p: Path) -> bool:
    # Quick skip (platform agnostic)
    parts = p.parts
    return any(part.startswith('.') and part not in ('.', '..') for part in parts)

def _collect_files(roots, includes, excludes):
    """Yield files under roots that match includes and NOT excludes."""
    seen = set()
    for root in roots:
        root = Path(root).resolve()
        if not root.exists():
            continue
        if root.is_file():
            cands = [root]
        else:
            # rglob with broad pattern; we'll filter by includes/excludes
            cands = root.rglob("*")
        for p in cands:
            try:
                if p.is_dir():
                    continue
                rp = p.resolve()
                if rp in seen:
                    continue
                rel = rp.as_posix()
                # includes
                if not any(fnmatch(rel, pat) for pat in includes):
                    continue
                # excludes
                if any(fnmatch(rel, pat) for pat in excludes):
                    continue
                seen.add(rp)
                yield rp
            except Exception:
                continue

def _snapshot(roots, includes, excludes):
    """Return dict[path->(size, mtime_ns)] for watched files."""
    snap = {}
    for p in _collect_files(roots, includes, excludes):
        try:
            st = p.stat()
            snap[p] = (st.st_size, getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        except FileNotFoundError:
            # file deleted between rglob and stat
            continue
        except Exception:
            continue
    return snap

def _diff(prev, cur):
    """Return True if changed."""
    if len(prev) != len(cur):
        return True
    # Check mtimes/sizes quickly
    for p, meta in cur.items():
        if p not in prev or prev[p] != meta:
            return True
    return False

# ---------------- Child process ----------------

def _spawn(cmd, env):
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

# ---------------- Main loop ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--debounce", type=float, default=1.5, help="minimum seconds between restarts")
    ap.add_argument("-m", "--module", help="run as python -m <module>")
    ap.add_argument("--poll", type=float, default=0.5, help="file watch poll interval (sec)")
    ap.add_argument("--watch", action="append", default=[], help="path(s) to watch (files or dirs). Repeatable.")
    ap.add_argument("--include", action="append", default=[], help="glob(s) to include (default: **/*.py, .env)")
    ap.add_argument("--exclude", action="append", default=[], help="glob(s) to exclude (default: .git/**, __pycache__/**, .supersonic_cache/**)")
    ap.add_argument("sep", nargs="?", help="-- separator", default=None)
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="command after -- (if not using -m)")
    args = ap.parse_args()

    # Build child command
    if args.module and args.cmd:
        print("Use either -m or -- <cmd>, not both.", file=sys.stderr)
        sys.exit(2)
    if args.module:
        child_cmd = [sys.executable, "-u", "-m", args.module]
    else:
        if not args.cmd:
            # default runner
            child_cmd = [sys.executable, "-u", "scripts/run_offline_llm.py"]
        else:
            child_cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd

    # Watch configuration
    watch_roots = args.watch or []
    includes = args.include or DEFAULT_INCLUDE
    excludes = args.exclude or DEFAULT_EXCLUDE
    do_watch = len(watch_roots) > 0

    # Normalize patterns to POSIX-like strings
    includes = [p if "**" in p or "*" in p else (p + "/**" if Path(p).is_dir() else p) for p in includes]

    env = os.environ.copy()
    print(f"[supervisor] starting: {' '.join(child_cmd)}")
    if do_watch:
        print(f"[supervisor] watch roots: {', '.join(str(Path(r).resolve()) for r in watch_roots)}")
        print(f"[supervisor] include: {includes}")
        print(f"[supervisor] exclude: {excludes}")
        print(f"[supervisor] poll: {args.poll:.2f}s")

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

    # Initial snapshot for watcher
    prev_snap = _snapshot(watch_roots, includes, excludes) if do_watch else {}

    while True:
        if stop_requested:
            print("[supervisor] exiting loop")
            sys.exit(0)

        # debounce restarts
        now = time.time()
        if now - last_start < args.debounce:
            time.sleep(args.debounce - (now - last_start))

        last_start = time.time()
        proc, q = _spawn(child_cmd, env)

        exit_code = None
        last_watch_check = 0.0

        while exit_code is None and not stop_requested:
            # Stream child logs
            _ = _log_child(q)

            # Poll for file changes
            if do_watch:
                t = time.time()
                if t - last_watch_check >= args.poll:
                    last_watch_check = t
                    cur_snap = _snapshot(watch_roots, includes, excludes)
                    if _diff(prev_snap, cur_snap):
                        print("[supervisor] change detected → restarting child")
                        try:
                            proc.terminate()
                            try:
                                proc.wait(timeout=2.0)
                            except subprocess.TimeoutExpired:
                                proc.kill()
                        except Exception:
                            pass
                        prev_snap = cur_snap
                        break  # leave loop to restart

            # Check child exit
            exit_code = proc.poll()

        # Drain remaining logs
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
            print(f"[supervisor] child exited; stop requested → done.")
            sys.exit(exit_code if exit_code is not None else 0)

        # If we broke due to change, loop continues (restart).
        if do_watch and (exit_code is None):
            continue

        # Child exited on its own → restart by policy
        if exit_code == 0:
            print("[supervisor] child exited cleanly (code 0) → restarting by policy")
        else:
            print(f"[supervisor] child crashed (code {exit_code}) → restarting after debounce")
        # loop continues

if __name__ == "__main__":
    main()