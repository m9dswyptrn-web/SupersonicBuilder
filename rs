#!/usr/bin/env bash
set -euo pipefail

car_board_link() {
  python3 tools/car_board_link.py "$@"
}

car_install_plus() {
  bash tools/car_install_plus.sh "$@"
}

sonic_preinstall() {
  bash tools/sonic_preinstall.sh "$@"
}

sonic_postinstall() {
  bash tools/sonic_postinstall.sh "$@"
}

supersonic_preflight() {
  python3 tools/supersonic_preflight.py "$@"
}

supersonic_postinstall_v4() {
  python3 tools/supersonic_post_install.py "$@"
}

# -------------------------
# RS – Replit Shell CLI
# Unified control for your SupersonicBuilder autonomy stack
# -------------------------

# Ports (respect existing env, fall back to your working defaults)
STATUS_PORT="${AUTONOMY_STATUS_PORT:-6000}"
BRIDGE_PORT="${AUTONOMY_BRIDGE_PORT:-6800}"
BOARD_PORT="${AUTONOMY_BOARD_PORT:-8008}"
LOG_DIR="logs"; RUN_DIR=".run"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-12}"

# Colors
g(){ printf "\033[32m%s\033[0m\n" "$*"; }
y(){ printf "\033[33m%s\033[0m\n" "$*"; }
r(){ printf "\033[31m%s\033[0m\n" "$*"; }
b(){ printf "\033[36m%s\033[0m\n" "$*"; }

need() { command -v "$1" >/dev/null 2>&1 || { r "Missing: $1"; exit 127; }; }

port_up() {
  local p="$1"
  # Try ss, then nc, then /proc
  if command -v ss >/dev/null 2>&1; then ss -tlpn 2>/dev/null | grep -qE "LISTEN .* :$p "; return $?; fi
  if command -v nc >/dev/null 2>&1; then nc -z 127.0.0.1 "$p" >/dev/null 2>&1; return $?; fi
  awk -v p="$(printf '%04X' "$p")" 'NR>1{ if(substr($2,10,4)==p) {found=1; exit} } END{ exit(found?0:1) }' /proc/net/tcp 2>/dev/null
}

wait_port() {
  local p="$1" name="${2:-port $1}" secs="$HEALTH_TIMEOUT"
  for ((i=0;i<secs;i++)); do port_up "$p" && { g "✅ $name up on :$p"; return 0; }; sleep 1; done
  r "❌ $name did not come up on :$p"; return 1
}

health_status() {
  local ok=0
  # Status server: HTTP /health
  if curl -fsS "http://127.0.0.1:${STATUS_PORT}/health" >/dev/null 2>&1; then
    g "✅ Status server healthy (:${STATUS_PORT})"
  else
    if port_up "$STATUS_PORT"; then y "⚠️  Status port open but /health failed (:${STATUS_PORT})"; else r "❌ Status server down (:${STATUS_PORT})"; fi
    ok=1
  fi
  # Shell bridge: port-only check (no GET endpoint)
  if port_up "$BRIDGE_PORT"; then
    g "✅ Shell Bridge listening (:${BRIDGE_PORT})"
  else
    r "❌ Shell Bridge down (:${BRIDGE_PORT})"; ok=1
  fi
  # Healthboard (optional)
  if port_up "$BOARD_PORT"; then
    g "✅ Healthboard up (:${BOARD_PORT})"
  else
    y "ℹ️ Healthboard not detected (:${BOARD_PORT})"
  fi
  return $ok
}

start_services() {
  mkdir -p "$RUN_DIR" "$LOG_DIR"
  # Prefer your simple launcher if present
  if [[ -x "./START_AUTONOMY.sh" ]]; then
    g "▶️  Launching via START_AUTONOMY.sh…"
    nohup bash ./START_AUTONOMY.sh >>"$LOG_DIR/start.out" 2>&1 &
  else
    g "▶️  Launching autonomy_manager.py directly…"
    ALLOW_SHELL=1 AUTONOMY_STATUS_PORT="$STATUS_PORT" AUTONOMY_BRIDGE_PORT="$BRIDGE_PORT" \
      nohup python3 -u scripts/autonomy_manager.py >>"$LOG_DIR/autonomy_manager.out" 2>&1 &
  fi
  # Give things a moment and verify
  wait_port "$STATUS_PORT" "Status server" || true
  wait_port "$BRIDGE_PORT" "Shell bridge" || true
}

