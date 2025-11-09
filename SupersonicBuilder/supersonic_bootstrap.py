#!/usr/bin/env python3
"""
Supersonic Bootstrapper
- One command to inject/upgrade:
  • Rotating file logger (supersonic.log)
  • Request/response logging hooks (+ exception tracer)
  • /health endpoint (rich: disk/uptime/checks + CPU/load/mem/errors/5xx)
  • /metrics endpoint (JSON + Prometheus text)
- Idempotent (safe to re-run)
- Revert support (restores the most recent backup)
- Status check

Usage:
  python3 supersonic_bootstrap.py --all
  python3 supersonic_bootstrap.py --status
  python3 supersonic_bootstrap.py --revert
  python3 supersonic_bootstrap.py --no-reload --all
"""

import os, re, sys, json, shutil, glob, datetime, time
from pathlib import Path
from typing import Optional

ROOT   = Path(os.getcwd())
SERVER = ROOT / "serve_pdfs.py"
STAMP  = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def die(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)

def ok(msg: str) -> None:
    print(f"✅ {msg}")

def warn(msg: str) -> None:
    print(f"⚠️  {msg}")

def backup() -> Path:
    dst = SERVER.with_suffix(SERVER.suffix + f".bak.{STAMP}")
    shutil.copy2(SERVER, dst)
    print(f"🧾 Backup: {SERVER.name} -> {dst.name}")
    return dst

def latest_backup() -> Optional[Path]:
    pats = sorted(SERVER.parent.glob(SERVER.name + ".bak.*"), reverse=True)
    return pats[0] if pats else None

def touch_hotreload() -> None:
    try:
        with open(".hotreload","a",encoding="utf-8") as f:
            f.write(f"# reload {STAMP}\n")
        print("🔄 Touched .hotreload (Replit will restart)")
    except Exception as e:
        warn(f"could not touch .hotreload: {e}")

ROTATING_HANDLER_SNIPPET = r"""
# --- Supersonic: ensure rotating file handler for logs ---
import logging
from logging.handlers import RotatingFileHandler
_log = logging.getLogger("supersonic")
if not _log.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
_log_file = os.getenv("SUPERSONIC_LOG_FILE", "supersonic.log")
try:
    _rh = RotatingFileHandler(_log_file, maxBytes=1_000_000, backupCount=3)
    _rh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    if not any(isinstance(h, RotatingFileHandler) for h in _log.handlers):
        _log.addHandler(_rh)
        _log.info("FILE_LOGGER_READY file=%s", _log_file)
except Exception as _e:
    _log.warning("FILE_LOGGER_DISABLED err=%s", _e)
# --- end Supersonic rotating handler ---
"""

AFTER_REQUEST_SNIPPET = r"""
# --- Supersonic: request/response logging hooks ---
import time
from flask import request

try:
    import logging
    log = logging.getLogger("supersonic") if logging.getLogger("supersonic") else logging.getLogger()
except Exception:
    log = None

@app.before_request
def _supersonic_req_start():
    request._supersonic_t0 = time.time()

def _client_ip():
    fwd = request.headers.get("X-Forwarded-For")
    return (fwd.split(",")[0].strip() if fwd else request.remote_addr) or "unknown"

@app.after_request
def _supersonic_after(resp):
    try:
        t0 = getattr(request, "_supersonic_t0", None)
        ms = int((time.time() - t0) * 1000) if t0 else -1
        ua = request.headers.get("User-Agent","")
        ln = f'REQ method={request.method} path={request.path} status={resp.status_code} ms={ms} bytes={resp.calculate_content_length() or 0} ua="{ua}" ip={_client_ip()}'
        if log: log.info(ln)
        else: print(ln)
    except Exception as e:
        if log: log.warning("REQ_LOG_FAIL err=%s", e)
    return resp

@app.errorhandler(Exception)
def _supersonic_ex(e):
    try:
        import traceback
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        ua = request.headers.get("User-Agent","")
        ln = f'EXC method={request.method} path={getattr(request,"path","?")} ua="{ua}" ip={_client_ip()}'
        if log:
            log.error(ln)
            for line in tb.splitlines():
                log.error(line)
        else:
            print(ln); print(tb)
    except Exception:
        pass
    raise e
# --- end Supersonic hooks ---
"""

