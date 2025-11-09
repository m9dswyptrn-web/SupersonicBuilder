# 2014 Chevy Sonic LTZ — Master Manual Builder
# Produces DARK/LIGHT PDFs + a bundle ZIP in /build
import os, datetime, textwrap, zipfile, argparse, hashlib, yaml
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.graphics import renderPDF, renderPM
from svglib.svglib import svg2rlg
from PyPDF2 import PdfReader
from PIL import Image, ImageOps
from tools.canvas_draw_helpers import AssetResolver, draw_image_fit, draw_svg_fit

# --- canvas helpers init ---
RES = AssetResolver('assets')

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

from src.toc_jobcards import PdfToc, render_job_cards, draw_icon
from utils.stamp_utils import get_version, build_timestamp

BASE   = os.path.abspath(".")
CONFIG = os.path.join(BASE, "config")
ASSETS = os.path.join(BASE, "assets")
BUILD  = os.path.join(BASE, "build")

SECTIONS = [
    ("RR2 + GM2 Primary Gateway",          "rr2_gm2_primary.yaml"),
    ("G-RZ-GM59 Overlay (Listen-Only)",    "grz_overlay.yaml"),
    ("AUX Chime + Bin AUX Mixer",          "aux_mixer.yaml"),
    ("DSP / Amp Stack",                    "dsp_amp_stack.yaml"),
    ("USB + HDMI Retrofit",                "usb_hdmi_retrofit.yaml"),
    ("Trigger Bus + Star Ground",          "trigger_ground.yaml"),
    ("44-Pin Radio Harness Pinout",        "pinout_44pin.yaml"),
]

BUILD_STAMP = datetime.datetime.now().strftime("Build %Y-%m-%d %H:%M")

os.makedirs(CONFIG, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(BUILD,  exist_ok=True)

def _asset_candidates(basename: str):
    """Return possible files for a logical asset name in priority order."""
    stem = basename.strip()
    return [
        os.path.join(ASSETS, f"{stem}.svg"),
        os.path.join(ASSETS, f"{stem}.png"),
        os.path.join(ASSETS, f"{stem}.jpg"),
        os.path.join(ASSETS, f"{stem}.jpeg"),
        os.path.join(ASSETS, stem),
    ]

def _first_existing(path_list):
    for p in path_list:
        if os.path.isfile(p):
            return p
    return None

def draw_image_auto(c, logical_name: str, x: float, y: float, w: float, h: float, dpi: int=300):
    """Draw an asset by logical name. Prefers SVG. Falls back to PNG/JPG."""
    if not logical_name:
        return False
    
    path = _first_existing(_asset_candidates(logical_name))
    if not path:
        return False

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".svg":
            drawing = svg2rlg(path)
            if drawing:
                px_w = int(w / 72.0 * dpi)
                px_h = int(h / 72.0 * dpi)
                img = renderPM.drawToPIL(drawing, dpi=dpi)
                img_aspect = img.width / img.height
                box_aspect = px_w / px_h if px_h else img_aspect
                if img_aspect > box_aspect:
                    target_w = px_w
                    target_h = int(px_w / img_aspect)
                else:
                    target_h = px_h
                    target_w = int(px_h * img_aspect)
                img = img.resize((target_w, target_h), resample=Image.Resampling.LANCZOS)
                img_reader = ImageReader(img)
                dx = x + (w - (target_w * 72.0 / dpi)) / 2.0
                dy = y + (h - (target_h * 72.0 / dpi)) / 2.0
                c.drawImage(img_reader, dx, dy, width=(target_w * 72.0 / dpi), height=(target_h * 72.0 / dpi), mask='auto')
                return True
        else:
            img = Image.open(path)
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            img_reader = ImageReader(img)
            iw, ih = img_reader.getSize()
            img_aspect = iw / ih
            box_aspect = (w / h) if h else img_aspect
            if img_aspect > box_aspect:
                tw = w
                th = w / img_aspect
            else:
                th = h
                tw = h * img_aspect
            dx = x + (w - tw) / 2.0
            dy = y + (h - th) / 2.0
            c.drawImage(img_reader, dx, dy, width=tw, height=th, mask='auto')
            return True
    except Exception as e:
        if ext == ".svg":
            png_alt = _first_existing([path.replace(".svg", ".png"), path.replace(".svg", ".jpg")])
            if png_alt:
                try:
                    img = Image.open(png_alt)
                    try:
                        img = ImageOps.exif_transpose(img)
                    except Exception:
                        pass
                    img_reader = ImageReader(img)
                    iw, ih = img_reader.getSize()
                    img_aspect = iw / ih
                    box_aspect = (w / h) if h else img_aspect
                    if img_aspect > box_aspect:
                        tw = w
                        th = w / img_aspect
                    else:
                        th = h
                        tw = h * img_aspect
                    dx = x + (w - tw) / 2.0
                    dy = y + (h - th) / 2.0
                    c.drawImage(img_reader, dx, dy, width=tw, height=th, mask='auto')
                    return True
                except Exception:
                    pass
    return False

def draw_diagram_block(c, box_x, box_y, box_w, box_h, assets, dpi=300, mode_hint=None):
    """
    assets: str or [str, str]    (one or two images)
    mode_hint: 'stack' or 'two-up' or None (auto)
    """
    if isinstance(assets, str):
        assets = [assets]
    assets = [a for a in assets if a] if assets else []

    if not assets:
        c.setLineWidth(0.75)
        c.roundRect(box_x, box_y, box_w, box_h, 10)
        return

    if len(assets) == 1:
        draw_image_auto(c, assets[0], box_x, box_y, box_w, box_h, dpi)
        return

    if mode_hint not in ("stack", "two-up"):
        mode_hint = "two-up" if box_w >= box_h else "stack"

    pad = 8
    if mode_hint == "two-up":
        cell_w = (box_w - pad) / 2.0
        cell_h = box_h
        draw_image_auto(c, assets[0], box_x, box_y, cell_w, cell_h, dpi)
        draw_image_auto(c, assets[1], box_x + pad + cell_w, box_y, cell_w, cell_h, dpi)
    else:
        cell_w = box_w
        cell_h = (box_h - pad) / 2.0
        draw_image_auto(c, assets[0], box_x, box_y + pad + cell_h, cell_w, cell_h, dpi)
        draw_image_auto(c, assets[1], box_x, box_y, cell_w, cell_h, dpi)

def seed(path, text):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.strip()+"\n")

