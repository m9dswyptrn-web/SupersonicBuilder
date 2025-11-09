#!/usr/bin/env python3
"""Verify SonicBuilder PDF metadata and optional filename suffix."""
import sys, os, re
from pathlib import Path
from pypdf import PdfReader

REQ_KEYS = ["/Version", "/Commit", "/BuildDate", "/Repository"]

def meta_ok(md):
    """Check if all required metadata keys are present and non-empty."""
    if not md:
        return False
    for k in REQ_KEYS:
        if k not in md or not str(md[k]).strip():
            return False
    return True

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Verify SonicBuilder PDF metadata and optional filename suffix")
    ap.add_argument("--root", default="release_assets", help="Folder to scan for PDFs")
    ap.add_argument("--require-suffix", action="store_true", help="Require filenames to include _g<commit>")
    ap.add_argument("--commit", default=os.environ.get("SB_COMMIT", ""), help="Expected short commit (optional)")
    args = ap.parse_args()

    root = Path(args.root)
    pdfs = sorted(root.rglob("*.pdf"))
    if not pdfs:
        print(f"[verify] No PDFs found under {root}, nothing to verify.")
        sys.exit(0)

    ok = True
    suffix_re = re.compile(r"_g[0-9a-f]{7,12}\.pdf$", re.IGNORECASE)

    for p in pdfs:
        try:
            r = PdfReader(str(p))
            md = r.metadata
        except Exception as e:
            print(f"[FAIL] {p.name}: unreadable PDF ({e})")
            ok = False
            continue

        # Metadata checks
        if not meta_ok(md):
            print(f"[FAIL] {p.name}: missing one or more required metadata keys {REQ_KEYS}")
            print(f"       found: {sorted(md.keys()) if md else 'none'}")
            ok = False
        else:
            # Optional: commit match in metadata
            if md and "/Commit" in md and args.commit:
                if args.commit.lower() not in str(md["/Commit"]).lower():
                    print(f"[FAIL] {p.name}: /Commit does not contain expected short SHA '{args.commit}' (got {md['/Commit']})")
                    ok = False

        # Suffix checks (release only)
        if args.require_suffix:
            if not suffix_re.search(p.name):
                print(f"[FAIL] {p.name}: filename missing _g<commit> suffix")
                ok = False
            elif args.commit:
                # if requires suffix and commit provided, ensure same commit
                suf = re.search(r"_g([0-9a-f]{7,12})\.pdf$", p.name, re.IGNORECASE)
                if suf and not str(suf.group(1)).lower().startswith(args.commit.lower()):
                    print(f"[FAIL] {p.name}: filename commit '{suf.group(1)}' does not match expected '{args.commit}'")
                    ok = False

        if ok:
            print(f"[OK]   {p.name}")

    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
