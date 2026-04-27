Phase 0 keeps repo-local overrides, but Phases 1–11 persist durable state in GitHub issues and comments instead of local per-work-item markdown files.

- **Phase 6 approval:** record Gate D approval as an explicit comment on the **plan issue** using the approval comment shape (`Approved. Proceed with the implementation plan captured in this issue.` plus the machine-data block). Once that plan artifact is complete, **close the Phase 6 plan issue**.
- **Phase 7 task graph:** create a **task-graph issue** and put the task graph directly in that issue’s **body** under the deliverable section, preserving it as a fenced `yaml` block. The workflow no longer writes a physical `06-task-graph.yaml` file.
- **Phase 8 implementation log:** record progress on the individual **implementation task issues** by adding comments for each RED / GREEN / REFACTOR step. Use the implementation-log comment shape on the task issue instead of writing `07-implementation-log.md`.

So the new GitHub-native record is: plan approval comment on the plan issue, YAML task graph in the task-graph issue body, and implementation progress as comments on task issues.
