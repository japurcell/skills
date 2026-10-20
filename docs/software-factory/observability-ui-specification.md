# Detailed observability UI contract

Status: detailed design and refined prototype accepted by the human on 2026-10-20. Product policies remain owned by their [decision tickets](map.md). This document specifies their presentation, not a new execution system.

## Purpose and hierarchy

Answer three questions: What happened? What needs my attention? What evidence can teach us something? Preserve the accepted run cards, owner/session timeline, and phase inspector beneath it. No alternate dashboards, task boards, workflow editor, or execution controls are required.

The repository index shows run request, workflow, latest invocation identity/outcome, start time, elapsed time, miniature observed activity, cleanup, capture, and unknown usage explicitly. Opening a run selects its latest invocation, with a chronological invocation selector and explicit links to earlier invocations. The latest result never overwrites earlier outcomes. A history group is not a resumable workflow.

Inside an invocation, show the summary and outstanding attention first, timeline second, selected phase/attempt details third. Keep workspace, retained accounting, configuration, and storage in disclosures. Do not require opening a transcript to discover uncertain cleanup.

## Independent state labels

| Dimension | Presentation |
| --- | --- |
| Execution | Preparing, running, stopping; then succeeded, failed, ended: needs input, interrupted, or cancelled. No saved final result means outcome unknown. |
| Ownership/cleanup | Owned by active invocation, cleanup in progress, automatically checked, manual cleanup required, or operator confirmed. Show cleanup basis and note, not a generic safe badge. |
| Capture | Capturing, complete, partial, unknown, or explicitly pruned. Complete means complete supported capture, not access to every harness internal. |
| Telemetry | Reported children, parent only, unavailable usage, or unsupported detail. Missing telemetry is never zero usage or proof of no children. |
| Observation | Connected, catching up, disconnected with last update time, or frozen at a saved cursor. Connection loss is not execution failure. |

Status text accompanies color. Needs-input with manual cleanup gets both labels and both next steps. An independently failed call during shutdown remains visible beside a saved question; calls stopped because dispatch ended are labeled interrupted for shutdown, not independently failed. A saved question without finalization remains a question under outcome unknown.

Automatic cleanup and operator confirmation have distinct wording permanently. Releasing ownership does not revise the old outcome. Show known process/session/worktree references as diagnostics, never a stale PID kill button. The user reads CLI/native-tool guidance to inspect children and record clearance.

## Timeline and navigation

- Lanes represent managed phases and native owner/session activity. Reported child sessions nest beneath their parent with a text relationship. Child visibility never implies control or factory-managed tasks. A parent-only example states that child activity is unavailable.
- Order phases by recorded start and stable identity; group repeated attempts within their named phase. Never hardcode plan/build/review stages. Distinct simultaneous sessions get separate rows, avoiding overlapping clickable blocks. Sequential attempts remain separately selectable.
- Show declared work without a time bar or duration. Show skipped branches explicitly. Insert newly observed children under the parent without moving keyboard focus or changing selected details. No predicted completion percentages or fictitious future loop iterations.
- Collapse children per parent; preserve selection and reveal ancestors when following a deep link. Provide an equivalent text list of phases, attempts, times, and states for keyboard, screen-reader, and narrow-screen access. Truncated timeline labels retain full names in that list and inspector.
- Product URLs identify repository/run/invocation/phase/attempt and optionally event cursor. Invalid, pruned, or unknown references show a diagnostic and nearest surviving parent link; never silently select another record. Native conversation IDs are metadata, not resume links.
- Selecting a phase focuses the inspector heading without moving the timeline off its place in the document. Back/forward restores selection and reading position. A return-to-timeline link restores the originating phase focus. Search/filter/collapse are local views only; a hidden selection is disclosed rather than silently changed.
- Search run request, workflow, and identities. Outcome filtering refers to the selected/latest invocation and is labeled accordingly. Index ordering is stable during reading; a new-runs notice refreshes ordering explicitly rather than shuffling cards under the pointer.

