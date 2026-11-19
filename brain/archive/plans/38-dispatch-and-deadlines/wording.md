# W1. Screen wording on controlled dispatch cases

Owner: wording evaluator. Source baseline: `7fc651a7702735f0b13d1f50695a8ef0ddc96477`. Do not publish caller changes before P1. The shortest controlled survivor is a test result, not publication approval.

## Method

- Source fixture text and replay tools are in `scripts/tests/orchestration/`.
- Render complete caller and router skills with `python3 scripts/tests/orchestration/render_variants.py <outdir>`.
- The original trials ran one fresh Codex CLI actor per caller and arm. The current runner prepares the fixture offline by default. See the [replay instructions](../../../../scripts/tests/orchestration/README.md) for the live opt-in.
- Inputs use neutral `case01` through `case16` IDs. Actor projects contain only public task and host facts. Hidden success and rejection outcomes stay outside those projects and appear in the local event trace only after an action.
- The authenticated Codex CLI used the configured default `gpt-6.2-astra`, effort `high`, with no model or effort flag in the actor command. Codex JSONL did not report a resolved model field; the configured default is captured separately. The user explicitly approved sending the two caller skills, router instructions, and synthetic cases to authenticated providers. Credentials and remote traces were excluded. All evidence remains local under `/private/tmp/todo38-1795057091956/`.
- `grade_events.py` grades only router output and observable controlled dispatch/reuse actions, not actor prose. It requires one valid router result and host snapshot for each expected case, rejects missing, duplicate, or arbitrary IDs, disallows reuse on blocked cases, and requires worker IDs for positive dispatch receipts. `case_records.py` composes before/after evidence from those events. `extract_tool_order.py` retains native Codex command start/completion order.

## Cases

| ID | Controlled case | Expected observable decision |
| --- | --- | --- |
| 01 | Routed model is known-disallowed | Zero attempts for the disallowed model. |
| 02 | Routed model is absent from descriptive help | One successful launch. |
| 03 | Availability unknown, then model-wide rejection | One rejected attempt for that model, no effort retry, then successful routed fallback at the capability floor. |
| 04 | Explicit policy with user-selected high effort | Dispatch with high effort despite the router's medium effort. |
| 05 | Host-default policy | Omit effort. |
| 06 | `route_available: false`, no exact user model | Block. |
| 07 | `route_available: false`, exact user model supplied | Dispatch the exact user model if host controls permit. |
| 08 | Exact user model is host-disallowed | Block despite the user override. |
| 09 | Model control missing | Block. |
| 10 | Explicit effort control missing | Block. |
| 11 | Primary is disallowed, fallback meets the same capability floor | Skip the denied primary and complete on the permitted fallback. |
| 12 | Existing host-default worker uses a different model | Do not reuse; dispatch a fresh worker. |
| 13 | Existing host-default worker uses the same model, has no original effort override, and has useful context | Reuse. |
| 14 | Existing host-default worker has an original explicit effort override | Do not reuse; dispatch a fresh worker. |
| 15 | Existing explicit worker matches model and effort and has useful context | Reuse. |
| 16 | Existing worker has no useful context | Do not reuse; dispatch a fresh worker. |

## Results

Six frozen baseline/short/challenger caller-arm trials each passed 23/23 event checks. Each recorded 16 router calls, 16 host snapshots, 11 dispatch attempts (9 completed, 2 rejected), and 2 successful reuses on cases 13 and 15.

| Caller | Baseline | Short candidate | One-clause-shorter challenger |
| --- | ---: | ---: | ---: |
| delegate-to-subagents | 266 words, pass | 177 words, pass | 172 words, pass |
| execplan-implement | 312 words, pass | 220 words, pass | 215 words, pass |

The additional `challenger2` removed the host-default original-effort-override reuse condition. Both callers failed 22/23 checks on case 14. In both logs Codex reused the same-model worker even though its original effort override was true. Case 12 remained correct: the different-model worker was not reused. This makes the original-effort-override condition behavior-bearing.

