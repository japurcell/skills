**Overdue running worker**
- **Immediate action**: Treat runtime limit as warning threshold. Send non-interrupting warning requesting current status, completed work, blockers, and updated ETA.
- **Evidence & retry**: Keep running to preserve partial work. Do not interrupt, cancel, or replace solely because overdue.

**Terminated worker (`timed_out`)**
- **Evidence retention**: Record error, `selected`/`submitted`/`executed` (`unconfirmed` if unreported; never use self-report) config, `runtime_limit` (`value` and `mechanism`), `status: timed_out`, `output_verified`, `routing_compliant`, completed work, findings, unresolved items, and artifacts in the single session artifact before replacement.
- **Retry**: Diagnose instructions, context, dependencies, permissions, tools, and environment. Revise task scope or runtime limit (incorporating partial results). Record any revised route before redispatch, then dispatch at most one replacement with explicit `model`, `reasoning_effort`, and `runtime_limit` unless the user authorizes more retries. Pause dependent subtasks until prerequisites are verified.

**Model tier escalation**
- Neither event requires a stronger model by itself. Reroute to a stronger tier only if diagnosis shows requirements or demonstrated capability needs changed.