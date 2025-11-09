#!/usr/bin/env python3
import os, sys, json, time, subprocess
print("[*] SonicBuilder OTG Diagnostics")
cands = [f for f in os.listdir('/dev') if f.startswith(('ttyACM','ttyUSB'))] if os.path.isdir('/dev') else []
print("Candidates:", ", ".join(('/dev/'+c for c in cands)) if cands else "none")
print("[*] Done.")
