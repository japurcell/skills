Do not serialize exclusive area documentation or transfer its write ownership to the coordinator.

- **Parallel execution:** Run both independent workers in parallel with `dependencies: none`.
- **Write ownership:** Each worker keeps exclusive write ownership of its own source directory and exclusive area documentation.
- **Shared canonical docs:** No worker touches shared canonical documents (maps, indexes, known issues), so shared-file serialization is `not applicable` during worker execution. If durable findings or critical guidance affect a shared canonical document, workers retain scoped evidence and promptly notify the designated integration owner.
- **Coordinator pass:** After all tasks finish, the coordinator reconciles admitted claims and runs the final documentation pass.