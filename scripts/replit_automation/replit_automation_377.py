#!/usr/bin/env python3
# scripts/run_offline_llm.py
# Launches the local UI and auto-runs a benchmark once after first successful boot.

import os, sys, time, json, hashlib, subprocess
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("PORT", "7860"))
HOST = f"http://127.0.0.1:{PORT}"
CACHE_DIR = ROOT / ".supersonic_cache"
CACHE_DIR.mkdir(exist_ok=True)
BENCH_ONCE = CACHE_DIR / "bench_once.json"

def read_env_var(key, default=""):
    val = os.environ.get(key)
    if val is not None:
        return val
    envp = ROOT / ".env"
    if envp.exists():
        for line in envp.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip()
    return default

def http_get_json(url, timeout=2.5):
    try:
        with request.urlopen(url, timeout=timeout) as r:
            import json as _json
            return _json.loads(r.read().decode("utf-8", "ignore"))
    except Exception:
        return None

def http_post_json(url, timeout=30):
    try:
        req = request.Request(url, method="POST")
        with request.urlopen(req, timeout=timeout) as r:
            import json as _json
            return _json.loads(r.read().decode("utf-8", "ignore"))
    except Exception:
        return None

def current_fingerprint():
    """Make a fingerprint from backend + model path + size/mtime."""
    # Ask backend via gpu_detect if present
    backend = "unknown"
    gp = ROOT / "scripts" / "gpu_detect.py"
    try:
        if gp.exists():
            out = subprocess.check_output([sys.executable, str(gp)], text=True, timeout=6)
            for ln in out.splitlines():
                if ln.startswith("Backend:"):
                    backend = ln.split(":", 1)[1].strip()
                    break
    except Exception:
        pass

    model_path = read_env_var("AGENT_MODEL", "gguf/llama-3.1-8b-q4_0.gguf")
    mp = ROOT / model_path
    sig = ""
    try:
        st = mp.stat()
        sig = f"{mp}|{st.st_size}|{int(st.st_mtime)}"
    except Exception:
        sig = f"{mp}|missing"

    h = hashlib.sha256()
    h.update(backend.encode())
    h.update(sig.encode())
    return backend, str(mp), h.hexdigest()

def need_bench(fp: str) -> bool:
    if not BENCH_ONCE.exists():
        return True
    try:
        data = json.loads(BENCH_ONCE.read_text(encoding="utf-8"))
    except Exception:
        return True
    return data.get("last_fp") != fp

def record_bench(fp: str, payload: dict | None):
    try:
        BENCH_ONCE.write_text(json.dumps({"last_fp": fp, "last_result": payload}, indent=2), encoding="utf-8")
    except Exception:
        pass

def wait_until_up(max_wait=45):
    """Wait for /api/status to respond."""
    t0 = time.time()
    while time.time() - t0 < max_wait:
        j = http_get_json(f"{HOST}/api/status", timeout=2.5)
        if j and isinstance(j, dict):
            return True
        time.sleep(1.2)
    return False

def main():
    # Launch the Flask app as a child process
    env = os.environ.copy()
    env.setdefault("APP_MODE", "offline")
    app_py = ROOT / "desktop" / "webui" / "app.py"
    if not app_py.exists():
        print("✖ desktop/webui/app.py not found.")
        sys.exit(1)

    print(f"→ Launching UI at {HOST} …")
    proc = subprocess.Popen([sys.executable, str(app_py)], env=env)

    try:
        if not wait_until_up():
            print("⚠️ UI did not become ready in time; leaving process running for manual check.")
            return proc.wait()

        print("✅ UI is up. Evaluating auto-bench…")
        backend, model_path, fp = current_fingerprint()
        print(f"Backend={backend}  Model={Path(model_path).name}  FP={fp[:12]}…")

        if need_bench(fp):
            print("→ First boot for this backend+model. Running /api/bench …")
            res = http_post_json(f"{HOST}/api/bench", timeout=180)
            if res and res.get("ok"):
                avg = (res.get("avg") or {}).get("avg_tok_per_sec")
                print(f"   Bench OK. avg_tok/s={avg if avg is not None else 'n/a'}")
            else:
                print("   Bench did not return OK (check logs).")
            record_bench(fp, res or {})
        else:
            print("→ Bench already recorded for this backend+model. Skipping.")

        # Keep attached to the app process
        return proc.wait()

    except KeyboardInterrupt:
        print("\n⛔ Ctrl+C received; stopping app…")
        try: proc.terminate()
        except Exception: pass
        try: proc.wait(timeout=5)
        except Exception: pass
    except Exception as e:
        print("❌ Launcher error:", e)
        try: proc.terminate()
        except Exception: pass
        try: proc.wait(timeout=5)
        except Exception: pass

if __name__ == "__main__":
    sys.exit(main() or 0)