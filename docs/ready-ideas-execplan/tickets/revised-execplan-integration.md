# Revised ExecPlan Integration

**Type:** grilling
**Status:** closed
**Blocked By:** stable-rtk-simplification.md, repository-state-retirement.md, markdown-health-retirement.md, repository-okf-hook.md, lifecycle-notifications.md, high-rate-hook-performance-review.md, actionable-tool-guardian-denials.md
**Research Dir:** none

## Question

How should the existing ExecPlan record completed historical work while specifying the new migration, actionable Tool Guardian denials, performance review, cross-provider acceptance, installed-hook cleanup, and documentation updates as independently verifiable new milestones? Decide the execution order and the precise gate before implementation resumes.

---

## Resolution

Keep the prior implementation milestones as a compact, clearly historical record. Their old `done` and `Acceptance: met` labels are evidence for the former design, not acceptance of the revised requirements. Add new, independently verifiable milestones in dependency order: stable RTK migration and retirement of obsolete hooks; repository-local OKF lint and sparse lifecycle messages; actionable Tool Guardian denials; performance review after the retained high-rate hook graph is final; then automated platform checks and separate functional live CLI checks. Document source versus installed state and leave retired user-level copies for manual cleanup as decided in the retirement tickets.

Keep the native Windows scan-secrets HEAD-failure proof open until executed. Put Copilot and Gemini live checks in separate milestones for sessions with those CLIs available. Source and automated milestones may be accepted independently, but the overall plan stays incomplete while required live checks remain open. The macOS high-rate performance audit runs scripts directly and has no live CLI gate. Record the six blocked legacy branch deletions as separate historical housekeeping for a reviewed user-run Git command, not a hook acceptance gate.

Revise `ExecPlan.md` and `windows-live-check.md` before any hook, installer, registration, or installed-user change. Record why the old milestones were superseded in the plan's living sections. The user must explicitly approve the completed revised plan before source implementation resumes. Do not infer approval merely from this ticket's agreement to revise the planning documents.
