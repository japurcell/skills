#!/usr/bin/env bash

# Tool Guardian Hook
# Blocks dangerous tool operations (destructive file ops, force pushes, DB drops,
# etc.) before Gemini executes them.
#
# Environment variables:
#   GUARD_MODE           - "warn" (log only) or "block" (deny on threats) (default: block)
#   SKIP_TOOL_GUARD      - "true" to disable entirely (default: unset)
#   TOOL_GUARD_LOG_DIR   - Directory for guard logs (default: ~/.gemini/hooks/tool-guardian)
#   TOOL_GUARD_ALLOWLIST - Comma-separated patterns to skip (default: unset)

set -euo pipefail

if [[ "${SKIP_TOOL_GUARD:-}" == "true" ]]; then
  exit 0
fi

INPUT="$(cat)"
MODE="${GUARD_MODE:-block}"
LOG_DIR="${TOOL_GUARD_LOG_DIR:-$HOME/.gemini/hooks/tool-guardian}"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if [[ "$MODE" != "warn" && "$MODE" != "block" ]]; then
  MODE="block"
fi

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/guard.log"

emit_allow_without_jq() {
  printf 'Tool Guardian skipped: required command not found: jq\n' >&2
  printf '%s\n' '{"decision":"allow","systemMessage":"Tool Guardian skipped: required command not found: jq."}'
  exit 0
}

command -v jq >/dev/null 2>&1 || emit_allow_without_jq

emit_response() {
  local decision="$1"
  local reason="${2:-}"
  local system_message="${3:-}"

  jq -nc \
    --arg decision "$decision" \
    --arg reason "$reason" \
    --arg system_message "$system_message" '
      { decision: $decision } +
      (if $reason != "" then { reason: $reason } else {} end) +
      (if $system_message != "" then { systemMessage: $system_message } else {} end)
    '
  exit 0
}

append_log() {
  local event="$1"
  local tool_name="$2"
  local threat_count="${3:-0}"
  local threats_json="${4:-[]}"

  jq -nc \
    --arg timestamp "$TIMESTAMP" \
    --arg event "$event" \
    --arg mode "$MODE" \
    --arg tool "$tool_name" \
    --argjson threat_count "$threat_count" \
    --argjson threats "$threats_json" '
      {
        timestamp: $timestamp,
        event: $event,
        mode: $mode,
        tool: $tool
      } +
      (if $event == "threats_detected" then { threat_count: $threat_count, threats: $threats } else {} end)
    ' >> "$LOG_FILE"
}

build_threats_json() {
  local threat
  local category
  local severity
  local match
  local suggestion
  local threats_json="[]"

  for threat in "${THREATS[@]}"; do
    IFS=$'\t' read -r category severity match suggestion <<< "$threat"
    threats_json="$(
      jq -nc \
        --argjson threats "$threats_json" \
        --arg category "$category" \
        --arg severity "$severity" \
        --arg match "$match" \
        --arg suggestion "$suggestion" '
          $threats + [{
            category: $category,
            severity: $severity,
            match: $match,
            suggestion: $suggestion
          }]
        '
    )"
  done

  printf '%s' "$threats_json"
}

build_block_reason() {
  local threat
  local category
  local severity
  local match
  local suggestion
  local summary=()
  local index=0

  for threat in "${THREATS[@]}"; do
    IFS=$'\t' read -r category severity match suggestion <<< "$threat"
    summary+=("${category}/${severity} matched '${match}'")
    index=$((index + 1))
    if [[ $index -ge 3 ]]; then
      break
    fi
  done

  local joined=""
  local item
  for item in "${summary[@]}"; do
    if [[ -n "$joined" ]]; then
      joined="${joined}; "
    fi
    joined="${joined}${item}"
  done

  printf 'Tool Guardian blocked %s. %s. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional.' \
    "${TOOL_NAME:-tool invocation}" \
    "$joined"
}

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<< "$INPUT"; then
  emit_response "allow" "" "Tool Guardian skipped: invalid hook input JSON."
fi

TOOL_NAME="$(
  jq -r '
    .tool_name //
    .toolName //
    empty |
    if . == null then empty else tostring end
  ' <<< "$INPUT" 2>/dev/null || true
)"
TOOL_INPUT="$(
  jq -rc '
    .tool_input //
    .toolInput //
    .toolArgs //
    empty |
    if . == null then ""
    elif type == "string" then .
    else tojson
    end
  ' <<< "$INPUT" 2>/dev/null || true
)"
COMBINED="${TOOL_NAME} ${TOOL_INPUT}"

