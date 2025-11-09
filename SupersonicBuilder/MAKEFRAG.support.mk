# --- Diagnostics & Support (fragment) -----------------------------------------
DIAG_DIR     ?= diag
SUPPORT_DIR  ?= support
OUT_DIR      ?= output
DIST_DIR     ?= dist
GIT_SHA      := $(shell git rev-parse --short=10 HEAD 2>/dev/null || echo unknown)
STAMP        := $$(date -u +%Y%m%d_%H%M%S)

.PHONY: diag-env
diag-env:
	@python tools/diag/collect_env.py
	@cd $(DIAG_DIR) && zip -qr ../diag_bundle.zip . && mv ../diag_bundle.zip .
	@echo "[diag] bundle ready at $(DIAG_DIR)/diag_bundle.zip"

.PHONY: support-bundle-full
support-bundle-full: diag-env
	@mkdir -p $(SUPPORT_DIR)
	@echo "$(GIT_SHA)" > $(SUPPORT_DIR)/GIT_SHA.txt
	@cp -f VERSION $(SUPPORT_DIR)/ 2>/dev/null || true
	@cp -f $(DIAG_DIR)/diag_bundle.zip $(SUPPORT_DIR)/ 2>/dev/null || true
	@find $(OUT_DIR) -maxdepth 1 -type f \( -name "*.pdf" -o -name "*.sha256" \) -print0 2>/dev/null | xargs -0 -I{} cp -f "{}" $(SUPPORT_DIR)/ 2>/dev/null || true
	@find $(DIST_DIR) -maxdepth 1 -type f -name "*.pdf" -print0 2>/dev/null | xargs -0 -I{} cp -f "{}" $(SUPPORT_DIR)/ 2>/dev/null || true
	@cd $(SUPPORT_DIR) && sha256sum * 2>/dev/null | tee SUPPORT_SHA256.txt || true
	@cd $(SUPPORT_DIR) && zip -qr ../support_bundle_$(STAMP)_g$(GIT_SHA).zip . && mv ../support_bundle_$(STAMP)_g$(GIT_SHA).zip .
	@echo "[support] bundle ready at $(SUPPORT_DIR)/support_bundle_$(STAMP)_g$(GIT_SHA).zip"
