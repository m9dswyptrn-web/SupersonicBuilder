# Two-Up Raster & QR Gallery — SB_REPO_URL Aware

This patch adds:
- `scripts/two_up_raster.py` — rasterize a page and lay it out as a 2-up card sheet
- `scripts/qr_gallery.py` — generate a printable sheet of QR codes for common links
- `make_patches/MAKEFRAG.two_up_qr` — Makefile targets using SB_REPO_URL by default

## Usage

1. Copy the scripts into your repo `scripts/` and include the Makefile fragment:
   ```make
   -include MAKEFRAG.two_up_qr
   ```

2. Build the two-up field card (with footer + QR):
   ```bash
   make two_up
   ```

3. Build the QR gallery sheet (uses SB_REPO_URL as base):
   ```bash
   make qr_gallery
   ```

Both scripts automatically read `SB_REPO_URL` from the environment; if unset,
they fall back to your current Replit app URL.

Tip: In CI, ensure `SB_REPO_URL` is set via the reusable `repo-url-setup.yml`.
