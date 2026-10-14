# V1 after T11: complete timing gate passed

The new complete T11 timing run passes **all 468 comparisons**, with complete native decisions, completed logging, source/baseline integrity, cold bytecode and warm adjacency checks. Together with the attributed unchanged full resource and functional/installed proofs, available-environment V1 verification is complete. The historical **89/468** and **25/468** timing failures remain rejected and unchanged. The scheduling repair does not establish their causal origin; this is a new complete run on the reviewed method, with no repeat or waiver.

## Frozen provenance and authorization

The private candidate was clean `81fe28bbbbc9682ff6a417d3f5b563c948f8c943` on `codex/hook-resilience-v1`. All runtime, maintained runners, corpus and registry match `1817d569`; T11 adapter/tests match reviewed `8f250431` and tested `19518f2`. Both original independent reviewers accepted T11 with no new findings and finished all probes. Primary explicitly granted the exclusive quiet window at **21:22 UTC**, with all other tests/probes/generation/bookkeeping finished. No ancillary analysis, compression, tests or generation ran during timing. Native execution was approved. The quiet window ended only after the complete result and adjacency audit passed.

[Freeze](V1-T11-freeze.json) retains source/harness fingerprints and a fresh exact `git archive` baseline `bc52d7d69aaa046ea97e323879402241a01fead7`. Archive SHA-256 is `9d9626b766a1c2f252b83554bc6876c7c3f0b8ee4278e6fa1b13c221fa263ff6`; the maintained adapter independently verified actual baseline runtime hashes. [Declarations](V1-T11-performance-declared-cases.json.gz) pin all 528 condition/case expected decisions and input hashes before measurement; they are identical to the prior frozen case set and never derived from outcomes. Final [runtime inventory](V1-T11-runtime-fingerprints.json) covers 74 assets/modes, hash `5adb02a8a6bb6bb356cffa023efc43b84f5e41e503b82bf869e33a4492212b3d`.

One complete maintained timing command ran, with no filters or mechanics-only flag, using new never-existing output:

```text
rtk proxy python3 scripts/verify-hook-release.py --baseline-root <owned-fresh-baseline> --candidate-root <verification-worktree> --mode timing --output <new-evidence>/timing.json
```

The [capture wrapper](V1-T11-capture-wrapper.py.gz) and [execution](V1-T11-timing-execution.json) retain disposable HOME/CODEX_HOME/XDG/log isolation and cleared conflicting inherited overrides. Exact adapter [source](../../scripts/verify-hook-release.py) at the frozen commit has SHA-256 `e88095f3115f730176b11507e72d13f01d3d546cc4b62084095f4851e81e2019`. Maintained runner/corpus hashes are in the complete report. Python was 3.14.6 on native macOS 26.7.1 arm64; the exact interpreter/platform/Git metadata remain retained.

## Complete results under unchanged gates

The run exited **0** in **763.250 seconds**, release eligible, verified baseline, `sources_unchanged=true`, `errors=[]`, `gates_met=true`. It completed **156 cases per condition**, **624 warm rows**, **7,800 independent cold launches**, **468 separately gated comparisons** and **six separate concurrency rows**. Each warm row retains first process, three discarded warmups and 25 measured samples. Pair 1 launches baseline/candidate adjacent per call; pair 2 reverses the source order. Each case/pair must independently meet +2 ms median/+5 ms p95. Statistics remain independently computed condition medians/p95, candidate minus baseline; there is no pooling, pair averaging or quantile-of-paired-differences replacement.

Cold conditions retain 25 independent fresh provider copies and homes per case, zero provider bytecode before and after every launch, and unchanged +5/+10 ms allowances. OS and standard-library caches remain uncleared. Concurrency is retained separately and does not feed latency gates. All 312 warm and 156 cold comparisons pass. The largest warm median delta is +1.216 ms; largest warm p95 delta +3.611 ms. The largest cold median delta is +4.454 ms (Gemini full-provider-envelope search); largest cold p95 delta +6.000 ms (Gemini semicolon-rich writer).

