#!/usr/bin/env python3
"""
Supersonic — Multi-Pack Voice Generator
Creates WAV event prompts for multiple packs under assets/audio/voicepacks/<PACK>/.

Packs (default):
  commander     – neutral, moderate rate
  aiops         – faster, "assistant" vibe
  flightops     – calm, slightly slower
  industrialops – slow, weighty
  arcadehud     – quick, gamey

Usage:
  python3 scripts/generate_multipack_voicepacks.py
  python3 scripts/generate_multipack_voicepacks.py --packs commander,aiops
  VOICE_RATE=190 python3 scripts/generate_multipack_voicepacks.py
"""

from pathlib import Path
import os, io, math, wave, struct, argparse

EVENT_LINES = {
    "build_start":  "Build sequence initiated.",
    "build_success":"Build complete. All systems nominal.",
    "build_fail":   "Build failed. Review diagnostics.",
    "deploy_start": "Deployment sequence initiated.",
    "deploy_done":  "Deployment complete. Systems online.",
    "doctor_ok":    "Doctor scan complete. Green across the board.",
    "doctor_warn":  "Doctor scan complete. Review warnings.",
}

PACK_PROFILES = {
    "commander":     {"rate": 185, "voice_hint": ["en", "us", "neutral", "zira", "microsoft", "default"]},
    "aiops":         {"rate": 205, "voice_hint": ["en", "female", "aria", "zira", "assistant"]},
    "flightops":     {"rate": 170, "voice_hint": ["en", "male", "guy", "george", "baritone"]},
    "industrialops": {"rate": 155, "voice_hint": ["en", "male", "microsoft", "robot", "david"]},
    "arcadehud":     {"rate": 215, "voice_hint": ["en", "light", "casual", "young", "fast"]},
}

SAMPLE_RATE = 22050
BEEP_HZ = 880
BEEP_MS = 140
PAUSE_MS = 80

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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buf.getvalue())

def pick_voice(engine, hints):
    try:
        voices = engine.getProperty("voices") or []
        if not voices: return None
        lower_hints = [h.lower() for h in hints]
        for v in voices:
            meta = f"{getattr(v,'name','')} {getattr(v,'id','')} {getattr(v,'languages','')}".lower()
            if all(h in meta for h in lower_hints):
                return v.id
        for v in voices:
            meta = f"{getattr(v,'name','')} {getattr(v,'id','')} {getattr(v,'languages','')}".lower()
            if any(h in meta for h in lower_hints):
                return v.id
        return voices[0].id
    except Exception:
        return None

def save_tts(text: str, path: Path, rate: int, voice_hints=None) -> bool:
    try:
        import pyttsx3
        eng = pyttsx3.init()
        vid = pick_voice(eng, voice_hints or [])
        if vid:
            try: eng.setProperty("voice", vid)
            except Exception: pass
        env_rate = os.getenv("VOICE_RATE")
        r = int(env_rate) if env_rate and env_rate.isdigit() else rate
        try: eng.setProperty("rate", r)
        except Exception: pass

        path.parent.mkdir(parents=True, exist_ok=True)
        eng.save_to_file(text, str(path))
        eng.runAndWait()
        return path.exists() and path.stat().st_size > 0
    except Exception as e:
        print(f"[tts:skip] {path.name}: {e.__class__.__name__}")
        return False

def build_pack(pack: str, rate: int, voice_hints):
    out_dir = Path("assets/audio/voicepacks") / pack
    out_dir.mkdir(parents=True, exist_ok=True)
    made = 0
    for event, line in EVENT_LINES.items():
        wav = out_dir / f"{event}.wav"
        if save_tts(line, wav, rate=rate, voice_hints=voice_hints):
            print(f"[ok][tts] {pack}/{wav.name}")
        else:
            write_beep(wav)
            if "warn" in event or "fail" in event:
                tmp = out_dir / f"_{event}_tmp.wav"
                write_beep(tmp, hz=600, ms=120)
                with wave.open(str(wav),'rb') as w1, wave.open(str(tmp),'rb') as w2:
                    params = w1.getparams()
                    merged = io.BytesIO()
                    with wave.open(merged,'wb') as w3:
                        w3.setparams(params)
                        w3.writeframes(w1.readframes(w1.getnframes()))
                        w3.writeframes(w2.readframes(w2.getnframes()))
                    wav.write_bytes(merged.getvalue())
                try: tmp.unlink()
                except: pass
            print(f"[ok][beep] {pack}/{wav.name}")
        made += 1
    print(f"✅ Pack ready: {pack} ({made} files) -> {out_dir}")
    return out_dir

def parse_args():
    ap = argparse.ArgumentParser(description="Generate multiple voicepacks for Supersonic.")
    ap.add_argument("--packs", help="Comma list of packs to build", default="commander,aiops,flightops,industrialops,arcadehud")
    return ap.parse_args()

def main():
    args = parse_args()
    packs = [p.strip() for p in args.packs.split(",") if p.strip()]
    for p in packs:
        prof = PACK_PROFILES.get(p, {"rate": 185, "voice_hint": ["en"]})
        build_pack(p, rate=prof["rate"], voice_hints=prof["voice_hint"])

if __name__ == "__main__":
    main()
