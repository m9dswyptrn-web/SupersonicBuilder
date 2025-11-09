#!/usr/bin/env python3
"""
post_tune_ping.py — play a success chime and print a one-line summary
- Tries to play assets/audio/assistant_ready.wav using platform-native players
  (macOS: afplay, Linux: aplay/paplay, Windows: winsound)
- Falls back to TTS (pyttsx3) if available, otherwise prints text-only.
- Also echoes key .env values and current backend from gpu_detect.py.
"""
import os, sys, shutil, subprocess, platform, configparser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "assets" / "audio" / "assistant_ready.wav"
ENV = ROOT / ".env"
GPU_DETECT = ROOT / "scripts" / "gpu_detect.py"

def load_env_keys():
    # robust .env reader without extra deps
    E = {"LLM_CTX":"", "LLM_THREADS":"", "AGENT_MODEL":""}
    if not ENV.exists():
        return E
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"): 
            continue
        if "=" in line:
            k,v = line.split("=",1)
            if k in E: E[k] = v.strip()
    return E

def detect_backend():
    try:
        out = subprocess.check_output([sys.executable, str(GPU_DETECT)], text=True)
        for line in out.splitlines():
            if line.startswith("Backend:"):
                return line.split(":",1)[1].strip()
    except Exception:
        pass
    return "unknown"

def say_tts(msg: str):
    try:
        import pyttsx3
        eng = pyttsx3.init()
        eng.say(msg)
        eng.runAndWait()
        return True
    except Exception:
        return False

def play_wav(path: Path) -> bool:
    if not path.exists():
        return False
    system = platform.system().lower()
    if system == "darwin" and shutil.which("afplay"):
        return subprocess.run(["afplay", str(path)], check=False).returncode == 0
    if system == "linux":
        if shutil.which("paplay"):
            return subprocess.run(["paplay", str(path)], check=False).returncode == 0
        if shutil.which("aplay"):
            return subprocess.run(["aplay", str(path)], check=False).returncode == 0
    if system == "windows":
        try:
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception:
            return False
    return False

def main():
    env = load_env_keys()
    backend = detect_backend()
    summary = (
        f"Supersonic tuned: backend={backend}  "
        f"LLM_CTX={env['LLM_CTX'] or 'n/a'}  "
        f"LLM_THREADS={env['LLM_THREADS'] or 'n/a'}  "
        f"MODEL={Path(env['AGENT_MODEL']).name if env['AGENT_MODEL'] else 'n/a'}"
    )
    print(summary)

    # chime or TTS
    played = play_wav(AUDIO)
    if not played:
        _ = say_tts("Supersonic tuning complete. System ready.")  # best-effort

if __name__ == "__main__":
    main()