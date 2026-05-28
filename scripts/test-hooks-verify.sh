#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_hook() {
  local audit_log="$1"
  local payload="$2"
  local copilot_home="${3:-}"

  run_copilot_hook "verify.sh" "$audit_log" "$payload" "$copilot_home"
}

test_skips_when_no_relevant_files() {
  local workdir
  local audit_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  run_hook \
    "$audit_log" \
    '{"sessionId":"skip","timestamp":"2026-05-12T19:00:00Z","toolName":"edit","toolArgs":{"path":"README.txt","file_text":"hello"}}'

  assert_file_contains "$audit_log" "skipping verify.sh: No relevant files changed" \
    "Expected the hook to skip non-relevant files."
}

test_logs_correct_audit_format() {
  local workdir
  local audit_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  run_hook \
    "$audit_log" \
    '{"sessionId":"format-check","timestamp":"2026-05-12T19:00:01Z","toolName":"edit","toolArgs":{"path":"src/Widget.cs","file_text":"class W {}"}}'

  # Correct format: [sender] [timestamp] Session: ...
  if grep -q "^\[verify.sh\] \[2026-05-12T19:00:01Z\] Session: format-check, File: src/Widget.cs" "$audit_log"; then
    echo "Confirmed: Audit log entry format is correct."
  else
    echo "Audit log entry format is INCORRECT." >&2
    cat "$audit_log" >&2
    exit 1
  fi
}

test_dotnet_verify_success() {
  local workdir
  local audit_log
  local repo_mock

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  repo_mock="$workdir/repo"

  mkdir -p "$repo_mock/src/Project"
  touch "$repo_mock/src/Project/Project.csproj"

  mock_bin "$workdir" "dotnet" '#!/usr/bin/env bash\nif [[ "$1" == "build" ]]; then\n  echo "Build successful"\n  exit 0\nelif [[ "$1" == "test" ]]; then\n  echo "Tests passed"\n  exit 0\nfi\nexit 1'

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"
  
  # We need verify.sh to use our repo_mock
  # The hook gets REPO_ROOT from git rev-parse or pwd.
  # We'll run it from repo_mock.
  (
    cd "$repo_mock"
    git init >/dev/null
    run_hook \
      "$audit_log" \
      '{"sessionId":"verify-ok","timestamp":"2026-05-12T19:00:02Z","toolName":"edit","toolArgs":{"path":"src/Project/Widget.cs","file_text":"public class Widget {}"}}'
  )

  PATH="$old_path"

  assert_file_contains "$audit_log" "Command: dotnet build && dotnet test --no-build" \
    "Expected the hook to run dotnet verify."
}

test_efficient_subagent_polling() {
  local workdir
  local audit_log
  local copilot_home
  local session_id
  local repo_mock

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  session_id="efficient-polling"
  repo_mock="$workdir/repo"

  mkdir -p "$repo_mock/src"
  touch "$repo_mock/src/Project.csproj"

  mock_bin "$workdir" "dotnet" '#!/usr/bin/env bash\nexit 0'

  mkdir -p "$copilot_home/session-state/$session_id"
  local events_file="$copilot_home/session-state/$session_id/events.jsonl"
  
  cat >"$events_file" <<EOF
{"type":"tool.execution_start","data":{"toolName":"create","arguments":{"path":"src/One.cs"}}}
EOF

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"

  (
    cd "$repo_mock"
    git init >/dev/null
    
    # First run
    run_hook "$audit_log" "{\"sessionId\":\"$session_id\",\"toolName\":\"task\"}" "$copilot_home"
    assert_file_contains "$audit_log" "File: src/One.cs" "Expected first run to process first event."

    # Clear audit log for second run
    > "$audit_log"

    # Second run without new events
    run_hook "$audit_log" "{\"sessionId\":\"$session_id\",\"toolName\":\"task\"}" "$copilot_home"
    if grep -q "File: src/One.cs" "$audit_log"; then
      echo "Efficiency failure: Processed same event twice." >&2
      exit 1
    fi

    # Third run with new event
    cat >>"$events_file" <<EOF
{"type":"tool.execution_start","data":{"toolName":"edit","arguments":{"path":"src/Two.cs"}}}
EOF
    run_hook "$audit_log" "{\"sessionId\":\"$session_id\",\"toolName\":\"task\"}" "$copilot_home"
    assert_file_contains "$audit_log" "File: src/Two.cs" "Expected third run to process new event."
    if grep -q "File: src/One.cs" "$audit_log"; then
      echo "Efficiency failure: Processed old event again." >&2
      exit 1
    fi
  )

  PATH="$old_path"
  echo "Efficiency test passed."
}

test_logs_apply_patch_files() {
  local workdir
  local audit_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  local patch_data='*** Update File: src/Patch.cs
--- old
+++ new
'
  
  local payload
  payload=$(jq -n \
    --arg sid "patch-test" \
    --arg ts "2026-05-12T19:00:05Z" \
    --arg tn "apply_patch" \
    --arg ta "$patch_data" \
    '{sessionId: $sid, timestamp: $ts, toolName: $tn, toolArgs: $ta}')

  run_hook "$audit_log" "$payload"

  assert_file_contains "$audit_log" "File: *** Update File: src/Patch.cs" \
    "Expected apply_patch to log the relevant file line."
}

main() {
  test_skips_when_no_relevant_files
  test_logs_correct_audit_format
  test_logs_apply_patch_files
  test_dotnet_verify_success
  test_efficient_subagent_polling
}

main "$@"
