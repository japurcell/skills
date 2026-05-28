#!/usr/bin/env bash
# scripts/test-repo-root.sh

set -euo pipefail

REPO_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_SH="$REPO_ROOT_DIR/.copilot/hooks/scripts/common.sh"

test_repo_root_in_git_repo() {
  local tmp_repo
  tmp_repo="$(mktemp -d)"
  trap 'rm -rf "$tmp_repo"' RETURN

  pushd "$tmp_repo" >/dev/null
  git init >/dev/null
  mkdir -p subdir
  cd subdir

  cat > test_script.sh <<EOF
source "$COMMON_SH"
echo "REPO_ROOT=\$REPO_ROOT"
EOF
  
  local output
  output=$(bash test_script.sh)
  popd >/dev/null

  if [[ "$output" != "REPO_ROOT=$tmp_repo" ]]; then
    echo "FAILED: REPO_ROOT should be $tmp_repo, got $output"
    return 1
  fi
  echo "PASSED: REPO_ROOT correctly identified in git repo"
}

test_repo_root_fallback_to_pwd() {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' RETURN

  pushd "$tmp_dir" >/dev/null
  # Not a git repo

  cat > test_script.sh <<EOF
source "$COMMON_SH"
echo "REPO_ROOT=\$REPO_ROOT"
EOF

  local output
  output=$(bash test_script.sh)
  popd >/dev/null

  if [[ "$output" != "REPO_ROOT=$tmp_dir" ]]; then
    echo "FAILED: REPO_ROOT should be $tmp_dir (fallback to pwd), got $output"
    return 1
  fi
  echo "PASSED: REPO_ROOT fallback to pwd works"
}

main() {
  local exit_code=0
  test_repo_root_in_git_repo || exit_code=1
  test_repo_root_fallback_to_pwd || exit_code=1
  exit "$exit_code"
}

main "$@"
