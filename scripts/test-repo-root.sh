#!/usr/bin/env bash
# scripts/test-repo-root.sh

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
REPO_ROOT_DIR="$REPO_ROOT"

assert_repo_root_with_common_sh() {
  local common_sh="$1"
  local workdir
  local output
  local git_repo_dir
  local fallback_dir

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' RETURN

  git_repo_dir="$workdir/git-repo"
  fallback_dir="$workdir/fallback"

  mkdir -p "$git_repo_dir/subdir" "$fallback_dir"

  pushd "$git_repo_dir" >/dev/null
  git init >/dev/null
  cd subdir

  cat > test_script.sh <<EOF
source "$common_sh"
echo "REPO_ROOT=\$REPO_ROOT"
EOF

  output=$(bash test_script.sh)
  popd >/dev/null

  if [[ "$output" != "REPO_ROOT=$git_repo_dir" ]]; then
    echo "FAILED: REPO_ROOT should be $git_repo_dir, got $output"
    return 1
  fi
  echo "PASSED: REPO_ROOT correctly identified in git repo"

  pushd "$fallback_dir" >/dev/null

  cat > test_script.sh <<EOF
source "$common_sh"
echo "REPO_ROOT=\$REPO_ROOT"
EOF

  output=$(bash test_script.sh)
  popd >/dev/null

  if [[ "$output" != "REPO_ROOT=$fallback_dir" ]]; then
    echo "FAILED: REPO_ROOT should be $fallback_dir (fallback to pwd), got $output"
    return 1
  fi
  echo "PASSED: REPO_ROOT fallback to pwd works"
}

test_repo_root_with_copilot_and_gemini_common_sh() {
  assert_repo_root_with_common_sh "$REPO_ROOT_DIR/scripts/common.sh"
}

main() {
  local exit_code=0
  test_repo_root_with_copilot_and_gemini_common_sh || exit_code=1
  exit "$exit_code"
}

main "$@"
