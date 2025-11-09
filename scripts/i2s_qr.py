#!/usr/bin/env python3
import subprocess, sys, os
out = "Appendix/C_I2S_Integration/QR_Index.pdf"
cmd = [sys.executable, "scripts/qr_gallery.py", "--out", out, "--title", "Appendix C — QR Gallery",
       "--links", "manuals=/releases",
       "--links", "latest=/releases/latest",
       "--links", "appendixC=/tree/main/Appendix/C_I2S_Integration",
       "--links", "pcb=/tree/main/Appendix/C_I2S_Integration/PCB_Photos",
       "--links", "taps=/tree/main/Appendix/C_I2S_Integration/Tap_Diagrams"]
subprocess.check_call(cmd, env=os.environ.copy()); print(f"Wrote {out}")
