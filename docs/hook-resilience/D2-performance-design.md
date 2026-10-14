# D2: Remove measured Guardian overhead while preserving hardening

D2 is complete as a bounded diagnosis and design decision on 2026-10-14. T10 owns production implementation and semantic proof; V1 owns final release acceptance. No production source, tests, generator, harness, enforcement budget, logging requirement, or installed home changed in D2. All experiments used disposable copies under `/private/tmp/hook-resilience-d2/` after the coordinator confirmed exclusive quiet measurement ownership.

## Decision and remaining acceptance

Implement three localized changes: avoid eagerly importing POSIX readiness machinery when input or EOF is immediately readable; replace Python iteration over ordinary input bytes with a linear structural-token scan; and avoid compiling the credential-label regex for ASCII labels that cannot contain any of its triggers. Preserve the existing regex as the authority on potential credential labels. Do not retain the separate JSON-byte-count shortcut, which produced no conclusive public-process benefit.

The final disposable two-case probe passes both prescribed warm pairs and cold comparisons. This supports implementation, not release acceptance. The original V1 failure remains failed: 89 of 468 comparisons, 78 distinct cases, including 11 cold-p95 failures. D2 does not explain away, supersede, or waive those observations. T10 must establish security equivalence and V1 must execute the complete prescribed matched procedure on the integrated production repair.

## Source and measurement identity

The baseline is exact extracted `bc52d7d69aaa046ea97e323879402241a01fead7` at `/private/tmp/hook-resilience-v1-phase2/baseline`. D2 starts from detached `1b7c2a39` and private branch `codex/hook-resilience-d2`; its hook runtime is identical to frozen V1 candidate `6c1623ff06d58566cf659658c9a92196b71bff7d`. Later changes are documentation only. Maintained targeted runs verify baseline fingerprints against Git, candidate fingerprints before/after, harness fingerprints, decisions, successful completed logs, and bytecode conditions. All three targeted reports have `errors: []` and `sources_unchanged: true`.

Interpreter: `/Users/adam/.pyenv/versions/3.14.6/bin/python3`, Python 3.14.6, native macOS 26.7.1 arm64. Public launches use the maintained runner's identical interpreter, inputs and isolated logging environment. Warm measurements use two alternating condition pairs, 25 samples and three discarded warmups plus a retained first process. Cold measurements use 25 independent fresh provider copies/homes per condition with zero provider bytecode; OS and standard-library caches remain uncleared. Warm limits stay +2 ms median/+5 ms p95; cold limits stay +5/+10 ms. Profiled timings never participate in acceptance.

## Findings

V1 has a broad fixed shift plus variation. Median of per-case warm median deltas is Copilot 1.738/Gemini 1.570/Codex 1.414 ms in pair 1 and 1.261/2.487/1.808 ms in pair 2. The first exact six-case repeat still fails Codex `write.examples.md` warm pair 1 (+2.035 ms) and `search.literal` in both pairs (+2.753/+2.381 ms). Other selected cases pass that repeat, but this does not resolve their original failures.

Trace against baseline:

- T1, `hooks/families/common.py`: new eager `select` import and Python `for byte in chunk` lexical walk. Three warm-bytecode Codex `-X importtime` observations charge 0.235-0.250 ms to `select`. Common cumulative import cost is 1.263-1.331 ms versus baseline 1.073-1.130 ms.
- T1: three cProfile launches per source/case show the 36,118-byte Gemini UTF-8 envelope's `_read_json_input_text` at 0.529 ms versus baseline 0.126 ms. Tiny inputs are 0.025-0.036 ms, so the byte loop is a size-dependent component rather than the entire fixed shift.
- T6, `hooks/families/reporting.py` and Guardian `sanitize_tool_name`: a clean identifier now reaches a complex `re.search` that compiles once in every new hook process. Three profiled launches show `report_label` around 0.468-0.476 ms, dominated by regex compile/search; the baseline identifier branch is about 0.003-0.004 ms. Successful audit logging sanitizes the tool label even on small allowed calls.
- T6: `report_json_bytes` costs about 0.109-0.123 ms in these profiles, but its printable-ASCII shortcut does not establish a public-process improvement. Leave it alone.
- T2 exact profiles add `_native_shell_shape` at about 0.010 ms cumulative for the tiny Codex case and leave native traversal close to baseline in these probes. There is no measured reason to weaken or redesign profiles. Full-provider-envelope behavior remains intentionally different from the old baseline.

No single profiled number establishes causality. The source trace, distinct small/large public cases, startup tracing and independent single-factor ablations together identify bounded work that can be removed. They do not attribute every tail spike or prove a universal fixed overhead.

## Ablation ledger

All variants retain full public subprocess decisions and completed audit records, with source fingerprints before/after. The first two-pair block ablation has mixed gains and regressions depending on order, so it remains inconclusive. Later diagnostics alternate variant order at every launch and retain 50 raw samples per condition/case after three warmups. These exploratory diagnostics do not replace the release protocol. Paired median confidence intervals below are percentile bootstrap intervals from 10,000 resamples with seed 42; they describe this diagnostic run, not a general latency guarantee.

