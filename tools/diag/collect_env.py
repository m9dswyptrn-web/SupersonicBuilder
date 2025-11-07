#!/usr/bin/env python3
import os, json, platform, subprocess, pathlib, time

d = pathlib.Path("diag")
d.mkdir(parents=True, exist_ok=True)

def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output or str(e)

report = {
  "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "git_sha": os.environ.get("GITHUB_SHA") or sh("git rev-parse --short=10 HEAD").strip(),
  "python": platform.python_version(),
  "system": {"platform": platform.platform(), "machine": platform.machine()},
  "env": {k:v for k,v in os.environ.items() if k in ("REPL_SLUG","GITHUB_RUN_ID","GITHUB_REF","GITHUB_SHA")},
  "pip_freeze": sh("python -m pip freeze"),
  "tree_output": sh("ls -lah"),
}

(d/"diag_report.json").write_text(json.dumps(report, indent=2))
print(f"[diag] wrote {d/'diag_report.json'}")
