#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

write_required_skill_fixtures() {
  local skills_dir="$1"

  mkdir -p \
    "$skills_dir/universal-guidelines" \
    "$skills_dir/cli-compression" \
    "$skills_dir/context-engineering" \
    "$skills_dir/caveman"

  cat >"$skills_dir/universal-guidelines/SKILL.md" <<'EOF'
---
name: universal-guidelines
description: Universal rules.
---
# Universal Guidelines
Line A.
EOF

  cat >"$skills_dir/cli-compression/SKILL.md" <<'EOF'
---
name: cli-compression
description: RTK rules.
---
# CLI Compression
Line B.
EOF

  cat >"$skills_dir/context-engineering/SKILL.md" <<'EOF'
---
name: context-engineering
description: Context rules.
---
# Context Engineering
Line C.
EOF

  cat >"$skills_dir/caveman/SKILL.md" <<'EOF'
---
name: caveman
description: Terse style.
---
# Caveman
Line D.
EOF
}

run_skill_context_injector() {
  local skills_dir="$1"
  local payload="$2"

  AGENTS_SKILLS_DIR="$skills_dir" \
  bash "$REPO_ROOT/.gemini/hooks/scripts/skill-context-injector.sh" <<<"$payload"
}

expected_caveman_context() {
  local skills_dir="$1"
  cat "$skills_dir/caveman/SKILL.md"
}

assert_caveman_context_shape() {
  local context="$1"

  [[ "$context" == *"# Caveman"* ]] || {
    echo "Expected payload to include caveman content." >&2
    exit 1
  }
  [[ "$context" != *"# Universal Guidelines"* ]] || {
    echo "Expected payload to exclude universal-guidelines content." >&2
    exit 1
  }
  [[ "$context" != *"# CLI Compression"* ]] || {
    echo "Expected payload to exclude cli-compression content." >&2
    exit 1
  }
  [[ "$context" != *"# Context Engineering"* ]] || {
    echo "Expected payload to exclude context-engineering content." >&2
    exit 1
  }
}

test_before_agent_default_mode_returns_caveman_only_context() {
  local workdir
  local output
  local skills_dir
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  skills_dir="$workdir/skills"
  write_required_skill_fixtures "$skills_dir"

  output="$(
    AUDIT_LOG="$workdir/audit.log" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-default","timestamp":"2026-06-24T10:00:00Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_equals "BeforeAgent" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected hookSpecificOutput.hookEventName to reflect the Gemini event."
  assert_equals "$(expected_caveman_context "$skills_dir")" "$context" \
    "Expected default mode to emit only caveman skill contents."
  assert_caveman_context_shape "$context"
}

test_compact_mode_override_still_returns_caveman_only_context() {
  local workdir
  local output
  local skills_dir
  local expected
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  skills_dir="$workdir/skills"
  write_required_skill_fixtures "$skills_dir"

  output="$(
    AUDIT_LOG="$workdir/audit.log" \
    GEMINI_REQUIRED_SKILL_CONTEXT_MODE="compact" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-compact","timestamp":"2026-06-24T10:00:01Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  expected="$(expected_caveman_context "$skills_dir")"
  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_equals "$expected" "$context" \
    "Expected compact override to be ignored and only caveman skill contents to load."
  assert_caveman_context_shape "$context"
}

test_missing_required_skill_file_fails_explicitly() {
  local workdir
  local output
  local skills_dir
  local missing_path

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  skills_dir="$workdir/skills"
  write_required_skill_fixtures "$skills_dir"
  missing_path="$skills_dir/caveman/SKILL.md"
  rm -f "$missing_path"

  output="$(
    AUDIT_LOG="$workdir/audit.log" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-missing","timestamp":"2026-06-24T10:00:02Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  assert_equals "false" "$(jq -r '.continue' <<<"$output")" \
    "Expected missing skill files to hard-stop the hook output."
  assert_equals "Required skill file not found: $missing_path" "$(jq -r '.stopReason' <<<"$output")" \
    "Expected missing skill files to report an explicit stop reason."
}

main() {
  test_before_agent_default_mode_returns_caveman_only_context
  test_compact_mode_override_still_returns_caveman_only_context
  test_missing_required_skill_file_fails_explicitly
}

main "$@"