HEALTH_BASE_FUNC = r'''
@app.route("/health")
def supersonic_health():
    from pathlib import Path as _Path
    import os as _os, sys as _sys, json as _json, time as _time, shutil as _shutil, datetime as _dt

    _start_file = _Path(".supersonic_start.json")
    _now = _time.time()
    _pid = _os.getpid()
    _start_ts = None
    if _start_file.exists():
        try:
            data = _json.loads(_start_file.read_text(encoding="utf-8"))
            if data.get("pid") == _pid and isinstance(data.get("ts"), (int, float)):
                _start_ts = float(data["ts"])
        except Exception:
            _start_ts = None
    if _start_ts is None:
        _start_ts = _now
        try:
            _start_file.write_text(_json.dumps({"pid": _pid, "ts": _start_ts}), encoding="utf-8")
        except Exception:
            pass
    _uptime = max(0.0, _now - _start_ts)

    try:
        _du = _shutil.disk_usage(".")
        _disk = {"total": int(_du.total), "used": int(_du.used), "free": int(_du.free)}
    except Exception as _e:
        _disk = {"total": 0, "used": 0, "free": 0, "error": str(_e)}

    def _present(bin_name: str) -> bool:
        try:
            return _shutil.which(bin_name) is not None
        except Exception:
            return False

    _checks = {
        "git_present": _present("git"),
        "make_present": _present("make"),
    }

    _cpu_count = 0
    try:
        _cpu_count = max(1, (_os.cpu_count() or 1))
    except Exception:
        _cpu_count = 1

    _load_raw = None
    _load_per_cpu = None
    try:
        if hasattr(_os, "getloadavg"):
            _l1, _l5, _l15 = _os.getloadavg()
            _load_raw = [_l1, _l5, _l15]
            _load_per_cpu = [round(_l1/_cpu_count, 4), round(_l5/_cpu_count, 4), round(_l15/_cpu_count, 4)]
    except Exception:
        _load_raw = None
    _log_path = _os.getenv("SUPERSONIC_LOG_FILE", "supersonic.log")
    _err_rx = _os.getenv("HEALTH_ERROR_PATTERNS", r"(?i)\\bERROR\\b|\\bTraceback\\b")
    try:
        _err_re = __import__("re").compile(_err_rx)
    except Exception:
        _err_re = None
    _errors_last_5m = 0
    try:
        import time as _time
        _now2 = _time.time()
        _max_bytes = 200_000
        with open(_log_path, "r", encoding="utf-8", errors="replace") as _f:
            _f.seek(0, _os.SEEK_END)
            _pos = max(0, _f.tell() - _max_bytes)
            _f.seek(_pos)
            _chunk = _f.read()
        _cutoff = _now2 - 300.0
        _ts_re = __import__("re").compile(r"(20\\d\\d-\\d\\d-\\d\\d \\d\\d:\\d\\d:\\d\\d)")
        for _ln in _chunk.splitlines():
            if _err_re and _err_re.search(_ln):
                _m = _ts_re.search(_ln)
                if _m:
                    try:
                        import datetime as _dt, time as _time
                        _t = _time.mktime(_dt.datetime.strptime(_m.group(1), "%Y-%m-%d %H:%M:%S").timetuple())
                        if _t >= _cutoff:
                            _errors_last_5m += 1
                    except Exception:
                        _errors_last_5m += 1
                else:
                    _errors_last_5m += 1
    except Exception:
        pass

    _mem = {"rss_bytes": None, "vms_bytes": None, "rss_mb": None, "vms_mb": None, "source": "unknown"}
    try:
        import psutil as _ps
        _p = _ps.Process()
        _mi = _p.memory_info()
        _mem["rss_bytes"] = int(getattr(_mi, "rss", 0))
        _mem["vms_bytes"] = int(getattr(_mi, "vms", 0))
        _mem["rss_mb"]    = round(_mem["rss_bytes"] / (1024*1024), 3)
        _mem["vms_mb"]    = round(_mem["vms_bytes"] / (1024*1024), 3)
        _mem["source"]    = "psutil"
    except Exception:
        try:
            _page = _os.sysconf("SC_PAGE_SIZE")
            with open("/proc/self/statm","r") as _f:
                _vals = _f.read().strip().split()
            _rss_pages = int(_vals[1]) if len(_vals) > 1 else 0
            _rss_bytes = _rss_pages * _page
            _mem["rss_bytes"] = int(_rss_bytes)
            _mem["rss_mb"]    = round(_rss_bytes / (1024*1024), 3)
            _mem["source"]    = "proc/statm"
        except Exception:
            try:
                import resource as _res
                _ru = _res.getrusage(_res.RUSAGE_SELF)
                _rss_kb = getattr(_ru, "ru_maxrss", 0)
                _rss_b  = int(_rss_kb * 1024) if _rss_kb < 10**7 else int(_rss_kb)
                _mem["rss_bytes"] = _rss_b
                _mem["rss_mb"]    = round(_rss_b / (1024*1024), 3)
                _mem["source"]    = "resource"
            except Exception:
                pass

    _win_sec  = int(_os.getenv("HEALTH_5XX_WINDOW_SEC", "600"))
    try:
        _p5xx_re = __import__("re").compile(_os.getenv("HEALTH_5XX_REGEX", r'(?i)\\b(5\\d\\d)\\b'))
    except Exception:
        _p5xx_re = __import__("re").compile(r'(?i)\\b(5\\d\\d)\\b')
    _http_5xx_count = 0
    try:
        import time as _time
        _now3 = _time.time()
        _cut = _now3 - _win_sec
        _max_bytes = 250_000
        with open(_log_path, "r", encoding="utf-8", errors="replace") as _f:
            _f.seek(0, _os.SEEK_END)
            _pos = max(0, _f.tell() - _max_bytes)
            _f.seek(_pos)
            _chunk = _f.read()
        _ts_re = __import__("re").compile(r"(20\\d\\d-\\d\\d-\\d\\d \\d\\d:\\d\\d:\\d\\d)")
        for _ln in _chunk.splitlines():
            if not _p5xx_re.search(_ln):
                continue
            _m = _ts_re.search(_ln)
            if _m:
                try:
                    import datetime as _dt, time as _time
                    _t = _time.mktime(_dt.datetime.strptime(_m.group(1), "%Y-%m-%d %H:%M:%S").timetuple())
                    if _t >= _cut:
                        _http_5xx_count += 1
                except Exception:
                    _http_5xx_count += 1
            else:
                _http_5xx_count += 1
    except Exception:
        pass

    _free_mb = _disk.get("free", 0) // (1024 * 1024)
    _status = "ok"
    if _free_mb < int(_os.getenv("HEALTH_MIN_FREE_MB", "500")):
        _status = "degraded"
    if not _checks["git_present"] or not _checks["make_present"]:
        _status = "degraded"

    return jsonify({
        "ok": True,
        "status": _status,
        "uptime_sec": float(_uptime),
        "started_at": _dt.datetime.utcfromtimestamp(_start_ts).isoformat() + "Z",
        "disk": _disk,
        "checks": _checks,
        "python": _sys.version,
        "cwd": _os.getcwd(),
        "cpu_count": int(_cpu_count),
        "loadavg": { "raw": _load_raw, "per_cpu": _load_per_cpu },
        "errors_last_5m": int(_errors_last_5m),
        "memory": _mem,
        "http_5xx": {"count": int(_http_5xx_count), "window_sec": int(_win_sec)},
        "log_file": _log_path
    })
'''

