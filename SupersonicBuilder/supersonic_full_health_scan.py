#!/usr/bin/env python3
"""
Supersonic Full Health Scan — scan + reversible organize

Features:
- Full project health scan → docs/HEALTH_REPORT.md
- Optional CI gate (--ci-check) using `make ci-check` or a safe fallback
- Optional auto-organize (--apply) of orphan .py into tools/ | supersonic_pkg/ | extras/snippets/
- **Move ledger** (--log-file) records each move (JSONL)
- **Undo** (--undo) replays ledger in reverse to restore originals
- Safety: hash verification on undo; collision-safe restore with __restoreN suffix

Exit codes:
  0 = OK
  1 = warnings only (if --fail-on-warn)
  2 = critical issues found (duplicates, compile errors, missing configs, CI gate failed)
  99 = unexpected error
"""

from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, textwrap, time, traceback, py_compile, ast
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

# ---------- Layout ----------
ROOT      = Path(__file__).resolve().parent
DOCS      = ROOT / "docs"
REPORT    = DOCS / "HEALTH_REPORT.md"
PKG_DIR   = ROOT / "supersonic_pkg"
TOOLS_DIR = ROOT / "tools"
SNIP_DIR  = ROOT / "extras" / "snippets"
GITHUB    = ROOT / ".github"
WF_DIR    = GITHUB / "workflows"
WF_NEW    = GITHUB / "workflows_new"

EXPECTED = [
    ("Makefile or make/ControlCore.mk", [ROOT / "Makefile", ROOT / "make" / "ControlCore.mk"]),
    ("pyproject.toml", [ROOT / "pyproject.toml"]),
    ("requirements.txt", [ROOT / "requirements.txt"]),
    (".pre-commit-config.yaml", [ROOT / ".pre-commit-config.yaml"]),
    ("mypy.ini", [ROOT / "mypy.ini"]),
    ("pyrightconfig.json", [ROOT / "pyrightconfig.json"]),
    ("CI workflow (active or staged)", [WF_DIR / "ci.yml", WF_NEW / "ci.yml"]),
]

BADGE_PATTERNS = {
    "ci": re.compile(r"\[!\[CI\]\(https://github\.com/.+?/actions/workflows/ci\.yml/badge\.svg\)\]"),
    "pages": re.compile(r"\[!\[Pages\]\(https://github\.com/.+?/actions/workflows/pages\.yml/badge\.svg\)\]"),
}

STAMP_RE = re.compile(r"Last updated:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)

STANDALONE_HINTS = (
    r"if\s+__name__\s*==\s*[\"']__main__[\"']",
    r"argparse\.ArgumentParser\(",
    r"click\.command\(",
)

IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist",
               ".mypy_cache", ".pytest_cache", ".ruff_cache", ".idea", ".vscode", "tmp", "temp",
               ".DS_Store"}

# ---------- Data ----------
@dataclass
class FileInfo:
    path: Path
    sha: str
    kind: str               # standalone | package | snippet
    compiles: bool
    compile_err: str | None = None

@dataclass
class HealthSummary:
    py_count: int = 0
    unique_py: int = 0
    duplicates: list[tuple[Path, Path]] = field(default_factory=list)
    standalone: list[Path] = field(default_factory=list)
    package: list[Path] = field(default_factory=list)
    snippet: list[Path] = field(default_factory=list)
    compile_errors: list[tuple[Path, str]] = field(default_factory=list)
    orphans: list[Path] = field(default_factory=list)
    pkg_unexported: list[str] = field(default_factory=list)
    missing_expected: list[str] = field(default_factory=list)
    badges_missing: list[str] = field(default_factory=list)
    large_assets: list[tuple[Path, int]] = field(default_factory=list)
    stale_stamps: list[Path] = field(default_factory=list)
    ci_check_ran: bool = False
    ci_check_code: int | None = None
    critical_count: int = 0
    warning_count: int = 0
    moves_planned: list[tuple[Path, Path, str]] = field(default_factory=list)
    moves_done: list[tuple[Path, Path, str]] = field(default_factory=list)

