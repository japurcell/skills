# Foreground invocation lifecycle specification

Status: lifecycle design complete under accepted policies; Windows inbox API choice accepted on 2026-10-16. No runtime implementation or native qualification is claimed.

## Authority and scope

The [Invocation lifecycle and interrupted work decision](tickets/recovery-and-runtime-selection.md) owns the human-approved policies. This document supplies their concrete mechanisms under the user's instruction to resolve routine details. It does not replace those policies, add durable workflow execution, or authorize implementation. Numeric recorder defaults below are initial engineering settings to qualify, not measured capacity guarantees.

One foreground invocation runs one selected current TypeScript workflow from entry in an exclusively owned worktree. The implementer owns its subagents. SQLite retains observation, inputs, results, allowances, and ownership facts. A later invocation does not restore a call stack, queue, native conversation, or executable environment. Workflow code controls phase order and bounded corrections.

## Small module interfaces

| Module | Interface and responsibility |
| --- | --- |
| Lifecycle | Start an invocation, admit managed work, request shutdown, finalize. Own ordering and one shutdown path; never expose checkpoint/replay methods. |
| Repository store | Transactionally claim/release ownership, admit/settle attempts, append captured data, read bounded history, and perform exclusive maintenance. The same module owns durable facts and observation-event cursors. |
| Harness adapter | Validate a selected profile, start a non-interactive call, stream supported output, request stop, and report launch/exit/child-control facts. Adapters do not choose fallback profiles or relaunch failed calls. |
| Native host adapter | Inspect an owner, stop only an identified owned execution scope where supported, and submit one desktop notice. Return supported, unsupported, inaccessible, or uncertain results explicitly. |
| Maintenance controller | Apply an explicit install/update/repair/uninstall/selected-cleanup operation under the shared gate, validate completion, and release the matching owner. |

These are local modules, not independent services, plugins, or public extension frameworks. Native and harness adapters exist because those mechanisms actually vary. Use the same storage/ownership operations from the runner, dashboard, and maintenance controller.

## Repository layout and installation identity

Resolve Git's common directory to identify the repository shared by its linked worktrees. Store the factory's managed installation, database, backups, and maintenance records under a dedicated `factory/` child of that common directory. This keeps them outside disposable worktree contents and version control. Store editable workflows, prompts, settings, and factory dependency declarations in the repository's `.factory/` authoring directory. Each invocation resolves its selected authoring inputs from the chosen worktree unless an explicit configured external input says otherwise; new worktrees still start from committed content only. Existing application dependency files are not modified.

Assign the installation a repository ID in its database. A registered worktree has its own ID, canonical path, and Git registration reference. Validate both Git registration and repository identity before reuse. A moved/mismatched registration requires an explicit diagnostic and correction; do not silently adopt another checkout by path similarity. Renaming a path does not create fresh allowances or clear ownership. Symlinks and case differences must resolve to one registration rather than permit duplicate claims.

Use one managed Node LTS installation and one shared factory dependency environment. The installed manifest records runtime/build-tool versions, dependency-lock identity, factory release, and schema version. At invocation start, validate the selected authoring dependency declaration against that installed set. A mismatch or missing package fails startup with an explicit install/update instruction. Startup never downloads, installs, or rewrites locks. Build tooling uses the shared environment through factory-owned resolution scaffolding; it must refuse a conflicting user-owned path rather than replace it. No global compiler or application dependency edit is required.

The one invocation build emits disposable output associated with that invocation. Do not use it as a version archive, cross-invocation cache, or recovery input. Preserve build diagnostics in startup history where recording works. Build and workspace preparation both precede every phase; neither failure creates an agent attempt. The compiler configuration and normal module-resolution rules must be covered by authoring conformance tests, including relative imports and shared installed dependencies.

## Records and state

Use opaque fresh IDs for runs, invocations, attempts, claims, maintenance operations, and questions. A UUID implementation is a routine choice; IDs carry no workflow position or ordering semantics. Use a database-assigned monotonically increasing integer for the repository observation cursor. Wall-clock timestamps are display evidence, not lock expiry or event ordering.