# Seed default YAMLs (safe if already present)
seed(os.path.join(CONFIG, "pinout_44pin.yaml"), """
pinout_44pin:
  title: "44-Pin Radio Harness Pinout"
  diagram: "pinout_44pin"
  photo: "pinout_harness_closeup"
  pins:
    - pin: 44
      name: "+12V Battery (B+)"
      color: "RED/BLUE"
      status: confirmed
    - pin: 38
      name: "Chassis Ground"
      color: "BLACK"
      status: confirmed
    - pin: 28
      name: "GMLAN Low-Speed (SW)"
      color: "GREEN"
      status: confirmed
    - pin: 10
      name: "AUX Right +"
      color: "GREEN"
      status: confirmed
    - pin: 23
      name: "AUX Common / Shield -"
      color: "BROWN"
      status: confirmed
    - pin: 24
      name: "AUX Left +"
      color: "GRAY"
      status: confirmed
    - pin: 11
      name: "AUX Detect"
      color: "BLUE"
      status: confirmed
    - pin: 7
      name: "Reverse Camera Video +"
      color: ""
      status: confirmed
    - pin: 8
      name: "Reverse Camera Video -"
      color: ""
      status: confirmed
""")

seed(os.path.join(CONFIG, "rr2_gm2_primary.yaml"), """
rr2_gm2_primary:
  title: "RR2 + GM2 Primary Gateway"
  diagram: "rr2_gm2_primary"
  photo: "rr2_gm2_primary_photo"
  role: "Primary CAN/GMLAN brain (Universal/Analog; no serial)"
  harness: "iDatalink GM2 T-harness"
  outputs:
    b_plus: "+12V Battery to HU BATT"
    acc: "Ignition ACC to HU ACC and accessory relays"
    ground: "To star ground node"
    reverse: "HU reverse trigger + DVR trigger"
    illumination: "HU dim input (optional)"
    parking_brake: "HU PB input"
    vss: "HU speed input (optional)"
    amp_remote: "Blue/White -> remote relay bus (DSP/Amp)"
    swc: "KEY1/KEY2 + SWC GND to Android HU"
    chime_audio: "Stereo L/R + GND to AUX mixer"
  programming: "Flash RR2 for Universal/Analog head unit"
  notes:
    - "RR2 is the single trigger source; don't parallel other modules"
    - "GM2 T-harness avoids cutting OEM loom"
    - "Harness routes using OEM loom"
""")

