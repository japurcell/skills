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
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  installed_skills="$(
    find "$workdir/dest/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | paste -sd ',' -
  )"

  assert_equals \
    "addy-alpha,addy-beta" \
    "$installed_skills" \
    "Expected dependency copying to work even when no agent files exist."
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
    bash "$REPO_ROOT/scripts/addy-install.sh" --skills alpha >/dev/null

  copied_skill="$(<"$workdir/dest/skills/addy-alpha/SKILL.md")"

  assert_equals \
    $'---\nname: addy-alpha\n---\nSee `../../references/accessibility-checklist.md` for the full checklist.' \
    "$copied_skill" \
    "Expected copied skill reference links to point to the repository references directory."
}

main() {
  local workdir

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' EXIT

  test_copies_referenced_skills_transitively "$workdir/transitive"
  test_copies_referenced_skills_without_agents "$workdir/no-agents"
  test_copies_root_references_directory "$workdir/references"
  test_rewrites_root_reference_links_for_copied_skills "$workdir/skill-reference-links"
}

main "$@"
