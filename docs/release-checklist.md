# 📦 SonicBuilder — Documentation Release Checklist

✅ **Version**: `v2.1.0`  
🪪 **Commit**: `476ff0f024f1`  
📅 **Date**: `2025-10-29 01:04:16 UTC`

---

## 🚀 Preflight

- [ ] Run `make docs_release_local_strict` to generate and verify docs
- [ ] Run `make badge_compute_complete_local` to check completeness
- [ ] Run `make badges_local_on` to preview the local completeness badge
- [ ] Check `.status/docs-release-completeness.local.json` for ✅ `complete`
- [ ] Review CHANGELOG: `make changelog_preview`

---

## 🏷️ Tag & Push

- [ ] `make release_tag VERSION=v2.1.0`
- [ ] Review changes: `git diff`
- [ ] `git add CHANGELOG.md README.md .status/`
- [ ] `git commit -m "docs: prepare release v2.1.0"`
- [ ] `git tag v2.1.0`
- [ ] `git push && git push --tags`

---

## 🧪 CI/CD Verification

- [ ] Wait for `docs-release` workflow to finish
- [ ] Check **Docs Release** badge ✅  
- [ ] Check **Docs Complete** badge ✅
- [ ] Verify GitHub Release created with all assets

---

## 📎 Post-Release

- [ ] Verify all required assets in GitHub Release
- [ ] Verify `README` badges show live endpoints
- [ ] Test download & extract of release artifacts
- [ ] Update project documentation if needed
- [ ] Celebrate 🍻 — another verified SonicBuilder release shipped!

---

🧰 **Pro Tip:**  
You can run `make release_tag VERSION=vX.Y.Z` to automate CHANGELOG + badge switching.
