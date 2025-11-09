#!/usr/bin/env python3
"""
iOS Viewer Builder for Sonic Manual
Creates a mobile-optimized web interface for viewing PDFs on iOS devices
"""

import os
import argparse
import shutil
from pathlib import Path


def create_ios_viewer(output_dir, version, base_url=''):
    """Create iOS-compatible PDF viewer interface"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create main index.html
    create_main_index(output_path, version, base_url)
    
    # Create viewer page
    create_viewer_page(output_path, version, base_url)
    
    # Create manifest for PWA (Progressive Web App)
    create_manifest(output_path, version)
    
    # Create service worker for offline access
    create_service_worker(output_path)
    
    print(f"✓ iOS viewer created in {output_dir}/")


def create_main_index(output_dir, version, base_url):
    """Create main landing page"""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Sonic Manual">
    <title>Sonic Manual Viewer - {version}</title>
    <link rel="manifest" href="manifest.json">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 40px 20px;
            border-bottom: 2px solid #4CAF50;
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 2em;
            color: #4CAF50;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #999;
            font-size: 0.9em;
        }}
        
        .manual-grid {{
            display: grid;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .manual-card {{
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 12px;
            padding: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        
        .manual-card:active {{
            transform: scale(0.98);
        }}
        
        .manual-card:hover {{
            border-color: #4CAF50;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
        }}
        
        .manual-card h3 {{
            color: #4CAF50;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        
        .manual-card p {{
            color: #aaa;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        
        .manual-card .size {{
            display: inline-block;
            background: #333;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            margin-top: 10px;
            color: #888;
        }}
        
        .icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid #333;
            color: #666;
            font-size: 0.9em;
        }}
        
        .install-prompt {{
            background: #1e3a1e;
            border: 1px solid #4CAF50;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 30px;
            display: none;
        }}
        
        .install-prompt.show {{
            display: block;
        }}
        
        .install-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 1em;
            margin-top: 10px;
            cursor: pointer;
            width: 100%;
        }}
        
        .install-btn:active {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📘 Sonic Manual Viewer</h1>
            <p class="subtitle">2014 Chevy Sonic LTZ Audio/Electrical Integration</p>
            <p class="subtitle">{version}</p>
        </header>
        
        <div id="install-prompt" class="install-prompt">
            <p><strong>📱 Add to Home Screen</strong></p>
            <p>Install this app for offline access and quick launch from your home screen.</p>
            <button id="install-btn" class="install-btn">Install App</button>
        </div>
        
        <div class="manual-grid">
            <a href="viewer.html?pdf=../sonic_manual_dark.pdf" class="manual-card">
                <div class="icon">🌙</div>
                <h3>Dark Theme Manual</h3>
                <p>Full installation manual optimized for low-light viewing</p>
                <span class="size">~15 MB</span>
            </a>
            
            <a href="viewer.html?pdf=../sonic_manual_light.pdf" class="manual-card">
                <div class="icon">☀️</div>
                <h3>Light Theme Manual</h3>
                <p>Full installation manual with bright background for printing</p>
                <span class="size">~15 MB</span>
            </a>
            
            <a href="viewer.html?pdf=../sonic_field_cards.pdf" class="manual-card">
                <div class="icon">📋</div>
                <h3>Field Service Cards</h3>
                <p>Quick reference cards for troubleshooting and continuity testing</p>
                <span class="size">~100 KB</span>
            </a>
            
            <a href="../qr_codes/index.html" class="manual-card">
                <div class="icon">🔲</div>
                <h3>QR Codes</h3>
                <p>Scannable QR codes for sharing manual links</p>
                <span class="size">View</span>
            </a>
        </div>
        
        <footer>
            <p>Sonic Builder {version}</p>
            <p>Optimized for iOS Safari and Chrome</p>
        </footer>
    </div>
    
    <script>
        // PWA Installation prompt
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('install-prompt').classList.add('show');
        }});
        
        document.getElementById('install-btn').addEventListener('click', async () => {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                const {{ outcome }} = await deferredPrompt.userChoice;
                deferredPrompt = null;
                document.getElementById('install-prompt').classList.remove('show');
            }}
        }});
        
        // Register service worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js').catch(console.error);
        }}
    </script>
</body>
</html>
'''
    
    (output_dir / 'index.html').write_text(html)


def create_viewer_page(output_dir, version, base_url):
    """Create PDF viewer page"""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <title>PDF Viewer - Sonic Manual</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: #000;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        #toolbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(10px);
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            border-bottom: 1px solid #333;
        }}
        
        #toolbar button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
        }}
        
        #toolbar button:active {{
            background: #45a049;
        }}
        
        #pdf-title {{
            color: #e0e0e0;
            font-size: 14px;
            flex-grow: 1;
            text-align: center;
            padding: 0 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        #pdf-container {{
            position: fixed;
            top: 50px;
            left: 0;
            right: 0;
            bottom: 0;
            overflow: auto;
            -webkit-overflow-scrolling: touch;
        }}
        
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #4CAF50;
            font-size: 18px;
            text-align: center;
        }}
        
        .spinner {{
            border: 3px solid #333;
            border-top: 3px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div id="toolbar">
        <button onclick="window.history.back()">← Back</button>
        <div id="pdf-title">Loading...</div>
        <button onclick="window.open(pdfUrl, '_blank')">Open</button>
    </div>
    
    <div id="pdf-container">
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading PDF...</p>
        </div>
    </div>
    
    <script>
        // Get PDF URL from query parameter
        const urlParams = new URLSearchParams(window.location.search);
        const pdfPath = urlParams.get('pdf');
        const pdfUrl = pdfPath || '../sonic_manual_dark.pdf';
        
        // Update title
        const filename = pdfUrl.split('/').pop();
        document.getElementById('pdf-title').textContent = filename;
        document.title = filename;
        
        // Load PDF
        const container = document.getElementById('pdf-container');
        
        // Use iframe for iOS compatibility
        const iframe = document.createElement('iframe');
        iframe.src = pdfUrl;
        iframe.style.display = 'none';
        
        iframe.onload = () => {{
            container.innerHTML = '';
            iframe.style.display = 'block';
            container.appendChild(iframe);
        }};
        
        iframe.onerror = () => {{
            container.innerHTML = '<div class="loading"><p style="color: #f44336;">Failed to load PDF</p></div>';
        }};
        
        container.appendChild(iframe);
    </script>
</body>
</html>
'''
    
    (output_dir / 'viewer.html').write_text(html)


def create_manifest(output_dir, version):
    """Create PWA manifest for iOS"""
    
    manifest = f'''{{
  "name": "Sonic Manual Viewer",
  "short_name": "Sonic Manual",
  "description": "2014 Chevy Sonic LTZ Installation Manual",
  "version": "{version}",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#1a1a1a",
  "theme_color": "#4CAF50",
  "orientation": "any",
  "icons": [
    {{
      "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%234CAF50' width='100' height='100'/><text x='50' y='70' font-size='60' text-anchor='middle' fill='white'>S</text></svg>",
      "sizes": "any",
      "type": "image/svg+xml"
    }}
  ]
}}
'''
    
    (output_dir / 'manifest.json').write_text(manifest)


def create_service_worker(output_dir):
    """Create service worker for offline caching"""
    
    sw = '''// Service Worker for offline PDF access
const CACHE_NAME = 'sonic-manual-v1';
const urlsToCache = [
  './index.html',
  './viewer.html',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
'''
    
    (output_dir / 'sw.js').write_text(sw)


def main():
    parser = argparse.ArgumentParser(description='Build iOS-compatible PDF viewer')
    parser.add_argument('--output', default='output/ios_viewer',
                        help='Output directory for iOS viewer')
    parser.add_argument('--version', default='v1.0.0',
                        help='Version string')
    parser.add_argument('--base-url', default='',
                        help='Base URL for assets')
    
    args = parser.parse_args()
    
    print(f"📱 Building iOS viewer...")
    create_ios_viewer(args.output, args.version, args.base_url)


if __name__ == '__main__':
    main()
