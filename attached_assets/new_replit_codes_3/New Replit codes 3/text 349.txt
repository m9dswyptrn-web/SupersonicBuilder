#!/usr/bin/env python3
"""
auto_tune_env.py — read GPU detect output and update .env automatically.
Creates .env.bak first, then merges in new LLM_CTX / LLM_THREADS.
"""

import re, shutil, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
BACKUP = ROOT / ".env.bak"

def parse_suggestions():
    try:
        out = subprocess.check_output([sys.executable, "scripts/gpu_detect.py"], text=True)
    except Exception as e:
        print("gpu_detect.py failed:", e)
        return None
    # crude parse
    ctx = None
    quant = None
    for line in out.splitlines():
        if "LLM_CTX:" in line:
            try: ctx = int(re.findall(r"(\d+)", line)[0])
            except: pass
        if "Quant:" in line:
            quant = line.split("Quant:")[-1].strip()
    return {"ctx": ctx, "quant": quant}

def edit_env(new_ctx, new_threads=None):
    if not ENV_FILE.exists():
        print(".env not found, creating new from sample if possible.")
        sample = ROOT / ".env.sample"
        if sample.exists():
            shutil.copy2(sample, ENV_FILE)
        else:
            ENV_FILE.write_text("", encoding="utf-8")

    shutil.copy2(ENV_FILE, BACKUP)
    print(f"→ Backup saved: {BACKUP}")

    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    out = []
    updated = {"ctx": False, "threads": False}
    for l in lines:
        if l.startswith("LLM_CTX="):
            out.append(f"LLM_CTX={new_ctx}")
            updated["ctx"] = True
        elif l.startswith("LLM_THREADS=") and new_threads is not None:
            out.append(f"LLM_THREADS={new_threads}")
            updated["threads"] = True
        else:
            out.append(l)
    if not updated["ctx"]:
        out.append(f"LLM_CTX={new_ctx}")
    if new_threads is not None and not updated["threads"]:
        out.append(f"LLM_THREADS={new_threads}")
    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("✅ .env updated.")

def main():
    sug = parse_suggestions()
    if not sug:
        print("Couldn’t parse GPU suggestions.")
        return
    ctx = sug.get("ctx") or 4096
    threads = os.cpu_count()//2 or 4
    print(f"Suggested LLM_CTX={ctx}, LLM_THREADS={threads}")
    edit_env(ctx, threads)

if __name__ == "__main__":
    main()