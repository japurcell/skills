#!/usr/bin/env bash

# Reusable audit helpers for bash scripts.
# Intended to be sourced:
#   source "/path/to/lib/audit.sh"

# Ensures dependencies and log directory exist
audit_init() {
  for cmd in jq flock; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Error: $cmd not found" >&2; exit 1; }
  done
  mkdir -p "$(dirname "${AUDIT_LOG:-$HOME/.copilot/hooks/audit.log}")"
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

audit_log_event() {
  local sender="$1"
  local message="$2"
  local log="${AUDIT_LOG:-$HOME/.copilot/hooks/audit.log}"
  local lock="${AUDIT_LOCK:-$log.lock}"

  (
    flock -x 9
    rotate_audit_log "$log"
    append_audit_line "$log" "$sender" "$message"
  ) 9>"$lock"
}