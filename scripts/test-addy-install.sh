#!/usr/bin/env bash

set -euo pipefail

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

commit_repo() {
  local repo="$1"
  local message="$2"

  git -C "$repo" add .
  git -C "$repo" commit -q -m "$message"
}

init_addy_remote_repo() {
  local repo="$1"
  local skill_body="$2"

  mkdir -p "$repo/agents" "$repo/skills/alpha" "$repo/references"

  git -C "$repo" init -q -b main
  git -C "$repo" config user.name "Test User"
  git -C "$repo" config user.email "test@example.com"

  printf '%s\n' '---' 'name: helper' '---' 'Use alpha.' > "$repo/agents/helper.md"
  printf '%s\n' '---' 'name: alpha' '---' "$skill_body" > "$repo/skills/alpha/SKILL.md"
  printf '%s\n' 'Reference.' > "$repo/references/testing.md"

  commit_repo "$repo" "Initial addy repo"
}

test_copies_referenced_skills_transitively() {
  local workdir="$1"
  local installed_skills

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/references" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/skills/beta" \
    "$workdir/src/skills/gamma" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references"

  printf '%s\n' '---' 'name: helper' '---' 'Use alpha and beta.' > "$workdir/src/agents/helper.md"
  printf '%s\n' '---' 'name: alpha' '---' 'Use beta for follow-up work.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' '---' 'name: beta' '---' 'Use gamma for deeper work.' > "$workdir/src/skills/beta/SKILL.md"
  printf '%s\n' '---' 'name: gamma' '---' 'Standalone.' > "$workdir/src/skills/gamma/SKILL.md"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  installed_skills="$(
    find "$workdir/dest/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | paste -sd ',' -
  )"

  assert_equals \
    "addy-alpha,addy-beta,addy-gamma" \
    "$installed_skills" \
    "Expected referenced skills to be copied transitively alongside explicitly selected skills."
}

test_copies_referenced_skills_without_agents() {
  local workdir="$1"
  local installed_skills

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/references" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/skills/beta" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references"

  printf '%s\n' '---' 'name: alpha' '---' 'Use beta for follow-up work.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' '---' 'name: beta' '---' 'Standalone.' > "$workdir/src/skills/beta/SKILL.md"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  installed_skills="$(
    find "$workdir/dest/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | paste -sd ',' -
  )"

  assert_equals \
    "addy-alpha,addy-beta" \
    "$installed_skills" \
    "Expected dependency copying to work even when no agent files exist."
}

test_copies_skills_selected_from_file() {
  local workdir="$1"
  local installed_skills

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/references" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/skills/beta" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references"

  printf '%s\n' '---' 'name: alpha' '---' 'Use beta for follow-up work.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' '---' 'name: beta' '---' 'Standalone.' > "$workdir/src/skills/beta/SKILL.md"
  printf '%s\n' 'alpha' > "$workdir/skills.txt"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills-file "$workdir/skills.txt" >/dev/null

  installed_skills="$(
    find "$workdir/dest/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | paste -sd ',' -
  )"

  assert_equals \
    "addy-alpha,addy-beta" \
    "$installed_skills" \
    "Expected --skills-file to install listed skills and their referenced dependencies."
}

test_writes_skills_state_file_for_current_install() {
  local workdir="$1"
  local installed_skills_file="$workdir/installed-skills.txt"
  local installed_skills

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/references" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/skills/beta" \
    "$workdir/src/skills/gamma" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references"

  printf '%s\n' '---' 'name: alpha' '---' 'Use beta for follow-up work.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' '---' 'name: beta' '---' 'Standalone.' > "$workdir/src/skills/beta/SKILL.md"
  printf '%s\n' '---' 'name: gamma' '---' 'Standalone.' > "$workdir/src/skills/gamma/SKILL.md"
  printf '%s\n' 'gamma' > "$installed_skills_file"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_SKILLS_STATE_FILE="$installed_skills_file" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  installed_skills="$(<"$installed_skills_file")"

  assert_equals \
    $'alpha\nbeta' \
    "$installed_skills" \
    "Expected the installer to update the skills state file to match the current installed source skills."
}

test_copies_root_references_directory() {
  local workdir="$1"
  local copied_reference
  local stale_reference_exists

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/references" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references"

  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' 'Testing patterns go here.' > "$workdir/src/references/testing-patterns.md"
  printf '%s\n' 'stale' > "$workdir/dest/references/stale.md"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  copied_reference="$(<"$workdir/dest/references/testing-patterns.md")"
  stale_reference_exists="no"
  [[ -e "$workdir/dest/references/stale.md" ]] && stale_reference_exists="yes"

  assert_equals \
    "Testing patterns go here." \
    "$copied_reference" \
    "Expected top-level references to be copied into the destination repository."

  assert_equals \
    "no" \
    "$stale_reference_exists" \
    "Expected destination references to mirror the source references directory."
}

test_rewrites_root_reference_links_for_copied_skills() {
  local workdir="$1"
  local copied_skill

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/references" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references"

  printf '%s\n' \
    '---' \
    'name: alpha' \
    '---' \
    'See `references/accessibility-checklist.md` for the full checklist.' \
    > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' 'Accessibility checklist.' > "$workdir/src/references/accessibility-checklist.md"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  copied_skill="$(<"$workdir/dest/skills/addy-alpha/SKILL.md")"

  assert_equals \
    $'---\nname: addy-alpha\n---\nSee `../../references/accessibility-checklist.md` for the full checklist.' \
    "$copied_skill" \
    "Expected copied skill reference links to point to the repository references directory."
}

