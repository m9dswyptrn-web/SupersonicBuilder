#!/usr/bin/env python3
import os, subprocess, json, argparse, textwrap, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "supersonic_settings.json"
DEFAULTS = {"engine_mode":"hybrid","summary_commit_count":8}

def load_cfg():
    data={}
    if CFG_PATH.exists():
        try: data=json.loads(CFG_PATH.read_text(encoding="utf-8"))
        except Exception: pass
    if os.getenv("SUP_ENGINE_MODE"):
        data["engine_mode"]=os.getenv("SUP_ENGINE_MODE")
    return {**DEFAULTS, **data}

CFG = load_cfg()

def _get_openai_client():
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key: return None, "OPENAI_API_KEY not set"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        return ("new", client), None
    except Exception:
        pass
    try:
        import openai
        openai.api_key = api_key
        return ("legacy", openai), None
    except Exception as e:
        return None, f"OpenAI import failed: {e}"

def _openai_respond(prompt:str)->str:
    got = _get_openai_client()[0]
    if not got: raise RuntimeError("OpenAI client not available")
    which, client = got
    model = os.getenv("OPENAI_MODEL","gpt-4o-mini")
    if which=="new":
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":"You are a concise release-notes generator."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2
        )
        return resp.choices[0].message.content.strip()
    else:
        import openai  # type: ignore
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role":"system","content":"You are a concise release-notes generator."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2
        )
        return resp["choices"][0]["message"]["content"].strip()

def _latest_commits(n=8)->str:
    try:
        out = subprocess.check_output(
            ["git","log",f"-n{n}","--pretty=format:%h %ad %s","--date=short"],
            stderr=subprocess.STDOUT
        )
        return out.decode("utf-8","ignore").strip()
    except Exception:
        return ""

def _diffstat()->str:
    try:
        out = subprocess.check_output(["git","diff","--stat","HEAD~1..HEAD"],stderr=subprocess.STDOUT)
        return out.decode("utf-8","ignore").strip()
    except Exception:
        return ""

def _local_summarize(text:str)->str:
    lines=[ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines: return "No recent commits detected. (local summary)"
    bullets=[]
    for ln in lines[:10]:
        parts=ln.split(" ",2)
        subject = parts[2] if len(parts)>=3 else ln
        bullets.append(f"- {subject}")
    return "Recent highlights (local):\n" + "\n".join(bullets)

def summarize_latest(n=None)->str:
    n=int(n or CFG["summary_commit_count"])
    commits=_latest_commits(n)
    if not commits: return "No commits found."
    mode=CFG["engine_mode"].lower()
    want_openai = (mode=="openai") or (mode=="hybrid")
    if want_openai:
        got, why = _get_openai_client()
        if got:
            prompt = textwrap.dedent(f'''
            Summarize the following recent commits into 3–6 bullet points.
            Be concrete and non-redundant; surface user-facing changes first.

            COMMITS:
            {commits}

            DIFFSTAT (optional):
            {_diffstat() or "[none]"}
            ''').strip()
            try:
                return _openai_respond(prompt)
            except Exception as e:
                if mode=="openai": return f"[OpenAI error] {e}"
    return _local_summarize(commits)

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd")
    s1=sub.add_parser("summarize"); s1.add_argument("--n",type=int,default=None)
    sub.add_parser("changelog")
    sub.add_parser("narrate")
    args=ap.parse_args()
    if args.cmd in (None,"summarize"):
        print(summarize_latest(n=getattr(args,"n",None))); return
    if args.cmd=="changelog":
        print("# Changes\n\n"+summarize_latest()); return
    if args.cmd=="narrate":
        txt=summarize_latest(); print((txt.splitlines() or ["No changes."])[0]); return

if __name__=="__main__":
    main()
