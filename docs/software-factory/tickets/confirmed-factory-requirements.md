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
- Planning can produce a dependency graph of tasks requiring individual implementation.
- Verification may include lint, unit tests, E2E tests, and interactive UI verification. The user controls whether token-intensive interactive verification runs.
- Review and refactor cycles can run for individual tasks or for the resulting diff across all tasks.
- Human review before PR creation is configurable.
- Extract skill and prompt improvement candidates from session and trace logs.
- Configure the harness, model, and reasoning level per workflow stage. Codex CLI, Copilot CLI, and Gemini CLI are primary; OpenCode and Pi are also desired.
- Allow a step to specify a skill or prompt.
- Every factory session and step must be inspectable in a swimlane-style UI that updates in real time as work progresses. The SSSF experience is a design reference.
- Installation through a skill remains required. Multiple workflows and inspection of live and historical activity were part of the original brief.
- Prefer quality, simplicity, robustness, scalability, and maintainability over development cost.

### Planning scope

The user explicitly selected an implementation-ready specification as the destination. Current work captures decisions and plans the remaining sessions. The later executor decision supersedes the earlier Restate prototype direction; implementation awaits the specification.

The user approved grilling plus codebase-design as the substitute for wayfinder's unavailable domain-modeling dependency.

### Proposals requiring a later decision

Restate was selected for an earlier prototype, not a production stack. The user's later executor and continuation decisions are owned by [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation) and supersede that prototype direction. Runtime-specific child workflows and explicit improvement promotion remain unresolved. Record their tradeoffs in the relevant open tickets before treating them as settled. Incremental serialized integration, ready-result ordering, and stale-work tracking and refresh are now accepted in [Task scheduling and integration](task-scheduling-and-integration.md). Configuration profiles are now settled in [Agent execution profiles](agent-execution-profiles.md); saved event delivery, SSE transport, and retained evidence are now settled in [Session events and live progress](session-events-and-live-progress.md). [Verification and review policy](verification-and-review-policy.md#resolution) now owns check selection, review/repair defaults, budgets, rerun/reuse policy, and acceptance evidence.

TypeScript authoring was subsequently chosen by the user. The closed [Workflow authoring and task contract](workflow-authoring-and-task-contract.md) owns that decision, the accepted task contract, and the other answers from its live exchange. Its code-level nesting decision does not select a runtime-specific child-workflow mechanism.

The earlier three-repair example, mandatory plan/candidate approvals, one-adapter prototype scope, and exact storage layout are not fixed requirements.

### Evidence and limits

The source of the requirements above is the user's conversation, including the six-stage use case, the real-time/customization clarification, and the destination/substitute-skill answers.

Existing source studies are retained in [the research synthesis](../research.md). [The interactive documents](../README.md) use simulated runs; they do not prove runtime behavior. Prior implementation-oriented notes are historical context, not current authorization.

