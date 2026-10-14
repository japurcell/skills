# V1 Phase 1 checkpoint, not release acceptance

Observed on 2026-10-14 in the exclusive verification worktree, private branch `codex/hook-resilience-v1`, frozen candidate `ec73604420201c20734a83aa39e32df5a05e0687`. No product or maintained test source was edited. The coordinator owns active-plan changes, repairs, and the final coordinated KB pass. Phase 2 release timing has not run and is not authorized at this checkpoint. V1 remains incomplete.

## Environment and procedure

Host: native macOS/Darwin 25.6.0, arm64; Python 3.14.6; PowerShell 7.6.6; RTK 0.51.0. The aggregate ran through approved native execution because the adapter's separate native macOS RSS mechanics are known to fail in the sandbox with `time: sysctl kern.clockrate: Operation not permitted`. Passing those inert adapter mechanics does not establish product resource acceptance.

The exact maintained command was `rtk proxy python3 scripts/test-all.py`, run serially through an external output-capture wrapper. All 51 registered suites ran; none were removed or weakened. The wrapper redirected HOME, CODEX_HOME, XDG config/data/cache homes and bytecode cache to disposable state. It set `OBSERVABILITY_TESTING=1`, generic/provider-specific observability paths and AUDIT_LOG to disposable paths. Provider Guardian fallback logs therefore also remained beneath disposable HOME. No live-home install, authenticated provider dispatch, or native Windows execution occurred.

`rtk proxy python3 scripts/generate-hooks.py --check` passed all 38 outputs before and after the aggregate. Git status was clean on the frozen candidate before and after. No code-generation write ran during the aggregate or generator checkout-snapshot suite. Reviewer/probe work in separate worktrees was concurrent; the elapsed times below are functional suite durations, not isolated performance evidence.

## Aggregate result and exact durations

The runner reported **46 successful suite processes, 5 failed, 879.5 seconds** (external wrapper wall duration 879.984 seconds). Three successful processes were explicit native Windows skips: **43 exercised suite successes, 5 failures, 3 platform skips**. The macOS PowerShell installer passed with its unsupported junction creation subcheck skipped. The Codex PowerShell scanner envelope script has no non-Windows guard and actually ran here; its failure must not be called a platform skip.

