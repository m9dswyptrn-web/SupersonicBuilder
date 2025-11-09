#!/usr/bin/env python3
"""
diagnostic_system.py — Supersonic smart diagnostics + auto-tune trigger

What it does:
1) Prints toolchain presence (python/node/npm/cargo/mkdocs)
2) Verifies key project files exist
3) Runs GPU detection (gpu_detect.py)
4) Tracks hardware + model state in .supersonic_cache/hw_state.json
5) Auto-runs auto_tune_env.py when hardware/model changed since last run
"""

import os, sys, json, shutil, platform, subprocess, hashlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / ".supersonic_cache"
CACHE_DIR.mkdir(exist_ok=True)
STATE_FILE = CACHE_DIR / "hw_state.json"

def which(x): 
    p = shutil.which(x)
    return p if p else "not found"

def exists(p): 
    return "OK" if Path(p).exists() else "missing"

def file_sig(p: Path):
    try:
        s = p.stat()
        return {"size": s.st_size, "mtime": int(s.st_mtime)}
    except Exception:
        return None

def run_py(args):
    return subprocess.run([sys.executable] + args, check=False, capture_output=True, text=True)

def parse_gpu_detect(text: str):
    out = {"backend":"cpu","quant":None,"ctx":None,"gpus":[],"model_path":None,"model_size":None}
    for line in text.splitlines():
        ls = line.strip()
        if ls.startswith("Backend:"):
            out["backend"] = ls.split(":",1)[1].strip()
        elif ls.startswith("Suggested settings:"):
            pass
        elif ls.startswith("Quant:"):
            out["quant"] = ls.split(":",1)[1].strip()
        elif ls.startswith("LLM_CTX:"):
            try: out["ctx"] = int(ls.split(":",1)[1].strip())
            except: pass
        elif ls.startswith("Model path:"):
            mp = ls.split(":",1)[1].strip().split(" (",1)[0].strip()
            out["model_path"] = mp
        elif "GPU" in ls and "VRAM" in ls:
            # lines like: "GPU0: 8.0 GB"
            out["gpus"].append(ls)
        elif "Model path:" in ls and "(" in ls and "B)" in ls:
            # handled above
            pass
    # model size extraction
    try:
        # find text "(X.Y GB)" pattern from the same line if present
        import re
        m = re.search(r"Model path:.*\(([\d\.]+\s*[KMGT]?B)\)", text)
        if m: out["model_size"] = m.group(1)
    except Exception:
        pass
    return out

def load_prev_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def state_fingerprint(info: dict):
    """
    Build a stable fingerprint from backend, gpu lines, model path + file sig.
    """
    h = hashlib.sha256()
    h.update((info.get("backend") or "cpu").encode())
    for g in info.get("gpus", []):
        h.update(g.encode())
    mp = info.get("model_path") or ""
    h.update(mp.encode())
    # add file signature (size/mtime) for precision
    sig = file_sig(Path(mp)) if mp else None
    h.update(json.dumps(sig, sort_keys=True).encode())
    return h.hexdigest()

def main():
    print("=== Supersonic Diagnostics ===")
    print("System:", platform.platform())
    items = {
        "python": which("python"),
        "node": which("node"),
        "npm": which("npm"),
        "cargo": which("cargo"),
        "mkdocs": which("mkdocs"),
    }
    for k,v in items.items():
        print(f"{k:24} {v}")

    print("\nKey paths:")
    for p in ["desktop/webui/app.py", "agent/main_llm.py", "src-tauri/tauri.conf.json"]:
        print(f"{p:32} {exists(p)}")

    env_path = ROOT / ".env"
    print("\n.env present? ", "OK" if env_path.exists() else "missing")
    print(".env.sample?  ", "OK" if (ROOT / ".env.sample").exists() else "missing")

    # --- GPU detect
    gp = ROOT / "scripts" / "gpu_detect.py"
    gpu_info = {}
    if gp.exists():
        print("\n--- GPU Detect ---")
        res = run_py([str(gp)])
        sys.stdout.write(res.stdout)
        sys.stderr.write(res.stderr)
        gpu_info = parse_gpu_detect(res.stdout)
    else:
        print("\n(gpu_detect.py not found — skip)")

    # Build current state
    cur = {
        "backend": gpu_info.get("backend","cpu"),
        "gpus": gpu_info.get("gpus", []),
        "model_path": gpu_info.get("model_path"),
        "model_sig": file_sig(Path(gpu_info.get("model_path") or "")) if gpu_info.get("model_path") else None,
        "ts": int(time.time())
    }
    cur["fingerprint"] = state_fingerprint(cur)

    prev = load_prev_state()
    prev_fp = prev.get("fingerprint")
    changed = (prev_fp != cur["fingerprint"])

    print("\nState:")
    print(json.dumps(cur, indent=2))

    if changed:
        print("\n⚠️ Hardware/model change detected (or first run). Auto-tuning .env …")
        auto = ROOT / "scripts" / "auto_tune_env.py"
        if auto.exists():
            res = run_py([str(auto)])
            sys.stdout.write(res.stdout)
            sys.stderr.write(res.stderr)
        else:
            print("(auto_tune_env.py not found — skipping auto-tune)")
        save_state(cur)
    else:
        print("\n✅ No hardware/model changes since last run. Skipping auto-tune.")
        # still allow manual opt-in
        try:
            ans = input("\nRun auto-tune anyway? [y/N]: ").strip().lower()
        except EOFError:
            ans = "n"
        if ans.startswith("y"):
            auto = ROOT / "scripts" / "auto_tune_env.py"
            if auto.exists():
                res = run_py([str(auto)])
                sys.stdout.write(res.stdout)
                sys.stderr.write(res.stderr)
            else:
                print("(auto_tune_env.py not found — skipping)")

if __name__ == "__main__":
    main()