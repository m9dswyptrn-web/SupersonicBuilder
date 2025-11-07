# Supersonic Control Core — v4 Ultimate Edition
# Include from your root Makefile:
#   -include make/ControlCore.mk

# ========= Config =========
MODE               ?= commander
AI_ASSET           ?= SonicBuilder_Supersonic_Overlays_MEGA_v2.zip
PY                 ?= python3
SUP_AUTOPUSH       ?= 1
SUP_ENGINE_MODE    ?= hybrid
VOICE_EVENT        ?= deploy_done

# ========= Phony =========
.PHONY: ai-help ai-build ai-watch ai-bump ai-release \
        ai-doctor ai-rollback ai-hash ai-sbom ai-notes \
        ai-voice ai-announce ai-voice-install \
        ai-voicepack ai-voicepacks ai-voicepack-list ai-voicepack-current ai-voicepack-use \
        ai-voicepack-preview ai-voicepack-audition ai-voicepack-smoke ai-voicepack-smoke-repair \
        ai-console ai-lastgood \
        unit-deploy unit-reboot unit-logs

# ========= Helper =========
_define_env = SUP_AUTOPUSH=$(SUP_AUTOPUSH) SUP_ENGINE_MODE=$(SUP_ENGINE_MODE)

# ========= Core Ops =========
ai-build:
	@$(_define_env) $(PY) helpers/supersonic_core.py build --ai

ai-watch:
	@$(_define_env) $(PY) helpers/supersonic_core.py watch --ai

ai-bump:
	@$(_define_env) $(PY) scripts/version_bump.py

# Full pipeline: bump -> build -> integrity -> sbom -> notes -> notify
ai-release:
	@$(MAKE) ai-bump
	@$(MAKE) ai-build || true
	@$(MAKE) ai-hash
	@$(MAKE) ai-sbom
	@$(MAKE) ai-notes
	@$(_define_env) $(PY) scripts/notify_webhooks.py --asset "$(AI_ASSET)" || true

# ========= Utilities =========
ai-doctor:
	@$(PY) scripts/doctor.py

# Usage: make ai-rollback TAG=v2.3.1
ai-rollback:
	@$(PY) scripts/rollback.py $(TAG)

ai-hash:
	@$(PY) scripts/integrity.py

ai-sbom:
	@$(PY) scripts/sbom_scan.py

ai-notes:
	@$(PY) scripts/release_notes_ai.py

# ========= Voice & Console =========
ai-voice:
	@$(PY) helpers/supersonic_core.py set-voice $(MODE)

ai-announce:
	@VOICE_PACK=$(MODE) VOICE_EVENT=$(VOICE_EVENT) $(PY) helpers/supersonic_voice_console.py

# Usage: make ai-voice-install URL=https://example.com/MyPack.zip
ai-voice-install:
	@test -n "$(URL)" || (echo "ERROR: provide URL=..."; exit 1)
	@$(PY) scripts/voicepack_manager.py "$(URL)"

# ========= Voice Pack Management =========
# Generate single voice pack (default: commander, or VOICE_PACK=aiops)
ai-voicepack:
	@$(PY) scripts/generate_commander_voicepack.py

# Generate all 5 voice packs (commander, aiops, flightops, industrialops, arcadehud)
ai-voicepacks:
	@$(PY) scripts/generate_multipack_voicepacks.py

# List available voice packs
ai-voicepack-list:
	@$(PY) scripts/voicepack_switch.py list

# Show currently active voice pack
ai-voicepack-current:
	@$(PY) scripts/voicepack_switch.py current

# Usage: make ai-voicepack-use PACK=arcadehud
ai-voicepack-use:
	@test -n "$(PACK)" || (echo "ERROR: provide PACK=<name>"; exit 1)
	@$(PY) scripts/voicepack_switch.py use "$(PACK)"
	@$(MAKE) ai-voicepack-current