| Single factor versus unchanged candidate | Copilot clean paired median ms | Gemini UTF-8 paired median ms | Codex literal paired median ms | Decision |
| --- | ---: | ---: | ---: | --- |
| Conservative ASCII label prefilter | -0.258, CI [-0.355,-0.178] | -0.287, CI [-0.417,-0.241] | -0.102, CI [-0.310,+0.046] | Select for Copilot/Gemini benefit; Codex inconclusive |
| Printable-ASCII exact JSON byte count | -0.083, CI crosses zero | -0.081, CI crosses zero | -0.048, CI crosses zero | Discard |
| POSIX nonblocking read before readiness import | -0.186, CI [-0.432,-0.054] | -0.297, CI [-0.502,-0.213] | -0.301, CI [-0.352,-0.232] | Select |
| C structural-token scan instead of every byte | -0.023, CI crosses zero | -0.307, CI [-0.404,-0.175] | +0.006, CI crosses zero | Select for larger envelopes; no tiny-case gain claimed |

A six-case combined prefilter/nonblocking probe passes 17/18 comparisons but retains Gemini UTF-8 pair-1 median +2.061 ms as a failure. Pair 2 is +1.448 ms. This unresolved case motivates the independently measured structural-token change.

The final combined design was checked only on the remaining UTF-8 case and persistent tiny Codex literal case:

| Exact public case | Warm pair 1 median/p95 delta ms | Warm pair 2 median/p95 delta ms | Cold median/p95 delta ms |
| --- | --- | --- | --- |
| `gemini.guard.write.utf8-growth` | +0.071/+0.632 | +0.151/+0.592 | +2.209/+3.472 |
| `codex.guard.search.literal` | +0.755/+0.885 | +1.117/+0.964 | +1.722/+1.541 |

All six comparisons meet unchanged allowances; `release_acceptance_eligible` is false because exact filters were used and the root is a disposable ablation. These are not a rerun of all failed cases or security acceptance of the prototype.

## T10 implementation contract

Own canonical `hooks/families/common.py` and `hooks/families/reporting.py`, focused transport/reporting tests, and generator-owned outputs resulting from these inputs. Keep `hooks/families/tool_guard.py` policy/profile classification unchanged except a narrowly necessary import/interface adjustment. Do not edit generated helpers directly. Activate TDD and reproduce exact public cases before source edits. Disposable diffs are prototypes to review, not patches to transplant without proof.

### Immediate reads with unchanged readiness fallback

Introduce `_read_stdin_chunk(stdin_fd, max_bytes, timeout)` returning bytes, or `None` when readiness times out. POSIX first tries `os.read` with nonblocking mode temporarily enabled. Restore the original descriptor blocking flag in `finally`, on data, EOF, timeout and error. If the immediate read raises `BlockingIOError`, call existing bounded `_stdin_is_ready` with the supplied timeout and read only if ready. Move POSIX `import select` into that readiness path. Existing Windows `PeekNamedPipe` remains the readiness authority; do not assume POSIX descriptor behavior there.

Use this helper in initial/chunk acquisition and trailing drain. `None` means incomplete-input denial in acquisition and completion of a zero-time drain; `b""` means EOF. Keep raw-byte charging before append, 2 MiB ceiling, per-read length cap, nonextendable two-second deadline, 0.5-second first-byte/incomplete idle deadline, bounded trailing drain, UTF-8 decoding, native failure behavior and fail-closed exceptions. Recheck the total deadline at existing boundaries. The fast path must preserve transport authority and open-stdin completion.

### Linear structural-token scanning

In `_read_json_input_text`, scan only ASCII quote, backslash, braces and brackets using a fixed byte regex with no nested repetition. The exact tested iteration is `for match in re.finditer(rb'["\\\[\]{}]', chunk):`, also retained in `ablations.diff`. Ordinary bytes inside already-started JSON have no lexical state effect and can be skipped in C; `json.loads` remains the complete syntax validator after bounded collection. A regex match is a lexical marker, not proof that JSON is valid.

Preserve `started`, container stack, `in_string`, `escaped` and `complete`. Track each marker's byte position. An escaped marker is consumed only if it immediately follows the pending backslash; intervening ordinary bytes consume the escape first. Carry a final backslash at the last chunk byte across chunks; clear it if ordinary bytes follow within the chunk. Validate pre-object and post-completion slices as JSON whitespace. Reject initial arrays, mismatched closers and depth above 64. Continue checking every structural marker outside strings so skipping safe bytes cannot skip depth limits or treat braces inside strings as containers. Avoid repeatedly searching a growing prefix or rescanning remaining suffixes once per escape. Keep each chunk bounded at 65,536 bytes and existing deadline checks.

A disposable differential test compares current and token-scan collectors on 1,504 valid, truncated, trailing and depth-boundary inputs at chunk widths 1,2,3,7,64 and 65,536: 9,024 matched outcomes, zero mismatches. This supports the state design; it does not replace public retained-pipe and timeout tests.

