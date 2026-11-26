# AGENTS.md

This repository publishes skills from `skills/`, canonical custom-agent Markdown from `agents/`, repo-local Copilot hooks from `.github/hooks/`, installed Copilot hook sources from `.copilot/hooks/`, Gemini hooks plus config from `.gemini/`, and user-global Codex hook sources from `.codex/`. The repository `.codex/` directory is not a source for generated Codex custom agents.

For installer CLI verification, category selection, generated agents, or installed provider configuration, activate the `verify-skills` skill. It owns the disposable-install journeys and evidence procedure.

## Evaluations

For every skill change, add a new behavioral eval first. Run it against the old skill and confirm it fails for the intended reason before editing the skill. Then run the same eval against the updated skill and verify it passes.

Use Codex by default for live evals and wording iterations. Copilot credits are limited. Run Copilot when requested or when a check requires Copilot-specific evidence, using the fewest scenarios and repetitions that satisfy the requested coverage. If the user doesn't specify a model, use Luna by default to keep costs minimal.

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
