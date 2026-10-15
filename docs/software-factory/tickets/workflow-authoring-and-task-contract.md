# Workflow authoring and task contract

> Continuation amendment, 2026-10-15: [current workflow invocation](workflow-versioning-and-run-changes.md#resolution) executes from its entry point. Managed operations instrument and validate work; they do not imply serialized checkpoints, replay, or durable workflow resume.

**Type:** grilling
**Status:** closed
**Blocked By:** confirmed-factory-requirements.md
**Research Dir:** not applicable

## Question

What is the smallest code-defined workflow contract that supports arbitrary workflow structure and both imported and agent-generated task graphs?

Discuss workflow definitions versus run data; custom stages, conditions, nesting, parallel work, and bounded loops; task identity, dependencies, acceptance criteria, and artifacts; plan import and ambiguity handling; and which invariants every custom step must honor.

Decide how much structure authors must declare so the UI can show planned work and dynamically discovered work. Consider plain TypeScript functions, a constrained builder, and configuration-driven recipes without assuming one is selected.

Resolution should include vocabulary, example contracts for the user's default workflow and one structurally different workflow, validation rules, and the chosen extension seam. Do not implement the runtime.

---

## Resolution

Accepted on 2026-10-12 through the live exchange: the user selected three authoring choices, selected both task-record and ambiguity recommendations, then answered "accept all" to the four remaining contract details. The prerequisite, `confirmed-factory-requirements.md`, was verified closed. This resolves the authoring and task contract; it does not authorize implementation.

### Prior answers applied

[Confirmed factory requirements](confirmed-factory-requirements.md) owns the prior human answers. Its requirements for code-controlled orchestration, fully customizable workflow structure, both planning entry points, task dependencies, step-specific agent choices, configurable verification/review/checkpoints, and real-time visibility apply here without renewed questions. The six-stage use case remains an example recipe.

The decisions below do not adopt earlier runtime code sketches wholesale. The subsequently selected executor is recorded in [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation); [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns its remaining mechanisms and proofs.

### Confirmed answers, round one

The user explicitly selected all three recommended options on 2026-10-12:

1. **Authoring interface:** TypeScript functions with managed operations. Code owns control flow; configuration supplies values. Authors use a small managed-execution interface for steps, parallel work, and checkpoints. Conditions, ordering, parallel groups, and bounded loops remain code-defined; durability details depend on the later runtime decision.
2. **External plan intake:** accept both prose and structured graphs. Convert prose to a validated task graph and surface material ambiguity. Preserve the original plan alongside the normalized representation. Round two below settles the minimum task record and the default ambiguity response.
3. **Visibility before execution:** a declared outline plus discovered tasks. The outline describes expected stages and expansion points; concrete work appears as discovered. Unknown future work stays visibly unknown. The outline is descriptive metadata, not a second executable graph.

These choices will not be asked again. Human checkpoint policy, scheduling, runtime choice, and event transport retain their own tickets.

### Confirmed answers, round two

The user explicitly selected both recommended options on 2026-10-12:

4. **Minimum task record:** every executable task requires an ID, title, objective, dependencies, and acceptance criteria. Optional typed inputs and artifact references provide extensions. Acceptance criteria can be prose; they need not all be automated tests.
5. **Consequential plan gaps:** clarify consequential gaps in scope, dependencies, or acceptance criteria before admitting the affected graph for execution by default. Mechanical normalization proceeds automatically. A custom workflow can explicitly override the ambiguity policy; this does not waive required task fields or structural validation.

These answers are settled and must not be asked again. Holding an ambiguous graph does not add mandatory human approval to every valid plan or change the separately configurable pre-PR checkpoint.

### Accepted contract

The final acceptance covers task data versus code, graph validation, the managed-step interface, and nested scope identities. These details complete the five choices recorded above.

**Vocabulary and separation:** a workflow definition is a reusable TypeScript routine; a run is one invocation with its inputs and recorded execution; a task is a deliverable work item from a plan; a step is a managed operation within a workflow; a session is a concrete harness conversation attached to a step attempt; an artifact is a referenced input, output, or evidence object. A task graph is run data. A workflow may use a task graph, but workflows without implementation tasks remain valid.

**Task data:** require a stable graph-local `id`, a human-readable `title`, an `objective`, a `dependsOn` list (possibly empty), and explicit `acceptanceCriteria`. Optional fields reference source context, input artifacts, expected outputs, and typed workflow-specific inputs. A task may select a named task routine defined by the workflow; executable code stays in TypeScript modules rather than imported plan records. Agent profile and skill/prompt selection remain available at steps, with precedence owned by the execution-profiles ticket. A one-task change uses the same contract; no artificial decomposition is required.

**Validation:** check unique identities, valid dependency references, absence of cycles in each admitted task graph, required fields, and the selected routine's input schema before admitting that graph for execution. A cyclic task dependency graph is invalid even though the surrounding workflow may contain an explicit bounded repair loop. Acceptance criteria may be human-readable; automated checks and acceptance evidence are configured by the verification/review policy rather than inferred from a string alone.

**Plan import:** preserve source provenance. An agent may interpret prose and propose a normalized graph; code validates the result. Normalization is not permission to execute newly invented scope. Confirmed default: normalize harmless formatting and wording, but surface missing acceptance criteria or consequential scope/dependency ambiguities as questions and withhold admission of the affected graph until resolved. Workflows can explicitly define another ambiguity policy while still producing valid task records. Mandatory approval of every valid plan is not implied.

**Extension seam:** custom routines execute through the managed-step interface. Each visible operation has an identity, parent scope, input/output references, attempt identity, recorded outcome, and associated sessions. Pure helpers need no separate step; external effects and agent sessions use managed operations so progress and recovery are not hidden. The interface must expose failure and waiting, and separate an agent's process completion from the workflow's acceptance decision. Managing an external effect does not itself guarantee exactly-once execution. Exact runtime methods, event schemas, process recovery, and effect reconciliation remain downstream decisions.

**Nesting and outline:** named scopes describe the expected stages; a scope may execute a reusable routine, parallel branches, or an admitted task graph. Dynamic children attach to their scope and are registered before execution begins; the live UI consumes their progress. Declared work remains distinguishable from discovered, running, skipped, and finished work. The outline must not imply a complete statically known graph. Outline declarations and execution should reference the same named scopes to limit drift; the UI ticket determines rendering and the event ticket determines delivery behavior.

**Example contracts, not required stages:**

| Example | Input and declared outline | Discovered work and result |
| --- | --- | --- |
| Repository change | Prompt, prose plan, or structured graph; plan, implement, verify, review, optional human checkpoint, publish, improve | Normalized implementation tasks populate the task scope. Workflow code chooses per-task or aggregate review, optional browser verification and human review, and bounded repair policies. Result references changes, evidence, publication outcome if requested, and improvement candidates. |
| Read-only repository audit | Repository reference and audit questions; inventory, parallel investigations, synthesize, report | Inventory discovers investigation branches and their sessions. No implementation task graph, code repair, or PR is required. Result is a report with evidence references. This exercises arbitrary structure without treating the change recipe as a fixed pipeline. |

### Downstream decisions and limits

- Code-level scopes and reusable routines are accepted. Their mapping to observable scopes remains a schema detail; no persisted execution position is required.
- Agent configuration precedence belongs to [Agent execution profiles](agent-execution-profiles.md). Scheduling, workspace ownership, and integration belong to [Task scheduling and integration](task-scheduling-and-integration.md).
- Review policies, evidence requirements, and exact repair limits belong to [Verification and review policy](verification-and-review-policy.md). Human control and publication policy remain in their own ticket.
- Event schemas and delivery behavior belong to [Session events and live progress](session-events-and-live-progress.md); visual interaction belongs to [Swimlane interaction design](swimlane-interaction-design.md). The accepted outline does not choose a transport or UI layout.
- Current inputs and later invocation semantics belong to [Workflow versioning and run changes](workflow-versioning-and-run-changes.md). Structural validation alone does not authorize arbitrary edits to an active run.

No new decision ticket is needed from this resolution: these downstream questions already have owners. The two examples are design checks, not executable proof. No runtime, adapter, recovery, or real-time delivery behavior was implemented or tested here.