stop_services() {
  y "⏹  Stopping services…"
  pkill -f "autonomy_manager.py"     >/dev/null 2>&1 || true
  pkill -f "status_server.py"        >/dev/null 2>&1 || true
  pkill -f "shell_bridge.py"         >/dev/null 2>&1 || true
  pkill -f "healthboard.py"          >/dev/null 2>&1 || true
  sleep 1
}

show_logs() {
  local n="${1:-80}"
  for f in autonomy_manager.out status.out bridge.out start.out healthboard.out; do
    if [[ -f "$LOG_DIR/$f" ]]; then
      b "---- $LOG_DIR/$f (last $n lines) ----"; tail -n "$n" "$LOG_DIR/$f" || true
    fi
  done
}

doctor() {
  b "🔎 RS Doctor — prerequisites"; need curl; g "curl ✔︎"
  b "🔎 Ports"; echo "STATUS_PORT=$STATUS_PORT  BRIDGE_PORT=$BRIDGE_PORT  BOARD_PORT=$BOARD_PORT"
  b "🔎 Health check"; if health_status; then g "✅ All healthy"; else r "❌ Issues detected"; return 1; fi
}

heal() {
  b "🛠  RS Heal — check → (maybe) restart → verify"
  if health_status; then g "✅ Already healthy; no action needed."; return 0; fi
  y "♻️  Attempting recovery: stop → start"
  stop_services
  start_services
  sleep 1
  if health_status; then g "✅ Recovery successful"; return 0; fi
  r "❌ Recovery failed — check logs with: ./rs logs"; return 2
}

board() {
  b "📊 Healthboard"
  echo "URL: http://localhost:${BOARD_PORT}"
  if ! port_up "$BOARD_PORT"; then
    y "Healthboard not running; attempting to launch…"
    AUTONOMY_HEALTHBOARD_PORT="${BOARD_PORT}" \
      nohup python3 -u tools/healthboard.py >>"$LOG_DIR/healthboard.out" 2>&1 & disown || true
    wait_port "$BOARD_PORT" "Healthboard" || true
  fi
}

status() { health_status; }
start()  { start_services; health_status; }
stop()   { stop_services; g "✅ Stopped"; }
restart(){ stop_services; start_services; health_status; }

guard() {
  # Lightweight guard loop that only heals when something fails
  local interval="${1:-3}"
  b "🛡  RS Guard loop (every ${interval}s) — healing only on failures (Ctrl+C to exit)"
  while true; do
    if ! health_status; then
      y "⚠️  Health FAIL → healing…"; heal || true
    fi
    sleep "$interval"
  done
}

push() {
  # Safety: require explicit opt-in
  if [[ "${RS_ALLOW_PUSH:-0}" != "1" ]]; then
    r "Push disabled. Set RS_ALLOW_PUSH=1 to enable:  RS_ALLOW_PUSH=1 ./rs push"
    exit 3
  fi
  need git
  b "⬆️  Git push (auto-commit)"
  git add -A
  git commit -m "RS: automated commit $(date -u +"%Y-%m-%dT%H:%M:%SZ")" || true
  git push
  g "✅ Pushed"
}

