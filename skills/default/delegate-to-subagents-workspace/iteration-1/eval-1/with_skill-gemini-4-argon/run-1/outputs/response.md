Do not serialize the documentation work or transfer area documentation ownership to the coordinator. Run both independent workers in parallel because neither touches a shared file or shared canonical document. Exclusive area documentation remains worker-owned.

Coordination rules:
- Assign each worker disjoint write ownership for its source directory and its area documentation.
- Tell workers they share the codebase, must preserve others' edits, and must stay within their write ownership.
- Have workers retain scoped evidence and promptly notify the owner of durable findings, including critical guidance.
- After all tasks finish, the coordinator verifies outputs, reconciles admitted findings and documentation ownership, and completes the final documentation pass.