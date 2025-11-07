#!/usr/bin/env python3
import os, shutil, glob, sys, subprocess

SRC = "assets/schematics_drop_here"
DST = "manual/04-Appendix/Wiring_Diagrams"
os.makedirs(DST, exist_ok=True)
os.makedirs(SRC, exist_ok=True)

def have_mod(mod):
    try:
        __import__(mod); return True
    except Exception:
        return False

def convert_svg(svg_path, out_png):
    if have_mod("cairosvg"):
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=out_png, dpi=300)
        return True
    return False

def convert_pdf(pdf_path, out_dir):
    ok = False
    if have_mod("pdf2image"):
        from pdf2image import convert_from_path
        try:
            pages = convert_from_path(pdf_path, dpi=300)
            for i, img in enumerate(pages, 1):
                out = os.path.join(out_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_p{i:02d}.png")
                img.save(out, "PNG"); 
            ok = True
        except Exception as e:
            print("[warn] pdf2image failed:", e)
    else:
        print("[warn] pdf2image not installed; skipping PDF conversion:", os.path.basename(pdf_path))
    return ok

def main():
    copied = 0; converted = 0
    files = []
    for pat in ("*.png","*.PNG","*.jpg","*.JPG","*.jpeg","*.JPEG","*.svg","*.SVG","*.pdf","*.PDF"):
        files += glob.glob(os.path.join(SRC, pat))
    if not files:
        print("[warn] No files in", SRC); return 0

    for f in sorted(files):
        base = os.path.basename(f)
        ext = os.path.splitext(base)[1].lower()
        if ext in (".png",".jpg",".jpeg"):
            dst = os.path.join(DST, base); shutil.copy2(f, dst); copied += 1
        elif ext == ".svg":
            out_png = os.path.join(DST, os.path.splitext(base)[0] + ".png")
            if convert_svg(f, out_png):
                converted += 1
            else:
                # fallback: just copy SVG
                dst = os.path.join(DST, base); shutil.copy2(f, dst); copied += 1
                print("[warn] cairosvg not found; copied SVG without rasterizing:", base)
        elif ext == ".pdf":
            if convert_pdf(f, DST):
                converted += 1
            else:
                # fallback: copy pdf for manual reference
                dst = os.path.join(DST, base); shutil.copy2(f, dst); copied += 1
                print("[warn] PDF not converted; copied as-is:", base)
        else:
            print("[skip] Unknown type:", base)
    print(f"[ok] Schematics processed. Copied={copied}, Converted={converted}. Output -> {DST}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
