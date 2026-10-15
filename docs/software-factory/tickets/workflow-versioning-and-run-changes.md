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

- A human explicitly invokes a selected workflow script. The invocation executes the currently installed TypeScript workflow from its entry point, using the current selected configuration and prompt/skill resources. Opening the repository or observer never launches work.
- The human may explicitly join an existing history/context identity, analogous to SSSF's `adw_id`. Joining associates newly executed phases with retained history and may reuse compatible harness conversations. It does not restore a program counter, suspended call stack, queue, task graph execution position, or pending callback.
- Invoking the same workflow again executes its code again. Recorded success does not automatically skip a phase. A purpose-built follow-up workflow may consume saved artifacts or context through explicit inputs, but there is no generic replay, resume-at-failed-step, or state-migration engine.
- Continue, if retained as a command label, means explicit script invocation with selected history/context. It must disclose the workflow being invoked and that execution begins at its entry point. Exact command spelling and history/invocation identity fields remain specification details.
- Agent conversation reuse is separate from workflow continuation. Preserve accepted fresh implementation/review defaults, compatible repair reuse, required capabilities, native permissions, and explicit fallback/fresh-session policies. Adopting SSSF's continuation model does not restrict the product to Pi or copy its model-only compatibility check across harnesses.
- Record distinct invocations and newly executed phases without rewriting prior attempts. History retains events, actual effective settings/instructions, outputs, usage, outcomes, and registered evidence for observation and audit. Record provenance as used; this is not an executable environment snapshot or a promise of reproducibility.

### Changes, versions, and history

| Concern | Current contract |
| --- | --- |
| Workflow code and runtime | Later invocations use the currently installed versions. Retaining old executable bundles, dependency closures, or runtimes for unfinished executions is no longer required. The installation may still pin its current runtime/dependencies for predictable operation. |
| Prompts, skills, profiles, and plan inputs | Later invocations use the selected current files/arguments. A changed plan is validated when admitted by that invocation. No suspended-run patch, plan migration, or automatic cross-invocation impact-analysis feature is required. Live workflow-managed discovery, repair, and freshness checks remain as previously accepted. |
| Changes during active execution | This decision introduces no hot-swapping or mutation protocol. Record the material actually consumed; do not claim a whole-run immutable snapshot. Resource read timing and safe installer updates while processes are active remain lifecycle details. |
| Old results and approvals | Preserve them as history. Joining history does not automatically reuse gate passes, approve new requests, or certify changed inputs. Explicit artifact reuse must satisfy current workflow checks and approval binding. |
| Accounting | Joining the same history does not silently reset an existing bounded allowance or disguise repeated work as a first attempt. Retained usage/allowance records are accounting, not restorable control flow. A genuinely new run has its own explicitly established scope; exact invocation/history accounting representation remains lifecycle work. |
| Upgrade and uninstall | Preserve user-owned files and readable retained history. No restoration of an old execution environment is required to invoke a new workflow. History schema compatibility remains necessary; executable-state migration is removed. Uninstall still refuses active/uncertain owned work and full purge remains separate. |
| Interruption | Preserve partial files, recorded evidence, and honest incomplete status. Further work requires an explicit invocation; no automatic restart or durable resume is promised. |

### Controls and effects that survive the simplification

Pause/Ctrl+C still stops dispatch and interrupts owned work under the accepted grace policy. It no longer promises restoration of a saved execution position. Cancel still marks abandonment and preserves history; any later work must be explicitly authorized as new execution. [Human control and publication](human-control-and-publication.md#resolution) applies this to waits and approvals.

Saved requests and responses may remain evidence, but runner exit does not create an executable checkpoint. Continuing a waiting call requires a live owner; after exit, a later script must reach and validate its own request. No dead native callback is revived.

Removing durable resume does not permit blind repetition of uncertain publication or interference with surviving processes. Keep known ownership checks, current gate validation, authorization, stable publication intent/outcome records, and block-for-human behavior when effects are uncertain. These are bounded lifecycle/publication safeguards, not a general workflow-recovery engine.

### Simplifications and remaining owners

Removed from the initial design: durable workflow executor, serialized execution checkpoints, replay/skip-completed machinery, executable version retention, suspended-run migration, and automatic restoration of pending waits. SQLite remains an observability/accounting store; TypeScript remains the workflow language; SSE remains the selected observation transport. SSSF is the continuation reference, not a wholesale replacement of our stack or unrelated policies.

[Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) now owns process ownership, shutdown, live waits, explicit follow-up invocation, accounting, history integrity, and uncertain-effect handling. [Skill and prompt improvement](skill-and-prompt-improvement.md) owns proposal/evaluation/promotion, with promoted files used by later invocations. [Detailed observability UI design](detailed-observability-ui-design.md) must distinguish history/context reuse from resumed execution.

The retained [SSSF study](../research/super-simple-software-factory.md) and its pinned sources explain the reference approach. Their source findings do not validate our future multi-harness implementation. No implementation or runtime test was performed for this amendment.

## Historical discussion, superseded

The following proposals preceded the simplification and were not accepted. References here to unfinished-run migration, retained executable versions, and pending question rounds are historical only.


Claimed on 2026-10-15 after the human accepted the swimlane layout and explicitly asked to continue to the next decision. Both exact prerequisites were verified closed. The accepted retention, configuration precedence, explicit fallback, session recovery, approval invalidation, and limit-increase policies remain inputs, not questions to repeat.

Earlier first-round proposals, superseded by the Resolution above:

1. Should changing workflow code require a new run? Recommendation: retain the original executable definition for an unfinished run; changed workflow code starts a new run that may explicitly reference preserved work. Do not silently replace code on Continue.
2. May the human explicitly change prompts, skills, models, or profiles for remaining work in an existing run? Recommendation: allow a recorded CLI change while paused and quiescent, affecting future attempts only after capability validation. Ordinary file edits affect future runs only. Preserve prior attempt configuration and evidence; invalidate affected approvals or evidence when their bound inputs change. Compatibility determines whether a new session is needed.
3. May the human revise the admitted task plan within the same run? Recommendation: allow a validated, recorded CLI revision while paused and quiescent, preserving superseded task/attempt history and invalidating affected downstream results, gates, and approvals. A plan revision must not silently change workflow code, expand publication authority, or reset consumed budgets.

These proposals were superseded by SSSF-style continuation. Executable retention and suspended-run migration are no longer subsequent branches; history compatibility and current installation lifecycle remain with the lifecycle ticket. No runtime implementation is authorized.
