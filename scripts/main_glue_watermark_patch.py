
"""
Monkey-patch to add a watermark overlay after the page frame is drawn.

Usage in scripts/main_glue.py (after parsing args and optionally patching light frame):
    from scripts.main_glue_watermark_patch import patch_watermark
    patch_watermark(
        text=os.getenv("WM_TEXT", "LTZ RR2 GRZ"),
        mode=os.getenv("WM_MODE", "footer"),   # footer | diagonal | off
        opacity=float(os.getenv("WM_OPACITY", "0.55")),
        footer_pos=os.getenv("WM_FOOTER_POS","right")  # left|center|right
    )
"""
def patch_watermark(text="LTZ RR2 GRZ", mode="footer", opacity=0.55, footer_pos="right"):
    import scripts.render_pages as rp
    from scripts.watermark import draw_footer_watermark, draw_diagonal_watermark

    original = getattr(rp, "draw_dark_frame", None)
    if original is None:
        return False

    def wrapped(c, title, page_num, total_pages):
        # call original dark/light frame first
        original(c, title, page_num, total_pages)
        # then overlay watermark
        m = (mode or "off").lower()
        if m == "footer":
            draw_footer_watermark(c, text=text, pos=footer_pos, opacity=opacity)
        elif m == "diagonal":
            draw_diagonal_watermark(c, text=text, opacity=min(max(opacity,0.02),0.2))
        else:
            pass

    rp.draw_dark_frame = wrapped
    return True