ALLOWLIST=()
if [[ -n "${TOOL_GUARD_ALLOWLIST:-}" ]]; then
  IFS=',' read -ra ALLOWLIST <<< "$TOOL_GUARD_ALLOWLIST"
fi

is_allowlisted() {
  local text="$1"
  local pattern

  for pattern in "${ALLOWLIST[@]}"; do
    pattern="$(printf '%s' "$pattern" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$pattern" ]] && continue
    if [[ "$text" == *"$pattern"* ]]; then
      return 0
    fi
  done

  return 1
}

if [[ ${#ALLOWLIST[@]} -gt 0 ]] && is_allowlisted "$COMBINED"; then
  append_log "guard_skipped" "$TOOL_NAME"
  emit_response "allow"
fi

PATTERNS=(
  "destructive_file_ops:::critical:::rm -rf /:::Use targeted 'rm' on specific paths instead of root"
  "destructive_file_ops:::critical:::rm -rf ~:::Use targeted 'rm' on specific paths instead of home directory"
  "destructive_file_ops:::critical:::rm -rf \.:::Use targeted 'rm' on specific files instead of current directory"
  "destructive_file_ops:::critical:::rm -rf \.\.:::Never remove parent directories recursively"
  "destructive_file_ops:::critical:::(rm|del|unlink).*\.env:::Use 'mv' to back up .env files before removing"
  "destructive_file_ops:::critical:::(rm|del|unlink).*\.git([^[:alnum:]_]|$):::Never delete .git directory — use 'git' commands to manage repo state"
  "destructive_git_ops:::critical:::git push --force.*(main|master):::Use 'git push --force-with-lease' or push to a feature branch"
  "destructive_git_ops:::critical:::git push -f.*(main|master):::Use 'git push --force-with-lease' or push to a feature branch"
  "destructive_git_ops:::high:::git reset --hard:::Use 'git stash' to preserve changes, or 'git reset --soft'"
  "destructive_git_ops:::high:::git clean -fd:::Use 'git clean -n' (dry run) first to preview what will be deleted"
  "database_destruction:::critical:::DROP TABLE:::Use 'ALTER TABLE' or create a migration with rollback support"
  "database_destruction:::critical:::DROP DATABASE:::Create a backup first; consider revoking DROP privileges"
  "database_destruction:::critical:::TRUNCATE:::Use 'DELETE FROM ... WHERE' with a condition for safer data removal"
  "database_destruction:::high:::DELETE FROM [a-zA-Z_]+ *;:::Add a WHERE clause to 'DELETE FROM' to avoid deleting all rows"
  "permission_abuse:::high:::chmod -R 777:::Use specific permissions ('chmod -R 755') and limit scope"
  "permission_abuse:::high:::chmod 777:::Use 'chmod 755' for directories or 'chmod 644' for files"
  "network_exfiltration:::critical:::curl.*\|.*bash:::Download script first, review it, then execute"
  "network_exfiltration:::critical:::wget.*\|.*sh:::Download script first, review it, then execute"
  "network_exfiltration:::high:::curl.*--data.*@:::Review what data is being sent before using 'curl --data @file'"
  "system_danger:::high:::sudo :::Avoid 'sudo' — run commands with least privilege needed"
  "system_danger:::high:::npm publish:::Use 'npm publish --dry-run' first to verify package contents"
)

THREATS=()
for entry in "${PATTERNS[@]}"; do
  category="${entry%%:::*}"
  rest="${entry#*:::}"
  severity="${rest%%:::*}"
  rest="${rest#*:::}"
  regex="${rest%%:::*}"
  suggestion="${rest#*:::}"

  if printf '%s\n' "$COMBINED" | grep -qiE "$regex" 2>/dev/null; then
    match="$(printf '%s\n' "$COMBINED" | grep -oiE "$regex" 2>/dev/null | head -1)"
    THREATS+=("${category}"$'\t'"${severity}"$'\t'"${match}"$'\t'"${suggestion}")
  fi
done

THREAT_COUNT="${#THREATS[@]}"

if [[ "$THREAT_COUNT" -eq 0 ]]; then
  append_log "guard_passed" "$TOOL_NAME"
  emit_response "allow"
fi

THREATS_JSON="$(build_threats_json)"
append_log "threats_detected" "$TOOL_NAME" "$THREAT_COUNT" "$THREATS_JSON"

if [[ "$MODE" == "warn" ]]; then
  emit_response "allow" "" "⚠️ Tool Guardian warning: $(build_block_reason)"
fi

emit_response "deny" "$(build_block_reason)" "$(build_block_reason)"
