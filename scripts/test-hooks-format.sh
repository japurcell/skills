#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_hook() {
  local audit_log="$1"
  local max_bytes="$2"
  local payload="$3"
  local copilot_home="${4:-}"

  run_copilot_hook "format.sh" "$audit_log" "$payload" "$copilot_home" "AUDIT_LOG_MAX_BYTES=$max_bytes" >/dev/null
}

test_hook_scripts_use_audit_lib_without_deprecated_helpers() {
  local scripts_dir="$REPO_ROOT/.copilot/hooks/scripts"
  local script

  if grep -Fq 'parse_input()' "$scripts_dir/common.sh"; then
    echo "Expected common.sh to delete deprecated parse_input helper." >&2
    exit 1
  fi

  if grep -Fq 'cleanup_lock()' "$scripts_dir/common.sh"; then
    echo "Expected common.sh to delete deprecated cleanup_lock helper." >&2
    exit 1
  fi

  if grep -Fq 'setup_audit_log()' "$scripts_dir/common.sh"; then
    echo "Expected common.sh to delete deprecated setup_audit_log helper." >&2
    exit 1
  fi

  while IFS= read -r script; do
    if grep -Fq 'parse_input ' "$script"; then
      echo "Expected parse_input usage to be removed from $script." >&2
      exit 1
    fi

    if grep -Fq 'setup_audit_log' "$script"; then
      echo "Expected deprecated setup_audit_log usage to be removed from $script." >&2
      exit 1
    fi
  done < <(find "$scripts_dir" -maxdepth 1 -name '*.sh' | sort)

  for script in \
    "$scripts_dir/format.sh" \
    "$scripts_dir/hedge-detector.sh" \
    "$scripts_dir/log-agent-stop.sh" \
    "$scripts_dir/log-error-occurred.sh" \
    "$scripts_dir/log-notification.sh" \
    "$scripts_dir/log-permission-request.sh" \
    "$scripts_dir/log-post-tooluse.sh" \
    "$scripts_dir/log-pre-tooluse.sh" \
    "$scripts_dir/log-session-end.sh" \
    "$scripts_dir/log-session-start.sh" \
    "$scripts_dir/log-subagent-start.sh" \
    "$scripts_dir/log-subagent-stop.sh" \
    "$scripts_dir/log-tooluse-failure.sh" \
    "$scripts_dir/pride-check.sh"
  do
    assert_file_contains "$script" 'source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"' \
      "Expected $script to source audit.sh."
    assert_file_contains "$script" 'audit_init' \
      "Expected $script to initialize audit logging with audit_init."
    assert_file_contains "$script" 'audit_log_event' \
      "Expected $script to log through audit_log_event."
  done

  assert_file_contains "$scripts_dir/scan-secrets.sh" 'source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"' \
    "Expected scan-secrets.sh to source audit.sh."
  assert_file_contains "$scripts_dir/scan-secrets.sh" 'audit_init' \
    "Expected scan-secrets.sh to initialize audit logging with audit_init."
  assert_file_contains "$scripts_dir/scan-secrets.sh" 'audit_log_event' \
    "Expected scan-secrets.sh to log through audit_log_event."
  assert_file_contains "$scripts_dir/tool-guard.sh" 'source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"' \
    "Expected tool-guard.sh to source audit.sh."
  assert_file_contains "$scripts_dir/tool-guard.sh" 'audit_init' \
    "Expected tool-guard.sh to initialize audit logging with audit_init."
  assert_file_contains "$scripts_dir/tool-guard.sh" 'audit_log_event' \
    "Expected tool-guard.sh to log through audit_log_event."
}

test_logs_csharp_apply_patch_command_before_formatter_failure() {
  local workdir
  local audit_log
  local old_path

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "dotnet" '#!/usr/bin/env bash\nexit 1'

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"
  if run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"cs","timestamp":"2026-05-12T19:00:03Z","toolName":"apply_patch","toolArgs":"*** Begin Patch\n*** Update File: /tmp/Widget.cs\n@@\n- old\n+ new\n*** End Patch"}'
  then
    echo "Expected the hook to fail when dotnet format fails." >&2
    exit 1
  fi
  PATH="$old_path"

  assert_file_contains "$audit_log" "Session: cs, File: /tmp/Widget.cs" \
    "Expected the hook to detect C# edits reported via apply_patch."

  assert_file_contains "$audit_log" "Session: cs, Command: dotnet format --no-restore --include /tmp/Widget.cs" \
    "Expected the hook to log the formatter command before the formatter fails."

  assert_file_contains "$audit_log" "Session: cs, Failure: dotnet format --no-restore --include /tmp/Widget.cs (exit 1)" \
    "Expected the hook to write the dotnet format failure to the audit log."
}

