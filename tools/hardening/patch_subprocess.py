#!/usr/bin/env python3
"""
Subprocess hardening helper.

- Dry-run:  python3 tools/hardening/patch_subprocess.py --check
- Apply:    python3 tools/hardening/patch_subprocess.py --apply

The script makes conservative changes:
 - replaces explicit "shell=True" with "shell=False" where safe
 - converts simple quoted string commands to argv lists (best-effort)
 - writes .bak backups for files it changes
"""
from __future__ import annotations
import re, sys, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
SKIP_DIRS = {".git", "venv", ".venv", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache", ".ruff_cache"}

TARGET_FUNCS = ("subprocess.call", "subprocess.check_call", "subprocess.run", "subprocess.check_output")

STRING_CMD_RE = re.compile(
    r'(?P<prefix>\\bsubprocess\\.(?:call|check_call|run|check_output)\\s*\\()\\s*' +
    r'(?P<cmd>(?:\'[^\']*\'|\\"[^\\"]*\\") )\\s*(?P<rest>[^)]*\\))',
    re.VERBOSE | re.DOTALL
)

SHELL_TRUE_RE = re.compile(r"\\bshell\\s*=\\s*True\\b")

def py_files():
    for p in ROOT.rglob("*.py"):
        parts = set(p.parts)
        if parts & SKIP_DIRS:
            continue
        yield p

def harden_text(src: str, relpath: str, apply: bool):
    modified = 0
    text = src

    # 1) shell=True -> shell=False
    def shell_fix(m):
        nonlocal modified
        modified += 1
        return m.group(0).replace("shell=True", "shell=False")

    text, n1 = SHELL_TRUE_RE.subn(shell_fix, text)

    # 2) simple string command -> argv list (best-effort)
    def str_to_argv(m):
        nonlocal modified
        prefix = m.group('prefix')
        cmd_quoted = m.group('cmd').strip()
        rest = m.group('rest')
        cmd = cmd_quoted[1:-1].strip()
        if not cmd or " " not in cmd:
            return m.group(0)
        argv = [s for s in cmd.split(" ") if s]
        modified += 1
        return f"{prefix}{argv!r}{rest}"

    text, n2 = STRING_CMD_RE.subn(str_to_argv, text)

    if apply and (n1 or n2):
        return text, n1 + n2
    return text, n1 + n2

def process_file(path, apply):
    src = path.read_text(encoding="utf-8", errors="ignore")
    new_src, changed = harden_text(src, str(path), apply)
    if changed and apply:
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            bak.write_text(src, encoding="utf-8")
        path.write_text(new_src, encoding="utf-8")
    return changed

def main():
    apply = "--apply" in sys.argv
    total_changed = 0
    files = []
    for p in py_files():
        c = process_file(p, apply)
        if c:
            total_changed += c
            files.append(str(p))
            if not apply:
                print(f"WOULD PATCH {p} ({c} change(s))")
    print(json.dumps({"files_with_changes": files, "total_changes": total_changed}, indent=2))
    if apply:
        print("Applied changes and wrote backups as *.py.bak")

if __name__ == "__main__":
    main()
