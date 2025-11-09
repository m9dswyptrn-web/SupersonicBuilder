#!/usr/bin/env python3
import subprocess, sys, os, re, textwrap, datetime, json, pathlib

def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def latest_tag():
    try:
        return sh("git describe --tags --abbrev=0")
    except subprocess.CalledProcessError:
        return None

def commit_range(prev_tag, new_tag=None):
    if prev_tag:
        rng = f"{prev_tag}..HEAD"
    else:
        # repo start
        rng = "--since='3 years ago'"
    return rng

def commits(rng):
    fmt = r"%h|%ad|%an|%s"
    try:
        out = sh(f"git log {rng} --date=short --pretty=format:'{fmt}'")
    except subprocess.CalledProcessError:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            rows.append({"hash":parts[0], "date":parts[1], "author":parts[2], "subject":parts[3]})
    return rows

def categorize(subject):
    s = subject.lower()
    if s.startswith(("feat:", "feature:", "feat(")): return "Features"
    if s.startswith(("fix:", "hotfix:", "bug:", "chore(fix)")): return "Fixes"
    if s.startswith(("docs:", "doc:")): return "Docs"
    if s.startswith(("perf:",)): return "Performance"
    if s.startswith(("refactor:", "refactor(")): return "Refactor"
    if s.startswith(("ci:", "chore(ci)", "workflow:")): return "CI"
    if s.startswith(("chore:", "build:", "deps:", "style:", "test:")): return "Chore"
    return "Other"

def render_markdown(tag, since_tag, rows):
    dt = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    groups = {}
    for r in rows:
        g = categorize(r["subject"])
        groups.setdefault(g, []).append(r)

    lines = []
    lines.append(f"# {tag}")
    lines.append("")
    lines.append(f"_Date: {dt}_")
    if since_tag:
        lines.append(f"_Changes since **{since_tag}**_")
    else:
        lines.append("_Initial release notes_")
    lines.append("")
    order = ["Features","Fixes","Docs","Performance","Refactor","CI","Chore","Other"]
    for k in order:
        if k in groups:
            lines.append(f"## {k}")
            for r in groups[k]:
                lines.append(f"- {r['subject']}  \n  — `{r['hash']}` · {r['author']} · {r['date']}")
            lines.append("")
    if not rows:
        lines.append("> No commit messages found for this range. Add details manually.")
    return "\n".join(lines)

def main():
    new_tag = os.environ.get("NEW_TAG","v2.0.10").strip() or "v2.0.10"
    prev = latest_tag()
    rng = commit_range(prev, new_tag)
    rows = commits(rng)
    md = render_markdown(new_tag, prev, rows)
    out_dir = pathlib.Path("RELEASE_NOTES"); out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{new_tag}.md"
    path.write_text(md, encoding="utf-8")
    print(str(path))

if __name__ == "__main__":
    main()
