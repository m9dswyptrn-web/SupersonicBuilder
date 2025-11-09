#!/usr/bin/env python3
"""
rotating_logger.py — size-rotating logger with gzip + pruning + request logging helpers.
Env:
  APP_LOG_PATH (default logs/app.log)
  APP_LOG_MAX_BYTES (default 1048576)
  APP_LOG_KEEP_FILES (default 7)
  APP_LOG_MAX_TOTAL_MB (default 50)
  APP_LOG_LEVEL (default INFO)
"""
import os, sys, gzip, shutil
from pathlib import Path
from datetime import datetime
import logging
from logging import Logger, Handler, LogRecord

APP_LOG_PATH       = Path(os.getenv("APP_LOG_PATH", "logs/app.log"))
APP_ARCHIVE_DIR    = APP_LOG_PATH.parent / "archive"
APP_LOG_MAX_BYTES  = int(os.getenv("APP_LOG_MAX_BYTES", str(1 * 1024 * 1024)))
APP_LOG_KEEP_FILES = int(os.getenv("APP_LOG_KEEP_FILES", "7"))
APP_LOG_MAX_TOTAL_MB = int(os.getenv("APP_LOG_MAX_TOTAL_MB", "50"))

def _ensure_dirs():
    APP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    APP_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def _rotate_if_needed():
    try:
        if not APP_LOG_PATH.exists() or APP_LOG_PATH.stat().st_size < APP_LOG_MAX_BYTES: return
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        raw = APP_ARCHIVE_DIR / f"app.{ts}.log"
        gz  = APP_ARCHIVE_DIR / f"app.{ts}.log.gz"
        shutil.move(str(APP_LOG_PATH), raw)
        with open(raw, "rb") as fin, gzip.open(gz, "wb", compresslevel=6) as fout:
            shutil.copyfileobj(fin, fout)
        raw.unlink(missing_ok=True)
        # keep last N
        archives = sorted(APP_ARCHIVE_DIR.glob("app.*.log.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in archives[APP_LOG_KEEP_FILES:]:
            old.unlink(missing_ok=True)
        # cap total
        def total_mb():
            return sum(p.stat().st_size for p in APP_ARCHIVE_DIR.glob("app.*.log.gz"))/(1024*1024)
        archives = sorted(APP_ARCHIVE_DIR.glob("app.*.log.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        while total_mb() > APP_LOG_MAX_TOTAL_MB and len(archives) > 1:
            victim = archives.pop(); victim.unlink(missing_ok=True)
    except Exception as e:
        print(f"[WARN] app log rotation failed: {e}", file=sys.stderr)

class _RotatingFileHandler(Handler):
    def __init__(self):
        super().__init__(); _ensure_dirs()
        self._stream = open(APP_LOG_PATH, "a", encoding="utf-8")
    def emit(self, record: LogRecord):
        try:
            msg = self.format(record)
            self._stream.write(msg + "\n"); self._stream.flush()
            _rotate_if_needed()
        except Exception as e:
            try: self.handleError(record)
            except Exception: print(f"[WARN] logging error: {e}", file=sys.stderr)
    def close(self):
        try: self._stream.close()
        except Exception: pass
        super().close()

_formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
                               datefmt="%Y-%m-%d %H:%M:%S")

def get_logger(name: str = "app") -> Logger:
    level_name = os.getenv("APP_LOG_LEVEL","INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger = logging.getLogger(name)
    if getattr(logger, "_supersonic_configured", False): return logger
    logger.setLevel(level)
    handler = _RotatingFileHandler(); handler.setFormatter(_formatter)
    logger.addHandler(handler)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console = logging.StreamHandler(sys.stdout); console.setLevel(level); console.setFormatter(_formatter)
        logger.addHandler(console)
    logger.propagate=False; logger._supersonic_configured=True
    logger.debug("Rotating logger initialized")
    return logger

class RequestLogMiddleware:
    """ASGI middleware (FastAPI/Starlette) to log method/path/status/time/client."""
    def __init__(self, app, logger: Logger | None = None):
        self.app = app; self.log = logger or get_logger("http")
    async def __call__(self, scope, receive, send):
        if scope["type"]!="http": return await self.app(scope, receive, send)
        method=scope.get("method"); path=scope.get("path"); client=scope.get("client")
        host=f"{client[0]}:{client[1]}" if client else "-"
        from time import perf_counter
        t0=perf_counter(); status_holder={"status":0}
        async def send_wrapper(event):
            if event["type"]=="http.response.start": status_holder["status"]=event["status"]
            await send(event)
        try: await self.app(scope, receive, send_wrapper)
        finally:
            ms=int((perf_counter()-t0)*1000); self.log.info("%s %s %s %dms", method, path, host, ms)

def wsgi_request_logger(app, logger: Logger | None = None):
    """WSGI wrapper (Flask) to log method/path/remote/time."""
    log = logger or get_logger("http")
    def middleware(environ, start_response):
        from time import perf_counter
        t0=perf_counter()
        def _start_response(status, headers, exc_info=None):
            ms=int((perf_counter()-t0)*1000)
            log.info("%s %s %s %dms",
                     environ.get("REQUEST_METHOD","-"),
                     environ.get("PATH_INFO","-"),
                     environ.get("REMOTE_ADDR","-"),
                     ms)
            return start_response(status, headers, exc_info)
        return app(environ, _start_response)
    return middleware
