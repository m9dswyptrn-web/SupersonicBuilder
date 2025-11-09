#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_settings.py
------------------------------------------------------------
Centralized settings loader for Supersonic Commander.
Reads supersonic_settings.json and exposes values safely.
"""

import json
from pathlib import Path

SETTINGS_FILE = Path("supersonic_settings.json")

DEFAULTS = {
    "voice_pack": "FlightOps",
    "volume": 1.0,
    "rate": 185,
    "dashboard_auto_refresh": True,
    "telemetry_interval_sec": 30,
    "theme": "dark",
    "show_changelog_cards": True,
}

def load_settings() -> dict:
    data = DEFAULTS.copy()
    if SETTINGS_FILE.exists():
        try:
            with SETTINGS_FILE.open(encoding="utf-8") as f:
                raw = json.load(f)
            data.update(raw)
        except Exception as e:
            print(f"⚠️  Could not read {SETTINGS_FILE}: {e}")
    return data

def save_settings(cfg: dict):
    SETTINGS_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