METRICS_ROUTE = r'''
# --- Supersonic: /metrics endpoint (JSON + Prom) ---
from flask import request, Response
import os as _os, time as _time, json as _json, shutil as _shutil

def _ss_require_key():
    want = _os.getenv("DOCTOR_KEY", "")
    got  = request.headers.get("X-Doctor-Key", "")
    return (not want) or (got == want)

def _ss_disk():
    try:
        du = _shutil.disk_usage(".")
        return {"total": int(du.total), "used": int(du.used), "free": int(du.free)}
    except Exception as e:
        return {"total": 0, "used": 0, "free": 0, "error": str(e)}

def _ss_cpu_load():
    try:
        cpus = max(1, (_os.cpu_count() or 1))
    except Exception:
        cpus = 1
    raw = per = None
    try:
        if hasattr(_os, "getloadavg"):
            l1, l5, l15 = _os.getloadavg()
            raw = [l1, l5, l15]
            per = [round(l1/cpus,4), round(l5/cpus,4), round(l15/cpus,4)]
    except Exception:
        pass
    return {"cpu_count": cpus, "raw": raw, "per_cpu": per}

def _ss_memory():
    mem = {"rss_bytes": None, "vms_bytes": None, "rss_mb": None, "vms_mb": None, "source": "unknown"}
    try:
        import psutil as _ps
        p = _ps.Process()
        mi = p.memory_info()
        mem["rss_bytes"] = int(getattr(mi, "rss", 0))
        mem["vms_bytes"] = int(getattr(mi, "vms", 0))
        mem["rss_mb"]    = round(mem["rss_bytes"]/(1024*1024),3)
        mem["vms_mb"]    = round(mem["vms_bytes"]/(1024*1024),3)
        mem["source"]    = "psutil"
        return mem
    except Exception:
        pass
    try:
        page = _os.sysconf("SC_PAGE_SIZE")
        with open("/proc/self/statm","r") as f:
            vals = f.read().strip().split()
        rss_pages = int(vals[1]) if len(vals) > 1 else 0
        rss = rss_pages * page
        mem["rss_bytes"] = int(rss)
        mem["rss_mb"] = round(rss/(1024*1024),3)
        mem["source"] = "proc/statm"
        return mem
    except Exception:
        pass
    try:
        import resource
        ru = resource.getrusage(resource.RUSAGE_SELF)
        rss_kb = getattr(ru, "ru_maxrss", 0)
        rss_b  = int(rss_kb*1024) if rss_kb < 10**7 else int(rss_kb)
        mem["rss_bytes"] = rss_b
        mem["rss_mb"]    = round(rss_b/(1024*1024),3)
        mem["source"]    = "resource"
    except Exception:
        pass
    return mem

def _ss_recent_errors_and_5xx():
    import time as _t
    import datetime as _dt
    log_path = _os.getenv("SUPERSONIC_LOG_FILE", "supersonic.log")
    err_rx  = _os.getenv("HEALTH_ERROR_PATTERNS", r"(?i)\\bERROR\\b|\\bTraceback\\b")
    win_sec = int(_os.getenv("HEALTH_5XX_WINDOW_SEC","600"))
    p5xx    = _os.getenv("HEALTH_5XX_REGEX", r"(?i)\\b(5\\d\\d)\\b")

    try:
        err_re = __import__("re").compile(err_rx)
    except Exception:
        err_re = __import__("re").compile(r"(?i)\\bERROR\\b|\\bTraceback\\b")
    try:
        p5xx_re = __import__("re").compile(p5xx)
    except Exception:
        p5xx_re = __import__("re").compile(r"(?i)\\b(5\\d\\d)\\b")

    errors_5m = 0
    http5xx   = 0
    now  = _t.time()
    cut5 = now - 300.0
    cutx = now - win_sec

    max_bytes = 300_000
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, _os.SEEK_END)
            size = f.tell()
            pos  = max(0, size - max_bytes)
            f.seek(pos)
            chunk = f.read()
    except FileNotFoundError:
        return {"errors_last_5m": 0, "http_5xx": {"count": 0, "window_sec": win_sec}, "log_file": log_path}
    except Exception:
        return {"errors_last_5m": None, "http_5xx": {"count": None, "window_sec": win_sec}, "log_file": log_path}

    ts_re = __import__("re").compile(r"(20\\d\\d-\\d\\d-\\d\\d \\d\\d:\\d\\d:\\d\\d)")
    for ln in chunk.splitlines():
        m_ts = ts_re.search(ln)
        t = None
        if m_ts:
            try:
                t = _t.mktime(_dt.datetime.strptime(m_ts.group(1), "%Y-%m-%d %H:%M:%S").timetuple())
            except Exception:
                t = None
        if err_re.search(ln):
            if t is None or t >= cut5:
                errors_5m += 1
        if p5xx_re.search(ln):
            if t is None or t >= cutx:
                http5xx += 1

    return {
        "errors_last_5m": int(errors_5m),
        "http_5xx": {"count": int(http5xx), "window_sec": int(win_sec)},
        "log_file": log_path
    }

def _ss_uptime_start():
    try:
        import json
        p = Path(".supersonic_start.json")
        if p.exists():
            j = json.loads(p.read_text(encoding="utf-8"))
            return float(j.get("ts", 0.0)), int(j.get("pid", 0))
    except Exception:
        pass
    return None, None

@app.route("/metrics")
def supersonic_metrics():
    if not _ss_require_key():
        return jsonify({"ok": False, "error": "invalid key"}), 401

    disk  = _ss_disk()
    load  = _ss_cpu_load()
    mem   = _ss_memory()
    errs5 = _ss_recent_errors_and_5xx()
    ts, pid = _ss_uptime_start()
    now = _time.time()
    uptime = (now - ts) if ts else None

    payload = {
        "ok": True,
        "pid": pid,
        "uptime_sec": uptime,
        "disk": disk,
        "loadavg": {"cpu_count": load.get("cpu_count"), "raw": load.get("raw"), "per_cpu": load.get("per_cpu")},
        "memory": mem,
        "errors_last_5m": errs5.get("errors_last_5m"),
        "http_5xx": errs5.get("http_5xx"),
        "log_file": errs5.get("log_file"),
        "health_min_free_mb": int(_os.getenv("HEALTH_MIN_FREE_MB","500")),
    }

    want_prom = ("format" in request.args and request.args.get("format") == "prom") or \
                ("text/plain" in request.headers.get("Accept",""))
    if not want_prom:
        return jsonify(payload)

    def line(k, v, labels=None):
        if v is None: return ""
        lab = ""
        if labels:
            parts = []
            for kk, vv in labels.items():
                # Escape backslashes and quotes for Prometheus label values
                bs = chr(92)  # backslash
                qt = chr(34)  # double-quote
                val_str = str(vv).replace(bs, bs+bs).replace(qt, bs+qt)
                parts.append(f'{kk}="{val_str}"')
            inner = ",".join(parts)
            lab = "{" + inner + "}"
        return f"{k}{lab} {v}\n"

    prom = []
    prom.append("# HELP app_uptime_seconds Process uptime seconds\n# TYPE app_uptime_seconds gauge\n")
    prom.append(line("app_uptime_seconds", round(uptime or 0, 3)))
    prom.append("# HELP app_disk_bytes Disk usage in bytes\n# TYPE app_disk_bytes gauge\n")
    for k in ("total","used","free"):
        prom.append(line("app_disk_bytes", disk.get(k), {"kind": k}))
    if payload["loadavg"].get("raw"):
        prom.append("# HELP app_load_avg Load average\n# TYPE app_load_avg gauge\n")
        prom.append(line("app_load_avg", payload["loadavg"]["raw"][0], {"window":"1m"}))
        prom.append(line("app_load_avg", payload["loadavg"]["raw"][1], {"window":"5m"}))
        prom.append(line("app_load_avg", payload["loadavg"]["raw"][2], {"window":"15m"}))
    if payload["loadavg"].get("per_cpu"):
        prom.append("# HELP app_load_avg_per_cpu Load average normalized per CPU\n# TYPE app_load_avg_per_cpu gauge\n")
        prom.append(line("app_load_avg_per_cpu", payload["loadavg"]["per_cpu"][0], {"window":"1m"}))
        prom.append(line("app_load_avg_per_cpu", payload["loadavg"]["per_cpu"][1], {"window":"5m"}))
        prom.append(line("app_load_avg_per_cpu", payload["loadavg"]["per_cpu"][2], {"window":"15m"}))
    prom.append("# HELP app_memory_bytes Memory usage\n# TYPE app_memory_bytes gauge\n")
    if mem.get("rss_bytes") is not None:
        prom.append(line("app_memory_bytes", mem["rss_bytes"], {"type":"rss"}))
    if mem.get("vms_bytes") is not None:
        prom.append(line("app_memory_bytes", mem["vms_bytes"], {"type":"vms"}))
    prom.append("# HELP app_errors_recent Recent error lines (5m window)\n# TYPE app_errors_recent gauge\n")
    prom.append(line("app_errors_recent", errs5.get("errors_last_5m")))
    prom.append("# HELP app_http_5xx_recent Recent HTTP 5xx lines (rolling window)\n# TYPE app_http_5xx_recent gauge\n")
    http5 = errs5.get("http_5xx") or {}
    prom.append(line("app_http_5xx_recent", http5.get("count"), {"window_sec": http5.get("window_sec")}))
    body = "".join(prom)
    return Response(body, status=200, headers={"Content-Type":"text/plain; version=0.0.4; charset=utf-8"})
# --- end Supersonic /metrics ---
'''

