# Supersonic Overlays: Release Signing + OPA Policy Guard (Additive-only)

**Release signing** — `.github/workflows/release-signing-cosign-supersonic.yml`

- Keyless OIDC signing of release assets using Cosign; uploads `.sig` files to the same release.

**OPA guard** — `.github/workflows/opa-policy-guard-supersonic.yml`

- Evaluates Rego in `policies/supersonic/*.rego` against PR metadata. Deny messages fail the job.

Promote overlays later by renaming (remove `-supersonic`).
