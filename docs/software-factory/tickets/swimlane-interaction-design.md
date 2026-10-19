# Swimlane interaction design

> Post-acceptance lifecycle amendment, 2026-10-15: layout acceptance remains valid. [SSSF-style continuation](workflow-versioning-and-run-changes.md#resolution) supersedes fixture text about saved waits after runner exit or Continue restoring an interrupted run. The HTML is retained as layout evidence; the detailed UI ticket owns replacement labels and scenarios. The later non-interactive amendment also removes live human/native permission waits: show ended needs-input outcomes and attention notifications under [Human input and execution controls](human-control-and-publication.md#resolution).

**Type:** prototype
**Status:** closed
**Blocked By:** session-events-and-live-progress.md, human-control-and-publication.md
**Research Dir:** not applicable

> Workspace/delegation amendment, 2026-10-15: the accepted layout remains. Interpret lanes as phases and owner/session activity, nesting harness-reported subagents beneath their parent. Factory task scheduling, integration lanes, and per-task workspace semantics are historical. The detailed UI ticket owns fixture updates, workspace preparation, and parent-only visibility examples. Managed publication, generic criterion-evidence/reviewer-policy panels, and immutable captured-artifact guarantees are also superseded; retain the accepted layout with ordinary saved results.

## Question

How should the read-only UI expose arbitrary workflow structure, concurrent sessions, and the effects of CLI interventions without hardcoded stage columns?

Work with the human using the prototype skill when this ticket is selected. Existing HTML designs are reference material, not the answer.

Choose lane grouping, nesting, planned versus observed work, dynamic task insertion, session/attempt drilldown, active output, wait/failure/skipped states, and live versus historical navigation. Observe the updated human-control contract: workflow inputs are configuration and command arguments, not browser controls.

Use representative workflows: an implementation phase with supported nested subagents, a parent-only implementation with unavailable child telemetry, a review-only run, and a custom workflow with a branch and loop. Resolve through human review of a cheap interactive artifact; link that artifact rather than embedding it in this ticket.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

## Prototype review record

### Current direction, 2026-10-15

The human supplied six SSSF screenshots and changed the web UI to observability only. The [owning control amendment](human-control-and-publication.md#observability-only-amendment-2026-10-15) supersedes the previous approval inbox and browser controls. The earlier A/B/C question was never answered or accepted and is superseded as the next review prompt. Follow the supplied hierarchy rather than asking that question again.

All six local screenshots were inspected:

| Reference | Observed pattern and application |
| --- | --- |
| [Session index](../prototypes/screenshots/session-index.png) | Multiple run cards, each showing request, workflow, status, timing, and miniature owner lanes. Use a repository run index with miniature event timelines. |
| [Live index](../prototypes/screenshots/session-index-live-updates.png) | Running and historical cards coexist, with live status and event marks. Append saved activity at index level without opening a run. |
| [Session details](../prototypes/screenshots/session-details.png) | Full elapsed-time timeline, owner/model labels, multiple phases per lane, and event marks within blocks. Preserve task/session distinctions and repeated attempts. |
| [Live session details](../prototypes/screenshots/session-details-live-updates.png) | Timeline remains above the selected phase's request and event details. Inspect phases beneath the timeline while retaining run context. |
| [Phase details](../prototypes/screenshots/phase-details.png) | Collapsible request, configuration, instructions, gates, usage, and outputs beside timestamped events. Use a two-column inspector that stacks at compact widths. |
| [TUI workflow picker](../prototypes/screenshots/tui-workflow-picker.png) | Terminal workflow names, descriptions, and compositions. This informs command-side selection but does not establish a requirement to build a TUI. |

Screenshots establish visual structure, not transport, reliability, exact behavior, or current model capabilities. The human describes the live behavior; a still image cannot measure latency. Preserve factory vocabulary: a run contains steps/attempts and concrete harness sessions. Do not rename a run to a harness session because SSSF calls its top level “sessions.”

The revised [observability prototype](../prototypes/observability-prototype.html), served at [the run index](http://localhost:8765/prototypes/observability-prototype.html), contains six example runs, full timelines, phase details, retained failed attempts, and synthetic live events. Waiting and interrupted states have no browser response buttons. Local view filters and Freeze this view do not stop recording. Design annotations are explicitly prototype-only and use separate browser storage. The earlier [A/B/C artifact](../prototypes/swimlane-prototype.html) remains for existing notes and comparison history; its execution controls are obsolete product guidance.

The human accepted this layout on 2026-10-15; see the Resolution below. Branding, fine polish, and detailed interaction behavior remain with [Detailed observability UI design](detailed-observability-ui-design.md). Do not re-ask whether the web UI should control execution.

Browser verification on 2026-10-15 covered the six-run index, search and status filtering, live event growth, frozen view remaining unchanged while recording continued, catch-up on Follow, phase configuration/events, and a retained failed review after later success. Waiting/interrupted examples expose no workflow action buttons. At a 390px viewport both index and run detail measured 390px document width; the timeline scrolls internally. The annotation dialog opens independently of workflow state; current-version save/export persistence has not been browser-tested. JavaScript parsing and whitespace checks passed after fixing a template-literal syntax error found on first load. This remains a synthetic in-memory fixture, with no evidence of actual SSE, durable storage, native harness operation, or the one-second performance target.

### Earlier prototype, 2026-10-14 (superseded control surface)

Claimed on 2026-10-14 as `subagent-s7w4n2`. Both exact prerequisite files were verified closed. This session compares three structurally different views of the same simulated run data: a nested elapsed-time timeline, scope-based lanes, and a session console with an activity feed. The UI prototype is a planning artifact, not a factory implementation. No layout is accepted yet.

Settled policies are inputs, not new questions: arbitrary named scopes and dynamic children; saved-before-display progress; retained evidence; independent dashboard; Pause/Continue/Cancel; distinct factory checkpoints and live native waits; one-action grants with profile-gated broader scope; bounded repairs; no automatic restart or publication.

Design direction: a compact repository workbench, left-aligned labels, system sans for navigation and monospace only for output/code. Colors: paper `#f5f7fa`, ink `#18283b`, blue `#215aca`, teal `#176b56`, amber `#87500a`, red `#b02e40`. Status always has text. Three layouts disagree about the primary organizing unit (elapsed work, scope, or active session), while retaining the same inspector and approval inbox. Avoid fixed plan/implement/review columns: those names are fixture data only.

### Artifact for human review

- [Standalone interactive prototype](../prototypes/swimlane-prototype.html), served at [local layout A](http://localhost:8765/prototypes/swimlane-prototype.html?variant=A). Use the bottom bar or left/right arrow keys outside form controls to switch A/B/C. The selected variant is in the URL.
- [Review guide](../README.md#swimlane-design-review) explains scenarios, annotations, and preview setup. Review notes persist in browser storage and export as Markdown; run state is an in-memory simulation.

| Variant | Primary structure | Benefit | Tradeoff |
| --- | --- | --- | --- |
| A / Nested timeline | Workflow scopes contain step rows against observed elapsed time | Parallel sessions and waits are visible together; arbitrary scope names fit | Deep trees need collapse/filter controls; transcripts require selecting a step |
| B / Scope lanes | Columns come from the workflow's own scopes | Easy scanning of work items, outcomes, and dependencies | Many scopes become a wide board; elapsed concurrency is less obvious |
| C / Session console | Session list beside recorded activity | Direct access to conversations and custom progress messages | Commands and the declared future are less prominent than in the other layouts |

**Assistant recommendation, not an accepted decision:** use A as the default overview, retaining C as a focused activity/session view. Keep a common inspector and inbox so changing the view does not change identities, history, or control semantics. B remains a comparison candidate, not a required product feature. The visible grouping and inspection controls are proposals to review, not newly settled requirements.

The fixture deliberately includes the default repository-change recipe, a read-only audit with discovered parallel investigations, and a custom conditional branch with a bounded repair loop. Skipped branches remain visible. Unknown future iterations do not become fictitious tasks or percentages. Prior attempts remain accessible through the inspector. Timeline bars are illustrative, not scheduler estimates or measured durations.

### Suggested review path

1. Compare the same initial native-permission wait in all three layouts. Select the UI task and inspect its output, effective-profile example, and context.
2. Allow the simulated action, then advance to two parallel reviewers, a blocking finding, a separate repair, and fresh review attempts. Inspect an earlier attempt.
3. At the factory checkpoint, save an approval while no runner exists. Continue separately; inspect the illustrative foreground command. Withdrawal is available before dispatch.
4. Reset, simulate a runner crash, and inspect the disabled native request. Continue simulates successful reconciliation and creates a fresh request rather than answering the dead callback.
5. Inspect older snapshots while playback continues; return to Follow live. Try the review-only and custom-loop workflows. Leave layout or step comments and export them.

### Verification and limits

Browser checks on 2026-10-14 covered layout switching, permission response, parallel review and repair progression, crash invalidation and fresh request identity, Pause/Continue, an unanswered checkpoint blocking advancement after Continue, saved approval without automatic resume, withdrawal, and simulated publication completion. Review-only and custom-loop examples reached completion; the second custom repair became visible when discovered. Historical controls were disabled. Annotation save/reload and Markdown download were exercised, and the temporary annotation was removed. At a 390px viewport, document content was 375px wide with internal horizontal scrollers. Inline JavaScript parsing and whitespace checks passed. These checks verify the artifact only.

The artifact does not implement SSE, SQLite, native adapters, real transcript streaming, process termination, Git worktrees, publication, reconciliation, or measured latency. Play produces synthetic saved events every 1.5 seconds. The request-changes path captures feedback and stops at a queued-repair explanation; it does not simulate another complete cycle. Switching example runs resets their simulations. Profiles, revisions, evidence, elapsed time, and commands are illustrative. Exact CLI spelling, adapter capabilities, and recovery mechanisms remain unselected or unverified where their owning tickets say so.

Additional browser checks confirmed the simulated run continued to completion while inspecting history, and Cancel produced a terminal state with Continue disabled. At compact widths, selecting a step scrolls to its inspector and a Back to workflow control returns to the diagram. These affordances are part of the proposal, not an accepted layout policy.

The original A/B/C question is superseded by the 2026-10-15 direction and acceptance below. Its controls and review instructions above are historical evidence only.

## Resolution

On 2026-10-15, the human said: "The layout looks good. Record it as accepted." Both exact prerequisites are closed. This accepts the layout of the [observability prototype](../prototypes/observability-prototype.html): a repository run index with miniature timelines, a full run timeline grouped by owners/tasks, and selected phase details beneath that timeline. Phase context and recorded events sit alongside one another at wider widths and stack on compact screens.

The web UI remains observability-only under the [control amendment](human-control-and-publication.md#observability-only-amendment-2026-10-15). Workflow input comes through configuration or CLI arguments. Local navigation, filtering, and freezing affect observation only; prototype notes are design feedback, not a product execution channel.

The human also requested a later ticket for detailed UI design. [Detailed observability UI design](detailed-observability-ui-design.md) owns remaining interaction, visual, accessibility, responsive, and scale decisions before specification acceptance. This acceptance establishes the layout direction, not every fixture detail or a finished product design. The earlier A/B/C alternatives were not accepted.

The browser checks above validate only the synthetic prototype. No runtime, persistence, transport, adapter, or latency guarantee is proved by layout acceptance. Factory implementation remains outside this planning effort.

