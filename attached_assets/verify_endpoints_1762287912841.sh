    #!/usr/bin/env bash
    # verify_endpoints.sh — quick health/sync test
    # Usage:
    #   BASE_URL="http://localhost:8000" ./verify_endpoints.sh
    #   (defaults to http://localhost:8000)
    set -euo pipefail

    BASE_URL="${BASE_URL:-http://localhost:8000}"

    has_jq() { command -v jq >/dev/null 2>&1; }
    pretty() { if has_jq; then jq .; else cat; fi; }

    echo "== GET $BASE_URL/api/ping =="
    curl -sS "$BASE_URL/api/ping" | pretty || true

    echo -e "
== GET $BASE_URL/api/ready =="
    code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/ready" || true)
    echo "HTTP $code"
    if [[ "$code" != "200" ]]; then
      echo "Not ready (yet)."
    fi

    echo -e "
== GET $BASE_URL/api/status =="
    curl -sS "$BASE_URL/api/status" | pretty || true

    echo -e "
== POST $BASE_URL/api/sync =="
    curl -sS -X POST "$BASE_URL/api/sync" | pretty || true

    echo -e "
Done."
