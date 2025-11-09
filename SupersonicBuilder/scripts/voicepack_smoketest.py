#!/usr/bin/env python3
"""
Supersonic — Voice Pack Smoke Test

Checks all voicepacks under assets/audio/voicepacks/<PACK>/ for required WAVs.
Optionally auto-repairs missing files using pyttsx3 TTS (offline) or
beep placeholders when TTS isn't available.

Usage:
  python3 scripts/voicepack_smoketest.py
  python3 scripts/voicepack_smoketest.py --pack commander
  python3 scripts/voicepack_smoketest.py --repair
  python3 scripts/voicepack_smoketest.py --pack flightops --repair --strict

Exit codes:
  0 = all good
  2 = repaired issues (now good)
  1 = failures remain
"""
from pathlib import Path
import argparse, io, math, wave, struct, sys

ROOT = Path(__file__).resolve().parents[1]
VP_ROOT = ROOT / "assets" / "audio" / "voicepacks"

REQUIRED_EVENTS = [
    "build_start",
    "build_success",
    "build_fail",
    "deploy_start",
    "deploy_done",
    "doctor_ok",
    "doctor_warn",
]

EVENT_LINES = {
    "build_start":  "Build sequence initiated.",
    "build_success":"Build complete. All systems nominal.",
    "build_fail":   "Build failed. Review diagnostics.",
    "deploy_start": "Deployment sequence initiated.",
    "deploy_done":  "Deployment complete. Systems online.",
    "doctor_ok":    "Doctor scan complete. Green across the board.",
    "doctor_warn":  "Doctor scan complete. Review warnings.",
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

def save_tts(text: str, path: Path) -> bool:
    try:
        import pyttsx3
        eng = pyttsx3.init()
        try:
            rate = int(eng.getProperty("rate") or 185)
            eng.setProperty("rate", int(rate * 0.95))
        except Exception:
            pass
        path.parent.mkdir(parents=True, exist_ok=True)
        eng.save_to_file(text, str(path))
        eng.runAndWait()
        return path.exists() and path.stat().st_size > 0
    except Exception:
        return False

def repair_event(pack_dir: Path, event: str) -> bool:
    wav = pack_dir / f"{event}.wav"
    text = EVENT_LINES.get(event, event.replace("_", " ").title())
    if save_tts(text, wav):
        print(f"  [fix][tts] {pack_dir.name}/{wav.name}")
        return True
    write_beep(wav)
    if "warn" in event or "fail" in event:
        tmp = pack_dir / f"_{event}_tmp.wav"
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
    print(f"  [fix][beep] {pack_dir.name}/{wav.name}")
    return True

def test_pack(pack_dir: Path, strict: bool, do_repair: bool) -> tuple:
    missing = []
    for ev in REQUIRED_EVENTS:
        wav = pack_dir / f"{ev}.wav"
        if not wav.exists():
            missing.append(ev)
        elif strict and wav.stat().st_size <= 44:
            missing.append(ev)

    repaired = 0
    if missing and do_repair:
        print(f"[repair] {pack_dir.name}: repairing {len(missing)} missing/corrupt file(s)")
        for ev in missing:
            if repair_event(pack_dir, ev):
                repaired += 1

    bad_after = 0
    for ev in REQUIRED_EVENTS:
        wav = pack_dir / f"{ev}.wav"
        if not wav.exists():
            bad_after += 1
        elif strict and wav.stat().st_size <= 44:
            bad_after += 1

    return len(missing), repaired, bad_after

def main():
    ap = argparse.ArgumentParser(description="Voice pack smoke test / repair")
    ap.add_argument("--pack", help="Single pack to test (default = all packs)")
    ap.add_argument("--repair", action="store_true", help="Auto-repair missing files")
    ap.add_argument("--strict", action="store_true", help="Treat tiny/empty WAVs as failures")
    args = ap.parse_args()

    if not VP_ROOT.exists():
        print("No voicepacks folder found:", VP_ROOT)
        return 1

    packs = []
    if args.pack:
        pdir = VP_ROOT / args.pack
        if not pdir.exists():
            print(f"ERROR: pack '{args.pack}' not found under {VP_ROOT}")
            return 1
        packs = [pdir]
    else:
        packs = sorted([p for p in VP_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")], key=lambda x: x.name)

    total_missing = total_repaired = total_bad = 0
    for p in packs:
        print(f"[check] {p.name}")
        miss, rep, bad = test_pack(p, strict=args.strict, do_repair=args.repair)
        total_missing += miss
        total_repaired += rep
        total_bad += bad
        print(f"  -> missing: {miss}, repaired: {rep}, remaining issues: {bad}")

    print("\nSummary:")
    print(f"  Packs checked: {len(packs)}")
    print(f"  Initially missing: {total_missing}")
    print(f"  Repaired: {total_repaired}")
    print(f"  Remaining issues: {total_bad}")

    if total_bad == 0 and total_repaired > 0:
        return 2
    return 0 if total_bad == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
