#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT_SH="$REPO_ROOT/.copilot/hooks/scripts/audit.sh"

# shellcheck source=/dev/null
source "$AUDIT_SH"

test_audit_max_bytes_respected() {
  local workdir
  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' RETURN

  local audit_log="$workdir/audit.log"
  echo "initial content" > "$audit_log"

  AUDIT_LOG="$audit_log"
  AUDIT_LOG_MAX_BYTES=1
  audit_init
  audit_log_event "repro_audit_max_bytes.sh" "rotation test"

  if [[ -f "$audit_log.1" ]]; then
    echo "SUCCESS: AUDIT_LOG_MAX_BYTES was respected"
  else
    echo "FAILURE: AUDIT_LOG_MAX_BYTES was NOT respected"
    exit 1
  fi
}

test_audit_max_bytes_respected
