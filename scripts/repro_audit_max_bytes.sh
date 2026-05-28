#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_SH="$REPO_ROOT/.copilot/hooks/scripts/common.sh"

# Mock audit.sh to see what it receives
AUDIT_SH="$REPO_ROOT/.copilot/hooks/scripts/audit.sh"

test_audit_max_bytes_ignored() {
  local workdir
  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' RETURN

  local audit_log="$workdir/audit.log"
  echo "initial content" > "$audit_log"

  # Mock audit.sh
  cat > "$workdir/audit_mock.sh" <<EOF
rotate_audit_log() {
  echo "MAX_BYTES_RECEIVED: \$2"
}
append_audit_line() { :; }
EOF

  cat > "$workdir/test_script.sh" <<EOF
# Create a modified common.sh that uses our mock
sed "s|AUDIT_LIB=.*|AUDIT_LIB=\"$workdir/audit_mock.sh\"|" "$COMMON_SH" > "$workdir/common_mod.sh"
source "$workdir/common_mod.sh"
AUDIT_LOG="$audit_log" AUDIT_LOG_MAX_BYTES=1234 setup_audit_log
EOF

  local output
  output=$(bash "$workdir/test_script.sh")
  
  echo "Output: $output"
  if [[ "$output" == *"MAX_BYTES_RECEIVED: 1234"* ]]; then
    echo "SUCCESS: AUDIT_LOG_MAX_BYTES was respected"
  else
    echo "FAILURE: AUDIT_LOG_MAX_BYTES was NOT respected"
    exit 1
  fi
}

test_audit_max_bytes_ignored
