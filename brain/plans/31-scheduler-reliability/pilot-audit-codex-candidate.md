# P05 Codex candidate independent audit

Native execution completed with exit0 in337.168054 seconds. Root session `01a1d07d-5170-75b3-a2cb-8dcfcbc61a06` observed Sol/medium. Automated qualification remains invalid with `scenario-state-or-output-invalid`, grade not evaluated and comparison ineligible. `outputs/result.json` exists, has the required actions/final_state schema, uses canonical `outputs/scenario-state.json` and `outputs/ownership.json`, and confines action evidence beneath `outputs/evidence/`.

## Collector gap and actual linked execution

Root stdout contains no helper execution. Root rollout spawn line53, call `call_15ae893395c9451580abeebfd15fe04b`, dispatches `scenario`. Native child `01a1d07e-2114-7863-a5cf-a7757e7059c7` session metadata binds its parent ID and `/root/scenario` path. Actual child contexts at lines9/338 establish `gpt-6-luna`/`medium`. The requested effort was omitted during spawn. Authored coordination says effort unverified, while native context supplies medium. No further descendants were spawned.

The collector scans only root calls, so its empty scheduler-record set explains the state/output invalidity flag despite available linked receipts. Genuine agent errors also prevent treating the whole original phase as one clean chain.

Sanitized native projections with exact source hash, command/receipt lines and full before/after states are retained in `descendants/codex-candidate-sanitized.json`. All26 scheduler and one parent-update receipts complete before root exit. Every scheduler receipt uses the exact frozen scheduler prefix and canonical absolute state. Each generation is internally continuous.

## Initial errors and explicit restart

Initial generation has8 scheduler receipts. Child ticks at100 then105, stopping B before attempting checkpoint102. Checkpoint fails exit2 at line107. It then confirms shutdown202, followed by backdated transfer201, which succeeds at line121 because stop confirmation is already true. This fails the requested premature-transfer rejection and monotonic chronology.

At line145,16:02:48 UTC, the child moves state/lock into `outputs/invalid-attempt/`. Fresh register A at line152 starts with `before=null`. The rejected checkpoint evidence and original state remain preserved. This actual reset breaks continuity across the whole phase. It cannot be erased by choosing only the later sequence.

## Restarted generation, limited diagnostics

The restarted generation has18 scheduler receipts, including two read-only final lists, and one parent update. Its final state matches the current canonical artifact. Each of the8 authored required action commands/exit codes matches one actual restarted native receipt.

| Assertion | Supported restarted observation |
| --- | --- |
| exact_output | Required final schema/paths and8 one-to-one action matches exist. |
| immutable_execution | Direct frozen-helper commands and exact child argv throughout. |
| stop_timing | A105/B200 stop transitions, lines205/226. |
| single_extension | Extension200, checkpoint150 preserving it, then valid ETA250 rejection151 with active/extended unchanged state, lines191/212/219. |
| exclusive_pending_shutdown | Rejected transfer201 preserves state/old owner, confirmation202 follows, lines233/240. |
| independent_progress | C checkpoint102 and completion104 precede B confirmation, lines184/198/240. |
| parent_transfer | Confirmation202, authorization203, actual parent update204, lines240/245/266. |

Candidate acknowledgment is separately supported. Line273 confirms transfer205, exit0, with owner agent-new and evidence `outputs/ownership.json`, after the real parent write. `transfer_completed=true`; the receipt target and later list readbacks match current ownership.

Compared with baseline, this phase exits0 and retains final output, while both contain restarts and root-only collection misses legitimate descendant execution. Child-model/effort differences confound interpretation. These diagnostic observations preserve original invalidity and support no efficacy claim from the ineligible pair. No model/provider calls, tests or original source/evidence edits occurred.

## Retained audit provenance

[External original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-05/review/codex-candidate.md), SHA-256 `578bc02e223b6c8b902d6d1365cf88474773a778bc5b69ba291cbf21be5a6431`. Native line references refer to that cell's original external stdout/rollout. This retained Markdown contains no raw session dump.
