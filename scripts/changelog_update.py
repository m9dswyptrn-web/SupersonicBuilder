#!/usr/bin/env python3
"""
CHANGELOG generator (prev tag -> current tag/HEAD), Conventional-Commit aware
"""
import os, re, subprocess, sys, textwrap
from datetime import datetime

TYPES = [
  ("feat", "✨ Features"),
  ("fix", "🐞 Fixes"),
  ("perf", "⚡ Performance"),
  ("refactor", "♻️ Refactors"),
  ("docs", "📝 Docs"),
  ("build", "🏗️ Build"),
  ("ci", "🧰 CI"),
  ("test", "✅ Tests"),
  ("style", "🎨 Style"),
  ("chore", "🧹 Chore"),
  ("revert", "⏪ Reverts"),
  ("other", "🔧 Other")
]

def run(cmd):
  return subprocess.check_output(cmd, shell=True, text=True).strip()

def repo_slug():
  url = run("git config --get remote.origin.url || true")
  # extract owner/repo
  m = re.search(r'[:/ ]([^/]+/[^/.]+)(?:\.git)?$', url or "")
  return m.group(1) if m else "owner/repo"

def latest_tag_or_none():
  try:
    return run("git describe --tags --abbrev=0 2>/dev/null")
  except subprocess.CalledProcessError:
    return None

def log_between(a, b):
  # format: <sha>||<subject>
  return run(f"git log --pretty=format:'%H||%s' {a}..{b} || true")

def classify(subject):
  # Conventional Commits: type(scope)!: subject
  m = re.match(r'^(\w+)(\([^)]*\))?(!)?:\s*(.*)$', subject)
  if not m:
    return "other", subject
  t = m.group(1).lower()
  rest = m.group(4).strip()
  return (t if t in [k for k,_ in TYPES] else "other"), rest

def short(sha): return sha[:12]

def guess_pr(subject):
  m = re.search(r'\(#(\d+)\)', subject)
  return f" #{m.group(1)}" if m else ""

def build_entry(tag, prev_tag, when, head_sha, slug):
  compare = f"https://github.com/{slug}/compare/{prev_tag}...{tag}" if prev_tag else ""
  title = f"## {tag} — {when}"
  sub = f"[Full Changelog]({compare})" if compare else ""
  return title + ("\n\n" + sub if sub else "")

def main():
  import argparse
  ap = argparse.ArgumentParser()
  ap.add_argument("--new-tag", default=os.environ.get("NEW_TAG",""))
  ap.add_argument("--prev-tag", default="")
  ap.add_argument("--write", action="store_true", help="write into CHANGELOG.md")
  ap.add_argument("--since", default="", help="override prev ref (e.g. v2.0.8)")
  ap.add_argument("--until", default="HEAD", help="override new ref")
  args = ap.parse_args()

  slug = repo_slug()
  now = datetime.utcnow().strftime("%Y-%m-%d")

  new_ref = args.new_tag or args.until or "HEAD"
  prev = args.prev_tag or args.since or latest_tag_or_none()

  if prev:
    rng = f"{prev}..{new_ref}"
  else:
    # first release; include everything
    first_commit = run("git rev-list --max-parents=0 HEAD | tail -n1")
    prev = first_commit
    rng = f"{prev}..{new_ref}"

  raw = log_between(prev, new_ref)
  groups = {k:[] for k,_ in TYPES}
  head_sha = run("git rev-parse HEAD 2>/dev/null || echo unknown")

  for line in raw.splitlines():
    if "||" not in line: continue
    sha, subj = line.split("||",1)
    t, msg = classify(subj)
    pr = guess_pr(subj)
    groups[t].append(f"- {msg} ([{short(sha)}](https://github.com/{slug}/commit/{sha})){pr}")

  # Build markdown
  out = []
  out.append(build_entry(args.new_tag or "Unreleased", prev, now, head_sha, slug))
  out.append("")

  for typ, heading in TYPES:
    if groups[typ]:
      out.append(f"### {heading}\n")
      out.extend(groups[typ])
      out.append("")

  text = "\n".join(out)

  if args.write:
    # Prepend to CHANGELOG.md
    old = ""
    if os.path.exists("CHANGELOG.md"):
      with open("CHANGELOG.md","r",encoding="utf-8") as f:
        old = f.read()
    with open("CHANGELOG.md","w",encoding="utf-8") as f:
      f.write(text)
      f.write("\n---\n\n")
      f.write(old)
    print(f"✅ CHANGELOG.md updated with {args.new_tag or 'Unreleased'}")
  else:
    print(text)

if __name__ == "__main__":
  main()
