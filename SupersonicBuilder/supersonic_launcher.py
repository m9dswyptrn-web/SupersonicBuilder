#!/usr/bin/env python3
"""
Supersonic Auto-Launcher (v4)
A friendly mission console for SonicBuilder's Supersonic Control Core.

• Color output (colorama) with clear phase banners
• Voice cues via helpers/supersonic_voice_console.py (QUIET=1 to silence)
• Maps simple commands -> Make targets (or direct Python fallbacks)
• Safe when Makefile isn't wired yet (calls helpers/scripts directly)
"""
import os, sys, subprocess, shutil, argparse, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable or "python3"

def have_make() -> bool:
    return shutil.which("make") is not None and (ROOT / "make" / "ControlCore.mk").exists()

def say(event: str, pack: str = None, quiet_env: str = None):
    env = os.environ.copy()
    if pack: env["VOICE_PACK"] = pack
    if event: env["VOICE_EVENT"] = event
    if quiet_env is not None: env["QUIET"] = quiet_env
    vc = ROOT / "helpers" / "supersonic_voice_console.py"
    if vc.exists():
        subprocess.run([PY, str(vc)], env=env, check=False)

def banner(title: str):
    try:
        from colorama import init, Fore, Style
        init()
        bar = Fore.CYAN + "=" * 64 + Style.RESET_ALL
        print(bar)
        print(Fore.MAGENTA + f"🛫 {title}" + Style.RESET_ALL)
        print(bar)
    except Exception:
        print("=" * 64)
        print(f"🛫 {title}")
        print("=" * 64)

def run_make(target: str, extra_env=None) -> int:
    env = os.environ.copy()
    if extra_env: env.update(extra_env)
    return subprocess.call(["make", "-f", "make/ControlCore.mk", target], env=env)

def run_py(mod_path: Path, args=None, extra_env=None) -> int:
    env = os.environ.copy()
    if extra_env: env.update(extra_env)
    cmd = [PY, str(mod_path)]
    if args: cmd += args
    return subprocess.call(cmd, env=env)

def do_or_fallback(make_target: str, py_path: Path, py_args=None, env=None) -> int:
    if have_make():
        return run_make(make_target, extra_env=env)
    return run_py(py_path, py_args, extra_env=env)

