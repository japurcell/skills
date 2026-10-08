# AGENTS.md

This repository publishes skills from `skills/`, canonical custom-agent Markdown from `agents/`, repo-local Copilot hooks from `.github/hooks/`, installed Copilot hook sources from `.copilot/hooks/`, Gemini hooks plus config from `.gemini/`, and user-global Codex hook sources from `.codex/`. The repository `.codex/` directory is not a source for generated Codex custom agents.

## ExecPlans

The default location for ExecPlans is `docs/<feature-slug>/`.

## Agent Orientation

For read-only questions, reviews, and audits, start with the requested artifact and load only guidance needed for accurate conclusions.

Before editing, read [instruction routes](.agents/instructions/INDEX.md), identify the affected areas, and load only their matching instructions and validation branches. Follow explicit loading triggers; architecture, unrelated subsystems, and the entire memory corpus are not prerequisites for every task. Formatting is owned by `.editorconfig`.

### Knowledge maintenance

- Cross-check factual claims against current source, tests, configuration, or attributable evidence. Correct stale guidance encountered during the task.
- Apply [knowledge admission](.agents/instructions/knowledge-base.md) whenever selecting, recovering, or writing KB content, including source ingestion. Preserve established rules; an old model's recommendation does not establish policy.
- Keep only evidence-backed, non-obvious memories that change future decisions. Do not automatically create file/API maps, record every surprise, or copy session history. The optional [memory index](.agents/memory/INDEX.md) routes supporting evidence and source references.
- At the [end of every work session](#end-of-work-session-defined) that changes code, directories, configuration, schemas, or agent guidance, activate `update-agent-docs` and complete one coordinated pass. Wait for all tasks and delegated work to finish. A pass may conclude that no new memory is warranted.
- When documents move or change purpose, repair their indexes and inbound links. Preserve source-ingestion state and immutable raw inputs according to the admission rules.

## End of Work Session Defined

You are at the end of a _work session_ when:

- The task within a single task session is complete.
- All tasks within a multi-task session are completed.
- All tasks delegated to subagents have been completed.

## Protected Sections

- Never modify the `## ExecPlans`, `## Agent Orientation`, `## End of Work Session Defined`, or `## Validation Checklist` sections in `AGENTS.md` unless explicitly requested. These sections must remain intact as stable agent entry points.

## Validation Checklist

For read-only work, load guidance as needed. For changes:

1. Read the instruction index and matching area rules before editing.
2. Follow existing patterns and inspect the source that owns the behavior.
3. Run applicable builds and targeted tests using [testing routes](.agents/instructions/testing.md). Keep source, installed, and platform-specific evidence distinct.
4. Complete the single end-of-session `update-agent-docs` pass. Apply the admission rubric; adding memory is not a completion requirement.
5. For canonical KB changes, run `rtk proxy python3 scripts/lint-okf.py`, check affected links, and review the diff for lost obligations. Commit synchronized documentation with your changes.
