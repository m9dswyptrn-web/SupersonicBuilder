# Supersonic Security Overlays (Additive-only)

These overlays add security scanning and SBOM generation without touching any existing workflows.

**Included:**
- `.github/workflows/codeql-supersonic.yml` — GitHub CodeQL analysis for Python
- `.github/workflows/trivy-supersonic.yml` — Trivy filesystem + (optional) Docker image scan
- `.github/workflows/sbom-slsa-supersonic.yml` — SBOM (SPDX JSON via Syft) + optional keyless attestation with Cosign

## Usage
- **CodeQL/Trivy** run automatically on pushes/PRs.
- **SBOM** runs on push or manual dispatch; set the dispatch input `attest: true` to attempt keyless attestation.
- All files use `-supersonic` suffixes so they won’t conflict; rename later if you choose to promote to primary workflows.
