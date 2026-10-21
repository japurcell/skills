**Overdue running worker:** Treat runtime limit as warning threshold. Send non-interrupting warning requesting status, completed work, blockers, and updated ETA. Keep worker running; lateness alone does not justify interruption, cancellation, or replacement.

**Timed-out terminated worker:**
- **Evidence retention:** Before replacement, retain error, submitted settings, runtime limit, completed work, findings, unresolved items, and artifacts.
- **Immediate action:** Diagnose instructions, context, dependencies, permissions, tools, and environment. Revise assignment or runtime limit as needed.
- **Retries:** Dispatch at most one replacement unless user authorizes more retries.

**Model tier:** Neither event alone justifies a stronger tier. Reroute only if requirements or demonstrated capability needs changed.