# Human control and publication

**Type:** grilling
**Status:** open
**Blocked By:** task-scheduling-and-integration.md, verification-and-review-policy.md
**Research Dir:** not applicable

## Question

Where can a workflow request human input, and what must be true before it creates a PR or another external artifact?

Decide optional checkpoint semantics, approve/revise/stop actions, timeouts, authorization, binding decisions to evidence and revisions, and rejection of stale or duplicate decisions. Clarify workflow review versus a harness's native tool approval.

Define whether users can pause, cancel, or steer active work, what happens to children and running CLI processes, and which changes require a new run or checkpoint.

Set publication identity and reconciliation rules for a crash after the remote action but before recording its result. PR creation, pushing, merging, and deployment are separate actions; do not infer authorization from one to another.

Resolution should specify the human interaction contract and acceptance cases for stale approvals and duplicate publication.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