usage() {
  cat <<USAGE
RS — Replit Shell CLI
Usage: ./rs <command>

Core Commands:
  doctor        Run full health diagnostics
  status        Quick health check
  start         Start autonomy stack
  stop          Stop all services
  restart       Restart stack
  heal          Heal only if unhealthy
  logs [N]      Tail last N lines of all logs (default 80)
  board         Ensure Healthboard is up and show URL
  guard [secs]  Watch + heal loop (default 3s)
  push          Git add/commit/push (requires RS_ALLOW_PUSH=1)

Shell Guard & Enhanced Diagnostics:
  where         Verify you're at repo root (checks .replit, rs, .git, docs/)
  autoplace     Find repo root from anywhere and show cd command
  doctor-plus   Comprehensive diagnostic sweep (where→health→doctor→sonic→car→metrics)
  launch-all [N] Safe stack launcher with optional guard mode (N=interval in seconds)

Console Bridge (Bidirectional Command Executor):
  console       Start interactive shell bridge (execute commands from Agent console)
  console "cmd" Execute single shell command and stream output

Monitoring:
  health        Health probe → logs/health.json
  metrics       Refresh badges from health data
  diag          Full diagnostic (health→metrics→print)
  pulse         Health→metrics→GitHub Pages sync

Car Profile:
  car-install   Toggle car install mode on/off
  car-metrics   Export car profile metrics
  sonic-checklist  Sonic installation checklist

Ports (override via env):
  AUTONOMY_STATUS_PORT (default 6000)
  AUTONOMY_BRIDGE_PORT (default 6800)
  AUTONOMY_BOARD_PORT  (default 8008)

Examples:
  ./rs where                 # Check if at repo root
  ./rs launch-all            # Start stack with health check
  ./rs launch-all 5          # Start stack + enter 5-second guard loop
  ./rs doctor-plus           # Full system diagnostic
USAGE
}


# ==================== NEW CAR PROFILE FUNCTIONS ====================

docs() {
    subcmd="${1:-hub}"
    shift || true
    DOC_FILES=()
    [ -f QUICKSTART.md ] && DOC_FILES+=("QUICKSTART.md")
    [ -f INTEGRATION_COMPLETE.md ] && DOC_FILES+=("INTEGRATION_COMPLETE.md")
    [ -f replit.md ] && DOC_FILES+=("replit.md")
    
    case "$subcmd" in
        hub|"")
            echo ""
            echo "📘  RS Documentation Hub"
            echo "──────────────────────────────────"
            if [ ${#DOC_FILES[@]} -eq 0 ]; then
                echo "⚠ No docs found yet."
            else
                for f in "${DOC_FILES[@]}"; do
                    printf "✔ %s\n" "$f"
                done
            fi
            echo ""
            echo "🌐 Local Dashboard: http://localhost:${AUTONOMY_BOARD_PORT:-8008}"
            echo ""
            ;;
        search)
            term="${1:-}"
            [ -z "$term" ] && { echo "Usage: ./rs docs search <term>"; exit 64; }
            echo "🔍 Searching docs for: \"$term\""
            grep -Rni "$term" "${DOC_FILES[@]}" 2>/dev/null || echo "No matches found"
            ;;
        *)
            echo "Usage: ./rs docs [hub|search TERM]"
            exit 64
            ;;
    esac
}

docs_snap() {
    mkdir -p snapshots
    ts=$(date -u +"%Y%m%d-%H%M%S")
    SNAP_DIR="snapshots/docs-$ts"
    mkdir -p "$SNAP_DIR"
    
    echo "📸 Docs snapshot → $SNAP_DIR"
    [ -f QUICKSTART.md ] && cp QUICKSTART.md "$SNAP_DIR"/
    [ -f INTEGRATION_COMPLETE.md ] && cp INTEGRATION_COMPLETE.md "$SNAP_DIR"/
    [ -f replit.md ] && cp replit.md "$SNAP_DIR"/
    
    echo "✅ Snapshot created"
}

diag_all() {
    echo "🩺 RS diag-all"
    echo "=============================="
    ./rs diag || true
    echo ""
    echo "📘 Docs: $(ls -1 *.md 2>/dev/null | wc -l) markdown files"
    echo "✅ diag-all complete"
}

metrics_plus() {
    echo "📊 RS metrics-plus"
    ./rs health || true
    ./rs metrics || true
    ./rs docs-snap 2>/dev/null || true
    ./rs car-metrics 2>/dev/null || true
    ./rs sonic-checklist export 2>/dev/null || true
    echo "✅ metrics-plus complete"
}