test_clones_addy_repo_before_copying() {
  local workdir="$1"
  local cloned_skill

  mkdir -p "$workdir/remote" "$workdir/repo-root"
  init_addy_remote_repo "$workdir/remote" "Fresh from clone."

  ADDY_REPO_ROOT="$workdir/repo-root" \
    ADDY_REMOTE_URL="$workdir/remote" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  cloned_skill="$(<"$workdir/repo-root/skills/addy-alpha/SKILL.md")"

  assert_equals \
    $'---\nname: addy-alpha\n---\nFresh from clone.' \
    "$cloned_skill" \
    "Expected the installer to clone the addy repository before copying skills."
}

test_pulls_latest_addy_repo_before_copying() {
  local workdir="$1"
  local copied_skill

  mkdir -p "$workdir/remote" "$workdir/repo-root"
  init_addy_remote_repo "$workdir/remote" "Stale version."
  git clone -q "$workdir/remote" "$workdir/addy-agent-skills"

  printf '%s\n' '---' 'name: alpha' '---' 'Latest version.' > "$workdir/remote/skills/alpha/SKILL.md"
  commit_repo "$workdir/remote" "Update alpha skill"

  ADDY_REPO_ROOT="$workdir/repo-root" \
    ADDY_REMOTE_URL="$workdir/remote" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  copied_skill="$(<"$workdir/repo-root/skills/addy-alpha/SKILL.md")"

  assert_equals \
    $'---\nname: addy-alpha\n---\nLatest version.' \
    "$copied_skill" \
    "Expected the installer to pull the latest addy repository changes before copying skills."
}

test_copies_hooks_directory() {
  local workdir="$1"
  local copied_hook

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/references" \
    "$workdir/src/hooks" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references" \
    "$workdir/dest/hooks"

  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' '#!/bin/bash' 'echo "New hook"' > "$workdir/src/hooks/new-hook.sh"
  chmod +x "$workdir/src/hooks/new-hook.sh"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_HOOKS_SRC="$workdir/src/hooks" \
    ADDY_HOOKS_DEST="$workdir/dest/hooks" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  copied_hook="$(<"$workdir/dest/hooks/new-hook.sh")"

  assert_equals \
    $'#!/bin/bash\necho "New hook"' \
    "$copied_hook" \
    "Expected hooks to be copied from source to destination."
}

test_preserves_existing_hooks_files() {
  local workdir="$1"
  local existing_content

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/references" \
    "$workdir/src/hooks" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references" \
    "$workdir/dest/hooks"

  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$workdir/src/skills/alpha/SKILL.md"
  printf '%s\n' '#!/bin/bash' 'echo "Source hook"' > "$workdir/src/hooks/source-hook.sh"
  printf '%s\n' '#!/bin/bash' 'echo "Existing hook"' > "$workdir/dest/hooks/existing-hook.sh"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_HOOKS_SRC="$workdir/src/hooks" \
    ADDY_HOOKS_DEST="$workdir/dest/hooks" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  existing_content="$(<"$workdir/dest/hooks/existing-hook.sh")"

  assert_equals \
    $'#!/bin/bash\necho "Existing hook"' \
    "$existing_content" \
    "Expected existing hook files in destination to be preserved during copy."
}

test_handles_missing_hooks_dir_gracefully() {
  local workdir="$1"

  mkdir -p \
    "$workdir/src/agents" \
    "$workdir/src/skills/alpha" \
    "$workdir/src/references" \
    "$workdir/dest/agents" \
    "$workdir/dest/skills" \
    "$workdir/dest/references" \
    "$workdir/dest/hooks"

  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$workdir/src/skills/alpha/SKILL.md"

  ADDY_AGENTS_SRC="$workdir/src/agents" \
    ADDY_SKILLS_SRC="$workdir/src/skills" \
    ADDY_AGENTS_DEST="$workdir/dest/agents" \
    ADDY_SKILLS_DEST="$workdir/dest/skills" \
    ADDY_REFERENCES_SRC="$workdir/src/references" \
    ADDY_REFERENCES_DEST="$workdir/dest/references" \
    ADDY_HOOKS_SRC="$workdir/src/hooks" \
    ADDY_HOOKS_DEST="$workdir/dest/hooks" \
    ADDY_SKILLS_STATE_FILE="$workdir/installed-skills.txt" \
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  assert_equals \
    "yes" \
    "$([[ -d "$workdir/dest/hooks" ]] && echo yes || echo no)" \
    "Expected destination hooks directory to be created."
}

main() {
  local workdir

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' EXIT

  test_copies_referenced_skills_transitively "$workdir/transitive"
  test_copies_referenced_skills_without_agents "$workdir/no-agents"
  test_copies_skills_selected_from_file "$workdir/skills-file"
  test_writes_skills_state_file_for_current_install "$workdir/skills-state-file"
  test_copies_root_references_directory "$workdir/references"
  test_rewrites_root_reference_links_for_copied_skills "$workdir/skill-reference-links"
  test_clones_addy_repo_before_copying "$workdir/clone"
  test_pulls_latest_addy_repo_before_copying "$workdir/pull"
  test_copies_hooks_directory "$workdir/hooks"
  test_preserves_existing_hooks_files "$workdir/hooks-preserve"
  test_handles_missing_hooks_dir_gracefully "$workdir/hooks-missing"
}

main "$@"
