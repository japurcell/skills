# Agent execution profiles

> Continuation amendment, 2026-10-15: [SSSF-style invocation](workflow-versioning-and-run-changes.md#resolution) replaces durable workflow resume. Harness conversation reuse is limited to corrections within the current invocation under the [accepted session boundary](#invocation-scoped-correction-conversations). No retained workflow/runtime or interrupted execution position is restored.

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md, operating-and-installation-model.md
**Research Dir:** not applicable

## Question

How does a workflow choose a harness, model, reasoning level, prompt, and skills without silently losing requested capabilities?

Set configuration precedence and run overrides, profile versioning, required versus optional capabilities, unsupported-setting behavior, and explicit profile selection without automatic fallback. Decide fresh versus continued sessions for implementation, independent review, and repair.

Define the adapter interface for launch, progress, result, cancellation, non-interactive permission enforcement, and conversation reuse. Distinguish requested skills from observed loading and unknown usage from zero usage.

Use the retained harness research as a starting point, not a current compatibility guarantee. If a decision needs new CLI facts, create a research ticket with an assigned research directory and delegate it.

Resolution should include profile examples, adapter obligations, conformance criteria, and initial versus later harness coverage, chosen with the user.

---

## Decision record

Claimed on 2026-10-12 after [Operating and installation model](operating-and-installation-model.md) closed. Both exact prerequisites were verified closed.

### Selected profile or failure

On 2026-10-15 the human accepted removing automatic profile fallback chains. This section supersedes earlier permission to configure automatic substitutions anywhere in these decisions.

- Honor the selected effective harness, model, reasoning setting, permission policy, skill inputs/delivery mode, and required capabilities. If a requirement cannot be honored, stop with an actionable failure; reject before launch where detectable. Do not try another profile or downgrade a required capability automatically, even through a configured fallback list.
- The user can explicitly edit/select another profile for a later invocation after ordinary ownership and current-input checks. Different workflow steps may deliberately select different profiles. Existing configuration precedence and step-start resolution remain; removing automatic fallback does not freeze all phases to one profile.
- Preserve optional telemetry with honest unknown/unsupported status, supported manual child cleanup, and bounded code/format corrections using the selected profile. [Factory-level automatic infrastructure retries are removed](verification-and-review-policy.md#no-factory-level-automatic-infrastructure-retries). Starting a correction fresh when conversation reuse is unsupported/incompatible remains allowed. These paths do not authorize profile substitution or wider permissions.
- Unsupported profile behavior is a failure, not a fabricated `needs_input` question. Save the selected settings and actionable error, perform required cleanup, and apply the existing failure notification contract. Preserve uncertainty about launched work; never try another profile to bypass unresolved ownership or effects.

Acceptance must prove that unsupported required settings fail without a substitute launch, explicitly configured fallback chains cannot execute, and separate steps/later explicit invocations can use deliberately selected profiles. Verify optional missing telemetry remains usable, native permissions stay enforced, and corrections retain the selected profile. No runtime behavior is proved by this documentation.

### Invocation-scoped correction conversations

On 2026-10-15 the human accepted the narrower session simplification after comparing SSSF's correction and continuation behavior. This section owns the current session policy and supersedes the earlier cross-invocation reuse and configured fresh-session recovery policies.

- Keep fresh sessions for implementation phases and independent review attempts. A bounded code or format correction may reuse the conversation it corrects within the same invocation when the adapter supports it and the effective harness/profile inputs remain compatible. Reuse is optional, not a required harness capability. Independent review must not inherit the implementer's conversation.
- Every later invocation starts fresh native conversations, including an invocation answering a saved `needs_input` question or joining an existing run/worktree. No factory option may resume a native conversation from an earlier invocation. Saved native IDs remain observation/provenance, not cross-invocation restart handles.
- If reuse is unavailable or incompatible before dispatch, start the permitted correction fresh with explicit task context, saved output, and relevant findings. This uses the selected, validated profile and needs no separate native-resume recovery configuration. It does not authorize harness/model substitution, a hidden extra attempt, or blind repetition after an uncertain launch. A failed reuse launch follows ordinary failure finalization and ownership checks; it must not trigger an automatic fresh-session retry.
- Remove cross-invocation conversation lookup/compatibility and automatic native-resume recovery machinery. Keep only the adapter checks needed for optional in-invocation corrections. Factory-controlled inputs still resolve at each step's start; reuse must not silently retain superseded instructions or bypass native permissions.
- Preserve history, learning sources, worktree reuse, explicit follow-up inputs, attempt identity, and retained allowances. Reused conversations do not merge attempts or reset budgets. Supply needed context explicitly; do not build automatic full-transcript replay or a context-reconstruction engine. Internal turns and subagents remain implementer/harness-owned.

Acceptance must cover same-invocation correction reuse, unsupported/incompatible reuse starting a fresh correction, fresh independent reviews, and fresh later invocations even when recorded native sessions remain available. Verify recorded context choice, distinct attempts, retained allowances, and unchanged permissions/step-start inputs. No adapter behavior or performance benefit is proved by this decision.

### Step-start inputs amendment, 2026-10-15

Apply [Step-start input resolution](workflow-versioning-and-run-changes.md#step-start-input-resolution), accepted on 2026-10-15. Resolve factory-controlled settings, prompt templates, and skill inputs at each managed step's start under the existing precedence/composition rules. Record what is actually supplied. Edits can affect later steps in the same invocation, but the factory does not reconfigure an already launched call. Native skill/instruction-file loading is separately qualified; no whole-invocation snapshot or native loading guarantee is implied.

### Non-interactive amendment, 2026-10-15

[Human input and execution controls](human-control-and-publication.md#resolution) supersedes all live native-approval/question obligations in the earlier record. Managed harness steps run non-interactively under explicit, recorded permissions. Preserve enforcement; denied operations or unsupported interactive requirements must not trigger silent approval or broader access. Unsupported required capabilities block under the selected-profile-or-failure contract. Exact supported CLI/RPC/SDK modes require adapter evidence.

The adapter captures schema-valid `needs_input` as a non-success outcome that stops further workflow dispatch and ends the invocation after owned-process cleanup. It preserves the actionable question/context; it does not wait for a reply or launch format correction for that valid outcome. A later explicit invocation supplies new inputs to fresh native conversations under the accepted session boundary above. Failures remain distinct from questions. Apply the [accepted needs-input and invocation finalization contract](recovery-and-runtime-selection.md#accepted-needs-input-and-invocation-finalization), including early question persistence, interruption of other active managed calls, and separate outcome/cleanup facts. No factory live callback bridge, pending request routing, or native grant/withdrawal system remains. Internal subagents receive no additional authority.

Existing live output, configured instructions, results, usage, cancellation, and supported child visibility remain required as previously scoped. Compatibility tests must establish non-interactive permission enforcement and honest blocked/unsupported outcomes, not human response round trips. Source research about interactive native protocols remains historical feasibility evidence, not a requirement to implement them.

Apply the [accepted manual-cleanup fallback](recovery-and-runtime-selection.md#accepted-manual-cleanup-fallback): reliable automatic child control is used where supported, but its absence alone does not disqualify a harness mode. Report the limitation and require operator cleanup when child activity remains uncertain, preserving blocked workspace ownership after runner exit. The managed-session stop-request path and native permissions remain required; an unsupported explicitly required automatic child-control capability still blocks. No universal descendant-control guarantee is implied. Apply the [accepted cleanup confirmation and ownership release contract](recovery-and-runtime-selection.md#accepted-cleanup-confirmation-and-ownership-release) when automatic cleanup cannot be established; absent telemetry alone does not prevent informed operator clearance, while known active owned work prevents release.

### Delegation amendment, 2026-10-15

[Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution) removes factory-managed implementation tasks. The factory selects a profile and fresh session for each implementation phase and independent review attempt; compatible managed repair may reuse the implementing conversation within the same invocation only. Internal subagent profiles, assignments, permissions, and session policies belong to the implementer/harness, subject to explicitly supported configuration. Per-step factory settings do not promise universal control of internal children.

All managed phases receive the prepared run worktree as their repository working directory. Preserve native permission controls for parent and child work; delegation does not grant extra authority. Record supported child identities, parent links, lifecycle/output, and usage without inventing absent information or double-counting parent totals. Child telemetry, child shutdown, and internal concurrency limits are separate capabilities. Limited telemetry is allowed by default; required capabilities must still be satisfied or dispatch fails. A parent exit alone does not prove its children stopped.

### Prior answers applied

- Harness, model, reasoning level, skill, and prompt selection are required per stage/step. Workflows remain fully customizable.
- Codex CLI, Copilot CLI, and Gemini CLI are the primary harnesses; OpenCode and Pi are also desired. Do not ask the human to name the same harnesses again. Exact supported version/capability combinations require evidence, not assumptions.
- Workflows use TypeScript managed operations. External effects and agent sessions must remain visible to the executor and live UI.
- Repository-owned editable settings and isolated, pinned installation dependencies are accepted. The skill provisions the factory runtime; existing harness authentication and permission controls remain in use.
- The foreground TypeScript runner, SQLite observability history, explicit invocation, interruption, and history retention are settled under the continuation amendment.
- Old executable-version retention is superseded. Current files and saved traces/prompts/outputs are governed by [Workflow versioning and run changes](workflow-versioning-and-run-changes.md).

### Confirmed answers, round one

On 2026-10-12, the human explicitly accepted all three recommendations:

1. **Configuration precedence:** reusable named profiles in the repository, resolved as repository defaults, then the selected profile, then step-specific settings, then explicit run overrides targeted to that step. Display and record the effective configuration. A broad override must not silently replace unrelated specialist choices.
2. **Unsupported settings:** stop and explain when the selected profile cannot be honored. The later [selected-profile-or-failure decision](#selected-profile-or-failure) removes the earlier configured automatic fallback allowance; deliberate profile selection and required safety checks remain.
3. **Session context:** fresh implementation/review sessions and compatible correction reuse remain. The later [invocation-scoped correction decision](#invocation-scoped-correction-conversations) supersedes cross-invocation native reuse and configurable exceptions to that boundary. Always-fresh corrections were considered but not adopted.

These answers are settled. Do not repeat the configuration-precedence, selected-profile-or-failure, or session-default questions.

### Confirmed answers, round two

On 2026-10-12, the human explicitly accepted all three recommendations:

1. **Skill delivery modes:** prefer a harness's native skill mechanism when supported. Also allow a profile to explicitly select an instruction-based mode that delivers the skill instructions and required resources through the adapter. This is a distinct mode, not a claim of native skill execution. Preserve required capabilities; block if they cannot be provided. Select the delivery mode explicitly; do not switch it automatically when the selected mode fails. Record the requested skill, delivery mode, and evidence of loading separately.
2. **Minimum visibility:** require live session output, lifecycle status, final output/artifact references, and a stop request path. Permit richer tool events, exact token/cost metrics, or positive evidence of skill loading to be unavailable, with each shown as unknown or unsupported rather than zero or verified. This does not relax required skill delivery or the real-time session-visibility requirement. A profile may explicitly require a richer capability and then block if it is missing.
3. **Recovery without native session resume, superseded:** the [invocation-scoped correction decision](#invocation-scoped-correction-conversations) removes the separate native-resume recovery policy. Fresh later-invocation sessions and fresh corrections when reuse is unavailable follow that contract; ordinary safety checks, explicit profile selection, provenance, and retained budgets remain.

These are settled product contracts, not assertions that a particular CLI supports them today. Do not repeat skill-delivery or minimum-telemetry questions. The later session amendment owns the superseding recovery policy. The desired harness set remains Codex CLI, Copilot CLI, Gemini CLI, OpenCode, and Pi; none has been dropped. Current CLI facts must be verified through delegated research if needed; do not ask the human to supply discoverable compatibility facts.

### Profile examples

These examples illustrate the accepted contracts. Names are illustrative repository settings, not final schema or tested CLI commands. Model and reasoning values refer to user-configured, validated selections; the examples do not assume identical model names or reasoning controls across harnesses.

| Step and named profile | Harness and instructions | Context and recovery |
| --- | --- | --- |
| Implement candidate using `builder` | Codex CLI; repository-selected model and reasoning; implementation prompt and explicitly selected implementation skill | Fresh implementation session. Compatible corrections may reuse it within this invocation; otherwise receive explicit context in a fresh session. Later invocations always start fresh. |
| Independent code review using `reviewer` | Copilot CLI; reviewer-specific model and reasoning; review prompt and explicitly selected review skill | Fresh session for each independent review attempt. Missing required settings block; no automatic profile fallback. |
| Independent acceptance review using `acceptance` | Gemini CLI; acceptance-specific model and reasoning; acceptance prompt and task evidence | Fresh review session. Live output and status remain required even when exact usage or tool telemetry is unavailable. |

The two review sessions may run in parallel against one fixed candidate when workflow code chooses it and implementation/repair writers have stopped. Internal implementation subagents are parent-owned rather than factory-scheduled tasks. A run override targeting only code review changes that step's effective configuration without replacing the builder or acceptance selections. OpenCode or Pi may be selected through the same contract; actual admission depends on capability validation. The table assigns no mandatory harness to any stage.

### Adapter obligations derived from accepted choices

Keep harness-specific behavior behind one execution interface. Workflow code supplies a resolved request; the adapter owns CLI-specific launch arguments, instruction delivery, session access, output decoding, and stop requests. The runner owns invocation/step identity, attempt records, history persistence, budgets, and relevant effect checks.

| Obligation | Conformance evidence required before claiming support |
| --- | --- |
| Validate the resolved request | Exercise supported and unsupported harness/model/reasoning/required-skill selections. Reject an unmet requirement before starting work where detectable; surface failures discovered later. Never automatically substitute, including through a configured fallback chain. |
| Deliver instructions | Record the requested prompt/skills, selected delivery mode, and delivery evidence. Distinguish delivered instructions from observed skill loading or compliance. Exercise missing resources and unavailable required tools. |
| Expose sessions live | Attach output and lifecycle status to the correct run, step, attempt, and session. Exercise parallel sessions without mixing output. Mark absent optional telemetry unknown or unsupported. |
| Return an outcome | Preserve final output, available artifact references, and process outcome. A clean process exit does not prove workflow acceptance. Exercise valid, missing, and malformed required results; preserve raw output and expose validation failure. Correction attempts must be visible and respect the workflow's explicit budget. |
| Request interruption | Exercise Pause during active work and expose whether the process has actually exited. The runner retains history and partial work without promising durable resume. Pause request acceptance alone is not proof that child processes ended. |
| Respect the invocation session boundary | Exercise supported in-invocation correction reuse and fresh corrections when reuse is unavailable/incompatible. Start fresh for independent reviews and every later invocation. Preserve provenance and budgets; uncertain earlier activity/effects still block unsafe dispatch. |
| Preserve native permission controls | Enforce explicitly selected permissions without live approval callbacks. Denied operations and unsupported interactive behavior must stop/report honestly, never silently approve or bypass controls. See [Human input and execution controls](human-control-and-publication.md). |
| Qualify compatibility claims | Record tested adapter, CLI, runtime, and OS versions plus relevant capabilities. Native macOS, Linux, and Windows remain targets; no combination is verified by this planning document. |

No adapter is currently qualified. Codex CLI, Copilot CLI, and Gemini CLI remain primary; OpenCode and Pi remain additional desired harnesses. This is priority information already supplied by the human, not a decision to drop any harness or an unverified release-support promise. Detailed compatibility evidence and release acceptance belong to [Specification readiness and acceptance](specification-readiness-and-acceptance.md).

### Confirmed answers, round three

On 2026-10-12, after reviewing visual examples and the tradeoffs, the human explicitly accepted both remaining choices and asked to record them and stop:

1. **Replacement by default, explicit composition:** resolve fields independently using the accepted precedence. A supplied prompt replaces the inherited prompt; a supplied ordered skill list replaces the inherited list. Omitted fields inherit, and an explicit empty skill list clears inherited skills. Authors may explicitly compose or extend instructions, but nothing is silently concatenated. Changing the skill list does not replace unrelated harness, model, or reasoning settings. Show the effective instructions and their sources so discarded inherited guidance is visible. Separately declared required capabilities still validate. Skill selection does not schedule separate steps; workflow code owns execution order.
2. **Optional schemas per step, required for execution decisions:** require schemas for review verdicts, implementation outcome reports, and other agent-produced outputs that control factory execution. Allow text and artifacts for explanations and reports. Missing or malformed required data makes the attempt unsuccessful even when the CLI exits successfully; preserve raw output for inspection. Another agent attempt requires the workflow's explicit bounded correction/repair policy or an explicit later invocation and counts against its applicable budget. Adapters must not launch hidden correction conversations. A structurally valid result does not prove correctness or replace verification evidence. An invalid result does not prove that no effects occurred; reconcile existing effects before repeating work. A format-only correction should reuse saved output where possible.

The tradeoff is explicit: replacement can discard useful inherited guidance, while automatic merging can silently introduce conflicts and extra instructions. Per-step schemas add validation and possible correction work where deterministic branching needs a contract, without imposing structured output on every report. Neither automatic instruction merging nor universally required structured results was selected.

These answers are settled. Do not repeat prompt/skill composition or structured-result policy questions.

## Resolution

The non-interactive amendment above supersedes earlier live approval obligations. The delegation amendment also applies to the accepted contract: implementation-phase profiles replace per-task launch profiles, and child visibility is conditional on harness support. Factory controls do not silently extend to opaque child calls.

Closed on 2026-10-12 after three rounds of explicit human decisions. Both exact prerequisites, `workflow-authoring-and-task-contract.md` and `operating-and-installation-model.md`, were verified closed. The confirmed answers above own the configuration, session, skill-delivery, telemetry, recovery, composition, and result contracts. Profile examples illustrate them; adapter obligations define the required conformance evidence without claiming an implementation exists.

Exact configuration field names remain illustrative until the specification is assembled. Profile/prompt/skill provenance and accepted step-start input resolution belong to [Workflow versioning and run changes](workflow-versioning-and-run-changes.md); exact repair limits and evidence policy belong to [Verification and review policy](verification-and-review-policy.md). Non-interactive permissions, needs-input outcomes, and notifications belong to [Human input and execution controls](human-control-and-publication.md), and event delivery belongs to [Session events and live progress](session-events-and-live-progress.md). These downstream mechanisms do not reopen the accepted profile policies.

No new ticket is needed: the remaining mechanisms and compatibility proof already have owners. No adapter, runtime, recovery behavior, or platform combination was implemented or tested. No next ticket was claimed; the user explicitly requested stopping after this documentation update.

