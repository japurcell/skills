# V1 after T10: full release timing rejected

**V1 remains incomplete.** The final composed functional/install proof and full native resource gate passed. The full timing run failed **25 of 468 comparisons across 22 cases**, all in warm phases. Three cases failed in both warm pairs. No repeat, waiver, changed budget or product/test/harness edit was performed. This is the complete residual failure for a new bounded diagnosis, not a release acceptance.

## Frozen method and integrity

The candidate was clean `1817d569b42008019ec66d3ac3469f7fd704308c` on private unpushed `codex/hook-resilience-v1`; runtime and harness are byte-identical to reviewed `864bbda0cc59cc7ae44ee814d343765525562700`. [Freeze provenance](V1-T10-freeze.json) records 74 asset hashes/modes, harness hashes, generated freshness and fresh exact baseline archive `bc52d7d69aaa046ea97e323879402241a01fead7` (archive SHA-256 `9d9626b766a1c2f252b83554bc6876c7c3f0b8ee4278e6fa1b13c221fa263ff6`). The maintained adapter verified actual baseline source identity; a directory label was not treated as proof. Both independent review axes accepted T10 and all other checks had ended. Primary explicitly confirmed the quiet window at 20:41 UTC. No tests, generation, other probes or evidence compression ran concurrently with measurements. Approved native execution enabled macOS RSS collection.

Resources ran first, then timing, with new never-overwritten outputs:

```text
rtk proxy python3 scripts/verify-hook-release.py --baseline-root <owned-fresh-baseline> --candidate-root <verification-worktree> --mode resources --output <new-evidence>/resources.json
rtk proxy python3 scripts/verify-hook-release.py --baseline-root <owned-fresh-baseline> --candidate-root <verification-worktree> --mode timing --output <new-evidence>/timing.json
```

The [capture wrapper](V1-T10-capture-wrapper.py.gz) records disposable environment isolation and commands. Exact maintained mechanics are in [verify-hook-release.py](../../scripts/verify-hook-release.py), [high-rate runner](../../scripts/benchmark-high-rate-hooks.py) and [resource runner](../../scripts/benchmark-tool-guard-resources.py) at the frozen candidate. No mechanics-only or filtered run was used. All 528 condition/case expected native decisions and input hashes were declared from frozen builders **before both modes**: [declarations](V1-T10-performance-declared-cases.json.gz).

## Full finite-resource result

The run passed in **162.144 seconds**, 108 cases per condition, 216 rows. Each row retains first process, three warmups, 25 measured calls, outputs, normal bytecode reuse, and a separate native `/usr/bin/time -l` RSS launch. All first/measured calls were below the unchanged 500 ms ceiling; separate RSS launches passed decisions and logging. All 6,480 required completed records were present. Baseline verified, source/harness unchanged, errors empty, release eligible and gates met.

| Condition | Maximum first/measured call | Case | Native RSS range, bytes |
| --- | ---: | --- | ---: |
| Baseline | 60.071 ms | `copilot.resources.patch-high-line-max` | 19,660,800 to 23,429,120 |
| Candidate | 60.345 ms | `copilot.resources.patch-high-line-max` | 20,250,624 to 24,002,560 |

Full [resource report](V1-T10-resources.json.gz), [summary](V1-T10-resources-summary.json), [execution](V1-T10-resources-execution.json) and [progress log](V1-T10-resources-runner.log.gz) are retained. This finite-input result is not a universal raw-JSON memory bound.

## Complete timing result

Timing exited **1** in **764.496 seconds**. All 156 cases per condition completed: **624 warm rows, 7,800 independent cold launches, 468 comparisons and six separate concurrency rows**. Two warm pairs alternate baseline/candidate then candidate/baseline, each with first process, three discarded warmups and 25 measured samples per case/condition. Each pair must independently meet +2 ms median/+5 ms p95. Cold uses 25 fresh provider copies per case/condition, zero provider bytecode before and after, with +5/+10 ms gates. OS and standard-library caches remain uncleared. Concurrency is retained separately and does not feed latency gates.

Every predeclared native decision passed, including the explicit legacy baseline full-search deny versus candidate allow. All valid calls had completed guard logging: **17,748 warm, 7,650 cold and 12 concurrency records**. The exact malformed-JSON `*.guard.failure` fixture retains the established legacy transport exception (12 warm rows/150 cold rows, zero records); it is not generalized to valid inputs or counted as successful inspection. All warm bytecode and 7,800 cold zero-bytecode checks passed. Baseline verification, release eligibility, source/harness invariance and errors=[] passed. The failure is timing acceptance, not collection integrity.

Warm pair 1 failed **16**, pair 2 failed **9**, cold failed **0** comparisons. There are **16 median** and **21 p95** violations, 12 exceeding both. Provider totals are Copilot 12, Gemini 5 and Codex 8. The following ranges describe all 52 cases in each cell; they never aggregate away an individual failure.

