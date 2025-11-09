
import os
from scripts.annotation_modes import render_photos_page_by_mode

def page_photos_with_modes(c, assets_root, annotations_json, theme_json, page_num, total_pages):
    mode = os.getenv("ANNOTATION_MODE","themed")
    render_photos_page_by_mode(c,
        title="Annotated Harness Photos",
        assets_root=assets_root,
        annotations_json=annotations_json,
        mode=mode,
        theme_json=theme_json,
        page_num=page_num,
        total_pages=total_pages)
