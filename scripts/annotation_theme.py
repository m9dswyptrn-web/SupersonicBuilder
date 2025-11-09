
"""
Annotation Theming Engine
-------------------------
Usage:
    from scripts.annotation_theme import apply_theme, load_theme

    theme = load_theme("templates/theme.sonic.json")
    themed_ann = apply_theme(annotations_json_obj, theme)

Theme format (templates/theme.sonic.json):
{
  "priority": [
    "power", "ground", "gmlan", "rca", "mic", "reverse", "camera", "trigger"
  ],
  "rules": {
    "power":   { "any": ["power", "12v", "b+"], "arrow_color":"#ff3b30", "box_stroke":"#ff3b30" },
    "ground":  { "any": ["ground", "gnd", "chassis"], "arrow_color":"#8e8e93", "box_stroke":"#8e8e93" },
    "gmlan":   { "any": ["gmlan", "can"], "arrow_color":"#34c759", "box_stroke":"#34c759" },
    "rca":     { "any": ["rca", "line-level", "preout"], "arrow_color":"#0a84ff", "box_stroke":"#0a84ff" },
    "mic":     { "any": ["mic", "microphone"], "arrow_color":"#d1d1d6", "box_stroke":"#d1d1d6", "text_color":"#ffffff" },
    "reverse": { "any": ["reverse"], "arrow_color":"#ffd60a", "box_stroke":"#ffd60a" },
    "camera":  { "any": ["camera", "cam"], "arrow_color":"#ffd60a", "box_stroke":"#ffd60a" },
    "trigger": { "any": ["trigger"], "arrow_color":"#ff9f0a", "box_stroke":"#ff9f0a" }
  },
  "defaults": {
    "arrow_color":"#f2a527",
    "box_stroke":"#f2a527",
    "box_fill":"#00000099",
    "text_color":"#ffffff",
    "line_width":1.2,
    "font_size":9
  }
}
"""
from __future__ import annotations
from typing import Dict, Any, List

def _norm(s: str) -> str:
    return (s or "").lower()

def load_theme(path: str) -> Dict[str, Any]:
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _match_rule(label: str, rule: Dict[str, Any]) -> bool:
    lbl = _norm(label)
    any_terms = [t.lower() for t in rule.get("any", [])]
    all_terms = [t.lower() for t in rule.get("all", [])]
    none_terms = [t.lower() for t in rule.get("none", [])]
    if any_terms and not any(t in lbl for t in any_terms):
        return False
    if all_terms and not all(t in lbl for t in all_terms):
        return False
    if none_terms and any(t in lbl for t in none_terms):
        return False
    return True

def _apply_style(dst: Dict[str, Any], style: Dict[str, Any]) -> None:
    # Copy styling keys if not already present
    for k in ("arrow_color","box_stroke","box_fill","text_color","line_width","font_size","label_dx","label_dy","arrow_size","w","h"):
        if k in style and dst.get(k) is None:
            dst[k] = style[k]

def apply_theme(annotations_obj: Dict[str, Any], theme: Dict[str, Any]) -> Dict[str, Any]:
    """Return a NEW annotations dict with styles applied where absent."""
    rules = theme.get("rules", {})
    order = theme.get("priority", [])
    defaults = theme.get("defaults", {})

    out = {"annotations": []}
    for a in annotations_obj.get("annotations", []):
        # base copy
        b = dict(a)  # shallow copy
        # prime with defaults (do not overwrite existing explicit values)
        for k, v in defaults.items():
            b.setdefault(k, v)

        label = str(b.get("label",""))
        matched_key = None
        # walk priority order
        for key in order:
            r = rules.get(key)
            if not r: 
                continue
            if _match_rule(label, r):
                _apply_style(b, r)
                matched_key = key
                break
        # if not matched, try any rule (fallback unordered)
        if matched_key is None:
            for key, r in rules.items():
                if _match_rule(label, r):
                    _apply_style(b, r)
                    break

        out["annotations"].append(b)
    return out
