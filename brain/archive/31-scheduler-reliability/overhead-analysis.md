# Retained scheduler overhead analysis

## Finding and scope

The eight eligible Codex A/B cells support a context-reading and extra-tool-turn mechanism, not scheduler execution overhead. Every candidate reads its README; two also read the full scheduler source. No A/B cell invokes the scheduler CLI or router CLI. B reads router instructions in both variants. All eight produce a written simulation with 3/3 common assertions and a valid output contract. The sample does not show a behavior improvement or isolate a causal latency contribution.

This is read-only analysis of [the retained benchmark](../../archive/plans/31-scheduler-evaluation/benchmark.json), checked against every A/B cell's raw native JSONL, run argv, prompt, timing and provider metrics. No provider call, optimization, or source change was performed. The older experiment's `old_skill` and `with_skill` snapshots are the compared variants; this is not a measurement of the new v2-versus-v3 pilot.

Evidence root: `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/`. Each timeline link below identifies the complete native file; line numbers are physical JSONL lines. `run.json`, `prompt.md` and `evidence/timing.json` are siblings relative to each linked cell. The `/var` and `/private/var` spellings identify the same retained files on this host.

## Per-cell ordered timelines

Each cell has `thread.started` at line 1 and exactly one `turn.started` at line 2. The event pairs below are starts/completions, not durations. All listed shell completions exit 0. The last message precedes the final `turn.completed` usage record. File-change start/completion is one operation, not two writes. A/B prompts expressly prohibit scheduler invocation and dispatch; router reads are instruction delivery, not routing or native worker dispatch.

| Cell | Native event timeline | Whole process seconds |
|---|---|---:|
| [A baseline r1](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-A/codex/old_skill/repeat-1/evidence/stdout.jsonl) | L3 announcement; L4-5 selected SKILL read; L6-7 add exact repo/outputs/result.json; L8 final message; L9 usage. | 33.519828 |
| [A baseline r2](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-A/codex/old_skill/repeat-2/evidence/stdout.jsonl) | L3 announcement; L4-5 RTK version; L6-7 selected SKILL read; L8-9 one Python heredoc authors result.json; L10 final; L11 usage. | 35.336385 |
| [A current r1](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-A/codex/with_skill/repeat-1/evidence/stdout.jsonl) | L3 announcement; L4-5 RTK version; L6-7 selected SKILL read; L8-9 README read; L10-11 full scheduler.py source read; L12-13 add result.json; L14 final; L15 usage. | 44.571111 |
| [A current r2](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-A/codex/with_skill/repeat-2/evidence/stdout.jsonl) | L3 announcement; L4-5 selected SKILL read; L6-7 README read; L8-9 add result.json; L10 final; L11 usage. | 40.450379 |
| [B baseline r1](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-B/codex/old_skill/repeat-1/evidence/stdout.jsonl) | L3 announcement; L4-5 RTK version; L6-7 selected SKILL read; L8-9 router SKILL read; L10-11 add result.json; L12-13 Python validates its schema; L14 final; L15 usage. | 61.151280 |
| [B baseline r2](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-B/codex/old_skill/repeat-2/evidence/stdout.jsonl) | L3 announcement; L4-5 selected SKILL read; L6-7 router SKILL read; L8-9 one Python heredoc authors result.json; L10 final; L11 usage. | 56.471811 |
| [B current r1](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-B/codex/with_skill/repeat-1/evidence/stdout.jsonl) | L3 announcement; L4-5 selected SKILL read; L6-7 router SKILL read; L8-9 README read; L10-11 add result.json; L12 final; L13 usage. | 65.822003 |
| [B current r2](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-eval-09vb9n1r/harness/prepared-matrix-t3-attempt-1/iteration-1/eval-B/codex/with_skill/repeat-2/evidence/stdout.jsonl) | L3 announcement; L4-5 RTK version; L6-7 selected SKILL read; L8-9 router SKILL read; L10-11 list selected bundle; L12-13 README read; L14-15 full scheduler.py source read; L16-17 add result.json; L18-19 Python validates schema; L20 final; L21 usage. | 64.054003 |