def ensure_imports(src: str) -> str:
    need = "from flask import Flask, jsonify, request"
    if "from flask import render_template, jsonify, request" in src or "from flask import Flask, jsonify, request" in src:
        return src
    if "from flask import Flask" in src:
        return src.replace("from flask import Flask", "from flask import Flask, jsonify, request")
    m = re.search(r"from\s+flask\s+import\s+.*", src)
    if m:
        line_end = src.find("\n", m.start())
        return src[:line_end+1] + "from flask import jsonify, request\n" + src[line_end+1:]
    return src

def inject_rotating_handler(src: str) -> str:
    if "FILE_LOGGER_READY" in src or "RotatingFileHandler(" in src:
        return src
    ins_at = src.find("\n", src.find("import os")) if "import os" in src else src.find("\n")
    if ins_at == -1: ins_at = 0
    return src[:ins_at+1] + ROTATING_HANDLER_SNIPPET + src[ins_at+1:]

def inject_after_request(src: str) -> str:
    if "_supersonic_after(resp)" in src and "_supersonic_req_start()" in src:
        return src
    blk_start = src.find("# --- Supersonic Control Panel & Health Endpoints")
    blk_end   = src.find("# --- end Supersonic ---")
    if blk_start != -1 and blk_end != -1:
        region = src[blk_start:blk_end]
        if "_supersonic_after(" in region:
            return src
        patched_region = region + "\n" + AFTER_REQUEST_SNIPPET + "\n"
        return src[:blk_start] + patched_region + src[blk_end:]
    m = re.search(r"\bapp\s*=\s*Flask\s*\(", src)
    if m:
        ins = src.find("\n", m.end())
        return src[:ins+1] + AFTER_REQUEST_SNIPPET + src[ins+1:]
    return src.rstrip() + "\n\n" + AFTER_REQUEST_SNIPPET + "\n"

