#!/usr/bin/env bash
set -euo pipefail

# Bash GitHub Release autopublisher using gh CLI.
# Requirements:
#   - GitHub CLI installed: https://cli.github.com/
#   - Auth: gh auth login (or set GH_TOKEN/GITHUB_TOKEN)
#
# Usage:
#   ./helpers/autopublish_release.sh \
#     --repo m9dswyptrn-web/SonicBuilder \#     --tag v2.0.0-supersonic \#     --name "Supersonic Overlays — MEGA v2 (Commander Edition)" \#     --body-file docs/Supersonic_Overlays_MEGA_v2_ReleaseBody.md \#     --asset SonicBuilder_Supersonic_Overlays_MEGA_v2.zip \#     [--draft true] [--prerelease false]

repo=""
tag=""
name=""
body_file=""
asset=""
draft="false"
prerelease="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) repo="$2"; shift 2;;
    --tag) tag="$2"; shift 2;;
    --name) name="$2"; shift 2;;
    --body-file) body_file="$2"; shift 2;;
    --asset) asset="$2"; shift 2;;
    --draft) draft="$2"; shift 2;;
    --prerelease) prerelease="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "[error] gh CLI not found. Install from https://cli.github.com/"
  exit 1
fi

if [[ -z "${repo}" || -z "${tag}" || -z "${name}" || -z "${body_file}" || -z "${asset}" ]]; then
  echo "Missing required args. See header usage."
  exit 2
fi

if [[ ! -f "${body_file}" ]]; then
  echo "[error] body file not found: ${body_file}"
  exit 1
fi

if [[ ! -f "${asset}" ]]; then
  echo "[warn] asset not found: ${asset} (continuing; will create release without asset)"
fi

# Normalize booleans
to_flag() {
  local v="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
  if [[ "$v" == "1" || "$v" == "true" || "$v" == "yes" || "$v" == "y" ]]; then echo "true"; else echo "false"; fi
}
draft="$(to_flag "${draft}")"
prerelease="$(to_flag "${prerelease}")"

set +e
gh release view "${tag}" -R "${repo}" >/dev/null 2>&1
exists=$?
set -e

if [[ $exists -ne 0 ]]; then
  echo "[info] creating release ${tag} in ${repo}"
  gh release create "${tag}"     -R "${repo}"     --title "${name}"     --notes-file "${body_file}"     $( [[ "${draft}" == "true" ]] && echo "--draft" )     $( [[ "${prerelease}" == "true" ]] && echo "--prerelease" )

else
  echo "[info] updating release ${tag} in ${repo}"
  gh release edit "${tag}"     -R "${repo}"     --title "${name}"     --notes-file "${body_file}"     $( [[ "${draft}" == "true" ]] && echo "--draft" || echo "--draft=false" )     $( [[ "${prerelease}" == "true" ]] && echo "--prerelease" || echo "--prerelease=false" )
fi

if [[ -f "${asset}" ]]; then
  echo "[info] uploading asset: ${asset}"
  gh release upload "${tag}" "${asset}" -R "${repo}" --clobber
fi

echo "[ok] release ready: https://github.com/${repo}/releases/tag/${tag}"
