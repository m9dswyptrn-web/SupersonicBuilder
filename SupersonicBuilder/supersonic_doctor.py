#!/usr/bin/env python3
"""
supersonic_doctor.py
One-shot health report (no installs). Safe for Replit, Codespaces, or local.

What it checks:
  - Python/runtime basics
  - .env loading (via load_env if available)
  - Dependency presence (fastapi, flask, uvicorn, requests)
  - Endpoint health: /api/ping, /api/ready, /api/status, POST /api/sync
  - Git: repo present, branch, remote origin, pending changes

Usage:
  python3 supersonic_doctor.py
"""
from __future__ import annotations
import os, sys, subprocess, json, platform
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")

def info(title, value):
    print(f"[INFO] {title}: {value}")

def warn(title, value):
    print(f"[WARN] {title}: {value}")

def ok(title, value="OK"):
    print(f"[OK] {title}: {value}")

def err(title, value):
    print(f"[ERROR] {title}: {value}")

def have(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False

def sh(cmd: str, check=False) -> tuple[int, str]:
    p = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and p.returncode != 0:
        raise RuntimeError(f"$ {cmd}\n{p.stdout}")
    return p.returncode, p.stdout.strip()

def curl_json(method: str, url: str) -> tuple[int, str]:
    cmd = f"curl -s -X {method} {url}"
    return sh(cmd, check=False)

def req_json(method: str, url: str) -> tuple[int, str]:
    try:
        import requests
        func = getattr(requests, method.lower())
        r = func(url, timeout=5)
        return r.status_code, r.text
    except Exception as e:
        return -1, str(e)

def get_json(method: str, url: str) -> tuple[int, str]:
    if have("requests"):
        return req_json(method, url)
    return curl_json(method, url)

def check_endpoints(base: str):
    print("\n== Endpoint Checks ==")
    codes = {}
    for meth, path in [("GET","/api/ping"), ("GET","/api/ready"), ("GET","/api/status"), ("POST","/api/sync")]:
        url = base + path
        code, body = get_json(meth, url)
        codes[path] = code
        label = f"{meth} {path}"
        if code in (200, 204):
            ok(label, f"HTTP {code}")
        else:
            warn(label, f"HTTP {code} body={body[:200]}")
    return codes

def check_git():
    print("\n== Git Checks ==")
    rc, inside = sh("git rev-parse --is-inside-work-tree")
    if rc != 0 or "true" not in inside:
        warn("git repo", "not inside a repository")
        return {"inside": False}
    rc, branch = sh("git symbolic-ref --short HEAD || echo '(detached)'")
    rc, origin = sh("git remote get-url origin || echo '(none)'")
    rc, status = sh("git status --porcelain")
    ok("git repo", "inside")
    info("branch", branch.strip())
    info("origin", origin.strip())
    info("pending changes", "yes" if status else "no")
    if status:
        print(status)
    return {"inside": True, "branch": branch.strip(), "origin": origin.strip(), "dirty": bool(status)}

def main():
    print("== Supersonic Doctor Report ==")
    info("time (UTC)", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))
    info("cwd", str(ROOT))
    info("python", sys.version.split()[0])
    info("platform", platform.platform())

    # Env loading
    try:
        import load_env  # noqa: F401
        ok(".env loader", "loaded")
    except Exception as e:
        warn(".env loader", f"not loaded ({e})")

    # Dependencies (no install)
    print("\n== Dependency Presence (no install) ==")
    for mod in ("fastapi","flask","uvicorn","requests"):
        if have(mod):
            ok(f"module '{mod}'")
        else:
            warn(f"module '{mod}'", "missing")

    # Endpoints
    codes = check_endpoints(BASE_URL)

    # Git
    git = check_git()

    print("\n== Summary ==")
    summary = {
        "base_url": BASE_URL,
        "deps": {m: have(m) for m in ("fastapi","flask","uvicorn","requests")},
        "endpoints": codes,
        "git": git,
    }
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
