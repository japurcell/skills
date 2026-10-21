The milestone **cannot** be accepted (`Status` remains `in progress`/`open` and `Acceptance: not met`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the composed-behavior proof on the integrated base tree is unrun.

The exact next task is a **milestone integration / verification task** (composed-behavior proof) executed on the base topic branch—either run directly by the coordinator or delegated as the named integration task to a fresh subagent. It must exercise an interrupted install followed by prune and recovery against the integrated base tree, including relevant regression and negative cases, and retain concise evidence of the actual result. If the check fails, keep milestone acceptance unmet, record a repair task in the ExecPlan with prerequisites, and delegate the repair through Step 5.

Reconcile and keep these ExecPlan sections synchronized in the same edit:
- **Milestone state lines** (`Status: done | in progress | open` and `Acceptance: met | not met`)
- **Progress** (the milestone-tagged checklist entry for the combined recovery proof, dated when verified)
- **Concrete Steps** (lead with the next unfinished action or label completed steps)
- **Validation and Acceptance** (record actual integrated test evidence vs expectations)
- **Outcomes & Retrospective** (distinguish completed implementation from pending/completed acceptance)
- **Surprises & Discoveries** and **Decision Log** (if integration reveals findings or scope/repair decisions).
