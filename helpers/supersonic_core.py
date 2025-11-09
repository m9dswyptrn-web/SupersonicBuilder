#!/usr/bin/env python3
import argparse, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "supersonic_settings.json"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

def load_cfg():
    base = {
        "voice_mode":"commander",
        "auto_push": False,
        "watch_dirs": ["helpers","docs","assets",".github/workflows","policies"],
        "log_level": "info",
        "engine_mode": "hybrid",
        "summary_commit_count": 8,
    }
    if CFG_PATH.exists():
        try: base.update(json.loads(CFG_PATH.read_text(encoding="utf-8")))
        except Exception: pass
    if os.getenv("SUP_ENGINE_MODE"):
        base["engine_mode"] = os.getenv("SUP_ENGINE_MODE")
    return base

CFG = load_cfg()

def say(event, line=None):
    import subprocess
    env = os.environ.copy()
    env["VOICE_PACK"] = CFG.get("voice_mode","commander")
    env["VOICE_EVENT"] = event
    try:
        subprocess.run([sys.executable, str(ROOT / "helpers" / "supersonic_voice_console.py")],
                       env=env, check=False)
    except Exception:
        if line: print(f"[voice] {line}")

def build(ai=False):
    from helpers import supersonic_autobuilder as ab
    say("build_start","Build engaged, Commander.")
    ok = ab.make_release()
    if ok:
        if ai:
            from helpers import supersonic_ai_reasoner as ai_mod
            txt = ai_mod.summarize_latest(CFG.get("summary_commit_count"))
            (LOGS / "supersonic_changelog.log").write_text(str(txt)+"\n", encoding="utf-8")
            print("\n=== AI SUMMARY ===\n"+str(txt)+"\n==================\n")
        say("build_success","Build complete.")
    else:
        say("build_fail","Build failed.")
    if ok and CFG.get("auto_push", False):
        ab.git_autopush("chore: supersonic auto-build")
    return ok

def watch(ai=False):
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except Exception:
        print("[warn] watchdog not installed; run: pip install watchdog"); return

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory: return
            p = Path(event.src_path)
            watched = [ROOT / d for d in CFG.get("watch_dirs",[])]
            if not any(str(p).startswith(str(w)) for w in watched):
                return
            print(f"[watch] change: {p}")
            build(ai=ai)

    say("build_start","Watch mode engaged.")
    obs = Observer()
    for d in CFG.get("watch_dirs", []):
        p = ROOT / d
        if p.exists(): obs.schedule(Handler(), str(p), recursive=True)
    obs.start()
    try:
        while True:
            time.sleep(1.0)
    finally:
        obs.stop(); obs.join()

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s1 = sub.add_parser("build"); s1.add_argument("--ai", action="store_true")
    s2 = sub.add_parser("watch"); s2.add_argument("--ai", action="store_true")
    sub.add_parser("push")
    s4 = sub.add_parser("announce"); s4.add_argument("event", nargs="?", default="deploy_done")
    s5 = sub.add_parser("set-voice"); s5.add_argument("mode", choices=["commander","aiops","flightops","scificontrol","industrialops","arcadehud"])

    args = ap.parse_args()
    if args.cmd in (None,"build"):
        ok=build(ai=getattr(args,"ai",False)); sys.exit(0 if ok else 1)
    if args.cmd=="watch":
        watch(ai=getattr(args,"ai",False)); return
    if args.cmd=="push":
        from helpers import supersonic_autobuilder as ab
        print("Auto-push:", ab.git_autopush()); return
    if args.cmd=="announce":
        say(args.event, args.event); return
    if args.cmd=="set-voice":
        CFG["voice_mode"]=args.mode
        CFG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CFG_PATH.write_text(json.dumps(CFG, indent=2), encoding="utf-8")
        print(f"Voice mode set -> {args.mode}"); return

if __name__=="__main__":
    main()
