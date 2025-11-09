#!/usr/bin/env python3
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import qrcode, io, argparse, textwrap
from pathlib import Path

QR_URL = "https://github.com/<owner>/<repo>/releases"

def draw_card(c, x, y, w, h, title, body, qr):
    c.setFillColorRGB(0.047,0.055,0.071)
    c.rect(x,y,w,h,fill=1,stroke=0)
    c.setFillColorRGB(0.0,0.68,0.94)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x+12, y+h-20, title)
    c.setFillColorRGB(0.9,0.95,0.98)
    c.setFont("Helvetica", 8)
    text_y = y+h-36
    for line in textwrap.wrap(body, width=80):
        c.drawString(x+12, text_y, line)
        text_y -= 10
    qr_img = qrcode.make(qr)
    bio = io.BytesIO(); qr_img.save(bio, format="PNG"); bio.seek(0)
    c.drawImage(ImageReader(bio), x+w-72, y+12, width=56, height=56)

def make_two_up(outpdf, cards, qr):
    c = canvas.Canvas(outpdf, pagesize=landscape(letter))
    W, H = landscape(letter)
    for i in range(0, len(cards), 2):
        left = cards[i]
        right = cards[i+1] if i+1 < len(cards) else None
        draw_card(c, 36, 36, (W-72)/2, H-72, left['title'], left['body'], qr)
        if right:
            draw_card(c, 36 + (W-72)/2, 36, (W-72)/2, H-72, right['title'], right['body'], qr)
        c.showPage()
    c.save()

def make_four_up(outpdf, cards, qr):
    c = canvas.Canvas(outpdf, pagesize=letter)
    W, H = letter
    w = (W-72)/2; h = (H-72)/2
    for i in range(0, len(cards), 4):
        page_cards = cards[i:i+4]
        coords = [(36, H/2+6),(W/2+0, H/2+6),(36,36),(W/2+0,36)]
        for j,card in enumerate(page_cards):
            x,y = coords[j]
            draw_card(c, x, y, w, h, card['title'], card['body'], qr)
        c.showPage()
    c.save()

if __name__ == '__main__':
    import json, sys
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-two', default='out/field_cards_two_up.pdf')
    ap.add_argument('--out-four', default='out/field_cards_four_up.pdf')
    ap.add_argument('--qr', default=QR_URL)
    A = ap.parse_args()
    Path('out').mkdir(exist_ok=True)
    cards = [
        {'title':'Teensy CAN Bridge Wiring','body':'CAN1 -> HS (DLC 6/14). CAN2 -> SW (DLC 1). 5V, GND, common ground. Use transceivers.'},
        {'title':'GM5 ↔ RR2 Harness','body':'GM5 harness maps to RR2: preserve chime, SWC, amplifier remote. Verify pins.'},
        {'title':'Power & Ground','body':'B+ to constant battery; ACC to switched accessory; remote to amp. Use 30A fuse as required.'},
        {'title':'Android HU I/O','body':'USB OTG host required for Teensy. Use USB DAC for digital audio if HU supports host mode.'}
    ]
    make_two_up(A.out_two, cards, A.qr)
    make_four_up(A.out_four, cards, A.qr)
    print('Field cards generated:', A.out_two, A.out_four)
