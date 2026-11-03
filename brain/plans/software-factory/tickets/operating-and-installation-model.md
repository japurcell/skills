# Operating and installation model

**Type:** grilling
**Status:** closed
**Blocked By:** confirmed-factory-requirements.md
**Research Dir:** not applicable

## Question

Who owns and runs the factory, and what installation and lifecycle contract must the skill provide?

Compare per-repository execution, a per-user local service, and a shared service. Set initial expectations for simultaneous repositories/users, supported operating systems, offline operation, trust and filesystem access, credentials, and start/stop/uninstall behavior.

The current resolution distinguishes installation/version pinning from retained observability history. Durable workflow resume and retention of old executable versions were explicitly removed on 2026-10-15.

Resolution should state the initial operating envelope, installation ownership, and deferred deployment modes. This is a product/deployment decision, not an installer implementation task.

---

## Resolution

Updated on 2026-10-15 by the explicit SSSF-continuation decision. The [continuation contract](workflow-versioning-and-run-changes.md#resolution) owns its detailed semantics. The original 2026-10-12 record below is retained for rationale; conflicting durable-resume and version-retention requirements are superseded.

### Workspace amendment, 2026-10-15

Apply [Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution). Before any phase, bootstrap prepares a factory-owned run worktree from the selected committed revision only, under [committed-revision-only worktree creation](task-scheduling-and-integration.md#committed-revision-only-worktree-creation). Local uncommitted changes are not captured. Planning, implementation, checks, review, and repair use that same repository working directory. The user checkout remains separate; the factory creates no per-task/integration worktrees. A later invocation may explicitly reuse a preserved worktree only after ownership and input checks. Apply [exclusive invocation ownership](task-scheduling-and-integration.md#exclusive-invocation-ownership): one active invocation per worktree, including read-only calls, with internal parallel work and separate-worktree concurrency still allowed. No automatic takeover or process killing to force reuse.

The repository-scoped installation, history, and saved outputs are not disposable workspace contents. Workspace creation does not create another factory installation or change the current-script invocation policy. Worktree cleanup remains explicit; it does not erase retained history or authorize losing partial work. Native permissions remain in force because a Git worktree is not a security sandbox.

### Selected executor and continuation

Use a factory-owned foreground TypeScript runner with local SQLite history, not a durable workflow executor. Each explicit invocation executes the current selected script from its entry point. It may join prior history and explicitly supplied saved context, but starts fresh native conversations and does not restore execution position or automatically skip completed phases. Compatible conversation reuse is limited to corrections within that invocation under [Agent execution profiles](agent-execution-profiles.md#invocation-scoped-correction-conversations). No separate workflow engine, database service, or permanent supervisor is required.

| Decision | Current accepted policy |
| --- | --- |
| Installation and ownership | Per-repository isolated factory directory and dependency files. Keep editable workflows/prompts/settings in version control, managed install files and history outside version control, and application dependencies unchanged. |
| Runtime provisioning | The installation skill manages one pinned Node.js LTS runtime with built-in `node:sqlite`, under the [accepted runtime choice](recovery-and-runtime-selection.md#accepted-node-lts-and-built-in-sqlite). A compatible global runtime or separate SQLite addon is not required. Exact release/platform artifacts remain to qualify. |
| Workflow dependencies | One shared repository factory environment, changed only by explicit idle install/update maintenance under [the accepted dependency contract](recovery-and-runtime-selection.md#accepted-workflow-dependency-installation). Missing/incompatible dependencies fail startup; no invocation-time package installation, automatic lock edits, or per-workflow environments. Application dependencies remain separate. |
| Workflow loading | One startup type-check/build, then generated JavaScript execution under [the accepted build contract](recovery-and-runtime-selection.md#accepted-workflow-build-and-loading). Managed compiler/toolchain is isolated; no global compiler requirement, watcher, hot reload, or factory-managed incremental build cache. |
| Operating envelope | Local single-user operation in trusted repositories; native macOS, Linux, and Windows are validation targets. Existing harness authentication/permissions apply; no mandatory factory sandbox. Credentials stay out of configuration and logs. |
| Offline operation | Local history, inspection, and available local controls require no cloud account. Individual steps retain their own network requirements. |
| Upgrades | Preserve user-owned files and readable history. Later invocations use the current installation. Upgrade managed runtime/dependency files only when the repository installation is idle, across all worktrees; see the idle-only policy below. Do not retain obsolete executable versions merely to resume unfinished work. |
| Pause/Ctrl+C | Stop new dispatch, request graceful interruption, preserve partial work/history, and report uncertainty honestly. There is no durable execution position to resume after exit. |
| History retention | Apply [accepted history preservation for learning](recovery-and-runtime-selection.md#accepted-history-preservation-for-learning): preserve full captured history by default, including after extraction; cleanup is exceptional, informed, explicit, and idle-only. Show storage use and growth. No immutable evidence registry or automatic capture of linked artifacts is required. Interruption does not authorize deleting partial work. History supports observation, not automatic execution reconstruction. |
| Uninstall | Use the [accepted idle maintenance gate](recovery-and-runtime-selection.md#accepted-uninstall-through-the-maintenance-gate): refuse active/uncertain work and a running dashboard host, exclude new starts, and preserve incomplete-operation state after interruption. Remove managed runtime/install files while preserving history and user-owned files. [Built-in full purge is removed](recovery-and-runtime-selection.md#accepted-removal-of-built-in-full-purge); complete removal is documented manual operator work. A later invocation needs an available installation, not restoration of the old run environment. |

Non-interactive native permission enforcement, shutdown grace, worktree isolation, ordinary checks, and bounded attempts remain governed by their owning tickets. Structured `needs_input` ends the invocation after cleanup; no process stays alive solely for human input. Notifications do not select a permanent service or alter the foreground operating model. Managed PR publication is removed; workflows can end with local changes and a report. The [lifecycle ticket](recovery-and-runtime-selection.md) now covers interrupted work and explicit follow-up invocations without durable resume. No runtime or platform behavior has been implemented or proved.

Apply the [accepted manual-cleanup fallback](recovery-and-runtime-selection.md#accepted-manual-cleanup-fallback): unsupported reliable child control uses operator cleanup, with unresolved ownership preserved after runner exit. Upgrade/uninstall refusal remains until clearance under the [accepted cleanup confirmation and ownership release contract](recovery-and-runtime-selection.md#accepted-cleanup-confirmation-and-ownership-release); operator-confirmed clearance remains distinguishable from machine-verified shutdown. Repository-wide idle checks still apply. No permanent supervisor is required.

Apply [accepted saved-history consistency](recovery-and-runtime-selection.md#accepted-saved-history-consistency): repository SQLite owns factory records and captured text/JSON, independently of disposable worktrees. Do not automatically replace damaged/incompatible/unavailable essential storage with empty state or infer idle ownership/unused allowances. Preserve data for explicit repair under the idle migration/backup contract. Ordinary referenced files are not an automatic archive.

Under [accepted notification defaults and reminder ownership](recovery-and-runtime-selection.md#accepted-notification-defaults-and-reminder-ownership), use one on-demand dashboard host per repository shared by browser tabs. It owns opt-in reminders while running; the foreground runner owns initial notices. The host is not a permanent notifier service. Stopping the host ends reminders, whereas closing a browser tab alone need not stop it. Use the [accepted shared ownership mechanism](recovery-and-runtime-selection.md#accepted-shared-ownership-mechanism) for single-host admission, verified existing-endpoint reuse, and explicit stale clearance. Native delivery and concrete atomic/process behavior remain unproved.

### Idle-only managed upgrades

On 2026-10-15 the human accepted upgrades only when the repository installation is idle. The scope is the shared managed runtime/dependency installation, not ordinary edits to user-owned workflows, prompts, skills, or settings.

- Refuse the upgrade while any invocation or uncertain owned process remains across the installation's worktrees. Explain which known activity or uncertainty prevents the upgrade.
- Do not stop jobs automatically, queue an upgrade in the background, or maintain multiple runtime versions for active invocations. The user can finish work or explicitly stop it under the existing interruption policy, then retry the upgrade.
- Prevent new invocations from starting during the upgrade. The idle check and upgrade must be coordinated with launch so that a new run cannot race into an installation being replaced. Use the [accepted shared repository maintenance gate](recovery-and-runtime-selection.md#accepted-shared-repository-maintenance-gate), also used by explicit repair, dependency updates, uninstall, and exceptional history/backup cleanup. Concrete atomic/native behavior remains to qualify.
- Preserve user-owned editable files and readable history. Later invocations use the updated current installation. Stopped workflows and ended needs-input outcomes do not require retaining their old executable environment.
- An ended invocation's result alone does not prove the installation idle when owned children remain active or uncertain. This extends the already accepted active/uncertain-work refusal for uninstall.

The tradeoff is postponing upgrades until activity ends rather than supporting live replacement or runtime-version coexistence. Apply [accepted idle-upgrade coordination and failure handling](recovery-and-runtime-selection.md#accepted-idle-upgrade-coordination-and-failure-handling): stop/exclude the dashboard process during modification; prepare and validate replacements before changing the installation; take a consistent backup before history migration; keep an untouched installation usable after preparation failure, but block invocations after an incomplete modification until explicit repair. Preserve ownership/accounting and user files. No automatic old-backup restoration, empty-database replacement, or workflow restart. Apply [accepted forward-only upgrade repair](recovery-and-runtime-selection.md#accepted-forward-only-upgrade-repair): explicitly reinstall the intended managed version and complete pending transactional migrations, then validate the installation/history pair. No built-in downgrade or general database salvage; preserve data and stop when consistency cannot be established. Concrete staging, validation, and native coordination remain lifecycle specification work. [Upgrade-backup retention](recovery-and-runtime-selection.md#accepted-upgrade-backup-retention) is accepted: retain pre-migration backups until explicit informed cleanup under the existing maintenance gate; no automatic rotation. Step-start input resolution remains separately governed by its owning ticket.

Acceptance must reject upgrades during active invocations in any worktree and uncertain child activity, prevent concurrent launch during upgrade, and preserve editable files/history in a successful idle upgrade. These are future acceptance obligations, not executed tests.

## Historical decision record

Claimed on 2026-10-12. The exact prerequisite, [Confirmed factory requirements](confirmed-factory-requirements.md), is closed. Installation through a skill, customizable workflows, multiple workflows, and live/historical session visibility are already confirmed there. [Workflow authoring and task contract](workflow-authoring-and-task-contract.md) owns the accepted TypeScript authoring contract. Do not ask for those decisions again.

### Confirmed answers

On 2026-10-12, the user accepted native macOS, Linux, and Windows as the initial supported-platform target. Runtime and harness combinations require validation before support can be claimed; this planning decision does not prove portability.

On 2026-10-12, after comparing operating models, the user selected **per-repository installation and one runner per workflow invocation**. Simplicity and ease of upgrade are explicit preferences. Installation scope and process lifetime are separate: installing a factory in each repository does not require a permanent service for each repository.

In the next answer round, the user accepted three additional choices:

- **Repository file ownership:** a dedicated factory directory with separate dependency files and a pinned runtime version. Editable workflows, prompts, and settings are committed; installed runtime files and execution state are Git-ignored. The application's dependency files remain unchanged.
- **Trust and credentials:** local single-user execution in explicitly selected trusted repositories, using existing CLI authentication and permission controls. No mandatory factory-managed sandbox is required. Repository/workflow code remains trusted executable code, and credentials stay out of repository configuration and logs.
- **Offline operation:** local history, inspection, and control work without a factory cloud account or internet connection. Individual steps still require the network access and other dependencies of their configured models and tools.

The user selected **foreground execution**. The earlier automatic-recovery-on-next-invocation policy was subsequently superseded by the explicit Continue decision below.

The final answer round below settles runtime provisioning, upgrade ownership, resumable Pause, history retention, and uninstall defaults. Detailed cancellation/recovery mechanisms remain downstream. Native platform support and real-time session visibility remain required. A shared per-user installation is not selected.

### Former executor and continuation, superseded

On 2026-10-12, after the runtime comparison and the illustrative TypeScript workflow discussion, the user explicitly selected **a factory-owned SQLite executor and human-triggered Continue**.

- The factory owns the execution implementation and stores durable workflow state in local SQLite. A separate Restate server, DBOS/Postgres deployment, or other general-purpose workflow engine is not part of the selected initial architecture.
- Per-repository installation and one foreground runner per workflow invocation remain selected. Opening the repository, UI, or a new invocation must not automatically restart interrupted workflows. The human selects an unfinished run and chooses Continue.
- Continue uses persisted execution state. Selecting this trigger does not authorize blind repetition of completed steps, resetting repair budgets, bypassing human checkpoints, or treating uncertain external effects as safe to repeat. Continue is distinct from approval.
- TypeScript functions with managed operations remain the authoring contract. Deterministic execution and recovery belong to factory code; agents perform reasoning.
- The factory consequently owns checkpointing, run ownership, CLI/effect reconciliation, and state compatibility. This decision does not prove those mechanisms or native Windows support.

The rationale is to fit the selected local foreground lifecycle and editable code-defined workflows without operating a separate workflow engine or database service. The tradeoff is owning durable execution correctness and upgrades. The linked [runtime comparison](../research/embedded-runtime-comparison.md) retains the alternatives and their evidence limits.

The exact SQLite binding/version, database layout, managed-operation method names, replay/graph mechanism, ownership protocol, and schema/version migration design are not selected by the example code. An on-demand UI host and configured agent CLIs may still be separate processes. Runtime provisioning ownership is settled in the final answer round below; exact distribution/version remains to be specified. Detailed recovery requirements remain with [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md), whose engine-choice input is now settled.

### Alternatives considered

Package installation and process lifetime are separate decisions. One versioned installation can launch independent processes for individual runs across repositories. A per-repository runtime could also mean repository-local dependencies without a long-lived service; the comparison below uses an independently managed repository service to distinguish the three lifecycle choices.

| Concern | Per-user local service | Separate service per repository | Process per workflow invocation |
| --- | --- | --- | --- |
| Lifecycle | One supervisor manages the user's repositories and workers. | Each repository has its own supervisor and lifecycle. | Launch a runner for a run; no permanent factory supervisor is required by this model. |
| Upgrade ownership | One installation to update, with coordination for active runs. | Independently pinned versions are natural, but each installation/lifecycle must be managed. | A shared launcher can select a version for new runs while existing processes retain theirs. |
| Human waits | Service remains available to receive decisions and schedule continuation. | Repository service remains available for its runs. | Persist the wait; either keep the process alive or resume through a later command. Automatic waking requires a listener or supervisor. |
| Recovery trigger | A supervisor can automatically restart and reconcile interrupted work. | Same capability within that repository. | Explicit resume by default; automatic restart needs additional supervision. |
| Live UI | One place to collect and expose cross-repository progress. | Aggregate progress from separate runtimes. | Runners persist/stream events; an on-demand UI observer discovers runs and exposes live/history views. |
| Shared resource limits | A central scheduler can enforce limits across repositories. | Requires coordination between repository runtimes. | Requires cross-process coordination if limits apply across runs. |

All three require persisted execution state and external-effect reconciliation for durable recovery. A long-lived process alone does not provide those guarantees. A foreground invocation also does not promise survival after its terminal closes; detachment and child-process ownership need an explicit lifecycle contract. A process per invocation does not necessarily remove an engine's database or service prerequisites.

The earlier shared-installation and background-runner recommendations were superseded by the user's per-repository, foreground choice. The retained comparison explains tradeoffs; it does not override that choice. An invocation-based runner still needs durable managed operations; this operating decision does not authorize weaker recovery or publication guarantees.

The final answer round accepts version retention for unfinished runs and preservation of user-owned edits. Dependency/state-format compatibility and effect reconciliation still require design and validation. Keeping old process binaries alone is insufficient for safe resume; the accepted upgrade policy requires compatibility or deferring the upgrade.

### Foreground recovery and runtime implications

**Runner lifetime and recovery.** The selected foreground lifecycle and explicit Continue trigger are recorded above. Earlier background and automatic-next-invocation recommendations are superseded.

The explanation distinguishes recovery triggers and remaining mechanisms:

- A surviving foreground launcher can restart a crashed worker, subject to bounded restart/backoff policy and reconciliation. This introduces a supervisor role within the invocation; it does not require a permanent daemon.
- If the entire invocation is gone, no code remains there to initiate recovery. Immediate unattended restart then requires an external supervisor or an OS startup mechanism.
- A subsequent invocation drives the specific unfinished run selected through Continue. New work must not silently attach to or restart an old run.

A lightweight foreground supervisor could handle worker failures while an invocation remains alive, but it is not selected. Recovery must reconcile existing agent processes and uncertain external effects and preserve unresolved human checkpoints. Resumable Pause is accepted below. Exact run-selection, compatibility, signal escalation, and orphan reconciliation remain downstream mechanisms.

**Runtime prerequisites.** The user requested the show-me skill to explain these alternatives before choosing the first shape with a factory-owned executor. This table is retained comparison context:

| Shape | Execution and storage | Operational owner |
| --- | --- | --- |
| Runner and local files | Durability logic runs inside the runner and persists state to local files or an embedded database. | No separate engine process to operate; a library may provide durability, or the factory must implement it. |
| Skill-managed local helpers | The runner communicates with a locally installed engine and/or storage helper when needed. | Deterministic installer/start/stop commands invoked through the skill own lifecycle. The user does not manually provision a database or require Docker under this proposal. |
| Separately operated infrastructure | The runner connects to a separately deployed engine/database. | The user or an administrator operates its startup, upgrades, backup, and availability. |

The earlier recommendation to permit an engine/database helper is superseded for initial workflow execution by the selected SQLite executor. A permanent supervisor, separately operated database, and Docker are not required by that architecture. The skill owns JavaScript runtime provisioning under the final resolution. Exact UI and agent subprocess launch mechanisms remain downstream.

The closed [Local runtime prerequisites](local-runtime-prerequisites.md) fact check owns the Restate and DBOS TypeScript requirements. Both need an additional engine/database process; Restate's documented native server does not require Docker. Those facts remain evidence about the alternatives, not prerequisites of the selected executor.

### Research context

The user requested a comparison of embedded TypeScript runtimes against Restate and DBOS, then asked about non-TypeScript options and SSSF's recovery behavior. The [combined runtime comparison](../research/embedded-runtime-comparison.md) links delegated source findings and distinguishes documented capabilities from untested platform/recovery claims. Its earlier library-prototype recommendations are retained as research history; they do not supersede the user's factory-owned executor choice. Python workflows or a cross-language bridge were not selected.

### Historical resolution, superseded where amended

Closed on 2026-10-12 after the human explicitly accepted all five recommendations in the final answer round. The exact prerequisite, [Confirmed factory requirements](confirmed-factory-requirements.md), was verified closed. The confirmed answers and selected executor/continuation sections above, together with this resolution, own the accepted operating contract.

Terminology update on 2026-10-14: the human renamed the resumable Stop control to Pause and accepted a separate terminal Cancel in [Human input and execution controls](human-control-and-publication.md#accepted-pause-and-cancel-controls). The interruption, preservation, and Ctrl+C behavior chosen here is unchanged; current contract wording uses Pause.

| Decision | Accepted policy |
| --- | --- |
| Runtime provisioning | The installation skill manages a pinned JavaScript runtime inside the isolated factory installation. A compatible global runtime is not required. Application dependencies remain unchanged. Exact distribution, version, and SQLite binding remain to be specified. |
| Upgrades with unfinished runs | New runs use the upgraded runtime. Retain the runtime and workflow version needed by unfinished runs, and preserve user-owned files. An upgrade must wait if storage compatibility cannot be maintained. Version identities, migrations, and rollback mechanics belong to the versioning/recovery tickets. |
| Pause or Ctrl+C | Stop new dispatch, request graceful interruption of active agent work, preserve recorded progress, and leave the run resumable through Continue. This does not guarantee an external effect was rolled back or every child process stopped; escalation and reconciliation require detailed design. |
| History retention | Retain completed-run history, transcripts, and artifacts until explicit cleanup, with storage usage visible. Protect unfinished-run recovery data from routine cleanup. |
| Uninstall | Remove managed runtime/install files while preserving execution history, unfinished-run data, and user-owned workflows, prompts, and settings. The later [full-purge removal](recovery-and-runtime-selection.md#accepted-removal-of-built-in-full-purge) supersedes the separate purge action anticipated here. Retained data alone does not make a run executable after uninstall; a compatible installation must be restored before Continue. |

The initial envelope is local single-user operation in trusted repositories on native macOS, Linux, and Windows, with separate repository installations and foreground invocations. A shared per-user runtime service and a shared team service are outside this initial envelope. The selected architecture needs no separate workflow engine or database service. Configured agent CLIs retain their own authentication, permission controls, and network needs.

Remaining work has existing owners: [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) for compatible retained definitions and intentional changes; [Human input and execution controls](human-control-and-publication.md) for cancellation, intervention, and child-process behavior; [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) for execution ownership, SQLite/replay mechanisms, and failure acceptance; and the live-progress/UI tickets for observer lifecycle and rendering. Do not reopen the policy choices recorded here when designing those mechanisms.

No new decision ticket is needed. No executor, installer, upgrade, signal-handling, native-platform, or recovery behavior was implemented or tested in this planning session.

