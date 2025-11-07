#!/usr/bin/env python3
"""
Supersonic AI Console (TUI)
Mission control for Supersonic Control Core v4.

Features
- Show current pipeline status (worst of Build & Housekeeping)
- Open Last Known Good (LKG) Pages/Release
- Trigger Build & Release workflow (manual)
- Trigger Housekeeping workflow (manual)
- Force Status Banner (success/failure/cancelled) via repository_dispatch

Requirements
- GitHub CLI (gh) authenticated: `gh auth login`
- Optional: rich (pretty output). Falls back to plain text.
"""
import json, os, subprocess, sys, webbrowser, shutil

BUILD_WF_NAME = "Supersonic v4 — Build & Release"
HOUSE_WF_NAME = "Supersonic — Housekeeping (Pages + Releases)"
BANNER_WF_NAME = "Supersonic — Status Banner"
BUILD_WF_FILE = "release-v4-supersonic.yml"
HOUSE_WF_FILE = "housekeeping-supersonic.yml"

def have(cmd): return shutil.which(cmd) is not None

def run(cmd, check=False, text=True):
    return subprocess.run(cmd, check=check, text=text, capture_output=True)

def gh_json(cmd):
    p = run(cmd)
    if p.returncode != 0 or not p.stdout.strip():
        return None
    return json.loads(p.stdout)

def repo_full():
    p = run(["gh","repo","view","--json","nameWithOwner","--jq",".nameWithOwner"])
    return p.stdout.strip() if p.returncode==0 else ""

def latest_release():
    p = run(["gh","release","list","--limit","1","--json","tagName","--jq","'.[0].tagName'"])
    tag = p.stdout.strip().strip("'") if p.returncode==0 else ""
    return tag if tag!="null" else ""

def pages_url(tag, repo=None):
    if not tag: return ""
    if not repo: repo = repo_full()
    if not repo: return ""
    user, name = repo.split("/")
    return f"https://{user}.github.io/{name}/{tag}/"

def release_url(tag, repo=None):
    if not tag: return ""
    if not repo: repo = repo_full()
    if not repo: return ""
    return f"https://github.com/{repo}/releases/tag/{tag}"

def latest_run_conclusion(wf_name):
    p = run(["gh","run","list","--workflow",wf_name,"--json","name,conclusion,updatedAt","-L","1"])
    if p.returncode!=0 or not p.stdout.strip(): return None
    try:
        arr = json.loads(p.stdout)
        if not arr: return None
        return arr[0]
    except Exception:
        return None

def worst_state(states):
    s = [x for x in states if x]
    if any((x.get("conclusion") or "").lower()=="failure" for x in s): return "failure"
    if any((x.get("conclusion") or "").lower()=="cancelled" for x in s): return "cancelled"
    return "success"

def print_header():
    try:
        from rich.console import Console
        from rich.panel import Panel
        Console().print(Panel.fit("[bold cyan]Supersonic AI Console v4[/]\n[dim]Mission Control[/]"))
    except Exception:
        print("="*60)
        print(" Supersonic AI Console v4 — Mission Control ")
        print("="*60)

def print_status():
    repo = repo_full()
    tag = latest_release()
    build = latest_run_conclusion(BUILD_WF_NAME)
    house = latest_run_conclusion(HOUSE_WF_NAME)
    state = worst_state([build, house])

    try:
        from rich.console import Console
        from rich.table import Table
        c = Console()
        t = Table(title="System Status", show_lines=True)
        t.add_column("Item", style="cyan", no_wrap=True)
        t.add_column("Value")
        t.add_row("Repository", repo or "unknown")
        t.add_row("Last Known Good", tag or "n/a")
        t.add_row("Build (last)", f"{(build or {}).get('conclusion','n/a')} @ {(build or {}).get('updatedAt','')}")
        t.add_row("Housekeeping (last)", f"{(house or {}).get('conclusion','n/a')} @ {(house or {}).get('updatedAt','')}")
        t.add_row("Global State", state)
        c.print(t)
    except Exception:
        print(f"Repository:       {repo or 'unknown'}")
        print(f"Last Known Good:  {tag or 'n/a'}")
        print(f"Build (last):     {(build or {}).get('conclusion','n/a')} @ {(build or {}).get('updatedAt','')}")
        print(f"Housekeeping:     {(house or {}).get('conclusion','n/a')} @ {(house or {}).get('updatedAt','')}")
        print(f"Global State:     {state}")

