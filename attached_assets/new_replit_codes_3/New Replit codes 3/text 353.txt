#!/usr/bin/env python3
"""
auto_tune_env.py — GPU-aware environment optimizer.
• Detects backend + VRAM via gpu_detect.py
• Suggests ctx + quant
• Updates .env intelligently (LLM_CTX, LLM_THREADS, AGENT_MODEL)
• Creates safe .env.bak
"""

import re, shutil, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
BACKUP = ROOT / ".env.bak"
GGUF_DIR = ROOT / "gguf"  # where your model files live

def run_gpu_detect():
    try:
        out = subprocess.check_output([sys.executable, "scripts/gpu_detect.py"], text=True)
        return out
    except Exception as e:
        print("gpu_detect.py failed:", e)
        return ""

def parse_gpu_suggestions(text):
    ctx = None
    quant = None
    backend = "cpu"
    for line in text.splitlines():
        if "LLM_CTX:" in line:
            try:
                ctx = int(re.findall(r"(\d+)", line)[0])
            except: pass
        if "Quant:" in line:
            quant = line.split("Quant:")[-1].strip()
        if "Backend:" in line:
            backend = line.split("Backend:")[-1].strip()
    return {"ctx": ctx or 4096, "quant": quant or "Q4_K_M", "backend": backend}

def find_best_model(quant):
    """Try to find a GGUF file that matches quant preference"""
    if not GGUF_DIR.exists():
        print("⚠️ GGUF dir missing — skipping model relink.")
        return None
    cand = list(GGUF_DIR.glob(f"*{quant.lower()}*.gguf"))
    if cand:
        best = max(cand, key=lambda p: p.stat().st_size)
        return best
    # fallback to any gguf
    anyfile = list(GGUF_DIR.glob("*.gguf"))
    return anyfile[0] if anyfile else None

def edit_env(ctx, threads, quant, model_path):
    if not ENV_FILE.exists():
        print(".env missing — creating new.")
        ENV_FILE.write_text("", encoding="utf-8")

    shutil.copy2(ENV_FILE, BACKUP)
    print(f"💾 Backup saved as {BACKUP.name}")

    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    out = []
    set_ctx = set_threads = set_model = False

    for l in lines:
        if l.startswith("LLM_CTX="):
            out.append(f"LLM_CTX={ctx}")
            set_ctx = True
        elif l.startswith("LLM_THREADS="):
            out.append(f"LLM_THREADS={threads}")
            set_threads = True
        elif l.startswith("AGENT_MODEL=") and model_path:
            out.append(f"AGENT_MODEL={model_path}")
            set_model = True
        else:
            out.append(l)

    if not set_ctx: out.append(f"LLM_CTX={ctx}")
    if not set_threads: out.append(f"LLM_THREADS={threads}")
    if model_path and not set_model: out.append(f"AGENT_MODEL={model_path}")

    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"✅ Updated .env:\n  LLM_CTX={ctx}\n  LLM_THREADS={threads}\n  AGENT_MODEL={model_path or 'unchanged'}")

def main():
    print("=== Auto-Tune .env ===")
    gpu_out = run_gpu_detect()
    sug = parse_gpu_suggestions(gpu_out)
    threads = max(2, (os.cpu_count() or 8)//2)

    print(f"→ Backend: {sug['backend']}")
    print(f"→ Quant:   {sug['quant']}")
    print(f"→ Context: {sug['ctx']}")
    print(f"→ Threads: {threads}")

    model_path = find_best_model(sug["quant"])
    if model_path:
        print(f"→ Best matching model: {model_path.name}")
    else:
        print("⚠️ No matching model found in /gguf")

    edit_env(sug["ctx"], threads, sug["quant"], model_path)

    print("\n✅ Auto-tune complete! You can verify by running:")
    print("   cat .env | grep -E 'LLM_CTX|LLM_THREADS|AGENT_MODEL'")
    print("   python scripts/diagnostic_system.py")

if __name__ == "__main__":
    main()