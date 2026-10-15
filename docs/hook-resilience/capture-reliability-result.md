# Scanner capture reliability investigation

The shared scanner now recovers from transient Git launch failures and reports enough safe OS detail to investigate future failures. The original single Copilot incident remains unattributed: its retained record discarded the underlying errno and capture operation. The reproduced failure class below matches its visible symptom, but does not prove retrospective causation.

## Evidence and cause

The original session record shows the synthetic-credential control failing with `git_capture_failed/git_head`, build `48e2bf05377ccd6e`. It contains no underlying OS exception. The fixture removed its temporary directory, so that missing detail cannot be recovered from its files.

Repeating the original public Copilot credential control 200 times serially and 800 times with four workers produced no failures. A disposable instrumented copy recorded no OS exceptions. Those passes do not explain the historical failure.

A native macOS reproduction temporarily lowered only the disposable hook process's `RLIMIT_NPROC` soft limit to zero at the HEAD launch. The kernel rejected process creation with `EAGAIN`, errno 35. Baseline `Popen` failure immediately became `git_capture_failed/git_head`, although process creation became available again before the scan ended. Treating a transient failed launch as a permanent scan failure is the reproduced reliability defect.

The same public credential regression was red before the fix and green afterward. A retained comparison covers all three providers and both an injected launch failure and a real kernel process-limit failure: all six baseline cases were incomplete; all six candidate cases detected findings. A second red/green regression proves that permanent launch errors now retain sanitized diagnostic detail.

Darwin may clamp the hard process limit when lowering the soft limit. An initial disposable probe could not restore its original reported hard limit. The maintained fixture restores the original soft limit using the current hard limit, inside the hook subprocess only. Its native fault must actually prevent launch; an unexpected successful launch fails the test.

## Changes

- [Canonical scanner](../../hooks/families/scan_secrets.py): retry only `Popen` launch errors with `errno.EAGAIN`, with three total attempts and 10/20 ms backoff. Preserve the original five-second Git deadline and eight-second scan deadline. Never replay a successfully launched command.
- Preserve incomplete outcomes for permanent launch errors and exhausted retries. Existing nonzero-exit, descendant, output, private-file, and cleanup checks remain active.
- Incomplete capture diagnostics now include a scanner-owned `capture_step`, numeric `os_errno` when available, and launch `attempts`. Responses and logs never include raw exception text, filenames, command output, or credential values.
- [Public capture suite](../../scripts/test-scan-secrets-capture.py): cover one/two transient failures, native macOS process exhaustion, clean and credential controls, persistent EAGAIN, immediate EACCES, and deadline preservation in both modes. Retain watchdogs, exact diagnostic assertions, redaction, and immediate temporary-file cleanup checks.
- Regenerate all provider scanner outputs and their diagnostic build identities. Document the new diagnostic fields in [README](../../README.md).

## Validation

Commands ran from `/Users/adam/.codex/worktrees/c164/skills` through `rtk proxy`. The initial source was clean at `ac273b60`. No test was disabled, skipped, deleted, or weakened.

| Check | Result |
| --- | --- |
| `bash scripts/test-hooks-secrets-scanner.sh` | Passed, including full Copilot public capture matrix; 90.568 seconds. |
| `bash scripts/test-gemini-hooks-secrets-scanner.sh` | Passed, including full Gemini public capture matrix; 93.050 seconds. |
| `bash scripts/test-codex-hooks-secrets-scanner.sh` | Passed, including public envelopes and full Codex capture matrix; 87.394 seconds. |
| `python3 scripts/test-security-banners.py` | 14 passed. |
| `python3 scripts/test-security-reporting.py` | 14 passed. |
| `python3 scripts/test-hook-diagnostics.py` | 10 passed on Python 3.14.6. |
| `/usr/bin/python3 scripts/test-hook-diagnostics.py` | 10 passed on native Python 3.9.6. |
| Native Python 3.9.6 focused public controls | Real kernel EAGAIN recovery and persistent-failure diagnostics passed for all three providers. |
| `python3 scripts/test-scan-secrets-merge.py` | 33 passed across all providers; 220.256 seconds. |
| Four-worker stress run | 1,200 passed: 48 provider/mode/content/fault combinations repeated 25 times each; 600 findings and 600 clean outcomes. Source hashes remained unchanged. |
| Independent review | No actionable findings; reviewer independently passed 15 public controls across all providers. |
| `python3 scripts/generate-hooks.py --check` | All 38 generated files current. |
| `git diff --check` | Passed. |

The stress run included 300 ordinary controls, 300 one-failure controls, 300 two-failure controls, and 300 native process-limit controls. It overlapped functional validation deliberately to exercise contention; elapsed times are not performance acceptance evidence. Every control checked actual findings or clean results, enforcement, redaction, and capture cleanup. Persistent-error cases in the maintained suite require exactly three EAGAIN attempts and one EACCES attempt. A real 5.05-second launch fault remains `git_timeout`, proving retries do not reset the command deadline.

All planned functional checks completed successfully. Timing figures above describe functional runs, not latency acceptance. No performance acceptance benchmark was needed or claimed for this change.

## Retained artifacts

- `/tmp/c164-capture-validation-ez344h88/`: serial suite commands, results, and logs; disposable observability paths prevented writes to installed logs.
- `/tmp/c164-capture-stress-agare6s4/`: runner, complete 1,200-row results, summary, and source fingerprints.
- `/tmp/c164-capture-causal-4jyqm670/results.json`: all-provider baseline/candidate comparison.
- `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/c164-capture-trace-hi_cwdbo/results.json`: 800 traced baseline controls with no failure.
- `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/c164-native-eagain-7foa7e_4/errno.txt`: initial kernel errno 35.

## Limits and review

The original failure's exact cause cannot be established from the surviving evidence. The fix addresses a demonstrated transient-launch cause, while the added diagnostics distinguish storage, launch, wait, descendant inspection, consumption, and cleanup errors if another incident occurs. Do not call the historical event conclusively explained.

No live home-directory hooks were installed or changed. Native Windows and authenticated provider delivery remain unverified. These checks do not establish race freedom during concurrent repository mutations or universal hook availability under resource exhaustion.

One read-only review agent used selected/submitted `gpt-6.1-sol` with `high` effort, a 10-minute warning threshold, and no nested delegation. It completed within the threshold. Runtime-executed configuration was not reported and remains unconfirmed. Its output and focused checks were verified; routing was compliant. The primary agent retained ownership of all edits and documentation.

## Knowledge maintenance

The single coordinated `update-agent-docs` pass completed after validation and review. Existing security and testing guidance remains consistent with the implementation; source-level retry details and session history do not warrant a new canonical memory. No canonical KB content changed, so no OKF validation was required.

Added: None. Changed: None. Split or moved: None. Deduplicated: None. Index updates: None. Remaining canonical doc quality TODOs: None.

The completed working plan was removed under repository retention rules. This result preserves the investigation, decisions, evidence, and unresolved historical attribution. Changes remain uncommitted.
