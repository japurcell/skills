# B2. Capture the Codex baseline

Owner: Codex operator and later integration coordinator. Prerequisites: reviewed architecture and 7fc651a7 caller/router sources. Earlier Codex 0.170.0 rejected a non-repository scratch folder. That fixture now has its own Git repository. Inspect `codex features list` and use a disposable project with the provider's normal authentication. Only disposable fixture writes are needed.

Exercise delegate-to-subagents and execplan-implement separately. Each operator uses the pinned skill to delegate a quick job and a silent bounded job. Collect a native worker start, timestamped early completion, quiet waiting, and action on the outstanding worker deadline. Pin actual source, CLI version, session and child IDs, commands, return values and native evidence. Retain traces privately and only summarize benign observations. Missing native events or service access leave the case unresolved. Stop after baseline verdicts or a verified host blocker; no candidate trials. Relay exact recovery conditions to parent.

## Baseline verdict

Both pinned callers launched real workers in Codex CLI 0.170.0. Enable `multi_agent_v2` only for the invocation and use a persistent session. Verify actual native child IDs in the saved rollouts because JSON stdout can omit the spawn. An independent positive control produced a child result in 3.56 seconds. The full sanitized attempt ledger, command lines, fixture paths and timestamps are in `/private/tmp/todo38-1795057091956/codex/codex.md`.

| Old caller | Early completion | Silent deadline and shutdown |
| --- | --- | --- |
| Delegate | First quick child `01a1f1db-cbf4-70f1-a6da-d760cccc69a8` completed at 03:31:21.675Z on November 19. | Parent contacted the first silent worker early and dispatched additional pairs for the same work. For the last silent worker, the saved deadline was 03:36:30.068Z and grace ended at 03:36:34.138Z. The interrupt came at 03:36:39.420Z. The helper record stayed active with shutdown unconfirmed. |
| ExecPlan | Child `01a1f1e3-eaf9-79e3-ac1d-7de10d93f377` completed at 03:40:24.040Z while the silent worker was active. The quick output bytes were verified. | The parent kept no durable registry. It contacted the silent worker 3.469 seconds after the task's target deadline and interrupted it 8.502 seconds beyond the expected grace. Its shell operation finished a further 6.090 seconds after interruption. |

Neither caller passed the full baseline. Use fresh paths for N1, establish the actual nearest-deadline alarm and check the outstanding operation independently of the worker thread state.
