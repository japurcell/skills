#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd git
require_cmd grep
require_cmd jq
require_cmd mktemp
require_cmd sed
require_cmd sort

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }

MODE="${SCAN_MODE:-warn}"
SCOPE="${SCAN_SCOPE:-diff}"

if [[ "$MODE" != "warn" && "$MODE" != "block" ]]; then
  MODE="warn"
fi

if [[ "$SCOPE" != "diff" && "$SCOPE" != "staged" ]]; then
  SCOPE="diff"
fi

AUDIT_LOG="${SECRETS_LOG_DIR:-$HOME/.copilot/hooks/secrets/scan.log}"
AUDIT_LOCK="$AUDIT_LOG.lock"
audit_init

PATTERNS=(
  "github_classic_pat|high|gh[pousr]_[A-Za-z0-9]{36}"
  "github_fine_grained_pat|high|github_pat_[A-Za-z0-9_]{20,}"
  "aws_access_key|high|AKIA[0-9A-Z]{16}"
  "stripe_live_key|high|sk_live_[0-9A-Za-z]{16,}"
  "slack_token|medium|xox[baprs]-[0-9A-Za-z-]{10,}"
)
ENV_FILES_SCANNED=()

ALLOWLIST=()
parse_allowlist_csv "${SECRETS_ALLOWLIST:-}" ALLOWLIST

append_scan_log() {
  local status="$1"
  local findings_json="${2:-[]}"
  local note="${3:-}"
  local timestamp="${TIMESTAMP:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"
  local env_files_json
  local log_payload

  env_files_json="$(build_string_array_json "${ENV_FILES_SCANNED[@]}")"

  log_payload="$(
    jq -nc \
      --arg timestamp "$timestamp" \
      --arg session_id "${SESSION_ID:-}" \
      --arg repo_root "$REPO_ROOT" \
      --arg mode "$MODE" \
      --arg scope "$SCOPE" \
      --arg status "$status" \
      --arg note "$note" \
      --argjson findings "$findings_json" \
      --argjson env_files "$env_files_json" '
        {
          timestamp: $timestamp,
          sessionId: $session_id,
          repoRoot: $repo_root,
          mode: $mode,
          scope: $scope,
          status: $status
        } +
        (if $note != "" then { note: $note } else {} end) +
        (if ($env_files | length) > 0 then { envFiles: $env_files } else {} end) +
        (if ($findings | length) > 0 then { findings: $findings } else {} end)
      '
  )"

  audit_log_event "$(basename "$0")" "$log_payload"
}

build_string_array_json() {
  jq -nc '$ARGS.positional' --args "$@"
}

collect_files() {
  if [[ "$SCOPE" == "staged" ]]; then
    git diff --cached --name-only --diff-filter=ACMRTUXB --
    return
  fi

  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    git diff --name-only --diff-filter=ACMRTUXB HEAD --
  else
    git diff --name-only --diff-filter=ACMRTUXB --
    git diff --cached --name-only --diff-filter=ACMRTUXB --
  fi

  git ls-files --others --exclude-standard
}

materialize_candidate() {
  local path="$1"
  local temp_file="$2"

  if [[ "$SCOPE" == "staged" ]]; then
    git show ":$path" > "$temp_file" 2>/dev/null
    return
  fi

  [[ -f "$path" ]]
  cat -- "$path" > "$temp_file"
}

is_untracked_file() {
  local path="$1"
  git ls-files --others --exclude-standard -- "$path" | grep -Fxq "$path"
}

is_env_path() {
  local lower_path="${1,,}"
  [[ "$lower_path" =~ (^|/)\.env($|[.]) ]]
}

is_credential_path() {
  local lower_path="${1,,}"
  local base_name="${lower_path##*/}"

  case "$base_name" in
    credentials|credentials.*|.git-credentials)
      return 0
      ;;
  esac

  [[ "$lower_path" =~ (^|/)\.ssh(/|$) ]] ||
    [[ "$lower_path" =~ (^|/)\.aws(/|$) ]] ||
    [[ "$lower_path" =~ (^|/)\.gnupg(/|$) ]] ||
    [[ "$lower_path" =~ (^|/)\.?credentials(/|$) ]] ||
    [[ "$lower_path" =~ (^|/)\.?secrets(/|$) ]]
}