## Inspector and evidence

The inspector uses context on the left and captured events on the right; below 850px it stacks. Default open sections are request/structured result and events. Secondary disclosures contain effective configuration, saved prompt/skill inputs, corrections, usage, and file references. Failed and needs-input results expand their explanations automatically on initial selection, not repeatedly during updates.

Every detail carries run, invocation, phase, and attempt identity. Native session identity, profile, and shared worktree are separate fields. Compatible corrections may share a native conversation within one invocation; later invocations always show fresh conversations. Display requested and effective profile separately when known; required-capability failure is an error, optional missing telemetry is a limitation. No fallback countdown or retry button.

Show workspace preparation before the first phase, resolved starting commit, new versus explicitly reused worktree, and one shared path. Never offer uncommitted-change capture. A later invocation starts at the current workflow entry; history/context/worktree reuse is not execution replay.

Accounting shows used/limit per named correction loop and retained run allowance, links to recorded increases, and charge basis for uncertain launches. Distinguish managed attempts from opaque native children. Do not sum parent-inclusive usage with child usage. Unknown cost, token counts, and context utilization remain unknown.

Saved traces, prompts, and outputs open as text tied to their captured identity. External file references have their path and recorded revision/time if available; current contents may differ or be missing. A missing file is not a corrupt history database. Render output as inert text, never executable HTML. Preserve raw saved output when structured parsing fails; show parse failure separately from captured text.

## Live following and bounded history

Use the accepted saved-before-display SSE contract. Apply events in saved order, deduplicate by event identity, and advance the cursor only after applying. Reconnect catches up from that cursor. A missing/pruned cursor requires a visible gap and a new saved snapshot; never silently claim continuous capture.

Freeze pins the displayed saved cursor and stops view advancement, not recording. Follow catches up explicitly. Scrolling away from output's bottom suspends automatic scrolling and exposes a new-events count. Return to latest restores following. Arriving events do not steal focus, reopen disclosures, reorder the index, or replace a reader's selected text. Do not announce every output line through a live region; announce connection and selected-invocation outcome changes politely.

Use bounded pages rather than a new search service or universal virtualized tree. Start with 30 run cards per page, 50 visible lane rows per page, and event pages capped by the lifecycle reader's 200 events/1 MiB limits. Load earlier/later pages explicitly while preserving the visible anchor. Large individual outputs open in bounded text chunks; no silent truncation of saved history. A follow window may evict older rendered pages only when the reader is at latest; saved content remains accessible. This bounds DOM and memory without automatic retention.

Implementers must qualify 10,000 runs, 1,000 sessions in an invocation, 100,000 events, deeply nested children, long labels, and multi-megabyte output. These are validation datasets, not a claim that the nine-run prototype implements paging or proves performance. The one-second display target remains an implementation test obligation.

## Attention without workflow controls

An attention block shows repository/run/invocation, reason, question and suggested answers where supplied, saved outcome, cleanup requirement, and CLI guidance. Acknowledge notice changes only persisted notification metadata; it does not answer, approve, stop, restart, or release anything. Preferences change notification metadata only. No permission dialog bridge is added.

Show notification submission separately from visible delivery, which may be unknown. Initial notices combine the invocation's issues. Success may be quiet. Optional links open saved details only; neither old links nor browser tabs start a stopped dashboard host. Missing delivery never hides the saved outcome.

Reminders default off. Show configured interval (default fifteen minutes) and delivery timeout (default five seconds) as observation. Reminders run only while the dashboard host runs; reopening lists outstanding items without replaying missed notices. Acknowledgment silences reminders for that invocation. The prototype's acknowledgment is in-memory and deliberately not a persistence demonstration.

## Learning inspection

Reuse ordinary invocation, result, and evidence views. No separate learning scheduler, benchmark registry, or promotion console.

