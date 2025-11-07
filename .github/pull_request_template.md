<!-- Thanks for contributing to SonicBuilder! -->

## Summary
Describe what this PR does and why.

## Changes
- [ ] ...

## Screenshots / Artifacts (optional)
Attach PDFs or screenshots if useful. CI will upload `/output/**` and `/dist/**` artifacts automatically.

## Checklist
- [ ] Ran `make verify` (dark) locally
- [ ] Ran `THEME=light make verify` (if relevant)
- [ ] Valid JSONs (manifest / annotations / themes)
- [ ] Assets added under `assets/` and referenced in manifest
- [ ] Ran `make demos` and spot-checked outputs in `/output/`
- [ ] CI is green

## Links
- Issue(s): #...
- Related PR(s): #...

## Reviewer Notes
Anything specific you want reviewers to focus on (e.g., annotation coordinates, SVG rendering, frame styling).

---

## CI Requirements
- [ ] **Docs Build must pass** (PDFs + checksums) — see the Actions tab → *docs-build*
- [ ] If this PR changes release docs, ensure **Latest Docs** block renders correctly

> **Maintainer Commands:**  
> • `/docs-ready` → apply **docs:ready** after verifying artifacts  
> • `/docs-reset` → remove **docs:ready** (e.g., after changes require fresh docs-build)