is_text_candidate() {
  local path="$1"
  local temp_file="$2"
  local mime_type=""

  if command -v file >/dev/null 2>&1; then
    mime_type="$(file --brief --mime-type -- "$temp_file" 2>/dev/null || true)"
    case "$mime_type" in
      text/*|application/json|application/javascript|application/xml|application/x-empty|inode/x-empty)
        return 0
        ;;
    esac
  fi

  [[ "$path" =~ \.(c|cc|cfg|conf|cpp|cs|css|csv|env|go|h|html|ini|java|js|json|jsx|kt|md|php|py|rb|rs|sh|sql|svg|tf|toml|ts|tsx|txt|xml|yaml|yml)$ ]]
}

emit_numbered_file_lines() {
  local source_file="$1"
  awk '{ printf "%d\t%s\n", NR, $0 }' "$source_file"
}

emit_diff_added_lines() {
  local path="$1"

  git diff --no-ext-diff --unified=0 HEAD -- "$path" | awk '
    /^\+\+\+/ { next }
    /^@@/ {
      split($3, span, ",")
      sub(/^\+/, "", span[1])
      line = span[1]
      next
    }
    /^\+/ {
      print line "\t" substr($0, 2)
      line++
      next
    }
  '
}

emit_candidate_lines() {
  local path="$1"
  local temp_file="$2"

  if [[ "$SCOPE" == "staged" ]]; then
    emit_numbered_file_lines "$temp_file"
    return
  fi

  if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    emit_numbered_file_lines "$temp_file"
    return
  fi

  if is_untracked_file "$path"; then
    emit_numbered_file_lines "$temp_file"
    return
  fi

  emit_diff_added_lines "$path"
}

redact_match() {
  local match="$1"
  local length="${#match}"

  if (( length <= 8 )); then
    printf '[REDACTED]'
    return
  fi

  printf '%s...%s' "${match:0:4}" "${match: -4}"
}

build_findings_json() {
  local findings_json='[]'
  local finding
  local pattern_name
  local severity
  local path
  local line_number
  local redacted

  for finding in "${FINDINGS[@]}"; do
    IFS=$'\t' read -r pattern_name severity path line_number redacted <<< "$finding"
    findings_json="$(
      jq -nc \
        --argjson findings "$findings_json" \
        --arg pattern_name "$pattern_name" \
        --arg severity "$severity" \
        --arg path "$path" \
        --arg line_number "$line_number" \
        --arg redacted "$redacted" '
          $findings + [{
            pattern: $pattern_name,
            severity: $severity,
            path: $path,
            line: ($line_number | tonumber),
            redactedMatch: $redacted
          }]
        '
    )"
  done

  printf '%s' "$findings_json"
}

print_findings() {
  local finding
  local pattern_name
  local severity
  local path
  local line_number
  local redacted

  printf 'Potential secrets detected in modified files:\n'
  for finding in "${FINDINGS[@]}"; do
    IFS=$'\t' read -r pattern_name severity path line_number redacted <<< "$finding"
    printf ' - %s:%s [%s] %s %s\n' "$path" "$line_number" "$severity" "$pattern_name" "$redacted"
  done
  printf 'Set SECRETS_ALLOWLIST to suppress intentional matches.\n'
}

if [[ "${SKIP_SECRETS_SCAN:-}" == "true" ]]; then
  append_scan_log "skipped" "[]" "scan disabled by SKIP_SECRETS_SCAN"
  exit 0
fi

if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  append_scan_log "skipped" "[]" "not inside git repository"
  printf 'Not in git repository. Skipping secrets scan.\n'
  exit 0
fi

cd "$REPO_ROOT"

mapfile -t FILES < <(collect_files | sed '/^$/d' | sort -u)

if [[ "${#FILES[@]}" -eq 0 ]]; then
  append_scan_log "clean" "[]" "no modified files to scan"
  printf 'No modified files to scan.\n'
  exit 0
fi

FINDINGS=()
for path in "${FILES[@]}"; do
  temp_file="$(mktemp)"
  if ! materialize_candidate "$path" "$temp_file"; then
    rm -f "$temp_file"
    continue
  fi

  if is_env_path "$path"; then
    ENV_FILES_SCANNED+=("$path")
  fi

  if ! is_text_candidate "$path" "$temp_file"; then
    rm -f "$temp_file"
    continue
  fi

  if is_credential_path "$path"; then
    allowlist_text="${path}:1:credential_path:[SENSITIVE PATH]"
    if ! allowlist_contains "$allowlist_text" "${ALLOWLIST[@]}"; then
      FINDINGS+=("credential_path"$'\t'"critical"$'\t'"${path}"$'\t'"1"$'\t'"[SENSITIVE PATH]")
    fi
  fi

  while IFS=$'\t' read -r line_number line_text; do
    [[ -n "$line_number" ]] || continue

    for entry in "${PATTERNS[@]}"; do
      IFS='|' read -r pattern_name severity regex <<< "$entry"
      while IFS= read -r match_value; do
        allowlist_text="${path}:${line_number}:${pattern_name}:${match_value}"
        if allowlist_contains "$allowlist_text" "${ALLOWLIST[@]}"; then
          continue
        fi
        FINDINGS+=("${pattern_name}"$'\t'"${severity}"$'\t'"${path}"$'\t'"${line_number}"$'\t'"$(redact_match "$match_value")")
      done < <(printf '%s\n' "$line_text" | grep -Eo "$regex" || true)
    done
  done < <(emit_candidate_lines "$path" "$temp_file")

  rm -f "$temp_file"
done

if [[ "${#FINDINGS[@]}" -eq 0 ]]; then
  append_scan_log "clean"
  printf 'Secrets scan clean.\n'
  exit 0
fi

findings_json="$(build_findings_json)"
append_scan_log "findings" "$findings_json"
print_findings

if [[ "$MODE" == "block" ]]; then
  exit 1
fi

exit 0
