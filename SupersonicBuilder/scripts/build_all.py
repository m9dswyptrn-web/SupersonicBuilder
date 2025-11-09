
import argparse, os, time, subprocess, sys, json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchdog.observers import Observer  # type: ignore
    from watchdog.events import FileSystemEventHandler  # type: ignore
    HAVE_WATCHDOG = True
except Exception:
    HAVE_WATCHDOG = False

def safe_run(cmd: list[str]) -> int:
    print("[build] >", " ".join(cmd))
    return subprocess.call(cmd)

def build_once(args):
    # Delegate to your existing builder if present, else stub
    # Try main.py first, then fallback to a simple ReportLab stub (not included here).
    if Path("main.py").exists():
        return safe_run([sys.executable, "main.py", "--theme", args.theme, "--assets", args.assets, "--output", args.output, "--config", args.config])
    else:
        print("main.py not found. Please wire your PDF generation entrypoint here.")
        return 1

class RebuildOnChange(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args
    def on_any_event(self, event):
        if event.is_directory: 
            return
        # Only rebuild for relevant file types
        extensions = (".py", ".svg", ".png", ".jpg", ".jpeg", ".json", ".md")
        if any(event.src_path.endswith(str(ext)) for ext in extensions):
            print("\n[watch] change detected:", event.src_path)
            build_once(self.args)

def main():
    p = argparse.ArgumentParser(description="SonicBuilder build orchestrator")
    p.add_argument("--theme", default="dark", choices=["dark","light"])
    p.add_argument("--assets", default="assets")
    p.add_argument("--output", default="output")
    p.add_argument("--config", default="config/manual.manifest.json")
    p.add_argument("--watch", action="store_true")
    args = p.parse_args()

    os.makedirs(args.output, exist_ok=True)

    rc = build_once(args)
    if rc != 0:
        sys.exit(rc)

    if args.watch:
        if not HAVE_WATCHDOG:
            print("[watch] python -m pip install watchdog to enable file watching")
            return
        if HAVE_WATCHDOG:
            handler = RebuildOnChange(args)
            observer = Observer()
            for path in [args.assets, "src", "scripts", "utils", "config"]:
                if Path(path).exists():
                    observer.schedule(handler, path, recursive=True)
            observer.start()
            print("[watch] watching for changes... Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

if __name__ == "__main__":
    main()
