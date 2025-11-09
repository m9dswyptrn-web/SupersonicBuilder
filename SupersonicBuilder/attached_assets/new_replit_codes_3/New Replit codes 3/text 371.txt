#!/usr/bin/env python3
"""
post_tune_ping.py — success/error chime + crisp summary + TTS speak mode

Usage:
  python scripts/post_tune_ping.py
  python scripts/post_tune_ping.py --error "Missing model"
  python scripts/post_tune_ping.py --say "Supersonic status is green"

Behavior:
- Default: plays assistant_ready.wav (or TTS fallback), prints env summary
- --error: plays error_alert.wav, prints reason, TTS fallback if needed
- --say: forces TTS of the provided message (no WAV required)
"""
import os, sys, shutil, subprocess, platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO_READY = ROOT / "assets" / "audio" / "assistant_ready.wav"
AUDIO_ERROR = ROOT / "assets" / "audio" / "error_alert.wav"
ENV = ROOT / ".env"
GPU_DETECT = ROOT / "scripts" / "gpu_detect.py"

def load_env_keys():
    keys = {"LLM_CTX":"", "LLM_THREADS":"", "AGENT_MODEL":""}
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                if "=" in line:
                    k,v = line.split("=",1)
                    if k in keys: keys[k] = v.strip()
    return keys

def detect_backend():
    try:
        out = subprocess.check_output([sys.executable, str(GPU_DETECT)], text=True)
        for line in out.splitlines():
            if line.startswith("Backend:"):
                return line.split(":",1)[1].strip()
    except Exception:
        pass
    return "unknown"

def play_wav(path: Path) -> bool:
    if not path.exists(): return False
    sysname = platform.system().lower()
    if sysname == "darwin" and shutil.which("afplay"):
        return subprocess.run(["afplay", str(path)], check=False).returncode == 0
    if sysname == "linux":
        if shutil.which("paplay"):
            return subprocess.run(["paplay", str(path)], check=False).returncode == 0
        if shutil.which("aplay"):
            return subprocess.run(["aplay", str(path)], check=False).returncode == 0
    if sysname == "windows":
        try:
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception:
            return False
    return False

def say_tts(msg: str):
    try:
        import pyttsx3
    except Exception:
        print("(pyttsx3 not installed; run: pip install pyttsx3)")
        return False
    try:
        eng = pyttsx3.init()
        eng.say(msg)
        eng.runAndWait()
        return True
    except Exception:
        return False

def main():
    # Modes
    if "--say" in sys.argv:
        i = sys.argv.index("--say")
        msg = " ".join(sys.argv[i+1:]).strip() or "Status not specified."
        print(f"[TTS] {msg}")
        _ = say_tts(msg)
        return

    is_error = False
    err_msg = ""
    if "--error" in sys.argv:
        is_error = True
        i = sys.argv.index("--error")
        err_msg = " ".join(sys.argv[i+1:]).strip() or "Unknown error"

    env = load_env_keys()
    backend = detect_backend()
    summary = (
        f"Supersonic status: {'ERROR' if is_error else 'OK'} | "
        f"backend={backend}  LLM_CTX={env['LLM_CTX'] or 'n/a'}  "
        f"LLM_THREADS={env['LLM_THREADS'] or 'n/a'}  "
        f"MODEL={Path(env['AGENT_MODEL']).name if env['AGENT_MODEL'] else 'n/a'}"
    )
    print(summary)
    if is_error:
        print(f"Reason: {err_msg}")

    sound = AUDIO_ERROR if is_error else AUDIO_READY
    played = play_wav(sound)
    if not played and is_error:
        _ = say_tts(f"Supersonic error. {err_msg}")
    elif not played:
        _ = say_tts("Supersonic tuning complete. System ready.")

if __name__ == "__main__":
    main()