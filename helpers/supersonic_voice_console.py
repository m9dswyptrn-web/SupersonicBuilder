#!/usr/bin/env python3
import os, platform, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "audio"
VOICE_PACK  = os.getenv("VOICE_PACK","commander")
VOICE_EVENT = os.getenv("VOICE_EVENT","build_start")
QUIET = os.getenv("QUIET","0")=="1"

def find_wav():
    candidates=[
        ASSETS / "voicepacks" / VOICE_PACK / f"{VOICE_EVENT}.wav",
        ASSETS / "flightops" / f"{VOICE_EVENT}.wav",
    ]
    for p in candidates:
        if p.exists(): return p
    return None

def tts_fallback(line):
    try:
        import pyttsx3
        e=pyttsx3.init(); e.setProperty("rate", 175); e.say(line); e.runAndWait()
    except Exception:
        print(f"[voice-tts] {line}")

def play(fp):
    sysname=platform.system().lower()
    cmds=[]
    if "darwin" in sysname: cmds=[["afplay", str(fp)]]
    elif "linux" in sysname: cmds=[["aplay", str(fp)], ["paplay", str(fp)], ["ffplay","-nodisp","-autoexit", str(fp)]]
    for cmd in cmds:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return True
        except Exception:
            continue
    return False

def say(event=None, pack=None, tts_line=None):
    global VOICE_EVENT, VOICE_PACK
    if event: VOICE_EVENT=event
    if pack: VOICE_PACK=pack
    fp=find_wav()
    if QUIET:
        print(f"[voice] {VOICE_PACK}/{VOICE_EVENT} (quiet)"); return
    if fp and play(fp):
        print(f"[voice] {VOICE_PACK}/{VOICE_EVENT} -> {fp}")
    else:
        tts_fallback(tts_line or f"{VOICE_PACK} {VOICE_EVENT}")

if __name__=="__main__":
    say()
