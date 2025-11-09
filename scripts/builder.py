
#!/usr/bin/env python3
# Builder patch: QR glyph in index + Back-to-Index link on each diagram page
import argparse, os, glob, yaml, csv, io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import qrcode

PAGE_SIZES = {"LETTER": letter, "A4": A4}

def read_md(p):
    if not p or not os.path.exists(p): return ""
    return open(p, "r", encoding="utf-8").read().strip()

def wrap(c, text, x, y, maxw, leading, font="Helvetica", size=11, color=colors.white):
    c.setFont(font, size); c.setFillColor(color)
    for para in text.split("\n\n"):
        line=""
        for word in para.split():
            trial=(line+" "+word).strip()
            if c.stringWidth(trial, font, size)<=maxw: line=trial
            else:
                c.drawString(x,y,line); y-=leading; line=word
        if line: c.drawString(x,y,line); y-=leading*1.2
        y-=leading*0.3
    return y

def header_footer(c,w,h,title,theme):
    c.setFont("Helvetica",8); fg = colors.white if theme=="dark" else colors.black; c.setFillColor(fg)
    c.drawCentredString(w/2, 0.4*inch, title)

def page_num(c,w,h,n,theme):
    c.setFont("Helvetica",8); fg = colors.white if theme=="dark" else colors.black; c.setFillColor(fg)
    c.drawRightString(w-0.4*inch, 0.4*inch, str(n))

