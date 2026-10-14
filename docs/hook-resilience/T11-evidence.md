# T11: Adjacent warm launches with unchanged acceptance

Implementation proof completed on 2026-10-14 in private branch `codex/hook-resilience-t11`, based on `51064b2b68e6655aa4681fce55c146183043d1ca`. Scope is only `scripts/verify-hook-release.py`, `scripts/test-verify-hook-release.py` and this evidence. The coordinator owns plan reconciliation, independent review, release timing and the coordinated KB pass.

This repairs the source-block scheduling confound identified by [accepted D3](D3-performance-design.md). It does not establish an environmental cause for any historical failure. The 25 failed warm comparisons across 22 cases in [V1's T10 evidence](V1-T10-release-evidence.md) remain rejected. No runtime optimization, budget change, case exclusion, live installation or complete release timing run occurred here.

## Red and green

The agreed seams were the existing adapter API with a traced process stub and the public CLI with real disposable provider scripts. The deterministic API test uses two maintained exact case IDs, including the full search's baseline denial/candidate allowance, and tests both full counts and mechanics counts. The first fixture attempt stopped before invocation because its parent run directory was absent; creating that directory exposed the intended red result:

`rtk proxy python3 scripts/test-verify-hook-release.py ReleaseVerificationTests.test_matched_warm_calls_are_adjacent_for_both_cases_and_pairs`

Before repair, exit 1: the first differing trace element was `codex.guard.search.full-provider-envelope, baseline, deny` where the adjacent `candidate, allow` launch was required. The stderr sequence showed all baseline cases before candidate cases in pair 1 and the reverse source blocks in pair 2. After repair, the same command exits 0. The test checks 29 calls per condition/case in full mode, 3 in mechanics mode, exact pair/case/call/source order, both homes prepared before invocation, first timing retained from inner elapsed, first/warmup/measured boundaries, independent measured samples and completed-record counts.

The real CLI mechanics fixture now writes source identity, input SHA-256 and per-home sequence to one disposable trace. Its first 24 launches are exactly two cases times three calls times two sources times two pairs: baseline/candidate adjacent for every pair-1 call, candidate/baseline for every pair-2 call. It checks positive first times, completed logging, unchanged normal bytecode reuse and ordered, nonoverlapping monotonic invocation intervals. It makes no latency acceptance assertion.

## Preserved behavior and failure evidence

`warm_pair_run` prepares both cases/homes, requires equal exact IDs and payload bytes, and retains native condition-specific expectations. `measure_timing` rejects missing or duplicate case IDs rather than dropping them. Both existing-schema rows are appended before launching either label. Call 0 is first process; 1-3 are warmups; 4-28 are the 25 measured samples. Mechanics remains first plus two measured calls.

The optional keyword-only `checked_invocation(..., observation=...)` records `start_monotonic_ns` and `end_monotonic_ns` immediately around the maintained `high_rate.invoke`. Validation follows the interval. The unchanged returned inner elapsed feeds first-process and measured values. The default return tuple and default caller path are preserved. Warm rows add invocation call index/kind/timestamps; failed native decisions retain the failed output, inner elapsed and timestamps. Missing logging after both labels finish retains both rows, summaries, logging counts and the last offending label's invocation evidence. New CLI controls fail on the second label's wrong native decision or missing log after the first label succeeds.

All 156 timing IDs and explicit baseline expectations remain. The legacy malformed-input zero-record exception remains labeled separately from completed logging. The independent cold copies and homes, zero cold bytecode, concurrency batch, source-mutation rejection, output overwrite refusal and exact case selection controls still pass. Every ordinary full warm row requires 29 completed records after both labels finish.

The numerical functions `summary`, `comparisons` and `compare` are unchanged. The asymmetric test uses baseline `[0 x 23, 50, 100]` and candidate `[100, 50, 1 x 23]`. Their independently computed nearest-rank p95 values both equal 50, so the accepted p95 delta is 0; p95 of paired differences is 50 and is explicitly rejected as the comparison statistic. The existing first-pair failure remains false even when pair 2 passes. Gates remain independently +2/+5 ms warm and +5/+10 ms cold, with a 500 ms resource ceiling.

## Verification results and limitations

Commands ran serially from the private worktree with `login:false` and RTK prefixes:

- `rtk proxy python3 scripts/test-verify-hook-release.py`: final 15 tests pass in 2.818 s.
- `rtk proxy python3 scripts/test-benchmark-high-rate-hooks.py`: 2 tests pass in 15.468 s.
- `rtk proxy python3 scripts/test_test_all.py`: maintained registry's 14 focused tests pass in 11.068 s.
- `rtk git diff --check`: pass.

The initial sandboxed adapter suite failed the existing resource test because native `/usr/bin/time -l` received `sysctl kern.clockrate: Operation not permitted`. The approved native rerun passed, including positive RSS and the separate completed fourth log record. Test-development failures were retained in the session: the asymmetric p95 assertion initially assumed interpolation rather than the maintained nearest-rank calculation, and the observation stub initially supplied `{}` for a provider requiring an explicit native decision. The expected p95 literals were corrected to the independently worked nearest-rank result; the observation stub now uses the maintained Codex clean case whose native allow output is `{}`. No production numerical function, failing test, security check or logging requirement was weakened.

Source hashes at completion:

- `scripts/verify-hook-release.py`: `e88095f3115f730176b11507e72d13f01d3d546cc4b62084095f4851e81e2019`.
- `scripts/test-verify-hook-release.py`: `f930928af51d6f07e3816624a90e426fb541707f01aeef9a55f88e458ff7f2a7`.

`rtk git diff --exit-code 1817d569 -- hooks .codex/hooks .copilot/hooks .gemini/hooks .github/hooks scripts/benchmark-high-rate-hooks.py scripts/benchmark-tool-guard-resources.py scripts/tool_guard_corpus.py scripts/fixtures/tool_guard_vectors.py scripts/test-all.py` exits 0. Product runtime, maintained runners/corpus and registry are unchanged from the frozen V1 candidate. Inspection of the scoped diff confirms `warm_run`, the cold loop, concurrency collection and `measure_resources` are unchanged; cold, resource and concurrency calls continue using `checked_invocation` without observations. This supports reuse of prior full resource evidence for unchanged behavior, with the bounded native RSS mechanics check as additional evidence. It is not a new full resource or timing acceptance run.

Both original independent review axes must inspect the immutable commit. V1 then owns a new complete timing run against the exact baseline and frozen candidate, retaining every result. This implementation evidence does not establish release acceptance or explain away the historical failures.
