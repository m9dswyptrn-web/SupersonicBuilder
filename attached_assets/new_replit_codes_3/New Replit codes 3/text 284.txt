#!/usr/bin/env python3
# Creates/patches everything for:
# - Local LLM backend (llama.cpp via llama-cpp-python)
# - Agent loader (no brittle edits to your current agent)
# - Flask UI integration with LLM agent
# - GGUF downloader + run scripts
# - Tauri desktop wrapper (Rust)
# - package.json patched with tauri scripts
#
# Idempotent: safe to run multiple times.

import json, os, re, stat, sys, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def write(path: Path, content: str, executable: bool=False, overwrite: bool=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        # leave existing (idempotent)
        print(f"→ exists {path} (kept)")
        return False
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"→ wrote {path}")
    return True

def ensure_line_in_file(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(line + "\n", encoding="utf-8")
        print(f"→ created {path} with line")
        return
    txt = path.read_text(encoding="utf-8").splitlines()
    if line.strip() not in [t.strip() for t in txt]:
        txt.append(line)
        path.write_text("\n".join(txt) + "\n", encoding="utf-8")
        print(f"→ appended to {path}")
    else:
        print(f"→ {path} already includes required line")

def patch_package_json():
    pj = ROOT / "package.json"
    if pj.exists():
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    else:
        data = {"name": "sonicbuilder-app", "private": True}

    dev = data.setdefault("devDependencies", {})
    if "@tauri-apps/cli" not in dev:
        dev["@tauri-apps/cli"] = "^1.6.0"

    scripts = data.setdefault("scripts", {})
    scripts.setdefault("tauri:dev", "tauri dev")
    scripts.setdefault("tauri:build", "tauri build")

    pj.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("→ patched package.json (tauri devDependencies + scripts)")

# ------------------- Agent LLM backend -------------------

AGENT_LLMBACKEND = """\
# agent/llm_backend.py
import os
from pathlib import Path
from typing import Iterable, Optional
from dotenv import load_dotenv
load_dotenv()

LLM_MODEL = os.getenv("AGENT_MODEL", "gguf/llama-3.1-8b-q4_0.gguf")

class LLM:
    \"\"\"Thin wrapper around llama.cpp via llama-cpp-python.\"\"\"
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or LLM_MODEL
        self._llm = None

    def _ensure_loaded(self):
        if self._llm is not None:
            return
        from llama_cpp import Llama  # lazy import
        mp = Path(self.model_path)
        if not mp.exists():
            raise FileNotFoundError(f"LLM model not found at {mp}. Set AGENT_MODEL or place a .gguf there.")
        self._llm = Llama(
            model_path=str(mp),
            n_ctx=int(os.getenv("LLM_CTX", "4096")),
            n_threads=int(os.getenv("LLM_THREADS", "0")) or None,
            verbose=False,
        )

    def generate(self, prompt: str, system: str = "", max_tokens: int = 512, temperature: float = 0.7) -> str:
        self._ensure_loaded()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        out = self._llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return out["choices"][0]["message"]["content"].strip()
"""

AGENT_MAIN_LLM = """\
# agent/main_llm.py
import os
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv
load_dotenv()

DOCS_DIR = Path(os.getenv("DOCS_DIR","docs"))
MEMORY_DIR = Path(os.getenv("MEMORY_DIR","agent/memory"))
SKILLS_DIR = Path(os.getenv("SKILLS_DIR","agent/skills"))
EMBED_MODEL = os.getenv("EMBED_MODEL","bge-small")

# RAG minimal (Chroma + sentence-transformers)
import chromadb
from sentence_transformers import SentenceTransformer

class RAG:
    def __init__(self, embed_model: str):
        self.model = SentenceTransformer(embed_model)
        self.client = chromadb.PersistentClient(path=str(MEMORY_DIR / "chroma"))
        self.collection = self.client.get_or_create_collection("kb")

    def embed(self, texts: List[str]):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def add_doc(self, doc_id: str, text: str, meta: Dict[str,Any]=None):
        self.collection.upsert(ids=[doc_id], documents=[text], metadatas=[meta or {}],
                               embeddings=self.embed([text]))

    def search(self, query: str, k: int=5):
        res = self.collection.query(query_embeddings=self.embed([query]), n_results=k)
        hits=[]
        for i, did in enumerate(res.get("ids",[[]])[0]):
            hits.append({"id": did,"text": res["documents"][0][i],"meta": res["metadatas"][0][i]})
        return hits

# SkillPacks
import yaml
class SkillPack:
    def __init__(self, folder: Path):
        self.folder = folder
        self.skills = []
        for y in sorted(folder.glob("*.yml")):
            with open(y, "r", encoding="utf-8") as f:
                self.skills.append({"file": y.name, **(yaml.safe_load(f) or {})})
    def list(self): return self.skills

from agent.llm_backend import LLM

SYS_PROMPT = (
    "You are Supersonic Tech Agent. Be concise, cite file paths from context when relevant. "
    "If a wiring or DSP task is requested, outline exact steps and common pitfalls."
)

class Agent:
    def __init__(self):
        self.rag = RAG(EMBED_MODEL)
        self.skills = SkillPack(SKILLS_DIR)
        self.llm = LLM()

    def ingest_dir(self, root: Path):
        for p in root.rglob("*.md"):
            text = p.read_text("utf-8", errors="ignore")
            self.rag.add_doc(str(p), text, {"path": str(p)})
        return "ingested"

    def query(self, q: str):
        ctx = self.rag.search(q, k=5)
        context_text = "\\n\\n".join(f"[{i+1}] {h['meta'].get('path','')}:\\n{h['text'][:1200]}"
                                     for i, h in enumerate(ctx))
        prompt = (f"Question:\\n{q}\\n\\nContext (may be partial):\\n{context_text}\\n\\n"
                  "Answer with numbered steps when relevant and cite paths [1], [2], ...")
        try:
            answer = self.llm.generate(prompt, system=SYS_PROMPT, max_tokens=512)
        except Exception as e:
            paths = "\\n".join(f"- {h['meta'].get('path','')}" for h in ctx)
            answer = f"(LLM not ready) {e}\\nRelated files:\\n{paths}"
        return {"answer": answer, "context_hits": [h["meta"].get("path","") for h in ctx], "skills": self.skills.list()}
"""

AGENT_SKILL_EXAMPLE = """\
name: wiring_mapper
version: 1
description: Map automotive wiring harnesses and generate pinout summaries.
tools:
  - name: pinout_summarize
    args: [photo_path, notes]
    returns: markdown
fewshot:
  - input: "Summarize GM 44-pin RADPB-44-1AK harness"
    steps:
      - tool: pinout_summarize
        with: { photo_path: "photos/radpb44.jpg", notes: "LTZ trim, OE mic present" }
"""

def patch_agent_requirements():
    req = ROOT / "agent" / "requirements.txt"
    ensure_line_in_file(req, "llama-cpp-python==0.3.2")

    # minimal deps to ensure main_llm works if agent/requirements.txt is new
    ensure_line_in_file(req, "chromadb==0.5.5")
    ensure_line_in_file(req, "sentence-transformers==3.1.1")
    ensure_line_in_file(req, "python-dotenv==1.0.1")
    ensure_line_in_file(req, "numpy==1.26.4")

# ------------------- Desktop Web UI integration -------------------

WEB_REQ = "flask==3.0.3\npython-dotenv==1.0.1\n"

AGENT_LOADER = """\
# desktop/webui/agent_loader.py
# Prefer LLM-enabled agent if present; fall back to legacy agent.main
import importlib

def load_agent():
    try:
        mod = importlib.import_module("agent.main_llm")
        return mod.Agent()
    except Exception:
        try:
            mod = importlib.import_module("agent.main")
            return mod.Agent()
        except Exception as e:
            raise RuntimeError(f"No usable Agent found: {e}")
"""

WEB_APP = """\
# desktop/webui/app.py
import os
from pathlib import Path
from flask import Flask, request, render_template_string, jsonify
from dotenv import load_dotenv
load_dotenv()

import sys, importlib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from desktop.webui.agent_loader import load_agent

PORT = int(os.getenv("PORT", "7860"))
agent = load_agent()

TPL = '''
<!doctype html>
<title>Supersonic Local</title>
<h1>Supersonic Local (Offline)</h1>
<form method="post" action="/ask">
  <input name="q" style="width:70%" placeholder="Ask the agent..." />
  <button>Ask</button>
</form>
<pre>{{ resp }}</pre>
'''

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TPL, resp="")

@app.route("/ask", methods=["POST"])
def ask():
    q = request.form.get("q","").strip()
    out = agent.query(q)
    return render_template_string(TPL, resp=out)

@app.route("/api/ingest", methods=["POST"])
def ingest():
    status = "ingested"
    try:
        d = Path(os.getenv("DOCS_DIR","docs"))
        status = agent.ingest_dir(d)
    except Exception as e:
        status = f"error: {e}"
    return jsonify({"status": status})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
"""

def ensure_webui():
    write(ROOT / "desktop" / "webui" / "requirements.txt", WEB_REQ)
    # Don't clobber an existing app.py; only write if missing
    write(ROOT / "desktop" / "webui" / "app.py", WEB_APP, overwrite=False)
    write(ROOT / "desktop" / "webui" / "agent_loader.py", AGENT_LOADER, overwrite=True)

# ------------------- Scripts: model download & runner -------------------

DL_GGUF = """\
#!/usr/bin/env python3
import sys, shutil
from pathlib import Path
import urllib.request

URL = "https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q4_K_M.gguf?download=true"
DEST = Path("gguf/llama-3.1-8b-q4_0.gguf")

DEST.parent.mkdir(parents=True, exist_ok=True)
print(f"Downloading to {DEST} ...")
with urllib.request.urlopen(URL) as r, open(DEST, "wb") as f:
    shutil.copyfileobj(r, f)
print("Done.")
"""

RUN_LLM = """\
#!/usr/bin/env python3
import os, subprocess, sys
os.environ.setdefault("APP_MODE", "offline")
os.environ.setdefault("AGENT_MODEL", "gguf/llama-3.1-8b-q4_0.gguf")
subprocess.run([sys.executable, "desktop/webui/app.py"], check=False)
"""

# ------------------- Tauri wrapper -------------------

CARGO_TOML = """\
[package]
name = "supersonic-desktop"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "1.6", features = ["shell-open"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"

[build-dependencies]
tauri-build = { version = "1" }
"""

TAURI_CONF = """\
{
  "package": {
    "productName": "Supersonic",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "shell": { "all": true },
      "open": true
    },
    "windows": [
      {
        "title": "Supersonic",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false,
        "url": "http://127.0.0.1:7860"
      }
    ],
    "bundle": {
      "active": true,
      "identifier": "com.yourname.supersonic",
      "targets": "all"
    }
  },
  "build": {
    "beforeBuildCommand": "",
    "beforeDevCommand": "",
    "devPath": "http://127.0.0.1:7860",
    "distDir": "http://127.0.0.1:7860"
  }
}
"""

MAIN_RS = r"""\
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::{thread, time::Duration};

fn launch_python() -> Result<(), String> {
    Command::new("python")
        .args(["scripts/run_offline_llm.py"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("failed to start python: {e}"))?;
    thread::sleep(Duration::from_millis(1200));
    Ok(())
}

fn main() {
    // Fire-and-forget Python on app start (best-effort)
    let _ = launch_python();

    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running Supersonic");
}
"""

def ensure_tauri():
    write(ROOT / "src-tauri" / "Cargo.toml", CARGO_TOML, overwrite=False)
    write(ROOT / "src-tauri" / "tauri.conf.json", TAURI_CONF, overwrite=False)
    write(ROOT / "src-tauri" / "src" / "main.rs", MAIN_RS, overwrite=True)

# ------------------- Minimal docs dir (RAG seed) -------------------

def ensure_docs_seed():
    d = ROOT / "docs"
    d.mkdir(parents=True, exist_ok=True)
    if not any(d.glob("*.md")):
        write(d / "hello.md", "# Hello Supersonic\n\nAdd your docs here for RAG.", overwrite=False)

# ------------------- Agent skill & memory dirs -------------------

def ensure_agent_dirs():
    write(ROOT / "agent" / "llm_backend.py", AGENT_LLMBACKEND, overwrite=True)
    write(ROOT / "agent" / "main_llm.py", AGENT_MAIN_LLM, overwrite=False)
    write(ROOT / "agent" / "skills" / "wiring_mapper.yml", AGENT_SKILL_EXAMPLE, overwrite=False)
    (ROOT / "agent" / "memory").mkdir(parents=True, exist_ok=True)
    patch_agent_requirements()

# ------------------- Scripts -------------------

def ensure_scripts():
    write(ROOT / "scripts" / "download_gguf.py", DL_GGUF, executable=True, overwrite=False)
    write(ROOT / "scripts" / "run_offline_llm.py", RUN_LLM, executable=True, overwrite=True)

# ------------------- Bootstrap -------------------

def main():
    print("=== Agent LLM + Tauri Bootstrap ===")
    ensure_agent_dirs()
    ensure_webui()
    ensure_docs_seed()
    ensure_scripts()
    ensure_tauri()
    patch_package_json()

    # Helpful .env.sample for defaults
    env_sample = """\
APP_MODE=offline
PORT=7860
AGENT_MODEL=gguf/llama-3.1-8b-q4_0.gguf
EMBED_MODEL=bge-small
MEMORY_DIR=agent/memory
SKILLS_DIR=agent/skills
DOCS_DIR=docs
"""
    write(ROOT / ".env.sample", env_sample, overwrite=False)

    print("\n✅ Bootstrap complete.")
    print("\nNext steps:")
    print("  1) python3 -m pip install --upgrade pip")
    print("  2) pip install -r agent/requirements.txt -r desktop/webui/requirements.txt")
    print("  3) python scripts/download_gguf.py   # or place your own GGUF at AGENT_MODEL path")
    print("  4) python scripts/run_offline_llm.py # open http://127.0.0.1:7860")
    print("  5) npm i                             # installs @tauri-apps/cli")
    print("  6) npm run tauri:dev                 # desktop app (dev)")
    print("  7) npm run tauri:build               # build .app/.msi/.AppImage\n")
    print("If Python is not on PATH inside Tauri, edit src-tauri/src/main.rs to point to your python/venv path.")

if __name__ == "__main__":
    main()