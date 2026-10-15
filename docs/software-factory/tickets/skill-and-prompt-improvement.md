# Skill and prompt improvement

**Type:** grilling
**Status:** open
**Blocked By:** agent-execution-profiles.md, verification-and-review-policy.md, session-events-and-live-progress.md, workflow-versioning-and-run-changes.md
**Research Dir:** not applicable

## Question

How do session and trace logs produce useful skill or prompt improvements, and who decides to apply them?

Decide extraction inputs from successful and failed runs, scope and ownership of proposals, evidence and counterexamples, evaluation cases, acceptance criteria, human versus automatic promotion, versioning, rollback, and visibility in the factory UI.

Apply [SSSF-style continuation](workflow-versioning-and-run-changes.md#resolution): promoted changes are used by later script invocations. Do not design migration of suspended workflows or retain executable environments for old runs. Improvement revision/rollback history is ordinary authoring history, separate from workflow resume.

Distinguish extracting a proposal from changing an installed skill or prompt. Define how evaluation avoids treating lower token use or a single passing run as sufficient proof of improvement.

Resolution should describe one complete proposal/evaluation/promotion example and the allowed automation level. Do not edit skills or prompts while resolving this planning question.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

