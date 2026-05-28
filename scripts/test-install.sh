#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

create_fixture_repo() {
  local repo="$1"

  mkdir -p \
    "$repo/scripts" \
    "$repo/skills/alpha" \
    "$repo/skills/alpha/evals" \
    "$repo/skills/beta-workspace" \
    "$repo/skills/archive" \
    "$repo/agents" \
    "$repo/agents/nested" \
    "$repo/references" \
    "$repo/.copilot/hooks" \
    "$repo/.gemini/policies"

  cp -p "$REPO_ROOT/scripts/install.sh" "$repo/scripts/install.sh"
  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$repo/skills/alpha/SKILL.md"
  printf '%s\n' 'fixture eval content' > "$repo/skills/alpha/evals/evals.json"
  printf '%s\n' 'workspace skill should not copy' > "$repo/skills/beta-workspace/SKILL.md"
  printf '%s\n' 'archive entry should not copy' > "$repo/skills/archive/README.md"
  printf '%s\n' '---' 'name: helper' '---' 'Use alpha.' > "$repo/agents/helper.md"
  printf '%s\n' '---' 'name: nested-helper' '---' 'Use alpha deeply.' > "$repo/agents/nested/helper.md"
  printf '%s\n' 'Gemini root.' > "$repo/.gemini/GEMINI.md"
  printf '%s\n' 'Nested policy.' > "$repo/.gemini/policies/plan-custom-directory.toml"
  printf '%s\n' 'Hidden note.' > "$repo/.gemini/.hidden-note"
  printf '%s\n' 'Copilot instructions.' > "$repo/.copilot/copilot-instructions.md"
  printf '%s\n' '{}' > "$repo/.copilot/lsp-config.json"
  printf '%s\n' '#!/bin/bash' 'echo hook' > "$repo/.copilot/hooks/test-hook.sh"
}

test_excludes_and_prunes_skill_evals() {
  local workdir
  local repo
  local home
  local copied_skill
  local copied_existing_note

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"
  mkdir -p "$home/.agents/skills/alpha/evals"
  printf '%s\n' 'stale eval content' > "$home/.agents/skills/alpha/evals/stale.txt"
  printf '%s\n' 'keep this installed note' > "$home/.agents/skills/alpha/existing-note.txt"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  copied_skill="$(<"$home/.agents/skills/alpha/SKILL.md")"
  copied_existing_note="$(<"$home/.agents/skills/alpha/existing-note.txt")"
  assert_equals $'---\nname: alpha\n---\nStandalone.' "$copied_skill" "Expected non-evals skill content to remain installed."
  assert_equals "keep this installed note" "$copied_existing_note" "Expected existing non-evals installed content to remain after eval cleanup."

  if [[ -d "$home/.agents/skills/alpha/evals" ]]; then
    echo "Expected ~/.agents/skills/alpha/evals to be removed during install." >&2
    exit 1
  fi

  if [[ -e "$home/.agents/skills/beta-workspace" ]]; then
    echo "Expected *-workspace skills to remain excluded from top-level selection." >&2
    exit 1
  fi

  if [[ -e "$home/.agents/skills/archive" ]]; then
    echo "Expected archive entries to remain excluded from top-level selection." >&2
    exit 1
  fi
}

test_copies_full_gemini_tree() {
  local workdir
  local repo
  local home
  local copied_gemini
  local copied_agent
  local copied_nested_agent
  local copied_copilot_agent
  local copied_copilot_nested_agent
  local copied_policy
  local copied_hidden
  local copied_hook

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  copied_gemini="$(<"$home/.gemini/GEMINI.md")"
  copied_agent="$(<"$home/.gemini/agents/helper.md")"
  copied_nested_agent="$(<"$home/.gemini/agents/nested/helper.md")"
  copied_copilot_agent="$(<"$home/.copilot/agents/helper.md")"
  copied_copilot_nested_agent="$(<"$home/.copilot/agents/nested/helper.md")"
  copied_policy="$(<"$home/.gemini/policies/plan-custom-directory.toml")"
  copied_hidden="$(<"$home/.gemini/.hidden-note")"
  copied_hook="$(<"$home/.copilot/hooks/test-hook.sh")"

  assert_equals "Gemini root." "$copied_gemini" "Expected GEMINI.md to be copied into ~/.gemini."
  assert_equals $'---\nname: helper\n---\nUse alpha.' "$copied_agent" "Expected agents to be copied into ~/.gemini/agents."
  assert_equals $'---\nname: nested-helper\n---\nUse alpha deeply.' "$copied_nested_agent" "Expected nested agents to be copied recursively into ~/.gemini/agents."
  assert_equals $'---\nname: helper\n---\nUse alpha.' "$copied_copilot_agent" "Expected agents to be copied into ~/.copilot/agents."
  assert_equals $'---\nname: nested-helper\n---\nUse alpha deeply.' "$copied_copilot_nested_agent" "Expected nested agents to be copied recursively into ~/.copilot/agents."
  assert_equals "Nested policy." "$copied_policy" "Expected nested Gemini files to be copied recursively."
  assert_equals "Hidden note." "$copied_hidden" "Expected hidden Gemini files to be copied recursively."
  assert_equals $'#!/bin/bash\necho hook' "$copied_hook" "Expected hooks to be copied into ~/.copilot/hooks."

  if [[ -e "$home/.gemini/.gemini" ]]; then
    echo "Expected the installer to copy Gemini contents into ~/.gemini, not nest another .gemini directory." >&2
    exit 1
  fi

}

main() {
  test_excludes_and_prunes_skill_evals
  test_copies_full_gemini_tree
}

main "$@"
