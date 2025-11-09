#!/usr/bin/env bash
set -e
python3 -m pip install -r requirements.txt
python3 main.py --clean --build both --dpi 300 --theme both
python3 serve_build.py
