#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_voice_commander.py
------------------------------------------------------------
Commander Voice Interface with voice pack support.
• Offline TTS via pyttsx3
• Voice packs from supersonic_voice_packs.py
• speak(text) and speak_event(event) helpers
• CLI: speak arbitrary text, list packs, preview pack

Usage:
  python supersonic_voice_commander.py --say "Build complete"
  python supersonic_voice_commander.py --event success --pack SciFiControl
  python supersonic_voice_commander.py --list
  python supersonic_voice_commander.py --preview --pack IndustrialOps
"""

from __future__ import annotations
import os, re, sys, time, threading, argparse
try:
    import pyttsx3
except Exception:
    pyttsx3 = None
from supersonic_voice_packs import get_pack, list_packs

EVENTS = ("online","start","success","warn","fail","offline","signing","signed","tagging","tagged","release")

def _pick_voice(engine, pref: str | None):
    if not pref or not engine:
        return
    tokens = [t.strip().lower() for t in re.split(r"[|,/]+", pref)]
    try:
        for v in engine.getProperty("voices"):
            name = (v.name or "").lower()
            if any(t in name for t in tokens):
                engine.setProperty("voice", v.id)
                return
    except Exception:
        pass

class VoiceCommander:
    def __init__(self, pack_name: str | None = None):
        self.pack = get_pack(pack_name or os.environ.get("SUP_VOICE_PACK"))
        meta = self.pack["meta"]
        self.engine = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate",   meta.get("rate", 185))
                self.engine.setProperty("volume", meta.get("volume", 1.0))
                _pick_voice(self.engine, meta.get("voice_pref"))
            except Exception as e:
                print(f"⚠️  TTS initialization failed: {e}")
                self.engine = None
        self._lock = threading.Lock()

    def speak(self, text: str):
        if not self.engine:
            print(f"🔊 [TTS disabled] {text}")
            return
        def _run():
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
        threading.Thread(target=_run, daemon=True).start()

    def speak_event(self, event: str):
        phrase = self.pack["phrases"].get(event)
        if not phrase:
            phrase = f"{event.title()}."
        self.speak(phrase)

def _cli():
    ap = argparse.ArgumentParser(description="Supersonic Commander Voice")
    ap.add_argument("--pack", help="Voice pack name", default=os.environ.get("SUP_VOICE_PACK"))
    ap.add_argument("--say", help="Speak literal text")
    ap.add_argument("--event", choices=EVENTS, help="Speak named event")
    ap.add_argument("--list", action="store_true", help="List voice packs")
    ap.add_argument("--preview", action="store_true", help="Preview all core events for a pack")
    args = ap.parse_args()

    if args.list:
        print("Available packs:", ", ".join(list_packs()))
        return

    vc = VoiceCommander(args.pack)

    if args.preview:
        for ev in EVENTS:
            vc.speak_event(ev)
            time.sleep(1.2)
        return

    if args.event:
        vc.speak_event(args.event)
        time.sleep(1.0)
        return

    if args.say:
        vc.speak(args.say)
        time.sleep(max(1.0, len(args.say.split())/3))
        return

    vc.speak_event("online")
    time.sleep(1.0)

if __name__ == "__main__":
    _cli()
