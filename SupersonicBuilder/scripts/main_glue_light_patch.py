
"""
Patch for scripts/main_glue.py to auto-switch the page frame when THEME=light.
Add these lines AFTER importing draw_dark_frame from scripts.render_pages.
"""

try:
    from scripts.frame_light import draw_light_frame as _draw_light_frame
except Exception:
    _draw_light_frame = None

def patch_frame_for_theme(theme: str):
    # Monkey-patch draw_dark_frame to the light version so downstream pages reuse it.
    if theme == "light" and _draw_light_frame is not None:
        import scripts.render_pages as rp
        rp.draw_dark_frame = _draw_light_frame
        return True
    return False
