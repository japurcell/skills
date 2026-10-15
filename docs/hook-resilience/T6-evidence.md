# T6 bounded security reporting evidence

T6 was implemented on private branch `codex/hook-resilience-t6` in
`/Users/adam/.codex/worktrees/hook-bounded-reports/skills`, starting at `b12005f8`.
The coordinator owns the active implementation plan, registry and final KB pass.
No live installation, provider dispatch, benchmark, or push was performed.

## Observable behavior and bounds

The generated Copilot, Gemini and Codex scanner entrypoints retain no more than
100 finding details from 1,000 processed findings. Display paths are sanitized
when entering the retained finding model, before JSON serialization. Printable
ASCII labels have a 160-character cap, token-shaped labels are replaced, control
characters are removed, and timestamps come from the hook. An exact JSON byte
cost calculation reserves structural metadata and selects optional environment
path labels before serialization. Records, including JSON escaping and newline,
remain at most 65,536 bytes. Omitted finding and environment-path counts remain
explicit. An existing positive finding survives audit failure or a later unsafe
candidate; inspection completeness, security, audit and enforcement are separate.

Guardian records retain safe rule metadata and a bounded excerpt, with a 16,384
byte ceiling including adapter overhead reserve. Existing strict classification
and exact allowlist decisions remain intact. Unsupported/malformed profiles carry
`profile=unsupported`, `route=strict_fallback` and fixed classification causes;
unknown names, keys and bodies are not echoed. Native input uses its recognized
profile. Early invalid JSON/non-object/read failures have safe fixed attribution,
deny, and explicitly report `audit_outcome=not_attempted`. Policy-helper bootstrap
failure also has fixed attribution when the implementation has loaded.

Build IDs are compiled at generation from trusted canonical sources plus
provider/manifest inputs. Runtime hooks do no source hashing and gain no installed
helper dependency: the small reporting primitives are embedded. Guardian's shared
policy helper stays byte-identical across providers. The existing diagnostics
collector remains separate, avoiding recursive rendering dependencies.

## Red observations retained

`rtk proxy python3 scripts/test-security-reporting.py` initially failed all three
new public tests. A fake secret plus 70,000-character session/timestamp metadata
created a 140,305-byte record and returned only `log_record_limit`/incomplete,
losing the known finding. Token-shaped paths/session/timestamps and a Guardian
tool label leaked `github_pat_` fake labels and an escaped terminal control.
All fixtures used disposable repositories/homes/logs, fake credentials,
`OBSERVABILITY_TESTING=1`, and generated JSON entrypoints.

The audit-failure slice exposed Copilot and Codex Guardian ignoring the audit
helper's `False` result: native messages claimed `audit_outcome=written` when the
log destination was a directory. The repaired adapters check the result and keep
the finding in the native denial/warning. The first expansion also had eight
fixture errors from unlinking a previously-created directory; the fixture was
corrected before evaluating behavior. Public later-unsafe-candidate cases prove
retention of an earlier real finding in both scanner modes.

The early-input slice failed six provider/input cases before repair:
`rtk proxy python3 scripts/test-security-reporting.py SecurityReportingTests.test_guardian_invalid_transport_and_nonobject_have_safe_attribution`.
The old native denials lacked all attribution and audit status. The same command
then passed after fixed attribution was added.

The first generator run failed three assertions: two expected oversized session
metadata to throw rather than produce a bounded record, and one caught a provider
literal outside an explicit adapter. Fixtures now assert bounded records and safe
session clipping; the provider value reuses the collector's explicit adapter.
Provider shell fixtures also required the new full native attribution suffix and
sanitized display of a newline-bearing Git path. Detection of that path remains
asserted at line one. Streaming's shared exact-envelope fixture now covers both
findings plus incomplete inspection and the new attribution fields.

A concurrent generator run was invalidated by other suites writing helper
bytecode during its whole-root snapshots. It became CPU-bound computing a giant
dictionary diff; interrupting the owned test showed
`test_lock_and_injected_write_failure_leave_outputs_unchanged` in `assertDictEqual`
and `difflib`, exit 130. No check was disabled. After every other test process
finished, a completely isolated rerun passed all 26 tests in 17.565 seconds.
An existing fixed five-second lock-holder fixture could expire before its second
hook call under parallel load; it now holds long enough for both bounded calls,
then the test's existing cleanup kills it. The public reporting suite independently
holds locks through each complete child invocation.

## Green commands and results

All commands ran from the isolated worktree root with `rtk` prefixes. Elapsed
times below are test observations under concurrent functional load, not timing
or resource acceptance.

| Command | Observed result |
| --- | --- |
| `rtk proxy python3 scripts/test-security-reporting.py` | 9 tests pass, including all provider/mode combinations for failure, contention, partial findings, token labels and encoded ceilings |
| `rtk proxy python3 scripts/test-security-banners.py` | 14 tests pass |
| `rtk proxy python3 scripts/test-hook-input-bounds.py` | 9 tests pass |
| `rtk proxy python3 scripts/test-scan-secrets-streaming.py` | 13 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-native-data.py` | 26 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-shell-data.py` | 17 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-limits.py` | 18 tests pass |
| `rtk proxy python3 scripts/test-tool-guard-false-positives.py` | 153 public fixtures pass |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` | 10 tests pass |
| `rtk proxy python3 scripts/test-hook-diagnostics.py` | 8 tests pass |
| `rtk proxy bash scripts/test-hooks-secrets-scanner.sh` | pass, including Copilot capture suite |
| `rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh` | pass, including Gemini capture suite |
| `rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh` | pass, including Codex capture suite |
| `rtk proxy env OBSERVABILITY_LOG_PATH=/tmp/t6-copilot-guard-obs.jsonl OBSERVABILITY_TESTING=1 bash scripts/test-hooks-tool-guard.sh` | pass |
| `rtk proxy env OBSERVABILITY_LOG_PATH=/tmp/t6-gemini-guard-obs.jsonl OBSERVABILITY_TESTING=1 bash scripts/test-gemini-hooks-tool-guard.sh` | pass |
| `rtk proxy bash scripts/test-codex-hooks-tool-guard.sh` | pass, including shared banners14 |
| `rtk proxy python3 scripts/test-generate-hooks.py` | isolated 26 tests pass |
| `rtk proxy python3 scripts/generate-hooks.py --check` | all 38 generated targets current |
| `rtk git diff --check` | pass |

An independent maintenance probe compared the pre-serialization size calculation
with `json.dumps(..., ensure_ascii=True, separators=(",", ":"))` for six boundary
values: empty text, ASCII controls and DEL, quote/backslash escaping, BMP and lone
surrogate text, an astral character, and a nested report structure. All six passed.
The permanent tests remain at the public generated-entrypoint seams.

## Limits and integration ownership

The I2 resource proof remains the coordinator's existing 24-case observation:
maximum 2.293 seconds and RSS 32.8-34.4 MB. T6 makes no universal memory/time bound
claim, and it ran no new benchmark. The large merge33 suite was not repeated:
candidate/index acquisition did not change; streaming13 and provider capture
suites cover affected reporting interactions. Native Windows, authenticated host
delivery, isolated installation/performance release gates and the final independent
review remain coordinator work. The coordinator will register the new maintained
`scripts/test-security-reporting.py` suite and perform the single final KB pass.
