The milestone cannot be accepted (`Status` must remain `in progress` and `Acceptance: not met`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the combined proof remains unrun on the integrated tree.

The exact next task is the milestone's **composed-behavior proof / integration verification task** executed against the integrated base branch (exercising interrupted install followed by prune and recovery, including relevant regression and negative cases). Because this is verification work on already-merged code, it requires task-appropriate verification evidence rather than new product code or empty commits. If the check fails, keep acceptance unmet, record an unfinished repair task with prerequisites, and return to the execution loop.

Keep these ExecPlan sections synchronized in the same edit:
- **Milestone state lines:** Keep `Status: in progress` and `Acceptance: not met` until the combined recovery proof passes; only set `Status: done` and `Acceptance: met` together with the final evidence.
- **Progress:** Keep the milestone integration check entry unchecked until verified; date and check it upon completion.
- **Concrete Steps:** Lead with the unfinished combined recovery check (or label completed implementation steps as completed and show observed evidence).
- **Validation and Acceptance** (and `Artifacts and Notes` if used): Record the actual command and observed recovery output, distinguishing expectations from verified evidence.
- **Outcomes & Retrospective:** Distinguish completed implementation from pending milestone acceptance.
