#!/usr/bin/env python3
import argparse, subprocess
from pathlib import Path
TOOLS = [
  ("generate_cover.py", ["--title","Chevy Sonic LTZ","--subtitle","EOENKK + Maestro RR2","--out","{out}/cover.png"]),
  ("generate_titlepage.py", ["--title","SonicBuilder Manual","--version","v2.0.9","--out","{out}/title.png"]),
  ("generate_parts_table_image.py", ["--items","ADS-MRR2,HRN-RR-GM5,EOENKK HU,USB DAC,SPDIF TX","--out","{out}/parts.png"]),
  ("generate_qr_label.py", ["--text","https://github.com/m9dswyptrn-web/SonicBuilder","--label","Repo","--out","{out}/qr_repo.png"]),
  ("header_strip.py", ["--text","Disassembly","--out","{out}/header.png"]),
  ("footer_strip.py", ["--text","© SonicBuilder","--out","{out}/footer.png"]),
  ("fieldcard_grid.py", ["--items","Step 1,Step 2,Step 3,Step 4","--out","{out}/fieldcards.png"]),
  ("two_up_cards.py", ["--items","Left,Right","--cols","2","--rows","1","--out","{out}/twoup.png"]),
  ("three_up_cards.py", ["--items","A,B,C","--cols","3","--rows","1","--out","{out}/threeup.png"]),
  ("callout_tip.py", ["--head","Pro Tip","--body","Label wires before removing harness","--out","{out}/tip.png"]),
  ("callout_warn.py", ["--head","Warning","--body","Disconnect battery before wiring","--out","{out}/warn.png"]),
  ("callout_danger.py", ["--head","Danger","--body","High voltage area","--out","{out}/danger.png"]),
  ("chapter_opener.py", ["--text","AUDIO SYSTEM","--out","{out}/chapter.png"]),
  ("divider_page.py", ["--text","—  BREAK  —","--out","{out}/divider.png"]),
  ("section_label.py", ["--text","Camera Integration","--out","{out}/section.png"]),
  ("figure_label.py", ["--text","Figure A","--out","{out}/figure.png"]),
  ("appendix_tab.py", ["--text","Appendix A","--out","{out}/appendix.png"]),
  ("toc_card.py", ["--text","Table of Contents","--out","{out}/toc.png"]),
  ("spec_block.py", ["--text","Specs","--out","{out}/specs.png"]),
  ("pinout_block.py", ["--text","GM 44-pin","--out","{out}/pinout.png"]),
  ("connector_block.py", ["--text","RCA Breakout","--out","{out}/connector.png"]),
  ("camera_overlay_label.py", ["--text","Rear Cam","--out","{out}/camera.png"]),
  ("canbus_label.py", ["--text","GMLAN HS/LS","--out","{out}/canbus.png"]),
  ("power_label.py", ["--text","12V/IGN/ACC","--out","{out}/power.png"]),
  ("audio_label.py", ["--text","I2S / SPDIF","--out","{out}/audio.png"]),
  ("testing_label.py", ["--text","Validation","--out","{out}/testing.png"]),
  ("programming_label.py", ["--text","Firmware","--out","{out}/programming.png"]),
  ("wiring_label.py", ["--text","Harness","--out","{out}/wiring.png"]),
  ("legend_key.py", ["--text","Legend / Key","--out","{out}/legend.png"]),
  ("note_card.py", ["--text","Note","--out","{out}/note.png"]),
  ("step_card.py", ["--text","Step","--out","{out}/step.png"]),
  ("result_card.py", ["--text","Result","--out","{out}/result.png"]),
  ("success_badge.py", ["--text","PASS","--out","{out}/success.png"]),
  ("warning_badge.py", ["--text","WARN","--out","{out}/warn_badge.png"]),
  ("error_badge.py", ["--text","FAIL","--out","{out}/error_badge.png"]),
  ("watermark_card.py", ["--text","DRAFT","--out","{out}/watermark.png"]),
  ("qr_frame_label.py", ["--text","QR FRAME","--out","{out}/qr_frame.png"]),
  ("photo_frame.py", ["--text","PHOTO","--out","{out}/photo_frame.png"]),
  ("diagram_canvas.py", ["--text","DIAGRAM","--out","{out}/diagram_canvas.png"]),
  ("grid_4x4.py", ["--out","{out}/grid4x4.png"]),
]
def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('--out', required=True)
  A = ap.parse_args()
  outdir = Path(A.out); outdir.mkdir(parents=True, exist_ok=True)
  here = Path(__file__).resolve().parent
  for tool, args in TOOLS:
    cmd = ['python', str(here / tool)] + [s.format(out=str(outdir)) for s in args]
    print('→', ' '.join(cmd))
    try:
      subprocess.check_call(cmd)
    except Exception as e:
      print('WARN:', tool, 'failed:', e)
if __name__ == '__main__':
  main()
