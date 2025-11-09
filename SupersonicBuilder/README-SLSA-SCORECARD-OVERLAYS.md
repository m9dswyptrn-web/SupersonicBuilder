# Supersonic SLSA + Scorecard Overlays (Additive-only)

**Files:**
- `.github/workflows/slsa-provenance-supersonic.yml` — On-demand provenance for a container digest or file artifact.
- `.github/workflows/scorecard-supersonic.yml` — Weekly OpenSSF Scorecard with SARIF upload.

## Usage
### SLSA
- For a pushed container digest (e.g., from GHCR): run the workflow with
  - `subject`: `ghcr.io/<org>/<image>@sha256:<digest>`
  - `is-container`: `true`
- For a local artifact file added to the repo: run with
  - `subject`: relative path to file
  - `is-container`: `false`

### Scorecard
- Runs weekly. You can also `Run workflow` manually to generate a fresh report in the repository’s Security tab.
