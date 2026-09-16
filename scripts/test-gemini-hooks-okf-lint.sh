#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

create_fixture_repo() {
  local repo="$1"

  rm -rf -- "$repo"
  mkdir -p "$repo"
  cp -R "$REPO_ROOT/scripts/fixtures/okf-valid-repo/." "$repo"
  mkdir -p "$repo/scripts"
  cp "$REPO_ROOT/scripts/lint-okf.py" "$repo/scripts/lint-okf.py"
  cp -R "$REPO_ROOT/scripts/vendor" "$repo/scripts/vendor"
  mkdir -p "$repo/.gemini/hooks/scripts"
  cp "$REPO_ROOT/.gemini/hooks/scripts/lint-okf.py" "$repo/.gemini/hooks/scripts/lint-okf.py"
  cp -R "$REPO_ROOT/.gemini/hooks/scripts/helpers" "$repo/.gemini/hooks/scripts/helpers"
}

run_adapter() {
  local repo="$1"
  local payload="$2"

  python3 "$repo/.gemini/hooks/scripts/lint-okf.py" <<<"$payload"
}

write_fake_linter() {
  local repo="$1"
  local body="$2"

  printf '%s\n' '#!/usr/bin/env python3' "$body" > "$repo/scripts/lint-okf.py"
  chmod 755 "$repo/scripts/lint-okf.py"
}

assert_json_only_stdout() {
  local output="$1"

  assert_equals 1 "$(wc -l <<<"$output" | tr -d ' ')" \
    "Expected the adapter to emit exactly one JSON line."
  jq -e 'type == "object"' <<<"$output" >/dev/null
}

test_clean_events_return_empty_json() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"

  for event in AfterTool AfterAgent; do
    output="$(run_adapter "$repo" '{"hook_event_name":"'"$event"'","cwd":"'"$repo"'"}')"
    assert_json_only_stdout "$output"
    assert_equals '{}' "$(jq -c . <<<"$output")" \
      "Expected clean $event validation to be a Gemini no-op."
  done
}

test_payload_cwd_stays_within_adapter_checkout() {
  local workdir repo nested decoy output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  nested="$repo/nested/work"
  decoy="$workdir/decoy"
  create_fixture_repo "$repo"
  mkdir -p "$nested" "$decoy/scripts"

  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'/nested/../nested/work"}')"
  assert_equals '{}' "$(jq -c . <<<"$output")" \
    "Expected a normalized nested payload cwd to lint the adapter checkout."

  write_fake_linter "$decoy" 'from pathlib import Path; import json; Path("decoy-ran").touch(); print(json.dumps({"schema_version": 1, "diagnostics": []}))'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$decoy"'"}')"
  jq -e 'keys == ["decision", "reason"] and .decision == "deny" and (.reason | contains("OKF900"))' \
    <<<"$output" >/dev/null
  if [[ -e "$decoy/decoy-ran" ]]; then
    echo "Expected an out-of-checkout payload cwd never to execute its decoy linter." >&2
    exit 1
  fi
}

test_invalid_after_tool_matches_central_diagnostics() {
  local workdir repo central adapter_output central_output adapter_diagnostics

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  printf '# invalid\n' > "$repo/.agents/instructions/invalid.md"

  central_output="$(cd "$repo" && python3 scripts/lint-okf.py --format json)" || true
  adapter_output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_json_only_stdout "$adapter_output"
  assert_equals "deny" "$(jq -r '.decision' <<<"$adapter_output")" \
    "Expected invalid AfterTool validation to deny the result."
  assert_file_contains <(jq -r '.reason' <<<"$adapter_output") "OKF002" \
    "Expected the Gemini denial to include the central diagnostic ID."
  adapter_diagnostics="$(jq -r '.diagnostics[] | "\(.path):\(.line):\(.column): \(.id) \(.message)"' <<<"$central_output")"
  assert_file_contains <(jq -r '.reason' <<<"$adapter_output") "$adapter_diagnostics" \
    "Expected the Gemini reason to preserve the central normalized diagnostic."
}

