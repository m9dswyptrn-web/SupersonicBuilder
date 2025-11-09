import pathlib

README = pathlib.Path("README.md")
text = README.read_text(encoding="utf-8") if README.exists() else "# SonicBuilder\n\n"

block = """\
### 📦 Documentation & Release Pipeline Status

| Stage | Workflow | Status | Description |
|------:|:---------|:------:|:------------|
| 🛡️ **Guard** | [Release Guard](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/release-guard.yml) | ![Release Guard](https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/release-guard.yml?label=guard) | Ensures `/docs-ready` PRs and checks pass before publishing. |
| 🧾 **Docs Build** | [Docs Release](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/docs-release.yml) | ![Docs Release](https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-release.yml?label=docs) | Builds light/dark manuals, stamps metadata, attaches PDFs to releases. |
| 🔍 **Smoke Test** | [Pages Smoke Test](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/pages-smoketest.yml) | ![Pages Smoke](https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/pages-smoketest.yml?label=pages%20smoke) | Verifies GitHub Pages is up and serving the latest docs. |
"""

inserted = False
lines = text.splitlines()
for i, line in enumerate(lines[:15]):
    if "shields.io" in line or "![" in line:
        lines.insert(i + 1, "")
        lines.insert(i + 2, block)
        inserted = True
        break

if not inserted:
    lines.insert(1, block)

README.write_text("\n".join(lines), encoding="utf-8")
print("✅ README updated with Documentation & Release Pipeline Status section.")
