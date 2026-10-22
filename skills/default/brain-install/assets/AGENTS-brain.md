## Brain

The `brain/` directory is an Obsidian vault - persistent memory across sessions.

- **Read first.** Read brain files relevant to your task before acting.
- **Write** after mistakes, corrections, or notable codebase learnings.
- **Structure:** One topic per file. Directories with standard Markdown link indexes - no inlined content.
- **Maintain:** Delete outdated notes. Clean completed/abandoned plans from `brain/plans/`.
- **Reflect:** At the end of every [work session](#end-of-work-session-defined) that changes code, run the `reflect` skill. Persist only durable findings; a review may require no write.
- **Index ownership:** Hooks generate `brain/index.md`. Put prose in topic notes and maintain link-only curated subindexes. Invoke `meditate` and `ruminate` only on explicit request.

## End of Work Session Defined

You are at the end of a _work session_ when:

- The task within a single task session is complete.
- All tasks within a multi-task session are completed.
- All tasks delegated to subagents have been completed.
