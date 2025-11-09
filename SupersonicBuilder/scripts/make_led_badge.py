#!/usr/bin/env python3
"""
Generates animated LED GIFs + a pulsing "SYSTEM ONLINE" banner
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

OUT = Path("docs/assets")
OUT.mkdir(parents=True, exist_ok=True)

def ring_led(color_on=(40,255,180), color_off=(20,70,60), frames=16, size=14):
    imgs=[]
    for i in range(frames):
        t = (i/frames)*2*math.pi
        glow = (math.sin(t)+1)/2
        r = int(color_off[0] + (color_on[0]-color_off[0])*glow)
        g = int(color_off[1] + (color_on[1]-color_off[1])*glow)
        b = int(color_off[2] + (color_on[2]-color_off[2])*glow)
        im = Image.new("RGBA",(size,size),(0,0,0,0))
        d = ImageDraw.Draw(im)
        d.ellipse((1,1,size-2,size-2), fill=(r,g,b), outline=(r,g,b))
        halo = Image.new("RGBA",(size,size),(0,0,0,0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse((0,0,size,size), fill=(r,g,b,30))
        im = Image.alpha_composite(halo, im)
        imgs.append(im.convert("P"))
    return imgs

def save_gif(imgs, path, dur=70):
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=dur, loop=0, disposal=2, optimize=True)

def text_banner(text="SYSTEM ONLINE", color=(0,255,255), frames=20, w=340, h=34):
    imgs=[]
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except:
        font = ImageFont.load_default()
    for i in range(frames):
        glow = (math.sin((i/frames)*2*math.pi)+1)/2
        bg = (10,12,16)
        im = Image.new("RGB",(w,h), bg)
        d=ImageDraw.Draw(im)
        line_c = (int(color[0]*0.5), int(color[1]*0.5), int(color[2]*0.5))
        d.rectangle((0,h-4,w,h-2), fill=line_c)
        x = 10; y = 7
        c = (int(color[0]*(0.6+0.4*glow)), int(color[1]*(0.6+0.4*glow)), int(color[2]*(0.6+0.4*glow)))
        for r in (2,1):
            d.text((x,y), text, font=font, fill=(c[0],c[1],c[2],128))
        d.text((x,y), text, font=font, fill=c)
        imgs.append(im.convert("P"))
    return imgs

def main():
    save_gif(ring_led(), OUT/"led_online.gif")
    save_gif(ring_led(color_on=(255,200,0), color_off=(100,70,10)), OUT/"led_warn.gif")
    save_gif(ring_led(color_on=(255,80,80), color_off=(70,20,20)), OUT/"led_fail.gif")
    save_gif(text_banner("SYSTEM ONLINE"), OUT/"system_online.gif", dur=60)
    print("[OK] Generated:", *(str(p.name) for p in OUT.glob("*.gif")), sep="\n  - ")

if __name__ == "__main__":
    main()
