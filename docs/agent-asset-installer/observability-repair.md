# Aggregate observability repair

The aggregate reported `Error: stepping, database is locked (5)` in `scripts/test-gemini-hooks-observability.sh`. This private repair worktree owns Gemini observability fixture isolation and the related operational shell capture-state isolation. Runtime capture behavior, generated sources, and provider outputs remain unchanged.

The original unmodified aggregate fixture failure remained intermittent: one initial full suite, five further full suite repetitions, and eight installed persistence/finalization pairs passed before the change. A separate installed-boundary stress case reproduced the identical error conclusively. Copied provider-local Gemini scripts used a disposable explicit trace path and 100,000 expired session rows; removing the sentinel and invoking the public `SessionStart` entrypoint launched real maintenance. The tenth concurrent raw SQLite write failed with exit 5 and `Error: stepping, database is locked (5)` while maintenance pruned the backlog. Bash traces show that unrelated SQLite fixtures launch detached maintenance and immediately replace or mutate the same WAL database using zero-timeout SQLite commands. These fixtures also use historical timestamps beyond retention windows. A fresh maintenance sentinel now prevents this unintended worker in both providers through `install_observability_test_home` in `scripts/test-common.sh`. Explicit detached-maintenance sections still remove it and validate startup, retention, rate limiting, and scavenging. Their eight fixture INSERTs use a bounded 5-second SQLite client wait because the sentinel marks child startup, not completion; permanent lock failures still fail the suite.

A separate public reproduction conclusively identified state leakage. Running the original Gemini RTK suite with both provider log paths pointed at disposable caller-owned paths returned success but created the caller's database, WAL, SHM, locks, and transcripts. The absence of these paths was the failing assertion. Without overrides the same subprocesses inherited real-home trace destinations, explaining aggregate `attempt to write a readonly database` diagnostics under the sandbox.

`setup_hook_observability_test_state` in `scripts/test-common.sh` now creates a unique temporary trace root, exports both provider-specific log paths, seeds maintenance sentinels, and uses a named exit cleanup. Twelve operational shell suites opt in before any hook execution. Capture stays enabled. Embedded Python subprocesses inherit the isolated overrides. Both RTK suites add real wrapper capture assertions with a subprocess mock at the existing external RTK command boundary.

All twelve operational shell suites and both provider observability suites passed with syntax validation and no database diagnostics. The final two observability suites passed again after the shared helper and bounded-client changes, with no database errors. The caller-path public reproduction passes for both providers with inherited paths untouched and no database errors. Installed stress validation has three outcomes: original detached-maintenance race reproduces the exact lock error; fresh sentinel permits 100 zero-wait writes and preserves all 100,000 fixture rows; deliberate maintenance with the bounded SQLite client permits 100 writes and removes all expired rows. Scoped canonical documentation, OKF lint, and whitespace checks pass. No assertions were deleted, disabled, skipped, or weakened. Generator validation is unnecessary because no generated/canonical runtime source changed.

The parent manages `docs/agent-asset-installer/ExecPlan.md`, independent review, integration, and the final aggregate rerun. This branch remains private and unpushed; no real home or client installation was performed.

Five-axis self-review found no required changes: capture remains enabled, provider-specific paths reach raw subprocesses, cleanup targets only an exact unique temporary root, helper logic stays in shell test support, and bounded waits apply only where a real concurrent maintenance writer is intentional. Independent parent review and the full aggregate rerun remain required before integration.

The exact passing suite commands were:

- `bash scripts/test-hooks-rtk.sh`
- `bash scripts/test-hooks-startup.sh`
- `bash scripts/test-hooks-tool-guard.sh`
- `bash scripts/test-hooks-secrets-scanner.sh`
- `bash scripts/test-hooks-auto-ingest.sh`
- `bash scripts/test-hooks-okf-lint.sh`
- `bash scripts/test-hooks-observability.sh`
- `bash scripts/test-gemini-hooks-rtk.sh`
- `bash scripts/test-gemini-hooks-startup.sh`
- `bash scripts/test-gemini-hooks-tool-guard.sh`
- `bash scripts/test-gemini-hooks-secrets-scanner.sh`
- `bash scripts/test-gemini-hooks-auto-ingest.sh`
- `bash scripts/test-gemini-hooks-okf-lint.sh`
- `bash scripts/test-gemini-hooks-observability.sh`
