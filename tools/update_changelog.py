#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION_FILE = ROOT / "VERSION"
REPO_URL = os.environ.get("REPO_URL")

CONV_RE = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<desc>.+)")
BREAKING_RE = re.compile(r"BREAKING CHANGES?:", re.IGNORECASE)

GROUP_ORDER = [
    "feat", "fix", "perf", "refactor", "deps", "docs", "test", "build", "ci", "chore", "style"
]
GROUP_TITLES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "refactor": "Refactoring",
    "deps": "Dependencies",
    "docs": "Documentation",
    "test": "Tests",
    "build": "Build System",
    "ci": "CI",
    "chore": "Chores",
    "style": "Style",
    "breaking": "BREAKING CHANGES"
}

def sh(args: List[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def latest_tag() -> str:
    try:
        return sh(["git", "describe", "--tags", "--abbrev=0"])
    except subprocess.CalledProcessError:
        return ""

def default_version() -> str:
    if VERSION_FILE.exists():
        v = VERSION_FILE.read_text().strip()
        if v:
            return v
    tag = latest_tag()
    return tag if tag else "v0.1.0"

def git_commits(from_ref: str) -> List[Tuple[str, str]]:
    range_arg = f"{from_ref}..HEAD" if from_ref else "HEAD"
    fmt = "%H%n%s%n%b%n--END--"
    out = sh(["git", "log", "--no-merges", f"--format={fmt}", range_arg])
    chunks = [c for c in out.split("--END--") if c.strip()]
    commits = []
    for ch in chunks:
        lines = [l for l in ch.splitlines()]
        if not lines: 
            continue
        sha = lines[0].strip()
        msg = "\n".join(lines[1:]).strip()
        commits.append((sha, msg))
    return commits

def parse_commit(msg: str) -> Dict:
    lines = msg.splitlines()
    subject = lines[0] if lines else ""
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""
    m = CONV_RE.match(subject)
    item = {
        "type": None, "scope": None, "desc": subject, "breaking": False, "subject": subject, "body": body
    }
    if m:
        item["type"] = (m.group("type") or "").lower()
        item["scope"] = m.group("scope")
        item["desc"] = m.group("desc").strip()
        item["breaking"] = bool(m.group("bang"))
    if BREAKING_RE.search(body):
        item["breaking"] = True
    if item["type"] in {"dependency", "deps"}:
        item["type"] = "deps"
    return item

def group_commits(commits: List[Tuple[str, str]]) -> Dict[str, List[Dict]]:
    groups: Dict[str, List[Dict]] = {k: [] for k in GROUP_ORDER}
    groups["breaking"] = []
    for sha, raw in commits:
        meta = parse_commit(raw)
        meta["sha"] = sha
        if meta["breaking"]:
            groups["breaking"].append(meta)
        t = meta["type"] or "chore"
        groups.setdefault(t, []).append(meta)
    return {k: v for k, v in groups.items() if v}

def compare_link(prev: str, new: str) -> str:
    if not REPO_URL:
        return ""
    if prev:
        return f"[Compare]({REPO_URL}/compare/{prev}...{new})"
    else:
        return f"[Commits]({REPO_URL}/commits/{new})"

def short_sha(sha: str) -> str:
    return sha[:7]

def render_section(version: str, prev_tag: str, grouped: Dict[str, List[Dict]]) -> str:
    today = dt.date.today().isoformat()
    compare = compare_link(prev_tag, version)
    header = f"## {version} — {today}" + (f" · {compare}" if compare else "")
    lines = [header, ""]
    if "breaking" in grouped:
        lines.append(f"### {GROUP_TITLES['breaking']}")
        for c in grouped["breaking"]:
            scope = f"**{c['scope']}**: " if c.get("scope") else ""
            lines.append(f"- {scope}{c['desc']}")
        lines.append("")
    for g in GROUP_ORDER:
        if g not in grouped: 
            continue
        title = GROUP_TITLES.get(g, g.title())
        lines.append(f"### {title}")
        for c in grouped[g]:
            scope = f"**{c['scope']}**: " if c.get("scope") else ""
            lines.append(f"- {scope}{c['desc']} ({short_sha(c['sha'])})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n\n"

def insert_or_prepend_changelog(new_section: str):
    if CHANGELOG.exists():
        current = CHANGELOG.read_text(encoding="utf-8")
        if current.startswith("# Changelog"):
            parts = current.splitlines()
            try:
                first_sub = next(i for i, ln in enumerate(parts) if ln.startswith("## "))
                head = "\n".join(parts[:first_sub]).rstrip() + "\n\n"
                rest = "\n".join(parts[first_sub:])
                CHANGELOG.write_text(head + new_section + rest, encoding="utf-8")
            except StopIteration:
                CHANGELOG.write_text(current.rstrip() + "\n\n" + new_section, encoding="utf-8")
        else:
            CHANGELOG.write_text(new_section + current, encoding="utf-8")
    else:
        CHANGELOG.write_text("# Changelog\n\n" + new_section, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Update CHANGELOG from git history.")
    ap.add_argument("--version", help="release tag (e.g., v1.0.1). Defaults to VERSION file or latest tag")
    ap.add_argument("--from-tag", help="override the starting tag for the log range")
    args = ap.parse_args()

    version = args.version or default_version()
    prev = args.from_tag if args.from_tag is not None else latest_tag()
    if prev == version:
        try:
            tags = sh(["git", "tag", "--sort=-creatordate"]).splitlines()
            later = tags.index(version)
            prev = tags[later+1] if later + 1 < len(tags) else ""
        except Exception:
            prev = ""

    commits = git_commits(prev)
    if not commits:
        print("No new commits to include.")
        return

    grouped = group_commits(commits)
    section = render_section(version, prev, grouped)
    insert_or_prepend_changelog(section)

    counts = {k: len(v) for k, v in grouped.items()}
    summary = ", ".join(f"{k}:{v}" for k, v in counts.items())
    print(f"CHANGELOG updated for {version} ({summary}) → {CHANGELOG}")

if __name__ == "__main__":
    main()
