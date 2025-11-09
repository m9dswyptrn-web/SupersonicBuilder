#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_voice_packs.py
------------------------------------------------------------
Configurable voice packs for Supersonic Commander.
Each pack defines TTS defaults + event phrases.
"""

VOICE_PACKS = {
    "FlightOps": {
        "meta": {"rate": 185, "volume": 1.0, "voice_pref": "female"},
        "phrases": {
            "online":  "Flight Ops online. Systems green.",
            "start":   "Pre-flight checks complete. Ignition.",
            "success": "Mission complete. All systems nominal.",
            "warn":    "Caution. Anomaly detected. Review advisories.",
            "fail":    "Abort. Mission failed verification.",
            "offline": "Flight Ops standing by.",
            "signing": "Authenticity signing in progress.",
            "signed":  "Signature complete. Identity verified.",
            "tagging": "Applying release tag.",
            "tagged":  "Release tag confirmed.",
            "release": "Package released. Ready for deployment.",
            "rollback": "Rollback complete. System restored.",
        },
    },
    "SciFiControl": {
        "meta": {"rate": 170, "volume": 0.95, "voice_pref": "Zira|Samantha|Google US"},
        "phrases": {
            "online":  "Control nexus online.",
            "start":   "Compilation lattice engaged.",
            "success": "Operation complete. Integrity affirmed.",
            "warn":    "Advisory. Non-fatal deviations present.",
            "fail":    "Critical fault. Integrity breach detected.",
            "offline": "Nexus offline.",
            "signing": "Initiating cryptographic attestation.",
            "signed":  "Attestation complete. Trust anchor locked.",
            "tagging": "Version anchor requested.",
            "tagged":  "Version anchor secured.",
            "release": "Distribution channel open. Release propagated.",
            "rollback": "State restored to last checkpoint.",
        },
    },
    "IndustrialOps": {
        "meta": {"rate": 160, "volume": 1.0, "voice_pref": "male|David|Alex"},
        "phrases": {
            "online":  "Industrial Ops ready.",
            "start":   "Spin-up sequence started.",
            "success": "Job finished. Output verified.",
            "warn":    "Heads up. Check the logs.",
            "fail":    "Stop work. Build failed checks.",
            "offline": "Industrial Ops idle.",
            "signing": "Signing artifacts.",
            "signed":  "Signature applied.",
            "tagging": "Tagging version.",
            "tagged":  "Tag recorded.",
            "release": "Release published.",
            "rollback": "Rollback finished. Previous version live.",
        },
    },
    "ArcadeHUD": {
        "meta": {"rate": 190, "volume": 1.0, "voice_pref": "Samantha|Zira|Alex|David"},
        "phrases": {
            "online":  "Player one ready.",
            "start":   "Level start — good luck!",
            "success": "Stage clear! High score!",
            "warn":    "Caution — bonus time running low.",
            "fail":    "Game over — insert coin to retry.",
            "offline": "Arcade idle. Press start.",
            "signing": "Authenticity power-up engaged.",
            "signed":  "Epic! Signature unlocked.",
            "tagging": "New level tag incoming.",
            "tagged":  "Level tag locked in.",
            "release": "Drop complete — claim your loot.",
            "rollback": "Rewind complete. Back in the fight.",
        },
    },
}

DEFAULT_PACK = "FlightOps"

def get_pack(name: str | None) -> dict:
    if not name:
        name = DEFAULT_PACK
    return VOICE_PACKS.get(name, VOICE_PACKS[DEFAULT_PACK])

def list_packs() -> list[str]:
    return sorted(VOICE_PACKS.keys())