def install_or_upgrade_health(src: str) -> str:
    rx_def = re.compile(r"@app\.route\(\s*[\"']\/health[\"']\s*\)", re.MULTILINE)
    if rx_def.search(src):
        rx_block = re.compile(
            r'@app\.route\(\s*["\']\/health["\']\s*\)[\s\S]*?(?=^\s*@app\.route|\Z)',
            re.MULTILINE
        )
        return rx_block.sub(HEALTH_BASE_FUNC + "\n", src, count=1)
    else:
        blk_end = src.find("# --- end Supersonic ---")
        if blk_end != -1:
            return src[:blk_end] + HEALTH_BASE_FUNC + "\n" + src[blk_end:]
        return src.rstrip() + "\n\n" + HEALTH_BASE_FUNC + "\n"

def install_metrics(src: str) -> str:
    # Always upgrade/replace the metrics endpoint to ensure latest version
    rx_def = re.compile(r"@app\.route\(\s*[\"']\/metrics[\"']\s*\)", re.MULTILINE)
    if rx_def.search(src):
        # Remove old metrics block and insert new one
        rx_block = re.compile(
            r'# --- Supersonic: /metrics endpoint.*?# --- end Supersonic /metrics ---',
            re.DOTALL
        )
        src = rx_block.sub("", src)
    blk_end = src.find("# --- end Supersonic ---")
    if blk_end != -1:
        return src[:blk_end] + METRICS_ROUTE + "\n" + src[blk_end:]
    return src.rstrip() + "\n\n" + METRICS_ROUTE + "\n"

