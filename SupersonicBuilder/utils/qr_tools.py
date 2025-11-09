import os, hashlib
from PIL import Image
import qrcode
_QR_DIR = os.path.join("assets","_qr")
os.makedirs(_QR_DIR, exist_ok=True)
def _qr_hash(s: str) -> str:
    import hashlib
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]
def ensure_qr_png(url: str, box_size=10, border=2) -> str:
    h = _qr_hash(url.strip())
    out = os.path.join(_QR_DIR, f"qr_{h}.png")
    if not os.path.exists(out):
        qr = qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=box_size,border=border)  # type: ignore
        qr.add_data(url.strip()); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img.save(out, "PNG", optimize=True)
    return out