| # | Maintained command | Observed status | Seconds |
| --- | --- | --- | ---: |
| 1 | `bash scripts/test-addy-install.sh` | PASS | 1.281 |
| 2 | `bash scripts/test-cleanup-skill-workspaces.sh` | PASS | 1.077 |
| 3 | `bash scripts/test-codex-hooks-startup.sh` | PASS | 6.214 |
| 4 | `bash scripts/test-codex-repository-okf.sh` | PASS | 0.846 |
| 5 | `bash scripts/test-codex-hooks-secrets-scanner.sh` | PASS | 52.778 |
| 6 | `bash scripts/test-gemini-hooks-auto-ingest.sh` | PASS | 12.707 |
| 7 | `bash scripts/test-gemini-hooks-observability.sh` | FAIL | 22.033 |
| 8 | `bash scripts/test-gemini-hooks-okf-lint.sh` | FAIL | 1.004 |
| 9 | `bash scripts/test-gemini-hooks-rtk.sh` | PASS | 4.881 |
| 10 | `bash scripts/test-gemini-hooks-secrets-scanner.sh` | PASS | 67.898 |
| 11 | `bash scripts/test-gemini-hooks-startup.sh` | PASS | 0.325 |
| 12 | `bash scripts/test-gemini-hooks-tool-guard.sh` | PASS | 2.025 |
| 13 | `bash scripts/test-hooks-auto-ingest.sh` | PASS | 1.290 |
| 14 | `bash scripts/test-hooks-observability.sh` | PASS | 31.836 |
| 15 | `bash scripts/test-hooks-okf-lint.sh` | PASS | 14.487 |
| 16 | `bash scripts/test-hooks-rtk.sh` | PASS | 5.367 |
| 17 | `bash scripts/test-hooks-secrets-scanner.sh` | PASS | 73.620 |
| 18 | `bash scripts/test-hooks-startup.sh` | PASS | 0.622 |
| 19 | `bash scripts/test-hooks-tool-guard.sh` | PASS | 1.834 |
| 20 | `bash scripts/test-codex-hooks-tool-guard.sh` | PASS | 7.335 |
| 21 | `python3 scripts/test-codex-agents.py` | PASS | 1.358 |
| 22 | `python3 scripts/test-install-codex-hooks.py` | PASS | 0.180 |
| 23 | `python3 scripts/test-probe-provider-hook-delivery.py` | PASS | 4.569 |
| 24 | `python3 scripts/test-generate-hooks.py` | PASS | 18.944 |
| 25 | `python3 scripts/test-rtk-stable.py` | PASS | 9.187 |
| 26 | `python3 scripts/test-security-banners.py` | PASS | 7.515 |
| 27 | `python3 scripts/test-security-reporting.py` | PASS | 27.204 |
| 28 | `python3 scripts/test-hook-input-bounds.py` | PASS | 32.431 |
| 29 | `python3 scripts/test-hook-diagnostics.py` | PASS | 1.958 |
| 30 | `python3 scripts/test-hook-diagnostic-recovery.py` | PASS | 10.384 |
| 31 | `python3 scripts/test-scan-secrets-merge.py` | FAIL | 201.178 |
| 32 | `python3 scripts/test-scan-secrets-stream-component.py` | PASS | 0.198 |
| 33 | `python3 scripts/test-scan-secrets-streaming.py` | PASS | 39.191 |
| 34 | `python3 scripts/test-tool-guard-false-positives.py` | PASS | 3.866 |
| 35 | `python3 scripts/test-tool-guard-native-data.py` | PASS | 12.229 |
| 36 | `python3 scripts/test-tool-guard-shell-data.py` | PASS | 27.418 |
| 37 | `python3 scripts/test-tool-guard-limits.py` | PASS | 10.675 |
| 38 | `python3 scripts/test-benchmark-high-rate-hooks.py` | PASS | 15.772 |
| 39 | `python3 scripts/test-verify-hook-release.py` | PASS | 2.053 |
| 40 | `pwsh -NoProfile -File scripts/test-install.ps1` | PASS; junction check skipped | 80.995 |
| 41 | `pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1` | FAIL | 0.979 |
| 42 | `pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1` | SKIP (process exit 0) | 0.251 |
| 43 | `pwsh -NoProfile -File scripts/test-repository-okf-windows.ps1` | SKIP (process exit 0) | 0.233 |
| 44 | `pwsh -NoProfile -File scripts/test-lifecycle-messages-windows.ps1` | SKIP (process exit 0) | 0.218 |
| 45 | `bash scripts/test-install.sh` | PASS | 32.078 |
| 46 | `bash scripts/test-okf-lint.sh` | PASS | 11.899 |
| 47 | `bash scripts/test-repo-root.sh` | PASS | 0.073 |
| 48 | `python3 scripts/test_helpers.py` | FAIL | 0.560 |
| 49 | `python3 skills/spec-to-tasks/evals/test_grade_benchmark.py` | PASS | 4.910 |
| 50 | `python3 skills/prd-ralph-loop/evals/test_grade_benchmark.py` | PASS | 0.754 |
| 51 | `python3 scripts/test_test_all.py` | PASS | 10.737 |

## Preserved failures and follow-up

1. **Gemini observability:** original exit 5 in 22.033 seconds, `Error: stepping, database is locked (5)`. An exact unchanged public-suite repeat with clean audit environment failed exit 1 in 16.855 seconds during fixture cleanup (`rm: .../.gemini/hooks: Directory not empty`). This is real fixture flakiness, not resolved by the later passing trace. The cleanup survivor had `.maintenance_last_run` plus SQLite database/WAL/SHM files; a read-only query returned zero sessions and zero spans. That is consistent with detached maintenance in a FORCE_NDJSON fixture. It does not identify the original SQLite statement. Shared nonmaintenance rotation fixtures in `scripts/observability-test-support.sh` around lines 139-498 lack the sentinel used by the later fail-open rotation fixture. The bounded next task is to reproduce and identify the exact race, use the established fresh-sentinel rule for fixtures unrelated to maintenance, preserve intentional maintenance coverage, and rerun both provider observability suites. Do not assume provider-local adversarial line 368 was the failing statement.
2. **Gemini OKF:** original exit 1 in 1.004 seconds because the verifier's global AUDIT_LOG took precedence over the fixture's `${AUDIT_LOG:-$repo/audit.log}`, while its assertion read `$repo/audit.log`. With AUDIT_LOG unset and disposable HOME/logging paths, the exact public suite passed in 11.155 seconds. This is confirmed verifier environment interference; no fixture or product source changed.
3. **Merge scanner:** exit 1, 33 tests in 201.123 seconds, 36 subtest failures from three path-presentation cases across all providers, block/warn and diff/staged modes. Findings, pattern and enforcement were present, but the shared assertion expected raw newline/tab or long names after T6 had sanitized/capped labels. Affected cases are `test_pre_238_git_allows_clean_index_and_detects_staged_secret`, `test_batch_paths_preserve_newlines_tabs_and_colons`, and `test_batch_long_paths_fit_bounded_git_command_lines`; shared assertion is `scripts/test-scan-secrets-merge.py:159-161`. The coordinator assigned a bounded presentation-contract repair retaining acquisition/path-separation, exact secret pattern/line, provider/scope and decoy proof. Original 36 failures remain in the complete log.
4. **Codex PowerShell envelope:** exit 1 in 0.979 seconds, `scripts/test-codex-hooks-windows.ps1:36` expects the old complete warning string without T6's attribution suffix. Repair must preserve deny/block/warn/clean and redaction proof. Native Windows behavior remains unverified even after portable PowerShell coverage is repaired on macOS.
5. **Shared helpers:** exit 1, 16 tests in 0.478 seconds; Gemini maintenance hit duplicate `sessions.session_id`, with an unclosed SQLite ResourceWarning on the failed path. The verifier's provider-specific log paths overrode the fixture's generic temporary path, and both provider log files shared one parent database directory. With provider-specific overrides unset, AUDIT_LOG unset, disposable HOME and a disposable generic observability path, all 16 tests passed in 0.751 seconds. This is confirmed verifier environment interference. Future aggregate invocation must omit those conflicting global overrides while preserving a disposable HOME and writable generic observability path; individual suites own their fixture paths.

