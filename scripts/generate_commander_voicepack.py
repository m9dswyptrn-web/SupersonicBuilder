#!/usr/bin/env python3
"""
Supersonic — Commander Voice Pack Builder
Generates WAV event prompts into assets/audio/voicepacks/<PACK>/.

- Uses pyttsx3 (offline TTS). If missing or errors, writes beep placeholders.
- Safe to run repeatedly (overwrites existing files).
- PACK name can be changed with env VOICE_PACK=yourpack

Usage:
  python3 scripts/generate_commander_voicepack.py
  VOICE_PACK=aiops python3 scripts/generate_commander_voicepack.py
"""
from pathlib import Path
import os, io, math, wave, struct

PACK = os.getenv("VOICE_PACK", "commander")
OUT_DIR = Path("assets/audio/voicepacks") / PACK
SAMPLE_RATE = 22050
BEEP_HZ = 880
BEEP_MS = 140
PAUSE_MS = 80

EVENT_LINES = {
    "build_start":  "Build sequence initiated.",
    "build_success":"Build complete. All systems nominal.",
    "build_fail":   "Build failed. Review diagnostics.",
    "deploy_start": "Deployment sequence initiated.",
    "deploy_done":  "Deployment complete. Systems online.",
    "doctor_ok":    "Doctor scan complete. Green across the board.",
    "doctor_warn":  "Doctor scan complete. Review warnings.",
}

def ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

def write_beep(path: Path, hz=BEEP_HZ, ms=BEEP_MS, sr=SAMPLE_RATE):
    frames = int(ms * sr / 1000)
    amp = 0.35
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        for n in range(frames):
            t = n / sr
            s = amp * math.sin(2 * math.pi * hz * t)
            w.writeframes(struct.pack('<h', int(s * 32767)))
        silence = int(PAUSE_MS * sr / 1000)
        for _ in range(silence):
            w.writeframes(struct.pack('<h', 0))
    path.write_bytes(buf.getvalue())

def save_tts(text: str, path: Path) -> bool:
    try:
        import pyttsx3
        eng = pyttsx3.init()
        try:
            rate = eng.getProperty("rate")
            eng.setProperty("rate", int(rate * 0.95))
        except Exception:
            pass
        eng.save_to_file(text, str(path))
        eng.runAndWait()
        return path.exists() and path.stat().st_size > 0
    except Exception as e:
        print(f"[tts:skip] {text} -> {path.name} ({e.__class__.__name__})")
        return False

def build_pack():
    ensure_dir(OUT_DIR)
    made = []
    for event, line in EVENT_LINES.items():
        out = OUT_DIR / f"{event}.wav"
        ok = save_tts(line, out)
        if not ok:
            write_beep(out, hz=BEEP_HZ, ms=BEEP_MS)
            if "warn" in event or "fail" in event:
                tmp2 = OUT_DIR / f"_{event}_tmp.wav"
                write_beep(tmp2, hz=600, ms=100)
                with wave.open(str(out), 'rb') as w1, wave.open(str(tmp2), 'rb') as w2:
                    params = w1.getparams()
                    merged = io.BytesIO()
                    with wave.open(merged, 'wb') as w3:
                        w3.setparams(params)
                        w3.writeframes(w1.readframes(w1.getnframes()))
                        w3.writeframes(w2.readframes(w2.getnframes()))
                    out.write_bytes(merged.getvalue())
                try: tmp2.unlink()
                except: pass
        made.append(out.name)
        print(f"[ok] {out}")
    print(f"\n✅ Voice pack generated: {PACK} ({len(made)} files) @ {OUT_DIR}")

if __name__ == "__main__":
    build_pack()
