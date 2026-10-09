# Scanner diagnostic implementation result

Task T4, 2026-10-08. Implementation branch: `codex/hook-scan-diagnostics`. The canonical owner is `hooks/families/scan_secrets.py`; provider entrypoints were regenerated only with `scripts/generate-hooks.py --write`.

## Observable result

Incomplete scans now retain the fixed scan action, report a typed cause and operation, attach safe numeric metadata when relevant, and give constant recovery advice. For example, a 1,048,577-byte candidate emits:

```text
scan-secrets blocked: tool scan; scan incomplete; potential secrets could not be checked. file_bytes_limit/candidate_read: candidate byte limit exceeded (measured 1048577 bytes, limit 1048576 bytes). Check pending file sizes and unintended generated artifacts.
```

Warn mode uses the same detail with `scan-secrets warning` in `systemMessage`. Block mode preserves each provider's existing denial JSON envelope. Every incomplete result exits zero. Missing Git and audit initialization failures remain action `scan`; parsed requests use the fixed tool or session-end action. No failure becomes an unconditional allow.

The cause vocabulary covers initialization, invalid input, repository inspection, Git exits/capture/descendants/HEAD/output/timeouts, snapshot count, file/total/capture/request bytes, candidate safety/read failures, secure log storage/configuration/locks/record bounds, and unexpected internal failures. Measurements name snapshots rather than unique files. Git operation labels inspect scanner-owned flags before the path separator, so a filename resembling an option cannot select a different operation label.

Incomplete scan records persist `status`, a trusted timestamp, normalized mode/scope, fixed action, constant diagnostic note, and a `diagnostic` object containing cause, operation and bounded numbers. They omit payload-derived identifiers, timestamps and repository paths. Normal clean/findings records retain their existing schema. Diagnostics never derive from exception text or include Git stderr, Git arguments, candidate names, payload text, credential values or tracebacks. If writing the incomplete record also fails, the response still reports the original cause.

Repository-wide candidate selection, staged/worktree/untracked/merge coverage, no-follow reads, recognizers, finding redaction, process cleanup and all existing scanner bounds are preserved. Negative staged sizes are now accurately diagnosed as invalid Git output rather than a byte-limit excess; an integer conversion failure in batch metadata also reports invalid output.

## Regression and verification evidence

Public entrypoint regressions were written before implementation. The initial Copilot descendant case failed because the response lacked `git_descendant_running/git_repository`. Later red/green checks reproduced and repaired three diagnostic inaccuracies: a filename resembling a Git flag, an oversized integer in Git metadata, and an unexpected stdin-reader crash. Their responses now report the correct fixed operation/cause without revealing the hostile values.

Passed source checks:

- `rtk proxy python3 scripts/generate-hooks.py --check`: all 35 generated files current.
- `rtk proxy python3 scripts/test-scan-secrets-capture.py copilot`, `gemini`, and `codex`: each provider's block/warn public cases pass. Coverage includes missing Git, audit failure, malformed input, unexpected reader/capture crashes, failed Git/HEAD, valid unborn success, command and total timeouts, descendants, malformed/oversized captures, safe/failed candidate reads, exact snapshot/file/total limits, secure-log faults, first-cause preservation, hostile strings, and findings-specific fake credentials.
- All three provider Bash scanner suites passed with disposable audit and observability paths.
- `rtk proxy python3 scripts/test-scan-secrets-merge.py`: 32 tests passed across all providers. After strengthening cause assertions, four targeted merge safety/file/total tests passed; the expanded corrupt batch metadata test also passed across all providers, including the 5000-digit adversarial size.
- Scanner source/test syntax compilation and `rtk git diff --check` passed.

A Gemini fixture cleanup race occurred before the observability testing flag was applied: terminal-event observability launched detached maintenance that could write after cleanup began. Scanner fixtures now use the existing `OBSERVABILITY_TESTING=1` flag to prevent detached maintenance while retaining disposable observability capture. The rerun passed. This is fixture evidence, not the external incident cause.

The capture and merge suites use only disposable repositories, log destinations and temporary capture storage. No new suite or registry entry was added.

## Remaining ownership and limits

The coordinator owns integration, the frozen generator snapshot suite, shared security banners, final full-suite checks, independent review, the single KB update pass and deployment. This task did not install hooks, push the private branch, edit the active ExecPlan or KB, run timing benchmarks, or claim native Windows/provider dispatch acceptance.

The original report came from Copilot on an external Linux host. Its exact host cause remains unknown; these source reproductions repair opaque diagnostics without granting read/documentation exemptions, scanning submodules, increasing bounds or assuming the report's repository shape.
