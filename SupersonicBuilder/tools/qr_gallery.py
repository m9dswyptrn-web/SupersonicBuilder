# tools/qr_gallery.py — generate QR PNGs + simple index
import argparse, os, qrcode, datetime, pathlib, json
def main(base_url):
    out = pathlib.Path("output/qr_codes"); out.mkdir(parents=True, exist_ok=True)
    targets = {
        "manual_dark": f"{base_url}/Sonic_LTZ_RR2_GRZ_Manual_DARK.pdf",
        "manual_light": f"{base_url}/Sonic_LTZ_RR2_GRZ_Manual_LIGHT.pdf",
        "field_cards": f"{base_url}/field_cards/sonic_field_cards.pdf",
    }
    for name, url in targets.items():
        img = qrcode.make(url); img.save(out / f"{name}.png")
    (out/"index.json").write_text(json.dumps({"generated": datetime.datetime.now().isoformat(), "targets": targets}, indent=2))
    (out/"README.txt").write_text("QR codes generated for quick access. Update QR_BASE_URL to your published domain.\n")
    print("QR gallery generated in", out)
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--base-url", default="http://0.0.0.0:5000")
    a=ap.parse_args(); main(a.base_url)
