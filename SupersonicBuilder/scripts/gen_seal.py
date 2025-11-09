#!/usr/bin/env python3
"""
Generate SonicBuilder Official Seal graphics
Reads version from VERSION.txt and creates seal assets
"""
import os
import sys

def read_version():
    """Read version from VERSION.txt (first line only)"""
    if os.path.exists("VERSION.txt"):
        with open("VERSION.txt", "r") as f:
            # Read first line only and clean it
            first_line = f.readline().strip()
            # Extract just version number if it says "Version: X.X.X"
            if ":" in first_line:
                return first_line.split(":", 1)[1].strip()
            return first_line
    return "v2.5.0"

def generate_svg_seal(version):
    """Generate SVG seal with current version"""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <!-- Outer circle -->
  <circle cx="200" cy="200" r="190" fill="none" stroke="#1a1a1a" stroke-width="4"/>
  
  <!-- Inner circle -->
  <circle cx="200" cy="200" r="175" fill="none" stroke="#1a1a1a" stroke-width="2"/>
  
  <!-- Center circle background -->
  <circle cx="200" cy="200" r="120" fill="#f5f5f5" stroke="#1a1a1a" stroke-width="3"/>
  
  <!-- Top arc text: SONICBUILDER -->
  <path id="topArc" d="M 60,200 A 140,140 0 0,1 340,200" fill="none"/>
  <text font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#1a1a1a" letter-spacing="4">
    <textPath href="#topArc" startOffset="50%" text-anchor="middle">
      SONICBUILDER
    </textPath>
  </text>
  
  <!-- Bottom arc text: OFFICIAL SEAL -->
  <path id="bottomArc" d="M 340,200 A 140,140 0 0,1 60,200" fill="none"/>
  <text font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#1a1a1a" letter-spacing="3">
    <textPath href="#bottomArc" startOffset="50%" text-anchor="middle">
      OFFICIAL SEAL
    </textPath>
  </text>
  
  <!-- Center monogram: CE -->
  <text x="200" y="190" font-family="Georgia, serif" font-size="72" font-weight="bold" fill="#1a1a1a" text-anchor="middle">CE</text>
  
  <!-- Founder text -->
  <text x="200" y="230" font-family="Arial, sans-serif" font-size="16" font-weight="normal" fill="#333333" text-anchor="middle">FOUNDER</text>
  
  <!-- Version badge -->
  <rect x="170" y="240" width="60" height="24" rx="12" fill="#1a1a1a"/>
  <text x="200" y="257" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{version}</text>
  
  <!-- Decorative stars -->
  <text x="100" y="210" font-family="Arial, sans-serif" font-size="28" fill="#1a1a1a" text-anchor="middle">⭕</text>
  <text x="300" y="210" font-family="Arial, sans-serif" font-size="28" fill="#1a1a1a" text-anchor="middle">⭕</text>
</svg>
'''
    return svg_content

def generate_svg_badge(version):
    """Generate minimal SVG badge (no outer text rings)"""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <!-- Single outer circle -->
  <circle cx="150" cy="150" r="140" fill="none" stroke="#1a1a1a" stroke-width="3"/>
  
  <!-- Center circle background -->
  <circle cx="150" cy="150" r="130" fill="#f5f5f5" stroke="#1a1a1a" stroke-width="2"/>
  
  <!-- Center monogram: CE -->
  <text x="150" y="140" font-family="Georgia, serif" font-size="64" font-weight="bold" fill="#1a1a1a" text-anchor="middle">CE</text>
  
  <!-- Founder text -->
  <text x="150" y="180" font-family="Arial, sans-serif" font-size="14" font-weight="normal" fill="#333333" text-anchor="middle">FOUNDER</text>
  
  <!-- Version badge -->
  <rect x="120" y="195" width="60" height="22" rx="11" fill="#1a1a1a"/>
  <text x="150" y="211" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">{version}</text>
</svg>
'''
    return svg_content

def generate_png_from_svg(svg_file, png_file, width=2000, height=2000, invert=False):
    """Convert SVG to PNG using cairosvg"""
    try:
        import cairosvg
        
        if invert:
            # Read SVG and invert colors
            with open(svg_file, 'r') as f:
                svg_content = f.read()
            
            svg_content = svg_content.replace('#1a1a1a', '#FFFFFF')
            svg_content = svg_content.replace('#f5f5f5', '#1a1a1a')
            svg_content = svg_content.replace('#333333', '#CCCCCC')
            
            # Convert directly from modified content
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=png_file,
                output_width=width,
                output_height=height
            )
        else:
            # Convert from file
            cairosvg.svg2png(
                url=svg_file,
                write_to=png_file,
                output_width=width,
                output_height=height
            )
        
        return True
    except ImportError:
        print("[warn] cairosvg not available - PNG generation skipped")
        print("[info] Install with: pip install cairosvg")
        return False

def main():
    # Read current version
    version = read_version()
    print(f"[info] Generating seal and badge with version: {version}")
    
    # Create directory
    os.makedirs("Founder_Seal", exist_ok=True)
    
    # Generate SEAL (full version with outer rings)
    svg_content = generate_svg_seal(version)
    svg_path = "Founder_Seal/SonicBuilder_Seal.svg"
    
    with open(svg_path, "w") as f:
        f.write(svg_content)
    print(f"[ok] Generated {svg_path}")
    
    # Generate seal PNG versions
    png_path = "Founder_Seal/SonicBuilder_Seal.png"
    white_path = "Founder_Seal/SonicBuilder_Seal_white.png"
    
    if generate_png_from_svg(svg_path, png_path):
        print(f"[ok] Generated {png_path}")
    
    if generate_png_from_svg(svg_path, white_path, invert=True):
        print(f"[ok] Generated {white_path}")
    
    # Generate BADGE (minimal version, no outer text)
    badge_svg_content = generate_svg_badge(version)
    badge_svg_path = "Founder_Seal/SonicBuilder_Badge.svg"
    
    with open(badge_svg_path, "w") as f:
        f.write(badge_svg_content)
    print(f"[ok] Generated {badge_svg_path}")
    
    # Generate badge PNG versions
    badge_png_path = "Founder_Seal/SonicBuilder_Badge.png"
    badge_white_path = "Founder_Seal/SonicBuilder_Badge_white.png"
    
    if generate_png_from_svg(badge_svg_path, badge_png_path):
        print(f"[ok] Generated {badge_png_path}")
    
    if generate_png_from_svg(badge_svg_path, badge_white_path, invert=True):
        print(f"[ok] Generated {badge_white_path}")
    
    print("[ok] Seal and badge generation complete")

if __name__ == "__main__":
    main()