car_profile() {
    subcmd="${1:-show}"
    shift || true
    
    case "$subcmd" in
        show)
            profile_id=$(cat state/car_profile.txt 2>/dev/null || echo "sonic_2014")
            echo "🚗 Current car profile: $profile_id"
            [ -f "profiles/$profile_id.json" ] && head -n 30 "profiles/$profile_id.json"
            ;;
        list)
            echo "🚗 Available car profiles:"
            ls -1 profiles/*.json 2>/dev/null | sed 's|profiles/||; s|\.json||' || echo "None found"
            ;;
        check)
            python3 tools/car_profile_check.py "$@"
            ;;
        *)
            echo "Usage: ./rs car-profile [show|list|check]"
            exit 64
            ;;
    esac
}

car_install_mode() {
    subcmd="${1:-status}"
    mkdir -p state
    FLAG_FILE="state/car_install_mode"
    [ -f "$FLAG_FILE" ] || echo "off" > "$FLAG_FILE"
    
    case "$subcmd" in
        on|enable)
            echo "on" > "$FLAG_FILE"
            echo "✅ Car install mode: ON"
            ;;
        off|disable)
            echo "off" > "$FLAG_FILE"
            echo "✅ Car install mode: OFF"
            ;;
        status)
            mode=$(cat "$FLAG_FILE")
            echo "🚦 Car install mode: $mode"
            ;;
        *)
            echo "Usage: ./rs car-install [on|off|status]"
            exit 64
            ;;
    esac
}

car_metrics() {
    echo "🚗 Car metrics export"
    python3 tools/car_mode_export.py 2>/dev/null && echo "✅ Car metrics updated" || echo "⚠ Export failed"
}

sonic_checklist() {
    subcmd="${1:-show}"
    
    case "$subcmd" in
        show)
            echo "🧾 Sonic Install Checklist"
            python3 tools/sonic_checklist_export.py >/dev/null 2>&1 || true
            if [ -f metrics/sonic_checklist.json ]; then
                python3 -c "import json; data=json.load(open('metrics/sonic_checklist.json')); [print(('\u2705' if i.get('status')=='done' else '\u2B1C') + ' ' + str(i.get('label'))) for i in data.get('items',[])]"
            fi
            ;;
        export)
            python3 tools/sonic_checklist_export.py
            ;;
        done)
            item_id="${1:-}"
            [ -z "$item_id" ] && { echo "Usage: ./rs sonic-checklist done <id>"; exit 64; }
                python3 -c "import json; data=json.load(open('metrics/sonic_checklist.json')); [print(('\u2705' if i.get('status')=='done' else '\u2B1C') + ' ' + str(i.get('label'))) for i in data.get('items',[])]"
            python3 tools/sonic_checklist_export.py >/dev/null 2>&1 || true
            ;;
        *)
            echo "Usage: ./rs sonic-checklist [show|export|done <id>]"
            exit 64
            ;;
    esac
}


board_setup() {
    echo "📷 Android 15 Board Photo Setup"
    if [ ! -f "android15_board_setup.py" ]; then
        echo "❌ android15_board_setup.py not found"
        exit 1
    fi
    
    subcmd="${1:-run}"
    
    case "$subcmd" in
        run)
            python3 android15_board_setup.py
            ;;
        view)
            if [ -f "docs/sonic/android15_board/board_map.md" ]; then
                cat docs/sonic/android15_board/board_map.md | head -100
                echo ""
                echo "📄 Full map: docs/sonic/android15_board/board_map.md"
            else
                echo "⚠ Board map not created yet. Run: ./rs board-setup run"
            fi
            ;;
        photos)
            echo "📸 Board photos:"
            ls -1 docs/sonic/headunit/board_photos/android15/*.jpg 2>/dev/null | grep -v "eoenkk_android15_" | head -20 || echo "No photos found"
            total=$(ls -1 docs/sonic/headunit/board_photos/android15/*.jpg 2>/dev/null | grep -v "eoenkk_android15_" | wc -l)
            echo ""
            echo "Total: $total photos (excluding aliases)"
            ;;
        *)
            echo "Usage: ./rs board-setup [run|view|photos]"
            exit 64
            ;;
    esac
}

cmd="${1:-doctor}"; shift || true
mkdir -p "$LOG_DIR" "$RUN_DIR"
case "$cmd" in
  board-setup|boardsetup) board_setup "$@";;
  docs) docs "$@";;
  docs-snap|snapdocs) docs_snap "$@";;
  diag-all) diag_all "$@";;
  metrics-plus) metrics_plus "$@";;
  car-profile) car_profile "$@";;
  car-install|install-mode) car_install_mode "$@";;
  car-metrics) car_metrics "$@";;
  sonic-checklist) sonic_checklist "$@";;
  doctor)  doctor "$@";;
  status)  status "$@";;
  start)   start "$@";;
  stop)    stop "$@";;
  restart) restart "$@";;
  heal)    heal "$@";;
  logs)    show_logs "${1:-80}";;
  board)   board "$@";;
  guard)   guard "${1:-3}";;
  push)    push;;
  car-board-link) car_board_link "$@";;
  car-install+|install+) car_install_plus "$@";;
  sonic-preinstall|preinstall) sonic_preinstall "$@";;
  sonic-postinstall|postinstall) sonic_postinstall "$@";;
  supersonic-preflight) supersonic_preflight "$@";;
  supersonic-postinstall-v4) supersonic_postinstall_v4 "$@";;
  
  # Health monitoring commands
  health)
    echo "🩺 rs health — probe ports/files → logs/health.json & .jsonl"
    python3 tools/health_probe.py
    ;;
  
  metrics)
    echo "📈 rs metrics — refresh badges from latest health + release"
    python3 tools/metrics_refresh.py
    ;;
  
  diag)
    echo "🔎 rs diag — health → metrics → print latest.json"
    python3 tools/health_probe.py
    python3 tools/metrics_refresh.py
    echo "— badges/latest.json —"
    cat badges/latest.json 2>/dev/null || true
    ;;
  
  rotate-logs)
    echo "🧹 rs rotate-logs — gzip + trim health.jsonl & zap.out"
    bash tools/rotate_logs.sh
    ;;
  
  pulse)
    echo "⚡ rs pulse — health → metrics → pages sync"
    python3 tools/health_probe.py || true
    python3 tools/metrics_refresh.py || true
    [ -x tools/sync_pages_artifacts.sh ] && bash tools/sync_pages_artifacts.sh || true
    echo "✓ Pulse complete"
    ;;
  
  cron-pulse)
    echo "⏲️ rs cron-pulse — loop 'rs pulse' every N minutes (default: 5)"
    MIN="${1:-5}"
    exec bash tools/cron_pulse.sh "$MIN"
    ;;
  
  alerts-test)
    echo "📣 rs alerts-test — send a Discord alert with current health"
    python3 tools/health_probe.py || true
    python3 tools/discord_alert.py || true
    ;;
  
  alerts-email-test)
    echo "📧 rs alerts-email-test — send an email with current health snapshot"
    python3 tools/health_probe.py || true
    python3 tools/email_alert.py  || true
    ;;
  
  # Shell Guard & Enhanced Diagnostics
  where)
    exec bash tools/rs_where_core.sh
    ;;
  
  autoplace)
    bash tools/rs_autoplace.sh "$@"
    ;;
  
  doctor-plus)
    bash tools/rs_doctor_plus.sh "$@"
    ;;
  
  launch-all)
    bash tools/rs_launch_all.sh "$@"
    ;;

  # Console Bridge (Bidirectional Command Executor)
  console)
    # $@ already contains everything after 'console' due to initial shift
    if (($#)); then 
      python3 tools/console_bridge.py "$@"
    else 
      python3 tools/console_bridge.py
    fi
    ;;

  -h|--help|help) usage;;
  *) r "Unknown command: $cmd"; usage; exit 64;;
esac

docs() {
    subcmd="${1:-hub}"
    shift || true

    DOC_FILES=()
    [ -f QUICKSTART.md ] && DOC_FILES+=("QUICKSTART.md")
    [ -f INTEGRATION_COMPLETE.md ] && DOC_FILES+=("INTEGRATION_COMPLETE.md")
    [ -f replit.md ] && DOC_FILES+=("replit.md")
    if [ -d docs ]; then
        while IFS= read -r f; do
            DOC_FILES+=("$f")
        done < <(find docs -type f -maxdepth 5 \( -name "*.md" -o -name "*.txt" \) | sort)
    fi

    case "$subcmd" in
        hub|"")
            echo ""
            echo "📘  RS Documentation Hub"
            echo "──────────────────────────────────"
            if [ ${#DOC_FILES[@]} -eq 0 ]; then
                echo "⚠ No docs found yet. Create QUICKSTART.md or docs/*.md"
            else
                for f in "${DOC_FILES[@]}"; do
                    printf "✔ %s\n" "$f"
                done
            fi
            echo ""
            echo "🌐 Local Dashboard:"
            echo "   http://localhost:${AUTONOMY_BOARD_PORT:-8008}"
            echo ""

            if [ -f .pages_url ]; then
                PAGES_URL=$(cat .pages_url 2>/dev/null || echo "")
                if [ -n "$PAGES_URL" ]; then
                    echo "📡 GitHub Pages Dashboard:"
                    echo "   $PAGES_URL"
                    echo ""
                fi
            fi

            echo "💡 Usage:"
            echo "   ./rs docs              # Hub (this view)"
            echo "   ./rs docs search term  # Search all docs"
            echo "   ./rs docs view quick   # View QUICKSTART.md"
            echo "   ./rs docs ask question # Smart search helper"
            echo ""
            ;;

        search)
            term="${1:-}"
            if [ -z "$term" ]; then
                echo "Usage: ./rs docs search <term>"
                exit 64
            fi
            if [ ${#DOC_FILES[@]} -eq 0 ]; then
                echo "No docs to search."
                exit 0
            fi
            echo "🔍 Searching docs for: \"$term\""
            echo "──────────────────────────────────"
            # Use grep with filename + line numbers, color if available
            if command -v rg >/dev/null 2>&1; then
                rg -n --hidden --glob '!*.git' --color=always -- "$term" "${DOC_FILES[@]}" || true
            else
                GREP_COLORS="mt=1;32" grep -Rni --color=always -- "$term" "${DOC_FILES[@]}" || true
            fi
            echo ""
            ;;

        view|show)
            target="${1:-quick}"
            file=""
            case "$target" in
                quick|quickstart)
                    [ -f QUICKSTART.md ] && file="QUICKSTART.md"
                    ;;
                full|complete)
                    [ -f INTEGRATION_COMPLETE.md ] && file="INTEGRATION_COMPLETE.md"
                    ;;
                repl|replit)
                    [ -f replit.md ] && file="replit.md"
                    ;;
                *)
                    # Try exact match
                    [ -f "$target" ] && file="$target"
                    ;;
            esac
            if [ -z "$file" ]; then
                echo "❌ Could not resolve doc for \"$target\"."
                echo "   Try one of: quick, full, repl, or a filename."
                exit 64
            fi
            echo "📄 Viewing: $file"
            echo "──────────────────────────────────"
            if command -v bat >/dev/null 2>&1; then
                bat "$file"
            else
                sed -n "1,160p" "$file"
                echo ""
                echo "… (end of preview, open in editor for full file)"
            fi
            ;;

        ask)
            # Local smart helper: search using question words as terms
            if [ $# -eq 0 ]; then
                echo "Usage: ./rs docs ask \"How do I …?\""
                exit 64
            fi
            question="$*"
            echo "🤖 RS Docs Helper"
            echo "Question: $question"
            echo ""
            if [ ${#DOC_FILES[@]} -eq 0 ]; then
                echo "No docs available yet, nothing to search."
                exit 0
            fi

            # Extract simple keywords (lowercase, drop tiny words)
            terms=$(
              printf "%s\n" "$question" |
                tr "[:upper:]" "[:lower:]" |
                sed "s/[^a-z0-9 ]/ /g" |
                tr -s " " "\n" |
                grep -Ev "^(the|a|an|and|or|to|of|for|in|on|with|do|i|you|we|it|is|are)$" |
                head -n 5 |
                tr "\n" " "
            )

            if [ -z "$terms" ]; then
                echo "Could not extract useful keywords, falling back to full question search."
                terms="$question"
            fi

            echo "🔍 Keywords: $terms"
            echo "──────────────────────────────────"
            if command -v rg >/dev/null 2>&1; then
                rg -n --hidden --glob '!*.git' --color=always -- $terms "${DOC_FILES[@]}" || true
            else
                GREP_COLORS="mt=1;32" grep -Rni --color=always -- $terms "${DOC_FILES[@]}" || true
            fi
            echo ""
            echo "💡 Tip: refine your question and re-run if you get too many matches."
            ;;

        *)
            echo "Usage:"
            echo "  ./rs docs              # Hub"
            echo "  ./rs docs search TERM  # Search"
            echo "  ./rs docs view quick   # View quickstart"
            echo "  ./rs docs ask QUESTION # Smart search"
            exit 64
            ;;
    esac
}

docs_summary() {
    DOC_INDEX="tools/docs_index.txt"
    DOC_FILES=()
    [ -f QUICKSTART.md ] && DOC_FILES+=("QUICKSTART.md")
    [ -f INTEGRATION_COMPLETE.md ] && DOC_FILES+=("INTEGRATION_COMPLETE.md")
    [ -f replit.md ] && DOC_FILES+=("replit.md")
    if [ -d docs ]; then
        while IFS= read -r f; do
            DOC_FILES+=("$f")
        done < <(find docs -type f -maxdepth 5 \( -name "*.md" -o -name "*.txt" \) | sort)
    fi

    echo "📘 Docs Summary"
    echo "────────────────────────"
    if [ ${#DOC_FILES[@]} -eq 0 ]; then
        echo "• Detected docs : 0"
        echo "• Hint          : Add QUICKSTART.md or docs/*.md"
    else
        echo "• Detected docs : ${#DOC_FILES[@]}"
        for f in "${DOC_FILES[@]}"; do
            printf "   - %s\n" "$f"
        done
    fi

    if [ -f "$DOC_INDEX" ]; then
        ts=$(grep -m1 "^# Detected at:" "$DOC_INDEX" 2>/dev/null | sed "s/^# Detected at:[[:space:]]*//")
        echo "• Index file    : $DOC_INDEX"
        [ -n "$ts" ] && echo "• Index time    : $ts"
    else
        echo "• Index file    : (not generated yet)"
        echo "  ↳ Run: ./rs docs   to regenerate"
    fi
    echo ""
}

