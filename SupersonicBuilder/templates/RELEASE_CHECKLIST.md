# 📦 SonicBuilder — Documentation Release Checklist

✅ **Version**: `{VERSION}`  
🪪 **Commit**: `{COMMIT}`  
📅 **Date**: `{DATE}`

---

## 🚀 Preflight

- [ ] Run `make docs_release_local_strict` to generate and verify docs
- [ ] Run `make badge_compute_complete_local` to check completeness
- [ ] Run `make badges_local_on` to preview the local completeness badge
- [ ] Check `.status/docs-release-completeness.local.json` for ✅ `complete`
- [ ] Review CHANGELOG: `make changelog_preview`

---

## 🏷️ Tag & Push

- [ ] `make release_tag VERSION={VERSION}`
- [ ] Review changes: `git diff`
- [ ] `git add CHANGELOG.md README.md .status/`
- [ ] `git commit -m "docs: prepare release {VERSION}"`
- [ ] `git tag {VERSION}`
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
