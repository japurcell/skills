# Session notes

- Two subagents implemented different runtime slices, but neither owned the committed manifest or `.agents/` docs. Parent agent had to rework the final integration because the shared surface had no explicit owner.
- Several follow-up edits failed with `Path does not exist` and `apply_patch` `ENOENT` after the parent assumed a subagent had created files it only reported conceptually.
- Durable fix: if work touches shared files or shared contracts, keep that surface with the parent agent or assign one subagent to own it explicitly.
- Durable fix: after background subagents or failed patches, refresh the real worktree state before `Update File` or `Delete File`.
- One-off noise: somebody reopened the same diff three times while thinking.
