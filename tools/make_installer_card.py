from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

W,H = letter
c = canvas.Canvas("docs/installer/Supersonic_Installer_Summary_Dark_USLetter.pdf", pagesize=letter)

# Dark background
c.setFillColorRGB(0.07, 0.07, 0.09)
c.rect(0, 0, W, H, fill=1, stroke=0)

# Title
c.setFillColor(colors.white)
c.setFont("Helvetica-Bold", 24)
c.drawString(0.75*inch, H-1.1*inch, "Supersonic Installer Summary (Dark)")

# Subtitle
c.setFillColorRGB(0.8, 0.9, 1.0)
c.setFont("Helvetica", 12)
c.drawString(0.75*inch, H-1.45*inch, "US Letter 8.5\" × 11\" • High-contrast shop-manual theme")

y = H-2.1*inch
line = 16
def bullet(txt):
    global y
    if y < 1.0*inch:
        c.showPage()
        c.setFillColorRGB(0.07,0.07,0.09); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica", 11)
        y = H-1.0*inch
    c.circle(0.65*inch, y+3, 2, fill=1, stroke=0)
    c.drawString(0.75*inch, y, txt)
    y -= line

c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 14)
c.drawString(0.75*inch, y, "Checklist"); y -= 20
c.setFont("Helvetica", 11)
for t in [
    "Power off battery/ACC • Verify grounds • Label all connectors.",
    "Mount head unit • Secure harness strain-relief • Route mic/cam cables.",
    "CAN/SWC verify • Test audio L/R/F/R • Set DSP baseline preset.",
    "Backup camera polarity • 360 harness continuity • Sub out muted by default.",
    "Finalize: tie-downs, squeak/rattle check, reset error codes if any."
]:
    bullet(t)

c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 14)
c.drawString(0.75*inch, y, "Post-install Quick Config"); y -= 20
c.setFont("Helvetica", 11)
for t in [
    "Time/date/GPS lock • Wireless CarPlay/AA pairing.",
    "DSP: crossover fronts 80–100 Hz, sub 80 Hz; time-align driver seat.",
    "Steering-wheel keys learn • Reverse trigger • Front cam hotkey.",
    "Update firmware (HU/DSP/cam) • Export settings to SD/USB."
]:
    bullet(t)

c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 14)
c.drawString(0.75*inch, y, "Service Notes"); y -= 20
c.setFont("Helvetica", 11)
for t in [
    "Keep original OEM harness labeled in bag.",
    "Document any splices/adapters; photo the fuse taps.",
    "If noise: verify star ground + isolate RCA grounds.",
]:
    bullet(t)

# Footer
c.setFillColorRGB(0.8,0.9,1.0); c.setFont("Helvetica", 9)
c.drawRightString(W-0.75*inch, 0.6*inch, "SupersonicBuilder • Dark Installer Card • v2.1.1")
c.save()
