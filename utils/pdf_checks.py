
from pathlib import Path
from typing import Iterable
def _info(msg): print("[pdf] •", msg)
def _ok(msg): print("[pdf] ✅", msg)
def _bad(msg): print("[pdf] ❌", msg)

def check_existing_pdfs(output_dir: str, open_test: bool = True) -> bool:
    p = Path(output_dir)
    if not p.exists():
        return True
    ok = True
    pdfs = list(p.glob("*.pdf"))
    if not pdfs:
        _info("no PDFs to check yet")
        return True
    if open_test:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            _info("pypdf not installed; skipping PDF open test")
            return ok
        for pdf in pdfs:
            try:
                _ = PdfReader(str(pdf))
                _ok(f"opened: {pdf.name}")
            except Exception as e:
                _bad(f"failed to open {pdf.name}: {e}")
                ok = False
    return ok

def check_pdf_openable(pdf_paths: Iterable[str]) -> bool:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        _info("pypdf not installed; skipping open check")
        return True
    ok = True
    for p in pdf_paths:
        try:
            _ = PdfReader(str(p))
            _ok(f"opened: {Path(p).name}")
        except Exception as e:
            _bad(f"failed to open {p}: {e}")
            ok = False
    return ok
