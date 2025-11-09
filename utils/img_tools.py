# utils/img_tools.py
from PIL import Image, ImageOps, ImageCms
import io
def normalize_photo(path_in: str) -> str:
    try:
        img = Image.open(path_in)
        try: img = ImageOps.exif_transpose(img)
        except Exception: pass
        try:
            if "icc_profile" in img.info and img.info["icc_profile"]:  # type: ignore
                src = io.BytesIO(img.info["icc_profile"])  # type: ignore
                srgb = ImageCms.createProfile("sRGB")
                img = ImageCms.profileToProfile(img, src, srgb, outputMode=img.mode)  # type: ignore
        except Exception: pass
        img.save(path_in, optimize=True)  # type: ignore
    except Exception: pass
    return path_in