The logical tables are `runs`, `invocations`, `attempts`, `operations`, `allowance_ledger`, `worktrees`, `owner_claims`, `clearances`, `captures`, `capture_chunks`, `questions`, `maintenance_operations`, `notification_preferences`, `notification_deliveries`, `notification_acknowledgments`, and `observation_events`. These names describe one store, not separate subsystems. Use foreign keys and uniqueness constraints for ownership keys, operation identities, and `(capture_id, sequence)`; index history by run/invocation/attempt and cursor. Do not index entire transcript text or add full-text/vector search merely for lifecycle completeness.

Store the minimum facts from the decision's [derived record contract](tickets/recovery-and-runtime-selection.md#derived-lifecycle-records-and-sequencing), with these concrete distinctions:

| Fact | Values and meaning |
| --- | --- |
| Invocation stage | `starting`, `running`, `shutting_down`, `finalized`. Missing finalization after owner loss is incomplete; a stored running stage does not prove liveness. |
| Final execution outcome | `succeeded`, `failed`, `needs_input`, `interrupted`, `cancelled`. Preserve all questions and independent failure reasons alongside the summary. |
| Launch evidence | `admitted`, `started`, `not_started`, `unknown`. Admission is not proof of launch; uncertainty retains its debit. |
| Attempt completion | Reported result, native exit/signal where available, and interruption origin. Shutdown-requested interruption is distinct from an independently failed call. |
| Cleanup | `complete`, `required`, `unknown`, with automatic or operator-confirmed clearance provenance. Outcome does not grant clearance. |
| Capture | `open`, `complete`, `partial`, `unknown`, plus explicit `pruned` detail markers. Unsupported telemetry is a capability fact, not an empty successful capture. |
| Installation | `ready`, `absent`, or `incomplete`, with intended version and operation reference where applicable. |
| Maintenance stage | `preparing`, `modifying`, `validating`, `complete`, or `incomplete`. An absent/live owner and operation completion are separate facts. |

Preserve terminal outcomes. Later clearance, acknowledgments, allowance increases, and explicit corrections to administrative facts are separate recorded events, not edits that relabel earlier execution as successful. A run need not have a single mutable workflow status: summarize its invocations without inventing a resumable run state.

## Ownership and admission transactions

An owner claim contains repository/resource identity, a fresh claim token, owning invocation/maintenance ID when relevant, host identity, and available native process-start identity. PID alone is insufficient. Persist known owned launch scopes and cleanup limitations. Claims have no expiry or heartbeat. Claim tokens prevent delayed release of a replacement owner; they do not remotely stop a process that is already running.

All participants use the same short transaction for installation/maintenance checks and claim insertion. Resource-specific conflicts are:

| Requested owner | Admission requirement |
| --- | --- |
| Worktree invocation | Ready compatible installation, no incomplete/exclusive maintenance, and no current claim for that worktree. Other worktrees and a dashboard may coexist. |
| Dashboard | Ready compatible installation, no incomplete/exclusive maintenance, and no other dashboard claim. If a host exists, verify its repository/claim identity and report its endpoint; do not trust an open port alone. |
| Maintenance | No active or uncertain worktree invocation, dashboard, or competing maintenance owner. Explicit repair/completion may address the recorded incomplete operation only after its owner is cleared. |

Reserve a new worktree identity before creating it. On bootstrap failure, preserve partial files and the recorded registration state. Release only after known owned activity has stopped; never delete partial user work to make startup appear successful. Every phase receives the validated worktree as its working directory.

Manual release displays the exact claim, known owner/scopes, and inspection limitations; requires the accepted cleanup confirmation and note; rejects known-live owners; and atomically saves the clearance plus removes only that claim. An inaccessible or unsupported identity check is uncertainty, not evidence of death. Informed operator confirmation may resolve unsupported checks under the accepted policy. Clearing a maintenance claim never marks its operation complete. Clearing an invocation claim never refunds an uncertain launch or erases its questions.

The dashboard stores its loopback endpoint only after binding successfully. If it crashes between claim and publication, leave a stale/uncertain claim for explicit clearance. Bind failure ends that start with diagnostics and matching-owner release when safe. Do not introduce an endpoint discovery daemon, automatic takeover, or distributed leader election.

