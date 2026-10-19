# Workflow versioning and run changes

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md, agent-execution-profiles.md
**Research Dir:** not applicable

## Question

How should subsequent invocations use workflow code, settings, agent context, and earlier history without durable workflow resume?

## Resolution

On 2026-10-15, after comparing the complexity with SSSF, the human explicitly chose: "Let's simplify and use SSSF's continuation approach. Update the accepted decisions to match, keeping history for observability without durable workflow resume." This supersedes the earlier durable Continue and retained-executable-version policies. Both exact prerequisites are closed. This is a planning decision, not implementation authorization.

### Accepted continuation contract

- A human explicitly invokes a selected workflow script. The invocation type-checks/builds the current selected TypeScript workflow once before phases and executes the generated JavaScript from its entry point, under [accepted workflow build and loading](recovery-and-runtime-selection.md#accepted-workflow-build-and-loading). Prompts/settings/skills still resolve at step start as specified below. Opening the repository or observer never launches work.
- The human may explicitly join an existing history/context identity, analogous to SSSF's `adw_id`. Joining associates newly executed phases with retained history and explicit saved inputs; native conversations start fresh. It does not restore a program counter, suspended call stack, queue, task graph execution position, or pending callback.
- Invoking the same workflow again executes its code again. Recorded success does not automatically skip a phase. A purpose-built follow-up workflow may consume saved artifacts or context through explicit inputs, but there is no generic replay, resume-at-failed-step, or state-migration engine.
- Continue, if retained as a command label, means explicit script invocation with selected history/context. It must disclose the workflow being invoked and that execution begins at its entry point. Exact command spelling and history/invocation identity fields remain specification details.
- Agent conversation reuse is separate from workflow continuation. Apply [invocation-scoped correction conversations](agent-execution-profiles.md#invocation-scoped-correction-conversations): corrections may reuse compatible conversations within an invocation; later invocations always start fresh. Preserve required capabilities and native permissions. This borrows SSSF's correction continuity while deliberately omitting its cross-invocation native reuse; it does not restrict the product to Pi.
- Record distinct invocations and newly executed phases without rewriting prior attempts. Apply [accepted identity and retained accounting](recovery-and-runtime-selection.md#accepted-identity-and-retained-accounting): one run history/accounting scope, a fresh invocation ID per launch, and a fresh attempt ID per managed execution. Worktree and native conversation identities remain separate references. History retains events, actual effective settings/instructions, outputs, usage, and outcomes for observation and audit. Record provenance as used; this is not an executable environment snapshot or a promise of reproducibility.

### Step-start input resolution

On 2026-10-15 the human accepted resolving factory-controlled settings, prompt templates, and skill inputs at each managed step's start. The human then requested stopping after recording this decision.

- Resolve the step's selected inputs once when it starts, using the already accepted configuration precedence, explicit composition/replacement rules, required-capability validation, and the [selected-profile-or-failure policy](agent-execution-profiles.md#selected-profile-or-failure). Record the effective configuration and actual material supplied under that step/attempt.
- Edits made before a later step starts may affect that later step, even within the same invocation. The factory does not inject edits or reconfigure an already launched call.
- Dynamic prompts derived from earlier step outputs remain ordinary workflow behavior. Resolving inputs at step start does not freeze runtime-produced data at invocation start.
- Different phases may use different input revisions. Preserve their actual supplied material and provenance in saved history rather than claiming a whole-invocation immutable snapshot or reproducible executable bundle. Existing credential filtering still applies.
- This policy covers factory-resolved/delivered inputs. It does not guarantee that a harness never reads native instruction/skill files later, or freeze arbitrary workflow file reads, code imports, and external resources. Native loading semantics and required capabilities still need adapter qualification; do not claim unobserved skill loading.
- The selected resource paths and explicit overrides continue to govern which inputs a step resolves. This decision does not silently redirect between the user checkout, run worktree, or installed skill locations.
- Managed runtime/dependency upgrades remain idle-only. Ordinary input-file edits do not authorize permission broadening, reset accounting, migrate a suspended workflow, or restore an execution position.

Acceptance must edit a selected factory-controlled input between steps, verify the later step receives the new material, verify the factory does not reconfigure the already launched call, and retain distinct effective inputs in history. Missing/unsupported required inputs fail validation without automatic substitution. No runtime or adapter behavior has been implemented or tested.

### Changes, versions, and history

| Concern | Current contract |
| --- | --- |
| Workflow code and runtime | Later invocations use the currently installed versions. Retaining old executable bundles, dependency closures, or runtimes for unfinished executions is no longer required. The installation may still pin its current runtime/dependencies for predictable operation. |
| Prompts, skills, profiles, and plan inputs | Managed steps resolve selected factory-controlled settings, prompt templates, and skill inputs when each step starts, including later steps within the same invocation. Explicit run arguments retain their configured precedence. A changed plan is validated when admitted by that invocation. No suspended-run patch, plan migration, or automatic cross-invocation impact-analysis feature is required. Bounded phase corrections and checks of the current candidate remain; factory task discovery, scheduling, and dependency refresh are removed by the workspace/delegation amendment. |
| Changes during active execution | This decision introduces no hot-swapping or mutation protocol. Record the material actually consumed; do not claim a whole-run immutable snapshot. Factory-controlled settings/prompt/skill resolution at step start is accepted above; native harness loading and arbitrary custom reads remain outside that guarantee. Managed runtime/dependency upgrades are now [idle-only](operating-and-installation-model.md#idle-only-managed-upgrades), across the repository installation. |
| Old results and approvals | Preserve them as history. Joining history does not automatically reuse gate passes, approve new requests, or certify changed inputs. Reusing saved outputs or supplying a prior question's answer must satisfy current workflow checks and explicit permissions. There is no immutable registered-evidence system. |
| Accounting | Joining the same run retains shared and local allowances under the [accepted accounting contract](recovery-and-runtime-selection.md#accepted-identity-and-retained-accounting). Explicit operation/loop lineage identifies repeated work; ambiguous required lineage blocks dispatch rather than triggering automatic workflow comparison. Pre-launch admission atomically checks and records applicable charges. Uncertain launches retain charges unless non-launch is established. A genuinely new run has an explicitly established scope; no restorable control flow or automatic allowance reset is introduced. |
| Upgrade and uninstall | Preserve user-owned files and readable retained history. No restoration of an old execution environment is required to invoke a new workflow. History schema compatibility remains necessary; executable-state migration is removed. Managed upgrades and uninstall refuse active/uncertain owned work; both use the [idle maintenance gate](recovery-and-runtime-selection.md#accepted-uninstall-through-the-maintenance-gate), exclude concurrent launches, and require the dashboard host to stop. [Built-in full purge is removed](recovery-and-runtime-selection.md#accepted-removal-of-built-in-full-purge); complete removal is documented manual operator work. |
| Interruption | Preserve partial files, saved outputs, and honest incomplete status. Further work requires an explicit invocation; no automatic restart or durable resume is promised. |

### Workspace and delegation amendment, 2026-10-15

[Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution) supplies one prepared or explicitly reused worktree before any phase. Current-script invocation does not select per-task workspaces or restore an internal child team. A later invocation may explicitly reuse preserved files/context after ownership and input checks; all its phases use the selected workspace from entry. Retained accounting covers factory-managed calls, with child usage recorded where supported and no promised cap on opaque internal delegation.

### Controls and effects that survive the simplification

Pause/Ctrl+C still stops dispatch and interrupts owned work under the accepted grace policy. It no longer promises restoration of a saved execution position. Cancel still marks abandonment and preserves history; any later work must be explicitly authorized as new execution. [Human input and execution controls](human-control-and-publication.md#resolution) owns non-interactive execution and human decisions between invocations.

A structured `needs_input` saves the question/context and ends the invocation after safe cleanup. No live human wait or native approval callback is created. A later explicit invocation supplies an answer, validates current inputs/permissions, and starts from entry. Saved questions and answers remain history; no callback or workflow position is revived.

Managed PR publication was subsequently removed. No publication intent/outcome ledger, duplicate-PR reconciliation, or remote base-refresh protocol remains in the factory contract. Keep process ownership checks, current workflow checks, and authorization. A custom command with uncertain side effects is not safe to retry merely because a new invocation starts; custom code owns any domain-specific resolution without a general factory effect-recovery engine.

### Simplifications and remaining owners

Removed from the initial design: durable workflow executor, serialized execution checkpoints, replay/skip-completed machinery, executable version retention, suspended-run migration, and automatic restoration of pending waits. SQLite remains an observability/accounting store; TypeScript remains the workflow language; SSE remains the selected observation transport. SSSF is the continuation reference, not a wholesale replacement of our stack or unrelated policies.

[Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) now owns process ownership, shutdown, ended needs-input outcomes/notification delivery, explicit follow-up invocation, accounting, saved-history integrity, and interruption. Managed publication and immutable evidence capture are out of scope. [Skill and prompt improvement](skill-and-prompt-improvement.md) owns proposal/evaluation/promotion, with promoted input files consumed according to the accepted step-start resolution policy; [accepted evaluation and human adoption](skill-and-prompt-improvement.md#accepted-evaluation-and-human-adoption) now requires explicit human approval of the exact change and target after evaluation. [Detailed observability UI design](detailed-observability-ui-design.md) must distinguish history/context reuse from resumed execution.

The retained [SSSF study](../research/super-simple-software-factory.md) and its pinned sources explain the reference approach. Their source findings do not validate our future multi-harness implementation. No implementation or runtime test was performed for this amendment.

## Historical discussion, superseded

The following proposals preceded the simplification and were not accepted. References here to unfinished-run migration, retained executable versions, and pending question rounds are historical only.


Claimed on 2026-10-15 after the human accepted the swimlane layout and explicitly asked to continue to the next decision. Both exact prerequisites were verified closed. The accepted retention, configuration precedence, explicit fallback, session recovery, approval invalidation, and limit-increase policies remain inputs, not questions to repeat.

Earlier first-round proposals, superseded by the Resolution above:

1. Should changing workflow code require a new run? Recommendation: retain the original executable definition for an unfinished run; changed workflow code starts a new run that may explicitly reference preserved work. Do not silently replace code on Continue.
2. May the human explicitly change prompts, skills, models, or profiles for remaining work in an existing run? Recommendation: allow a recorded CLI change while paused and quiescent, affecting future attempts only after capability validation. Ordinary file edits affect future runs only. Preserve prior attempt configuration and evidence; invalidate affected approvals or evidence when their bound inputs change. Compatibility determines whether a new session is needed.
3. May the human revise the admitted task plan within the same run? Recommendation: allow a validated, recorded CLI revision while paused and quiescent, preserving superseded task/attempt history and invalidating affected downstream results, gates, and approvals. A plan revision must not silently change workflow code, expand publication authority, or reset consumed budgets.

These proposals were superseded by SSSF-style continuation. Executable retention and suspended-run migration are no longer subsequent branches; history compatibility and current installation lifecycle remain with the lifecycle ticket. No runtime implementation is authorized.