### Credential prefilter with original regex authority

In `report_label`, normalize and bound original input exactly as now, before clipping or shortcuts. Only when this normalized string is ASCII may a cheap lowercase literal prefilter bypass regex compilation. Conservative trigger substrings must cover every alternative in the existing expression: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, `github_pat_`, `akia`, `sk-`, `sk_live_`, `xoxb-`, `xoxa-`, `xoxp-`, `xoxr-`, `xoxs-`, `bearer`, `token`, `secret`, `password`, `passwd`, `api`, `authorization`, `http`. If any appears anywhere, run the unchanged regex and whole-label omission behavior. If none appears, return existing `report_text(text)`. Non-ASCII normalized strings always use the existing regex, preserving Unicode ignore-case behavior without reproducing it through lowercase logic. Calculate lowercase once. Do not replace this with known-tool allowlisting or prefix-only checks.

The conservative list permits extra regex work, not missed credential matches. Embedded tokens, prefixed identifiers, NFKC forms and credentials crossing the 160-character clipping boundary remain whole-label redactions. Attribution fields, report caps, audit failure enforcement and strict fallback remain intact.

## Required proof and stopping boundary

Before production changes, retain the exact failing public reproducer and logging result. Extend public transport tests for structural bytes and escape parity across relevant chunk splits, escaped backslash/quote combinations, braces in strings, long ordinary spans, split UTF-8, depth 64/65, malformed/trailing data, bounded drain, first-byte/incomplete/total deadlines and complete JSON with open stdin. Include POSIX descriptor-flag restoration on success and failure, and readiness controls showing EAGAIN invokes the deadline path. Preserve pre-3.12 Windows readiness; simulated tests do not prove native Windows execution.

Extend reporting tests with ASCII clean labels, every trigger in mixed case and embedded positions, non-ASCII regex case behavior, NFKC forms, clipping-boundary tokens, block/warn/clean logs and audit-failure controls. Keep exact report-byte assertions and security outcomes. Add a differential oracle for any new lexical helper using independent JSON expectations and explicit depth policy; do not copy implementation into expected values.

Run `rtk proxy python3 scripts/generate-hooks.py --write`, then `--check`. Focused semantic commands include `scripts/test-hook-input-bounds.py`, `scripts/test-security-reporting.py`, `scripts/test-security-banners.py`, `scripts/test-tool-guard-native-data.py`, `scripts/test-tool-guard-shell-data.py`, `scripts/test-tool-guard-limits.py`, `scripts/test-tool-guard-false-positives.py`, and affected common/scanner/recovery/diagnostic suites selected through testing routes. Shared common/reporting changes affect more than Guardian, so run affected registered suites and freshness before final release validation. Never remove a failing test or relax budgets.

After semantic proof, coordinate a quiet window and repeat representative exact matched probes against the real generated repair. Full V1 still requires all 156 cases, two warm pairs and 25 cold launches per condition, the finite-input 500 ms resource gate, successful logging and unchanged source/harness checks. Retain and investigate every new violation. Another full run waits for T10 repair and focused proof.

## Retained evidence and reproduction

[Compact evidence archive](D2-performance-evidence.tar.gz): 46 members, 591,984 bytes, SHA-256 `0037d5ea5072b79a7db07bacfe24937e6b1176e7f80bc7a3bd87ea65398a2f32`. `SHA256.json` hashes every other archive member. Retained: three exact targeted reports with raw first/warm/cold samples and output/log proof; inconclusive block ablation; interleaved samples and summaries; bootstrap summaries; 18 binary profiles plus summarized profile report; six import-time traces; lexical parity evidence; probe scripts; and `ablations.diff` for every tested variant. Git refs plus diffs reconstruct source. Full source copies, homes and routine logs are excluded. Working artifacts remain under `/private/tmp/hook-resilience-d2/` through T10/V1.

Scripts use recorded temporary paths and need path adaptation after extraction. `profile.py` produces profiled diagnostics; `ablation.py`, `interleaved.py`, `nonblocking.py` and `structural.py` are disposable drivers using maintained case/invocation/logging functions. The diff supplies final variants assembled from independent changes. No result proves native Windows, authenticated provider dispatch, live installation or full release acceptance. Prior V1 resource/RSS proof remains separate; D2 did not rerun RSS.

From repository root, maintained exact repeats use `rtk proxy python3 scripts/verify-hook-release.py --baseline-root /private/tmp/hook-resilience-v1-phase2/baseline --candidate-root ROOT --case NAME --output NEW.json`. Repeat `--case` for selected cases and never overwrite reports. Six-case set: Copilot clean and writer `chars-8787-segments-183`, Gemini `write.utf8-growth`, Codex `write.examples.md`, `write.examples.test.py`, `search.literal`. Final selected set: only Gemini UTF-8 and Codex literal. Preserve disposable successful logging, bytecode and maintained counts; mechanics-only output is not timing proof.

The coordinator owns active ExecPlan reconciliation and the single final knowledge-maintenance pass. D2 leaves production code unchanged, with a concrete owner boundary and original failed evidence still operative.
