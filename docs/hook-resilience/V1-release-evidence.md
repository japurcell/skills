# V1 release verification checkpoint: latency acceptance rejected

V1 remains incomplete. Functional and isolated installed-asset coverage is reconciled, and the full native finite-resource gate passed. The complete latency comparison failed **89 of 468 comparisons across 78 distinct cases**. No violation was waived, no budget changed, and no timing repeat or product/test edit was performed. The coordinator assigned D2 to diagnose systematic warm failures before selecting any narrow repeat or bounded repair.

## Frozen provenance and authorization

The measured candidate was `6c1623ff06d58566cf659658c9a92196b71bff7d` on private branch `codex/hook-resilience-v1`, cleanly rebased onto the explicitly approved base `3288cf4e8fe8899b9f179c49e6290e99f490051f`. Relative to the prior installed proof, the only added non-document change was T9's shared test fixture support. All 74 runtime/source hashes and modes remained identical, inventory `76e5086f4a3bc110e3d29547df04fabf5c64f6c3a469962dffd60e26267087b3`. Generated freshness passed all 38 outputs after rebase. No source, test, generator, or evidence edits ran during either measurement process.

The baseline was a fresh local `git archive` of `bc52d7d69aaa046ea97e323879402241a01fead7`; the adapter independently verified its actual runtime hashes against that Git revision. An archive directory name alone was not treated as identity. The exact archive SHA-256 and before-freeze checks are retained in [freeze provenance](V1-phase2-freeze.json). Both independent review axes had accepted all repairs, all other reviewers/probes/tests/generation/benchmarks had stopped, and the coordinator explicitly authorized serial Phase 2 after a quiet-process snapshot. Resources ran first, then timing. Native macOS collector execution was approved outside the sandbox that previously denied `sysctl kern.clockrate`.

Commands executed by the external capture wrapper, from the frozen candidate root:

```text
rtk proxy python3 scripts/verify-hook-release.py --baseline-root <owned-baseline> --candidate-root <verification-worktree> --mode resources --output <new-evidence>/resources.json
rtk proxy python3 scripts/verify-hook-release.py --baseline-root <owned-baseline> --candidate-root <verification-worktree> --mode timing --output <new-evidence>/timing.json
```

The maintained adapter and runners are [verify-hook-release.py](../../scripts/verify-hook-release.py), [benchmark-high-rate-hooks.py](../../scripts/benchmark-high-rate-hooks.py), and [benchmark-tool-guard-resources.py](../../scripts/benchmark-tool-guard-resources.py); inspect those files at the measured Git commit for exact source. Their runtime/harness hashes are retained in each complete report. No `--mechanics-only`, filtered case selection, historical baseline expectation flag, or reused output path was used.

## Native finite-resource gate

The run exited zero in **159.880 seconds** with **108 cases per condition, 216 rows total**. Every row retained its first process, 25 measured samples, three discarded warmups, native outputs, normal provider bytecode reuse, completed-log proof and a separate native `/usr/bin/time -l` launch reporting peak RSS in bytes. Every first/measured call met the 500 ms finite-input ceiling. The separate RSS launch also passed the expected native decision and logging check. All **6,480 required completed guard records** were present. The report is release-eligible, has no errors, verifies the exact baseline, and confirms unchanged runtime/harness source before and after.

| Condition | Maximum first/measured call | Case | RSS range, bytes |
| --- | ---: | --- | ---: |
| Baseline | 59.701 ms | `codex.resources.structure-wide-overflow` | 19,677,184 to 23,429,120 |
| Candidate | 54.858 ms | `copilot.resources.strict-max` | 20,430,848 to 24,084,480 |

These observations establish the accepted finite time gate. They are not a universal raw-JSON memory bound or a blanket improvement claim. Full evidence: [resources](V1-resources.json.gz), [summary](V1-resources-summary.json), [execution](V1-resources-execution.json), [raw progress](V1-resources-runner.log.gz).

## Complete timing method and functional integrity

The run exited **1** in **765.252 seconds** after completing all 156 cases per condition. It retained **624 warm rows**, **7,800 cold launches**, **468 per-case comparisons**, pair variation and **six separate concurrency rows**. Two matched warm pairs alternate baseline/candidate and candidate/baseline; every case/condition/pair has a first process, three discarded warmups and 25 measured samples. Warm gates are +2 ms median/+5 ms p95 for each pair independently. Every cold sample has its own fresh provider source copy and log home, with zero provider bytecode before and after. Cold gates are +5/+10 ms. OS and standard-library caches remain uncleared. Concurrency is separate and never feeds latency gates.

All predeclared native permission decisions passed, including V0's explicit baseline full-search-envelope deny versus candidate allow expectation. Every valid call had its required completed guard record: 17,748 warm, 7,650 cold and 12 concurrency records. The exact malformed-JSON `*.guard.failure` legacy fixture had zero completed records across 498 calls, retained as 12 warm-row and 150 cold-row transport exceptions; it was never generalized to valid inputs or counted as successful inspection/logging. Normal warm bytecode reuse and all 7,800 cold zero-bytecode conditions passed. The adapter reports **errors=[]**, **sources_unchanged=true**, and a verified baseline. The failure is latency acceptance, not an omitted case, decision mismatch or collection failure.

