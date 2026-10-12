# Agent execution profiles

**Type:** grilling
**Status:** claimed by subagent-0gnr9j
**Blocked By:** workflow-authoring-and-task-contract.md, operating-and-installation-model.md
**Research Dir:** not applicable

## Question

How does a workflow choose a harness, model, reasoning level, prompt, and skills without silently losing requested capabilities?

Set configuration precedence and run overrides, profile versioning, required versus optional capabilities, unsupported-setting behavior, and explicit fallback policy. Decide fresh versus continued sessions for implementation, independent review, and repair.

Define the adapter interface for launch, progress, result, cancellation, native approval requests, and resumability. Distinguish requested skills from observed loading and unknown usage from zero usage.

Use the retained harness research as a starting point, not a current compatibility guarantee. If a decision needs new CLI facts, create a research ticket with an assigned research directory and delegate it.

Resolution should include profile examples, adapter obligations, conformance criteria, and initial versus later harness coverage, chosen with the user.

---

## Session progress

Claimed on 2026-10-12 after [Operating and installation model](operating-and-installation-model.md) closed. Both exact prerequisites were verified closed.

### Prior answers applied

- Harness, model, reasoning level, skill, and prompt selection are required per stage/step. Workflows remain fully customizable.
- Codex CLI, Copilot CLI, and Gemini CLI are the primary harnesses; OpenCode and Pi are also desired. Do not ask the human to name the same harnesses again. Exact supported version/capability combinations require evidence, not assumptions.
- Workflows use TypeScript managed operations. External effects and agent sessions must remain visible to the executor and live UI.
- Repository-owned editable settings and isolated, pinned installation dependencies are accepted. The skill provisions the factory runtime; existing harness authentication and permission controls remain in use.
- The factory-owned SQLite executor, manual Continue, resumable Stop, and retention policies are settled. Concrete adapter obligations must support those policies.
- Workflow/runtime version retention is accepted. Whether and how prompt, skill, profile, or plan changes affect an unfinished run belongs to [Workflow versioning and run changes](workflow-versioning-and-run-changes.md).

### Confirmed answers, round one

On 2026-10-12, the human explicitly accepted all three recommendations:

1. **Configuration precedence:** reusable named profiles in the repository, resolved as repository defaults, then the selected profile, then step-specific settings, then explicit run overrides targeted to that step. Display and record the effective configuration. A broad override must not silently replace unrelated specialist choices.
2. **Unsupported settings and fallback:** stop and explain when a requested harness, model, reasoning setting, or required skill cannot be honored. Allow a substitution only through an explicitly configured fallback policy and record it visibly. Fallback must not bypass effect reconciliation for work already started.
3. **Session context:** default to a fresh session per implementation task and independent review attempt. Repairs may continue the implementing session when the harness and profile remain compatible; otherwise start a new session with explicit task context and recorded findings. Crash recovery may reconnect to the same interrupted attempt. These are configurable defaults for custom workflows. Always-fresh sessions for every new step attempt were offered but not selected as the default.

These answers are settled. Do not repeat the configuration-precedence, fallback-default, or session-default questions.

### Confirmed answers, round two

On 2026-10-12, the human explicitly accepted all three recommendations:

1. **Skill delivery modes:** prefer a harness's native skill mechanism when supported. Also allow a profile to explicitly select an instruction-based mode that delivers the skill instructions and required resources through the adapter. This is a distinct mode, not a claim of native skill execution. Preserve required capabilities; block if they cannot be provided. Switching modes as a fallback still requires the already accepted explicit fallback policy. Record the requested skill, delivery mode, and evidence of loading separately.
2. **Minimum visibility:** require live session output, lifecycle status, final output/artifact references, and a stop request path. Permit richer tool events, exact token/cost metrics, or positive evidence of skill loading to be unavailable, with each shown as unknown or unsupported rather than zero or verified. This does not relax required skill delivery or the real-time session-visibility requirement. A profile may explicitly require a richer capability and then block if it is missing.
3. **Recovery without native session resume:** allow the profile's explicit recovery policy to start a fresh session with recorded task context and findings when native continuation is unavailable. Continue initiates that policy only after code reconciles previous processes and effects; uncertain effects still block. Record a new attempt linked to the original step/session, disclose the context change, and preserve applicable budgets. Without the configured policy, stop and explain. This is not an unconfigured harness/model substitution.

These are settled product contracts, not assertions that a particular CLI supports them today. Do not repeat skill-delivery, minimum-telemetry, or configured fresh-session recovery questions. The desired harness set remains Codex CLI, Copilot CLI, Gemini CLI, OpenCode, and Pi; none has been dropped. Current CLI facts must be verified through delegated research if needed; do not ask the human to supply discoverable compatibility facts.

### Profile examples

