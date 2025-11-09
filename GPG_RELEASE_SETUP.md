# 🔐 GPG Release Signing Setup Guide

Complete guide for cryptographically signing your releases with GPG.

---

## 🎯 What This Does

Your release system now includes **cryptographic verification**:

1. ✅ **SHA-256 checksums** generated for all artifacts
2. ✅ **GPG signature** on `SHA256SUMS.txt`
3. ✅ **Post-release verification** workflow
4. ✅ **Tamper detection** for all downloads

---

## 🔑 Generate GPG Key (One-time Setup)

### Step 1: Generate New Key Pair

```bash
# Generate GPG key (follow prompts)
gpg --full-generate-key

# Choose:
# - Type: (1) RSA and RSA
# - Size: 4096 bits
# - Expiry: 0 (never) or 2y (2 years)
# - Name: Your Name or "Supersonic Release Signing Key"
# - Email: your@email.com
# - Passphrase: Create a strong passphrase
```

### Step 2: List Keys

```bash
# List your keys
gpg --list-secret-keys --keyid-format LONG

# Output looks like:
# sec   rsa4096/ABCD1234EFGH5678 2025-11-04 [SC]
#       Full-fingerprint-here
# uid   [ultimate] Your Name <your@email.com>
```

Copy the **key ID** (e.g., `ABCD1234EFGH5678`)

### Step 3: Export Keys

```bash
# Replace ABCD1234EFGH5678 with your key ID
KEY_ID="ABCD1234EFGH5678"

# Export PRIVATE key (ASCII-armored)
gpg --armor --export-secret-keys $KEY_ID > private-key.asc

# Export PUBLIC key (ASCII-armored)
gpg --armor --export $KEY_ID > public-key.asc
```

---

## 🔒 Add Secrets to GitHub

### Required Secrets

Go to: `https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings/secrets/actions`

Add these secrets:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `GPG_PRIVATE_KEY` | Full contents of `private-key.asc` | **KEEP SECRET!** |
| `GPG_PASSPHRASE` | Your GPG key passphrase | Optional (empty if no passphrase) |
| `GPG_KEYID` | Your key ID (e.g., `ABCD1234EFGH5678`) | Optional but recommended |
| `RELEASE_GPG_PUBLIC_KEY` | Full contents of `public-key.asc` | For verification workflow |

### How to Add Secrets

```bash
# 1. Go to repository settings
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings/secrets/actions

# 2. Click "New repository secret"

# 3. For GPG_PRIVATE_KEY:
#    Name: GPG_PRIVATE_KEY
#    Value: Paste entire contents of private-key.asc (including BEGIN/END lines)

# 4. For RELEASE_GPG_PUBLIC_KEY:
#    Name: RELEASE_GPG_PUBLIC_KEY
#    Value: Paste entire contents of public-key.asc

# 5. For GPG_PASSPHRASE:
#    Name: GPG_PASSPHRASE
#    Value: Your passphrase (if you set one)

# 6. For GPG_KEYID:
#    Name: GPG_KEYID
#    Value: ABCD1234EFGH5678 (your key ID)
```

---

## 🚀 Using the System

### Local Signing (Manual)

```bash
# 1. Generate checksums
python3 tools/release_artifacts_guard.py \
  --globs "dist/**
build/**
**/*.zip" \
  --out SHA256SUMS.txt

# 2. Sign checksums (requires GPG key in env)
export GPG_PRIVATE_KEY="$(cat private-key.asc)"
export GPG_PASSPHRASE="your-passphrase"
python3 tools/sign_checksums.py

# 3. Verify signature works
gpg --verify SHA256SUMS.txt.asc SHA256SUMS.txt
```

### GitHub Actions (Automatic)

The existing `.github/workflows/release.yml` workflow will automatically:

1. ✅ Build artifacts
2. ✅ Generate `SHA256SUMS.txt`
3. ✅ Sign with GPG → `SHA256SUMS.txt.asc`
4. ✅ Upload both to GitHub Release

**You need to add the signing step to your workflow** (see below).

---

## 📝 Update Your Release Workflow

Add this to `.github/workflows/release.yml`:

```yaml
# Add to env section at top:
env:
  ARTIFACT_GLOBS: |
    dist/**
    build/**
    **/*.zip
    **/*.tar.gz
    !**/node_modules/**
    !**/.venv/**
  ART_MAX_PER_MB: "300"
  ART_MAX_TOTAL_MB: "1200"

# Add these steps before "Create Release":
      - name: Guard artifacts + generate checksums
        run: |
          python3 tools/release_artifacts_guard.py \
            --globs "${{ env.ARTIFACT_GLOBS }}" \
            --out SHA256SUMS.txt

      - name: Sign checksums (GPG detached)
        env:
          GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
          GPG_KEYID: ${{ secrets.GPG_KEYID }}
        run: |
          sudo apt-get update && sudo apt-get install -y gnupg
          python3 tools/sign_checksums.py

# Update "files:" in Create Release step:
          files: |
            SHA256SUMS.txt
            SHA256SUMS.txt.asc
            dist/**
            build/**
```

---

## ✅ Post-Release Verification

The `post_release_verify.yml` workflow **automatically runs** after each release:

1. ✅ Downloads all release assets
2. ✅ Imports your public GPG key
3. ✅ Verifies `SHA256SUMS.txt.asc` signature
4. ✅ Verifies all file checksums
5. ✅ Posts result to Release notes

