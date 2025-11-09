#!/usr/bin/env python3
from pathlib import Path
import re, sys, traceback, py_compile

TARGET = Path("supersonic_doc_updater.py")
LINE_NO = 130

def preview(lines, i, radius=3):
    start = max(0, i - radius - 1)
    end   = min(len(lines), i + radius)
    block = []
    for n in range(start, end):
        mark = ">>" if (n+1)==i else "  "
        block.append(f"{mark} {n+1:4d}: {lines[n].rstrip()}")
    return "\n".join(block)

def escape_lone_braces(s: str) -> str:
    out = []
    depth = 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "{":
            if i+1 < len(s) and s[i+1] == "{":
                out.append("{{"); i += 2; continue
            depth += 1; out.append("{"); i += 1; continue
        if ch == "}":
            if i+1 < len(s) and s[i+1] == "}":
                out.append("}}"); i += 2; continue
            if depth == 0:
                out.append("}}"); i += 1; continue
            depth -= 1; out.append("}"); i += 1; continue
        out.append(ch); i += 1
    return "".join(out)

def patch_fstring_segment(line: str) -> str:
    def repl(m):
        quote = m.group(1)
        body  = m.group(2)
        fixed = escape_lone_braces(body)
        return f"f{quote}{fixed}{quote}"
    pattern = r"""f(['"])((?:\\.|[^\\])*?)\1"""
    return re.sub(pattern, repl, line)

def main():
    if not TARGET.exists():
        print(f"ERROR: {TARGET} not found")
        sys.exit(2)

    text = TARGET.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    if not (1 <= LINE_NO <= len(lines)):
        print(f"ERROR: file only has {len(lines)} lines, cannot address {LINE_NO}")
        sys.exit(2)

    print("Context BEFORE:\n" + preview(lines, LINE_NO))

    line = lines[LINE_NO - 1]
    fixed = patch_fstring_segment(line)

    candidate = "\n".join(lines[:LINE_NO-1] + [fixed] + lines[LINE_NO:])

    try:
        py_compile.compile(TARGET, doraise=True)
        print("File already compiles; no change made.")
        return
    except Exception:
        pass

    try:
        compile(candidate, TARGET.name, "exec")
        TARGET.write_text(candidate, encoding="utf-8")
        print("\nPatched line saved. Re-checking with py_compile…")
        py_compile.compile(TARGET, doraise=True)
        print("✅ Compile OK after patch.")
    except Exception:
        def fix_all(src: str) -> str:
            def repl(m):
                q = m.group(1); body = m.group(2)
                return f"f{q}{escape_lone_braces(body)}{q}"
            return re.sub(r"""f(['"])((?:\\.|[^\\])*?)\1""", repl, src, flags=re.S)
        candidate2 = fix_all(text)
        try:
            compile(candidate2, TARGET.name, "exec")
            TARGET.write_text(candidate2, encoding="utf-8")
            py_compile.compile(TARGET, doraise=True)
            print("✅ Compile OK after whole-file f-string brace sanitation.")
        except Exception as e:
            print("\n❌ Could not auto-fix. Leaving file unchanged.")
            print("Most common manual fixes on/around the failing f-string:")
            print("  • Close any unclosed f\"\"\"…\"\"\" block")
            print("  • Escape literal braces as {{ and }}")
            print("  • If embedding Markdown fences like ```json { … } ```, escape braces")
            print("\nContext AFTER attempted fix (not applied):\n" + preview(lines, LINE_NO))
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
