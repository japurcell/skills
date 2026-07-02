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

strip_frontmatter() {
  local file_path="$1"
  awk '
    BEGIN { in_header = 0; first_line = 1 }
    {
      line = $0
      sub(/\r$/, "", line)
      if (first_line) {
        first_line = 0
        if (line == "---") {
          in_header = 1
          next
        }
      }
      if (in_header) {
        if (line == "---") {
          in_header = 0
        }
        next
      }
      print
    }
  ' "$file_path"
}

expected_caveman_context() {
  local skills_dir="$1"
  strip_frontmatter "$skills_dir/caveman/SKILL.md"
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
  local expected_context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  skills_dir="$workdir/skills"
  write_required_skill_fixtures "$skills_dir"

  output="$(
    AUDIT_LOG="$workdir/audit.log" \
    AGENTS_REQUIRED_SKILL_FILES="caveman/SKILL.md" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-default","timestamp":"2026-06-24T10:00:00Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_equals "BeforeAgent" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected hookSpecificOutput.hookEventName to reflect the Gemini event."

  expected_context="<!-- BEGIN REQUIRED SKILL: $skills_dir/caveman/SKILL.md -->"$'\n'
  expected_context+="$(expected_caveman_context "$skills_dir")"$'\n'
  expected_context+="<!-- END REQUIRED SKILL: $skills_dir/caveman/SKILL.md -->"

  assert_equals "$expected_context" "$context" \
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
    AGENTS_REQUIRED_SKILL_FILES="caveman/SKILL.md" \
    GEMINI_REQUIRED_SKILL_CONTEXT_MODE="compact" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-compact","timestamp":"2026-06-24T10:00:01Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  expected="<!-- BEGIN REQUIRED SKILL: $skills_dir/caveman/SKILL.md -->"$'\n'
  expected+="$(expected_caveman_context "$skills_dir")"$'\n'
  expected+="<!-- END REQUIRED SKILL: $skills_dir/caveman/SKILL.md -->"

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
    AGENTS_REQUIRED_SKILL_FILES="caveman/SKILL.md" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-missing","timestamp":"2026-06-24T10:00:02Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  assert_equals "false" "$(jq -r '.continue' <<<"$output")" \
    "Expected missing skill files to hard-stop the hook output."
  assert_equals "Required skill file not found: $missing_path" "$(jq -r '.stopReason' <<<"$output")" \
    "Expected missing skill files to report an explicit stop reason."
}

test_multiple_skills_loading_works_correctly() {
  local workdir
  local output
  local skills_dir
  local context
  local expected_context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  skills_dir="$workdir/skills"
  write_required_skill_fixtures "$skills_dir"

  output="$(
    AUDIT_LOG="$workdir/audit.log" \
    AGENTS_REQUIRED_SKILL_FILES="caveman/SKILL.md,context-engineering/SKILL.md" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-multiple","timestamp":"2026-06-24T10:00:03Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_equals "BeforeAgent" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected hookSpecificOutput.hookEventName to reflect the Gemini event."

  expected_context="<!-- BEGIN REQUIRED SKILL: $skills_dir/caveman/SKILL.md -->"$'\n'
  expected_context+="$(expected_caveman_context "$skills_dir")"$'\n'
  expected_context+="<!-- END REQUIRED SKILL: $skills_dir/caveman/SKILL.md -->"$'\n\n'
  expected_context+="<!-- BEGIN REQUIRED SKILL: $skills_dir/context-engineering/SKILL.md -->"$'\n'
  expected_context+="$(strip_frontmatter "$skills_dir/context-engineering/SKILL.md")"$'\n'
  expected_context+="<!-- END REQUIRED SKILL: $skills_dir/context-engineering/SKILL.md -->"

  assert_equals "$expected_context" "$context" \
    "Expected multiple skills mode to emit correct delimited skill contents."
}

test_empty_skills_logs_no_skills_loaded_and_outputs_no_hook_specific_output() {
  local workdir
  local output
  local skills_dir

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  skills_dir="$workdir/skills"
  write_required_skill_fixtures "$skills_dir"

  output="$(
    AUDIT_LOG="$workdir/audit.log" \
    AGENTS_REQUIRED_SKILL_FILES="" \
    run_skill_context_injector \
      "$skills_dir" \
      '{"session_id":"gemini-empty","timestamp":"2026-06-24T10:00:04Z","hook_event_name":"BeforeAgent","cwd":"/repo","prompt":"hello"}'
  )"

  assert_equals "No skills loaded" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected empty skills output to have systemMessage 'No skills loaded'."
  assert_equals "true" "$(jq -r '.suppressOutput' <<<"$output")" \
    "Expected empty skills output to have suppressOutput true."
  assert_equals "false" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected no hookSpecificOutput for empty skills payload."

  assert_file_contains "$workdir/audit.log" "Message: No skills loaded" \
    "Expected audit log to contain No skills loaded message."
}

main() {
  test_before_agent_default_mode_returns_caveman_only_context
  test_compact_mode_override_still_returns_caveman_only_context
  test_missing_required_skill_file_fails_explicitly
  test_multiple_skills_loading_works_correctly
  test_empty_skills_logs_no_skills_loaded_and_outputs_no_hook_specific_output
}

main "$@"