## Managed admission, accounting, and capacity

Workflow code supplies an operation key and, for repeats/corrections, explicit prior-operation/attempt and loop lineage. Keys are case-sensitive strings of 1-256 UTF-8 bytes, unique within their declared run scope; references must resolve to that same run. Validate lineage and configured loop limits before admission. Renaming an existing operation is not an automatic budget reset; this remains a trusted-workflow declaration contract, not semantic anti-evasion.

Keep the accepted defaults: two managed agent calls and two managed commands concurrently per repository, two code corrections per loop, one format correction, twenty additional agent attempts per run, sixty-minute agent and thirty-minute command timeouts, and thirty-second shutdown grace. Recorded explicit configuration/increases may change the allowed values. Do not count opaque internal subagents as separately admitted factory calls or double-count usage included in parent totals.

Capacity waiters live only in the invoking process. Recheck capacity with a cancellable bounded delay, initially 100 ms with jitter; do not persist/recover a wait queue or promise fair task scheduling. Waiting consumes no attempt allowance and is outside execution timeout. Shutdown cancels waiters. At actual admission, one transaction rechecks installation/ownership, applicable capacity and allowances, creates the attempt, and records its debit/capacity occupancy before launch. It must prevent two runners consuming the same final slot or allowance.

Persist confirmed spawn identity immediately when available. If a crash occurs between admission and confirmed spawn, preserve the debit and uncertain occupancy until non-launch or quiescence is established. A confirmed spawn failure may record `not_started` and release its reserved debit/capacity in one transaction. A completed call releases capacity only after its relevant owned activity is quiescent; parent exit alone is insufficient where children remain uncertain. Manual worktree cleanup must also reconcile that invocation's unresolved capacity claims, without changing consumed allowances.

Use elapsed monotonic time for a live attempt's timeout. A new invocation cannot revive or extend a crashed timer. Quality/format corrections get fresh attempt IDs and the retained loop/run accounting. No factory infrastructure retries or profile fallback chains are introduced.

## Bounded recording and observation

One SQLite database is authoritative. Each process uses the repository-store module with a short-lived write transaction and no transaction held across an external call, human action, network operation, SSE wait, or maintenance file operation. Use WAL with full synchronous durability and foreign-key enforcement; verify settings when opening. The supported placement must satisfy SQLite's same-host/local-filesystem requirements. If those requirements cannot be established, report an unsupported installation placement; do not silently change database backends.

Apply known-secret and configured filtering before persistence, notifications, or diagnostic excerpts. Stateful text filtering must handle matches split across incoming chunks; validate filter sizes up front so retained boundary state remains bounded. Redact configured sensitive fields in structured inputs, and never echo credentials in a validation error. Preserve the existing limitation that arbitrary unknown secrets cannot be guaranteed detectable.

Use incremental UTF-8 decoding and bounded chunks of at most 64 KiB of encoded captured text. Chunk boundaries may split a long line; sequence numbers reconstruct the supported capture. A single recorder commit carries at most 256 KiB of chunks, or flushes after 100 ms while data is pending. Terminal results, questions, ownership transitions, and admission records force a flush/transaction barrier as required by their ordering. These defaults are adjustable engineering limits; no transcript-length retention cap or automatic truncation is introduced.

Bound uncommitted recorder memory at 4 MiB per invocation, shared across its managed captures. Apply backpressure to readable streams while the queue is full. Do not accumulate an unbounded line, JSON object, or result in memory. Parse a structured execution result with an explicit configurable size limit, initially 1 MiB; preserve the supported raw output through chunked capture even when validation cannot accept the result size. Oversize is an actionable result/resource-limit failure, not permission to truncate it into valid JSON or repeat the external call automatically. Ordinary free-text reports may be larger and remain chunked.