docs_snap() {
    # Optional dry run
    DRY_RUN=0
    if [ "${1:-}" = "--dry-run" ]; then
        DRY_RUN=1
        shift || true
    fi

    DOC_FILES=()
    [ -f QUICKSTART.md ] && DOC_FILES+=("QUICKSTART.md")
    [ -f INTEGRATION_COMPLETE.md ] && DOC_FILES+=("INTEGRATION_COMPLETE.md")
    [ -f replit.md ] && DOC_FILES+=("replit.md")
    if [ -d docs ]; then
        while IFS= read -r f; do
            DOC_FILES+=("$f")
        done < <(find docs -type f -maxdepth 5 \( -name "*.md" -o -name "*.txt" \) | sort)
    fi

    mkdir -p snapshots
    ts=$(date -u +"%Y%m%d-%H%M%S")
    SNAP_DIR="snapshots/docs-$ts"
    DOC_INDEX="tools/docs_index.txt"

    echo "📸 Docs snapshot"
    echo "────────────────────────"
    echo "• Target dir : $SNAP_DIR"

    if [ ${#DOC_FILES[@]} -eq 0 ] && [ ! -f "$DOC_INDEX" ]; then
        echo "⚠ No docs or index found, nothing to snapshot."
        return 0
    fi

    if [ "$DRY_RUN" -eq 1 ]; then
        echo "🔎 Dry run only – would copy:"
    else
        mkdir -p "$SNAP_DIR"
    fi

    if [ -f "$DOC_INDEX" ]; then
        echo "   - $DOC_INDEX"
        [ "$DRY_RUN" -eq 0 ] && cp "$DOC_INDEX" "$SNAP_DIR"/
    fi

    for f in "${DOC_FILES[@]}"; do
        echo "   - $f"
        if [ "$DRY_RUN" -eq 0 ]; then
            dest="$SNAP_DIR/$f"
            mkdir -p "$(dirname "$dest")"
            cp "$f" "$dest"
        fi
    done

    if [ "$DRY_RUN" -eq 0 ]; then
        echo ""
        echo "✅ Snapshot created: $SNAP_DIR"
    else
        echo ""
        echo "✅ Dry run complete – no files copied."
    fi
}

diag_all() {
    echo "🩺 RS diag-all"
    echo "=============================="

    echo ""
    echo "1) Core diag (./rs diag)"
    echo "────────────────────────"
    # Call the existing diag handler via re-entry
    "$0" diag || echo "⚠ ./rs diag returned non-zero (see above)."

    echo ""
    echo "2) Docs health"
    echo "────────────────────────"
    docs_summary

    echo "✅ diag-all complete."
    echo "Tip: use ./rs docs search TERM to dig deeper in docs."
}

diag_all_auto() {
    echo "🩺 RS diag-all (with auto snapshot)"
    echo "===================================="

    echo ""
    echo "1) Core diag"
    echo "────────────────────────"
    # Use existing diag_all() if present, otherwise fall back to plain diag
    if command -v diag_all >/dev/null 2>&1; then
        diag_all "$@" || echo "⚠ diag_all() returned non-zero (see above)."
    else
        "$0" diag || echo "⚠ ./rs diag returned non-zero (see above)."
    fi

    echo ""
    echo "2) Docs snapshot"
    echo "────────────────────────"
    if command -v docs_snap >/dev/null 2>&1; then
        docs_snap >/dev/null 2>&1 || echo "⚠ Snapshot failed (see logs)."
        echo "✅ Snapshot written under snapshots/ (see latest docs-*)."
    else
        echo "ℹ docs_snap() not defined, skipping docs snapshot."
    fi

    echo ""
    echo "✅ diag-all complete (core diag + docs snapshot)."
}

metrics_plus() {
    echo "📊 RS metrics-plus"
    echo "=============================="
    echo "Pipeline: health → metrics → docs-snap → optional Git push"
    echo ""

    echo "1) Health check → logs/health.json"
    echo "────────────────────────"
    ./rs health || echo "⚠ ./rs health returned non-zero (continuing)."
    echo ""

    echo "2) Metrics refresh (badges, JSON, etc.)"
    echo "────────────────────────"
    ./rs metrics || echo "⚠ ./rs metrics returned non-zero (continuing)."
    echo ""

    echo "3) Docs snapshot"
    echo "────────────────────────"
    if command -v docs_snap >/dev/null 2>&1; then
        ./rs docs-snap || echo "⚠ ./rs docs-snap returned non-zero (continuing)."
    else
        echo "ℹ docs_snap not available; skipping."
    fi
    echo ""

    echo "4) Optional GitHub commit + push"
    echo "────────────────────────"

    # Prefer explicit CI vars, fall back to your Replit secrets
    GH_PAT_ENV="${GITHUB_PAT:-${GH_PAT:-${github_pat:-}}}"
    REPO_ENV="${GITHUB_REPOSITORY:-${GIT_REMOTE_REPO:-}}"

    if [ -z "$GH_PAT_ENV" ] || [ -z "$REPO_ENV" ]; then
        echo "ℹ No GH token / repo env found; skipping git push."
        echo "   Set GITHUB_PAT + GITHUB_REPOSITORY (or GH_PAT/github_pat + GIT_REMOTE_REPO)."
        echo "✅ metrics-plus finished (no push)."
        return 0
    fi

    # Configure git identity safely
    git config user.name  "${GIT_USER_NAME:-SupersonicBuilder-Bot}" || true
    git config user.email "${GIT_USER_EMAIL:-supersonic-builder@example.invalid}" || true

    # Ensure remote url has token if running in CI (optional)
    if git remote get-url origin >/dev/null 2>&1; then
        ORIGIN_URL="$(git remote get-url origin)"
        case "$ORIGIN_URL" in
          https://github.com/*) : ;; # fine
          https://"$GH_PAT_ENV"@github.com/*) : ;; # already embedded
          *)
            # Do not blindly rewrite if it looks custom
            :
            ;;
        esac
    fi

    # Stage the interesting stuff (ignore errors if some paths missing)
    git add logs/ metrics/ snapshots/ tools/docs_index.txt 2>/dev/null || true

    if git diff --cached --quiet 2>/dev/null; then
        echo "ℹ No changes to commit; skipping push."
        echo "✅ metrics-plus pipeline complete."
        return 0
    fi

    COMMIT_MSG="chore: metrics+docs snapshot $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    git commit -m "$COMMIT_MSG" >/dev/null 2>&1 || {
        echo "⚠ git commit failed (possibly nothing staged)."
    }

    echo "→ Pushing to origin (repo: $REPO_ENV)…"
    if ! GIT_ASKPASS=true git push origin HEAD >/dev/null 2>&1; then
        echo "⚠ Git push failed. Check token scopes / remote URL."
    else
        echo "✅ Git push complete."
    fi

    echo ""
    echo "✅ metrics-plus pipeline finished."
}
