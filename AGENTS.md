# AGENTS.md

This repository publishes skills from `skills/`, canonical custom-agent Markdown from `agents/`, repo-local Copilot hooks from `.github/hooks/`, installed Copilot hook sources from `.copilot/hooks/`, Gemini hooks plus config from `.gemini/`, and user-global Codex hook sources from `.codex/`. The repository `.codex/` directory is not a source for generated Codex custom agents.

## Git state protection

- Never edit `.git` metadata directly. Use Git commands for repository state.
- Before a command that could discard local work, show `git status`, unstaged `git diff -- <affected-paths>`, staged `git diff --cached -- <affected-paths>`, and untracked files or a dry-run deletion list. Plain `git diff` omits staged and untracked work.
- If work would be lost, ask the user to approve the exact command. Approval for one command never carries forward. If a hook blocks the command, have the user run it directly after review. Do not infer approval from prose.
- Hook text checks cannot see arbitrary later writes inside Python, PowerShell, child processes, or Git hooks. Inspect scripts and use platform sandbox controls where proven effective.

## ExecPlans

The default location for ExecPlans is `docs/<feature-slug>/`.

## Agent Orientation

For read-only questions, reviews, and audits that make no repository edits, start with the requested artifact and load only guidance needed for accurate conclusions. Before any repository edit, complete these applicable reads in order:

1. **Read `.agents/memory/INDEX.md` first** (knowledge base loading map) for authoritative answers before searching the file system.
2. **For every non-trivial task**, read both `.agents/memory/ARCHITECTURE.md` and `.agents/memory/CONVENTIONS.md` before loading task-specific skills or starting task-specific exploration.
3. **Before editing, identify every affected area** and read each `.agents/instructions/<area>.md`, plus matching `.agents/memory/known-issues/<area>.md` and `.agents/memory/testing/<area>.md` files.
4. **At the [end of every _work session_](#end-of-work-session-defined), activate `update-agent-docs` before editing `.agents/` documentation, then complete its workflow.**
   - This is a mandatory step to capture findings, conventions, and architectural changes.
   - **Only run at the end of a _work session_:** Running this multiple times in a single session is expensive and wasteful.

### Memory

`.agents/memory/` is your persistent knowledge base. You may freely create new focused files, update existing ones when you find corrections, and reorganize when structure no longer fits. Use descriptive filenames.

**Memory freshness is your absolute, non-negotiable responsibility.** Documentation drift causes failure:

- **Verify before trust:** Always cross-check memory and instructions against actual code.
- **Immediate repair:** If you find stale docs, fix them in the current task. Do not defer.
- **Immediate logging:** Document any new pattern, surprise, or workaround in `.agents/memory/` immediately.

### Absolute Doc Update Obligation

Every [_work session_](#end-of-work-session-defined) modifying code, directories, configurations, or schemas **must** end with a formal doc pass via the `update-agent-docs` skill. Update:

- **Files added/moved/removed?** → `.agents/memory/FILE_MAP.md` and `.agents/instructions/<area>.md`.
- **Public interface, API, or diagnostic ID changed?** → `.agents/instructions/<area>.md` and `.agents/memory/API_MAP.md`.
- **Surprising quirk/gotcha?** → `.agents/memory/KNOWN_ISSUES.md` (repo-wide) or `.agents/memory/known-issues/<area>.md` (layer-specific).
- **New pattern/formatting/architecture?** → `.agents/memory/CONVENTIONS.md` (repo-wide) or `.agents/instructions/<area>.md` (layer-specific).
- **Test class/location/command changed?** → `.agents/memory/TESTING_STRATEGY.md` (repo-wide) or `.agents/memory/testing/<area>.md` (layer-specific).
- **Memory file added/removed/renamed?** → `.agents/memory/INDEX.md`.

## End of Work Session Defined

You are at the end of a _work session_ when:

- The task within a single task session is complete.
- All tasks within a multi-task session are completed.
- All tasks delegated to subagents have been completed.

## Protected Sections

- Never modify the `## ExecPlans`, `## Agent Orientation`, `## End of Work Session Defined`, or `## Validation Checklist` sections in `AGENTS.md` unless explicitly requested. These sections must remain intact as stable agent entry points.

## Validation Checklist

For a read-only question, review, or audit, load guidance as needed. Before repository edits, complete the checklist:

1. **Read `.agents/memory/INDEX.md`** before editing.
2. **Read core architecture, conventions, and area-scoped instructions** (for non-trivial tasks).
3. **Build modified project(s)** (e.g., `yarn build`).
4. **Run targeted tests** for affected project(s).
5. **Follow existing patterns** in similar files.
6. **Mandatory Doc Pass (No Exceptions):** Run `update-agent-docs` [at the end of the _work session_](#end-of-work-session-defined), perform all Absolute Doc Update Obligation tasks, and commit synchronized `.agents/` docs with your changes.
