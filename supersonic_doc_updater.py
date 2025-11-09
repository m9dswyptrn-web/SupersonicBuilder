#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_doc_updater.py
------------------------------------------------------------
AI (or fallback) changelog generator for Supersonic Commander.

What it does
------------
• Collects recent git changes (since last tag or last 1 day).
• Summarizes changes (OpenAI if OPENAI_API_KEY set; else regex fallback).
• Writes:
    SonicBuilder/docs/changelog/CHANGELOG.md       (rolling)
    SonicBuilder/docs/changelog/changes_<ts>.md    (snapshot)
    SonicBuilder/docs/changelog/changes_<ts>.html  (dashboard card)

Usage
-----
python supersonic_doc_updater.py              # autodetect window
python supersonic_doc_updater.py --since v3.4.1
python supersonic_doc_updater.py --range v3.4.1..HEAD

Requirements
------------
• git available in PATH
• Optional: pip install openai (only if you want LLM summaries)
"""

from __future__ import annotations
import os, re, subprocess, json, argparse
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(".")
OUTDIR = Path("SonicBuilder/docs/changelog"); OUTDIR.mkdir(parents=True, exist_ok=True)
CHANGELOG = OUTDIR / "CHANGELOG.md"

def _sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()

def git_range_auto() -> str:
    """Prefer last tag..HEAD, else last 1 day."""
    try:
        last_tag = _sh(["git", "describe", "--tags", "--abbrev=0"])
        return f"{last_tag}..HEAD"
    except Exception:
        since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        return f'--since="{since}"'

def git_log_text(rng: str) -> str:
    try:
        if ".." in rng:
            return _sh(["git", "log", "--no-merges", "--name-status", "--date=iso", "--pretty=format:%h %ad %an %s", rng])
        if rng.startswith("--since="):
            return _sh(["git", "log", "--no-merges", "--name-status", "--date=iso", "--pretty=format:%h %ad %an %s", rng])
        return _sh(["git", "log", "--no-merges", "--name-status", "--date=iso", "--pretty=format:%h %ad %an %s", f"--since={rng}"])
    except Exception:
        return ""

def fallback_summary(log_text: str) -> str:
    if not log_text.strip():
        return "No changes detected."
    added = len(re.findall(r"^A\t", log_text, flags=re.M))
    modified = len(re.findall(r"^M\t", log_text, flags=re.M))
    removed = len(re.findall(r"^D\t", log_text, flags=re.M))
    py_files = len(re.findall(r"\.py$", log_text, flags=re.M))
    pdfs = len(re.findall(r"\.pdf$", log_text, flags=re.M))
    svg_png = len(re.findall(r"\.(svg|png)$", log_text, flags=re.M))
    lines = [
        f"Changes: {added} added, {modified} modified, {removed} removed.",
        f"Touched: {py_files} Python files, {pdfs} PDFs, {svg_png} images.",
        "Summary generated without AI (fallback mode)."
    ]
    return " ".join(lines)

def ai_summary(log_text: str) -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return fallback_summary(log_text)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        prompt = (
            "You are a release notes generator for a technical build system. "
            "Summarize these git logs into concise, scannable bullet points with short headers. "
            "Group by feature area when obvious. Keep it within 8 bullets max. "
            "Prefer active voice. Include any user-facing changes, new artifacts, or CI/Docs changes.\n\n"
            f"LOGS:\n{log_text[:120000]}\n"
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Concise release notes writer."},
                      {"role":"user","content": prompt}],
            temperature=0.2,
            max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return fallback_summary(log_text)

def write_outputs(summary_md: str, rng_used: str, log_excerpt: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    snap_name = OUTDIR / f"changes_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    html_name = OUTDIR / f"changes_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"

    header = f"## {ts} — Range: `{rng_used}`\n\n"
    block = header + summary_md.strip() + "\n\n<details><summary>Raw log excerpt</summary>\n\n```\n" + log_excerpt[:4000] + "\n```\n</details>\n\n---\n"

    snap_name.write_text(block, encoding="utf-8")

    if CHANGELOG.exists():
        existing = CHANGELOG.read_text(encoding="utf-8")
    else:
        existing = "# Supersonic Changelog\n\n"
    CHANGELOG.write_text(existing + block, encoding="utf-8")

    summary_html = summary_md.replace('\n', '<br>')
    html_card = f"""<!doctype html><meta charset="utf-8">
<style>
body{{background:#0d0d0d;color:#e0e0e0;font-family:Segoe UI,Roboto,Arial,sans-serif;padding:16px}}
.card{{background:#1b1b1b;border:1px solid #00ffff44;border-radius:10px;padding:14px;max-width:900px}}
h3{{color:#00ffff;margin:.2em 0}}
small{{color:#aaa}}
pre{{white-space:pre-wrap;background:#111;padding:8px;border-radius:8px;border:1px solid #00ffff22}}
</style>
<div class="card">
  <h3>Supersonic Release Notes</h3>
  <small>{ts} — {rng_used}</small>
  <div>{summary_html}</div>
</div>
"""
    html_name.write_text(html_card, encoding="utf-8")

    print(f"📝 Changelog updated → {CHANGELOG}")
    print(f"🧾 Snapshot → {snap_name}")
    print(f"🖼  HTML card → {html_name}")

def main():
    ap = argparse.ArgumentParser(description="Supersonic AI Doc Updater")
    ap.add_argument("--since", help="Generate notes since <ref/date> (e.g., v3.4.1 or 2025-01-20)")
    ap.add_argument("--range", dest="range_", help="Explicit git range like v3.4.1..HEAD")
    args = ap.parse_args()

    rng = args.range_ or (f"--since={args.since}" if args.since else git_range_auto())

    logs = git_log_text(rng)
    summary = ai_summary(logs)
    if not re.search(r"^\s*[-*•]", summary, flags=re.M):
        summary = "- " + summary.replace("\n", "\n- ")

    write_outputs(summary, rng, logs)

if __name__ == "__main__":
    main()
