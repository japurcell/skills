**Overdue, still running:** Send a non-interrupting warning. Request status, completed work, blockers, and updated ETA. Keep it running; do not cancel or replace solely because it is overdue.

**Runtime-terminated worker:** Retain partial results. Before replacement, record the error, submitted model and effort, runtime limit, completed work, findings, unresolved items, and artifact locations. Diagnose instructions, context, dependencies, permissions, tools, and environment. Verify partial results before reuse; hold dependent work until prerequisites are verified.

Revise the task or runtime limit if warranted. Allow **at most one replacement** without user authorization for more retries. Reroute if requirements or demonstrated capability needs changed. Record any revised route before redispatch; explicitly apply its exact model, effort, and enforced runtime limit.

**Neither event alone requires a stronger model.** Escalate only if diagnosis establishes greater capability needs. In live coordination, retain evidence and completion records in the same session artifact. No dispatches or file writes here.