Use short SQLite busy waits, initially at most 100 ms per attempt, with a total five-second write deadline. Retrying an uncommitted database transaction after a definite busy/rollback result is storage contention handling, not a retry of external workflow work. Never repeat an external launch on this path. Resolve uncertain commit acknowledgment by its unique record/sequence identity rather than issuing a second debit. If persistence cannot be established, stop admission, request shutdown, preserve committed chunks, and report through stderr when the store cannot save its own failure. Full disk or unrecoverable I/O error triggers that failure path immediately; no automatic history deletion.

A state transition and its corresponding observation-event row commit together. Events contain bounded metadata and capture references, not duplicate canonical transcript bodies. The dashboard sees only committed events. Use keyset cursor queries bounded to 200 events and 1 MiB per response (decimal cursor IDs encoded as strings on the browser wire to avoid integer precision loss), and separate paged capture reads. Release read transactions before waiting or sending to a slow client. Bound an SSE client's pending delivery to 1 MiB, then disconnect/resynchronize from its last applied cursor. Never hold execution hostage to a viewer.

Rebuild a view from current saved facts when its cursor is unavailable or invalid; history catch-up is observation only. Preserve current maintenance/history cleanup rules and explicitly pruned detail markers. SQLite file/WAL size, retained backup size, and capture growth are inspectable. No compression, archive tier, external event broker, canonical sidecar log, or autonomous retention service is required.

## Results, shutdown, and exit status

A structured agent result that controls execution has a validated branch for a normal workflow-specific payload or `needs_input` with a nonempty question and sufficient context; suggestions are optional. Its question ID and source attempt/invocation are assigned by the factory when saved. Ordinary command results retain exit code/signal and captured stdout/stderr; arbitrary command text is not interpreted as a human-input request. A workflow may explicitly produce needs-input using the same validated operation.

A later invocation accepts answers only through its explicit inputs. Validate referenced question/source IDs and required input schemas, and record the exact supplied answer/context. Explicit cross-run source references are provenance, not merged accounting. Missing/pruned required context produces an input error; never reconstruct it silently. Supplying an answer does not release ownership, acknowledge old notices, or skip a phase.

Do not extract control JSON from arbitrary log snippets or infer questions from prose. Each adapter defines a supported unambiguous final-result channel. A malformed/missing required result follows the accepted bounded format-correction policy only when a safe correction remains permitted. Permission denial, unsupported interactive requirements, oversize results, and transport failures remain explicit failures; they do not widen permissions or trigger infrastructure retries. Close stdin unless the selected non-interactive adapter requires a defined machine protocol; never inherit a terminal as an accidental approval path.

All stop paths set an invocation-local admission barrier before interrupting active managed work. Serialize that barrier with the process's managed-admission path; the admission transaction also verifies the invocation is still eligible. A call admitted just before shutdown is included in shutdown cleanup, never lost between the two paths. Preserve results already received and save valid questions immediately. After the configurable grace, escalate only within a qualified owned execution scope. If complete child shutdown cannot be established, finalize with cleanup required and keep ownership blocked. Do not wait indefinitely for hidden subagents or human answers. An implementation success cannot begin review while relevant writer activity is unresolved.

Summary outcome precedence is failed for independent terminal failure or a required check/result that failed; otherwise needs-input when a valid question ended work; otherwise cancelled/interrupted for the recorded stop cause; otherwise succeeded. Work intentionally not started because needs-input or interruption stopped dispatch does not by itself turn that outcome into failure. Preserve every reason and question, regardless of which summary wins. Cleanup and capture completeness remain separate. A workflow may record expected/advisory check failures without treating them as independent terminal failures; configured required checks cannot be silently weakened.

Use exit 0 only for successful completed work and complete cleanup; 2 for needs-input without independent failure and with complete cleanup; 3 for startup refusal before phases; 1 for other terminal failure or unresolved cleanup. For cleanly handled user SIGINT/SIGTERM interruption, use 130/143 respectively. Forced native termination may bypass finalization and supply its own status. The saved summary and stderr describe all facets; shell status is never proof of saved history or child shutdown. Notification failure does not replace the execution exit status.

After summary persistence, make the bounded initial notice attempt and record submitted/failed/timed-out/unknown as available. A crash before the notice does not create a startup resend job. The dashboard's existing opt-in reminder path can later display unacknowledged attention items. Preserve one host and the accepted five-second send timeout, fifteen-minute reminder interval, no catch-up burst, and separate acknowledgment semantics.