def status_report(src: str) -> dict:
    return {
        "rotating_logger": ("FILE_LOGGER_READY" in src or "RotatingFileHandler(" in src),
        "req_resp_hooks": ("_supersonic_after(resp)" in src and "_supersonic_req_start()" in src),
        "health_endpoint": ("/health" in src and "supersonic_health" in src),
        "metrics_endpoint": ("/metrics" in src and "supersonic_metrics" in src),
    }

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Supersonic Bootstrapper")
    ap.add_argument("--all", action="store_true", help="Install/upgrade all components")
    ap.add_argument("--status", action="store_true", help="Print status of installed components")
    ap.add_argument("--revert", action="store_true", help="Revert to most recent backup")
    ap.add_argument("--no-reload", action="store_true", help="Do not touch .hotreload")
    args = ap.parse_args()

    if not SERVER.exists():
        die("serve_pdfs.py not found in project root.")

    if args.revert:
        bak = latest_backup()
        if bak is None:
            die("No backups found (serve_pdfs.py.bak.*).")
        # Type checker: bak is now guaranteed to be Path
        assert bak is not None
        shutil.copy2(bak, SERVER)
        ok(f"Reverted to {bak.name}")
        if not args.no_reload: touch_hotreload()
        return

    src = SERVER.read_text(encoding="utf-8", errors="ignore")

    if args.status and not args.all:
        rep = status_report(src)
        print(json.dumps(rep, indent=2))
        return

    if args.all:
        backup()
        out = src
        out = ensure_imports(out)
        out = inject_rotating_handler(out)
        out = inject_after_request(out)
        out = install_or_upgrade_health(out)
        out = install_metrics(out)
        if out != src:
            SERVER.write_text(out, encoding="utf-8")
            ok("Supersonic stack installed/upgraded.")
            if not args.no_reload:
                touch_hotreload()
        else:
            warn("No changes applied (already up-to-date).")
        rep = status_report(out)
        print("Status:", json.dumps(rep, indent=2))
        return

    ap.print_help()

if __name__ == "__main__":
    main()