seed(os.path.join(CONFIG, "grz_overlay.yaml"), """
g_rz_gm59_overlay:
  title: "G-RZ-GM59 Overlay (Listen-Only)"
  diagram: "grz_overlay"
  photo: "grz_overlay_photo"
  role: "Overlay-only HVAC/status display"
  inputs:
    can_low_speed: "Tap OEM green GMLAN-L (Pin 28 path)"
    acc: "From HU ACC / relay"
    ground: "Star ground node"
  settings:
    swc_output: "disabled"
    power_outputs: "disabled"
    overlay: "enabled"
  notes:
    - "Listen-only; RR2 remains master for SWC/power/triggers"
""")

seed(os.path.join(CONFIG, "aux_mixer.yaml"), """
aux_mixer_block:
  title: "AUX Chime + Bin AUX Mixer"
  diagram: "aux_mixer_diagram"
  photo: "aux_mixer_real"
  purpose: "Combine RR2 chime audio and OEM bin AUX into one HU AUX input"
  inputs:
    - name: "RR2 Chime L/R"
    - name: "Bin AUX L/R (Pin 24,10 w/ Pin 23 common)"
  output:
    name: "HU AUX L/R + shield"
  type: "Passive stereo 2-in/1-out"
  shielding: "Twisted pair shielded; bond shield at star node only"
  alt:
    - "Direct RR2 chime to HU AUX if bin AUX unused"
""")

seed(os.path.join(CONFIG, "dsp_amp_stack.yaml"), """
dsp_amp_stack:
  title: "DSP / Amp Stack"
  diagram: "dsp_amp_stack"
  photo: "dsp_amp_stack_rear"
  rca:
    front: "HU FRONT L/R -> DSP IN 1/2 -> Front Amp -> Front components"
    rear:  "HU REAR L/R -> DSP IN 3/4 -> Rear Amp (optional) -> Rear speakers"
    sub:   "HU SUB -> DSP IN 5/6 -> Mono Sub Amp -> Subwoofer"
  remote_bus:
    source: "RR2 Blue/White"
    distribution: "Relay/splitter to DSP, Sub Amp, Front/Rear Amps"
    delay: "Optional 1.5s amp-on delay after DSP"
  power_ground:
    power: "Battery -> main fuse -> distribution -> amps/DSP"
    ground: "Single star point on chassis (rear floor)"
  notes:
    - "Use shielded RCA; route away from power"
    - "Torque ground lugs on prepped bare metal"
""")

seed(os.path.join(CONFIG, "usb_hdmi_retrofit.yaml"), """
usb_hdmi_retrofit:
  title: "USB + HDMI Retrofit"
  diagram: "usb_hdmi_retrofit"
  photo: "usb_hdmi_console"
  upper_bin:
    usb1: "CarPlay/Android Auto (data/power)"
    usb2: "DVR/Expansion (data/power)"
    aux:  "Bin AUX retained through mixer block"
    hdmi: "Optional HDMI IN from DVR"
  cig_port_conversion:
    replaces: "12V socket -> dual USB module"
    power: "From relay bus; fused 10A"
  dvr:
    hdmi_out: "To HU HDMI IN"
    reverse_trigger: "From RR2 reverse output"
""")

seed(os.path.join(CONFIG, "trigger_ground.yaml"), """
trigger_ground:
  title: "Trigger Bus + Star Ground"
  diagram: "trigger_ground"
  photo: "trigger_ground_star_point"
  trigger_bus:
    reverse: "RR2 -> HU & DVR"
    parking_brake: "RR2 -> HU"
    illumination: "RR2 -> HU (optional)"
    amp_remote: "RR2 -> relay -> DSP/Amps"
  grounding:
    star_node: "Single chassis bolt; all grounds return here"
    shields: "Bond drains at star node only (CAN/USB/AUX/RCA)"
    can_shield: "Drain spiral ok; one-end bond"
""")

