#!/usr/bin/env python3
"""
load_env.py - tiny .env loader
- Loads key=value pairs from a `.env` file in the current working directory.
- If `.env` is missing but `ENV.example` exists, it will copy ENV.example -> .env (first run bootstrap).
- Exposes values via os.environ.
- Quiet mode with QUIET=1.

Usage:
    import load_env  # place at the top of main.py / app entrypoint
"""
from __future__ import annotations

import os, sys, shutil
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(".").resolve()
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / "ENV.example"

def _maybe_bootstrap_env() -> bool:
    """Create .env from ENV.example if .env doesn't exist. Returns True if created."""
    if not ENV_PATH.exists() and EXAMPLE_PATH.exists():
        try:
            shutil.copy2(EXAMPLE_PATH, ENV_PATH)
            print("[load_env] .env was missing - created from ENV.example")
            return True
        except Exception as e:
            print(f"[load_env] WARN: could not create .env from ENV.example: {e}", file=sys.stderr)
    return False

def _parse_line(line: str) -> Tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Support KEY="value with spaces", KEY='value', KEY=value
    if "=" not in line:
        return None
    key, val = line.split("=", 1)
    key = key.strip()
    val = val.strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return key, val

def _load_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    try:
        with path.open("r", encoding="utf-8") as f:
            for ln, raw in enumerate(f, 1):
                parsed = _parse_line(raw)
                if not parsed:
                    continue
                k, v = parsed
                env[k] = v
    except FileNotFoundError:
        pass
    return env

def _apply_env(env: Dict[str, str]):
    for k, v in env.items():
        if k not in os.environ:
            os.environ[k] = v

def _print_summary(env: Dict[str, str]):
    if os.environ.get("QUIET", "0") == "1":
        return
    if not env:
        print("[load_env] No .env variables loaded")
        return
    redacted_keys = {"GH_TOKEN", "GITHUB_TOKEN", "OPENAI_API_KEY", "SUPABASE_KEY", "DATABASE_URL", "JWT_SECRET"}
    def fmt(k, v):
        if k in redacted_keys:
            return f"{k}=***"
        if len(v) > 80:
            return f"{k}={v[:77]}..."
        return f"{k}={v}"
    print("[load_env] Loaded environment variables:")
    for k in sorted(env.keys()):
        print("  ", fmt(k, env[k]))

# ---- run on import ----
created = _maybe_bootstrap_env()
env = _load_env(ENV_PATH)
_apply_env(env)
if created and "SAFE_REMOTE" in env:
    # Convenience: if SAFE_REMOTE present, set GIT_REMOTE_URL for scripts that rely on it
    os.environ.setdefault("GIT_REMOTE_URL", env.get("SAFE_REMOTE", ""))
_print_summary(env)