An extraction result links examined invocation/attempt/event sources with capture limits, candidate proposal and scope, or an explicit no-justified-proposal result. Unexamined history remains distinct. An evaluation result shows exact baseline/candidate inputs, cases, criteria, outcomes, evidence, and limitations; inconclusive is not passing. An adoption record shows the human decision and actual applied revision/target separately. Approval with absent or uncertain application is not adoption. Reverts link the actual reverting revision and original change. Source pruning renders an explicit missing-detail marker, not a fabricated evidence excerpt. Extraction does not mark history disposable.

All source selection, execution, approval, adoption, and revert occur through existing CLI/workflow/authoring paths. The browser links saved evidence only.

## Empty, unavailable, and maintenance states

| Situation | What the user sees |
| --- | --- |
| Loading | Labeled loading region; no zero-count or success claim. |
| No runs | No saved runs, with CLI startup guidance. |
| Filter has no matches | No matching runs, with a local clear-filter action. |
| Disconnected | Last saved display and last update time; execution state remains last observed. |
| Database cannot be read | History unavailable with diagnostic; never an empty-history success state. |
| Partial/pruned capture | Available chunks plus explicit missing ranges/reason where known. |
| Missing external file | Missing reference, with saved outputs still accessible. |
| Maintenance | Dashboard host must stop. An already-open tab becomes disconnected; it cannot promise live maintenance progress. CLI identifies operation, interrupted state, and explicit forward repair. |
| Uninstalled | Existing tab is stale. Compatible installation is required to read retained history. No browser repair, restore, uninstall, or gate release. |

Repository storage shows saved history, upgrade backups, measurement time, and unknown measurements honestly. Growth uses existing measurements only; no new collector service. Cleanup guidance explains explicit exceptional idle maintenance, including stopping the dashboard process. Closing a browser tab is not host shutdown. No deletion, automatic rotation, downgrade, restore, or purge controls.

## Visual and accessibility contract

Preserve the accepted compact dark workbench. Tokens: background `#0e1622`, panel `#162130`, text `#e4ebf5`, secondary text `#adbbcd`, links `#75d5e1`, attention `#e7c47d`. System sans carries UI text; monospace is reserved for code and identifiers. Body text is 14px minimum, primary heading 24px, section heading 18px; compact event metadata may use 12px. Use 8px spacing increments with 16-24px panel padding, existing restrained borders, and no decorative motion.

Cards use three columns above 1150px, two until 650px, then one. Context/events stack below 850px. At 390px and 200% zoom, the document must not scroll horizontally; the labeled timeline may scroll internally. Normal text must meet 4.5:1 contrast, meaningful controls/focus indicators 3:1. Targets must meet at least 24 by 24 CSS pixels or sufficient spacing, with larger primary controls. Verify actual rendered combinations, not token values alone.

Use semantic headings, links, buttons, labeled controls, native disclosures, visible focus, and a skip link. All actions work by keyboard without global arrow-key interception. Dialog focus is contained and restored. Do not rely on color, hover titles, or chart position to communicate essential information. Respect reduced motion. Screen-reader order matches visual hierarchy. Full screen-reader, zoom, contrast, and focus audits remain implementation gates.

## Prototype coverage and review boundary

The [refined prototype](prototypes/observability-prototype.html) preserves the accepted layout and contains nine synthetic runs: observed children, bounded corrections and later-invocation context, ended needs-input plus manual cleanup, review-only work, branching, operator-confirmed cleanup with partial capture, learning, selected-provider failure, and crash-before-finalization.

It demonstrates index filtering, phase deep links, child collapse, freeze/follow, disconnected observation, saved-output inspection, and notification acknowledgment. It does not implement a runtime, SQLite, SSE, process control, native delivery, multiple-invocation paging, large-history paging, or learning execution. The text contract governs those unimplemented interaction details. Prototype review comments are separate design feedback, never product workflow input.

The user delegated routine design decisions. No new consequential scope choice was found. The human accepted the concrete artifact and this contract on 2026-10-20. Final specification acceptance remains a separate ticket; design acceptance does not certify unimplemented behavior.
