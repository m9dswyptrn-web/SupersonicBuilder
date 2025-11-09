#!/usr/bin/env python3
# scripts/post_tune_ping.py
import os, argparse, time, wave, struct, math, sys
try:
    import simpleaudio as sa
except Exception:
    sa = None

def load_wav_bytes(path):
    with wave.open(path, 'rb') as wf:
        fr = wf.getframerate(); nch = wf.getnchannels(); sw = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())
    return frames, fr, nch, sw

def apply_volume(frames, sampwidth, volume):
    if sampwidth != 2:  # 16-bit PCM expected; else no scale
        return frames
    vol = max(0.0, min(1.0, float(volume)))
    if abs(vol - 1.0) < 1e-6:
        return frames
    # scale 16-bit little-endian samples
    out = bytearray(len(frames))
    for i in range(0, len(frames), 2):
        s = struct.unpack_from('<h', frames, i)[0]
        s = int(max(-32768, min(32767, round(s * vol))))
        struct.pack_into('<h', out, i, s)
    return bytes(out)

def play(path, volume=1.0):
    frames, fr, nch, sw = load_wav_bytes(path)
    frames = apply_volume(frames, sw, volume)
    if sa is None:
        return False
    try:
        p = sa.play_buffer(frames, nch, sw, fr)
        p.wait_done()
        return True
    except Exception:
        return False

def say(text, volume=1.0):
    # If you have TTS, call it here; otherwise fallback to chime OK
    ok_wav = os.getenv("OK_WAV", "assets/audio/ok.wav")
    return play(ok_wav, volume)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--error", default=None, help="error message")
    ap.add_argument("--say", default=None, help="speak message")
    ap.add_argument("--volume", default=None, help="0..1")
    args = ap.parse_args()

    vol = float(os.getenv("VOLUME", args.volume or 1.0))
    ok_wav  = os.getenv("OK_WAV",  "assets/audio/ok.wav")
    err_wav = os.getenv("ERR_WAV", "assets/audio/error.wav")

    if args.say is not None:
        say(args.say, vol)
        return 0

    if args.error:
        play(err_wav, vol)
    else:
        play(ok_wav, vol)
    return 0

if __name__ == "__main__":
    sys.exit(main())