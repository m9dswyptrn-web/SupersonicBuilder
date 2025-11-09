# Supersonic Full Health Scan

Enterprise-grade project health auditor with reversible file organization.

## Quick Start

```bash
# Scan only (generates report)
make health-scan

# Scan + organize orphan files (with undo log)
make health-apply

# Scan + run CI checks
make health-ci

# View the report
make health-open
```

## What It Does

The health scanner analyzes your entire project and generates `docs/HEALTH_REPORT.md` with:

### ✅ Quality Checks
- **Python files**: Total count, unique files (SHA-256 dedup)
- **Duplicates**: Exact content matches across codebase
- **Compile errors**: Syntax errors caught before runtime
- **Orphans**: Files outside expected directories
- **Package coverage**: Modules not exported by `supersonic_pkg/__init__.py`
- **Repo hygiene**: Missing configs, badges, stale doc stamps
- **Large assets**: Files over size thresholds
- **CI gate**: Optional `make ci-check` execution

### 🎯 File Classification

Every Python file is automatically classified as:
- **Standalone**: Executable scripts (has `if __name__ == "__main__"`)
- **Package**: Library modules (classes, functions, no main)
- **Snippet**: Code fragments, incomplete files

### 📁 Auto-Organization

The `--apply` mode moves orphan files into proper locations:
```
Orphan scripts → Organized structure
─────────────────────────────────────
standalone scripts  → tools/
package modules     → supersonic_pkg/
code snippets       → extras/snippets/
```

## Usage Examples

### Basic Scan

```bash
# Scan only (no changes)
python3 supersonic_full_health_scan.py

# Or use Makefile
make health-scan
```

**Output**: `docs/HEALTH_REPORT.md`

### Organize Orphans (with undo log)

```bash
# Auto-organize + log moves
make health-apply

# Or manually with custom log
python3 supersonic_full_health_scan.py --apply --log-file .supersonic/moves.log
```

**What happens**:
1. Scans all Python files
2. Classifies each file (standalone/package/snippet)
3. Moves orphans to proper directories
4. Logs every move to `.supersonic/moves.log` (JSONL format)
5. Re-runs scan to show updated state

### Undo Moves (Reversible!)

```bash
# Undo all moves from default log
make health-undo

# Undo from specific log
make health-undo LOG=.supersonic/moves_2025-11-03T13-22-55Z.log

# Force undo (skip SHA verification)
python3 supersonic_full_health_scan.py --undo --force-undo --log-file .supersonic/moves.log
```

**Safety features**:
- SHA-256 verification before restore
- Collision-safe: restores as `filename__restoreN.py` if original path taken
- Skips files that have been modified since move

### Scan + CI Gate

```bash
# Scan + run CI checks
make health-ci

# Or with organize
make health-apply-ci
```

Runs your CI gate:
- Prefers `make ci-check` if Makefile exists
- Falls back to: `pytest -q && ruff check . && mypy . && pyright`

### Advanced Options

```bash
# Custom asset threshold (flag files > 200 MB)
python3 supersonic_full_health_scan.py --max-asset-mb 200

# Fail on warnings (not just critical issues)
python3 supersonic_full_health_scan.py --fail-on-warn

# All together
python3 supersonic_full_health_scan.py --apply --ci-check --max-asset-mb 300 --log-file .supersonic/moves.log
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make health-scan` | Scan only, generate report |
| `make health-ci` | Scan + run CI gate |
| `make health-apply` | Auto-organize orphans (logged) |
| `make health-apply-ci` | Organize + CI gate |
| `make health-undo` | Undo moves from log |
| `make health-open` | Open report in browser/editor |
| `make health-clean-ledgers` | Delete all move logs |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | OK - no issues or only minor warnings |
| `1` | Warnings (if `--fail-on-warn` enabled) |
| `2` | Critical issues: compile errors, duplicates, missing configs, CI failed |
| `99` | Unexpected error (Python exception) |

## Report Sections

### 🔴 Critical Issues (block exit code 0)
- **Compile errors**: Syntax errors that prevent file execution
- **Duplicates**: Exact file copies (wasted space, confusion)
- **Missing configs**: Required files like `pyproject.toml`, `Makefile`, CI workflows

### 🟡 Warnings (informational, or exit code 1 with `--fail-on-warn`)
- **Orphans**: Files outside `tools/`, `supersonic_pkg/`, `extras/snippets/`
- **Unexported modules**: Modules in package but not in `__init__.py`
- **Missing badges**: CI/Pages badges not in README
- **Large assets**: Files over threshold (default 300 MB)
- **Stale stamps**: "Last updated" dates > 45 days old

## Move Ledger Format

Each move is logged as JSONL (one JSON object per line):

```json
{
  "ts": "2025-11-04T12:34:56Z",
  "action": "move",
  "src": "/path/to/original.py",
  "dst": "/path/to/destination.py",
  "kind": "standalone",
  "sha256": "a1b2c3..."
}
```

## Integration with Build System

Add to your CI workflow:

```yaml
- name: Health Scan
  run: |
    python3 supersonic_full_health_scan.py --ci-check --fail-on-warn
    cat docs/HEALTH_REPORT.md
```

## Configuration

Expected directory structure:
```
project/
├── tools/              # Standalone scripts (executables)
├── supersonic_pkg/     # Python package (library modules)
├── extras/snippets/    # Code fragments, templates
├── docs/               # Documentation
└── .supersonic/        # Health scan logs
```

Expected config files checked:
- `Makefile` or `make/ControlCore.mk`
- `pyproject.toml`
- `requirements.txt`
- `.pre-commit-config.yaml`
- `mypy.ini`
- `pyrightconfig.json`
- CI workflow: `.github/workflows/ci.yml` or `.github/workflows_new/ci.yml`

## Tips

1. **Run before releases**: Catch issues before tagging
2. **CI integration**: Add to GitHub Actions for continuous monitoring
3. **Regular cleanup**: Use `--apply` periodically to keep files organized
4. **Safe experimentation**: All moves are reversible with `--undo`
5. **Custom thresholds**: Adjust `--max-asset-mb` for your project needs

## Troubleshooting

**"ERROR: --undo requires --log-file"**
- Provide log file path: `--undo --log-file .supersonic/moves.log`

**"Skip (hash mismatch)"**
- File changed since move, SHA verification failed
- Use `--force-undo` to override (dangerous!)

**"No moves recorded"**
- Log file empty or doesn't exist
- Run `--apply` first to generate moves

**Compile errors from system packages**
- Normal for `.pythonlibs/` files (external dependencies)
- Focus on your project files in the report

---

**Last Updated**: 2025-11-04  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
