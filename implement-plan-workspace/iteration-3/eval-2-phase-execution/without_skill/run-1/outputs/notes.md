# Notes

- Output intentionally scoped to one phase (Core) per prompt.
- Format mirrors /implement-plan behavior: dependency-aware execution, [P] handling, file-path conflict serialization, per-task task-list updates, and phase checkpoint gating.
- Kept concise while preserving stop/continue rules and handoff payload shape.
