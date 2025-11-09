# 🚀 SonicBuilder Supersonic

**Precision Build System for the 2014 Chevy Sonic LTZ (T300)**  
_"Build of Builds" → fully automated DSP, documentation, and traceable packaging system._

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/status-SUPERSONIC-success)

---

## 🧠 Overview

**SonicBuilder Supersonic** is an end-to-end automated builder for the **Chevy Sonic Android Head Unit project**.  
It generates DSP configuration sets, laminated-style PDF documentation, wiring guides, and version-tracked ZIP bundles.  
Everything is fully **traceable** to the exact Git tag and commit.

---

## 🧩 Core Features

| Feature | Description |
|----------|-------------|
| 🔧 **Lean Auto Installer** | `make_supersonic_lean_auto.py` creates or updates your full environment, fetching the latest scripts directly from GitHub. |
| 🧱 **Builder Chain** | `supersonic_build_all.py` runs the entire build, generates packages, verifies, and optionally publishes releases. |
| 🧪 **Preflight Verifier** | `supersonic_verify.py` checks file integrity, tag sync, and trace consistency with GitHub. |
| 🪶 **Mission Cards (PDF)** | `make_supersonic_cards_autoattach.py` produces dark + light reference cards with embedded tag and repo trace. |
| 🎨 **Banner Generators** | Dark, light, and animated glow banners for GitHub and presentations. |
| 📊 **Dashboard System** | Three versions of HTML dashboards with QR codes, PDF previews, and live GitHub integration. |
| 🎴 **Verification Cards** | Single and double-sided laminated field cards with QR trace and wiring reference. |
| 📦 **Field Kit Packager** | Bundles all assets into ready-to-deploy ZIP with SHA-256 manifests. |
| 🔐 **Secure Release** | Auto-generates manifests, USB autorun, and optionally uploads to GitHub releases. |
| 🧾 **Build Trace System** | Every run generates `BUILD_REPORT.md` + embedded trace in `sonicbuilder.config.json`. |
| 🌐 **Cross-Platform Ready** | Works seamlessly on Windows, macOS, or Linux — no path rewrites needed. |
| 🚀 **CI/CD Integration** | GitHub Actions and AWS CodeBuild configurations included for automated builds. |
| 🛰️ **Watch System** | File watchers with smart-diff detection for continuous development automation. |
| 🖥️ **System Tray Commander** | Control builds from system tray with color indicators and audio feedback. |
| 🎧 **Audio Engine** | Modular sound cue system with MP3/WAV support for build events. |

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/ChristopherElgin/SonicBuilderSupersonic.git
cd SonicBuilderSupersonic
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install reportlab segno qrcode[pil] pikepdf
```

### 3️⃣ Create lean environment
```bash
python make_supersonic_lean_auto.py
```

---

## 🚀 Quick Start

### Build everything
```bash
python supersonic_build_all.py
```

### Build + publish to GitHub
```bash
python supersonic_build_all.py --publish
```

### Generate mission cards
```bash
python make_supersonic_cards_autoattach.py --auto-run
```

**Output:**
```
SonicBuilder/docs/
 ├── Mission_Summary_Card.pdf
 ├── Mission_Summary_Card_Light.pdf
 └── Mission_Cards_Supersonic_v3.2.1.zip
```

---

## 📦 Build Traceability

Every build embeds the exact repo and version:

```json
"build_origin": {
  "repo": "https://github.com/ChristopherElgin/SonicBuilderSupersonic",
  "tag_or_commit": "v3.2.1"
}
```

---

## 📁 Repository Structure

```
SonicBuilder/
 ├── dsp/              # DSP configuration templates
 ├── docs/             # Generated documentation + cards
 ├── extras/           # Optional media or calibration files
 └── tools/            # Build tools (e.g., diff_render_html.py)
builder.py
supersonic_build_all.py
supersonic_verify.py
make_supersonic_lean_auto.py
make_supersonic_cards_autoattach.py
BUILD_REPORT.md
CHANGELOG.md
```

---

## 🏷️ Releasing

Tag a new version:
```bash
git tag v3.2.1
git push origin v3.2.1
```

Then publish:
```bash
python supersonic_build_all.py --publish
```

---

## 📄 License

MIT License — see `LICENSE` for details.

---

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/ChristopherElgin/SonicBuilderSupersonic/issues)
- **Docs:** [README.md](https://github.com/ChristopherElgin/SonicBuilderSupersonic#readme)

---

**Built with ⚡ by the SonicBuilder team**
