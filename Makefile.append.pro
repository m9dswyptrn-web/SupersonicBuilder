# ==== PRO Manual Add-ons ======================================================
.PHONY: pro_cover parts_sheet appendix_wiring final_manual_pro

# Generate a branded cover page (set THEME=dark|light; default dark)
pro_cover:
	$(PY) scripts/make_cover.py --hero assets/grz_overlay_photo.jpg \
		--title "2014 Chevy Sonic LTZ" \
		--subtitle "Android Head-Unit Install Guide" \
		--brand "Sonic Builder" \
		--version $$(cat VERSION) \
		--theme $${THEME:-dark} -o output/_cover.pdf

# Parts & Tools with QR codes (edit config/parts.csv)
parts_sheet:
	$(PY) scripts/make_parts_sheet.py --csv config/parts.csv \
		--theme $${THEME:-dark} -o output/_parts.pdf

# Appendix renders wiring/diagram images as full-page plates
appendix_wiring:
	$(PY) scripts/make_image_appendix.py -o output/_appendix.pdf

# Merge: cover + existing manual + parts + appendix
final_manual_pro: pro_cover parts_sheet appendix_wiring
	$(PY) scripts/merge_pdfs.py \
		output/_cover.pdf \
		output/sonic_manual_$${THEME:-dark}.pdf \
		output/_parts.pdf \
		output/_appendix.pdf \
		-o output/sonic_manual_$${THEME:-dark}_PRO.pdf
	@echo "Wrote output/sonic_manual_$${THEME:-dark}_PRO.pdf"