def add_image(c, path, x, y, maxw, maxh):
    try:
        im = Image.open(path); iw, ih = im.size
        scale = min(maxw/iw, maxh/ih); tw, th = iw*scale, ih*scale
        c.drawImage(path, x+(maxw-tw)/2, y+(maxh-th)/2, width=tw, height=th, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        c.setFillColor(colors.red); c.drawString(x, y+maxh/2, f"[img error] {os.path.basename(path)}: {e}")

def newpage(c,theme):
    c.showPage(); w,h = c._pagesize; c.setFillColor(colors.black if theme=="dark" else colors.white); c.rect(0,0,w,h,0,1)

def list_appendix_diagrams(diagram_dir):
    exts = ("*.png","*.jpg","*.jpeg","*.svg","*.pdf")
    files = []
    for pat in exts:
        files += glob.glob(os.path.join(diagram_dir, pat))
    files = sorted(files, key=lambda p: os.path.basename(p).lower())
    return files

def titleize(name):
    base = os.path.splitext(os.path.basename(name))[0]
    base = base.replace("_"," ").replace("-"," ").strip()
    if not base: return os.path.basename(name)
    words = []
    for w in base.split():
        if len(w)<=4 and w.isupper():
            words.append(w.upper())
        else:
            words.append(w.capitalize())
    return " ".join(words)

def group_prefix(base):
    b = os.path.basename(base)
    if "_" in b: return b.split("_",1)[0].upper()
    if "-" in b: return b.split("-",1)[0].upper()
    return "MISC"

def draw_qr(c, data, x, y, size=0.9*inch):
    try:
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        c.drawImage(buf, x, y, width=size, height=size, mask='auto')
    except Exception:
        c.setFillColor(colors.red); c.setFont("Helvetica",8)
        c.drawString(x, y+size/2, "[QR error]")

def draw_qr_glyph(c, x, y, size=0.12*inch, theme="dark"):
    # Simple 3-square QR-like glyph for index lines
    fg = colors.white if theme=="dark" else colors.black
    c.setFillColor(fg); c.setStrokeColor(fg)
    c.rect(x, y, size, size, stroke=1, fill=0)               # outer
    c.rect(x+size*0.12, y+size*0.12, size*0.3, size*0.3, 1,1) # finder 1
    c.rect(x+size*0.58, y+size*0.58, size*0.3, size*0.3, 1,1) # finder 2
    c.rect(x+size*0.12, y+size*0.58, size*0.3, size*0.3, 1,1) # finder 3

def build(out, outline_path):
    cfg = yaml.safe_load(open(outline_path, "r", encoding="utf-8"))
    theme = cfg.get("theme","dark")
    page_size = PAGE_SIZES.get(cfg.get("page_size","LETTER"), letter)
    w, h = page_size
    c = canvas.Canvas(out, pagesize=page_size)
    fg = colors.white if theme=="dark" else colors.black

    # cover
    c.setFillColor(colors.black if theme=="dark" else colors.white); c.rect(0,0,w,h,0,1)
    c.setFillColor(fg); c.setFont("Helvetica-Bold", 26); c.drawCentredString(w/2, h-2*inch, cfg.get("title","Manual"))
    c.setFont("Helvetica", 14); c.drawCentredString(w/2, h-2.7*inch, f"Version {cfg.get('version','1.0.0')}")
    c.setFont("Helvetica", 12); c.drawCentredString(w/2, h-3.3*inch, f"Author: {cfg.get('author','')}")
    newpage(c, theme)

    # TOC placeholder
    c.setFont("Helvetica-Bold", 18); c.setFillColor(fg); c.drawString(1*inch, h-1.2*inch, "Table of Contents")
    y = h-1.7*inch; page = 2; toc=[]

    diagram_dir = "manual/04-Appendix/Wiring_Diagrams"

    for part in cfg.get("parts",[]):
        c.setFont("Helvetica-Bold", 14); c.drawString(1*inch, y, part.get("name","")); y -= 0.35*inch
        for ch in part.get("chapters",[]):
            title = ch.get("title","(untitled)"); mdp = ch.get("md"); text = read_md(mdp)
            ch_id = ch.get("id")
            is_diagrams = (ch_id == "diagrams")

            page += 1; toc.append((title,page))

            # Chapter header
            c.setFillColor(fg); c.setFont("Helvetica-Bold", 16); c.drawString(1*inch, h-1*inch, title)
            header_footer(c, w, h, cfg.get("title","Manual"), theme); page_num(c, w, h, page, theme)
            ytext = h-1.5*inch; ytext = wrap(c, text, 1*inch, ytext, w-2*inch, 14, size=11, color=fg)

            if is_diagrams:
                files = list_appendix_diagrams(diagram_dir)

                # Index page with legend + bookmark
                newpage(c, theme); c.bookmarkPage("WIRING_INDEX")
                header_footer(c, w, h, cfg.get("title","Manual"), theme); page += 1; page_num(c, w, h, page, theme)
                c.setFillColor(fg); c.setFont("Helvetica-Bold", 16); c.drawString(1*inch, h-1*inch, "Wiring Diagram Index")
                yidx = h-1.5*inch; c.setFont("Helvetica", 11)

                legend = ("Legend: Prefix groups speed lookup.\n"
                          "AUDIO = Audio system, CAN = CAN/GMLAN, POWER = Power/Fusing, MISC = General.\n"
                          "Each entry shows page number and a small QR glyph indicates a QR on the diagram page.")
                for line in legend.split("\n"):
                    c.drawString(1*inch, yidx, line); yidx -= 0.22*inch
                yidx -= 0.12*inch

                groups = {}
                for f in files:
                    groups.setdefault(group_prefix(f), []).append(f)

                # Determine first diagram page
                first_diagram_page = page + 1

                # Build deterministic list
                ordered = []
                for g in sorted(groups.keys()):
                    ordered.extend(sorted(groups[g], key=lambda p: os.path.basename(p).lower()))

                # Draw grouped entries with inline page numbers + QR glyph
                for g in sorted(groups.keys()):
                    c.setFont("Helvetica-Bold", 12); c.drawString(1*inch, yidx, g.title()); yidx -= 0.25*inch
                    c.setFont("Helvetica", 11)
                    for f in sorted(groups[g], key=lambda p: os.path.basename(p).lower()):
                        idx = ordered.index(f)
                        pnum = first_diagram_page + idx
                        line = f"- {titleize(f)} — p.{pnum}"
                        # Draw text
                        c.drawString(1*inch, yidx, line)
                        # Draw tiny QR glyph at left margin
                        draw_qr_glyph(c, x=0.75*inch, y=yidx-0.02*inch, size=0.12*inch, theme=theme)
                        yidx -= 0.24*inch
                        if yidx < 1*inch:
                            newpage(c, theme); header_footer(c, w, h, cfg.get("title","Manual"), theme); page += 1; page_num(c, w, h, page, theme)
                            c.setFillColor(fg); c.setFont("Helvetica", 11); yidx = h-1*inch
                    yidx -= 0.08*inch

                # Render one diagram per page with QR + Back to Index link
                mapping = []
                for i, relp in enumerate(ordered):
                    newpage(c, theme); header_footer(c, w, h, cfg.get("title","Manual"), theme); page += 1; page_num(c, w, h, page, theme)
                    c.setFillColor(fg); c.setFont("Helvetica-Bold", 14); c.drawString(1*inch, h-1*inch, titleize(relp))
                    boxw, boxh = (w - 2*inch), (h - 3.0*inch)
                    add_image(c, relp, 1*inch, 1.2*inch, boxw, boxh)
                    # Source QR
                    spath = os.path.relpath(relp)
                    try:
                        img = qrcode.make(spath); buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
                        c.drawImage(buf, w - 1.2*inch, 0.6*inch, width=0.9*inch, height=0.9*inch, mask='auto')
                    except Exception:
                        pass
                    # Back to Index link (text + clickable area)
                    c.setFont("Helvetica-Oblique", 10)
                    c.drawString(1*inch, 0.6*inch, "↩ Back to Index")
                    # link rectangle to bookmark
                    c.linkAbsolute("back_to_index", "WIRING_INDEX", Rect=(1*inch, 0.55*inch, 2.4*inch, 0.75*inch))
                    mapping.append((spath, page))

                # write mapping CSV
                os.makedirs("assets", exist_ok=True)
                with open("assets/diagram_pages.csv", "w", newline="", encoding="utf-8") as fcsv:
                    wcsv = csv.writer(fcsv); wcsv.writerow(["source","page"])
                    for row in mapping: wcsv.writerow(row)

                newpage(c, theme)
            else:
                # Regular chapters (2 images per page)
                imgs = []
                gg = ch.get("images_glob")
                if gg: imgs += sorted(glob.glob(gg))
                chap_id = ch.get("id")
                manif = "assets/images/manifest.csv"
                if chap_id and os.path.exists(manif):
                    import csv as _csv
                    with open(manif,"r") as mf:
                        r = _csv.DictReader(mf)
                        for row in r:
                            if row.get("chapter_id")==chap_id: imgs.append(row["path"])
                cols, rows = 1,2; boxw, boxh = (w-2*inch), (h-2.5*inch)/rows; xi, yi = 1*inch, h-1.5*inch - boxh; count=0
                for ip in imgs:
                    add_image(c, ip, xi, yi, boxw, boxh); count+=1
                    if count % rows == 0:
                        newpage(c, theme); header_footer(c,w,h,cfg.get("title","Manual"),theme); page+=1; page_num(c,w,h,page,theme); yi = h-1.5*inch - boxh
                    else:
                        yi = yi - boxh
                newpage(c, theme)

    # TOC
    c.setFillColor(fg); c.setFont("Helvetica", 12); y = h-2*inch
    for title, p in toc:
        c.drawString(1*inch, y, title); c.drawRightString(w-1*inch, y, str(p)); y -= 0.3*inch
        if y < 1*inch: newpage(c, theme); c.setFillColor(fg); c.setFont("Helvetica", 12); y = h-1*inch
    c.save(); print("[ok] Built ->", out)

if __name__=="__main__":
    import sys
    out = "output/supersonic_manual_dark.pdf"
    if len(sys.argv)>1 and sys.argv[1]=="--light": out = "output/supersonic_manual_light.pdf"
    build(out, "outline.yml")