test_after_agent_retry_is_bounded() {
  local workdir repo first retry

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  printf '# invalid\n' > "$repo/.agents/memory/invalid.md"

  first="$(run_adapter "$repo" '{"hook_event_name":"AfterAgent","cwd":"'"$repo"'"}')"
  assert_equals "deny" "$(jq -r '.decision' <<<"$first")" \
    "Expected the first invalid AfterAgent result to request a retry."

  retry="$(run_adapter "$repo" '{"hook_event_name":"AfterAgent","stop_hook_active":true,"cwd":"'"$repo"'"}')"
  assert_equals "false" "$(jq -r '.continue' <<<"$retry")" \
    "Expected an active stop hook to halt retrying."
  assert_file_contains <(jq -r '.stopReason' <<<"$retry") "OKF002" \
    "Expected the retry stop reason to retain the OKF finding."
}

test_malformed_payload_and_linter_failures_are_okf900_blocks() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"

  output="$(printf 'not-json' | python3 "$repo/.gemini/hooks/scripts/lint-okf.py")"
  assert_equals "false" "$(jq -r '.continue' <<<"$output")" \
    "Expected malformed hook JSON to halt safely."
  assert_file_contains <(jq -r '.stopReason' <<<"$output") "OKF900" \
    "Expected malformed hook JSON to become OKF900."

  rm -f "$repo/scripts/lint-okf.py"
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected a missing linter to deny AfterTool."
  assert_file_contains <(jq -r '.reason' <<<"$output") "OKF900" \
    "Expected a missing linter to become OKF900."
}

test_invalid_linter_json_exit_two_and_timeout_are_okf900() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"

  write_fake_linter "$repo" 'print("not json")'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") "OKF900" \
    "Expected invalid linter JSON to become OKF900."

  write_fake_linter "$repo" 'import sys; print("{}") ; sys.exit(2)'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterAgent","cwd":"'"$repo"'"}')"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected exit 2 to deny the first AfterAgent completion."
  assert_file_contains <(jq -r '.reason' <<<"$output") "OKF900" \
    "Expected exit 2 to become OKF900."

  write_fake_linter "$repo" 'import time; time.sleep(9)'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") "OKF900" \
    "Expected an eight-second linter timeout to become OKF900."
}

test_truncates_sorted_diagnostics_and_keeps_rerun_command() {
  local workdir repo output reason lines

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  for number in $(seq -w 1 25); do
    printf '# invalid\n' > "$repo/.agents/instructions/invalid-$number.md"
  done

  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  reason="$(jq -r '.reason' <<<"$output")"
  lines="$(grep -c 'OKF002' <<<"$reason")"
  assert_equals "20" "$lines" "Expected the Gemini adapter to include only the first 20 diagnostics."
  assert_file_contains <(printf '%s' "$reason") '5 additional diagnostic(s) omitted.' \
    "Expected the Gemini adapter to report omitted diagnostics."
  assert_file_contains <(printf '%s' "$reason") './scripts/lint-okf.py' \
    "Expected the Gemini adapter to give the POSIX rerun command."
  if (( $(printf '%s' "$output" | wc -c | tr -d ' ') >= 8192 )); then
    echo "Expected Gemini adapter JSON output to remain below 8 KiB." >&2
    exit 1
  fi
}

test_windows_rerun_command_uses_python() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  printf '# invalid\n' > "$repo/.agents/instructions/invalid.md"

  output="$(OKF_LINT_TEST_PLATFORM=windows run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") 'Run: python scripts/lint-okf.py' \
    "Expected deterministic Windows test mode to use the Windows rerun command."
}

test_vendor_and_invalid_linter_shapes_become_okf900() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  rm -rf -- "$repo/scripts/vendor/yaml"
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") 'OKF900' \
    "Expected a missing vendored YAML dependency to become OKF900."

  create_fixture_repo "$repo"
  write_fake_linter "$repo" 'import json, sys; print(json.dumps({"schema_version": 2, "diagnostics": []})); sys.exit(1)'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") 'OKF900' \
    "Expected an unsupported linter schema to become OKF900."

  write_fake_linter "$repo" 'import json; print(json.dumps({"schema_version": 1, "diagnostics": [], "extra": True}))'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  jq -e '.decision == "deny" and (.reason | contains("OKF900"))' <<<"$output" >/dev/null

  write_fake_linter "$repo" 'import json, sys; print(json.dumps({"schema_version": 1, "diagnostics": [{"id": "BAD", "path": "bad.md", "line": 1, "column": 1, "message": "bad id"}]})); sys.exit(1)'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") 'OKF900' \
    "Expected an invalid linter diagnostic ID to become OKF900."

  write_fake_linter "$repo" 'import json, sys; print(json.dumps({"schema_version": 1, "diagnostics": [{"id": "OKF002", "path": "bad.md", "line": 1, "column": 1, "message": "extra key", "extra": True}]})); sys.exit(1)'
  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  jq -e '.decision == "deny" and (.reason | contains("OKF900"))' <<<"$output" >/dev/null
}

