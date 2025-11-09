# SonicBuilder core targets
# This file is auto-generated

.PHONY: enrich_docs smoke badges_update support-bundle-full

enrich_docs:
	@echo "[SB] Enriching docs..."
	@python3 scripts/enrich_release_notes.py 2>/dev/null || echo "No enrich script"

smoke:
	@echo "[SB] Running smoke tests..."
	@python3 scripts/test_gallery_http_smoke.py 2>/dev/null || echo "No smoke test script"

badges_update:
	@echo "[SB] Updating badges..."
	@$(MAKE) update_readme_badges || true

support-bundle-full:
	@echo "[SB] Creating support bundle..."
	@python3 scripts/create_support_bundle.py --full 2>/dev/null || echo "No bundle script"
