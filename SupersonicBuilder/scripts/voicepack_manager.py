#!/usr/bin/env python3
"""
Downloads and installs new voicepacks or themes for Supersonic Control Core.
"""
import sys, urllib.request, zipfile, tempfile, shutil
from pathlib import Path

ASSETS = Path("assets/audio/voicepacks")

def install(url):
    print(f"Downloading voicepack from {url} ...")
    with tempfile.TemporaryDirectory() as td:
        zip_path = Path(td)/"pack.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(ASSETS)
    print(f"Voicepack installed to {ASSETS}")

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: voicepack_manager.py <zip_url>")
        sys.exit(0)
    install(sys.argv[1])