def open_lkg():
    tag = latest_release()
    if not tag:
        print("⚠️  No releases found."); return
    pu = pages_url(tag); ru = release_url(tag)
    print(f"✅ LKG: {tag}\n🌐 Pages: {pu}\n📦 Release: {ru}")
    try:
        webbrowser.open(pu or ru)
    except Exception:
        os.system(f"open '{pu or ru}' || xdg-open '{pu or ru}' || true")

def dispatch_build(tag_input=None, draft=False, prerelease=False):
    cmd = ["gh","workflow","run",BUILD_WF_FILE]
    if tag_input: cmd += ["-f", f"tag={tag_input}"]
    cmd += ["-f", f"draft={'true' if draft else 'false'}",
            "-f", f"prerelease={'true' if prerelease else 'false'}"]
    print("▶️  Dispatching Build & Release …")
    p = run(cmd)
    print(p.stdout or p.stderr or "done.")

def dispatch_housekeeping(keep=10, dry_run=True, delete_tags=False, include_drafts=False, include_prereleases=True):
    cmd = ["gh","workflow","run",HOUSE_WF_FILE,
           "-f", f"keep={keep}",
           "-f", f"dry_run={'true' if dry_run else 'false'}",
           "-f", f"delete_tags={'true' if delete_tags else 'false'}",
           "-f", f"include_drafts={'true' if include_drafts else 'false'}",
           "-f", f"include_prereleases={'true' if include_prereleases else 'false'}"]
    print("🧹 Dispatching Housekeeping …")
    p = run(cmd); print(p.stdout or p.stderr or "done.")

def force_banner(state):
    state = state.lower().strip()
    if state not in ("success","failure","cancelled"):
        print("State must be one of: success | failure | cancelled"); return
    print(f"🛰️  Forcing Status Banner → {state}")
    p = run([
        "gh","api","repos/:owner/:repo/dispatches",
        "-f","event_type=force-status-banner",
        "-f",f"client_payload={{\"state\":\"{state}\"}}"
    ])
    if p.returncode!=0:
        print("Repository dispatch failed; falling back to direct banner workflow run.")
        run(["gh","workflow","run","status-banner.yml","-f",f"state={state}"])
    else:
        print("OK – banner flip event sent.")

def prompt(msg, default=None):
    s = input(f"{msg} " + (f"[{default}] " if default is not None else "")) or ""
    return s if s else default

def main():
    if not have("gh"):
        print("❌ GitHub CLI (gh) is required. Install & run `gh auth login` first.")
        sys.exit(1)

    while True:
        print_header()
        print("1) Show status")
        print("2) Open Last Known Good (Pages/Release)")
        print("3) Trigger Build & Release")
        print("4) Trigger Housekeeping")
        print("5) Force Status Banner (success/failure/cancelled)")
        print("6) Exit")
        choice = (input("\nSelect > ") or "").strip()

        if choice == "1":
            print_status()
        elif choice == "2":
            open_lkg()
        elif choice == "3":
            tag = prompt("Tag to publish (blank uses latest or none):", "")
            draft = (prompt("Create as draft? (y/N):","N") or "N").lower().startswith("y")
            pre  = (prompt("Mark as prerelease? (y/N):","N") or "N").lower().startswith("y")
            dispatch_build(tag or None, draft=draft, prerelease=pre)
        elif choice == "4":
            keep = int(prompt("Keep how many tags on Pages/Releases?","10"))
            dry  = (prompt("Dry run? (Y/n):","Y") or "Y").lower().startswith("y")
            delg = (prompt("Also delete git tags? (y/N):","N") or "N").lower().startswith("y")
            incd = (prompt("Include drafts? (y/N):","N") or "N").lower().startswith("y")
            incp = (prompt("Include prereleases? (Y/n):","Y") or "Y").lower().startswith("y")
            dispatch_housekeeping(keep=keep, dry_run=dry, delete_tags=delg, include_drafts=incd, include_prereleases=incp)
        elif choice == "5":
            st = prompt("State (success/failure/cancelled):","success")
            force_banner(st)
        elif choice == "6" or (choice or "").lower()=="q":
            print("👋 Exiting Supersonic AI Console.")
            break
        else:
            print("Unknown selection.")
        input("\nPress Enter to continue…")

if __name__ == "__main__":
    main()