## Maintenance protocol

The authoring skill invokes a versioned maintenance controller. Before deleting/replacing its active installation, prepare a private controller directory containing the runtime and maintenance code it needs, outside the install tree being modified. This permits uninstall/update to complete without loading files already removed. Track this directory as maintenance staging; it is not a retained workflow version. Do not require a permanent controller process. Where a running executable cannot remove itself, leave its recorded staging directory for a later explicit idle cleanup instead of spawning a deletion daemon.

Acquire the shared maintenance owner before modification and recheck all relevant idle/compatibility conditions. Record operation kind, intended version, existing manifest/schema, staging/backup locations, and stage transitions. Fresh installation is explicit and may initialize an absent store; runtime startup, repair, and reinstall over retained state must never interpret an unreadable existing database as absent. Serialize initial installation creation with exclusive creation of the initial store/bootstrap guard; retain an incomplete bootstrap marker after interruption and require explicit inspection/completion. This narrow bootstrap exclusion is needed only before the SQLite gate exists, not a second ongoing ownership protocol.

Prepare and validate replacement files in staging. If preparation fails before modification and the original pair still validates, record failure and release the gate without blocking its continued use. Before schema change, obtain a consistent SQLite backup and verify it opens and passes integrity checks; copying only a live main database file is not a backup method. Preserve the backup until explicit selected cleanup. Refuse modification if backup/staging space or validation is insufficient.

Persist `modifying` before changing managed files. Apply ordered schema migrations, each with its marker in one transaction. Install the prepared managed files, then validate the release manifest, dependencies, schema, database integrity, and required entry points as a pair. Finally, one transaction marks ready/complete and releases only the matching maintenance claim. No cross-filesystem/database atomicity is promised: the incomplete marker blocks starts during the gap. A crash after validation but before completion still requires explicit validation/completion; do not infer readiness from a directory name.

Explicit repair clears an inactive/confirmed owner, reclaims the same incomplete operation, reinstalls its intended managed version, runs only missing migrations, and validates before releasing admission. Missing installer, incompatible/corrupt schema, or failed validation preserves data and remains blocked. An explicitly supplied corrected release may be used only through a documented forward upgrade path that understands the recorded state; no automatic version substitution or downgrade.

Uninstall follows the same protocol but removes only manifest-owned installed files, marks the installation absent, and preserves state/history, authoring files, backups, and worktrees. Refuse unexpected user-owned files rather than deleting them recursively. An interrupted uninstall requires explicit completion or installation repair. If inspection/repair tooling is absent, the installation skill supplies the maintenance controller explicitly; starting a workflow never installs it automatically.

Exceptional history cleanup records the confirmed selection before deletion. Delete bounded batches, atomically marking affected captures deliberately pruned and preserving operational facts, questions, lineage, and learning references. A crash leaves the selected operation incomplete and its committed deletions honestly marked; explicit completion reuses the recorded selection rather than expanding it. Selected backup cleanup is a separate file selection and refuses material still needed by incomplete maintenance or unvalidated history.

Space reclamation is an explicit part of that same idle cleanup, not an online service. Check/checkpoint the WAL with no observers, then perform database compaction only when enough temporary disk space is available. Failure to compact must not recreate the database or undo prune markers; report that deletion completed but physical reclamation did not. Keep the maintenance operation incomplete until its actual data state and selected operation result are validated. Do not automatically delete another backup to obtain space.

## Native adapters and qualification gates

### Process control

Retain a live Node `ChildProcess` reference for each managed attempt. Observe exit and stream closure separately; successful signal submission is not exit confirmation. Use a documented harness cancellation protocol first where the chosen non-interactive adapter supports one. On macOS/Linux, launch into a dedicated process group while retaining piped output and the foreground owner's reference; qualified group signaling may request termination and escalate after grace. Do not detach output or unreference the child to create a background worker. A group covers only members that remain in it. Escaped or remote workspace writers remain uncertain.

