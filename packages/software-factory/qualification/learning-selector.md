# Learning selector qualification

Observed 2026-10-22 on local macOS arm64 with pinned Node v24.22.1. This is local deterministic evidence; it does not establish hosted native qualification.

## Results

- Before reorganization, the existing public dispatcher E2E passed locally in 17.973 seconds under its unchanged 30-second selector bound.
- `node scripts/test.mjs learning --operation extract` passed all 13 extraction cases, with no skips, in 9.412 seconds. The public `operation: 'extract'` filter selects all four explicitly registered files, and Node runs that batch with `--test-concurrency=2`.
- `node scripts/test.mjs fixtures` passed all 12 fixture and dispatcher checks in 20.331 seconds. Its existing `learning extraction selection executes public proposal and source checks` E2E completed in 9.377 seconds under the unchanged 30-second timeout.
- `node scripts/test.mjs adapters --provider fake` passed all 84 fake-adapter and validated-result checks in 65.944 seconds.
- Pinned Node syntax checks passed for the dispatcher, shared fixture, and all four extraction test files. A comparison against the original `HEAD` test declarations found the same 13 names with byte-identical bodies and assertions. `git diff --check` passed.
- The two exact source-case names used by `qualification-foundation.mjs` also passed when selected directly from `test/learning.test.mjs`: 2 passed in 2.920 seconds.
- The package build passed after installing the locked dependencies offline with scripts disabled. No provider or live call was made.

## Retained failure and native gates

The original Linux public red remains at `/tmp/factory-foundation-39818894909-failed.log`: the extraction selector exceeded its 30-second bound at 30,017.776 ms while fixed fixture markers showed ordinary source/extraction invocations reaching later cases. That evidence does not establish an interrupted-source deadlock. The same qualification log records a separate Windows startup-cleanup refusal; this task does not repair or clear it.

Hosted native CI must rerun the original selector with the unchanged 30-second bound and show all 13 cases completed on Linux and macOS. Windows remains unqualified for this selector while its separate startup-cleanup refusal prevents the learning fixture from entering. These local passes do not claim native qualification or live provider behavior.