| Phase | Provider | Passed | Median delta range, ms | p95 delta range, ms |
| --- | --- | ---: | ---: | ---: |
| warm-pair-1 | copilot | 52/52 | +0.524 to +1.046 | -0.093 to +1.644 |
| warm-pair-1 | gemini | 52/52 | +0.441 to +1.092 | -1.679 to +1.966 |
| warm-pair-1 | codex | 52/52 | +0.386 to +1.100 | -0.523 to +2.183 |
| warm-pair-2 | copilot | 52/52 | +0.253 to +1.025 | -0.569 to +3.611 |
| warm-pair-2 | gemini | 52/52 | +0.343 to +1.164 | -0.177 to +1.613 |
| warm-pair-2 | codex | 52/52 | +0.476 to +1.216 | -1.064 to +1.747 |
| cold | copilot | 52/52 | +0.744 to +2.912 | -0.093 to +4.454 |
| cold | gemini | 52/52 | +0.992 to +4.454 | +0.866 to +6.000 |
| cold | codex | 52/52 | +0.975 to +2.137 | -5.282 to +3.360 |

All predeclared native outputs passed, including explicit legacy baseline full-search denial versus candidate allowance. Every valid call had required completed logging: **17,748 warm**, **7,650 cold** and **12 concurrency** records. The exact malformed-JSON `*.guard.failure` legacy transport fixture remains separately labeled with zero records (12 warm rows and 150 cold rows); it is not generalized to valid inputs or claimed as successful inspection. Every normal warm row has 29 completed records. All normal warm bytecode-reuse and 7,800 cold zero-bytecode checks pass.

## Recorded adjacency and unchanged inner elapsed

The independent [adjacency validator](V1-T11-adjacency-validator.py.gz) and [result](V1-T11-adjacency-validation.json) check **18,096 timestamped warm invocations**, grouped into **9,048 adjacent matched launch pairs**. Every row has exactly 29 indexed calls: first 0, warmups 1-3, measured 4-28. Global start-sorted events exactly match pair, case, call index and fixed per-pair source order; intervals are positive and nonoverlapping, with no intervening different case. The matched end-to-next-start gap is min 0.011916 ms, median 0.019833 ms, max 0.193875 ms. Matched start separation ranges 18.213334-52.805209 ms, median 23.283625 ms.

The timestamps bracket the maintained invocation; first-process and measured values remain the original inner elapsed, not outer observation duration. The validator recomputes each warm summary from all 25 original samples and verifies every warm median/p95 delta is the difference of independent condition statistics. Warmups remain excluded. Counts, order and metadata are checked in addition to the maintained native/logging/cache/source validations. There were no timing violations, so no targeted or blanket repeat was needed or run.

The [complete timing report](V1-T11-timing.json.gz) retains all native first outputs, first-process timings, raw measured samples/outputs, warm timestamps, median/p95/MAD, pair variation, separate concurrency and source fingerprints. [Summary](V1-T11-timing-summary.json), [provider ranges](V1-T11-timing-ranges.json) and [raw progress](V1-T11-timing-runner.log.gz) are separate.

## Composed resource/function evidence and limits

[Final functional/resource evidence](V1-T11-functional-evidence.md) explains exact reuse and the [51-suite map](V1-T11-functional-map.json): 31 fresh T10 suites, three fresh T11 suites (adapter 15, high-rate 2 and maintained registry 14), one previously fresh portable PowerShell result, 13 unchanged results reused, three native Windows suites unverified. The full 108-case-per-condition resource gate and actual disposable Bash/macOS PowerShell asset/mode/build/registration/user-config/idempotence proofs apply to byte-identical runtime and unchanged resource/install interactions. T11's native resource mechanics also pass. No new all-51 passing aggregate or new full resource run is claimed.

Native Windows execution/ACLs/junction and authenticated provider delivery remain explicitly unverified. No live-home installation occurred. These limits do not disappear because finite source verification passes. Primary owns final plan/KB maintenance and integration.

Every prior V1 file is fingerprinted in [original preservation](V1-T11-original-artifacts-preserved.json) and remains unchanged, including both complete rejected timing runs. New evidence uses only V1-T11 filenames. Large artifacts are losslessly gzip-compressed (`gzip -dc PATH`); known user/worktree/temporary-user path prefixes are neutralized, while samples, decisions, numeric results and input/source hashes are unchanged. [Artifact hashes](V1-T11-artifacts.json) retain original, redacted-uncompressed and stored SHA-256. Unredacted originals remain in verifier-owned temporary state. No source/harness/policy edit or push occurred.