| Phase | Provider | Failed | Median delta range, ms | p95 delta range, ms |
| --- | --- | ---: | ---: | ---: |
| warm-pair-1 | copilot | 6/52 | -1.208 to +3.138 | -4.311 to +14.033 |
| warm-pair-1 | gemini | 4/52 | -1.925 to +3.961 | -9.182 to +15.873 |
| warm-pair-1 | codex | 6/52 | -0.332 to +5.503 | -2.631 to +26.157 |
| warm-pair-2 | copilot | 6/52 | -2.622 to +3.206 | -8.697 to +15.375 |
| warm-pair-2 | gemini | 1/52 | -1.768 to +1.176 | -3.228 to +7.507 |
| warm-pair-2 | codex | 2/52 | -0.784 to +2.222 | -8.439 to +8.875 |
| cold | copilot | 0/52 | +0.817 to +3.017 | +0.391 to +5.629 |
| cold | gemini | 0/52 | +0.483 to +3.464 | +0.817 to +4.600 |
| cold | codex | 0/52 | +0.401 to +2.063 | -2.300 to +2.265 |

Three cases fail independently in both warm pairs, sometimes on different metrics:

| Case | Pair 1 median / p95 delta, ms | Pair 2 median / p95 delta, ms |
| --- | ---: | ---: |
| `copilot.guard.danger.remove_env_file` | +2.708 / +3.591 | +0.943 / +7.765 |
| `gemini.guard.danger.drop_database` | +1.686 / +8.666 | -0.175 / +7.507 |
| `codex.guard.danger.forced_git_clean` | +4.112 / +6.749 | +1.526 / +8.875 |

The largest median delta is Codex `survey.analysis-source`, +5.503 ms median/+13.709 ms p95, pair 1. The largest p95 delta is Codex `patch.lines-330`, +5.094/+26.157 ms, pair 1. Fixture categories show 16 failed comparisons across 13 protection-control cases (84-123 input bytes), plus writer, patch, survey, native-write, Unicode-control and malformed legacy inputs (15-6,363 bytes). This is not confined to one large-payload profile or one provider. Exact case/profile/byte metadata and every failed delta, baseline/candidate median/p95/MAD, pair-wide shifts and case lists are in [residual analysis](V1-T10-timing-residual-analysis.json).

Pair-2 minus pair-1 case-median shift ranges were baseline/candidate: Copilot -2.021 to +3.928 / -1.342 to +2.254 ms; Gemini -2.474 to +2.315 / -2.310 to +0.493 ms; Codex -1.001 to +1.676 / -4.494 to +1.596 ms. Median shifts across each provider's 52 cases were baseline +0.352/+1.498/+1.132 ms and candidate +0.084/+0.049/+0.046 ms respectively. Variation and occasional large candidate MAD/tails are observations for diagnosis, not evidence of an environmental cause or permission to waive gates. Most comparisons and all cold comparisons pass, but multiple warm failures and three cases repeating across pairs reject acceptance. No environmental or runtime root cause is established. No blanket or narrow repeat was run.

The complete [failed timing JSON](V1-T10-timing-failed.json.gz) retains native first outputs, first-process times, raw samples/outputs, median/p95/MAD, pair variation, separate concurrency and fingerprints. [Summary](V1-T10-timing-summary.json), [ranges](V1-T10-timing-ranges.json), [execution](V1-T10-timing-execution.json) and [raw progress](V1-T10-timing-runner.log.gz) are separate. Primary will reopen bounded diagnosis against these exact residual failures before further timing.

## Functional mapping, preservation and limitations

[Final functional/install evidence](V1-T10-functional-evidence.md) and [51-suite map](V1-T10-functional-map.json) distinguish 31 fresh T10 suites, one fresh portable PowerShell suite, 16 unchanged reused results and three unverified native Windows suites. Fresh actual Bash/macOS PowerShell installations proved current owned bytes/modes/builds/registrations, preserved user config and complete regular-file idempotence. No live-home install or authenticated provider delivery occurred; native Windows/ACL/junction remain unverified.

All original V1 aggregate failures and the original full **89/468 failed** timing report remain unchanged. [Original-artifact hashes](V1-T10-original-artifacts-preserved.json) retain 24 original fingerprints. New files use V1-T10 names only. Large evidence is losslessly gzip-compressed (`gzip -dc PATH`). Known user/worktree/temporary-user prefixes are neutralized; samples, decisions, input/source hashes and numeric results are unchanged. [Artifact manifest](V1-T10-artifacts.json) records original, redacted-uncompressed and retained SHA-256. Unredacted originals remain in owned temporary state. V1 stays incomplete; primary owns active plan, final KB and worktree lifecycle.
