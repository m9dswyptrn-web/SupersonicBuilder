# Versioning & Auto-Bump

- Run `make bump FROM=v2.0.9 TO=v2.0.9` to update strings in text files and founder seal SVG.
- Use `make stamp_meta VERSION=v2.0.9 IN=... OUT=...` to stamp PDFs with updated metadata.
- Optional CI: `.github/workflows/version-bump-on-appendix.yml` bumps to v2.0.9 automatically when PCB photos/I²S taps paths change.
