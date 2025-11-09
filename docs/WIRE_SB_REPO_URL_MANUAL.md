# Wiring SB_REPO_URL into Manual Builds

This patch ensures your manual builds receive a canonical repository link for
QR codes, PDF metadata, and footer stamping.

## Files

- `.github/workflows/manual-build.yml` — CI job that builds manuals with `SB_REPO_URL`
- `make_patches/MAKEFRAG.urls` — Makefile fragment to include in your `Makefile`
- Use together with `.github/workflows/repo-url-setup.yml` (from the previous patch)

## Integrate

1. Copy `make_patches/MAKEFRAG.urls` to your repo root.
2. In your `Makefile` add near the top:

```make
-include MAKEFRAG.urls
```

3. Wherever you call your Python stampers or metadata tools, pass `$(SB_REPO_URL)`
   as a CLI flag/environment. Example:

```make
build_dark:
	@$(MAKE) echo-url
	$(PY) scripts/pdf_stamp_metadata.py --url "$(SB_REPO_URL)" --in output/sonic_manual_dark.pdf --out output/sonic_manual_dark.pdf
```

4. Commit and push. The workflow `manual-build.yml` will run on pushes to `main`
   and will set `SB_REPO_URL` automatically via the reusable `repo-url-setup.yml`.
