# Windows placement diagnostic candidate, 2026-10-22

## Retained native failure

[Run 39729936207](https://github.com/japurcell/skills/actions/runs/39729936207) tested `8db4c9cbdc6561441c819c4f9561344de2f15431`. Windows foundation failed on win25-vs2026 image 20261018.275.1, OS 10.0.26100, Node v24.22.1 and SQLite 3.53.4. The store group failed seven of 29 assertions after 69.201 seconds; its early capture/store cases report only `native Windows placement probe failed; storage refused`. Individual failing cases took approximately 10.8 to 14.8 seconds. The later isolated placement suite passed both cases in 3.303 seconds, runtime tests passed all four cases and the direct NTFS runtime probe passed with small-commit p95 26.368 ms.

Those observations establish failure during the native placement subprocess, not its cause. The discarded subprocess error, exit status and signal prevent distinguishing a deadline, output limit, launch failure or PowerShell error. Concurrent first-use compiler contention is only a hypothesis. Later success on the same host does not repair or waive the earlier failure.

Downloaded original artifacts: `/tmp/factory-native-39729936207/software-factory-foundation-win32-x64-39729936207-1/`; combined failure log: `/tmp/factory-foundation-39729936207-failed.log`. These are temporary local copies. Actions artifacts have 14-day retention.

## Candidate and local evidence

The candidate adds allowlisted subprocess error codes and signals, numeric exit status or `none`, and monotonic elapsed milliseconds to the refusal message. Unknown codes/signals become `other`. It does not attach the original Error or include stdout, stderr, storage paths or environment values. The native script, fixed PowerShell executable, 10-second timeout, 8192-byte output limit, concurrency and fixed-local-NTFS/ReFS acceptance rules stay unchanged. This is diagnostic instrumentation, not an established native failure repair.

The focused public `assertLocalPlacement` regression substitutes only OS boundaries in an isolated Node child. It fails on the original generic refusal message, then passes timeout, missing-executable, output-limit, nonzero-exit, signal and unknown-value refusal cases with bounded diagnostics and no path/output leakage. These substitutions do not execute Windows APIs. On native macOS arm64 with pinned Node v24.22.1: focused placement 3/3, unchanged store/capture/placement group 30/30, strict source/qualification typechecks and build passed. The original two placement tests and all prior store/capture assertions remain intact.

API authority: [Node v24.22.1 child_process documentation](https://r2.nodejs.org/docs/latest-v24.x/api/child_process.html#child_processspawnsynccommand-args-options) defines `error`, numeric/null `status`, and nullable `signal`. A timeout sends the kill signal and `spawnSync` waits for the child to close, so elapsed time can exceed the configured deadline. [PowerShell 5.1 Add-Type](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-5.1) compiles inline C# into an in-memory assembly; this confirms compilation occurs, not that it caused this failure.

## Exact next native experiment

After independent review and integration, dispatch the existing `software-factory-qualification.yml` workflow at the integrated candidate SHA using its current pinned runtime/bootstrap and foundation driver. Preserve current test-file concurrency and every assertion. In its existing order, `node scripts/qualification-foundation.mjs` executes `node scripts/test.mjs store` before standalone `node --test test/placement.test.mjs`, followed by runtime checks; this exercises the original failing public operations without a new warm-up or serialization change. Do not add automatic retries or raise any deadline.

Retain the run URL, integrated SHA, runner image, OS, full store/placement logs, foundation JSON and runtime JSON regardless of success. If placement fails, record each allowlisted error/status/signal/elapsed tuple. `ETIMEDOUT` establishes deadline expiry, `ENOBUFS` establishes output-bound failure, an allowlisted launch error identifies that OS failure, and an exit code identifies an ordinary failing process. None alone establishes compiler contention. An ordinary PowerShell exit still needs a subsequent narrowly designed stage experiment, without raw stderr or environmental output. A passing fresh-host run qualifies only that execution and leaves the earlier unexplained native failure retained.
