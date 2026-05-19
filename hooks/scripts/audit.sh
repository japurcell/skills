#!/usr/bin/env bash

# Reusable audit helpers for bash scripts.
# Intended to be sourced:
#   source "/path/to/lib/audit.sh"

rotate_audit_log() {
  local audit_log="${1:?rotate_audit_log: audit_log path is required}"
  local max_bytes="${2:-1048576}"   # default: 1 MiB
  local backups="${3:-3}"           # default: keep 3 rotated files
  local current_size
  local backup

  [[ -f "$audit_log" ]] || return 0

  current_size=$(wc -c < "$audit_log")
  (( current_size < max_bytes )) && return 0

  for ((backup=backups; backup >= 1; backup--)); do
    if [[ -f "$audit_log.$backup" ]]; then
      if (( backup == backups )); then
        rm -f -- "$audit_log.$backup"
      else
        mv -f -- "$audit_log.$backup" "$audit_log.$((backup + 1))"
      fi
    fi
  done

  mv -f -- "$audit_log" "$audit_log.1"
}

append_audit_line() {
  local audit_log="${1:?append_audit_line: audit_log path is required}"
  local line="${2-}"

  printf '%s\n' "$line" >> "$audit_log"
}