seed(os.path.join(CONFIG, "parts_quick_pick.yaml"), """
parts_quick_pick:
  passive_stereo_mixer:
    model: "PAC SNI-35 or equivalent 2-into-1 passive RCA mixer"
    alt: "2x RCA Y-cable (if chime & AUX levels are balanced)"
    notes:
      - "Mount behind HU cavity"
      - "Bond shield drain at star ground"
  relay_delay_module:
    model: "PAC TR4 or similar 12V delay relay (1–3 s)"
    purpose: "Stage DSP/amp turn-on after RR2 remote"
    notes:
      - "Prevents turn-on pop"
      - "Inline with AMP REM"
  fuse_block:
    model: "Stinger SFB or similar mini-ANL distribution"
    amp_rating: "Size to your amps; eg 60A total / 20A branches"
    notes:
      - "Place near battery"
      - "Protect DSP/amp feeds"
  star_ground_kit:
    model: "KnuKonceptz/NVX 4→1 ground block"
    wire: "4 AWG in / 8 AWG outs"
    notes:
      - "Bare-metal bond; torque properly"
      - "Keep RCA shield away from power return"
""")

SECTIONS = [
    ("RR2 + GM2 Primary Gateway", "rr2_gm2_primary.yaml"),
    ("G-RZ-GM59 Overlay (Listen-Only)", "grz_overlay.yaml"),
    ("AUX Chime + Bin AUX Mixer", "aux_mixer.yaml"),
    ("DSP / Amp Stack", "dsp_amp_stack.yaml"),
    ("USB + HDMI Retrofit", "usb_hdmi_retrofit.yaml"),
    ("Trigger Bus + Star Ground", "trigger_ground.yaml"),
    ("44-Pin Radio Harness Pinout", "pinout_44pin.yaml"),
    ("Parts Quick Pick — Hardware", "parts_quick_pick.yaml"),
    ("Harness Labels", "labels.yaml"),
    ("GM Wire Color Legend", "color_legend.yaml"),
    ("Install Checklists", "checklists.yaml"),
    ("Pocket Card", "cheat_card.yaml"),
]


def draw_header(c, title, subtitle, dark=True):
    w,h = letter
    if dark:
        c.setFillColor(colors.black); c.rect(0,0,w,h,stroke=0,fill=1); c.setFillColor(colors.white)
    else:
        c.setFillColor(colors.white); c.rect(0,0,w,h,stroke=0,fill=1); c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 22); c.drawString(0.75*inch, h-1.0*inch, title)
    c.setFont("Helvetica", 12); c.drawString(0.75*inch, h-1.3*inch, subtitle)

def draw_footer(c, page_num=None, page_total=None, dark=True, stamp_enabled=True, version="", timestamp=""):
    c.setFont("Helvetica", 8)
    c.setFillGray(0.35 if not dark else 0.65)
    
    # Add version stamp if enabled
    if stamp_enabled and version and timestamp:
        stamp = f"Sonic Builder • {version} • Generated {timestamp} UTC"
    else:
        stamp = BUILD_STAMP
    
    right = f"Page {page_num} of {page_total}" if page_num and page_total else ""
    c.drawString(36, 24, stamp)
    if right:
        w = c.stringWidth(right, "Helvetica", 8)
        c.drawString(c._pagesize[0] - 36 - w, 24, right)

def draw_labels_grid(c, data, dark=True):
    """Render printable harness labels in a grid"""
    items = data.get('items', [])
    layout = data.get('layout', {})
    cols = layout.get('cols', 4)
    cell_w = layout.get('cell_w', 120)
    row_h = layout.get('row_height', 28)
    font_size = layout.get('font_size', 12)
    border = layout.get('border', True)
    
    x_start = 72
    y_start = 650
    
    for i, label in enumerate(items):
        col = i % cols
        row = i // cols
        x = x_start + col * (cell_w + 8)
        y = y_start - row * (row_h + 4)
        
        if border:
            c.setStrokeColor(colors.white if dark else colors.black)
            c.setLineWidth(1)
            c.rect(x, y, cell_w, row_h)
        
        c.setFont("Helvetica-Bold", font_size)
        c.setFillColor(colors.white if dark else colors.black)
        c.drawCentredString(x + cell_w/2, y + row_h/2 - 4, str(label))