test_logs_js_formatter_failure() {
  local workdir
  local audit_log
  local old_path

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "npx" '#!/usr/bin/env bash\nexit 1'

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"
  if run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"js","timestamp":"2026-05-12T19:00:04Z","toolName":"edit","toolArgs":{"path":"/tmp/app.ts","file_text":"const value = 1;"}}'
  then
    echo "Expected the hook to fail when npx oxfmt fails." >&2
    exit 1
  fi
  PATH="$old_path"

  assert_file_contains "$audit_log" "Session: js, Command: npx oxfmt /tmp/app.ts" \
    "Expected the hook to log the formatter command before the formatter fails."

  assert_file_contains "$audit_log" "Session: js, Failure: npx oxfmt /tmp/app.ts (exit 1)" \
    "Expected the hook to write the npx oxfmt failure to the audit log."
}

test_logs_subagent_csharp_file_from_task_session_events() {
  local workdir
  local audit_log
  local copilot_home
  local session_id
  local task_result
  local old_path

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  session_id="task-parent"
  task_result="The file was created using the create tool. A minimal valid C# class was written to /tmp/Widget.cs. No repository files were modified."

  mock_bin "$workdir" "dotnet" '#!/usr/bin/env bash\nexit 0'

  mkdir -p "$copilot_home/session-state/$session_id"
  cat >"$copilot_home/session-state/$session_id/events.jsonl" <<EOF
{"type":"tool.execution_start","data":{"toolCallId":"parent-task","toolName":"task","arguments":{"description":"Reproducing subagent hook","agent_type":"general-purpose"}}}
{"type":"tool.execution_start","data":{"parentToolCallId":"parent-task","toolCallId":"child-create","toolName":"create","arguments":{"path":"/tmp/Widget.cs","file_text":"public class Widget {}"}}}
{"type":"tool.execution_complete","data":{"toolCallId":"parent-task","success":true,"result":{"content":"$task_result"},"toolTelemetry":{"restrictedProperties":{"agent_id":"subagent-hook-repro"}}}}
EOF

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"
  run_hook \
    "$audit_log" \
    1024 \
    "{\"sessionId\":\"$session_id\",\"timestamp\":\"2026-05-12T19:00:05Z\",\"toolName\":\"task\",\"toolArgs\":{\"description\":\"Reproducing subagent hook\",\"agent_type\":\"general-purpose\"},\"toolResult\":{\"resultType\":\"success\",\"textResultForLlm\":\"$task_result\",\"toolTelemetry\":{\"restrictedProperties\":{\"agent_id\":\"subagent-hook-repro\"}}}}" \
    "$copilot_home"
  PATH="$old_path"

  assert_file_contains "$audit_log" "Session: $session_id, Tool: task" \
    "Expected the hook to log the parent task tool use."

  assert_file_contains "$audit_log" "Session: $session_id, File: /tmp/Widget.cs" \
    "Expected the hook to recover subagent C# edits from the session events transcript."
}

test_logs_background_subagent_apply_patch_file_from_read_agent_events() {
  local workdir
  local audit_log
  local copilot_home
  local session_id
  local old_path

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  session_id="background-agent"

  mock_bin "$workdir" "dotnet" '#!/usr/bin/env bash\nexit 0'

  mkdir -p "$copilot_home/session-state/$session_id"
  cat >"$copilot_home/session-state/$session_id/events.jsonl" <<'EOF'
{"type":"tool.execution_start","data":{"toolCallId":"parent-task","toolName":"task","arguments":{"agent_type":"general-purpose","name":"share-cart-implementer","mode":"background","description":"Implement ShareCart task"}}}
{"type":"tool.execution_start","data":{"parentToolCallId":"parent-task","toolCallId":"child-apply-patch","toolName":"apply_patch","arguments":"*** Begin Patch\n*** Update File: /tmp/ShareCartOperationalAssetSeedingTests.cs\n@@\n- old\n+ new\n*** End Patch"}}
EOF

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"
  run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"background-agent","timestamp":"2026-05-13T14:10:17Z","toolName":"read_agent","toolArgs":{"agent_id":"share-cart-implementer","wait":true,"timeout":30},"toolResult":{"resultType":"success","textResultForLlm":"Agent is idle (waiting for messages). agent_id: share-cart-implementer"}}' \
    "$copilot_home"
  PATH="$old_path"

  assert_file_contains "$audit_log" "Session: background-agent, Tool: read_agent" \
    "Expected the hook to log read_agent tool use for background subagents."

  assert_file_contains "$audit_log" "Session: background-agent, File: /tmp/ShareCartOperationalAssetSeedingTests.cs" \
    "Expected the hook to recover subagent apply_patch edits when read_agent returns a background task result."
}

