I_CAN_SEE_SESSIONSTART_CONTEXT

# Orchestrator startup decision

- **Source of truth:** `evals/files/startup-fixture/prd.json` (`prd_file`); `progress_file` is append-only resume data.
- **Resolved `progress_file`:** `evals/files/startup-fixture/progress.txt` (`dirname(prd_file) + "/progress.txt"`; no explicit path was provided).
- **Story selected:** `story-auth-timeout` (`priority: 1`, first `passes: false` story).

Before any story-specific repo discovery:
- Resolve startup only.
- Read only `prd_file`, `progress_file` if it exists, and nearby `AGENTS.md` needed to dispatch work.
- If `progress_file` exists, read `## Codebase Patterns` and latest entries; otherwise initialize it on first append.
- Do not inspect story-specific repo files, tests, code, or behavior until a fresh `implementer` is dispatched.
