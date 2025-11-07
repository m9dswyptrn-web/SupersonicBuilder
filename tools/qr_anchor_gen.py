#!/usr/bin/env python3
"""
QR Code Anchor Generator for Sonic Builder
Generates QR codes linking to manual sections for quick mobile access
"""

import os
import argparse
from pathlib import Path

try:
    import qrcode
    from qrcode.image.svg import SvgPathImage
except ImportError:
    print("⚠️  qrcode library not available - skipping QR generation")
    print("   Install with: pip install qrcode[pil]")
    exit(0)


def generate_qr_codes(base_url, output_dir, version):
    """Generate QR codes for manual sections"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Define manual sections with anchor points (using renamed output/ files)
    sections = {
        'manual_dark': {
            'url': f'{base_url}/output/sonic_manual_dark.pdf',
            'label': 'Dark Theme Manual'
        },
        'manual_light': {
            'url': f'{base_url}/output/sonic_manual_light.pdf',
            'label': 'Light Theme Manual'
        },
        'continuity_card': {
            'url': f'{base_url}/output/sonic_field_cards.pdf',
            'label': 'USB/AUX Continuity Card'
        },
        'full_release': {
            'url': f'{base_url}/output/sonic_full_release_{version}.zip',
            'label': f'Full Release Package ({version})'
        }
    }
    
    generated = []
    
    for section_id, data in sections.items():
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data['url'])
            qr.make(fit=True)
            
            # Generate PNG image
            img = qr.make_image(fill_color="black", back_color="white")
            png_path = output_path / f"{section_id}_qr.png"
            img.save(str(png_path))
            
            # Also generate SVG version for print quality
            try:
                qr_svg = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                    image_factory=SvgPathImage
                )
                qr_svg.add_data(data['url'])
                qr_svg.make(fit=True)
                
                svg_img = qr_svg.make_image(fill_color="black", back_color="white")
                svg_path = output_path / f"{section_id}_qr.svg"
                svg_img.save(str(svg_path))
            except Exception:
                # SVG generation is optional
                pass
            
            generated.append({
                'id': section_id,
                'label': data['label'],
                'url': data['url'],
                'qr_png': str(png_path)
            })
            
        except Exception as e:
            print(f"⚠️  Failed to generate QR for {section_id}: {e}")
            continue
    
    # Create index HTML for QR codes
    create_qr_index(output_path, generated, version)
    
    return generated


def create_qr_index(output_dir, qr_codes, version):
    """Create an HTML index of all QR codes"""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sonic Manual QR Codes - {version}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
        }}
        h1 {{
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .qr-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .qr-card {{
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .qr-card:hover {{
            transform: translateY(-5px);
            border-color: #4CAF50;
        }}
        .qr-card img {{
            width: 200px;
            height: 200px;
            margin: 20px auto;
            display: block;
            background: white;
            padding: 10px;
            border-radius: 4px;
        }}
        .qr-card h3 {{
            color: #4CAF50;
            margin: 10px 0;
        }}
        .qr-card p {{
            color: #999;
            font-size: 0.9em;
            word-break: break-all;
        }}
        .version {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #333;
        }}
    </style>
</head>
<body>
    <h1>📱 Sonic Manual QR Codes</h1>
    <p>Scan these QR codes with your mobile device for quick access to manuals and resources.</p>
    
    <div class="qr-grid">
'''
    
    for qr in qr_codes:
        qr_filename = Path(qr['qr_png']).name
        html += f'''
        <div class="qr-card">
            <h3>{qr['label']}</h3>
            <img src="{qr_filename}" alt="{qr['label']} QR Code">
            <p>{qr['url']}</p>
        </div>
'''
    
    html += f'''
    </div>
    
    <div class="version">
        <p>Sonic Builder {version}</p>
    </div>
</body>
</html>
'''
    
    index_path = output_dir / 'index.html'
    index_path.write_text(html)
    print(f"   Created QR index: {index_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate QR codes for manual sections')
    parser.add_argument('--base-url', default='http://localhost:5000',
                        help='Base URL for QR code links')
    parser.add_argument('--output', default='output/qr_codes',
                        help='Output directory for QR codes')
    parser.add_argument('--version', default='v1.0.0',
                        help='Version string for index page')
    
    args = parser.parse_args()
    
    print(f"🔲 Generating QR codes...")
    qr_codes = generate_qr_codes(args.base_url, args.output, args.version)
    
    print(f"✓ Generated {len(qr_codes)} QR codes in {args.output}/")
    for qr in qr_codes:
        print(f"   • {qr['label']}")


if __name__ == '__main__':
    main()
