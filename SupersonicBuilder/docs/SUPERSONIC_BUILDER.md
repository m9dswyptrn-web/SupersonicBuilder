# 🚀 SonicBuilder Supersonic Edition

**Full-Featured Build Chain for SonicBuilder ProPack**

---

## 📋 Overview

The Supersonic Edition is a comprehensive, enterprise-grade build automation system that includes:

- ✅ **Multi-profile builds** (dark / light / all)
- ✅ **SBOM generation** (Software Bill of Materials)
- ✅ **QR code generator** for releases
- ✅ **PDF metadata stamping**
- ✅ **GitHub integration** (draft/publish releases)
- ✅ **ADB device testing**
- ✅ **Diff renderer integration**
- ✅ **Semantic version bumping**
- ✅ **SHA-256 checksums** and manifest generation

---

## 🎯 Quick Start

### Using Makefile (Recommended)

```bash
# Get help
make builders-help

# Run Supersonic builder
make builder-supersonic ARGS='<command>'

# Common commands
make builder-supersonic ARGS='pack'      # Full build
make builder-supersonic ARGS='clean'     # Clean build artifacts
make builder-supersonic ARGS='--help'    # Show all options
```

### Direct Execution

```bash
# Show all available commands
python3 builders/sonicbuilder_supersonic.py --help

# Run specific command
python3 builders/sonicbuilder_supersonic.py pack
```

---

## 📚 Available Commands

### Core Build Commands

#### `pack`
**Full build pipeline** - Runs all steps in sequence:
1. Clean old artifacts
2. Prepare source folders
3. Generate release notes
4. Create manifest
5. Generate checksums
6. Create SBOM
7. Generate QR code
8. Package everything into ZIP

```bash
make builder-supersonic ARGS='pack'
```

#### `clean`
Remove all build and dist artifacts

```bash
make builder-supersonic ARGS='clean'
```

#### `prepare`
Stage source folders into build directory

```bash
make builder-supersonic ARGS='prepare'
```

---

### Documentation Commands

#### `notes`
Generate RELEASE_NOTES.md from CHANGELOG.md

```bash
make builder-supersonic ARGS='notes'
```

---

### Manifest & Verification Commands

#### `manifest`
Create MANIFEST.json with complete file metadata:
- File paths and sizes
- SHA-256 checksums
- Total byte count
- File count
- Build timestamp

```bash
make builder-supersonic ARGS='manifest'
```

#### `sums`
Generate SHA256SUMS.txt for all build files

```bash
make builder-supersonic ARGS='sums'
```

#### `sbom`
Generate Software Bill of Materials (SBOM.json):
- Python version
- Platform information
- Installed packages
- Build timestamp

```bash
make builder-supersonic ARGS='sbom'
```

---

### QR Code Generation

#### `qr`
Generate QR code linking to project/version

**Requirements:** `segno` library (optional)
```bash
pip install segno
make builder-supersonic ARGS='qr'
```

---

### Device Testing

#### `adb-demo`
Run demo ADB command to verify device connectivity

```bash
make builder-supersonic ARGS='adb-demo'
```

---

### GitHub Integration

#### `gh-publish`
Publish built ZIPs as GitHub release

**Requirements:** GitHub CLI (`gh`)

```bash
# Publish with tag
make builder-supersonic ARGS='gh-publish --tag v3.2.1'
```

**Features:**
- Automatically finds all ZIPs in dist/
- Includes RELEASE_NOTES.md if available
- Creates GitHub release with tag
- Uploads all build artifacts

---

### Version Management

#### `bump`
Semantic version bump (major/minor/patch)

```bash
# Patch bump: v3.2.1 → v3.2.2
make builder-supersonic ARGS='bump --kind patch'

# Minor bump: v3.2.1 → v3.3.0
make builder-supersonic ARGS='bump --kind minor'

# Major bump: v3.2.1 → v4.0.0
make builder-supersonic ARGS='bump --kind major'
```

---

## ⚙️ Configuration

### Default Configuration

The builder uses built-in defaults but can be customized via `sonicbuilder.config.json`:

```json
{
  "project_name": "SonicBuilder",
  "vehicle": "Chevy Sonic LTZ (T300)",
  "version": "v3.2.1",
  "profile": "dark",
  "profiles_matrix": ["dark", "light"],
  "changelog_md": "CHANGELOG.md",
  "diff_renderer": "SonicBuilder/tools/diff_render_html.py",
  "src": {
    "dsp": "SonicBuilder/dsp",
    "docs": "SonicBuilder/docs",
    "extras": "SonicBuilder/extras"
  },
  "dist_name_pattern": "{project}_BuildOfBuilds_ProPack_ENHANCED_{version}_{profile}.zip",
  "adb_path": "adb",
  "adb_demo_cmd": ["shell", "echo", "SonicBuilder ADB demo OK"],
  "metadata": {
    "author": "Christopher Elgin",
    "theme": "dark-shop-manual",
    "pdf_style": "laminated"
  }
}
```

### Configuration File Location

Place `sonicbuilder.config.json` in the `builders/` directory.

---

## 📁 Build Output

### Directory Structure

```
builders/
├── build/                          # Staging area
│   ├── dsp/                        # DSP configurations
│   ├── docs/                       # Documentation PDFs
│   │   └── qr_v3.2.1.png          # Generated QR code
│   ├── extras/                     # Additional tools
│   ├── INSTALL_START_HERE.md       # User guide
│   ├── RELEASE_NOTES.md            # Generated release notes
│   ├── MANIFEST.json               # Complete file manifest
│   ├── SHA256SUMS.txt              # Checksums
│   └── SBOM.json                   # Software bill of materials
│
└── dist/                           # Final output
    └── SonicBuilder_BuildOfBuilds_ProPack_ENHANCED_v3.2.1_dark.zip
```