# Usage: make ai-voicepack-preview PACK=arcadehud [DELAY=0.6] [SHUFFLE=0] [KEEP=0]
ai-voicepack-preview:
	@test -n "$(PACK)" || (echo "ERROR: provide PACK=<name>"; exit 1)
	@$(PY) scripts/voicepack_preview.py "$(PACK)" $(if $(filter 1,${SHUFFLE}),--shuffle,) $(if $(filter 1,${KEEP}),--keep-active,) --delay $(if ${DELAY},${DELAY},0.6)

# Friendly alias (same args)
ai-voicepack-audition: ai-voicepack-preview

# Validate all packs (no changes)
ai-voicepack-smoke:
	@$(PY) scripts/voicepack_smoketest.py || true

# Validate + auto-repair missing/corrupt assets
ai-voicepack-smoke-repair:
	@$(PY) scripts/voicepack_smoketest.py --repair --strict || true

# ========= Recovery & Mission Control =========
# Open Last Known Good release (Pages + Release links)
ai-lastgood:
	@$(PY) scripts/ai_lastgood.py || echo "Fallback: gh not available"

# Launch AI Mission Console (TUI)
ai-console:
	@echo "🚀 Launching Supersonic AI Console..."
	@$(PY) scripts/ai_console.py || echo "⚠️  Could not launch console — ensure Python 3 is available."

# ========= Android / Head Unit =========
# Usage: make unit-deploy APK=app-release.apk
unit-deploy:
	@test -n "$(APK)" || (echo "ERROR: provide APK=path/to.apk"; exit 1)
	@$(PY) scripts/adb_actions.py deploy "$(APK)"

unit-reboot:
	@$(PY) scripts/adb_actions.py reboot

unit-logs:
	@$(PY) scripts/adb_actions.py logs

# ========= Help =========
ai-help:
	@echo "Supersonic v4 Ultimate Edition Targets:"
	@echo ""
	@echo "Core Build Operations:"
	@echo "  ai-build        - Build with AI summary"
	@echo "  ai-watch        - Watch + AI"
	@echo "  ai-bump         - Smart semver bump (feat/fix/breaking)"
	@echo "  ai-release      - Full pipeline (bump->build->hash->sbom->notes->notify)"
	@echo ""
	@echo "Diagnostics & Utilities:"
	@echo "  ai-doctor       - Preflight environment diagnostics"
	@echo "  ai-rollback     - Roll back to TAG=vX.Y.Z"
	@echo "  ai-hash         - SHA256 + optional Cosign signing"
	@echo "  ai-sbom         - SBOM + security scan"
	@echo "  ai-notes        - AI release notes"
	@echo ""
	@echo "Voice Pack Management:"
	@echo "  ai-voicepack             - Generate single pack (VOICE_PACK=commander)"
	@echo "  ai-voicepacks            - Generate all 5 packs"
	@echo "  ai-voicepack-list        - List available packs"
	@echo "  ai-voicepack-current     - Show active pack"
	@echo "  ai-voicepack-use         - Switch pack (PACK=arcadehud)"
	@echo "  ai-voicepack-preview     - Audition pack (PACK=flightops DELAY=0.6 SHUFFLE=0)"
	@echo "  ai-voicepack-smoke       - Validate all packs"
	@echo "  ai-voicepack-smoke-repair- Auto-repair missing assets"
	@echo "  ai-voice                 - Set voice MODE=$(MODE)"
	@echo "  ai-announce              - Play voice event VOICE_EVENT=$(VOICE_EVENT)"
	@echo "  ai-voice-install         - Install voicepack from URL=..."
	@echo ""
	@echo "Mission Control & Recovery:"
	@echo "  ai-console      - Launch AI Mission Console (TUI)"
	@echo "  ai-lastgood     - Open Last Known Good release"
	@echo ""
	@echo "Android / Head Unit:"
	@echo "  unit-deploy     - Deploy APK=... to head unit"
	@echo "  unit-reboot     - Reboot head unit"
	@echo "  unit-logs       - Fetch logcat dump"
