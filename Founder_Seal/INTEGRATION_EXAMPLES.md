# SonicBuilder Seal - Integration Examples

## 🎯 Quick Integration Guide

This document shows how to embed the SonicBuilder Official Seal into various document types.

---

## 📄 PDF Documents (ReportLab)

### Example 1: Cover Page with Large Seal

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def add_cover_with_seal(c, page_width, page_height):
    """Add cover page with SonicBuilder seal"""
    
    # Add seal image (top-right corner)
    seal_path = "Founder_Seal/SonicBuilder_Seal.png"
    seal_size = 150  # 150 points (~2 inches)
    
    c.drawImage(
        seal_path,
        page_width - seal_size - 50,  # 50pt from right
        page_height - seal_size - 50,  # 50pt from top
        width=seal_size,
        height=seal_size,
        mask='auto',  # Preserve transparency
        preserveAspectRatio=True
    )
    
    # Add title
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(page_width / 2, page_height - 200, "SONICBUILDER MANUAL")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(page_width / 2, page_height - 240, "EOENKK Android 15 + Maestro RR2 GM5")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_width / 2, page_height - 280, "Version 2.5.0")
```

### Example 2: Page Watermark (30% Opacity)

```python
def add_watermark_seal(c, page_width, page_height):
    """Add translucent seal watermark to page"""
    
    seal_path = "Founder_Seal/SonicBuilder_Seal.png"
    seal_size = 250  # Larger watermark
    
    # Center the watermark
    x = (page_width - seal_size) / 2
    y = (page_height - seal_size) / 2
    
    c.saveState()
    c.setFillAlpha(0.3)  # 30% opacity
    c.drawImage(
        seal_path,
        x, y,
        width=seal_size,
        height=seal_size,
        mask='auto'
    )
    c.restoreState()
```

### Example 3: Signature Block with Seal

```python
def add_signature_block(c, x, y):
    """Add signature block with seal"""
    
    seal_path = "Founder_Seal/SonicBuilder_Seal.png"
    seal_size = 50  # Small seal
    
    # Draw seal
    c.drawImage(seal_path, x, y, width=seal_size, height=seal_size, mask='auto')
    
    # Draw signature block text
    text_x = x + seal_size + 10
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(text_x, y + 35, "Christopher Elgin — SonicBuilder Founder")
    
    c.setFont("Helvetica", 9)
    c.drawString(text_x, y + 22, "EOENKK Android 15 + Maestro RR2 GM5")
    c.drawString(text_x, y + 10, "Date: 2025-10-28")
    
    # Signature line
    c.setFont("Helvetica", 9)
    c.drawString(text_x, y - 5, "Signature: _______________________________")
```

---

## 🌐 HTML Documents

### Example 1: Watermark Background

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .page-with-seal {
            position: relative;
            min-height: 100vh;
        }
        
        .seal-watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 400px;
            height: 400px;
            opacity: 0.15;
            z-index: -1;
            pointer-events: none;
        }
        
        .content {
            position: relative;
            z-index: 1;
            padding: 40px;
        }
    </style>
</head>
<body class="page-with-seal">
    <img src="Founder_Seal/SonicBuilder_Seal.png" class="seal-watermark" alt="SonicBuilder Seal">
    
    <div class="content">
        <h1>SonicBuilder Manual</h1>
        <p>Content goes here...</p>
    </div>
</body>
</html>
```

### Example 2: Header Seal

```html
<header style="display: flex; align-items: center; padding: 20px;">
    <img src="Founder_Seal/SonicBuilder_Seal.png" 
         alt="SonicBuilder Official Seal"
         style="width: 60px; height: 60px; margin-right: 15px; opacity: 0.8;">
    
    <div>
        <h1 style="margin: 0;">SonicBuilder Manual</h1>
        <p style="margin: 0; color: #666;">EOENKK Android 15 + Maestro RR2 GM5</p>
    </div>
</header>
```

---

## 📝 Markdown Documents

### Example: README Header with Seal