There are no repeated explicit reads of the same selected SKILL within any cell. Repeated model context ingestion is a plausible consequence of multiple tool continuations, not an observed sequence of duplicate SKILL reads. Shell-call counts are A r1 1 versus 4, A r2 3 versus 2, B r1 4 versus 3, B r2 3 versus 7 (baseline versus current). Thus extra call count alone does not explain every positive latency delta: A r2 and B r1 are slower despite fewer shell calls. Output authoring also differs: patch/file-change versus Python heredoc, and schema validation is optional in these traces. No A/B cell batches multiple scheduler operations, because none executes them.

## Native counter reconciliation

All eight final `turn.completed.usage` records exactly match benchmark input/cache/output/reasoning fields and `provider_metrics.json`. Each `timing.json.elapsed_monotonic_seconds` exactly matches its benchmark elapsed field, with exit 0 and 600-second timeout. Counters are whole provider-turn totals; there are no per-read, per-command, or per-continuation token counters. Cached input is a subset of input; reasoning output is a subset of output. All eight report `cache_write_input_tokens=0`. Derived noncached input below is input minus cached, not an additional counter to add. No bytes, output characters, or file length have been substituted for tokens.

| Cell | Input | Cached subset | Noncached derived | Output | Reasoning subset |
|---|---:|---:|---:|---:|---:|
| A baseline r1 | 75863 | 57600 | 18263 | 1221 | 93 |
| A baseline r2 | 75971 | 57600 | 18371 | 1183 | 164 |
| A current r1 | 110191 | 87424 | 22767 | 1500 | 79 |
| A current r2 | 102957 | 83712 | 19245 | 1245 | 70 |
| B baseline r1 | 81085 | 68480 | 12605 | 2613 | 89 |
| B baseline r2 | 105472 | 85120 | 20352 | 1850 | 105 |
| B current r1 | 107948 | 86912 | 21036 | 2524 | 125 |
| B current r2 | 175950 | 150912 | 25038 | 2384 | 82 |

| Matched current minus baseline | Seconds | Input | Cached subset | Noncached derived | Output | Reasoning subset |
|---|---:|---:|---:|---:|---:|---:|
| A r1 | +11.051283 | +34328 | +29824 | +4504 | +279 | -14 |
| A r2 | +5.113994 | +26986 | +26112 | +874 | +62 | -94 |
| B r1 | +4.670723 | +26863 | +18432 | +8431 | -89 | +36 |
| B r2 | +7.582191 | +70478 | +65792 | +4686 | +534 | -23 |

The A mean is +8.082638 seconds, +30,657 input, +27,968 cached subset, +2,689 noncached derived and +170.5 output. B mean is +6.126457 seconds, +48,670.5 input, +42,112 cached subset, +6,558.5 noncached derived and +222.5 output. These reproduce the archived rounded +8.1/+6.1 seconds and token deltas. In B r2, 65,792 of the 70,478 extra reported input is cached input, consistent with more accumulated-context processing. That does not establish which tool read caused which tokens.

## Supported mechanisms and attribution limits