def main():
    ap = argparse.ArgumentParser(
        prog="supersonic",
        description="Supersonic Auto-Launcher — mission console for Control Core v4",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("doctor", help="Preflight checks")

    p_build = sub.add_parser("build", help="Build with AI summary")
    p_build.add_argument("--quiet-voice", action="store_true")

    p_watch = sub.add_parser("watch", help="Watch + AI")
    p_watch.add_argument("--quiet-voice", action="store_true")

    sub.add_parser("bump", help="Smart semver bump (feat/fix/breaking)")
    sub.add_parser("release", help="Full pipeline (bump→build→hash→sbom→notes→notify)")

    p_rb = sub.add_parser("rollback", help="Rollback to tag")
    p_rb.add_argument("tag", nargs="?", help="vX.Y.Z (defaults to latest)")

    p_hash = sub.add_parser("hash", help="SHA256 + optional Cosign signing")
    p_sbom = sub.add_parser("sbom", help="SBOM + lightweight security scan")
    p_notes = sub.add_parser("notes", help="Generate AI release notes")

    p_voice = sub.add_parser("voice", help="Set voice mode")
    p_voice.add_argument("mode", choices=["commander","aiops","flightops","scificontrol","industrialops","arcadehud"])

    p_announce = sub.add_parser("announce", help="Play a voice event")
    p_announce.add_argument("--event", default="deploy_done")

    p_vinstall = sub.add_parser("voice-install", help="Install voicepack from URL")
    p_vinstall.add_argument("url")

    p_ud = sub.add_parser("unit-deploy", help="ADB deploy APK to head unit")
    p_ud.add_argument("apk")

    sub.add_parser("unit-reboot", help="ADB reboot head unit")
    sub.add_parser("unit-logs", help="ADB logcat dump")

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help(); sys.exit(0)

    # Common env defaults
    base_env = {
        "SUP_AUTOPUSH": os.getenv("SUP_AUTOPUSH", "1"),
        "SUP_ENGINE_MODE": os.getenv("SUP_ENGINE_MODE", "hybrid"),
    }

    # Paths
    H = ROOT / "helpers"
    S = ROOT / "scripts"
    mk_present = have_make()

    if args.cmd == "doctor":
        banner("Preflight Doctor")
        say("build_start", quiet_env="1")
        rc = do_or_fallback("ai-doctor", S / "doctor.py", env=base_env)
        say("build_success" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "build":
        banner("Build (AI summary)")
        say("build_start")
        env = base_env.copy()
        if args.quiet_voice: env["QUIET"] = "1"
        rc = do_or_fallback("ai-build", H / "supersonic_core.py", ["build","--ai"], env=env)
        say("build_success" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "watch":
        banner("Watch (AI)")
        say("build_start")
        env = base_env.copy()
        if args.quiet_voice: env["QUIET"] = "1"
        if mk_present:
            rc = run_make("ai-watch", extra_env=env)
        else:
            rc = run_py(H / "supersonic_core.py", ["watch","--ai"], extra_env=env)
        say("deploy_done" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "bump":
        banner("Smart SemVer Bump")
        rc = do_or_fallback("ai-bump", S / "version_bump.py", env=base_env)
        sys.exit(rc)

    if args.cmd == "release":
        banner("Full Release Pipeline")
        say("deploy_start")
        if mk_present:
            rc = run_make("ai-release", extra_env=base_env)
        else:
            # Manual fallback chain: bump -> build -> hash -> sbom -> notes -> notify
            rc1 = run_py(S / "version_bump.py", extra_env=base_env)
            rc2 = run_py(H / "supersonic_core.py", ["build","--ai"], extra_env=base_env)
            rc3 = run_py(S / "integrity.py", extra_env=base_env)
            rc4 = run_py(S / "sbom_scan.py", extra_env=base_env)
            rc5 = run_py(S / "release_notes_ai.py", extra_env=base_env)
            rc6 = run_py(S / "notify_webhooks.py", extra_env=base_env)
            rc = 0 if all(x == 0 for x in [rc1,rc2,rc3,rc4,rc5,rc6]) else 1
        say("deploy_done" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "rollback":
        banner(f"Rollback → {args.tag or '(latest)'}")
        if mk_present:
            os.environ["TAG"] = args.tag or ""
            rc = run_make("ai-rollback", extra_env=base_env)
        else:
            py_args = [args.tag] if args.tag else []
            rc = run_py(S / "rollback.py", py_args, extra_env=base_env)
        say("build_success" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "hash":
        banner("Integrity: SHA256 + Cosign")
        rc = do_or_fallback("ai-hash", S / "integrity.py", env=base_env)
        sys.exit(rc)

    if args.cmd == "sbom":
        banner("SBOM + Security Scan")
        rc = do_or_fallback("ai-sbom", S / "sbom_scan.py", env=base_env)
        sys.exit(rc)

    if args.cmd == "notes":
        banner("AI Release Notes")
        rc = do_or_fallback("ai-notes", S / "release_notes_ai.py", env=base_env)
        sys.exit(rc)

    if args.cmd == "voice":
        banner(f"Voice → {args.mode}")
        if mk_present:
            rc = run_make("ai-voice", extra_env={"MODE": args.mode, **base_env})
        else:
            rc = run_py(H / "supersonic_core.py", ["set-voice", args.mode], extra_env=base_env)
        say("deploy_done")
        sys.exit(rc)

    if args.cmd == "announce":
        banner(f"Announce → {args.event}")
        say(args.event)
        sys.exit(0)

    if args.cmd == "voice-install":
        banner("Install Voicepack")
        if mk_present:
            rc = run_make("ai-voice-install", extra_env={"URL": args.url, **base_env})
        else:
            rc = run_py(S / "voicepack_manager.py", [args.url], extra_env=base_env)
        say("deploy_done" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "unit-deploy":
        banner(f"Unit Deploy → {args.apk}")
        if mk_present:
            rc = run_make("unit-deploy", extra_env={"APK": args.apk, **base_env})
        else:
            rc = run_py(S / "adb_actions.py", ["deploy", args.apk], extra_env=base_env)
        say("deploy_done" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "unit-reboot":
        banner("Unit Reboot")
        if mk_present:
            rc = run_make("unit-reboot", extra_env=base_env)
        else:
            rc = run_py(S / "adb_actions.py", ["reboot"], extra_env=base_env)
        say("deploy_done" if rc == 0 else "build_fail")
        sys.exit(rc)

    if args.cmd == "unit-logs":
        banner("Unit Logs (logcat)")
        if mk_present:
            rc = run_make("unit-logs", extra_env=base_env)
        else:
            rc = run_py(S / "adb_actions.py", ["logs"], extra_env=base_env)
        say("deploy_done" if rc == 0 else "build_fail")
        sys.exit(rc)

if __name__ == "__main__":
    main()