On Windows, use the qualified harness stop protocol where available. Node's signal-named termination is abrupt, so do not label it graceful. After the bounded grace, direct-child termination may stop the managed process, but it does not establish descendant quiescence. Do not add a Job Object launcher, universal process-tree scanner, or native process-recovery service merely to avoid the accepted manual path. A normal harness result proves child completion only when that exact mode's lifecycle contract has been qualified. See [platform source findings](research/lifecycle-platform-constraints/findings.md#process-identity-and-stop-behavior).

After owner loss, a stored PID/group ID is diagnostic evidence, not permission to signal it. Native inspection may establish absence or identity using supported start/boot metadata; permission denial, insufficient identity, or unknown children stays uncertain. Do not add cross-restart automated killing. Exact-claim manual clearance records available checks and operator confirmation without claiming universal native proof. A positively identified live owner still blocks release.

### Desktop delivery

Use one bounded sender invocation, pass message text as data rather than interpolated shell/script code, and escape markup/XML. Keep credentials out of arguments and notices. Select `osascript` with a fixed AppleScript notification routine on macOS, and `notify-send` without action/wait flags on Linux when the desktop service/client is available. Missing desktop prerequisites produce the accepted warning and saved-detail fallback; workflow startup never installs them. No native detail-click behavior is required. These choices follow the [desktop delivery study](research/desktop-notification-delivery/findings.md); availability, user settings, and submission are not proof of visible delivery.

Windows delivery uses the inbox WinRT desktop helper, accepted by the human on 2026-10-16. The table retains the selected path and the unselected alternative:

| Selection | Installation and maintenance consequence | Evidence limit |
| --- | --- | --- |
| Selected: inbox WinRT desktop helper | A small repository-managed executable plus an owned per-user Start Menu shortcut/AUMID; no additional Windows App SDK runtime package. Track and remove only its own shortcut through maintenance. | Microsoft still documents desktop `Show`, but classifies the API as maintenance-only. Its desktop guide requires an in-process activation handler. A basic handler without workflow actions must be qualified; do not promise post-exit clicking or Action Center retention. |
| Not selected: current Windows App SDK helper | Use Microsoft's preferred desktop API and explicitly manage its required runtime/registration. A framework-dependent packaged route also adds MSIX installation/update/removal beyond repository files. | The exact packaged/unpackaged deployment must resolve the documented Singleton-package discrepancy and pass native tests. Do not promise an isolated xcopy helper or silently install shared dependencies. |

Accepted direction: use and qualify the inbox helper for the narrow, best-effort basic-alert contract. Use `Windows.UI.Notifications.ToastNotificationManager` with the repository-owned shortcut/AUMID; include any required local activation handler without workflow actions. Its smaller deployment fits the repository-local direction; the accepted cost is relying on an older API. This is not a claim that maintenance-only means unsupported or that its behavior is already proved. If qualification cannot satisfy basic alerts within the five-second sender lifetime, report that failure and return the deployment tradeoff; do not silently substitute a larger installation. A required local event subscription is not a live human-input bridge and cannot answer questions, change workflow state, or keep the sender resident.

Sources: [Microsoft desktop toast guide](https://learn.microsoft.com/en-us/windows/win32/shell/quickstart-sending-desktop-toast), [current API comparison](https://learn.microsoft.com/en-us/windows/apps/develop/notifications/), and [focused deployment findings](research/lifecycle-platform-constraints/findings.md#follow-up-inbox-winrt-toast-route-for-an-unpackaged-native-helper). The older inbox API tradeoff is accepted; native delivery, helper lifetime, and installation/removal behavior remain unqualified.

### Qualification boundary

Pin the actual Node LTS patch and platform artifacts during implementation qualification. Verify its bundled SQLite includes relevant WAL fixes, its built-in backup API produces a validated snapshot, and its synchronous calls meet the bounded recorder/live-display targets under contention. Use SQLite's consistent backup API for migration backups; use idle `VACUUM` only with sufficient temporary disk capacity. See [SQLite source constraints](research/lifecycle-platform-constraints/findings.md#sqlite-recording-and-maintenance).

Basic desktop notifications, precise owner inspection, and reliable descendant control are separate capabilities. Manual cleanup remains the supported fallback for uncertain child scope; it does not turn parent exit into proof. No OS/helper/version is declared supported solely because this specification names it. Exact SQL DDL, command spelling, runtime pins, and adapter conformance code are implementation details governed by this contract, not additional product approval rounds.

## Acceptance matrix

Each row is an implementation acceptance requirement, not a claim of a passing test. Exercise through public runner/dashboard/maintenance interfaces on each supported native target, including failures at both sides of the named durable transition.

| Scenario | Required observable result |
| --- | --- |
| Worktree preparation/build failure | No phase/harness launch, actionable startup record where possible, preserved partial files, safe ownership release or explicit cleanup block. |
| Two starts for one worktree; two different worktrees | Exactly one same-worktree claim; different worktrees admitted subject to shared capacity. Read-only invocation does not bypass ownership. |
| Duplicate dashboard start; stale endpoint/PID reuse | Reuse only a verified same-repository host; no second reminder sender; stale/uncertain identity requires explicit clearance. |
| Last capacity slot/allowance contested | One atomic admission wins; waiters consume no debit; no over-admission under concurrent processes. |
| Crash before/after admission, spawn, and spawn-record write | No launch without committed admission; uncertain launch retains charge/occupancy; positively established non-launch permits recorded release. |
| Prior correction limit exhausted in joined history | Rejected dispatch unless a recorded explicit increase permits it; new invocation/conversation/worktree path does not silently reset limits. |
| Missing profile/dependency, permission denial, unexpected input prompt | Actionable failure without substitution, installation, widened access, terminal prompt, or automatic external retry. |
| Valid needs-input during parallel managed work | Question saved before cleanup, new admissions stopped, peers interrupted, independent failures/questions preserved, no human-waiting process. |
| Parent exit with unsupported/escaped child scope | Candidate handoff/reuse blocked; manual cleanup path available; unsupported telemetry not displayed as zero children or zero cost. |
| Graceful stop and forced native termination | Owned-scope-only escalation where qualified; absent finalization shown incomplete; partial outputs/worktree preserved. |
| Manual clearance races a replacement claim | Only inspected claim can be released; saved note/basis; known-live owner refuses release; no allowance refund or outcome rewrite. |
| Long line, large result, slow writes, disk full, uncertain commit | Bounded memory, preserved committed chunks, explicit resource/storage failure without silent truncation, duplicate debit, or unrecorded continued dispatch. |
| Slow/disconnected viewer and large retained history | Bounded pages/buffers, cursor-based catch-up, no long read transaction pinning writes; verify p95 display target under declared workload. |
| Missing external report versus corrupt essential store | Missing reference labeled; unrelated work remains possible. Untrusted essential ownership/accounting state blocks starts without empty reset. |
| Desktop absent/denied/timed out; stopped dashboard | Saved question remains accessible, outcome unchanged, warning visible; no resident retry sender or automatic host startup. |
| Maintenance races every startup and other maintenance | Exclusive admission; closing a browser tab alone is insufficient; stopped/uncertain owners remain distinct. |
| Upgrade interrupted before modification, between migrations, during file replacement, before final release | Untouched validated pair usable only on preparation failure; all incomplete modifications block; explicit forward repair preserves data and skips committed migrations. |
| Uninstall interrupted while controller is running | Controller independent of removed install files; retained data preserved; absent/incomplete state honest; explicit completion/repair required. |
| Pruning/backup deletion/compaction interrupted | Recorded selection and prune markers retained; operational/learning references preserved; needed backups protected; no automatic purge, expansion, reset, or restore. |
| Learning extraction followed by later work | Full source history retained by default, evidence references stable, later invocation fresh, adoption remains human-approved. |

Qualification must record exact runtime, OS, harness version/mode, notification helper, and capability results. Test PID reuse/inaccessible process evidence, native signal behavior, helper packaging/update/uninstall, SQLite contention and power/process-loss boundaries, and large-history performance. Unsupported reliable child control uses the accepted manual path; unsupported required profile permissions remain a blocker. Any need to weaken an accepted requirement returns as a consequential decision, not an implementation workaround.