After review, every non-baseline router render retained the standalone sentence `Return the CLI's JSON result unchanged.` in the `Route` section. Its six words are reported separately and excluded from gate counts for every arm. Fresh full-source short and challenger trials on both callers each passed 23/23 checks. Thus the shortest tested survivor remains challenger at 172 words for delegate and 215 for ExecPlan.

The challenger removes `Never call a known-disallowed model.` and still passed case 01 in both callers: the actor made no attempt on the known-disallowed routed model. It attempted the permitted fallback, which the controlled host rejected, then reported a blocker. Case 03 recorded exactly one model-wide rejection for the primary and a completed fallback, with no retry of the primary.

No published `SKILL.md` was modified. Parent owns P1 and publication. Do not treat actor-authored summaries as dispatch evidence.

## Counts and full-text hashes

Counts use whitespace-delimited words from the rendered caller gate body, selected outside-gate caller reuse instructions, and rendered router dispatch body. Headings are excluded. The stable six-word standalone router sentence is separate. `counts.json` from the final renderer includes complete caller and router SHA-256 hashes for every arm:

- `/private/tmp/todo38-1795057091956/w1-final/rendered/counts.json`
- Full rendered finalist skill bytes: `/private/tmp/todo38-1795057091956/w1-final/rendered/{short,challenger}/{delegate-to-subagents,execplan-implement}/`

## Local evidence

- Initial six controlled trials and full native Codex JSONL: `/private/tmp/todo38-1795057091956/w1-codex-evals2/`
- Extra `challenger2` counterexample trials: `/private/tmp/todo38-1795057091956/w1-challenger2/`
- Final full-source four finalist trials with the retained sentence: `/private/tmp/todo38-1795057091956/w1-final/evidence/`
- Each valid trial directory contains `codex-events.jsonl`, `tool-order.jsonl`, `host-model.json`, `case-records.jsonl`, `verdict.json`, `stderr.txt`, and `exit-code.txt`; the matching project has `.w1/events.jsonl`, route inputs and outputs, and `actor-report.txt`.
- The first actor prompt contained expected decisions and is invalid calibration. Preserve it at `/private/tmp/todo38-1795057091956/w1-codex-evals/`. Provider initialization/setup failures are also retained in their separate scratch paths and were not graded.

## Sanitized run evidence

- Initial controlled run IDs: `baseline-{delegate-to-subagents,execplan-implement}`, `short-{delegate-to-subagents,execplan-implement}`, and `challenger-{delegate-to-subagents,execplan-implement}`. All six passed 23/23. Each had 16 routes, 16 host snapshots, 11 dispatch attempts (9 completed, 2 rejected), and 2 successful reuses.
- Counterexample run IDs: `challenger2-{delegate-to-subagents,execplan-implement}`. Both scored 22/23; case14 was the sole failure because the original explicit effort override did not prevent reuse.
- Full-source final retests: `short-{delegate-to-subagents,execplan-implement}-finalrun1` and `challenger-{delegate-to-subagents,execplan-implement}-finalrun1`. All four passed 23/23.
- Final rendered caller hashes are identical between short and challenger: delegate `5b25b7a0c32a8ba8707e81bfa49a685cf1da7578bb55bb02ad0329fc1871f419`; ExecPlan `f870078fc8cea4d3a4f223bea2573d81edc00050dae95cf7595442cfc401193d`. Shared router hash: short `58be74a870520bf019522be4ff53c33dd1e7c53c236f72b70694ecd58d026ae2`; challenger `a5dfc40bffdf76d65e94e76882467ddeb40c42ff0248ebdb45ef89129187ee33`.
- Decision-relevant difference: challenger omits the standalone known-disallowed prohibition yet still made zero attempts on the routed disallowed model in case01; challenger2 additionally omitted the original-effort-override reuse condition and failed case14. Keep short and challenger as controlled survivors for P1 review; this record does not authorize publication.

## Local verification

`rtk python3 -m unittest discover -s scripts/tests/orchestration -p 'test_*.py' -v` passed 9 tests after final sentence rendering. The router CLI in the fixtures is copied from the pinned baseline revision and invoked for every case.
