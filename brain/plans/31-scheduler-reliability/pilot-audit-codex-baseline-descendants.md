# P05 Codex baseline linked-descendant audit

The original outcome remains timeout 124, absent final `outputs/result.json`, invalid setup and comparison ineligibility. Linked native receipts support additional diagnostic observations. They do not convert the original phase into a valid score.

## Linkage and limits

Root rollout spawn calls at lines 50/86 returned `/root/scenario` and `/root/repair_scenario` at lines 53/89. Exact timestamp-matched native files establish those handles through `session_meta.source.subagent.thread_spawn.agent_path` and parent ID `01a1d072-43fb-7503-98d8-e87f01a66f31`.

- Initial child `01a1d072-f49a-7041-bef3-c70608778593` has actual turn context `gpt-6-luna`/`medium` at line 9.
- Repair child `01a1d074-df0a-79f3-ae5f-e86de426ede9` has actual child context `gpt-6-luna`/`max` at line 53. Its line-10 Sol/medium context belongs to inherited parent history, excluded from child execution.

Neither child spawned further descendants. These selectors confound any fixed-model interpretation of root Sol/medium. Exact safe projections, source paths/hashes, command lines, receipts and before/after states are frozen in `descendants/codex-baseline-sanitized.json`. Raw encrypted content was excluded from that artifact. No raw copy was required.

## Actual execution and reset

Initial child has 14 scheduler receipts plus one parent update. All scheduler `before` states join the preceding `after` state, starting empty, and final state matches `outputs/attempt-1/scenario-state.json`. Exact direct frozen helper commands invoke `python3` plus the pinned scheduler and canonical absolute state. Helper bytes match manifest hash `6a90409b727a14619c312e8a59c417712edc46cc9d59a30e9b534222275add66`, mode0500, shebang `/Users/adam/.pyenv/versions/3.14.6/bin/python3.14`.

Initial child executes C checkpoint102 after extension103, then performs extension151 only after parent-update204. Receipt line133 shows B already stopped/confirmed and parent already agent-new. That exit2 fails the required active-extended-state rejection. Checkpoint150 is absent.

Repair child line73 executes `mkdir -p outputs/attempt-1 && mv ... outputs/attempt-1/`, completing exit0 at line76, 15:51:37.449 UTC. This moves old state, ownership, result and evidence. Fresh register A at line84 has `before=null`. Ownership is absent during early repair receipts, then recreated with owner agent-old by patch line159 at15:53:05.

Repair has 15 continuous scheduler receipts plus parent-update. Required chronological operations complete through line197 at15:53:29.425. Final canonical state matches its last scheduler receipt. Every extracted helper result precedes parent cutoff15:58:32. No later output is included. Repair ends with evidence-file authoring through15:58:21 and supplies no final result.

## Common assertions, diagnostic observations

| Assertion | Initial generation | Repair generation |
| --- | --- | --- |
| exact_output | Earlier result exists, evidence command strings mismatch actual absolute commands | Missing final result |
| immutable_execution | Real linked helper receipts | Real linked helper receipts |
| stop_timing | Local A105/B200 stops observed, global chronology fails | Supported, lines141/169 |
| single_extension | Partial, checkpoint150 missing and rejection151 backdated/wrong state | Supported, lines127/148/155 |
| exclusive_pending_shutdown | Supported locally, lines98/105 | Supported, lines176/183 |
| independent_progress | C completes before B confirmation, lines72/79/105 | Supported, lines120/134/183 |
| parent_transfer | Stop confirmation, authorization, then real parent update, lines105/112/126 | Supported, lines183/190/197 |

Both generations are retained separately. Concatenation would cross a reset and break state continuity. Root-only collection missed these real descendant receipts. The earlier harmless-source-read flag remains overbroad, while timeout, missing final result, restart and initial sequencing errors remain genuine. No efficacy claim follows. No provider calls, tests, source edits or original evidence modifications occurred.

## Retained audit provenance

[External original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-05/review/codex-baseline-descendants.md), SHA-256 `c984cf8f803a9818e5f757c87f6268b65d5837868773af51615d1909ab9e2a10`. Native line references refer to that cell's original external stdout/rollout. This retained Markdown contains no raw session dump.
