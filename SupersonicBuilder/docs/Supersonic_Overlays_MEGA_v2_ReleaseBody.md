# 🚀 Supersonic Overlays — MEGA v2 (Commander Edition)

**Tag:** `v2.0.0-supersonic`
**Target:** `m9dswyptrn-web/SonicBuilder`
**Container:** `ghcr.io/m9dswyptrn-web/sonicbuilder:latest`
**Edition:** Full CI/CD · Security · Provenance · Governance · Voice Telemetry

## 🧩 Highlights
| Category | Module | Description |
|-----------|---------|-------------|
| 🐳 **CI/CD** | Docker Publish | GHCR buildx cache, multi-tag, OIDC push |
| 📚 **Docs** | Verify + Auto-Fix Preview + Pages Deploy | Lint, preview artifacts, full site deploy |
| 🛡️ **Security** | CodeQL, Trivy, Scorecard | Static + runtime vulnerability scanning |
| 📦 **Supply Chain** | SBOM + SLSA Provenance | SPDX JSON + attestation for containers/files |
| 🔏 **Integrity** | Cosign OIDC Signing | Keyless signatures per release asset |
| ⚖️ **Governance** | OPA Policy Guard | PR title convention + protected-file rules |
| 🔉 **Voice Telemetry** | FlightOps, SciFiControl, IndustrialOps, ArcadeHUD | Live audio cues for build/deploy/fail events |

## 🧠 Embedded Voice Packs
Run voice cues locally/Replit:
```bash
VOICE_PACK=flightops VOICE_EVENT=build_start python helpers/supersonic_voice_console.py
```
Toggle silent mode with `QUIET=1`.

## 🧰 Installation Paths
```
.github/workflows/      → CI/CD pipelines (-supersonic)
helpers/                → voice & verification utilities
policies/supersonic/    → OPA governance policies
assets/audio/           → embedded WAV voice packs
docs/README_MEGA_v2.md  → deployment quick guide
```

## 🧾 Validation Checklist
- [ ] Docker Publish → `ghcr.io/m9dswyptrn-web/sonicbuilder`
- [ ] Docs Verify / Pages Deploy
- [ ] CodeQL / Trivy / Scorecard in Security tab
- [ ] SBOM & SLSA artifacts
- [ ] Release Signing uploads `.sig`
- [ ] OPA Guard blocks bad PR titles
- [ ] Voice Telemetry cue playable

## 🔒 Security & Compliance
GitHub OIDC is used for signing/attestations. No external secrets needed. Overlays are additive-only.

## 🌀 Rollback
Remove `*-supersonic.yml` and the added helper/policy/audio folders, commit, and push.