**Triggers**:
- Automatically on every release
- Manually from Actions tab

---

## 🧪 Testing the System

### Test Locally

```bash
# 1. Create test artifacts
mkdir -p dist
echo "test content" > dist/test.txt

# 2. Generate checksums
python3 tools/release_artifacts_guard.py \
  --globs "dist/**" \
  --out SHA256SUMS.txt

# 3. Sign
export GPG_PRIVATE_KEY="$(cat private-key.asc)"
export GPG_PASSPHRASE="your-passphrase"
python3 tools/sign_checksums.py

# 4. Verify
gpg --verify SHA256SUMS.txt.asc SHA256SUMS.txt
# Should output: "Good signature from ..."

# 5. Verify checksums
mkdir verify
cp SHA256SUMS.txt dist/test.txt verify/
python3 tools/verify_release_assets.py --dir verify
# Should output: "✅ All 1 files match SHA256SUMS.txt"
```

### Test on GitHub

```bash
# 1. Create test release
git tag -a v0.0.1-test -m "Test release"
git push origin v0.0.1-test

# 2. Watch Actions
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/actions

# 3. Check that:
#    - Release workflow creates SHA256SUMS.txt + .asc
#    - Post-release verify workflow runs
#    - Verification passes

# 4. Delete test release
gh release delete v0.0.1-test --yes
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

---

## 🔍 Verify a Release (User Side)

Users can verify your releases:

```bash
# 1. Download release assets
TAG="v1.0.0"
gh release download $TAG -R ChristopherElgin/SonicBuilderSupersonic

# 2. Import your public key
curl -L https://github.com/ChristopherElgin.gpg | gpg --import
# Or manually: gpg --import public-key.asc

# 3. Verify signature
gpg --verify SHA256SUMS.txt.asc SHA256SUMS.txt
# Should show: "Good signature from Your Name <your@email.com>"

# 4. Verify checksums
sha256sum -c SHA256SUMS.txt
# Should show: "OK" for all files
```

---

## 🛡️ Security Best Practices

### Private Key Security

- ✅ **Never commit** `private-key.asc` to git
- ✅ **Backup** your private key securely (password manager, encrypted drive)
- ✅ **Use passphrase** on GPG key
- ✅ **Rotate keys** every 1-2 years
- ✅ **Revoke** if compromised

### Secrets Management

- ✅ GitHub Secrets are **encrypted at rest**
- ✅ Only accessible to workflow runs
- ✅ Never logged or exposed
- ✅ Rotate if you suspect compromise

### Key Expiry

```bash
# Set expiry on existing key
gpg --edit-key ABCD1234EFGH5678
> expire
> 2y  # 2 years
> save
```

---

## 📊 Tools Overview

| Tool | Exit Code | Purpose |
|------|-----------|---------|
| `release_artifacts_guard.py` | 42 | Budget check + SHA256SUMS.txt generation |
| `require_artifacts.py` | 43 | Ensure required artifacts exist |
| `sign_checksums.py` | 44, 45 | GPG sign SHA256SUMS.txt |
| `verify_release_assets.py` | 46 | Verify checksums match |
| Post-release workflow | 47 | GPG verify + checksum verify |

---

## 🎯 Complete Release Workflow

```bash
# 1. Local build
make build  # or your build command

# 2. Preflight check
python3 tools/release_artifacts_guard.py \
  --globs "dist/**" \
  --out SHA256SUMS.txt

# 3. Sign (if testing locally)
export GPG_PRIVATE_KEY="$(cat private-key.asc)"
python3 tools/sign_checksums.py

# 4. Commit & tag
git add -A
git commit -m "build: release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"

# 5. Push (triggers GitHub Actions)
git push origin main v1.0.0

# 6. GitHub Actions automatically:
#    - Builds artifacts
#    - Generates SHA256SUMS.txt
#    - Signs with GPG
#    - Creates GitHub Release
#    - Runs post-release verification
```

---

## ✅ Verification Checklist

After your first signed release:

- [ ] Release created on GitHub
- [ ] `SHA256SUMS.txt` attached to release
- [ ] `SHA256SUMS.txt.asc` attached to release
- [ ] Post-release verify workflow ran
- [ ] Verification passed (check Actions tab)
- [ ] Release notes show "✅ PASS" verification status

---

## 🚨 Troubleshooting

### "Missing GPG_PRIVATE_KEY"

```bash
# Check secret is set in GitHub
# Settings > Secrets > Actions > GPG_PRIVATE_KEY
```

### "Bad signature"

```bash
# Ensure public key matches private key
gpg --list-keys
gpg --list-secret-keys

# Re-export if needed
gpg --armor --export $KEY_ID > public-key.asc
```

### "Verification failed"

```bash
# Check workflow logs
# Actions > Post-Release Verify > Latest run

# Manually test
python3 tools/verify_release_assets.py --dir verify
```

---

## 📚 Resources

- **GPG Manual**: https://www.gnupg.org/documentation/
- **GitHub Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Best Practices**: https://riseup.net/en/security/message-security/openpgp/best-practices

---

## ✨ You're Protected!

Your releases now have:
- ✅ Cryptographic signatures
- ✅ Tamper detection
- ✅ Automated verification
- ✅ Audit trail

**Users can trust your releases!** 🔐