test_same_key_diagnostics_preserve_central_order() {
  local workdir repo output reason second first

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  write_fake_linter "$repo" 'import json, sys; print(json.dumps({"schema_version": 1, "diagnostics": [{"id": "OKF002", "path": "same.md", "line": 1, "column": 1, "message": "second from central"}, {"id": "OKF002", "path": "same.md", "line": 1, "column": 1, "message": "first alphabetically"}]})); sys.exit(1)'

  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  reason="$(jq -r '.reason' <<<"$output")"
  second="$(grep -n 'second from central' <<<"$reason" | cut -d: -f1)"
  first="$(grep -n 'first alphabetically' <<<"$reason" | cut -d: -f1)"
  if (( second >= first )); then
    echo "Expected same-key diagnostics to retain central JSON order." >&2
    exit 1
  fi
}

test_large_diagnostics_keep_json_below_8kib() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  write_fake_linter "$repo" 'import json, sys; print(json.dumps({"schema_version": 1, "diagnostics": [{"id": "OKF002", "path": "large.md", "line": 1, "column": 1, "message": "x" * 10000}]})); sys.exit(1)'

  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$output") 'OKF002' \
    "Expected the bounded reason to retain the first diagnostic."
  if (( $(printf '%s' "$output" | wc -c | tr -d ' ') >= 8192 )); then
    echo "Expected large diagnostic output to remain below 8 KiB." >&2
    exit 1
  fi
}

test_escape_heavy_diagnostics_keep_serialized_json_below_8kib() {
  local workdir repo output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  write_fake_linter "$repo" 'import json, sys; message = "\"\\\t" * 4000; print(json.dumps({"schema_version": 1, "diagnostics": [{"id": "OKF002", "path": "escaped.md", "line": 1, "column": 1, "message": message}]})); sys.exit(1)'

  output="$(run_adapter "$repo" '{"hook_event_name":"AfterTool","cwd":"'"$repo"'"}')"
  jq -e '.decision == "deny" and (.reason | contains("OKF002"))' <<<"$output" >/dev/null
  if (( $(printf '%s' "$output" | wc -c | tr -d ' ') >= 8192 )); then
    echo "Expected the exact escaped Gemini response to remain below 8 KiB." >&2
    exit 1
  fi
}

test_simultaneous_pending_ingest_and_okf_keep_both_reasons() {
  local workdir repo source_output okf_output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf -- "'"$workdir"'"' RETURN
  repo="$workdir/repo"
  create_fixture_repo "$repo"
  mkdir -p "$repo/.agents/sources"
  printf '# pending\n' > "$repo/.agents/sources/pending.md"
  printf '# invalid\n' > "$repo/.agents/memory/invalid.md"

  source_output="$(AUDIT_LOG="$workdir/audit.log" python3 "$REPO_ROOT/.gemini/hooks/scripts/inject-auto-ingest-context.py" <<<'{"hook_event_name":"AfterAgent","cwd":"'"$repo"'"}')"
  okf_output="$(run_adapter "$repo" '{"hook_event_name":"AfterAgent","cwd":"'"$repo"'"}')"
  assert_file_contains <(jq -r '.reason' <<<"$source_output") 'Pending ingest blocks normal work.' \
    "Expected the real source-ingest helper to report pending ingestion."
  assert_file_contains <(jq -r '.reason' <<<"$okf_output") 'OKF002' \
    "Expected the OKF adapter to retain its independent finding."
}

main() {
  test_clean_events_return_empty_json
  test_payload_cwd_stays_within_adapter_checkout
  test_invalid_after_tool_matches_central_diagnostics
  test_after_agent_retry_is_bounded
  test_malformed_payload_and_linter_failures_are_okf900_blocks
  test_invalid_linter_json_exit_two_and_timeout_are_okf900
  test_truncates_sorted_diagnostics_and_keeps_rerun_command
  test_windows_rerun_command_uses_python
  test_vendor_and_invalid_linter_shapes_become_okf900
  test_same_key_diagnostics_preserve_central_order
  test_large_diagnostics_keep_json_below_8kib
  test_escape_heavy_diagnostics_keep_serialized_json_below_8kib
  test_simultaneous_pending_ingest_and_okf_keep_both_reasons
}

main "$@"
