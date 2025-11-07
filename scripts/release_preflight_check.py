#!/usr/bin/env python3
# Enhanced fail-fast preflight for release artifacts with optional Markdown report:
# - Validates required files exist (supports globs)
# - Prints a pretty table with: Status | File | Size | SHA256 (for found files)
# - Prints a separate table for optional files
# - Optionally writes Markdown report to --md-out
# - Exits 1 if any required file is missing
import argparse, glob, hashlib, os, sys
from datetime import datetime

def expand(paths):
    """Expand globs to file lists. Returns (expanded_files, missing_patterns)."""
    expanded = []
    missing_patterns = []
    for p in paths:
        if any(ch in p for ch in ["*", "?", "["]):
            matches = sorted(glob.glob(p))
            if matches:
                expanded.extend(matches)
            else:
                # Glob pattern matched nothing - track as missing
                missing_patterns.append(p)
        else:
            expanded.append(p)
    return expanded, missing_patterns

def human_size(n):
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024.0:
            return f"{n:3.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"

def sha256_file(path, chunk=1024*1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def fmt_row(cols, widths):
    return " | ".join(s.ljust(w) for s, w in zip(cols, widths))

def print_table(title, rows, headers=("Status","File","Size","SHA256")):
    print(f"\n{title}")
    widths = [max(len(str(r[i])) for r in ([headers]+rows)) for i in range(len(headers))]
    sep = "-+-".join("-"*w for w in widths)
    print(fmt_row(headers, widths))
    print(sep)
    for r in rows:
        print(fmt_row(r, widths))

def to_markdown_table(title, rows, headers=("Status","File","Size","SHA256")):
    """Generate Markdown table from rows."""
    md = []
    md.append(f"### {title}")
    md.append("")
    md.append("| " + " | ".join(headers) + " |")
    md.append("| " + " | ".join("---" for _ in headers) + " |")
    for r in rows:
        # Escape backticks in file paths for markdown
        cells = []
        for i, cell in enumerate(r):
            cell_str = str(cell)
            # Wrap file paths in backticks for markdown
            if i == 1 and not cell_str.startswith("`"):
                cells.append(f"`{cell_str}`")
            elif i == 3 and cell_str != "-" and not cell_str.startswith("`"):
                # Wrap SHA256 in backticks
                cells.append(f"`{cell_str}`")
            else:
                cells.append(cell_str)
        md.append("| " + " | ".join(cells) + " |")
    md.append("")
    return "\n".join(md)

def main():
    ap = argparse.ArgumentParser(description="Validate and report release artifacts in dist/")
    ap.add_argument("--require", nargs="*", default=[], help="Exact file paths or globs required to exist")
    ap.add_argument("--optional", nargs="*", default=[], help="Optional file paths or globs")
    ap.add_argument("--quiet", action="store_true", help="Only print errors")
    ap.add_argument("--md-out", help="Write a Markdown report to this path (e.g., dist/RELEASE_ASSET_REPORT.md)")
    args = ap.parse_args()

    required, missing_req_patterns = expand(args.require)
    optional, missing_opt_patterns = expand(args.optional)

    # Smart defaults if nothing specified
    if not args.require and not args.optional:
        required = [
            "dist/sonic_manual_dark.pdf",
            "dist/sonic_manual_dark_two_up_raster.pdf",
        ]
        optional = [
            "dist/sonic_manual_light.pdf",
            "dist/sonic_manual_light_two_up_raster.pdf",
            "dist/SHA256SUMS.txt",
        ]

    # Add missing glob patterns as missing required files
    missing = list(missing_req_patterns)
    req_rows = []
    
    # Add rows for missing glob patterns first
    for pattern in missing_req_patterns:
        req_rows.append(("❌", f"{pattern} (no matches)", "-", "-"))
    
    # Then check expanded required files
    for p in required:
        if os.path.exists(p):
            size = human_size(os.path.getsize(p))
            digest = sha256_file(p) if p.lower().endswith(".pdf") or p.lower().endswith(".zip") else "-"
            req_rows.append(("✅", p, size, digest))
        else:
            missing.append(p)
            req_rows.append(("❌", p, "-", "-"))

    opt_rows = []
    
    # Add rows for missing optional glob patterns
    for pattern in missing_opt_patterns:
        opt_rows.append(("⚠️", f"{pattern} (no matches)", "-", "-"))
    
    # Then check expanded optional files
    for p in optional:
        if os.path.exists(p):
            size = human_size(os.path.getsize(p))
            digest = sha256_file(p) if p.lower().endswith(".pdf") or p.lower().endswith(".zip") or p.lower().endswith(".txt") else "-"
            opt_rows.append(("✅", p, size, digest))
        else:
            opt_rows.append(("⚠️", p, "-", "-"))

    if not args.quiet:
        print_table("== Preflight: Required artifacts ==", req_rows)
        if opt_rows:
            print_table("\n== Preflight: Optional artifacts ==", opt_rows)

    # Optional Markdown report
    if args.md_out:
        os.makedirs(os.path.dirname(args.md_out) or ".", exist_ok=True)
        parts = []
        parts.append("# Release Artifact Report")
        parts.append("")
        parts.append(f"- **Generated:** `{datetime.utcnow().isoformat(timespec='seconds')}Z`")
        parts.append("")
        parts.append(to_markdown_table("Required Artifacts", req_rows))
        if opt_rows:
            parts.append(to_markdown_table("Optional Artifacts", opt_rows))
        if missing:
            parts.append("> **Status:** ❌ Missing required artifacts.")
        else:
            parts.append("> **Status:** ✅ All required artifacts present.")
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))
        print(f"[ok] Wrote Markdown report -> {args.md_out}")

    if missing:
        print("\n[ERROR] Missing required artifacts:", *missing, sep="\n  - ")
        sys.exit(1)

    print("\n[OK] Preflight passed. Artifacts ready for upload.")
    sys.exit(0)

if __name__ == "__main__":
    main()
