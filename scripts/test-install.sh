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

create_fixture_repo() {
  local repo="$1"

  mkdir -p \
    "$repo/scripts" \
    "$repo/skills/alpha" \
    "$repo/agents" \
    "$repo/references" \
    "$repo/hooks" \
    "$repo/.gemini/policies" \
    "$repo/.copilot"

  cp -p "$REPO_ROOT/scripts/install.sh" "$repo/scripts/install.sh"
  printf '%s\n' '---' 'name: alpha' '---' 'Standalone.' > "$repo/skills/alpha/SKILL.md"
  printf '%s\n' '---' 'name: helper' '---' 'Use alpha.' > "$repo/agents/helper.md"
  printf '%s\n' 'Gemini root.' > "$repo/.gemini/GEMINI.md"
  printf '%s\n' 'Nested policy.' > "$repo/.gemini/policies/plan-custom-directory.toml"
  printf '%s\n' 'Hidden note.' > "$repo/.gemini/.hidden-note"
  printf '%s\n' 'Copilot instructions.' > "$repo/.copilot/copilot-instructions.md"
  printf '%s\n' '{}' > "$repo/.copilot/lsp-config.json"
}

test_copies_full_gemini_tree() {
  local workdir
  local repo
  local home
  local copied_gemini
  local copied_policy
  local copied_hidden

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  home="$workdir/home"

  create_fixture_repo "$repo"

  HOME="$home" bash "$repo/scripts/install.sh" >/dev/null

  copied_gemini="$(<"$home/.gemini/GEMINI.md")"
  copied_policy="$(<"$home/.gemini/policies/plan-custom-directory.toml")"
  copied_hidden="$(<"$home/.gemini/.hidden-note")"

  assert_equals "Gemini root." "$copied_gemini" "Expected GEMINI.md to be copied into ~/.gemini."
  assert_equals "Nested policy." "$copied_policy" "Expected nested Gemini files to be copied recursively."
  assert_equals "Hidden note." "$copied_hidden" "Expected hidden Gemini files to be copied recursively."

  if [[ -e "$home/.gemini/.gemini" ]]; then
    echo "Expected the installer to copy Gemini contents into ~/.gemini, not nest another .gemini directory." >&2
    exit 1
  fi
}

main() {
  test_copies_full_gemini_tree
}

main "$@"