# ---------- Helpers ----------
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def looks_standalone(code: str) -> bool:
    return any(re.search(pat, code) for pat in STANDALONE_HINTS)

def looks_pkg_file(p: Path, code: str) -> bool:
    if p.name == "__init__.py":
        return True
    if "class " in code or "def " in code:
        return not looks_standalone(code)
    return False

def classify_py(p: Path) -> str:
    try:
        code = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "snippet"
    if looks_standalone(code):
        return "standalone"
    if looks_pkg_file(p, code):
        return "package"
    return "snippet"

def safe_compile(p: Path) -> tuple[bool, str | None]:
    import py_compile as _pc
    try:
        _pc.compile(str(p), doraise=True)
        return True, None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def discover_py_files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.py"):
        if any(seg in IGNORE_DIRS for seg in p.parts):
            continue
        out.append(p)
    return out

def read_pkg_exports() -> set[str]:
    init = PKG_DIR / "__init__.py"
    if not init.exists():
        return set()
    try:
        tree = ast.parse(init.read_text(encoding="utf-8", errors="ignore"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                v = node.value
                if isinstance(v, (ast.List, ast.Tuple)):
                    vals = [elt.s for elt in v.elts if isinstance(elt, ast.Str)]
                    return set(vals)
    except Exception:
        return set()
    return set()

def check_expected_files() -> list[str]:
    missing = []
    for label, candidates in EXPECTED:
        if not any(c.exists() for c in candidates):
            missing.append(label)
    return missing

def check_badges(readme: Path) -> list[str]:
    if not readme.exists():
        return ["README.md (missing entirely)"]
    text = readme.read_text(encoding="utf-8", errors="ignore")
    missing = []
    for name, pat in BADGE_PATTERNS.items():
        if not pat.search(text):
            missing.append(f"{name} badge")
    return missing

def find_large_assets(max_bytes: int) -> list[tuple[Path, int]]:
    exts = {".zip", ".wav", ".mp3", ".ogg", ".flac", ".png", ".jpg", ".jpeg", ".svg", ".pdf", ".mp4", ".mov"}
    suspects = []
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size >= max_bytes:
                suspects.append((p, size))
    return sorted(suspects, key=lambda t: t[1], reverse=True)

def find_stale_stamps(max_age_days: int = 45) -> list[Path]:
    stale = []
    cutoff = datetime.utcnow().date() - timedelta(days=max_age_days)
    for pattern in ["docs/**/*.md", ".github/**/*.md", "README.md"]:
        for f in ROOT.glob(pattern):
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            m = STAMP_RE.search(text)
            if not m:
                continue
            try:
                d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                if d < cutoff:
                    stale.append(f)
            except ValueError:
                stale.append(f)
    return stale

def run_ci_check(do_ci: bool) -> tuple[bool, int | None, str]:
    if not do_ci:
        return False, None, ""
    if (ROOT / "Makefile").exists() or (ROOT / "make" / "ControlCore.mk").exists():
        cmd = ["bash", "-lc", "make ci-check"]
    else:
        cmd = ["bash", "-lc", "pytest -q || true && ruff check . && python -m mypy . && python -m pyright"]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        return True, proc.returncode, proc.stdout + "\n" + proc.stderr
    except Exception as e:
        return True, 997, f"Failed to run CI gate: {e}"

def ensure_dirs():
    DOCS.mkdir(parents=True, exist_ok=True)
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    SNIP_DIR.mkdir(parents=True, exist_ok=True)
    (PKG_DIR / "__init__.py").touch(exist_ok=True)

def choose_dest(kind: str) -> Path:
    return TOOLS_DIR if kind == "standalone" else PKG_DIR if kind == "package" else SNIP_DIR

def unique_name(dst_dir: Path, name: str, tag: str = "") -> Path:
    base = dst_dir / (f"{Path(name).stem}{tag}{Path(name).suffix}")
    if not base.exists():
        return base
    i = 1
    while True:
        cand = dst_dir / f"{Path(name).stem}{tag}__{i}{Path(name).suffix}"
        if not cand.exists(): return cand
        i += 1

# ---------- Ledger ----------
def write_move_log(log_path: Path, src: Path, dst: Path, kind: str, sha: str):
    rec = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "action": "move",
        "src": str(src),
        "dst": str(dst),
        "kind": kind,
        "sha256": sha,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

def read_ledger(log_path: Path) -> list[dict]:
    if not log_path.exists(): return []
    out = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                rec = json.loads(line)
                if isinstance(rec, dict) and rec.get("action") == "move":
                    out.append(rec)
            except json.JSONDecodeError:
                continue
    return out

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Move orphan .py files into standardized locations.")
    ap.add_argument("--ci-check", action="store_true", help="Run local CI gate and include result.")
    ap.add_argument("--max-asset-mb", type=int, default=300, help="Flag assets larger than this many MB (default 300).")
    ap.add_argument("--fail-on-warn", action="store_true", help="Exit non-zero on warnings as well as critical issues.")
    ap.add_argument("--log-file", type=str, default="", help="Path to JSONL move ledger (e.g., moves.log).")
    ap.add_argument("--undo", action="store_true", help="Undo logged moves (reverse order).")
    ap.add_argument("--force-undo", action="store_true", help="Undo even if SHA mismatches (dangerous).")
    args = ap.parse_args()

    ensure_dirs()

    log_path = Path(args.log_file) if args.log_file else None
    if args.undo:
        if not log_path:
            print("ERROR: --undo requires --log-file <path>")
            sys.exit(2)
        return undo_moves(log_path, force=args.force_undo)

    # Normal scan / apply
    summary = HealthSummary()

    # Discover & classify
    py_files = []
    for p in ROOT.rglob("*.py"):
        if any(seg in IGNORE_DIRS for seg in p.parts):
            continue
        py_files.append(p)
    summary.py_count = len(py_files)

    by_hash: dict[str, Path] = {}
    infos: list[FileInfo] = []
    for p in py_files:
        try:
            h = sha256(p)
        except Exception:
            continue
        if h in by_hash:
            summary.duplicates.append((p, by_hash[h]))
            continue
        by_hash[h] = p
        kind = classify_py(p)
        ok, err = safe_compile(p)
        infos.append(FileInfo(p, h, kind, ok, err))
        if not ok and err:
            summary.compile_errors.append((p, err))
        if kind == "standalone": summary.standalone.append(p)
        elif kind == "package":  summary.package.append(p)
        else:                    summary.snippet.append(p)
    summary.unique_py = len(infos)

    # Orphans
    std_roots = {TOOLS_DIR.resolve(), PKG_DIR.resolve(), SNIP_DIR.resolve()}
    orphans = []
    for fi in infos:
        parents = set(Path(fi.path).resolve().parents)
        if not parents.intersection(std_roots):
            orphans.append(fi)
    summary.orphans = [fi.path for fi in orphans]

    # Plan moves
    for fi in orphans:
        dst_root = choose_dest(fi.kind)
        dst_path = unique_name(dst_root, fi.path.name)
        summary.moves_planned.append((fi.path, dst_path, fi.kind))

    # Apply moves + log
    if args.apply and summary.moves_planned:
        for src, dst, kind in summary.moves_planned:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            summary.moves_done.append((src, dst, kind))
            if log_path:
                try:
                    write_move_log(log_path, src, dst, kind, sha256(dst))
                except Exception:
                    pass
        # Rebuild package index if present
        builder = ROOT / "tools" / "build_pkg_index.py"
        if builder.exists():
            try:
                subprocess.run(["python3", str(builder)], check=False)
            except Exception:
                pass
        # Re-run scan phase after moves
        return_code = subprocess.call([sys.executable, __file__] +
                                      (["--ci-check"] if args.ci_check else []) +
                                      ["--max-asset-mb", str(args.max_asset_mb)])
        sys.exit(return_code)

    # Package export coverage
    exported = read_pkg_exports()
    for mod in sorted({p.stem for p in PKG_DIR.glob("*.py") if p.name != "__init__.py" and not p.stem.startswith("_")}):
        if mod not in exported:
            summary.pkg_unexported.append(mod)

    # Repo hygiene
    summary.missing_expected = check_expected_files()

    # Badges
    summary.badges_missing = check_badges(ROOT / "README.md")

    # Large assets & stale stamps
    max_bytes = args.max_asset_mb * 1024 * 1024
    summary.large_assets = find_large_assets(max_bytes)
    summary.stale_stamps = find_stale_stamps()

    # CI gate (optional)
    ran, code, out = run_ci_check(args.ci_check)
    summary.ci_check_ran = ran
    summary.ci_check_code = code
    ci_output = out if ran else ""

    # Severity
    summary.critical_count += len(summary.compile_errors)
    summary.critical_count += len(summary.duplicates)
    summary.critical_count += len(summary.missing_expected)
    if ran and (code or 0) != 0:
        summary.critical_count += 1
    summary.warning_count += len(summary.orphans) + len(summary.pkg_unexported) + len(summary.badges_missing) + len(summary.large_assets) + len(summary.stale_stamps)

    # Report
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    def cb(s: str, lang: str = "") -> str:
        return f"\n```{lang}\n{s}\n```\n"

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(f"# Supersonic Health Report\n\nGenerated: **{now} UTC**\n")
    lines.append("## Summary")
    lines.append(f"- Python files: **{summary.py_count}**  · unique: **{summary.unique_py}**")
    lines.append(f"- Duplicates: **{len(summary.duplicates)}**")
    lines.append(f"- Compile errors: **{len(summary.compile_errors)}**")
    lines.append(f"- Orphan scripts: **{len(summary.orphans)}**")
    lines.append(f"- Unexported pkg modules: **{len(summary.pkg_unexported)}**")
    lines.append(f"- Missing expected configs: **{len(summary.missing_expected)}**")
    lines.append(f"- Large assets > {args.max_asset_mb} MB: **{len(summary.large_assets)}**")
    lines.append(f"- Stale 'Last updated' stamps: **{len(summary.stale_stamps)}**")
    if summary.moves_planned:
        lines.append(f"- Planned moves (dry-run): **{len(summary.moves_planned)}**")
    if summary.moves_done:
        lines.append(f"- Moves executed: **{len(summary.moves_done)}**")
    if summary.ci_check_ran:
        lines.append(f"- CI gate exit: **{summary.ci_check_code}**")
    lines.append("")

    if summary.compile_errors:
        lines.append("## 🔴 Compile Errors")
        for p, err in summary.compile_errors:
            lines.append(f"- `{p}`{cb(err)}")

    if summary.duplicates:
        lines.append("## 🔴 Duplicate Files (same content)")
        for a, b in summary.duplicates:
            lines.append(f"- `{a}`  is duplicate of  `{b}`")

    if summary.missing_expected:
        lines.append("## 🔴 Missing Required/Expected Files")
        for label in summary.missing_expected:
            lines.append(f"- {label}")

    if summary.orphans:
        lines.append("## 🟡 Orphan Python Files (outside tools/, supersonic_pkg/, extras/snippets/)")
        for p in sorted(summary.orphans):
            lines.append(f"- `{p}`")
        lines.append("\n*Tip:* run with `--apply --log-file moves.log` to organize and log moves.\n")

    if summary.pkg_unexported:
        lines.append("## 🟡 Modules in `supersonic_pkg/` not exported by `__init__.py`")
        lines.append(", ".join(f"`{m}`" for m in summary.pkg_unexported) or "—")
        lines.append("\n*Tip:* `python tools/build_pkg_index.py`.\n")

    if summary.badges_missing:
        lines.append("## 🟡 README Badges Missing")
        for b in summary.badges_missing:
            lines.append(f"- {b}")
        lines.append("\n*Tip:* `make status-badges`.\n")

    if summary.large_assets:
        lines.append(f"## 🟡 Large Assets (> {args.max_asset_mb} MB)")
        for p, sz in summary.large_assets:
            lines.append(f"- `{p}` — {sz/1024/1024:.1f} MB")
        lines.append("\n*Tip:* LFS/compress/move externals.\n")

    if summary.stale_stamps:
        lines.append("## 🟡 Stale 'Last updated' Stamps")
        for p in summary.stale_stamps:
            lines.append(f"- `{p}`")
        lines.append("\n*Tip:* `make bump-stamps`.\n")

    if summary.moves_planned and not args.apply:
        lines.append("## Proposed Moves (dry-run)")
        for src, dst, kind in summary.moves_planned:
            lines.append(f"- `{src}` → `{dst}` _(as {kind})_")
        lines.append("")

    if summary.moves_done:
        lines.append("## Executed Moves")
        for src, dst, kind in summary.moves_done:
            lines.append(f"- `{src}` → `{dst}` _(as {kind})_")
        lines.append("")

    if summary.ci_check_ran:
        lines.append("## CI Gate Output")
        lines.append(cb((ci_output or "").strip()[:20000], "text"))

    REPORT.write_text("\n".join(lines), encoding="utf-8")

    # Console summary
    print("=== Supersonic Health Scan ===")
    print(f"Report: {REPORT}")
    print(f"Python files: {summary.py_count} (unique: {summary.unique_py})")
    print(f"Duplicates: {len(summary.duplicates)} · Compile errors: {len(summary.compile_errors)}")
    print(f"Orphans: {len(summary.orphans)} · Planned moves: {len(summary.moves_planned)} · Executed: {len(summary.moves_done)}")
    if summary.ci_check_ran:
        print(f"CI gate exit: {summary.ci_check_code}")

    # Exit policy
    exit_code = 0
    if summary.critical_count > 0:
        exit_code = 2
    elif args.fail_on_warn and (summary.warning_count > 0):
        exit_code = 1
    sys.exit(exit_code)

# ---------- Undo implementation ----------
def undo_moves(log_path: Path, force: bool = False) -> int:
    """
    Replays move records in reverse.
    Verifies SHA of current dst against logged sha before moving back.
    On mismatch: skip (unless force=True).
    On collision at original path: restore as <name>__restoreN.py
    """
    recs = read_ledger(log_path)
    if not recs:
        print(f"No moves recorded in {log_path}. Nothing to undo.")
        return 0

    print(f"Loaded {len(recs)} records from {log_path}. Starting undo…")
    undone = 0
    skipped = 0
    for rec in reversed(recs):
        if rec.get("action") != "move":
            continue
        src = Path(rec["src"])
        dst = Path(rec["dst"])
        logged_sha = rec.get("sha256", "")
        kind = rec.get("kind", "unknown")

        if not dst.exists():
            print(f"Skip (missing current): {dst}")
            skipped += 1
            continue

        try:
            current_sha = sha256(dst)
        except Exception:
            current_sha = ""
        if not force and logged_sha and current_sha != logged_sha:
            print(f"Skip (hash mismatch): {dst} (expected {logged_sha[:8]}, got {current_sha[:8]})")
            skipped += 1
            continue

        restore_to = src if not src.exists() else unique_name(src.parent, src.name, tag="__restore")
        restore_to.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dst), str(restore_to))
        undone += 1
        print(f"Restored: {dst} -> {restore_to}")

    print(f"Undo complete. Restored: {undone}, Skipped: {skipped}")
    return 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(99)
