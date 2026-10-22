# Hybrid startup prototype

**Type:** prototype
**Status:** closed
**Blocked By:** startup-and-platform-delivery.md, integration-event-coverage.md
**Research Dir:** not applicable

## Question

Does starting once on the first event, staying resident, and optionally starting at login feel right across ordinary events, bursts, Quit, crash recovery, and returning to missed alerts?

User authorized this prototype on 2026-10-21. Build a single-file browser lifecycle simulation using the prototype logic branch. Expose relevant state and guided scenarios. This does not prove native processes, concurrency, window placement, OS sound, or login registration. Do not change real startup settings or hooks. Pending alerts use an explicitly disposable browser store; native application durability remains unverified.

## Prototype contract

- First simulated CLI invocation starts the app once. Later events reuse it.
- Optional simulated login startup starts it before an event.
- All alert types persist in a stack until dismissed. Snooze moves the front alert to the back; no timer or automatic expiry.
- Dismiss deletes an alert and Dismiss all deletes the whole pending stack. Both offer brief Undo. No dismissed-alert retention or history window.
- Explicit Quit preserves the stack and queues later events. Manual reopening restores the stack. User confirmed this choice.
- Pending alerts survive browser reload where browser storage is available. Undo is transient and ends on reload. Use one clearly named prototype storage key.
- Human feedback is required before closing. Native feasibility and detailed visual design are later decisions.

## Validation

Manually exercise public buttons: cold/warm event, burst, stack cycling, deletion with Undo, login toggle, quit/queue/resume, crash/recovery, and pending-alert reload. No automated tests for throwaway code, per prototype skill. Inspect desktop/narrow layouts, keyboard access, and console errors. Record actual evidence and limits before handoff.

## Prototype ready for review

- [Artifact, run instructions, and observed evidence](../phase-1-startup-prototype.md).
- Browser interaction checks and JavaScript syntax passed. Native behavior and narrow viewport remain unverified.
- User settled explicit Quit and requested persistent stacked alerts with Snooze cycling. [Current stack prototype and evidence](../phase-2-alert-stack.md) captures this revision.

## Resolution

- User reviewed the revised prototype, including Dismiss all, and said “This looks good.” The demonstrated browser interaction is accepted.
- Accepted flow: hybrid startup; explicit Quit queues alerts until reopening; persistent stack of all alert types; Snooze cycles to the back. User subsequently replaced retained history with deletion plus brief Undo for individual and bulk dismissal; see [current deletion contract](../phase-3-deletion-and-undo.md).
- Browser acceptance does not prove native startup, window placement, audio, latency, concurrency, accessibility, or platform parity. Those require separate feasibility work.
- Prototype artifacts and observed verification remain linked from the phase notes. No production code was created or promoted.