- Additional context is directly observed: current README reads in all four cells and source reads in A r1/B r2. The old SKILL snapshot is 3,378 bytes; current SKILL is 3,863, README 3,243 and scheduler source 13,854. These are artifact byte sizes only. They cannot explain +26,863 to +70,478 cumulative input by treating bytes as unique tokens. Tool results, instructions, prior messages and earlier generated content can be reprocessed across continuations; native cumulative input is not unique skill-body size.
- B r2 directly shows the most exploration: selected body, router body, directory listing, README, source, authoring and validation. It has the largest input delta and four extra shell calls. This supports an exploration/context mechanism. A r1 similarly adds README/source. A r2 and B r1 show that different turn structure, context size and generation remain confounded with the extra read.
- Exact latency attribution is unavailable for every cell. Raw JSONL records have event order but no timestamps, durations or per-command wall clocks. `started_utc` is only a process start label; `timing.json` supplies one monotonic whole-process duration. Consequently the entire 33.519828-65.822003 seconds per cell, and each +4.670723 to +11.051283 paired delta, cannot be partitioned numerically among CLI startup, service/queue/network time, model computation, read execution, writing or idle gaps. This is not evidence those components cost zero.
- Exact token attribution is likewise unavailable: the observed additional reads are mechanisms, not measured token shares. The entire paired input/output delta remains unattributed to individual actions. Output is separately measured and does not track latency monotonically: B r1 emits 89 fewer output tokens yet takes 4.670723 seconds longer. Reasoning counters are small subsets and do not establish reasoning time.
- All eight requested `gpt-6.1-sol` and medium reasoning in `run.json.argv`. Raw Codex native events expose thread identity and usage, not an independently resolved model/effort. The `provider_metrics.json.model` label does not establish independent observation. Requested and observed model identity must remain distinct.
- Whole-process scored timing excludes preparation, smoke, approval, coordinator work and later review. Those operations are absent from the timed subprocess scope. The retained harness starts its monotonic timer immediately before provider Popen and ends after communicate/exit; it does not retain tool-level timing. No available evidence assigns setup or smoke tokens to a scored A/B turn.

## C and Copilot are confounds, not extra attribution samples

C changes the task from written simulation to actual disposable CLI execution. Candidate prompts additionally require every scheduler operation in a separate shell call and an exact state path; baseline may construct its own equivalent mechanism and batch. Codex C baseline r1 has 27 completed shell events, r2 23; current has 26 and 33, with 16 and 15 scheduler-path command events respectively. A wrapper event can contain multiple subprocesses, so these are not subprocess counts. These structurally different workloads cannot explain A/B read latency or isolate scheduler speed.

C native references: current r1 `eval-C/codex/with_skill/repeat-1/evidence/stdout.jsonl` L26,30,34,38,42,46,50,54,58,62,66,70,75,79,83,87; current r2 same suffix under repeat-2 L34,36,38,40,42,44,46,48,50,52,57,61,63,67,69. Baseline r1 L18/L22 executes its own test scheduler; r2 L29/L31 begins its own parent scheduler calls. Paths are relative to the evidence root above. Inspect each cell's `prompt.md` final paragraph for the asymmetric separate-call requirement. C shutdown/write facts remain synthetic, and authorization does not prove parent transfer completion.

Copilot has no eligible A pair and only one B pair after access revisions. Its B candidate also writes the wrong output location (`eval-B/copilot/with_skill/repeat-2/evidence/stdout.jsonl` L2029/L2211); semantic 3/3 does not repair that output contract. Copilot C baseline required shell commands were denied (baseline r2 L3428-3430); current execution versus denied baseline is not a causal speed/quality comparison. Copilot native tool names and modelMetrics/session tokenDetails have different granularity from Codex command events/counters; preserve them separately. The archived report/benchmark remain authoritative for these exclusion categories; this analysis does not pool providers or reinterpret failures as improvement.

## Recommendation and completion evidence

No scheduler source optimization is supported by A/B: the scheduler did not execute there. A separately authorized experiment could test whether runtime guidance triggers unnecessary source/README exploration in a prose-only task, with an explicit target of reducing extra reads while retaining all behavioral assertions, exact output contracts and selected-body delivery. Do not change instructions from this small correlation alone. Before a timing attribution experiment, retain native per-event timestamps and per-request usage where the provider exposes them; explicitly mark unavailable telemetry rather than estimating it. Keep scored execution, smoke and coordinator/review time separate and match call granularity.

Validation was read-only: parsed all eight native streams and asserted equality of four usage counters plus elapsed time against the benchmark, inspected every native event and authored-output path, recomputed all four paired deltas and both means. All checks agreed. No live calls or tests of scheduler correctness were part of this task. The result is a bounded mechanism explanation with explicit unmeasured shares, not an optimization, causal estimate or reliability claim.
