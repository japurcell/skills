# Workflow versioning and run changes

**Type:** grilling
**Status:** open
**Blocked By:** workflow-authoring-and-task-contract.md, agent-execution-profiles.md
**Research Dir:** not applicable

## Question

Which inputs are fixed when a run starts, and how can workflow, prompt, skill, profile, or plan changes affect an unfinished run?

Apply the accepted upgrade and retention policy in [Operating and installation model](operating-and-installation-model.md#resolution): retain required runtime/workflow versions for unfinished runs, defer incompatible upgrades, and keep history until explicit cleanup. Do not ask those policy questions again.

Decide version identities, the exact artifacts needed for compatible resume, edits for future runs versus explicit changes to a running one, compatibility checks, superseded task handling, and rollback. Include unavailable old dependencies, restoring a compatible installation after uninstall, and an improvement promoted while other runs remain active.

Resolution should provide a change matrix showing allowed changes, required approvals or restarts, invalidated evidence, and compatibility obligations for the chosen runtime.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

