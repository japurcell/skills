# P05 Copilot baseline independent audit

Native process exits0 in162.913145 seconds, session `dbdc0992-9670-41aa-855f-acfa5406ece0`, observed `gpt-6.1-sol`/`medium`. Original qualification remains invalid with `missing-real-child-receipt` and `receipt-from-unmatched-command`. Original grade is not evaluated, ineligible and marks permission_failure. Raw/run/grade were preserved unchanged.

## Real helper execution and permission

All scored operations use the direct absolute frozen `invoke-scheduler`, with no prepended interpreter, exact pinned scheduler argv and canonical absolute state. Native completion lines780-3314 contain15 scheduler receipts plus one parent-write receipt. Every scheduler before-state equals the preceding after-state, starting empty. Final canonical state equals the final scheduler after-state. No restart, replay or reset appears in this scoring chain. All12 authored action command/child-exit pairs match one native completed call. Evidence paths remain beneath outputs.

These native calls demonstrate acceptance of the narrow direct-helper permission for the exercised operations. They supply stronger evidence than mere successful CLI exit. Safe projected calls, receipts, shell footers and state/action matches are retained in `copilot-baseline-sanitized.json`.

## Precise automated failure causes

- Line166, call `call_YZXPtIQXblgEEN8avCsSJNOp`, cats the frozen helper source, settings and ownership. Source text contains literal `pilot_child`, causing the unmatched-command flag. This is read-only inspection, with no claim of required execution.
- Line137 invokes helper `--state ... --help`. It returns `unsupported scheduler command`, shell exit2, no receipt. This exploratory syntax error contributes missing-receipt invalidity, but supplies no required behavioral proof.
- Line598 invokes supported `register --help`. It returns a genuine exit0 scheduler receipt with `before=null,after=null`. The parser rejects its absent assignment state, although this help operation is read-only.
- Lines2516/2854 are required negative tests, not harmless exploration. Both native tool records have `success=true`, while actual shell footers and helper receipts show exit2. The parser turns transport success into exit0, compares that against receipt2 and discards valid policy rejections. Their actual argv and state proof must remain required when correcting this mismatch.

Actual ancillary permission denials remain visible. Line435 denies redirected help, line5999 denies a Python evidence-saving script, and line10787 denies Python validation. The agent uses apply_patch to retain artifacts. These denials show ordinary narrow controls working. They do not show required direct-helper execution failed. The grader currently labels any such denial permission_failure.

## Independent common assertions

| Assertion | Actual evidence |
| --- | --- |
| exact_output | Required schema, confined final paths,12 unique authored/native action matches. |
| immutable_execution | Exact direct helper and scheduler argv, real completed child receipts. |
| stop_timing | A105/B200 transitions, lines2170/2685, chronological. |
| single_extension | Extension200 at1830, checkpoint150 preserves it at2342, valid ETA250 rejection151 at2516 leaves active extended state unchanged. |
| exclusive_pending_shutdown | Transfer201 exit2 preserves state/old owner at2854, confirmation202 follows at3036. |
| independent_progress | C checkpoint102/completion104 at1656/1998, B shutdown unconfirmed before/after, preceding3036. |
| parent_transfer | Confirmation202, authorization203, real parent update204 at3036/3205/3314, final owner agent-new. |

All seven have independent diagnostic support. Synthetic shutdown remains supplied scenario input. Initial help/tooling mistakes are recorded separately from scorer false flags. This audit changes no original score, makes no efficacy claim from currently ineligible pairs, and executes no model/provider calls or tests.

## Retained audit provenance

[External original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-05/review/copilot-baseline.md), SHA-256 `c679edc236b56e2d5a1acc01c4283247747fff569373bf39a1be88c621b949d9`. Native line references refer to that cell's original external stdout/rollout. This retained Markdown contains no raw session dump.
