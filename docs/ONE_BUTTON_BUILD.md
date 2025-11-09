# One-Button Build Patch
Install:
- Unzip at repo root.
- In your `Makefile` add:
  -include MAKEFRAG.onebutton
  -include MAKEFRAG.urls
  -include MAKEFRAG.repo
  -include MAKEFRAG.two_up_qr

Run:
  make all VERSION=v2.0.9

Outputs:
- Appendix/C_I2S_Integration/03_Photo_Index.csv
- Appendix/C_I2S_Integration/QR_Index.pdf and QR_Index_2UP.pdf
- Appendix/C_I2S_Integration/Appendix_C_I2S_Index.pdf
- dist/manual.pdf (stamped if present)

Dependencies:
  pip install reportlab pypdf pillow qrcode pdf2image
