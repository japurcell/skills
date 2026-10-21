The milestone cannot be accepted. Keep `Acceptance: not met` (and `Status` not `done`). Passing individual task tests and clean Git merges do not establish milestone acceptance while the plan's composed-behavior proof on the integrated base tree remains unrun.

The exact next task is the named milestone integration / composed-behavior verification task on the integrated base branch (exercising interrupted install followed by prune and recovery, plus relevant regression and negative cases, locally on base or delegated as the named integration task). Because it is verification-only, it must produce task-appropriate verification evidence without inventing product code changes or empty commits.

When reconciling and after running the check, keep these ExecPlan sections synchronized in the same edit:
- Milestone state lines (`Status: in progress | done` and `Acceptance: not met | met`).
- `Progress` (keep the combined-proof `[milestone-X]` entry unchecked until verified; date and check it only with actual evidence).
- `Concrete Steps` (lead with the unfinished integration check now; mark completed after it runs).
- `Validation and Acceptance` (distinguish expected results from actual observed evidence on base).
- `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` (distinguish completed implementation from pending milestone acceptance, or record repair tasks if the check fails).
