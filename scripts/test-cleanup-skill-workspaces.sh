#!/usr/bin/env bash

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SCRIPT_PATH="$REPO_ROOT/scripts/cleanup-skill-workspaces.sh"

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

assert_exists() {
  local path="$1"
  local message="$2"

  if [[ ! -e "$path" ]]; then
    echo "$message" >&2
    exit 1
  fi
}

assert_not_exists() {
  local path="$1"
  local message="$2"

  if [[ -e "$path" ]]; then
    echo "$message" >&2
    exit 1
  fi
}

run_cleanup() {
  local skills_root="$1"
  CLEANUP_SKILLS_ROOT="$skills_root" bash "$SCRIPT_PATH" >/dev/null
}

test_prunes_older_iterations_and_keeps_snapshot() {
  local test_root="$1"
  local skills_root="$test_root/skills"
  local workspace="$skills_root/feature-dev-workspace"

  mkdir -p "$workspace/iteration-old" "$workspace/iteration-new" "$workspace/skill-snapshot"
  sleep 1
  mkdir -p "$workspace/iteration-latest"

  run_cleanup "$skills_root"

  assert_not_exists \
    "$workspace/iteration-old" \
    "Expected older iteration-old directory to be deleted."
  assert_not_exists \
    "$workspace/iteration-new" \
    "Expected older iteration-new directory to be deleted."
  assert_exists \
    "$workspace/iteration-latest" \
    "Expected newest iteration directory to remain."
  assert_exists \
    "$workspace/skill-snapshot" \
    "Expected skill-snapshot directory to remain untouched."
}

test_leaves_workspace_with_single_iteration_unchanged() {
  local test_root="$1"
  local skills_root="$test_root/skills"
  local workspace="$skills_root/tdd-workspace"

  mkdir -p "$workspace/iteration-1" "$workspace/skill-snapshot-v2"

  run_cleanup "$skills_root"

  assert_exists \
    "$workspace/iteration-1" \
    "Expected single iteration directory to remain."
  assert_exists \
    "$workspace/skill-snapshot-v2" \
    "Expected skill-snapshot-v2 directory to remain untouched."
}

test_ignores_non_workspace_directories() {
  local test_root="$1"
  local skills_root="$test_root/skills"
  local non_workspace="$skills_root/regular-skill"

  mkdir -p "$non_workspace/iteration-a" "$non_workspace/iteration-b"

  run_cleanup "$skills_root"

  assert_exists \
    "$non_workspace/iteration-a" \
    "Expected non-workspace directories to be ignored."
  assert_exists \
    "$non_workspace/iteration-b" \
    "Expected non-workspace directories to be ignored."
}

main() {
  local workdir

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' EXIT

  test_prunes_older_iterations_and_keeps_snapshot "$workdir/prune"
  test_leaves_workspace_with_single_iteration_unchanged "$workdir/single"
  test_ignores_non_workspace_directories "$workdir/ignore"
}

main "$@"
