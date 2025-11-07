# SonicBuilder CoA Generator - QR URL Configuration

## Auto-Detection of Repository URL

The CoA generator now automatically detects your repository URL with smart fallback:

1. **Environment Variable:** `SB_REPO_URL` (highest priority)
2. **Config File:** `config/repo_urls.json`
3. **Git Remote:** Auto-detect from `.git/config`
4. **Replit Domain:** Falls back to your Replit dev URL
5. **Default:** `https://example.com/sonicbuilder`

## Quick Start

### On Replit (Current Setup)
```bash
cd tools/CoA_Generator
python generate_coa.py --auto-increment --version v2.0.9
```
**QR URL Generated:** `https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev/coa/0002`

### With GitHub Repository
```bash
# Option 1: Set environment variable
export SB_REPO_URL="https://github.com/YourUser/YourRepo"
python generate_coa.py --auto-increment

# Option 2: Update config/repo_urls.json
# Edit: "github_url": "https://github.com/YourUser/YourRepo"
python generate_coa.py --auto-increment
```
**QR URL Generated:** `https://github.com/YourUser/YourRepo/coa/0002`

### Override Per-CoA
```bash
python generate_coa.py --auto-increment --qr "https://custom.url/build/0042"
```

## Configuration File

Edit `config/repo_urls.json`:
```json
{
  "github_url": "",
  "replit_domain": "08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev",
  "default_base": "https://example.com/sonicbuilder"
}
```

**Priority:**
1. If `github_url` is set → use GitHub
2. Else if `replit_domain` exists → use Replit
3. Else → use `default_base`

## URL Formats

### Replit (Current)
```
https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev/coa/0002
```

### GitHub (After Setup)
```
https://github.com/YourUser/sonicbuilder/coa/0002
```

### Custom Domain
```
https://sonicbuilder.io/builds/0002
```

## GitHub Workflow

The `.github/workflows/qr-url-fallback.yml` workflow automatically:
- Detects if GitHub URL is configured
- Updates `config/repo_urls.json` on first push
- Uses GitHub URL in auto-generated CoAs

## Examples

### Replit Development
```bash
# Uses Replit domain automatically
python generate_coa.py --auto-increment
# QR: https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev/coa/0003
```

### GitHub Production
```bash
# After setting github_url in config/repo_urls.json
python generate_coa.py --auto-increment
# QR: https://github.com/YourUser/sonicbuilder/coa/0003
```

### Custom Per-Build
```bash
python generate_coa.py --auto-increment \
  --customer "Acme Corp" \
  --qr "https://sonicbuilder.io/customers/acme-001"
```

## Environment Variables

```bash
# Override repository URL
export SB_REPO_URL="https://github.com/user/repo"

# Override Replit domain (auto-detected from REPLIT_DOMAINS)
export REPLIT_DOMAINS="your-custom.replit.dev"

# Run generator
python generate_coa.py --auto-increment
```

## Migration Path

### Phase 1: Replit Development (Current)
- Uses Replit domain automatically
- QR codes point to Replit preview

### Phase 2: GitHub Integration
- Push to GitHub
- Update `config/repo_urls.json` with GitHub URL
- QR codes switch to GitHub

### Phase 3: Custom Domain
- Set custom domain in config
- QR codes use production URL

## Testing

```bash
# Test with different URLs
SB_REPO_URL="https://test.com" python generate_coa.py --serial 9999
# Check QR code in output/SonicBuilder_CoA_#9999.pdf

# Test auto-detection
python generate_coa.py --serial 9998
# Should use Replit domain or config value
```

## Current Configuration

**Replit Domain:** `08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev`  
**GitHub URL:** Not set (will use Replit fallback)  
**Status:** ✅ Ready for Replit development

---

**Next Steps:**
1. Keep using Replit domain for development
2. When ready, push to GitHub and update `config/repo_urls.json`
3. QR codes will automatically use GitHub URL
