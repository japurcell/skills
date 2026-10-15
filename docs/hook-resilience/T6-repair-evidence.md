# T6 repair: credential-bearing identifier labels

R1 standards and spec reviews reopened the original T6 implementation because
Guardian's ASCII identifier shortcut checked only the beginning of a label.
The repair starts at `e3103d74` in the exclusive
`/Users/adam/.codex/worktrees/hook-report-label-repair/skills` worktree on private
branch `codex/hook-resilience-t6-repair`. The original review and
[initial T6 evidence](T6-evidence.md) remain unchanged.

## Public red and repair

Before changing canonical source, the maintained public reporting suite added a
regression with nine labels across all three generated provider entrypoints:
prefixed fine-grained GitHub, classic GitHub, Stripe and AWS fake token forms;
credential prefixes starting at positions 150, 157, 160 and 200; and full-width
Unicode characters that normalize to a prefixed classic GitHub fake token. Every
label is exercised for a denied dangerous command, a warned dangerous command,
and a clean allowed command's audit log. Fixtures use disposable repositories,
homes and logs, isolated Python with `-I -S -B`, `OBSERVABILITY_TESTING=1`, fake
credentials, and cleared inherited skip/allowlist overrides.

Command from the worktree root:

`rtk proxy python3 scripts/test-security-reporting.py SecurityReportingTests.test_guardian_embedded_token_labels_are_safe_for_denials_warnings_and_clean_logs > /tmp/t6-repair-red.log 2>&1`

Observed before repair: exit 1, one test with **81 failing subtests**. The public
native output and guard log contained complete prefixed fake tokens. Clipping
cases also failed the conservative whole-label redaction check. The retained red log is disposable;
the committed regression and starting revision make the failure reproducible.

The canonical change is confined to `sanitize_tool_name` in
`hooks/families/tool_guard.py`. ASCII identifiers now call the existing shared
`report_label` primitive, which checks the complete bounded normalized label
before clipping. Credential-bearing identifiers become `[REDACTED]`, including
credentials after other identifier components or beyond the display boundary.
The incorrect starts-with blacklist and its word-boundary assumption are gone.
Known safe identifiers retain their display and 160-character clipping. Existing
spaced/punctuation label presentation retains its established redaction path.
No second credential detector or runtime dependency was introduced.

The second new public test independently asserts presentation for safe custom
identifiers and long safe names, and checks known provider shell fields keep
`shell_v1`/`native` classification and allow decisions. The hostile-label test
asserts native decisions as well as audit enforcement, strict fallback, absence
of credentials/markers, safe rule causes, and the existing 16 KiB encoded record
ceiling. Existing assertions were not removed or weakened.

## Verification

All commands below ran from the exclusive repair worktree root. These are
functional observations, not performance acceptance. Generator verification runs
alone after all other test processes finish and with all files frozen.

| Command | Observed result |
| --- | --- |
| `rtk proxy python3 scripts/test-security-reporting.py SecurityReportingTests.test_guardian_embedded_token_labels_are_safe_for_denials_warnings_and_clean_logs SecurityReportingTests.test_guardian_safe_identifiers_and_known_native_fields_keep_presentation` | 2 tests pass after repair |
| `rtk proxy python3 scripts/test-security-reporting.py` | 11 tests pass |
| `rtk proxy python3 scripts/test-security-banners.py` | 14 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-native-data.py` | 26 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-shell-data.py` | 17 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-limits.py` | 18 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-false-positives.py` | 153 fixtures pass |
| `rtk proxy env OBSERVABILITY_LOG_PATH=/tmp/t6-repair-copilot-guard-obs.jsonl OBSERVABILITY_TESTING=1 bash scripts/test-hooks-tool-guard.sh` | pass |
| `rtk proxy env OBSERVABILITY_LOG_PATH=/tmp/t6-repair-gemini-guard-obs.jsonl OBSERVABILITY_TESTING=1 bash scripts/test-gemini-hooks-tool-guard.sh` | pass |
| `rtk proxy bash scripts/test-codex-hooks-tool-guard.sh` | pass, including banners14 |
| `rtk proxy python3 scripts/test-generate-hooks.py` | isolated 26 tests pass in 19.153 seconds |
| `rtk proxy python3 scripts/generate-hooks.py --check` | all 38 outputs current |
| `rtk git diff --check` | pass |

Generated outputs were refreshed with
`rtk proxy python3 scripts/generate-hooks.py --write`. Guardian adapters and local
policy helpers change directly; scanner and standalone diagnostics outputs change
only for their compiled expected Guardian/build identities. Scanner acquisition,
matching, report limits and allowlist policy are unchanged, so scanner merge33
was not repeated. The full reporting suite still exercises affected scanner
reporting paths. No benchmark, live installation, push, KB update or active-plan
change was performed. T7 owns installer and diagnostic-registration changes in a
separate worktree; combined generated identities must be regenerated during
serialized integration if those canonical inputs change.
