# Session events and live progress

> Current history scope, 2026-10-15: save traces, prompts, and outputs. Immutable registered-evidence capture is removed. Live UI transport/reliability requirements remain accepted while the human compares them with SSSF; asking for that comparison does not change them.

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md, agent-execution-profiles.md
**Research Dir:** not applicable

## Question

How do saved traces, prompts, and outputs support a live and historical view of factory phases and supported subagent sessions?

## Resolution

Apply [accepted uninstall maintenance admission](recovery-and-runtime-selection.md#accepted-uninstall-through-the-maintenance-gate): the dashboard host must stop before uninstall and cannot start during removal. Closing a browser tab is insufficient. History is preserved; factory inspection after successful uninstall requires a compatible installation.

On 2026-10-15 the human simplified historical capture to saved traces, prompts, and outputs. Remove the separate immutable evidence registry, automatic screenshot/report/diff copying, content-addressed evidence storage obligations, and permanent integrity guarantee for arbitrary linked files. Keep useful history without a general artifact archival system.

### Saved history

- Save delivered trace events/output chunks, rendered prompts/effective configuration, structured results or textual outputs, check results, attempt outcomes, and available usage under identifiable runs/invocations/phases. Keep failed and corrected attempt outputs distinguishable through their attempt associations, not an immutable artifact service. Under [step-start input resolution](workflow-versioning-and-run-changes.md#step-start-input-resolution), record each step's actual supplied configuration/prompt/skill inputs rather than assuming every phase used one invocation-wide revision.
- Apply [accepted history preservation for learning](recovery-and-runtime-selection.md#accepted-history-preservation-for-learning): retain full captured history by default, independently of worktree deletion or learning extraction. Keep traceable extraction/source references; cleanup is exceptional, informed, explicit, and repository-idle-only. Never imply capture of content the harness did not deliver or recording did not save.
- Reports, screenshots, and other files may be ordinary workflow outputs or path/URL references. There is no automatic registration/copying guarantee. A reference may change or disappear; show that limitation and missing-file states rather than claiming the original bytes remain available. Workflows may explicitly save their own files without creating a core archival subsystem.
- Do not call old outputs current verification of changed code. A later explicit answer refers to the actual saved question and current selected inputs, not an assumed immutable evidence repository.
- Keep credentials out of saved traces/prompts/outputs using known-secret/configured filtering before persistence. Mark omitted/redacted content honestly; do not promise detection of every secret. No separate binary artifact capture/filter pipeline is required by this simplified history contract.

Apply [accepted saved-history consistency](recovery-and-runtime-selection.md#accepted-saved-history-consistency): SQLite is authoritative for factory records and captured text/JSON, written in bounded chunks after configured filtering. Workflow-generated files remain ordinary references. Capture completeness is separate from execution outcome; retain saved chunks and mark unfinished capture partial/unknown without inventing missing content. Missing essential ownership/accounting storage blocks new invocations until explicit repair, while a missing external report alone does not block unrelated work.

### Live UI reliability unchanged pending discussion

On 2026-10-15 the human explicitly reaffirmed SSE after rejecting the proposed polling replacement. Keep one read-only SSE feed per dashboard document. The retained [transport findings](../research/live-progress-transport-fit/findings.md) support the one-way feed; EventSource handles protocol parsing/reconnection while the application still owns saved history and applied cursors. Polling would retain those correctness obligations while adding request scheduling and polling delay. No net complexity or measured performance benefit justified changing transport. The heading is retained for existing links; transport selection is settled, not pending. Do not add optional transport variants or shared-worker coordination without a demonstrated need. Native/browser qualification and the latency target remain unproved.

- Persist an event or bounded output chunk before displaying it as recorded progress. Live and historical views read committed history. Reconnect catches up from saved cursors and suppresses duplicate delivery.
- Use one read-only SSE feed per dashboard document for the repository's observed runs/sessions. Track events applied to the view, not only received transport IDs; rebuild or resynchronize when view state is lost. Rebuilding a UI never executes workflow code.
- Bootstrap from a consistent saved view and cursor, then catch up and stream without omitting committed events. Durable ordering identifies events; timestamps alone do not determine causal order across parallel sessions.
- A slow or disconnected dashboard must not stop execution. Bound delivery buffers and catch up from history. If recording itself fails or cannot keep up within bounded capacity, stop new dispatch, request graceful interruption, preserve saved data/partial files, and report uncertainty through the terminal if storage cannot record the fault.
- Keep the independent on-demand dashboard and its lifetime separate from the foreground runner. Opening the UI never starts work; closing it does not stop a runner. Under [accepted idle-upgrade coordination and failure handling](recovery-and-runtime-selection.md#accepted-idle-upgrade-coordination-and-failure-handling), the dashboard process must stop before installation/history modification and cannot restart during the upgrade. Closing its browser tab alone does not establish process shutdown; no live observer migration is required. The [accepted shared maintenance gate](recovery-and-runtime-selection.md#accepted-shared-repository-maintenance-gate) supplies the common admission rule for upgrades, explicit repair, and exceptional history cleanup; this does not change SSE or require a resident coordinator.
- Keep the acceptance target that at least 95% of small state/output updates appear within one second after factory receipt under documented connected-local load. Model/harness buffering and disconnected time are excluded. This is unmeasured, not a demonstrated advantage over SSSF.
- Keep optional namespaced custom progress events with a generic readable data view. Only the runner controls authoritative lifecycle transitions; a custom event cannot declare success.

These are stronger explicit delivery/failure contracts, not evidence that SSSF loses events or has an unreliable UI. The [SSSF lifecycle study](../research/sssf-lifecycle-comparison/findings.md) records narrower source findings and their limits.

### Learning extraction visibility

Apply [accepted explicit learning invocations](skill-and-prompt-improvement.md#accepted-explicit-learning-invocations): display extraction as an explicitly launched invocation using existing history/attempt records. Preserve the exact examined source references, candidate reports, and no-proposal findings. A later invocation under the same source run is not implicitly examined. Disclose partial/missing source content. Extracted proposals do not change active configuration and must not appear adopted or proven effective merely because extraction succeeded. Apply [accepted evaluation and human adoption](skill-and-prompt-improvement.md#accepted-evaluation-and-human-adoption): link baseline/candidate identities, cases/results/limitations, the explicit human decision, and actual adoption or revert revisions. Distinguish approved from applied and inconclusive from passing; this view remains observational.

### Attention outcomes and notifications

Apply the notification policy in [Human input and execution controls](human-control-and-publication.md#notifications). Save structured `needs_input`, its question/context/suggested answers, failure reasons, and invocation outcomes. “Needs input” is persistent attention status for an ended invocation, not a running wait or executable checkpoint. Show pending/uncertain cleanup honestly. The UI displays later input/invocation links without rewriting prior outcomes or accepting answers. Under the [accepted needs-input and invocation finalization contract](recovery-and-runtime-selection.md#accepted-needs-input-and-invocation-finalization), show a saved question even if finalization is incomplete, distinguish shutdown-induced interruption from independent failure, and show outcome and cleanup separately. A saved question or attempt result does not imply a finalized invocation outcome.

Desktop delivery and dismissal do not control workflow execution or history retention. Presentation must distinguish a saved outcome from notification delivery failure. Apply the accepted bounded-delivery fallback and opt-in dashboard-scoped reminders from the linked policy. Reminder preferences/acknowledgment affect notification metadata only; no workflow mutation controls are added. Apply [accepted notification defaults and reminder ownership](recovery-and-runtime-selection.md#accepted-notification-defaults-and-reminder-ownership): one dashboard host per repository owns grouped reminders, browser tabs do not independently notify, and SQLite preserves preferences/per-invocation acknowledgment. Initial notices belong to the runner. Under [accepted optional notification links](recovery-and-runtime-selection.md#accepted-optional-notification-links), native click-through is optional and saved details remain accessible through the CLI/dashboard. Do not require a sender to stay alive for clicks or automatically start the dashboard from old alerts. The [accepted shared ownership mechanism](recovery-and-runtime-selection.md#accepted-shared-ownership-mechanism) supplies common claim/check/release behavior, verified existing-host reuse, and explicit stale clearance. An unresponsive endpoint does not prove shutdown. Native delivery and concrete coordination checks remain qualification work; no separate background notifier is authorized.

### Workspace and subagent observation

Apply [Run workspace and implementer delegation](task-scheduling-and-integration.md#resolution). Record pre-phase workspace preparation/failure and starting-content provenance. All phases operate in one run worktree. Observe parent/child identities, timing, lifecycle, output, and usage only where the harness exposes them; internal children are not factory-scheduled tasks.

The accepted index, owner/session timeline, and beneath-timeline inspector remain. Nest supported children under the parent phase. Otherwise display the parent and limited child visibility. Never invent progress or completion from silence or parent exit. Required child visibility must be declared as a capability requirement. Child observability does not prove child shutdown control.

Unknown telemetry stays unknown. Avoid double-counting child usage included in parent totals. The live-load acceptance scenario includes supported child streams and parent-only fallback; factory-managed launch limits do not bound internal child count.

### Acceptance obligations

1. Show the same saved phase outcomes, prompts, and outputs in live and historical views, including failed and corrected attempts.
2. Exercise reload, reconnect, duplicate delivery, catch-up, and slow/disconnected viewers without skipping committed history or executing work.
3. Expose recording failure and uncertain incomplete activity honestly; opening/closing the observer must not launch/stop workflow work.
4. Show supported child sessions and a limited-visibility fallback; handle unavailable metrics and redact configured sensitive output.
5. Show referenced output files that change or disappear without claiming immutable historical bytes. Preserve saved traces/prompts/outputs through explicit workspace cleanup.
6. Measure the retained latency target under documented load before claiming compliance; no such measurement has been performed.

[Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns history schema and recording/process mechanisms. [Detailed observability UI design](detailed-observability-ui-design.md) owns labels and fixtures. No runtime, browser transport, recorder, or harness behavior has been implemented or tested.

## Historical observability decisions, superseded where noted

The record below preserves prior choices and rationale. Immutable registered evidence, binary capture guarantees, and artifact integrity/copying obligations are removed by the current resolution. Earlier task scheduling/visibility assumptions are superseded by implementer-owned delegation. Other retained live UI choices are restated above.

## Decision record

Claimed on 2026-10-13 by `subagent-wmb34t` as the first eligible ticket in filename order. Both exact prerequisites, `workflow-authoring-and-task-contract.md` and `agent-execution-profiles.md`, were verified closed. The user explicitly resumed planning after the preceding stop request.

### Prior answers applied

- Every custom workflow must expose its steps and sessions in a real-time swimlane UI. The six-stage recipe is not a fixed workflow, and unknown future work must remain visibly unknown.
- [Workflow authoring and task contract](workflow-authoring-and-task-contract.md) owns run/invocation/step/session vocabulary, named scopes, parentage, managed effects, and outlines expanded with observed work. Pure helpers need no separate visible step; factory-managed external effects and agent sessions do. Harness-internal children follow the conditional observation contract above.
- [Agent execution profiles](agent-execution-profiles.md) requires live output, lifecycle status, final output/artifact references, and a stop path. Rich tool events, exact usage/cost, and positive skill-loading evidence may be unavailable and must be labeled unknown or unsupported. Do not ask the user to choose that minimum again.
- Requested instructions, delivery mode, observed loading, and actual compliance are distinct. Effective harness/model/reasoning/prompt/skills and unsupported-setting failures must be visible. The [selected-profile-or-failure decision](agent-execution-profiles.md#selected-profile-or-failure) removes automatic fallback chains. Review verdicts, implementation outcome reports, and other agent outputs controlling factory execution require validated schemas; readable reports may use text and artifacts.
- [Operating and installation model](operating-and-installation-model.md#resolution) owns local offline inspection/control, keeping history/transcripts/artifacts until explicit cleanup, preserving partial work and historical evidence, and keeping credentials out of configuration and logs. These policies are settled.
- The foreground TypeScript runner and SQLite history are selected. Opening the UI never starts work. Explicit script invocation and human approval remain distinct. An on-demand UI observer does not change this operating contract.

### Confirmed answers, round one

On 2026-10-13, the human explicitly accepted all three recommendations:

1. **Saved events as the live-view source:** persist an event or bounded output chunk before displaying it as recorded progress. Live and historical views read the same committed record. After reconnect, catch up from the last saved cursor and suppress duplicate delivery. Do not display an unsaved transcript tail as if it were recoverable history. The tradeoff is a small persistence/batching delay; previewing unsaved output could reduce delay but that output could vanish after a crash. This cannot promise capture of output the harness never delivered or the recorder never saved. Connection health is observation metadata, not proof of new workflow progress.
2. **Latency target:** target at least 95% of small state/output updates becoming visible within one second after the factory receives them, with a connected local UI and under a documented representative load. Allow short output batches instead of rendering each token separately. Exclude model thinking time, harness-side buffering, and time while disconnected; display disconnect or catch-up status honestly. This is an acceptance target to validate, not measured performance. The exact benchmark load remains to be specified; round three below selects the transport.
3. **Slow viewers versus recording failure:** a slow or disconnected UI must not slow agent execution; keep recording, bound delivery buffers, and let the viewer catch up from saved history. If recording itself cannot keep up within bounded capacity or becomes unavailable, stop dispatching new work, request graceful interruption of active work, and surface the recording fault. Preserve recorded history and partial work, then require an explicit script invocation after repair and relevant ownership/effect checks; do not silently run unrecorded or discard transcript data. A failed storage write may also prevent saving the fault itself, so the control/terminal path must report it and later inspection must expose uncertainty rather than invent a complete history. This does not change the accepted retention policy or guarantee that every in-flight external effect stopped.

These answers are settled. Do not repeat persistence-before-display, the one-second latency target, or interruption-on-recording-failure questions.

### Confirmed answers, round two

On 2026-10-13, the human accepted an **independent on-demand dashboard**: one local UI process observes the repository's runs and can remain available after a workflow runner exits. It can be closed independently. Workflow runners remain foreground processes, and opening or reconnecting the dashboard never resumes work. This selects the observer lifecycle, not a permanent workflow supervisor. Execution input belongs to CLI/config; invocation selection remains part of the lifecycle contract.

After the concrete show-me explanation, the human explicitly accepted **retaining registered evidence** on 2026-10-13. Preserve immutable copies of generated reports, screenshots, diffs, and other evidence explicitly registered with the factory; keep external links labeled as references unless captured. Later edits to a source path must not silently change the evidence shown for an old run. This adds storage compared with paths alone, under the already accepted explicit-cleanup policy. Capture applies to registered evidence, not automatic copies of the entire repository or every incidental temporary file.

Concrete example for that explanation: a UI verification attempt registers `artifacts/checkout.png`, showing a broken checkout form. A repair attempt writes a corrected screenshot to the same path. A path-only history entry now opens the corrected screenshot even when inspecting the earlier failed attempt. With retained evidence, the first attempt points to the original bytes and the second attempt to the corrected bytes; each preserves its attempt identity, original path, and capture time. A content digest can identify or deduplicate captured bytes, but a digest alone cannot recover an image whose bytes were never retained. This is an illustrative contract, not implemented storage behavior.

Both answers are settled. Do not repeat dashboard-lifetime or retained-evidence questions.

### Confirmed answers, round three

On 2026-10-13, the human explicitly accepted both remaining recommendations:

1. **Browser transport:** use one Server-Sent Events (SSE) feed per dashboard document, multiplexing that repository's observed runs and sessions. The later observability-only amendment removes browser control requests; execution input belongs to CLI/config. The completed [transport findings](../research/live-progress-transport-fit/findings.md) support this fit. The factory still owns saved-event replay for observation, applied cursors, and deduplication; a browser reconnect does not prove application consumption. EventSource is the initial browser interface described by the research. Fetch streaming and WebSocket were considered alternatives, not selected defaults. This is a design choice, not a performance or compatibility claim.
2. **Custom progress events:** allow a workflow to emit optional namespaced events within managed steps, with a readable message and schema-versioned structured data. For example, a custom test routine could emit `tests.batch_completed` with a completed count. Core run/step/session lifecycle transitions remain executor-owned and cannot be forged by a custom progress payload. Unknown custom event types remain inspectable through a generic message/data view; they do not require a custom UI renderer to be usable. Generic progress is optional, while managed lifecycle instrumentation remains mandatory. Restricting workflows to only standard events and ordinary session output was not selected.

These answers are settled. Do not repeat transport or custom-progress-event questions.

### Event and artifact obligations

The following engineering obligations make the confirmed policies concrete. They are derived design details, not additional answers attributed to the human. Exact serialized field names, storage layout, and transaction/compatibility mechanisms remain with the downstream specification work identified in the resolution.

- A versioned event envelope identifies its run, parent scope, applicable task/step/attempt/session, event identity, kind, source, and recorded time. Optional harness event IDs and reported timestamps retain provenance rather than replacing factory identities.
- A durable per-run sequence orders committed events; timestamps alone do not establish causal order across parallel sessions or runs. A browser feed cursor is scoped to its subscribed stream, with durable catch-up and event-identity deduplication. Do not assume separate runs share a causal order or that a browser transport itself persists history.
- Maintain a watermark for events actually applied to the UI, separately from EventSource's received-event cursor. Bootstrap a new view from a consistent saved snapshot and its watermark, then catch up and stream subsequent records without a gap. If UI state is lost or applying an event fails, replay or rebuild from a compatible saved snapshot; do not reuse a cursor that skips missing state. Subscription changes and unavailable history require an explicit resynchronization path. Rebuilding a view never re-executes workflow steps.
- Representative event kinds cover scope discovery, attempt start/wait/interruption/completion/failure, session attachment, output chunks, supported tool activity, result validation, registered artifacts, capability availability, and usage observations. Event payloads identify references and offsets for large content instead of duplicating whole transcripts in every update. Exact names are illustrative.
- Registering retained evidence must finish capture and integrity checks before an artifact-available event becomes visible. The artifact record links immutable content to its producing attempt, media type, size, original path or source, and capture time. A later replacement creates another artifact record rather than mutating the earlier evidence. A missing or corrupt retained artifact is an explicit error, never silently substituted with whatever occupies the original path now. Capture must use a stable source or producer handoff so concurrent writes cannot turn the stored evidence into an unrecognized mixture. Exact on-disk publication and crash reconciliation belong to recovery design.
- Managed operations supply lifecycle instrumentation for both agent sessions and deterministic commands. Quiet work shows elapsed time, last observed output, and separately qualified process/connection health. Silence is not proof of failure; a heartbeat is not proof of task progress or success. No invented tool activity, percentage, or model-reasoning trace fills a telemetry gap.
- Requested skill delivery, evidence of loading, and compliance remain separate facts. Usage values carry their source and distinguish reported values, estimates, and unavailable information; unavailable is never represented as zero. These apply the accepted execution-profile contract.
- Apply the accepted no-credentials-in-logs rule before persistence and display, using known credential values and configured sensitive fields, sources, or patterns. Filtering/exclusion must handle output chunk boundaries and registered artifacts; excluded or redacted content is visibly marked without retaining a hidden unfiltered copy in factory logs. Do not automatically snapshot credential stores or dump the process environment. Artifact registration must reject or withhold content that cannot satisfy the configured capture policy, rather than silently presenting altered or unavailable evidence as complete. State the limits of detection instead of promising discovery of every arbitrary secret. Exact filtering implementation remains to be designed and tested.

### Acceptance cases

- Live and historical inspection reconstruct the same committed step/session outcomes and output. Reload, connection loss, duplicate delivery, and events arriving during catch-up neither lose committed records nor apply a record twice to the UI projection. Cursor handling must cover a received event that was not yet successfully applied by the UI.
- Parallel sessions retain distinct run/step/attempt/session identities and output ordering; an ordinary command and a quiet custom step remain visible without fabricated progress or unavailable usage metrics.
- A namespaced custom event with an unfamiliar type appears through the generic message/data view and survives history replay. Attempts to impersonate reserved lifecycle events or use invalid event envelopes are rejected. A custom progress message cannot turn an unsuccessful attempt into a successful one.
- Under the documented representative load, at least 95% of small updates appear within one second from factory receipt, including batching and persistence. Test each supported browser/OS combination and separate reconnect/catch-up measurements. The representative load must include factory-managed concurrency and supported internal child streams; selecting that workload does not weaken the accepted target.
- Slow or closed viewers do not stop recording. Recording failure follows the accepted interruption policy and leaves uncertain process/effect outcomes for human resolution or relevant checks before another explicit invocation.
- Overwriting or deleting the original screenshot/report leaves the registered historical evidence unchanged. Incomplete capture is never announced as an available artifact. Missing or corrupt retained evidence is visible, and cleanup must not silently discard retained evidence or partial work.
- Opening/reconnecting the independent dashboard never dispatches workflow work. Closing the dashboard does not stop an independently running foreground invocation; closing that invocation follows the established interruption/recovery contract.
- Sensitive payload handling is exercised across chunk boundaries and artifact registration. Redacted or excluded content remains visibly identified as such. No test result should claim that arbitrary unknown secrets can always be discovered.

## Historical resolution

The delegation amendment above supersedes mandatory task-level instrumentation and universal child registration. Retain managed phase instrumentation and observe internal children where supported.

Closed on 2026-10-13 after the human accepted all three answer rounds, including the separately explained retained-evidence choice. Both exact prerequisites, `workflow-authoring-and-task-contract.md` and `agent-execution-profiles.md`, were verified closed. The confirmed-answer sections above own the live/history, latency, recording-failure, dashboard, retained-evidence, transport, and custom-progress policies. The event/artifact obligations and acceptance cases carry those policies into the implementation-ready specification without claiming implementation proof.

Remaining mechanisms have existing owners:

- [Run workspace and implementer delegation](task-scheduling-and-integration.md) owns the shared run worktree, managed launch limits, and conditional child visibility. Load tests must cover reported subagent streams without assuming factory limits cap internal delegation.
- [Verification and review policy](verification-and-review-policy.md) determines what registered evidence proves and when new work invalidates its applicability. Retaining old evidence does not make it current evidence for a later revision.
- [Human input and execution controls](human-control-and-publication.md) owns control authorization, stale decisions, native harness approvals, and CLI input to live requests and explicit subsequent invocation.
- [Invocation lifecycle and interrupted work](recovery-and-runtime-selection.md) owns history-write integrity, process ownership, artifact publication/incomplete capture, and interrupted-work handling. A durable browser stream is not an exactly-once external-effect guarantee.
- [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) removes executable-state migration; readable event/result/artifact history across upgrades remains an obligation for the lifecycle ticket. Exact field spelling may change while preserving this contract.
- [Swimlane interaction design](swimlane-interaction-design.md) owns the presentation of the agreed states, output, evidence, and custom events; [Specification readiness and acceptance](specification-readiness-and-acceptance.md) consolidates platform/browser and performance proof.

No new decision ticket is needed. [Live progress transport fit](live-progress-transport-fit.md) is completed source research supporting the selected SSE direction. No runtime, browser delivery, artifact capture, latency, recovery, or native-platform behavior was implemented or tested. No next design ticket was claimed in this session.

