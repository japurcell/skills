# Integrated hook validation

Verified on macOS on 2026-10-08. Initial review baseline is `72789d6978bb7255583f9fb1cd8e18c37fe3173b`. Scanner implementation integrated as `f158f66471b3ef04f5105000f1ab77ccda546a89`; Guardian implementation integrated as `f0cca423acb598e2a3ee582d44e2de8cc49ee842`.

## Source and integration proof

Both task branches rebased without conflicts. Scoped `git diff` comparisons against the tested pre-rebase commits were empty for their respective source and tests. Their focused results in [Guardian result](guardian-result.md) and [scanner result](scanner-result.md) therefore remain applicable. The generated freshness gate passed after the combined source was assembled.

Additional checks on integrated source all passed:

- `rtk proxy bash scripts/test-hooks-tool-guard.sh` and `rtk proxy bash scripts/test-gemini-hooks-tool-guard.sh`.
- `rtk proxy bash scripts/test-codex-hooks-tool-guard.sh`: 14 tests.
- `rtk proxy python3 scripts/test-security-banners.py`: 14 tests, including public response and guard-log parity.
- `rtk proxy python3 scripts/test-generate-hooks.py`: 26 tests; the checkout remained frozen during its snapshot checks.
- `rtk proxy bash scripts/test-install.sh`: disposable-home installation, preservation, and freshness fixtures.
- `rtk proxy python3 scripts/test-benchmark-high-rate-hooks.py`: two tests.
- `rtk proxy git diff --check`.

Provider suites received separate writable temporary `OBSERVABILITY_LOG_PATH` values and `OBSERVABILITY_TESTING=1`. No real installed hook log was used for these checks.

Three independent, bounded Python fixture probes invoked the actual generated Guardian and scanner subprocesses through `scripts/tool_guard_test_support.py`. Each used an isolated unborn Git repository and the same provider payload for both hooks. Copilot used `toolName: apply_patch` with a raw `toolArgs` patch; Codex used its existing `tool_input.command` form.

1. A multi-file patch containing 4,000 lines of safe prose and semicolon examples passed both hooks on the same clean repository, for both providers.
2. A valid patch still passed Guardian when the repository contained an unmistakably fake recognizer fixture. The independent scanner denied with `potential secrets detected`, without the fixture value or a generic incomplete result.
3. A benign argument-free documentation request passed Guardian while an untracked 1,048,577-byte safe file caused scanner denial. The response contained `file_bytes_limit/candidate_read` and the actual/limit byte counts, without the temporary repository path.

The first combined inline probe exceeded the existing command-token limit before execution. It created no fixture and supplied no acceptance evidence. The three smaller independent scenarios above each fit the unchanged executable budget and passed. No hook was disabled.

## Bounded resource proof

The maintained resource command ran serially against frozen hook source, after functional suites completed:

```sh
rtk proxy env OBSERVABILITY_LOG_PATH=/private/tmp/hook-resources-observability.ndjson python3 scripts/benchmark-tool-guard-resources.py --output /private/tmp/hook-input-resources.json --ceiling-ms 500
```

The sandbox initially denied the native collector's `sysctl kern.clockrate`. Approved native collection then succeeded. The JSON artifact retains source fingerprints, 25 measured samples and three warmups per case, a first-process observation, medians/p95/MAD, and separate native RSS measurements.

All 108 cases returned the expected decision and met the 500 ms finite-case ceiling. The maximum observed sample was 58.826750 ms; maximum p95 was 58.743916 ms. Maximum measured RSS was 23,494,656 bytes. The slowest case was Copilot's 256 KiB high-line-count patch, with median 57.312584 ms. This establishes the tested finite input bounds, not a universal raw-JSON memory bound, a latency improvement over baseline, or provider delivery timing.

## Installed verification

Read-only installed configuration preflights passed for RTK and all three provider mergers. After disposable-home installer fixtures passed, approved `rtk proxy bash scripts/install.sh` completed successfully. Byte comparisons confirm all nine changed installed hook/helper files match source: Guardian entrypoint, Guardian policy helper, and scanner for Copilot, Gemini, and Codex.

Direct installed-script probes used isolated unborn repositories, disposable homes/logs, and `OBSERVABILITY_TESTING=1`:

- Copilot's raw-string and Codex's existing object native patch shapes both allow a multi-file patch with 4,000 prose/semicolon lines above the former 64 KiB bound.
- Both Guardian providers deny a late protected-file deletion in a large patch, leaving the sentinel file unchanged.
- All three scanners explicitly deny a 1,048,577-byte safe candidate and expose `file_bytes_limit/candidate_read`, with actual/limit byte counts and no repository path.
- All three scanners explicitly deny a definite fake-secret fixture as findings, without the fixture value or a generic incomplete result.

These are installed subprocess results, not authenticated provider-dispatch evidence.

## Review and remaining limits

Independent [Standards and Spec reports](review.md) are complete. Standards found one active-plan documentation issue and verified its repair. Spec found zero issues. No finding remains open. The final generated freshness check passed for all 35 files; local artifact links resolved and diff checks passed.

Authenticated Copilot pre-tool delivery could not be tested because existing authentication was unavailable. Native Windows was not exercised. The original external Linux scanner cause remains unknown; typed diagnostics expose future incomplete causes while preserving the existing denial contract.

Both clean integrated task worktrees remain attached because the app rejected archival as protected by a pinned task or workspace. Their integrated branches are retained. No filesystem cleanup bypass or push was performed.

## Knowledge-maintenance pass

One coordinated `update-agent-docs` pass followed all delegated work. Current hook/security/testing routes and scanner consistency memory were cross-checked against the final diff and retained results. Exact provider shapes, budgets, and diagnostic vocabulary are readily discoverable in canonical source and tests; current guidance already routes those owners. No new durable rule, non-obvious memory, stale obligation, or policy conflict warranted KB edits. Canonical KB files and indexes remain unchanged; OKF lint was not required.

```text
Added: None
Changed: None
Split or moved: None
Deduplicated: None
Index updates: None
Remaining doc quality TODOs: None
```
