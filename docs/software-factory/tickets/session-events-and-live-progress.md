# Session events and live progress

**Type:** grilling
**Status:** open
**Blocked By:** workflow-authoring-and-task-contract.md, agent-execution-profiles.md
**Research Dir:** not applicable

## Question

What event and artifact contract makes every custom step and agent session visible in real time and inspectable later?

Define run/task/step/attempt/session identities, parentage, lifecycle events, sequence and cursor behavior, partial output, tool events, artifacts, observed skill use, and usage provenance. Include deterministic commands and work that emits no detailed harness telemetry.

Decide the user-visible latency target and streaming approach, persistence before display, reconnect behavior, ordering, deduplication, backpressure, retention, sensitive-data handling, and minimum instrumentation for custom steps.

Resolution should define representative events, live/history consistency guarantees, honest unsupported-data states, and acceptance criteria. Do not equate a stored final result with real-time session progress.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