def draw_color_legend(c, data, dark=True):
    """Render GM wire color legend table"""
    legend = data.get('legend', [])
    note = data.get('note', '')
    
    y = 650
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.white if dark else colors.black)
    c.drawString(72, y, "COLOR")
    c.drawString(240, y, "MEANING")
    
    y -= 25
    c.setFont("Helvetica", 10)
    for item in legend:
        color_name = item.get('color', '')
        meaning = item.get('meaning', '')
        c.drawString(72, y, color_name)
        c.drawString(240, y, meaning)
        y -= 18
    
    if note:
        y -= 15
        c.setFont("Helvetica-Oblique", 9)
        c.setFillGray(0.6 if dark else 0.4)
        for line in textwrap.wrap(note, width=90):
            c.drawString(72, y, line)
            y -= 12

def draw_checklists(c, data, dark=True):
    """Render installation checklists with checkboxes"""
    preflight = data.get('preflight', [])
    postflight = data.get('postflight', [])
    
    y = 660
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.white if dark else colors.black)
    c.drawString(72, y, "PRE-FLIGHT")
    
    y -= 20
    c.setFont("Helvetica", 9)
    for item in preflight:
        c.rect(74, y-1, 8, 8)
        c.drawString(90, y, f"☐  {item}")
        y -= 16
    
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "POST-FLIGHT")
    
    y -= 20
    c.setFont("Helvetica", 9)
    for item in postflight:
        c.rect(74, y-1, 8, 8)
        c.drawString(90, y, f"☐  {item}")
        y -= 16

def draw_pocket_card(c, data, dark=True):
    """Render pocket reference card with optional QR code"""
    bullets = data.get('bullets', [])
    qr_url = data.get('qr', '')
    
    y = 680
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.white if dark else colors.black)
    
    for bullet in bullets:
        for line in textwrap.wrap(bullet, width=95):
            c.drawString(72, y, f"• {line}")
            y -= 11
    
    if qr_url and HAS_QRCODE:
        qr = qrcode.QRCode(box_size=3, border=1)  # type: ignore
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        import io
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        c.drawImage(ImageReader(buf), 450, 480, width=100, height=100, mask='auto')
        c.setFont("Helvetica", 7)
        c.drawCentredString(500, 470, "Scan for video guide")

def draw_block(c, x,y,w,h, title, body, dark=True, width=92, max_lines=22):
    c.setLineWidth(1.0)
    if dark:
        c.setFillColorRGB(0.14,0.14,0.16); c.setStrokeColor(colors.white); c.setFillColor(colors.white)
    else:
        c.setFillColorRGB(0.96,0.96,0.96); c.setStrokeColor(colors.black); c.setFillColor(colors.black)
    c.roundRect(x,y,w,h,10,stroke=1,fill=1)
    c.setFont("Helvetica-Bold", 12); c.drawString(x+10, y+h-18, title[:70])
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.white if dark else colors.black)
    ty = y+h-35
    for line in textwrap.wrap(body, width=width)[:max_lines]:
        c.drawString(x+10, ty, line); ty -= 12

