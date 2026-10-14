# Session events and live progress

**Type:** grilling
**Status:** closed
**Blocked By:** workflow-authoring-and-task-contract.md, agent-execution-profiles.md
**Research Dir:** not applicable

## Question

What event and artifact contract makes every custom step and agent session visible in real time and inspectable later?

Define run/task/step/attempt/session identities, parentage, lifecycle events, sequence and cursor behavior, partial output, tool events, artifacts, observed skill use, and usage provenance. Include deterministic commands and work that emits no detailed harness telemetry.

Decide the user-visible latency target and streaming approach, persistence before display, reconnect behavior, ordering, deduplication, backpressure, retention, sensitive-data handling, and minimum instrumentation for custom steps.

Resolution should define representative events, live/history consistency guarantees, honest unsupported-data states, and acceptance criteria. Do not equate a stored final result with real-time session progress.

---

## Decision record

Claimed on 2026-10-13 by `subagent-wmb34t` as the first eligible ticket in filename order. Both exact prerequisites, `workflow-authoring-and-task-contract.md` and `agent-execution-profiles.md`, were verified closed. The user explicitly resumed planning after the preceding stop request.

### Prior answers applied

- Every custom workflow must expose its steps and sessions in a real-time swimlane UI. The six-stage recipe is not a fixed workflow, and unknown future work must remain visibly unknown.
- [Workflow authoring and task contract](workflow-authoring-and-task-contract.md) owns run/task/step/session vocabulary, named scopes, parentage, managed effects, and declared outlines expanded with discovered work. Pure helpers need no separate visible step; managed external effects and agent sessions do.
- [Agent execution profiles](agent-execution-profiles.md) requires live output, lifecycle status, final output/artifact references, and a stop path. Rich tool events, exact usage/cost, and positive skill-loading evidence may be unavailable and must be labeled unknown or unsupported. Do not ask the user to choose that minimum again.
- Requested instructions, delivery mode, observed loading, and actual compliance are distinct. Effective harness/model/reasoning/prompt/skills and configured fallbacks must be visible. Review verdicts, generated task graphs, and other agent outputs controlling execution require validated schemas; readable reports may use text and artifacts.
- [Operating and installation model](operating-and-installation-model.md#resolution) owns local offline inspection/control, keeping history/transcripts/artifacts until explicit cleanup, protecting unfinished-run data, and keeping credentials out of configuration and logs. These policies are settled.
- The factory-owned SQLite executor and one foreground runner per invocation are selected. Opening the UI does not resume work. Human Continue and checkpoint approval remain distinct. An on-demand UI observer does not change this operating contract.

### Confirmed answers, round one

On 2026-10-13, the human explicitly accepted all three recommendations:

1. **Saved events as the live-view source:** persist an event or bounded output chunk before displaying it as recorded progress. Live and historical views read the same committed record. After reconnect, catch up from the last saved cursor and suppress duplicate delivery. Do not display an unsaved transcript tail as if it were recoverable history. The tradeoff is a small persistence/batching delay; previewing unsaved output could reduce delay but that output could vanish after a crash. This cannot promise capture of output the harness never delivered or the recorder never saved. Connection health is observation metadata, not proof of new workflow progress.
2. **Latency target:** target at least 95% of small state/output updates becoming visible within one second after the factory receives them, with a connected local UI and under a documented representative load. Allow short output batches instead of rendering each token separately. Exclude model thinking time, harness-side buffering, and time while disconnected; display disconnect or catch-up status honestly. This is an acceptance target to validate, not measured performance. The exact benchmark load remains to be specified; round three below selects the transport.
3. **Slow viewers versus recording failure:** a slow or disconnected UI must not slow agent execution; keep recording, bound delivery buffers, and let the viewer catch up from saved history. If recording itself cannot keep up within bounded capacity or becomes unavailable, stop dispatching new work, request graceful interruption of active work, and surface the recording fault. Preserve recoverable state and require explicit Continue after repair/reconciliation; do not silently run unrecorded or discard transcript data. A failed storage write may also prevent saving the fault itself, so the control/terminal path must report it and later inspection must expose uncertainty rather than invent a complete history. This does not change the accepted retention policy or guarantee that every in-flight external effect stopped.

These answers are settled. Do not repeat persistence-before-display, the one-second latency target, or interruption-on-recording-failure questions.

### Confirmed answers, round two

On 2026-10-13, the human accepted an **independent on-demand dashboard**: one local UI process observes the repository's runs and can remain available after a workflow runner exits. It can be closed independently. Workflow runners remain foreground processes, and opening or reconnecting the dashboard never resumes work. This selects the observer lifecycle, not a permanent workflow supervisor. How a UI Continue action starts or attaches to a foreground invocation remains part of the human-control/recovery contract.

After the concrete show-me explanation, the human explicitly accepted **retaining registered evidence** on 2026-10-13. Preserve immutable copies of generated reports, screenshots, diffs, and other evidence explicitly registered with the factory; keep external links labeled as references unless captured. Later edits to a source path must not silently change the evidence shown for an old run. This adds storage compared with paths alone, under the already accepted explicit-cleanup policy. Capture applies to registered evidence, not automatic copies of the entire repository or every incidental temporary file.

Concrete example for that explanation: a UI verification attempt registers `artifacts/checkout.png`, showing a broken checkout form. A repair attempt writes a corrected screenshot to the same path. A path-only history entry now opens the corrected screenshot even when inspecting the earlier failed attempt. With retained evidence, the first attempt points to the original bytes and the second attempt to the corrected bytes; each preserves its attempt identity, original path, and capture time. A content digest can identify or deduplicate captured bytes, but a digest alone cannot recover an image whose bytes were never retained. This is an illustrative contract, not implemented storage behavior.

Both answers are settled. Do not repeat dashboard-lifetime or retained-evidence questions.

### Confirmed answers, round three

On 2026-10-13, the human explicitly accepted both remaining recommendations:

1. **Browser transport:** use one Server-Sent Events (SSE) feed per dashboard document, multiplexing that repository's observed runs and sessions. Send human controls through separate ordinary HTTP requests. The completed [transport findings](../research/live-progress-transport-fit/findings.md) support this fit. The factory still owns saved replay, applied cursors, and deduplication; a browser reconnect does not prove application consumption. EventSource is the initial browser interface described by the research. Fetch streaming and WebSocket were considered alternatives, not selected defaults. This is a design choice, not a performance or compatibility claim.
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
- Under the documented representative load, at least 95% of small updates appear within one second from factory receipt, including batching and persistence. Test each supported browser/OS combination and separate reconnect/catch-up measurements. The representative load must include the supported concurrency chosen in scheduling; selecting that workload does not weaken the accepted target.
- Slow or closed viewers do not stop recording. Recording failure follows the accepted interruption policy and leaves uncertain process/effect outcomes for reconciliation and human Continue.
- Overwriting or deleting the original screenshot/report leaves the registered historical evidence unchanged. Incomplete capture is never announced as an available artifact. Missing or corrupt retained evidence is visible, and cleanup protects unfinished-run recovery data.
- Opening/reconnecting the independent dashboard never dispatches workflow work. Closing the dashboard does not stop an independently running foreground invocation; closing that invocation follows the established interruption/recovery contract.
- Sensitive payload handling is exercised across chunk boundaries and artifact registration. Redacted or excluded content remains visibly identified as such. No test result should claim that arbitrary unknown secrets can always be discovered.

## Resolution

Closed on 2026-10-13 after the human accepted all three answer rounds, including the separately explained retained-evidence choice. Both exact prerequisites, `workflow-authoring-and-task-contract.md` and `agent-execution-profiles.md`, were verified closed. The confirmed-answer sections above own the live/history, latency, recording-failure, dashboard, retained-evidence, transport, and custom-progress policies. The event/artifact obligations and acceptance cases carry those policies into the implementation-ready specification without claiming implementation proof.

Remaining mechanisms have existing owners:

- [Task scheduling and integration](task-scheduling-and-integration.md) supplies supported concurrency and resource limits for representative live-progress load tests.
- [Verification and review policy](verification-and-review-policy.md) determines what registered evidence proves and when new work invalidates its applicability. Retaining old evidence does not make it current evidence for a later revision.
- [Human control and publication](human-control-and-publication.md) owns control authorization, stale decisions, native harness approvals, and starting or attaching a UI-requested Continue to a foreground invocation.
- [Recovery guarantees and runtime selection](recovery-and-runtime-selection.md) owns atomic workflow-state/event updates, stable ownership, artifact publication/reconciliation, and failure recovery. A durable browser stream is not an exactly-once external-effect guarantee.
- [Workflow versioning and run changes](workflow-versioning-and-run-changes.md) owns compatible event/result/artifact schemas and retained definitions across upgrades. Exact field spelling may change while preserving this contract.
- [Swimlane interaction design](swimlane-interaction-design.md) owns the presentation of the agreed states, output, evidence, and custom events; [Specification readiness and acceptance](specification-readiness-and-acceptance.md) consolidates platform/browser and performance proof.

No new decision ticket is needed. [Live progress transport fit](live-progress-transport-fit.md) is completed source research supporting the selected SSE direction. No runtime, browser delivery, artifact capture, latency, recovery, or native-platform behavior was implemented or tested. No next design ticket was claimed in this session.

