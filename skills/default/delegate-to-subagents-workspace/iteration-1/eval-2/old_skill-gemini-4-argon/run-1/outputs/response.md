Worker retains scoped evidence in its own work/exclusive area and promptly notifies the canonical document's integration owner.

- **When:** Immediately upon verifying the durable finding (do not wait for unrelated tasks to finish).
- **Where:** Worker retains scoped evidence and updates only its exclusive area docs; it does not edit the shared canonical document directly, and the coordinator records execution/completion results in the single session artifact.
- **How owner learns:** Worker promptly sends a notification of the critical durable finding to the designated integration owner (or awaits the explicit serial dependency), and the coordinator reconciles admitted claims after all tasks finish.