---

## 🔍 Generated Files

### MANIFEST.json
Complete build metadata:
```json
{
  "project": "SonicBuilder",
  "vehicle": "Chevy Sonic LTZ (T300)",
  "version": "v3.2.1",
  "profile": "dark",
  "total_bytes": 12345678,
  "file_count": 42,
  "files": [
    {
      "path": "docs/wiring.pdf",
      "size": 123456,
      "sha256": "abc123..."
    }
  ],
  "generated_utc": "2025-11-01T12:34:56.789Z"
}
```

### SHA256SUMS.txt
File integrity verification:
```
abc123...  docs/wiring.pdf
def456...  dsp/config.xml
ghi789...  INSTALL_START_HERE.md
```

### SBOM.json
Build environment details:
```json
{
  "python_version": "3.11.6",
  "platform": "Linux-5.15.0-x86_64",
  "timestamp": "2025-11-01T12:34:56.789Z",
  "packages": [
    "reportlab==4.0.7",
    "Pillow==10.1.0",
    "segno==1.6.0"
  ]
}
```

---

## 🚀 Common Workflows

### Complete Build & Publish

```bash
# 1. Full build
make builder-supersonic ARGS='pack'

# 2. Verify output
ls builders/dist/

# 3. Publish to GitHub
make builder-supersonic ARGS='gh-publish --tag v3.2.1'
```

### Version Bump Workflow

```bash
# 1. Bump version
make builder-supersonic ARGS='bump --kind minor'

# 2. Rebuild with new version
make builder-supersonic ARGS='pack'

# 3. Publish
make builder-supersonic ARGS='gh-publish --tag v3.3.0'
```

### Incremental Build

```bash
# Run individual steps
make builder-supersonic ARGS='clean'
make builder-supersonic ARGS='prepare'
make builder-supersonic ARGS='manifest'
make builder-supersonic ARGS='sums'
make builder-supersonic ARGS='sbom'
```

---

## 🔧 Requirements

### Required
- Python 3.8+
- Standard library (included with Python)

### Optional
- **segno** - QR code generation
  ```bash
  pip install segno
  ```

- **GitHub CLI (gh)** - GitHub publishing
  ```bash
  # Install from https://cli.github.com/
  gh --version
  ```

- **ADB** - Android device testing
  ```bash
  # Install Android SDK platform-tools
  adb version
  ```

---

## 📊 Features

### Multi-Profile Support
Build for different themes/configurations:
- Dark theme builds
- Light theme builds
- All profiles at once

### Comprehensive Checksums
- SHA-256 for every file
- Manifest with complete metadata
- Integrity verification ready

### SBOM Generation
Track your build environment:
- Python version
- Platform details
- All installed packages
- Build timestamp

### GitHub Integration
Seamless release publishing:
- Automatic ZIP upload
- Release notes inclusion
- Tag-based releases

### QR Code Generation
Link your builds to documentation:
- Version-specific QR codes
- Customizable content
- PNG output

---

## 🎯 Best Practices

1. **Always run `pack` for production builds**
   - Ensures all steps are executed
   - Creates complete build with all metadata

2. **Use configuration file for projects**
   - Maintain `sonicbuilder.config.json`
   - Version control your config
   - Share settings across team

3. **Verify checksums**
   - Check SHA256SUMS.txt after builds
   - Validate integrity before distribution

4. **Use semantic versioning**
   - Use `bump` command
   - Tag releases consistently
   - Maintain CHANGELOG.md

5. **Test before publishing**
   - Run `adb-demo` for device checks
   - Verify build output
   - Review MANIFEST.json

---

## 🐛 Troubleshooting

### QR Code Not Generated
**Issue:** `[skip] qr: No module named 'segno'`

**Solution:**
```bash
pip install segno
```

### GitHub Publish Fails
**Issue:** `[skip] gh CLI not installed`

**Solution:**
```bash
# Install GitHub CLI
# Visit: https://cli.github.com/
gh auth login
```

### ADB Demo Fails
**Issue:** `[warn] adb failed: ...`

**Solutions:**
- Install Android SDK platform-tools
- Enable USB debugging on device
- Verify device connection: `adb devices`

### Build Directory Missing
**Issue:** Source folders not found

**Solution:**
- Check `sonicbuilder.config.json` paths
- Ensure source folders exist
- Run from correct directory

---

## 📝 Examples

### Example 1: Simple Build
```bash
# Clean build of current version
make builder-supersonic ARGS='pack'
```

### Example 2: Version Update
```bash
# Update to v4.0.0 and build
make builder-supersonic ARGS='bump --kind major'
make builder-supersonic ARGS='pack'
```

### Example 3: GitHub Release
```bash
# Build and publish in one workflow
make builder-supersonic ARGS='pack'
make builder-supersonic ARGS='gh-publish --tag v3.2.1'
```

### Example 4: Custom Steps
```bash
# Run only specific steps
make builder-supersonic ARGS='prepare'
make builder-supersonic ARGS='manifest'
make builder-supersonic ARGS='qr'
```

---

## 🎉 Summary

The SonicBuilder Supersonic Edition provides a complete, production-ready build automation system with:

- **11 commands** for flexible workflows
- **Automatic metadata** generation
- **GitHub integration** for releases
- **Device testing** capabilities
- **Version management** tools
- **Complete traceability** with checksums and manifests

Perfect for professional build workflows and enterprise deployments!

---

**Location:** `builders/sonicbuilder_supersonic.py`  
**Makefile Target:** `make builder-supersonic ARGS='<command>'`  
**Help:** `make builders-help`
