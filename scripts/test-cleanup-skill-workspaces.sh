#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
readonly SCRIPT_PATH="$REPO_ROOT/scripts/cleanup-skill-workspaces.sh"

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

copy_cleanup_cli() {
  local repo_root="$1"
  mkdir -p "$repo_root/scripts"
  cp "$SCRIPT_PATH" "$repo_root/scripts/cleanup-skill-workspaces.sh"
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

test_prunes_category_workspace_with_literal_name() {
  local test_root="$1"
  local skills_root="$test_root/skills"
  local workspace="$skills_root/default/feature [draft]-workspace"

  mkdir -p "$workspace/iteration-old" "$workspace/skill-snapshot"
  sleep 1
  mkdir -p "$workspace/iteration-new"

  run_cleanup "$skills_root"

  assert_not_exists \
    "$workspace/iteration-old" \
    "Expected older category workspace iteration to be deleted."
  assert_exists \
    "$workspace/iteration-new" \
    "Expected newest category workspace iteration to remain."
  assert_exists \
    "$workspace/skill-snapshot" \
    "Expected category workspace snapshot to remain untouched."
}

test_default_roots_cover_categories_and_local_siblings_safely() {
  local test_root="$1"
  local repo_root="$test_root/repo"
  local skills_root="$repo_root/skills"
  local category_workspace="$skills_root/default/literal [default]-workspace"
  local local_workspace="$repo_root/.agents/skills/okf-authoring-workspace"
  local nested_workspace="$skills_root/default/owner/evals/files/run-workspace"
  local archived_workspace="$skills_root/archive/old-workspace"
  local nested_archive_workspace="$skills_root/default/archive/old-workspace"
  local outside_workspace="$test_root/outside-workspace"
  local outside_category="$test_root/outside-category"

  copy_cleanup_cli "$repo_root"
  mkdir -p \
    "$category_workspace/iteration-old" \
    "$local_workspace/iteration-old" \
    "$nested_workspace/iteration-old" \
    "$archived_workspace/iteration-old" \
    "$nested_archive_workspace/iteration-old" \
    "$outside_workspace/iteration-old" \
    "$outside_category/nested-workspace/iteration-old"
  sleep 1
  mkdir -p \
    "$category_workspace/iteration-new" \
    "$local_workspace/iteration-new" \
    "$nested_workspace/iteration-new" \
    "$archived_workspace/iteration-new" \
    "$nested_archive_workspace/iteration-new" \
    "$outside_workspace/iteration-new" \
    "$outside_category/nested-workspace/iteration-new"
  mkdir -p "$category_workspace/skill-snapshot" "$local_workspace/skill-snapshot"
  ln -s "$outside_workspace" "$skills_root/default/linked-workspace"
  ln -s "$outside_category" "$skills_root/linked-category"

  env -u CLEANUP_SKILLS_ROOT bash "$repo_root/scripts/cleanup-skill-workspaces.sh" >/dev/null

  assert_not_exists "$category_workspace/iteration-old" \
    "Expected the default category workspace to be pruned."
  assert_exists "$category_workspace/iteration-new" \
    "Expected the newest default category iteration to remain."
  assert_exists "$category_workspace/skill-snapshot" \
    "Expected the default category snapshot to remain untouched."
  assert_not_exists "$local_workspace/iteration-old" \
    "Expected the repo-local workspace to be pruned."
  assert_exists "$local_workspace/iteration-new" \
    "Expected the newest repo-local iteration to remain."
  assert_exists "$local_workspace/skill-snapshot" \
    "Expected the repo-local snapshot to remain untouched."
  assert_exists "$nested_workspace/iteration-old" \
    "Expected run fixtures inside skills not to be traversed."
  assert_exists "$archived_workspace/iteration-old" \
    "Expected archived workspace data to remain untouched."
  assert_exists "$nested_archive_workspace/iteration-old" \
    "Expected category archive data to remain untouched."
  assert_exists "$outside_workspace/iteration-old" \
    "Expected linked workspace targets not to be followed."
  assert_exists "$outside_category/nested-workspace/iteration-old" \
    "Expected linked category targets not to be followed."
}

test_configured_root_is_bounded_and_isolated() {
  local test_root="$1"
  local repo_root="$test_root/repo"
  local configured_root="$repo_root/custom-root"
  local direct_workspace="$configured_root/direct-workspace"
  local category_workspace="$configured_root/default/category-workspace"
  local nested_workspace="$configured_root/default/owner/nested-workspace"
  local repo_workspace="$repo_root/skills/default/repository-workspace"
  local local_workspace="$repo_root/.agents/skills/local-workspace"

  copy_cleanup_cli "$repo_root"
  mkdir -p \
    "$direct_workspace/iteration-old" \
    "$category_workspace/iteration-old" \
    "$nested_workspace/iteration-old" \
    "$repo_workspace/iteration-old" \
    "$local_workspace/iteration-old"
  sleep 1
  mkdir -p \
    "$direct_workspace/iteration-new" \
    "$category_workspace/iteration-new" \
    "$nested_workspace/iteration-new" \
    "$repo_workspace/iteration-new" \
    "$local_workspace/iteration-new"

  CLEANUP_SKILLS_ROOT="$configured_root" \
    bash "$repo_root/scripts/cleanup-skill-workspaces.sh" >/dev/null

  if CLEANUP_SKILLS_ROOT="" \
    bash "$repo_root/scripts/cleanup-skill-workspaces.sh" >/dev/null 2>&1; then
    echo "Expected an explicitly empty configured root to fail closed." >&2
    exit 1
  fi

  assert_not_exists "$direct_workspace/iteration-old" \
    "Expected a configured root's immediate workspace to be pruned."
  assert_not_exists "$category_workspace/iteration-old" \
    "Expected a configured root's category workspace to be pruned."
  assert_exists "$nested_workspace/iteration-old" \
    "Expected configured-root traversal to stop after one category level."
  assert_exists "$repo_workspace/iteration-old" \
    "Expected configured-root cleanup not to touch repository workspaces."
  assert_exists "$local_workspace/iteration-old" \
    "Expected configured-root cleanup not to touch local workspaces."
}

main() {
  local workdir

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' EXIT

  test_prunes_older_iterations_and_keeps_snapshot "$workdir/prune"
  test_leaves_workspace_with_single_iteration_unchanged "$workdir/single"
  test_ignores_non_workspace_directories "$workdir/ignore"
  test_prunes_category_workspace_with_literal_name "$workdir/category"
  test_default_roots_cover_categories_and_local_siblings_safely "$workdir/default"
  test_configured_root_is_bounded_and_isolated "$workdir/configured"
}

main "$@"