test_logs_background_subagent_apply_patch_file_from_read_agent_events_with_camel_case_agent_id() {
  local workdir
  local audit_log
  local copilot_home
  local session_id
  local old_path

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  session_id="background-agent-camel"

  mock_bin "$workdir" "dotnet" '#!/usr/bin/env bash\nexit 0'

  mkdir -p "$copilot_home/session-state/$session_id"
  cat >"$copilot_home/session-state/$session_id/events.jsonl" <<'EOF'
{"type":"tool.execution_start","data":{"toolCallId":"parent-task","toolName":"task","arguments":{"agent_type":"general-purpose","name":"share-cart-implementer","mode":"background","description":"Implement ShareCart task"}}}
{"type":"tool.execution_start","data":{"parentToolCallId":"parent-task","toolCallId":"child-apply-patch","toolName":"apply_patch","arguments":"*** Begin Patch\n*** Update File: /tmp/ShareCartCamelCase.cs\n@@\n- old\n+ new\n*** End Patch"}}
EOF

  old_path="$PATH"
  PATH="$workdir/bin:$PATH"
  run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"background-agent-camel","timestamp":"2026-05-13T14:10:18Z","toolName":"read_agent","toolArgs":{"agentId":"share-cart-implementer","wait":true,"timeout":30},"toolResult":{"resultType":"success","textResultForLlm":"Agent is idle (waiting for messages). agent_id: share-cart-implementer"}}' \
    "$copilot_home"
  PATH="$old_path"

  assert_file_contains "$audit_log" "Session: background-agent-camel, Tool: read_agent" \
    "Expected the hook to log read_agent tool use for background subagents."

  assert_file_contains "$audit_log" "Session: background-agent-camel, File: /tmp/ShareCartCamelCase.cs" \
    "Expected the hook to recover subagent apply_patch edits when read_agent uses camelCase agentId."
}

test_ignores_tools_without_files() {
  local workdir
  local audit_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"nofiles","timestamp":"2026-05-12T19:00:06Z","toolName":"report_intent","toolArgs":{"intent":"Testing"}}'

  assert_file_contains "$audit_log" "Session: nofiles, Tool: report_intent" \
    "Expected the hook to log tools that do not carry file paths without crashing."
}

test_rolls_over_audit_log() {
  local workdir
  local audit_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  run_hook \
    "$audit_log" \
    1 \
    '{"sessionId":"one","timestamp":"2026-05-12T19:00:00Z","toolName":"create","toolArgs":{"path":"/tmp/one.txt","file_text":"alpha"}}'

  run_hook \
    "$audit_log" \
    1 \
    '{"sessionId":"two","timestamp":"2026-05-12T19:00:01Z","toolName":"create","toolArgs":{"path":"/tmp/two.txt","file_text":"beta"}}'

  assert_equals "yes" "$([[ -f "$audit_log.1" ]] && echo yes || echo no)" \
    "Expected audit.log to roll over into audit.log.1 when it grows past the configured size."

  assert_equals "yes" "$([[ -f "$audit_log" ]] && echo yes || echo no)" \
    "Expected the current audit.log to remain writable after rollover."

  assert_file_contains "$audit_log.1" "Session: one, Tool: create" \
    "Expected the first write to move into audit.log.1."

  assert_file_contains "$audit_log" "Session: two, Tool: create" \
    "Expected the second write to stay in the active audit log."
}

test_waits_for_log_lock() {
  local workdir
  local audit_log
  local lock_file
  local start_ns
  local end_ns
  local elapsed_ms
  local locker_pid

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  lock_file="$audit_log.lock"

  (
    exec 9>"$lock_file"
    flock -x 9
    sleep 1
  ) &
  locker_pid="$!"

  start_ns="$(date +%s%N)"
  run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"lock","timestamp":"2026-05-12T19:00:02Z","toolName":"create","toolArgs":{"path":"/tmp/lock.txt","file_text":"gamma"}}'
  end_ns="$(date +%s%N)"
  wait "$locker_pid"

  elapsed_ms=$(( (end_ns - start_ns) / 1000000 ))

  if (( elapsed_ms < 900 )); then
    echo "Expected the hook to wait for the audit lock, but it completed in ${elapsed_ms}ms." >&2
    exit 1
  fi

  assert_file_contains "$audit_log" "Session: lock, Tool: create" \
    "Expected the hook to write after acquiring the log lock."
}

main() {
  test_hook_scripts_use_audit_lib_without_deprecated_helpers
  test_logs_csharp_apply_patch_command_before_formatter_failure
  test_logs_js_formatter_failure
  test_logs_subagent_csharp_file_from_task_session_events
  test_logs_background_subagent_apply_patch_file_from_read_agent_events
  test_logs_background_subagent_apply_patch_file_from_read_agent_events_with_camel_case_agent_id
  test_ignores_tools_without_files
  test_rolls_over_audit_log
  test_waits_for_log_lock
}

main "$@"
