
#!/usr/bin/env python3
from pathlib import Path
import argparse, datetime, re, sys

MAKEFILE = Path("Makefile")

BLOCKS = [
    "# === [SONIC-MERGE] Version / stamping (BEGIN) ===\nVERSION       ?= v1.0.0\nBUILD_DT      ?= $(shell date -u '+%Y-%m-%d %H:%M UTC')\nexport SONIC_VERSION=$(VERSION)\nexport SONIC_BUILD_DT=$(BUILD_DT)\n# === [SONIC-MERGE] Version / stamping (END) ===\n",
    '# === [SONIC-MERGE] PDF/SVG dependencies (BEGIN) ===\n.ONESHELL:\ninstall-overlay-reqs:\n\tpython3 -m pip install -q --upgrade pip\n\tpython3 -m pip install -q reportlab svglib Pillow pyyaml\n# === [SONIC-MERGE] PDF/SVG dependencies (END) ===\n',
    '# === [SONIC-MERGE] Continuity card builder (BEGIN) ===\nbuild-continuity: install-overlay-reqs\n\tpython3 tools/build_continuity_card.py --rev "$(VERSION) • $(BUILD_DT)"\n# === [SONIC-MERGE] Continuity card builder (END) ===\n',
    '# === [SONIC-MERGE] Zip artifacts (BEGIN) ===\nzip:\n\t@rm -f dist/*.zip 2>/dev/null || true\n\tmkdir -p dist\n\tzip -qr "dist/manual_$(VERSION).zip" output assets config docs || true\n# === [SONIC-MERGE] Zip artifacts (END) ===\n',
]

def already_contains(txt, block):
    # check by BEGIN marker
    import re
    m = re.search(r"^# === \[SONIC-MERGE\].*\(BEGIN\)", block, re.M)
    if m:
        begin_line = m.group(0).strip()
        return begin_line in txt
    return block.strip() in txt

def ensure_release_all_dep(txt):
    # ensure 'release-all' includes build-continuity
    rx = re.compile(r"^(release-all\s*:\s*)(.*)$", re.M)
    def repl(m):
        head, deps = m.group(1), m.group(2)
        if "build-continuity" in deps:
            return m.group(0)
        new_deps = ("build-continuity " + deps).strip()
        return head + new_deps
    if "release-all" in txt:
        txt2 = rx.sub(repl, txt, count=1)
        return txt2, (txt2 != txt)
    else:
        addition = "\n\nrelease-all: build-continuity\n\t@echo \"✅ Release (continuity only) complete\"\n"
        return txt + addition, True

def merge(makefile: Path, apply=False, force=False):
    if not makefile.exists():
        print("❌ No Makefile found in this directory.")
        sys.exit(1)
    src = makefile.read_text(encoding="utf-8")

    changes = []
    out = src

    for block in BLOCKS:
        if force or not already_contains(out, block):
            out = out.rstrip() + "\n\n" + block.rstrip() + "\n"
            changes.append(block.splitlines()[0])

    out2, changed_rel = ensure_release_all_dep(out)
    if changed_rel:
        out = out2
        changes.append("# === [SONIC-MERGE] HINT: ensure release-all depends on build-continuity ===")

    if not changes:
        print("✅ Nothing to change (already merged).")
        return False

    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = makefile.with_name(f"Makefile.bak-{ts}")
        bak.write_text(src, encoding="utf-8")
        makefile.write_text(out, encoding="utf-8")
        print(f"✅ Applied. Backup created: {bak.name}")
        for c in changes:
            print("   •", c)
    else:
        print("🛈 DRY RUN — would apply the following blocks:")
        for c in changes:
            print("   •", c)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default is dry-run)")
    ap.add_argument("--force", action="store_true", help="re-write blocks even if markers found")
    args = ap.parse_args()
    merge(MAKEFILE, apply=args.apply, force=args.force)

if __name__ == "__main__":
    main()