def build_pdf(outfile, dark=True, dpi=300, stamp_enabled=True, version="", timestamp=""):
    c = canvas.Canvas(outfile, pagesize=letter)
    title = "2014 Chevrolet Sonic LTZ — Android + RR2 + G-RZ Pro Integration Manual"
    subtitle = "RR2+GM2 Primary • G-RZ Overlay • AUX Mixer • DSP/Sub • USB/HDMI • Star Ground • 44-Pin Map"
    
    num_job_cards = 2
    total_pages = len(SECTIONS) + 5 + num_job_cards
    sections_for_toc = []
    
    draw_header(c, title, subtitle, dark)
    draw_block(c, 0.75*inch, 6.6*inch, 7.0*inch, 1.1*inch, "Build Status",
               "RR2: MASTER • G-RZ: OVERLAY • CAN: GREEN • AUDIO: CLEAN • RELAY: ARMED • POWER: STABLE",
               dark, width=100, max_lines=3)
    draw_block(c, 0.75*inch, 5.25*inch, 7.0*inch, 1.1*inch, "Quick Links",
               "RR2+GM2 • G-RZ Overlay • AUX Mixer • DSP/Amps • USB/HDMI • Trigger+Ground • 44-Pin • BOM",
               dark, width=110, max_lines=3)
    draw_footer(c, 1, total_pages, dark, stamp_enabled, version, timestamp)
    c.showPage()

    page_num = 2
    
    for name, fn in SECTIONS:
        anchor = fn.replace('.yaml', '').replace('_', '-')
        sections_for_toc.append({"title": name, "page": page_num, "anchor": anchor})
        
        path = os.path.join(CONFIG, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = f.read()
                yaml_data = yaml.safe_load(raw_data)
        except Exception as e:
            raw_data = f"(Could not read {fn}: {e})"
            yaml_data = None
        
        draw_header(c, name, f"from config/{fn}", dark)
        
        c.bookmarkPage(anchor)
        c.addOutlineEntry(name, anchor, level=0, closed=False)
        
        is_special_section = False
        if yaml_data and isinstance(yaml_data, dict):
            if 'items' in yaml_data:
                draw_labels_grid(c, yaml_data, dark)
                is_special_section = True
            elif 'legend' in yaml_data:
                draw_color_legend(c, yaml_data, dark)
                is_special_section = True
            elif 'preflight' in yaml_data:
                draw_checklists(c, yaml_data, dark)
                is_special_section = True
            elif 'bullets' in yaml_data:
                draw_pocket_card(c, yaml_data, dark)
                is_special_section = True
        
        if not is_special_section:
            left_diagram = None
            right_photo = None
            layout_hints = {}
            if yaml_data and isinstance(yaml_data, dict):
                config_key = list(yaml_data.keys())[0]
                config = yaml_data[config_key]
                if isinstance(config, dict):
                    # Support new simplified field names with backward compatibility
                    left_diagram = config.get('diagram') or config.get('left_diagram')
                    right_photo = config.get('photo') or config.get('diagram_right') or config.get('right_photo')
                    layout_hints = config.get('layout', {})
            
            left_w = 418
            left_h = 230
            right_w = 274
            right_h = 230
            
            # === AUTO-INSERT: USB/HDMI Retrofit (SVG + PNG + Panel Photo + Labels) ===
            if fn == "usb_hdmi_retrofit.yaml":
                try:
                    draw_svg_fit(c, RES, 'diagrams/usb_hdmi_overview.svg', x=72, y=260, max_w=420, max_h=260)
                    draw_image_fit(c, RES, 'diagrams/usb_hdmi_overview.png', x=72, y=120, width=420, height=120)
                except Exception as _err_usb:
                    pass
                
                # Panel snapshot with overlay labels (bottom-right corner)
                try:
                    panel_x, panel_y, panel_size = 468, 72, 200
                    draw_image_fit(c, RES, 'diagrams/panel_snapshot.png', x=panel_x, y=panel_y, width=panel_size, height=panel_size)
                    # Compact label overlay on top of panel photo
                    draw_svg_fit(c, RES, 'diagrams/panel_labels_compact_overlay.svg', x=panel_x, y=panel_y, max_w=panel_size, max_h=panel_size)
                except Exception as _err_panel:
                    pass
            
            # === AUTO-INSERT: Subwoofer Routing (SVG + PNG) ===
            elif fn == "dsp_amp_stack.yaml":
                try:
                    draw_svg_fit(c, RES, 'diagrams/subwoofer_route.svg', x=72, y=260, max_w=420, max_h=260)
                    draw_image_fit(c, RES, 'diagrams/subwoofer_route.png', x=72, y=120, width=420, height=120)
                except Exception as _err_sub:
                    pass
            
            draw_diagram_block(c, 36, 360, left_w, left_h, left_diagram, dpi, layout_hints.get('left'))
            draw_diagram_block(c, 468, 360, right_w, right_h, right_photo, dpi, layout_hints.get('right'))
            
            draw_block(c, 0.6*inch, 1.8*inch, 7.0*inch, 3.2*inch, "Config Data", raw_data, dark, width=110, max_lines=20)
            draw_block(c, 0.6*inch, 0.5*inch, 7.0*inch, 1.0*inch, "Installer Notes",
                       "Checklist: RR2 flash (Universal/Analog). Disable G-RZ SWC & power outs. "
                       "Mixer wiring (RR2 chime + Bin AUX -> HU AUX). Remote bus from RR2 -> DSP/Amps. "
                       "Bond shields at star node only. Keep RCA away from power.", dark, width=110, max_lines=4)
        
        draw_footer(c, page_num, total_pages, dark, stamp_enabled, version, timestamp)
        c.showPage()
        page_num += 1

    for i in range(2):
        draw_header(c, f"Blank Field Card {i+1}/2", "For sketches and quick notes", dark)
        w,h = letter
        c.setStrokeColor(colors.gray if dark else colors.lightgrey)
        for gy in range(1, 38):
            yy = 0.9*inch + gy*12
            c.line(0.6*inch, yy, w-0.6*inch, yy)
        c.setStrokeColor(colors.white if dark else colors.black)
        draw_footer(c, page_num, total_pages, dark, stamp_enabled, version, timestamp)
        c.showPage()
        page_num += 1
    
    job_cards_path = os.path.join(CONFIG, "job_cards.yaml")
    if os.path.isfile(job_cards_path):
        with open(job_cards_path, "r", encoding="utf-8") as f:
            job_cards_cfg = yaml.safe_load(f)
        
        render_job_cards(c, job_cards_cfg, icon_map="config/signal_icons.yaml")
    
    c.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Sonic LTZ Integration Manuals")
    parser.add_argument("--build", choices=["dark", "light", "both"], default="both",
                       help="Build dark, light, or both PDF manuals (default: both)")
    parser.add_argument("--theme", choices=["dark", "light", "both"], default="both",
                       help="Alias for --build (default: both)")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build directory before generating PDFs")
    parser.add_argument("--dpi", type=int, default=300,
                       help="DPI for rendered diagrams (default: 300)")
    parser.add_argument("--no-stamp", action="store_true",
                       help="Disable version/timestamp footer stamping")
    args = parser.parse_args()
    
    # Initialize version stamping parameters
    stamp_enabled = not args.no_stamp
    project_version = get_version()
    build_time_utc = build_timestamp()
    
    # Use --theme as alias for --build
    build_choice = args.theme if args.theme != "both" and args.build == "both" else args.build
    
    # Clean build directory if requested
    if args.clean:
        print("Cleaning build directory...")
        for item in os.listdir(BUILD):
            item_path = os.path.join(BUILD, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
        print("  ✓ Build directory cleaned")
    
    dark_pdf  = os.path.join(BUILD, "Sonic_LTZ_RR2_GRZ_Manual_DARK.pdf")
    light_pdf = os.path.join(BUILD, "Sonic_LTZ_RR2_GRZ_Manual_LIGHT.pdf")
    
    outputs = []
    
    if build_choice in ["dark", "both"]:
        print(f"Building DARK theme manual...")
        build_pdf(dark_pdf, True, args.dpi, stamp_enabled, project_version, build_time_utc)
        outputs.append(dark_pdf)
        print(f"  ✓ {dark_pdf}")
    
    if build_choice in ["light", "both"]:
        print(f"Building LIGHT theme manual...")
        build_pdf(light_pdf, False, args.dpi, stamp_enabled, project_version, build_time_utc)
        outputs.append(light_pdf)
        print(f"  ✓ {light_pdf}")
    
    if outputs:
        print(f"\nCreating bundle ZIP...")
        zip_path = os.path.join(BUILD, "Sonic_LTZ_RR2_GRZ_Builder_Package.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for fn in os.listdir(CONFIG):
                z.write(os.path.join(CONFIG, fn), arcname=f"config/{fn}")
            for pdf in outputs:
                z.write(pdf, arcname=os.path.basename(pdf))
        outputs.append(zip_path)
        print(f"  ✓ {zip_path}")
    
    print("\n✓ Build complete.")
    print("Outputs:")
    for output in outputs:
        print(f"  - {output}")