## Diagnostic attempts and their limits

A complete `bash -x scripts/test-gemini-hooks-observability.sh` run passed in 40.106 seconds and is retained as diagnostic context only. It cannot erase either uninstrumented failure or establish that the race is fixed.

Two unsuccessful instrumentation attempts are explicitly invalid product evidence: an initial PS4 used `FUNCNAME[0]` under nounset and failed before tests; a later external DEBUG trap enabled Bash functrace, which also inherited existing RETURN cleanup traps and deleted a fixture HOME during installation. Their logs are retained and labeled invalid. Neither changes any suite outcome above. No further fixture diagnostic or source repair was performed by V1.

## Installation and remaining acceptance

Historical aggregate Bash installer and macOS PowerShell installer checks passed against this frozen candidate, including their maintained asset/preservation fixtures. An additional actual full-installer byte/mode/registration proof was prepared only as disposable verification code and **not executed**: the coordinator deferred it until the required T7 isolated-launch registration repair is integrated. No installed-asset acceptance is claimed for that future registration state.

Required next actions: integrate T6/T7 and test-contract/race repairs through coordinator ownership; update this private branch through coordinated rebase; rerun checks affected by changed source and these failures with corrected verifier environment; run the deferred isolated installed-owned-assets/fingerprint/user-registration proof; then wait for explicit coordinator authorization before Phase 2. All review probes and all tests/generation/benchmarks must have stopped before release timing. The planned baseline is `bc52d7d69aaa046ea97e323879402241a01fead7` with V0's explicit actual expectation map.

No latency budget, 500 ms finite resource gate, authenticated provider delivery, junction-specific Windows behavior, or native Windows suite is accepted by this checkpoint. This checkpoint is committed as historical functional evidence only. V1 remains incomplete and the same verification task resumes after repair integration. The commit does not authorize Phase 2.

## Retained artifacts

Complete aggregate output, timestamped output, original suite statuses/durations, exact repeats and diagnostic attempts are retained alongside this document. Large logs are losslessly gzip-compressed; `gzip -dc PATH` reads them. Only known user/worktree/temporary path prefixes were replaced with neutral placeholders. Fake fixture credentials remain fake fixture data. The artifact manifest records original-byte hashes plus redacted and stored-byte hashes so path redaction is explicit. Original unredacted logs remain in verifier-owned disposable state pending final retention/cleanup.

- [V1-phase1-aggregate.log.gz](V1-phase1-aggregate.log.gz)
- [V1-phase1-aggregate-timestamped.jsonl.gz](V1-phase1-aggregate-timestamped.jsonl.gz)
- [V1-phase1-aggregate-summary.json](V1-phase1-aggregate-summary.json)
- [V1-phase1-repeats-summary.json](V1-phase1-repeats-summary.json)
- [V1-phase1-gemini-okf-repeat.log.gz](V1-phase1-gemini-okf-repeat.log.gz)
- [V1-phase1-gemini-observability-repeat.log.gz](V1-phase1-gemini-observability-repeat.log.gz)
- [V1-phase1-helpers-repeat.log.gz](V1-phase1-helpers-repeat.log.gz)
- [V1-phase1-diagnosis-summary.json](V1-phase1-diagnosis-summary.json)
- [V1-phase1-invalid-trace-prefix.log.gz](V1-phase1-invalid-trace-prefix.log.gz)
- [V1-phase1-observability-xtrace-summary.json](V1-phase1-observability-xtrace-summary.json)
- [V1-phase1-observability-xtrace.log.gz](V1-phase1-observability-xtrace.log.gz)
- [V1-phase1-invalid-debug-summary.json](V1-phase1-invalid-debug-summary.json)
- [V1-phase1-invalid-debug.log.gz](V1-phase1-invalid-debug.log.gz)
