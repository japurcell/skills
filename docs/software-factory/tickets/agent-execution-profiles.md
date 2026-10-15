# Agent execution profiles

> Continuation amendment, 2026-10-15: [SSSF-style invocation](workflow-versioning-and-run-changes.md#resolution) replaces durable workflow resume. Harness conversation reuse is a separate adapter capability; no retained workflow/runtime or interrupted execution position is restored.

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md, operating-and-installation-model.md
**Research Dir:** not applicable

## Question

How does a workflow choose a harness, model, reasoning level, prompt, and skills without silently losing requested capabilities?

Set configuration precedence and run overrides, profile versioning, required versus optional capabilities, unsupported-setting behavior, and explicit fallback policy. Decide fresh versus continued sessions for implementation, independent review, and repair.

Define the adapter interface for launch, progress, result, cancellation, native approval requests, and resumability. Distinguish requested skills from observed loading and unknown usage from zero usage.

Use the retained harness research as a starting point, not a current compatibility guarantee. If a decision needs new CLI facts, create a research ticket with an assigned research directory and delegate it.

Resolution should include profile examples, adapter obligations, conformance criteria, and initial versus later harness coverage, chosen with the user.

---

## Decision record

Claimed on 2026-10-12 after [Operating and installation model](operating-and-installation-model.md) closed. Both exact prerequisites were verified closed.

### Prior answers applied

- Harness, model, reasoning level, skill, and prompt selection are required per stage/step. Workflows remain fully customizable.
- Codex CLI, Copilot CLI, and Gemini CLI are the primary harnesses; OpenCode and Pi are also desired. Do not ask the human to name the same harnesses again. Exact supported version/capability combinations require evidence, not assumptions.
- Workflows use TypeScript managed operations. External effects and agent sessions must remain visible to the executor and live UI.
- Repository-owned editable settings and isolated, pinned installation dependencies are accepted. The skill provisions the factory runtime; existing harness authentication and permission controls remain in use.
- The foreground TypeScript runner, SQLite observability history, explicit invocation, interruption, and history retention are settled under the continuation amendment.
- Old executable-version retention is superseded. Current files and recorded provenance are governed by [Workflow versioning and run changes](workflow-versioning-and-run-changes.md).

### Confirmed answers, round one

On 2026-10-12, the human explicitly accepted all three recommendations:

1. **Configuration precedence:** reusable named profiles in the repository, resolved as repository defaults, then the selected profile, then step-specific settings, then explicit run overrides targeted to that step. Display and record the effective configuration. A broad override must not silently replace unrelated specialist choices.
2. **Unsupported settings and fallback:** stop and explain when a requested harness, model, reasoning setting, or required skill cannot be honored. Allow a substitution only through an explicitly configured fallback policy and record it visibly. Fallback must not bypass effect reconciliation for work already started.
3. **Session context:** default to a fresh session per implementation task and independent review attempt. Repairs may continue the implementing session when the harness and profile remain compatible; otherwise start a new session with explicit task context and recorded findings. A later explicit invocation may reuse compatible recorded conversation context; it creates new execution records rather than restoring an interrupted workflow attempt. These are configurable defaults for custom workflows. Always-fresh sessions for every new step attempt were offered but not selected as the default.

These answers are settled. Do not repeat the configuration-precedence, fallback-default, or session-default questions.

### Confirmed answers, round two

On 2026-10-12, the human explicitly accepted all three recommendations:

1. **Skill delivery modes:** prefer a harness's native skill mechanism when supported. Also allow a profile to explicitly select an instruction-based mode that delivers the skill instructions and required resources through the adapter. This is a distinct mode, not a claim of native skill execution. Preserve required capabilities; block if they cannot be provided. Switching modes as a fallback still requires the already accepted explicit fallback policy. Record the requested skill, delivery mode, and evidence of loading separately.
2. **Minimum visibility:** require live session output, lifecycle status, final output/artifact references, and a stop request path. Permit richer tool events, exact token/cost metrics, or positive evidence of skill loading to be unavailable, with each shown as unknown or unsupported rather than zero or verified. This does not relax required skill delivery or the real-time session-visibility requirement. A profile may explicitly require a richer capability and then block if it is missing.
3. **Recovery without native session resume:** allow the profile's explicit recovery policy to start a fresh session with recorded task context and findings when native continuation is unavailable. An explicit invocation may use that policy after checking ownership and any uncertain effects relevant to its work; it does not restore workflow execution state. Record a new attempt linked to the original step/session, disclose the context change, and preserve applicable budgets. Without the configured policy, stop and explain. This is not an unconfigured harness/model substitution.

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

Keep harness-specific behavior behind one execution interface. Workflow code supplies a resolved request; the adapter owns CLI-specific launch arguments, instruction delivery, session access, output decoding, and stop requests. The runner owns invocation/step identity, attempt records, history persistence, budgets, and relevant effect checks.

| Obligation | Conformance evidence required before claiming support |
| --- | --- |
| Validate the resolved request | Exercise supported and unsupported harness/model/reasoning/required-skill selections. Reject an unmet requirement before starting work where detectable; surface failures discovered later. Never silently substitute. |
| Deliver instructions | Record the requested prompt/skills, selected delivery mode, and delivery evidence. Distinguish delivered instructions from observed skill loading or compliance. Exercise missing resources and unavailable required tools. |
| Expose sessions live | Attach output and lifecycle status to the correct run, step, attempt, and session. Exercise parallel sessions without mixing output. Mark absent optional telemetry unknown or unsupported. |
| Return an outcome | Preserve final output, available artifact references, and process outcome. A clean process exit does not prove workflow acceptance. Exercise valid, missing, and malformed required results; preserve raw output and expose validation failure. Correction attempts must be visible and respect the workflow's explicit budget. |
| Request interruption | Exercise Pause during active work and expose whether the process has actually exited. The runner retains history and partial work without promising durable resume. Pause request acceptance alone is not proof that child processes ended. |
| Support recovery honestly | Advertise native resume availability without assuming it. Exercise compatible conversation reuse and explicitly configured fresh-session fallback in a later invocation, preserving provenance and applicable budgets. Uncertain earlier effects block. |
| Preserve native permission controls | Keep native tool approvals distinct from factory workflow checkpoints; never silently approve or bypass them. The interaction details belong to [Human control and publication](human-control-and-publication.md). |
| Qualify compatibility claims | Record tested adapter, CLI, runtime, and OS versions plus relevant capabilities. Native macOS, Linux, and Windows remain targets; no combination is verified by this planning document. |

No adapter is currently qualified. Codex CLI, Copilot CLI, and Gemini CLI remain primary; OpenCode and Pi remain additional desired harnesses. This is priority information already supplied by the human, not a decision to drop any harness or an unverified release-support promise. Detailed compatibility evidence and release acceptance belong to [Specification readiness and acceptance](specification-readiness-and-acceptance.md).

### Confirmed answers, round three

On 2026-10-12, after reviewing visual examples and the tradeoffs, the human explicitly accepted both remaining choices and asked to record them and stop:

1. **Replacement by default, explicit composition:** resolve fields independently using the accepted precedence. A supplied prompt replaces the inherited prompt; a supplied ordered skill list replaces the inherited list. Omitted fields inherit, and an explicit empty skill list clears inherited skills. Authors may explicitly compose or extend instructions, but nothing is silently concatenated. Changing the skill list does not replace unrelated harness, model, or reasoning settings. Show the effective instructions and their sources so discarded inherited guidance is visible. Separately declared required capabilities still validate. Skill selection does not schedule separate steps; workflow code owns execution order.
2. **Optional schemas per step, required for execution decisions:** require schemas for review verdicts, generated task graphs, and other agent-produced outputs that control execution. Allow text and artifacts for explanations and reports. Missing or malformed required data makes the attempt unsuccessful even when the CLI exits successfully; preserve raw output for inspection. Another agent attempt requires the workflow's explicit bounded correction/repair/retry policy and counts against its applicable budget. Adapters must not launch hidden correction conversations. A structurally valid result does not prove correctness or replace verification evidence. An invalid result does not prove that no effects occurred; reconcile existing effects before repeating work. A format-only correction should reuse saved output where possible.

The tradeoff is explicit: replacement can discard useful inherited guidance, while automatic merging can silently introduce conflicts and extra instructions. Per-step schemas add validation and possible correction work where deterministic branching needs a contract, without imposing structured output on every report. Neither automatic instruction merging nor universally required structured results was selected.

These answers are settled. Do not repeat prompt/skill composition or structured-result policy questions.

## Resolution

Closed on 2026-10-12 after three rounds of explicit human decisions. Both exact prerequisites, `workflow-authoring-and-task-contract.md` and `operating-and-installation-model.md`, were verified closed. The confirmed answers above own the configuration, session, skill-delivery, telemetry, recovery, composition, and result contracts. Profile examples illustrate them; adapter obligations define the required conformance evidence without claiming an implementation exists.

Exact configuration field names remain illustrative until the specification is assembled. Profile/prompt/skill provenance and use by later invocations belong to [Workflow versioning and run changes](workflow-versioning-and-run-changes.md); exact repair limits and evidence policy belong to [Verification and review policy](verification-and-review-policy.md). Native approval interaction belongs to [Human control and publication](human-control-and-publication.md), and event delivery belongs to [Session events and live progress](session-events-and-live-progress.md). These downstream mechanisms do not reopen the accepted profile policies.

No new ticket is needed: the remaining mechanisms and compatibility proof already have owners. No adapter, runtime, recovery behavior, or platform combination was implemented or tested. No next ticket was claimed; the user explicitly requested stopping after this documentation update.