These examples illustrate the accepted contracts. Names are illustrative repository settings, not final schema or tested CLI commands. Model and reasoning values refer to user-configured, validated selections; the examples do not assume identical model names or reasoning controls across harnesses.

| Step and named profile | Harness and instructions | Context and recovery |
| --- | --- | --- |
| Implement task using `builder` | Codex CLI; repository-selected model and reasoning; implementation prompt and explicitly selected implementation skill | Fresh task session. Repairs may reuse it when compatible. A configured recovery policy may supply recorded context to a fresh session after reconciliation. |
| Independent code review using `reviewer` | Copilot CLI; reviewer-specific model and reasoning; review prompt and explicitly selected review skill | Fresh session for each independent review attempt. Missing required settings block unless an explicit fallback applies. |
| Independent acceptance review using `acceptance` | Gemini CLI; acceptance-specific model and reasoning; acceptance prompt and task evidence | Fresh review session. Live output and status remain required even when exact usage or tool telemetry is unavailable. |

The two review sessions may run in parallel when workflow code chooses it. A run override targeting only code review changes that step's effective configuration without replacing the builder or acceptance selections. OpenCode or Pi may be selected through the same contract; actual admission depends on capability validation. The table assigns no mandatory harness to any stage.

### Adapter obligations derived from accepted choices

Keep harness-specific behavior behind one execution interface. Workflow code supplies a resolved request; the adapter owns CLI-specific launch arguments, instruction delivery, session access, output decoding, and stop requests. The executor owns step identity, attempts, persistence, budgets, and effect reconciliation.

| Obligation | Conformance evidence required before claiming support |
| --- | --- |
| Validate the resolved request | Exercise supported and unsupported harness/model/reasoning/required-skill selections. Reject an unmet requirement before starting work where detectable; surface failures discovered later. Never silently substitute. |
| Deliver instructions | Record the requested prompt/skills, selected delivery mode, and delivery evidence. Distinguish delivered instructions from observed skill loading or compliance. Exercise missing resources and unavailable required tools. |
| Expose sessions live | Attach output and lifecycle status to the correct run, step, attempt, and session. Exercise parallel sessions without mixing output. Mark absent optional telemetry unknown or unsupported. |
| Return an outcome | Preserve final output, available artifact references, and process outcome. A clean process exit does not prove workflow acceptance. Typed-result behavior is proposed in the next round. |
| Request interruption | Exercise Stop during active work and expose whether the process has actually exited. The executor retains resumable state. Stop request acceptance alone is not proof that child processes ended. |
| Support recovery honestly | Advertise native resume availability without assuming it. Exercise reconnect and explicitly configured fresh-session recovery after reconciliation, preserving lineage and budgets. Uncertain earlier effects block. |
| Preserve native permission controls | Keep native tool approvals distinct from factory workflow checkpoints; never silently approve or bypass them. The interaction details belong to [Human control and publication](human-control-and-publication.md). |
| Qualify compatibility claims | Record tested adapter, CLI, runtime, and OS versions plus relevant capabilities. Native macOS, Linux, and Windows remain targets; no combination is verified by this planning document. |

No adapter is currently qualified. Codex CLI, Copilot CLI, and Gemini CLI remain primary; OpenCode and Pi remain additional desired harnesses. This is priority information already supplied by the human, not a decision to drop any harness or an unverified release-support promise. Detailed compatibility evidence and release acceptance belong to [Specification readiness and acceptance](specification-readiness-and-acceptance.md).

### Remaining contract questions

Only the following profile-contract choices are still proposed:

1. **Prompt and skill composition:** resolve ordinary fields using the accepted precedence. Treat a supplied prompt as replacing the inherited prompt, and a supplied ordered skill list as replacing the inherited list. An omitted field inherits; an explicit empty skill list clears inherited skills. Allow explicit composition to extend a prompt or append skills, but never silently concatenate instructions. Show the resulting prompt and ordered skill list before dispatch. Any separately declared required capability must still validate.
2. **Typed agent results:** allow each step to require a validated result schema or accept text/artifact output. When a schema is required, malformed or missing data makes the attempt unsuccessful even if the CLI exited successfully. Preserve the raw output for inspection. Another agent attempt requires the workflow's explicitly bounded repair/retry policy and counts against its applicable budget; the adapter must not start a hidden correction conversation.

Exact configuration field names are illustrative until the specification is assembled. Profile/prompt/skill version identities and changes to unfinished runs belong to [Workflow versioning and run changes](workflow-versioning-and-run-changes.md); exact repair limits belong to [Verification and review policy](verification-and-review-policy.md). The remaining questions do not reopen either ticket's scope. No adapter or runtime implementation is authorized.

<!-- Append Resolution only after the live exchange reaches a confirmed decision. -->

