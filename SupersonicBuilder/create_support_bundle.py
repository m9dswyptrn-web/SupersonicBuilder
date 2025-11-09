#!/usr/bin/env python3
import os, sys, json, time, shutil, subprocess, platform, pathlib, webbrowser

ROOT = pathlib.Path(".").resolve()
STAMP = time.strftime("%Y%m%d-%H%M%S")
OUTDIR = ROOT / f"support_bundle_{STAMP}"
ZIPPATH = ROOT / f"support_bundle_{STAMP}.zip"

SAFE_COPY = [
    ".replit", "replit.nix", "requirements.txt", "pyproject.toml",
    "poetry.lock", ".gitignore", ".git/config",
    ".github/workflows", "README.md"
]

GIT_CMDS = {
    "git_status.txt":      ["git","status","-vv"],
    "git_branch.txt":      ["git","branch","-vv"],
    "git_remote.txt":      ["git","remote","-v"],
    "git_log_50.txt":      ["git","log","--oneline","-n","50"],
    "git_config_user.txt": ["git","config","--list","--show-origin"],
}

def run(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return p.stdout
    except Exception as e:
        return f"[error running {' '.join(cmd)}] {e}"

def mask_env(d: dict):
    masked = {}
    for k,v in d.items():
        kl = k.lower()
        if any(s in kl for s in ["token","secret","key","password","passwd","auth","cookie"]):
            masked[k] = "***redacted***"
        else:
            masked[k] = v
    return masked

def list_big_files(limit_mb=10, top_n=50):
    rows = []
    for p in ROOT.rglob("*"):
        if ".git" in p.parts or not p.is_file():
            continue
        try:
            sz = p.stat().st_size
        except Exception:
            continue
        rows.append((sz, str(p.relative_to(ROOT))))
    rows.sort(reverse=True)
    mb = 1024*1024
    lines = [f"{sz/mb:8.2f} MB  {path}" for sz, path in rows[:top_n] if sz >= limit_mb*mb]
    return "\n".join(lines) if lines else "(no files >= %d MB)" % limit_mb

def safe_copy(src, dst):
    srcp = ROOT / src
    dstp = dst / src
    try:
        if srcp.is_file():
            dstp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(srcp, dstp)
        elif srcp.is_dir():
            shutil.copytree(srcp, dstp, dirs_exist_ok=True)
    except Exception as e:
        (dst/("copy_errors.txt")).write_text(
            f"Failed to copy {src}: {e}\n", encoding="utf-8"
        )

def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # 1) System & env (masked)
    sysinfo = {
        "platform": platform.platform(),
        "python": sys.version,
        "cwd": str(ROOT),
        "time": STAMP,
    }
    (OUTDIR/"system_info.json").write_text(json.dumps(sysinfo, indent=2), encoding="utf-8")
    (OUTDIR/"env_masked.json").write_text(json.dumps(mask_env(dict(os.environ)), indent=2), encoding="utf-8")

    # 2) Git diagnostics
    for name, cmd in GIT_CMDS.items():
        (OUTDIR/name).write_text(run(cmd), encoding="utf-8")

    # 3) Biggest files snapshot
    (OUTDIR/"largest_files.txt").write_text(list_big_files(limit_mb=5, top_n=200), encoding="utf-8")

    # 4) Copy typical config files
    for p in SAFE_COPY:
        safe_copy(p, OUTDIR)

    # 5) Zip it
    if ZIPPATH.exists():
        ZIPPATH.unlink()
    shutil.make_archive(str(ZIPPATH).replace(".zip",""), "zip", OUTDIR)

    print("\n✅ Created Replit support bundle:")
    print("   ", ZIPPATH)
    print("\nAttach that ZIP to your support ticket.")
    try:
        webbrowser.open("https://replit.com/support")
        print("🌐 Opened Replit support page in a browser (if supported).")
    except Exception:
        pass

if __name__ == "__main__":
    main()
