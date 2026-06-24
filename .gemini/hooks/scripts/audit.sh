#!/usr/bin/env bash

# Reusable audit helpers for Gemini hooks.
# Must preserve $HOME/.gemini/ paths.

# Ensures dependencies and log directory exist
audit_init() {
  for cmd in jq flock; do
    # Return instead of exiting so the calling hook can emit JSON-safe fallback
    # responses when a dependency or init step is unavailable.
    command -v "$cmd" >/dev/null 2>&1 || { echo "Error: $cmd not found" >&2; return 1; }
  done
  local log="${AUDIT_LOG:-$HOME/.gemini/hooks/audit.log}"
  local mode="${GEMINI_PASSIVE_LOG_MODE:-default}"
  mkdir -p "$(dirname "$log")"
  if [[ "$mode" == "shadow" ]]; then
    mkdir -p "$(dirname "${GEMINI_PASSIVE_SHADOW_LOG:-$log.shadow}")"
  fi
}

# Rotates audit log if it exceeds size limit (default 1 MiB, 3 backups)
rotate_audit_log() {
  local log="${1:?log path required}"
  local max="${2:-1048576}"
  local backups="${3:-3}"
  
  [[ -f "$log" ]] && (( $(wc -c < "$log") >= max )) || return 0

  for ((i=backups; i>0; i--)); do
    [[ -f "$log.$i" ]] && { 
      if (( i == backups )); then rm -f "$log.$i"
      else mv -f "$log.$i" "$log.$((i+1))"
      fi
    }
  done
  mv -f "$log" "$log.1"
}

# Appends a line to the audit log with a sender tag
append_audit_line() {
  local log="${1:?log path required}"
  local sender="${2:?sender required}"
  local line="${3-}"
  printf '[%s] %s\n' "$sender" "$line" | tee -a "$log" >&2
}

# Helper to log with automatic locking and rotation
audit_log_event() {
  local sender="$1"
  local message="$2"
  local log="${AUDIT_LOG:-$HOME/.gemini/hooks/audit.log}"
  local lock="${AUDIT_LOCK:-$log.lock}"
  local max_bytes="${AUDIT_LOG_MAX_BYTES:-1048576}"
  local backups="${AUDIT_LOG_MAX_BACKUPS:-3}"

  (
    flock -x 9
    rotate_audit_log "$log" "$max_bytes" "$backups"
    append_audit_line "$log" "$sender" "$message"
  ) 9>"$lock"
}

audit_log_passive_event() {
  local sender="$1"
  local message="$2"
  local log="${AUDIT_LOG:-$HOME/.gemini/hooks/audit.log}"
  local mode="${GEMINI_PASSIVE_LOG_MODE:-default}"
  local shadow_log="${GEMINI_PASSIVE_SHADOW_LOG:-$log.shadow}"
  local lock="${AUDIT_LOCK:-$log.lock}"
  local max_bytes="${AUDIT_LOG_MAX_BYTES:-1048576}"
  local backups="${AUDIT_LOG_MAX_BACKUPS:-3}"

  (
    flock -x 9
    rotate_audit_log "$log" "$max_bytes" "$backups"
    append_audit_line "$log" "$sender" "$message"
    if [[ "$mode" == "shadow" ]]; then
      rotate_audit_log "$shadow_log" "$max_bytes" "$backups"
      append_audit_line "$shadow_log" "$sender" "$message"
    fi
  ) 9>"$lock"
}