[Declared case metadata](V1-performance-declared-cases.json.gz) pins expected decisions and payload SHA-256 from the unchanged maintained builders, never from observed outcomes. The supplemental resource hash table was captured after resource collection using the exact frozen source whose expectations were enforced during each invocation; the timing table was captured before timing. Native first outputs, all retained sample outputs, first-process times, raw measured samples, median/p95/MAD, pair variation, separate concurrency and source/harness fingerprints remain in [the complete failed timing report](V1-timing-failed.json.gz).

## Violations and rejection

Warm pair 1 failed **19** comparisons, warm pair 2 failed **59**, and cold failed **11**. There were **78 median** and **19 p95** violations, with eight comparisons exceeding both limits. All cold medians were within +5 ms; 11 cold p95 deltas failed. Provider totals are Gemini 48, Codex 23 and Copilot 18 failed comparisons. Delta ranges below are descriptive across all 52 cases for each provider/phase; they do not aggregate away any failed case.

| Phase | Provider | Failed | Median delta range, ms | p95 delta range, ms |
| --- | --- | ---: | ---: | ---: |
| warm-pair-1 | copilot | 11/52 | +1.360 to +4.042 | -2.004 to +4.941 |
| warm-pair-1 | gemini | 2/52 | +1.152 to +2.199 | -3.177 to +4.161 |
| warm-pair-1 | codex | 6/52 | -0.121 to +3.442 | -0.762 to +4.219 |
| warm-pair-2 | copilot | 7/52 | +0.377 to +5.105 | -0.835 to +13.715 |
| warm-pair-2 | gemini | 37/52 | +0.897 to +3.874 | +1.129 to +12.968 |
| warm-pair-2 | codex | 15/52 | +0.910 to +2.814 | +0.635 to +5.866 |
| cold | copilot | 0/52 | +0.419 to +2.694 | -15.118 to +3.611 |
| cold | gemini | 9/52 | +0.784 to +2.856 | -2.659 to +16.334 |
| cold | codex | 2/52 | +0.458 to +2.390 | -6.406 to +13.008 |

Five cases exceeded the warm median allowance in both independently gated pairs:

| Case | Pair 1 median / p95 delta, ms | Pair 2 median / p95 delta, ms |
| --- | ---: | ---: |
| `copilot.guard.writer.chars-8787-segments-183` | +2.271 / +2.326 | +2.022 / +13.715 |
| `gemini.guard.write.utf8-growth` | +2.199 / +2.066 | +2.925 / +7.327 |
| `codex.guard.write.examples.md` | +3.240 / +3.709 | +2.068 / +2.799 |
| `codex.guard.write.examples.test.py` | +2.717 / +3.829 | +2.114 / +2.913 |
| `codex.guard.search.literal` | +3.041 / +3.495 | +2.034 / +2.833 |

The broad warm failure families include native writer/edit/search inputs and executable-danger controls across all providers, with a larger second-pair Gemini cluster. The largest warm median delta is Copilot Unicode normalization, +5.105 ms median/+8.989 ms p95 in pair 2. The largest warm p95 delta is the Copilot semicolon-rich writer, +13.715 ms in pair 2. The largest cold p95 delta is Gemini download-and-execute-sh, +16.334 ms (its median delta is +1.449 ms).

No environmental cause is established. Different pair distributions and sample MAD remain evidence to diagnose, not permission to waive gates. This is a widespread failure with five cases repeating across pairs, so V1 did not run blanket repeats or select a later passing run. The original report remains authoritative and timing acceptance is **rejected**. D2 owns subsequent measured diagnosis and any proposed bounded repair; a narrow exact repeat can distinguish noise only after the systematic failures are understood. Full [concise summary](V1-timing-summary.json), [provider ranges and repeated cases](V1-timing-ranges.json), [execution](V1-timing-execution.json) and [runner log](V1-timing-runner.log.gz) are retained.

## Functional provenance, limitations and next action

[Functional evidence](V1-functional-evidence.md) and [all 51 suite provenance rows](V1-functional-map.json) preserve the original aggregate's five failures and map them to two environment-corrected repeats, two T8 contract repairs and one T9 fixture repair. Both full observability suites passed after T9 integration with all three completion markers. Existing passing evidence is reused only with the recorded source/interaction checks. Actual installed bytes/modes, user registration preservation, nonmutating doctor output and repeat-install fingerprints passed. No fresh all-51 passing aggregate is claimed.

Three native Windows suites remain explicit platform skips. macOS PowerShell coverage does not establish native Windows execution, ACLs or the unavailable junction subcheck. No live-home install or authenticated provider dispatch occurred. The finite-resource pass does not override failed latency acceptance. V1 remains incomplete pending D2 diagnosis/repair, affected functional verification and a new authorized frozen release check under the same prescribed budgets. Primary owns the active plan, final KB pass and worktree lifecycle.

Artifacts are losslessly gzip-compressed where large; `gzip -dc PATH` reads them. Only known user/worktree/temporary-user path prefixes were neutralized. Quantitative samples, decisions and source/input hashes are unchanged. [Artifact hashes](V1-performance-artifacts.json) retain both original-byte and redacted/stored-byte SHA-256 values. Original unredacted JSON/logs and the owned baseline archive remain in verifier temporary state for D2; no original output was overwritten or removed.
