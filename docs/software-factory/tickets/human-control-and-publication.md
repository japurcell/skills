# Human input and execution controls

> Current policy, 2026-10-15: non-interactive harness steps with explicit permissions; structured `needs_input` ends the invocation; human decisions occur in later explicit invocations. No live human waits or native approval bridge. Managed PR publication remains removed. Earlier conflicting decisions below are historical.

**Type:** grilling
**Status:** closed
**Blocked By:** task-scheduling-and-integration.md, verification-and-review-policy.md, codex-permission-feasibility.md, copilot-gemini-permission-feasibility.md, opencode-pi-permission-feasibility.md
**Research Dir:** not applicable

## Question

How does the factory request human attention without interactive harness calls or a live human-response subsystem?

## Resolution

On 2026-10-15 the human accepted non-interactive harnesses, structured `needs_input` outcomes, and the notification recommendation after clarifying that human review is not a mandatory stage. This supersedes optional live factory questions/reviews and factory-mediated native approval callbacks. Managed PR publication was removed earlier on the same date. The filename remains for existing links. This is a planning decision, not implementation authorization.

### Non-interactive execution and permissions

- Run managed harness steps without a live human answer channel. Supply instructions and effective permissions before launch, stream supported output, and capture the result. The exact CLI/RPC/SDK mode is adapter-specific and requires validation; non-interactive does not prescribe a single protocol.
- Preserve native permission enforcement and existing authentication. Non-interactive does not mean blanket approval, disabling a sandbox, or widening access. Operations outside explicit permissions must be denied or reported as blocked. Do not silently switch to a permissive mode to keep work running.
- Remove factory translation/routing of native questions and approval callbacks, pending native-request registries, live grants, response withdrawal, and live response deduplication machinery. Delegation grants no extra authority; internal children must operate within the supported non-interactive permission contract.
- Reject unsupported required behavior under [selected profile or failure](agent-execution-profiles.md#selected-profile-or-failure); do not automatically substitute another profile. A harness that cannot provide the selected permission policy without interaction is not qualified for that profile. Unexpected interactive behavior must surface as unsupported/blocked failure and terminate safely, never an invisible wait or automatic approval. Concrete detection and cleanup remain lifecycle/adapter work.

### Structured outcomes and human decisions

- Normal work proceeds automatically through configured phases, checks, review, and bounded corrections. There is no mandatory human plan/candidate approval stage or factory-supported live review phase.
- Use a schema-valid `needs_input` outcome when progress requires a human decision, clarification, or authorization. Preserve the question, relevant context, suggested answers where useful, saved outputs, and partial work. Exact field names and schema remain specification details.
- `needs_input` is a recognized non-success outcome, not malformed output and not a reason to launch automatic format corrections. Stop further workflow dispatch, safely finish/stop owned work, record the outcome, and exit the invocation. Process shutdown uncertainty remains visible and blocks unsafe workspace reuse; the result alone is not proof that children stopped.
- A failed operation, unsupported capability, or exhausted correction allowance remains a failed outcome, not automatically a question. Notify the human of the failure. Use `needs_input` only when an actual decision or missing input is identified; never disguise execution failure or approval refusal as success.
- Human decisions are required only when `needs_input` identifies them, not as a routine gate. Failure may require intervention without requiring an answer to a question. The user may voluntarily inspect or change inputs between invocations.
- Answers arrive as explicit CLI/configuration inputs to a later invocation. That invocation executes the selected current script from entry, may explicitly select preserved work/history and saved inputs, starts fresh native conversations, and validates current inputs and permissions. It does not resume a suspended phase or invoke an old callback. History records which prior question/context the new input addresses; it grants no authority by itself.
- Keep selected input/candidate identity and explicit authorization meaningful across invocations. Changed or missing relevant inputs cannot silently inherit an old approval. This does not require a live response ledger, immutable evidence archive, or generic approval engine.
- No process remains alive solely awaiting a human response. Live wait deadlines and human-wait exclusions from managed attempt timers are removed. Explicit allowance increases remain recorded without resetting consumed counters; answering a question or joining history is not an increase.

Apply the [accepted needs-input and invocation finalization contract](recovery-and-runtime-selection.md#accepted-needs-input-and-invocation-finalization): save the minimal actionable question before cleanup, interrupt other active managed calls, preserve results received during shutdown, and distinguish the execution outcome from cleanup. Incomplete finalization remains unknown; question answers and ownership release are separate actions. Exact result field names and exit-code values remain specification details.

### Notifications

| Outcome | Accepted notification behavior |
| --- | --- |
| `needs_input` | Prominent desktop notification, persistent dashboard “Needs input” status, and a clear CLI message. |
| Failed invocation or exhausted corrections | Prominent desktop notification explaining the blocker and next action, with saved failure status and CLI output. |
| Successful completion | Quiet completion notification, configurable. |
| Normal progress or successful automatic correction | Dashboard updates only; no attention notification. |

Attention notifications identify the repository and run and explain the outcome. Native clickable links are optional under [accepted optional notification links](recovery-and-runtime-selection.md#accepted-optional-notification-links); saved details remain accessible through the CLI/dashboard independently of desktop delivery or click support. Questions include suggested answers where useful. Notification delivery is separate from execution: dismissing or missing a notification cannot discard the saved question, authorize work, or keep a runner waiting. The dashboard remains observability-only; supported notification links open details, not execution actions. Do not keep senders alive solely for clicks or automatically start the dashboard to open old alerts. Later explicit inputs do not erase the earlier invocation's saved outcome.

On 2026-10-15 the human accepted bounded notification delivery and dashboard-scoped reminders:

- Save the invocation outcome before attempting a desktop alert. Bound the delivery attempt with a timeout. If delivery fails or permission is denied, preserve the original outcome, record a separate delivery warning, show that warning in CLI/dashboard, and exit according to the original outcome. Do not keep the runner alive retrying notification delivery.
- Surface known notification unavailability before work starts. Desktop attention is best effort; a user away from the terminal may miss the event. Saved questions and outcomes remain available independently of delivery.
- Reminders are configurable and disabled by default. When enabled, reminders run only while the dashboard runs. Closing it stops reminders; reopening shows outstanding attention items without replaying a backlog of missed alerts. Do not install a separate background notifier or keep an invocation alive to deliver reminders.
- Acknowledging a reminder only silences it. Reminder preferences and acknowledgment are notification metadata, not workflow inputs. They cannot answer a question, change an invocation outcome, authorize execution, or broaden the dashboard into an execution controller. This is a narrow allowance for notification controls within the observability UI; workflow mutation endpoints remain prohibited.

Apply [accepted notification defaults and reminder ownership](recovery-and-runtime-selection.md#accepted-notification-defaults-and-reminder-ownership): one initial summary per invocation from the runner, a configurable five-second delivery timeout, and opt-in grouped repository reminders with a configurable fifteen-minute interval. One on-demand dashboard host per repository serves its browser tabs and owns reminders; repository SQLite stores preferences and per-invocation acknowledgment. Wait a full interval after startup/enablement and do not replay missed alerts. Stopping the host stops reminders; closing a browser tab alone may not stop the host. Exact native delivery, schema/single-host coordination, and presentation remain specification/qualification work. Delivery and native-platform behavior have not been implemented or proved.

### Accepted Pause and Cancel controls

- **Pause/Ctrl+C:** stop new dispatch, request graceful interruption, retain files/history, allow the accepted configurable thirty-second grace, then terminate only positively identified owned processes. Report uncertainty. No restorable execution position is saved.
- **Continue:** if retained as a label, explicitly invoke the current selected script from entry, optionally joining history/context. It neither skips completed phases nor grants approval or extra allowance.
- **Cancel:** mark abandonment while preserving files/history; handle owned work and surface unresolved activity. Subsequent execution requires an explicit invocation.

Apply [Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution): one worktree before all phases; stable candidate handoff; unsafe reuse blocked by uncertain child activity. Uninstall still refuses active or uncertain owned work. Non-interactive execution does not remove process ownership or cleanup obligations.

Apply the [accepted manual-cleanup fallback](recovery-and-runtime-selection.md#accepted-manual-cleanup-fallback). Use reliable automatic child cleanup where supported; otherwise preserve blocked ownership, explain the known activity and limitation, and notify the operator that manual cleanup is required. The runner may exit with unresolved cleanup recorded rather than waiting for the operator. This does not claim children stopped or turn a cleanup failure into a human question. Later clearance follows the [accepted cleanup confirmation and ownership release contract](recovery-and-runtime-selection.md#accepted-cleanup-confirmation-and-ownership-release): explicit confirmation and a short cleanup note, available checks, and atomic release of the inspected claim. Operator-confirmed clearance is distinct from machine-verified shutdown and does not launch work or answer a structured needs-input question.

### Publication remains removed

There is no built-in push/PR operation, draft-PR default, publication authority model, publication intent ledger, remote-outcome reconciliation, base-refresh publication protocol, or duplicate-PR guarantee. Workflows may finish with local changes and a report. A user or explicitly authored custom workflow may publish under its own authorization and failure handling; arbitrary command capability grants no publication authority or safe-retry guarantee. Do not recreate publication management as a generic effect engine.

### Acceptance obligations

1. Complete ordinary workflow phases without human approval, preserving configured permissions and required capabilities.
2. Return valid `needs_input`, save the actionable question/partial work, stop owned work, and exit without waiting or launching correction attempts for that valid outcome.
3. Supply a later explicit answer, validate current inputs, and start from script entry without reviving callbacks, skipping phases automatically, or resetting allowances.
4. Reject or report restricted operations and unsupported interactive requests without broadening permissions; exercise child shutdown uncertainty separately.
5. Show needs-input, failed, and completed outcomes accurately; exercise desktop/CLI notices, persistent history, unavailable notification delivery, and no repeated reminders by default. Dismissing a notice must not execute work or lose the question.
6. Preserve interruption and data-preserving uninstall; finish local workflows without managed publication or an immutable evidence registry.
7. Exercise denied, unavailable, and stalled desktop delivery: preserve the original outcome, show a separate warning, and exit within the configured delivery bound. Show known unavailability before launch.
8. Verify reminders are off by default and stop with the dashboard. Reopening shows outstanding items without replaying missed alerts. Acknowledgment silences reminders without answering, authorizing, or changing execution history.

No runtime, notification delivery, or harness capability has been implemented or validated. [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns remaining mechanisms. The historical record below retains superseded live-wait, publication, and immutable-evidence policies.

## Historical decision record

### Observability-only amendment, 2026-10-15

The human explicitly changed the product direction: the web UI is only for observability, accepts no workflow inputs, and all inputs come through configuration or command arguments. This revises an earlier decision; do not ask it again.

- Remove browser actions that launch, pause, continue, cancel, approve, deny, withdraw approval, submit feedback, increase allowances, edit execution settings, or publish. Do not retain mutation HTTP endpoints in the observer's public interface merely because a button is hidden.
- Configuration and runtime interventions originate through CLI commands/configuration. The dashboard shows recorded effects and outstanding waits. It may display instructions or a command to run elsewhere, but cannot execute it. Exact CLI syntax and delivery to an active foreground runner remain to be designed.
- Keep approval binding, duplicate/stale-response handling, withdrawal ordering, one-action grants with profile-gated broader scopes, and publication authorization. Moving input out of the browser does not relax these guarantees or imply blanket preapproval in configuration.
- Keep the foreground runner alive for live native permission waits. CLI responses must target the matching live request and owner. The later continuation amendment removes executable factory checkpoints after runner exit. Historical requests remain evidence; commands cannot revive dead native callbacks.
- The later continuation amendment replaces resumable Pause/Continue with explicit script invocation. Keep shutdown grace, budgets, optional live human gates, retained history, and publication policies.
- Keep SSE as the read-only observation stream. The previous browser-facing HTTP control decision is superseded. CLI-to-runner communication must not silently turn the observer back into an execution service.

Presentation interpretation for the revised prototype: navigation, search, filters, expanding details, and freezing/following the stream change only the local view. Prototype-only design annotations are separate from product workflow input. These do not authorize execution mutations. [Swimlane interaction design](swimlane-interaction-design.md) owns review of that presentation.

Native-protocol research remains relevant to mediated CLI responses, but does not validate the new transport. [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns request delivery, ownership, authentication, and reconciliation. [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) owns configuration/version changes. Existing acceptance scenarios must substitute CLI response/control submission for dashboard submission, preserve their other assertions, and add absence/rejection of observer mutations. This ticket remains closed with this policy amendment; UI design remains in progress.

Claimed on 2026-10-14 after verifying both exact prerequisites, `task-scheduling-and-integration.md` and `verification-and-review-policy.md`, are closed. The user requested this ticket explicitly. This is planning only; no runtime implementation or external publication is authorized.

### Prior answers applied

- [Confirmed factory requirements](confirmed-factory-requirements.md#confirmed-requirements) already makes pre-PR human review configurable. Arbitrary code-defined workflows may place checkpoints where needed; the six-stage recipe is not a mandatory pipeline. Do not ask whether human pre-PR review is always required.
- [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation) owns one foreground runner per invocation and explicit human-triggered Continue. Opening the repository, dashboard, or a new invocation does not automatically resume old work. Continue is not approval, a budget reset, or permission to blindly repeat effects.
- The [operating resolution](operating-and-installation-model.md#resolution) already selects resumable Pause/Ctrl+C, preserving work and history, and data-preserving uninstall. The later [full-purge removal](recovery-and-runtime-selection.md#accepted-removal-of-built-in-full-purge) supersedes the separate purge originally anticipated here. Pause stops new dispatch and requests graceful interruption rather than merely draining active steps. The control was originally named Stop; the accepted rename below changes its label, not its behavior. Its signal escalation and uncertain child-process handling remain mechanisms for this ticket and recovery.
- [Agent execution profiles](agent-execution-profiles.md#resolution) owns existing harness authentication and permission controls, with no mandatory factory sandbox. Native tool approvals stay distinct from workflow checkpoints and cannot be silently approved or bypassed. The initial trust model is local single-user operation in explicitly selected trusted repositories, with credentials outside repository settings and logs.
- [Session events and live progress](session-events-and-live-progress.md#resolution) owns the independent on-demand repository dashboard, saved-before-display events, SSE updates, separate HTTP controls, and immutable registered evidence. Closing the dashboard does not stop an independently running invocation. Round two below settles the UI Continue interaction; platform and ownership mechanisms remain unverified.
- [Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution) owns independent-branch progress, parking unintegrated candidates awaiting input, and pausing ordinary scheduling when stale code is already integrated. A human response cannot bypass rebuilding/rechecking a parked candidate against changed combined inputs.
- [Verification and review policy](verification-and-review-policy.md#resolution) owns required/advisory gates, criterion-level evidence, bounded repair and correction, attempt timeouts, and one reviewer-clarification round before unresolved disputes reach a human. Missing required evidence and exhausted allowance do not become success through Continue. Attempt timeouts exclude recorded human waits but do not select checkpoint deadlines.
- Stale approvals and duplicate publication remain required acceptance scenarios from the user's earlier prototype request. Task/gate acceptance does not itself authorize publication. Round two settles approval binding and stale/duplicate response policy; storage mechanics and remote-effect reconciliation remain to be specified. Do not treat prior illustrative methods as finalized interfaces.

### Confirmed answers, round one

On 2026-10-14, the human explicitly accepted the following four choices, requested a Cancel comparison, then accepted both controls with the rename recorded below:

1. **Checkpoint deadlines:** no deadline by default, with the request saved across runner exits. Workflow code may configure expiry and its outcome; expiry never implies approval. A twenty-four-hour default deadline was not selected.
2. **Request changes:** route human feedback to the recipe's configured repair step within existing budgets, then run required checks and create a new checkpoint for the changed candidate. Feedback does not silently expand scope. Waiting for manual edits was not selected as the default.
3. **Limit increases:** allow an explicit UI action showing consumed allowance and the proposed new total for the selected scope, recording the change without resetting counters. Continue alone adds nothing; checks and publication authorization remain separate. Requiring a new run merely to obtain more allowance was not selected.
4. **Initial publication hosts:** GitHub PRs first, behind a managed publication interface that can support later hosts. Adding GitLab or Azure DevOps to the initial built-in scope was not selected. This is product scope, not verified provider behavior.

These four choices are settled and must not be asked again.

### Earlier Pause and Cancel controls

On 2026-10-14, after the comparison, the human explicitly chose both controls and renamed **Stop** to **Pause**. This completes the first round's fifth choice. The product controls are Pause, Continue, and Cancel; there is no separate Stop control or newly selected drain-only Pause action.

- **Pause:** stop new dispatch, request graceful interruption of active work, and preserve the unfinished run for Continue. Saved state, pending checkpoints, consumed budgets, and applicable elapsed-time accounting remain intact. Ctrl+C keeps this same resumable behavior. Pause does not mean suspending every process in memory or letting all active steps finish first.
- **Continue:** resume the selected unfinished run under the already accepted reconciliation, version, evidence, and budget rules. It does not approve a checkpoint or add allowance.
- **Cancel:** end the run after active work and effects are reconciled. Retain history, evidence, and partial changes, but do not allow Continue on the cancelled run. Further work requires a new run, which may explicitly use preserved changes as inputs.

Pause fits "resume this run later"; Cancel fits "abandon this run." Both request interruption and preserve evidence. Neither deletes history, discards code, or automatically undoes a PR or push that already happened. Ended cancelled runs must remain distinguishable from resumable unfinished runs. Exact stopping/escalation behavior still follows the unresolved mechanism questions below.

The alternative of keeping only a resumable control was not selected. Do not ask the human to choose these controls or their names again. No subsequent question round was started while answering the naming question.

### Confirmed answers, round two

Resumed on 2026-10-14 under the existing claim after rechecking both exact prerequisites as closed. The human accepted choices 2 through 5, requested an example for choice 1, then explicitly accepted approval binding as recommended. All five choices are now settled and must not be asked again.

1. **Approval binding:** bind checkpoint approval to the specific request, candidate revision, registered evidence, applicable gate policy, and requested action. Changes to those inputs require a new checkpoint; unrelated progress does not invalidate approval. Repeated delivery of the same response returns its saved outcome; stale or conflicting responses cannot replace it.
2. Allow checkpoint responses to be saved while a run is paused or has no runner, without dispatching work. Continue remains a separate action. An active runner may consume a valid response without an additional Continue, provided the run is not paused.
3. When no runner exists, have UI Continue present an exact command for the user to run in a foreground terminal. When an invocation remains attached, route Continue to it. Do not add a background workflow supervisor. Automatically opening a visible terminal is an alternative requiring platform validation.
4. Use a draft GitHub PR as the supplied publication recipe's default outcome, with ready PR and local-only outcomes explicitly configurable. Custom workflows remain unrestricted within their granted authority.
5. Confirm the publication scope when launching a run: destination repository, base branch, factory-owned source branch, and allowed actions. A configured run may push that branch and create its selected PR outcome after its gates pass, without another prompt unless a checkpoint is configured. Expanding this scope requires a new explicit authorization. Merge and deployment remain separately authorized actions.

All five choices specify accepted product policy, not implemented controls or verified GitHub behavior. Provider reconciliation, local authorization, native permission routing, and process escalation remain subsequent branches. No remote action or runtime implementation is authorized by this planning exchange.

The accepted approval-binding example concerns a paused run proposing a draft PR for revision R42, with captured test and review evidence under a named gate policy. A response saved while paused does not dispatch publication. If a separately authorized repair later produces R43 before publication, a new checkpoint is required and approval submitted from an old R42 browser tab is rejected. A duplicate delivery of the already recorded R42 response returns that historical outcome without approving R43 or repeating publication. Unrelated progress does not invalidate the request. Changed evidence, gate policy, or requested action also requires a new checkpoint. Launch authorization defines permitted publication scope, while an optional checkpoint decides whether a particular candidate is approved within that scope. Duplicate-response handling alone does not prove duplicate-publication prevention; remote-effect reconciliation remains separate.

### Confirmed answers, round three

On 2026-10-14, the human accepted choices 1, 2, 4, and 5, requested an interruption example, then explicitly accepted the configurable thirty-second grace period followed by termination of owned processes. All five choices are settled; do not re-ask them.

1. Allow explicit withdrawal of an unused approval. Record withdrawal as a new event rather than rewriting the original response. Withdrawal that wins before action dispatch blocks that action and requires a fresh checkpoint; if dispatch already won, show that the action may have happened and reconcile it without promising rollback. This is an intentional control, distinct from a conflicting duplicate response.
2. When only durable factory checkpoint waits remain and no active work or unresolved effects require supervision, save the waits and exit the foreground runner by default. The independent dashboard retains the requests; answering them does not resume execution, and Continue supplies the foreground command. The subsequently accepted native-wait distinction below keeps the runner alive for live harness permission callbacks.
3. **Interruption escalation:** after Pause or Cancel requests graceful interruption, allow thirty seconds by default, configurable, then terminate processes the factory can positively identify as owned by that invocation. Preserve work and mark interrupted attempts incomplete. Unknown ownership or uncertain effects block reconciliation rather than permitting unrelated process termination or assuming success. Requiring a separate Force stop action was not selected. Native-platform mechanisms and actual guarantees remain unverified.
4. Refuse uninstall while runners or owned work remain active or their status is uncertain. Show the affected runs and require explicit Pause or Cancel plus reconciliation before retrying uninstall. Unfinished saved runs remain preserved under the accepted uninstall policy. Automatically coordinating Pause as part of uninstall is the alternative.
5. If publication detects unexpected remote changes, such as another actor changing the factory-owned branch or an existing PR's target/state, block the publication step and show the discrepancy for human resolution. Do not automatically overwrite, reopen, retarget, or create a replacement. An explicitly configured reconciliation policy is the alternative; this choice does not define how ordinary base-branch advancement affects verification.

These policy questions require no new claims about provider APIs or native signal support. Exact dispatch/withdrawal ordering, ownership, and persistence mechanisms retain their downstream recovery owner.

The escalation explanation uses a hypothetical browser-test command whose cleanup hangs while closing a child browser. The factory stops dispatching and requests interruption, but the test process or child may remain alive. This is a process-lifecycle failure, not an agent deliberately refusing the human. A harness could also acknowledge interruption without successfully stopping a tool it launched. The accepted grace period allows orderly shutdown; termination limits lingering owned work where supported but can leave partial files or incomplete cleanup. The UI must not claim quiescence while owned work may still run, and killing a local process cannot undo a remote effect already accepted. These are illustrative failure modes, not observed bugs or validated behavior of any named harness. The thirty-second value is a configurable starting default, not a measured optimal timeout or a guarantee of termination within thirty seconds.

### Confirmed answers, round four

On 2026-10-14, the human accepted choices 2, 3, and 4, requested focused native capability research, then explicitly selected the dashboard approval inbox and keeping the foreground runner alive during native permission waits. All four choices are settled; do not re-ask them.

1. **Dashboard approval inbox:** use a shared dashboard inbox through harness-specific native protocol adapters, preserving distinct capabilities and permission semantics. Keep the foreground runner alive for native permission waits. The earlier proposed native-terminal default was not selected; the accepted contract below owns the details.
2. If pushing succeeds but PR creation fails or remains uncertain, retain the branch and report partial publication. Reconcile before any retry; do not automatically delete the branch as compensation. Explicit cleanup remains separate. This is an alternative to configured compensating branch deletion after a definitively failed creation.
3. If the destination base branch advances before publication, rebuild the candidate against the new base, rerun affected required gates, and obtain fresh approval if configured. Apply existing repair, freshness, and budget rules; never silently carry old approval to changed inputs. This is an alternative to publishing the verified fixed-base candidate while clearly recording that the current base was not verified. Repeated base movement may keep publication blocked; no unlimited refresh allowance is implied.
4. End the supplied recipe after the configured local gates pass and publication is confirmed. Display remote CI as outside that default completion claim. Waiting for remote CI can be an explicit workflow step, but does not imply merge or deployment authority. The alternative adds remote CI to the default recipe's completion gate.

The remaining engineering specification must derive control request identity, saved outcomes, scoped local control access, and publication intent/reconciliation from accepted policy. These are not reasons to re-ask the human whether stale approvals, duplicate publication, or unauthorized actions should be prevented. Provider-specific facts require delegated research before claiming a working mechanism; native adapter capabilities and platform shutdown need later conformance evidence.

### Native interaction evidence audit

The retained [Harness adapter feasibility](../research/harness-adapters.md) study, dated 2026-10-08 and inspected on 2026-10-14, identifies integration entry points rather than validating factory adapters. It explicitly leaves Codex interactive-approval protocol selection and Copilot approval behavior unproved. Its Gemini, OpenCode, and Pi rows document headless/event/RPC surfaces without establishing the proposed native permission-routing contract. It records no live agent invocation or adapter conformance test. The closed [Agent execution profiles](agent-execution-profiles.md#resolution) likewise qualifies platform/capability compatibility rather than proving it.

That initial survey was insufficient to select native interaction routing on feasibility grounds. A foreground factory process does not itself establish usable interactive input for multiple concurrent harness sessions. The focused studies below now cover permission detection/response, terminal and concurrency constraints, interruption, restart, policy scope and native platform documentation. They distinguish documented support, source inference, and local probes. No bypass or assumed auto-approval is an acceptable substitute for a missing required capability.

On 2026-10-14, the human explicitly requested delegated research for all five harnesses. Three assigned research tickets now own that prerequisite: [Codex permission feasibility](codex-permission-feasibility.md), [Copilot and Gemini permission feasibility](copilot-gemini-permission-feasibility.md), and [OpenCode and Pi permission feasibility](opencode-pi-permission-feasibility.md). The human requested findings and a feasible recommendation, not automatic adoption of a design. Any live conformance experiment must have an explicit scope and report its own evidence separately.

### Accepted dashboard inbox and native permission waits

All three research prerequisites closed on 2026-10-14. The human subsequently adopted the shared dashboard inbox and live-native-wait distinction informed by the [combined findings and interaction design](../research/native-permissions/findings.md). Candidate native routes are Codex app-server, Copilot SDK controlling the local CLI, Gemini ACP, and a version-matched OpenCode server/SDK. These are researched integration candidates, not permanently selected version pins or verified adapters. Pi RPC can carry extension UI, but native tool approval enforcement is unavailable without an explicitly configured and tested extension. Required capability/profile mismatches block dispatch under the already accepted fallback policy.

The foreground runner owns each native process, drains live output, saves request provenance before display, and forwards human responses only to the matching live request. The dashboard keeps the accepted factory SSE and HTTP interfaces; native protocol differences stay behind adapters. Preserve actual permission scopes and managed/deny/sandbox obligations, rather than flattening every native decision into a Boolean. Copilot SDK policy equivalence and OpenCode remembered-grant scope need particular attention. No permanent factory daemon or mandatory factory sandbox is proposed.

The accepted policy distinguishes durable factory checkpoints from live native tool-permission waits. Keep the foreground invocation alive for a native callback; save-and-exit remains appropriate for factory checkpoints with no active work. Closing the dashboard does not end that invocation. Pause/Cancel still interrupt work under the accepted grace-period policy. A process crash invalidates old controls until ownership and live requests are reconciled. A replacement process cannot consume a historical approval merely because the UI saved it. Saved responses while stopped apply to durable factory checkpoints, not a promise to revive dead native callbacks. Human Continue remains required after interruption.

Evidence supports interface feasibility, not completed integration. Codex local help/schema probes succeeded; Copilot help/version probes failed at protected cache extraction; Gemini, OpenCode and Pi were absent. No authenticated permission, cancellation, crash-recovery or cross-platform E2E test ran. The studies specify those acceptance gaps. Current and pinned documentation disagreements are retained rather than hidden.

### Accepted inbox grant scopes

On 2026-10-14, the human selected one-action approval by default, with broader native session/location/persistent grants exposed only when the execution profile explicitly permits those scopes. Display the actual scope and affected resources before submission; never map a narrow-looking choice to a broader native grant. Exposing every native option without profile opt-in was not selected. Existing configured native permissions remain visible in the effective profile and are not silently removed. This decision governs new grants through the inbox, not the already selected instruction/configuration precedence or a mandatory sandbox. A profile cannot manufacture a native one-action option where none exists: an unsupported required scope blocks or follows an already explicit compatible fallback.

### Derived engineering obligations

These follow from accepted policy and research; they are engineering obligations, not additional user preferences:

- Scope local human controls to the repository/run and current request. Unrelated browser origins and model/tool output cannot manufacture human approval. Protect control credentials and history access. This does not claim isolation from hostile code with the same OS-user authority in the accepted trusted-repository model. Detailed transport and fencing belong to recovery/security implementation.
- Record control identity, expected state/version, responses, withdrawals and consumed allowance without rewriting history. Revalidate ownership/state before dispatch. Deliberate withdrawal is separate from a conflicting duplicate response. Limit increases authorize only the stated scope and total, not publication or waived checks.
- Record native request resolution separately from tool completion; drain output during human waits. Keep permissions, ordinary questions, project trust, OS setup and factory checkpoints distinguishable. Historical events do not prove a callback remains live.
- Give each managed publication operation a stable local intent identity bound to authorized destination/action and candidate. Track push and PR creation as separate effects with observed remote identities. Reconcile uncertain delivery before another write. If evidence cannot establish whether an action occurred or a found artifact belongs to this intent, block for explicit resolution rather than creating another PR. No exactly-once provider guarantee is assumed; provider lookup/retry mechanisms remain recovery work requiring evidence.
- Refresh and required gates remain budgeted. Old approval cannot authorize a refreshed candidate. Record the observed base revision; observation does not lock the remote branch or promise it cannot advance afterward. Detectable remote divergence follows the accepted block-for-human policy.

### Historical resolution

Closed on 2026-10-14 after the human accepted all four conversation rounds, the researched dashboard/native-wait design, and the final inbox grant-scope choice. All five exact prerequisite tickets are closed. The accepted-answer sections above own the policy details; the derived obligations define the engineering consequences without claiming implementation proof.

### Interaction contract

| Concern | Owning decision and consequence |
| --- | --- |
| Workflow checkpoints | [Round one](#confirmed-answers-round-one) and [round two](#confirmed-answers-round-two): configurable placement, no default expiry, saved responses, bounded feedback repairs, revision/evidence/policy/action binding, and explicit limit increases. Human pre-PR review remains optional. |
| Lifecycle controls | [Pause and Cancel](#accepted-pause-and-cancel-controls) and [round three](#confirmed-answers-round-three): Pause preserves Continue, Cancel is terminal after reconciliation, withdrawal precedes dispatch, owned work has configurable thirty-second interruption grace, and active/uncertain work prevents uninstall. |
| Native permissions | [Dashboard and native waits](#accepted-dashboard-inbox-and-native-permission-waits) and [grant scopes](#accepted-inbox-grant-scopes): native protocol adapters, live foreground ownership, honest capabilities, one-action default with explicitly permitted broader scopes. Factory checkpoints remain distinct from native callbacks. |
| Publication | [Round two](#confirmed-answers-round-two), [round three](#confirmed-answers-round-three), and [round four](#confirmed-answers-round-four): launch scope authorizes selected GitHub publication, draft PR default, separate push/PR effects, retained partial publication, blocked unexpected changes, refreshed base/gates/approval, completion after confirmed publication unless workflow adds remote CI. Merge/deploy require distinct authority. |
| Durable controls and effects | [Engineering obligations](#derived-engineering-obligations): record and validate request identity, ownership, outcomes and stable publication intent. Uncertain effects require reconciliation rather than blind repetition. |

### Acceptance scenarios

These are required future tests and specification cases, not tests executed by this planning session.

1. Approve candidate R42, then refresh to R43 or change bound evidence/policy/action. R42 approval cannot authorize R43; an old browser tab cannot overwrite the current request. Unrelated progress alone leaves the request valid.
2. Deliver an identical response twice, or race conflicting responses and withdrawal against dispatch. Preserve a single effective response and auditable outcomes; withdrawal that loses to dispatch reports the race and does not promise rollback.
3. Save a factory checkpoint, exit the runner, answer in the independent dashboard, then Continue through the foreground command. Saving the answer or opening the dashboard never starts workflow work.
4. Hold one native permission request while another session streams. The owner stays alive, saves events before display, and routes responses only to matching live native identities. Dashboard closure does not implicitly cancel either session.
5. Crash the owner or native process while approval is pending or after response delivery but before observed completion. Continue reconciles processes and effects; old request IDs do not transfer to a replacement process. Historic approval never proves current callback liveness or tool completion.
6. Test one-action-only profiles and profiles enabling broader native scopes. Unsupported scopes remain unavailable; labels match actual reach. Existing deny/managed/sandbox obligations survive the chosen adapter. Pi generic dialogs alone cannot satisfy required native tool permission enforcement.
7. Pause or Cancel a cooperative and an unresponsive child. Stop dispatch immediately, request interruption, apply configured grace and terminate only positively identified owned processes where supported. Unknown ownership/effects remain unresolved, not falsely stopped. Pause resumes under original counters; Cancel cannot Continue. Uninstall refuses active or uncertain work.
8. Request changes or increase an exhausted allowance. Feedback enters the configured bounded repair, reruns required gates and creates a fresh checkpoint. A limit increase preserves consumed counters and does not approve publication or waive evidence.
9. Crash after push or PR creation but before local result persistence. Recover the same intended effect from sufficient evidence or remain blocked; do not create a second PR merely because local completion is missing. A pushed branch remains after failed/uncertain PR creation. Remote branch/PR divergence blocks automatic overwrite or replacement.
10. Observe base-branch advancement before publication. Refresh within existing budgets, rerun affected gates and renew configured approval. Record the base observation without claiming a remote lock. A configured publication succeeds only after its result is confirmed; remote CI, merge and deployment remain separate unless explicitly included and authorized.

### Downstream ownership and evidence limits

- [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) owns version identities, allowed live plan/profile/workflow edits, compatible resume and their invalidation rules. Explicit scope/limit actions here do not authorize arbitrary workflow mutation.
- [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns SQLite transactions, process generations/fencing, response-dispatch ambiguity, native pending-request reconciliation, external publication lookup/retry mechanisms and ownership. Provider-specific mechanisms require primary-source research; the current contract promises no provider-level exactly-once primitive.
- [Swimlane interaction design](swimlane-interaction-design.md) owns layouts and controls for the settled states, separate factory/native waits, grant scope, pausing/cancelling uncertainty, stale controls, partial publication and command-based Continue.
- [Specification readiness and acceptance](specification-readiness-and-acceptance.md) carries these scenarios and the per-harness conformance cases into the final acceptance inventory. Native platform support remains a target until its tests pass.

No factory runtime, control endpoint, authenticated permission round trip, native shutdown behavior, publication integration or crash-recovery guarantee was implemented or verified. Source/help/schema research establishes candidate interfaces only. This ticket closes human interaction policy, not the downstream mechanism or validation work.