```markdown
<div align="center">
  <img src="Founder_Seal/SonicBuilder_Seal.png" width="200" alt="SonicBuilder Official Seal">
  
  # SonicBuilder Manual
  
  **EOENKK Android 15 + Maestro RR2 GM5**
  
  Version 2.5.0 | Christopher Elgin, Founder
</div>
```

---

## 🖼️ LaTeX Documents

### Example: Title Page with Seal

```latex
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\begin{titlepage}
    \centering
    
    % Seal at top
    \includegraphics[width=0.3\textwidth]{Founder_Seal/SonicBuilder_Seal.png}
    
    \vspace{2cm}
    
    {\Huge\bfseries SonicBuilder Manual\par}
    \vspace{1cm}
    {\Large EOENKK Android 15 + Maestro RR2 GM5\par}
    \vspace{0.5cm}
    {\large Version 2.5.0\par}
    
    \vfill
    
    % Signature block
    \begin{flushleft}
    \includegraphics[width=1cm]{Founder_Seal/SonicBuilder_Seal.png}
    Christopher Elgin — SonicBuilder Founder\\
    Date: \today\\
    Signature: \rule{5cm}{0.4pt}
    \end{flushleft}
    
\end{titlepage}

\end{document}
```

---

## 🎨 Image Editing (Python/PIL)

### Example: Add Seal to Existing Image

```python
from PIL import Image

def add_seal_to_image(base_image_path, output_path):
    """Add SonicBuilder seal to existing image"""
    
    # Open images
    base = Image.open(base_image_path).convert("RGBA")
    seal = Image.open("Founder_Seal/SonicBuilder_Seal.png").convert("RGBA")
    
    # Resize seal (e.g., 200x200)
    seal = seal.resize((200, 200), Image.LANCZOS)
    
    # Adjust opacity
    seal_alpha = seal.split()[3]
    seal_alpha = seal_alpha.point(lambda p: int(p * 0.6))  # 60% opacity
    seal.putalpha(seal_alpha)
    
    # Position (bottom-right corner with 20px padding)
    position = (base.width - seal.width - 20, base.height - seal.height - 20)
    
    # Paste seal onto base
    base.paste(seal, position, seal)
    
    # Save result
    base.save(output_path, "PNG")

# Usage
add_seal_to_image("diagram.png", "diagram_with_seal.png")
```

---

## 📊 Common Use Cases

### 1. Cover Pages
- **Size:** 4-5 inches (300-375 points)
- **Opacity:** 100%
- **Position:** Center or top-right corner
- **File:** SonicBuilder_Seal.png

### 2. Headers/Footers
- **Size:** 1-1.5 inches (72-108 points)
- **Opacity:** 60-80%
- **Position:** Top-right or bottom-right
- **File:** SonicBuilder_Seal.png

### 3. Page Watermarks
- **Size:** 3-4 inches (225-300 points)
- **Opacity:** 25-35%
- **Position:** Center of page
- **File:** SonicBuilder_Seal.png

### 4. Signature Blocks
- **Size:** 0.75-1 inch (54-72 points)
- **Opacity:** 80-100%
- **Position:** Left of signature line
- **File:** SonicBuilder_Seal.png

### 5. Dark Backgrounds
- **Size:** Any
- **Opacity:** As needed
- **Position:** Any
- **File:** SonicBuilder_Seal_white.png ← Use white version!

---

## 🔄 Auto-Update Version

When your project version changes, regenerate seals with:

```bash
make seal
```

This reads `VERSION.txt` and updates the version badge in all seal files.

---

## 📐 Sizing Reference

| Points | Inches | Centimeters | Use Case |
|--------|--------|-------------|----------|
| 36 | 0.5" | 1.3 cm | Micro watermark |
| 72 | 1.0" | 2.5 cm | Small footer |
| 108 | 1.5" | 3.8 cm | Medium header |
| 216 | 3.0" | 7.6 cm | Large watermark |
| 300 | 4.2" | 10.7 cm | Cover page |

**Note:** 72 points = 1 inch (standard PDF/print measurement)

---

For complete usage guidelines, see: `README_Seal_Usage.txt`
