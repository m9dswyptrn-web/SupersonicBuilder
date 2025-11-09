#!/usr/bin/env python3
import argparse, subprocess, os
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def git_commit_hash(full=False):
    try:
        cmd = ['git','rev-parse','HEAD'] if full else ['git','rev-parse','--short','HEAD']
        out = subprocess.check_output(cmd).decode().strip()
        return out
    except Exception:
        return 'no-git'

ap = argparse.ArgumentParser()
ap.add_argument('--main', required=True)
ap.add_argument('--appendix', required=True)
ap.add_argument('--out-dir', default='out')
ap.add_argument('--commit', help='Commit hash (default: auto-detect short hash)')
A = ap.parse_args()

Path(A.out_dir).mkdir(parents=True, exist_ok=True)

# Use provided commit or detect from git
commit = A.commit if A.commit else git_commit_hash(full=False)

# Check for GitHub Actions environment variable (full SHA)
if not A.commit and os.getenv('GITHUB_SHA'):
    commit = os.getenv('GITHUB_SHA')

outname = Path(A.out_dir) / f"SonicBuilder_Manual_with_Appendix_{commit}.pdf"

w = PdfWriter()
for src in (A.main, A.appendix):
    if not Path(src).exists():
        print(f"Warning: {src} not found, skipping")
        continue
    r = PdfReader(src)
    for p in r.pages:
        w.add_page(p)

with open(outname, 'wb') as f:
    w.write(f)

print('Merged ->', outname)
