# Confirmed factory requirements

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** not applicable

## Question

Which requirements has the user already established, and which earlier recommendations remain proposals?

---

## Resolution

Imported from the existing conversation on 2026-10-12. This records prior human decisions; no new design ticket was resolved during charting.

### Confirmed requirements

- Deterministic workflow behavior belongs in code. Agents perform reasoning.
- Workflows are fully customizable, including the overall structure. The six-stage example is a useful default, not a mandatory pipeline.
- Planning may happen outside the factory, including through wayfinder or grilling. For simpler work, the factory may plan from a prompt.
- Planning may describe tasks and dependencies for the implementer. The factory does not schedule or integrate those tasks; the implementer owns internal delegation.
- Verification may include lint, unit tests, E2E tests, and interactive UI verification. The user controls whether token-intensive interactive verification runs.
- Verification/review uses structured results, checks, review phases, and bounded corrections on the resulting candidate. Internal task review belongs to the implementer; generic reviewer aggregation and criterion-evidence machinery are removed.
- Managed harness steps are non-interactive under explicit permissions. No routine human approval stage or live question/permission bridge remains. Structured `needs_input` saves the question and ends the invocation; answers arrive through a later explicit invocation. See [Human input and execution controls](human-control-and-publication.md#resolution).
- Notify prominently for needs-input and failed/exhausted outcomes, quietly for configurable successful completion, and only in the dashboard for routine progress. Persist attention status independently of desktop delivery; reminders are configurable and off by default.
- Managed push/PR publication is removed; workflows may finish with local changes and a report.
- Extract evidence-linked skill and prompt improvement candidates through [explicit learning invocations](skill-and-prompt-improvement.md#accepted-explicit-learning-invocations) over selected ended invocations. Preserve source history and do not automatically change active configuration; [explicit comparative evaluation and human approval before adoption](skill-and-prompt-improvement.md#accepted-evaluation-and-human-adoption) govern subsequent changes.
- Configure the harness, model, and reasoning level per workflow stage. Codex CLI, Copilot CLI, and Gemini CLI are primary; OpenCode and Pi are also desired.
- Allow a step to specify a skill or prompt.
- Every factory-managed session and step must be inspectable in a swimlane-style UI that updates in real time. Show nested subagent activity where the harness exposes it; otherwise label child visibility as limited. The SSSF experience is a design reference.
- Create one isolated run worktree before any phase, including planning. One active invocation owns each worktree, including read-only invocations; internal parallel work and concurrent runs in separate worktrees remain allowed. All phases operate in that repository workspace; the implementer/harness coordinates its own parallel subagents and returns one stable candidate.
- Historical capture saves traces, prompts, and outputs; an immutable registered-evidence service is not required.
- Installation through a skill remains required. Multiple workflows and inspection of live and historical activity were part of the original brief.
- Prefer quality, simplicity, robustness, scalability, and maintainability over development cost.

### Planning scope

The user explicitly selected an implementation-ready specification as the destination. Current work captures decisions and plans the remaining sessions. The later executor decision supersedes the earlier Restate prototype direction; implementation awaits the specification.

The user approved grilling plus codebase-design as the substitute for wayfinder's unavailable domain-modeling dependency.

### Proposals requiring a later decision

Restate was selected for an earlier prototype, not a production stack. The user's later executor and continuation decisions are owned by [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation) and supersede that prototype direction. [Skill and prompt improvement](skill-and-prompt-improvement.md#accepted-evaluation-and-human-adoption) now requires explicit comparative evaluation and human approval of the exact change/target before adoption; extraction never automatically changes active configuration. On 2026-10-15 the human removed factory-managed parallel tasks and integration in favor of [Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution). The former task scheduler, per-task worktrees, integration queues, and graph refresh rules are superseded. Configuration profiles are now settled in [Agent execution profiles](agent-execution-profiles.md); saved event delivery and SSE transport remain accepted; history has been reduced to saved traces/prompts/outputs in [Session events and live progress](session-events-and-live-progress.md). [Verification and review policy](verification-and-review-policy.md#resolution) now owns structured results, checks, review phases, bounded corrections, and the separately retained managed-attempt limits.

TypeScript authoring was subsequently chosen by the user. The closed [Workflow authoring and task contract](workflow-authoring-and-task-contract.md) owns that decision, plan intake, observable scopes, and managed phase contracts. Plans no longer require factory-executable task graphs; nested observed subagents do not select a runtime-specific child-workflow mechanism.

The earlier three-repair example, mandatory plan/candidate approvals, one-adapter prototype scope, and exact storage layout are not fixed requirements.

### Evidence and limits

The source of the requirements above is the user's conversation, including the six-stage use case, the real-time/customization clarification, and the destination/substitute-skill answers.

Existing source studies are retained in [the research synthesis](../research.md). [The interactive documents](../README.md) use simulated runs; they do not prove runtime behavior. Prior implementation-oriented notes are historical context, not current authorization.

