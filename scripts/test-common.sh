#!/usr/bin/env bash

# Common test helpers for scripts/test-*.sh

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

assert_equals() {
  local expected="$1"
  local actual="$2"
  local message="$3"

  if [[ "$actual" != "$expected" ]]; then
    echo "$message" >&2
    echo "Expected: $expected" >&2
    echo "Actual:   $actual" >&2
    exit 1
  fi
}

assert_file_contains() {
  local file="$1"
  local needle="$2"
  local message="$3"

  if ! grep -Fq "$needle" "$file"; then
    echo "$message" >&2
    echo "Missing: $needle" >&2
    echo "File: $file" >&2
    if [[ -f "$file" ]]; then
      echo "--- File Content ---" >&2
      cat "$file" >&2
      echo "--- End Content ---" >&2
    fi
    exit 1
  fi
}

setup_test_workdir() {
  local workdir
  workdir="$(mktemp -d)"
  echo "$workdir"
}

# Usage: mock_bin <workdir> <command_name> <script_content>
# Example: mock_bin "$workdir" "dotnet" '#!/bin/env bash\nexit 0'
mock_bin() {
  local workdir="$1"
  local cmd_name="$2"
  local content="$3"
  local bin_dir="$workdir/bin"

  mkdir -p "$bin_dir"
  printf "%b\n" "$content" > "$bin_dir/$cmd_name"
  chmod +x "$bin_dir/$cmd_name"
}

# Temporarily prepend <workdir>/bin to PATH while running a command.
# Usage: with_mock_bin_path <workdir> <command> [args...]
with_mock_bin_path() {
  local workdir="$1"
  shift

  local old_path="$PATH"
  local status

  PATH="$workdir/bin:$PATH"
  if "$@"; then
    status=0
  else
    status=$?
  fi
  PATH="$old_path"

  return "$status"
}

# Run a Copilot hook script with standard environment variables
# Usage: run_copilot_hook <hook_script_name> <audit_log> <payload> [copilot_home] [extra_env_vars...]
run_copilot_hook() {
  local hook_name="$1"; shift
  local audit_log="$1"; shift
  local payload="$1"; shift
  local copilot_home="${1:-}"; shift

  # The rest of arguments are extra env vars in KEY=VALUE format
  local env_cmd=("AUDIT_LOG=$audit_log")
  if [[ -n "$copilot_home" ]]; then
    env_cmd+=("COPILOT_HOME=$copilot_home")
  fi

  while [[ $# -gt 0 ]]; do
    env_cmd+=("$1")
    shift
  done

  # Execute the hook
  env "${env_cmd[@]}" bash "$REPO_ROOT/.copilot/hooks/scripts/$hook_name" <<<"$payload"
}
