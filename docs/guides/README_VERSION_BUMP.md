# Version bump patch

This sets project version to **v2.0.9+SB-appendix-demo**.

## Apply

```bash
git add VERSION CHANGELOG.md MAKEFRAG.version_hint
git commit -m "chore(version): bump to v2.0.9+SB-appendix-demo"
git push
git tag v2.0.9+SB-appendix-demo
git push --tags
```

## What Happens Next

After pushing the tag, your CI/CD workflows will automatically:

1. **release-appendixC.yml** - Build and upload 4 PDFs + ZIP package
2. **coa-on-release.yml** - Auto-mint Certificate of Authenticity #0007
3. **release-notes-enricher.yml** - Add professional asset table to release notes
4. **notify.py** - Send webhook notification (if configured)

Total time: ~5-7 minutes for complete professional release! 🚀
