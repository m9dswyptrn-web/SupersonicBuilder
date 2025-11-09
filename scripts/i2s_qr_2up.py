#!/usr/bin/env python3
import os, subprocess, sys
src = "Appendix/C_I2S_Integration/QR_Index.pdf"
out = "Appendix/C_I2S_Integration/QR_Index_2UP.pdf"
if not os.path.exists(src):
    print("QR_Index.pdf not found. Run i2s_qr first."); sys.exit(1)
cmd = [sys.executable, "scripts/two_up_raster.py", "--in", src, "--out", out, "--qr"]
subprocess.check_call(cmd, env=os.environ.copy()); print(f"Wrote {out}")
