#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_rtk_hook() {
  local payload="$1"

  bash "$REPO_ROOT/.gemini/hooks/scripts/rtk-hook-gemini.sh" <<<"$payload"
}

test_invalid_json_degrades_to_noop_json() {
  local output

  output="$(run_rtk_hook 'not-json')"

  assert_equals "{}" "$output" \
    "Expected invalid-input RTK hook to degrade to a no-op JSON response."
}

test_failed_rtk_rewrite_degrades_to_noop_json() {
  local workdir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash\nexit 23'

  output="$(
    with_mock_bin_path "$workdir" run_rtk_hook \
      '{"session_id":"rtk-fail","timestamp":"2026-06-24T23:55:00Z","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo ok"}}'
  )"

  assert_equals "{}" "$output" \
    "Expected RTK rewrite failures to leave the original Gemini tool input unchanged."
}

test_gemini_settings_register_rtk_rewrite_hook() {
  assert_equals '$HOME/.gemini/hooks/scripts/rtk-hook-gemini.sh' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "run_shell_command") | .hooks[0].command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to register rtk-hook-gemini.sh for run_shell_command rewrites."
}

main() {
  test_invalid_json_degrades_to_noop_json
  test_failed_rtk_rewrite_degrades_to_noop_json
  test_gemini_settings_register_rtk_rewrite_hook
}

main "$@"
