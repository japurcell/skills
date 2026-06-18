1. **Source of truth:** `evals/files/startup-fixture/prd.json` (`prd_file`) is the only official source for story status/completion; `evals/files/startup-fixture/progress.txt` is resume/append-only context only.

2. **Resolved `progress_file`:** `evals/files/startup-fixture/progress.txt` (resolved via `dirname(prd_file) + "/progress.txt"`). It exists, so read `## Codebase Patterns` and latest entries before dispatch.

3. **Story selection:** `story-auth-timeout` (highest priority `passes: false` story; `priority: 1`).

4. **Before any story-specific repo discovery:** invoke `subagent-model-router`, then limit orchestrator pre-dispatch reads to only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed for dispatch; do not read story-specific code/tests/behavior until a fresh `implementer` is dispatched with `./implementer-prompt.md`, full story properties, `progress_file`, and nearby `AGENTS.md`.
