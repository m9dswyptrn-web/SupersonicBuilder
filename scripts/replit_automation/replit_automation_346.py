#!/usr/bin/env python3
"""
gpu_detect.py — best-effort detector for CUDA / ROCm / Metal / CPU
Also checks your GGUF model size and estimates if VRAM/RAM is likely sufficient.

No external deps required, but will use torch/pynvml/rocm-smi if available.
"""

import os, sys, platform, shutil, subprocess
from pathlib import Path

AGENT_MODEL = os.getenv("AGENT_MODEL", "gguf/llama-3.1-8b-q4_0.gguf")

def _bytes_fmt(n):
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024.0: return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

def _file_size(path: Path):
    try:
        return path.stat().st_size
    except Exception:
        return None

def _try_import_torch():
    try:
        import torch
        return torch
    except Exception:
        return None

def _pynvml_total_mem():
    try:
        import pynvml
        pynvml.nvmlInit()
        devcount = pynvml.nvmlDeviceGetCount()
        totals = []
        for i in range(devcount):
            h = pynvml.nvmlDeviceGetHandleByIndex(i)
            totals.append(pynvml.nvmlDeviceGetMemoryInfo(h).total)
        return totals  # list of bytes
    except Exception:
        return None

def _nvidia_smi_total_mem():
    try:
        out = subprocess.check_output(["nvidia-smi","--query-gpu=memory.total","--format=csv,noheader,nounits"],
                                      stderr=subprocess.DEVNULL, text=True, timeout=3)
        vals = []
        for line in out.strip().splitlines():
            line=line.strip()
            if line:
                vals.append(int(line)*1024*1024)  # MiB -> bytes
        return vals or None
    except Exception:
        return None

def _rocm_smi_total_mem():
    try:
        if not shutil.which("rocm-smi"):
            return None
        out = subprocess.check_output(["rocm-smi", "--showmeminfo","vram"], stderr=subprocess.DEVNULL, text=True, timeout=4)
        # crude parse: look for digits + 'MB'
        import re
        vals=[]
        for m in re.finditer(r"Total VRAM Memory.*?:\s*([0-9.]+)\s*MiB", out):
            vals.append(int(float(m.group(1)))*1024*1024)
        return vals or None
    except Exception:
        return None

def detect_backend():
    sysname = platform.system().lower()
    torch = _try_import_torch()

    # CUDA via torch
    if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        return "cuda"

    # CUDA via NVML/NVIDIA-SMI
    if _pynvml_total_mem() or _nvidia_smi_total_mem():
        return "cuda"

    # ROCm via torch
    if torch is not None and hasattr(torch.version, "hip") and torch.version.hip:
        return "rocm"

    # ROCm via rocm-smi
    if _rocm_smi_total_mem():
        return "rocm"

    # Apple Metal heuristic
    if sysname == "darwin":
        # If on Apple Silicon, very likely Metal can be used by llama-cpp-python Metal build
        return "metal"

    # Fallback
    return "cpu"

def total_vram_bytes(backend: str):
    if backend == "cuda":
        return (_pynvml_total_mem() or _nvidia_smi_total_mem())
    if backend == "rocm":
        return _rocm_smi_total_mem()
    # Metal & CPU unknown
    return None

def suggest_quant_and_ctx(vram_bytes_list, model_bytes):
    """
    Very rough heuristics for safe starting points.
    Returns dict with suggested quant and ctx.
    """
    # Default suggestions
    suggestion = {"quant": "Q4_K_M", "ctx": 4096}

    # If we know VRAM (CUDA/ROCm)
    if vram_bytes_list:
        vram = max(vram_bytes_list)  # assume we’ll use the biggest GPU
        # Reserve headroom (~25%) for KV cache, runtime, OS
        safe_vram = int(vram * 0.75)

        # If model looks bigger than safe VRAM, suggest lower quant or CPU/Metal fallback
        if model_bytes and model_bytes > safe_vram:
            suggestion["quant"] = "Q3_K_M"
            suggestion["ctx"] = 3072 if safe_vram > 3_000_000_000 else 2048
        else:
            # Plenty of space: maybe keep Q4_K_M, ctx=4096
            pass

        return suggestion

    # For Metal/CPU (unknown VRAM): base on model size
    if model_bytes:
        if model_bytes >= 9_000_000_000:
            suggestion["quant"] = "Q3_K_M"
            suggestion["ctx"] = 3072
        elif model_bytes >= 5_500_000_000:
            suggestion["quant"] = "Q4_K_M"
            suggestion["ctx"] = 4096
        else:
            suggestion["quant"] = "Q4_K_M"
            suggestion["ctx"] = 4096
    return suggestion

def main():
    print("=== GPU Detect ===")
    backend = detect_backend()
    print("Backend:", backend)

    # VRAM list (bytes) if CUDA/ROCm
    vram_list = total_vram_bytes(backend)
    if vram_list:
        print("Detected GPUs / VRAM:")
        for i, b in enumerate(vram_list):
            print(f"  GPU{i}: {_bytes_fmt(b)}")

    # Model info
    mpath = Path(AGENT_MODEL)
    msize = _file_size(mpath)
    print(f"Model path: {mpath} ({_bytes_fmt(msize) if msize else 'missing'})")

    # Suggestions
    sug = suggest_quant_and_ctx(vram_list, msize or 0)
    print("Suggested settings:")
    print(f"  Quant: {sug['quant']}")
    print(f"  LLM_CTX: {sug['ctx']}")

    # Env hints
    print("\nHints:")
    if backend == "cuda":
        print("  Use CUDA build for llama-cpp-python:")
        print('    export CMAKE_ARGS="-DLLAMA_CUBLAS=on"')
        print("    pip install --force-reinstall --no-binary llama-cpp-python llama-cpp-python==0.3.2")
    elif backend == "rocm":
        print("  Use ROCm build for llama-cpp-python:")
        print('    export CMAKE_ARGS="-DLLAMA_HIPBLAS=on"')
        print("    pip install --force-reinstall --no-binary llama-cpp-python llama-cpp-python==0.3.2")
    elif backend == "metal":
        print("  Use Metal build on macOS:")
        print('    export CMAKE_ARGS="-DLLAMA_METAL=on"')
        print("    pip install --force-reinstall --no-binary llama-cpp-python llama-cpp-python==0.3.2")
    else:
        print("  CPU build detected; consider lowering quant (Q3_K_M) or ctx if memory is tight.")

    print("\nNext steps:")
    print("  1) Update your .env with suggested LLM_CTX and keep quant in your model filename choice.")
    print("  2) Re-run: python scripts/bench_llm.py")
    print("  3) Then:   python scripts/optimize_llm.py")

if __name__ == "__main__":
    main()