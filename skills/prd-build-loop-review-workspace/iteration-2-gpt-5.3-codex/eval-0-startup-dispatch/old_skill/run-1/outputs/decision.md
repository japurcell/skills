## Source of truth
`evals/files/startup-fixture/prd.json` is the only official source for story status/completion.

## Resolved progress_file
`evals/files/startup-fixture/progress.txt` (resolved via `dirname(prd_file) + "/progress.txt"`). It exists, so startup uses its `## Codebase Patterns` and latest entries for resume context.

## Story selection
`story-auth-timeout` — **Auth timeout matches spec** (highest-priority story with `passes: false`, `priority: 1`).

## Before any story-specific repo discovery
No story-specific code/test/file discovery by orchestrator yet. First, orchestration is constrained to `prd_file`, resolved `progress_file`, and nearby `AGENTS.md` needed for dispatch; then model routing and fresh `implementer` dispatch (`./implementer-prompt.md` + full story properties + `progress_file` + nearby `AGENTS.md`, mode `initial_implementation`) must occur before any story-specific repo discovery.
