# AGENTS.md

This repository publishes custom coding skills from `skills/`, custom agent definitions from `agents/`, repo-local Copilot hooks from `.github/hooks/`, Copilot-specific instructions from `.copilot/`, and Gemini-specific hooks and configs from `.gemini/`.

## ExecPlans

You MUST activate the `exec-plans` skill and write an ExecPlan before making code changes if the task meets ANY of the following AND there is no existing plan:

1. Touches or creates 3 or more files.
2. Involves multiple distinct milestones or execution phases.
3. Spans different packages or layers.

## Agent Orientation

Before executing tasks or answering questions, you **must**:

1. **Read `.agents/memory/INDEX.md` first** (knowledge base loading map) for authoritative answers before searching the file system.
2. **For non-trivial tasks**, also read `.agents/memory/ARCHITECTURE.md` and `.agents/memory/CONVENTIONS.md`.
3. **Read the area-scoped instruction file** for edited code (`.agents/instructions/<area>.md`, and matching `.agents/memory/known-issues/<area>.md` and `.agents/memory/testing/<area>.md`).
4. **Always run the `update-agent-docs` skill at the end of every task or work session to keep docs fresh.** This is a mandatory step to capture findings, conventions, and architectural changes.

### Memory

`.agents/memory/` is your persistent knowledge base. You may freely create new focused files, update existing ones when you find corrections, and reorganize when structure no longer fits. Use descriptive filenames.

**Memory freshness is your absolute, non-negotiable responsibility.** Documentation drift causes failure:

- **Verify before trust:** Always cross-check memory and instructions against actual code.
- **Immediate repair:** If you find stale docs, fix them in the current task. Do not defer.
- **Immediate logging:** Document any new pattern, surprise, or workaround in `.agents/memory/` immediately.

### Absolute Doc Update Obligation

Every task modifying code, directories, configurations, or schemas **must** end with a formal doc pass via the `update-agent-docs` skill. Update:

- **Files added/moved/removed?** → `.agents/memory/FILE_MAP.md` and `.agents/instructions/<area>.md`.
- **Public interface, API, or diagnostic ID changed?** → `.agents/instructions/<area>.md` and `.agents/memory/API_MAP.md`.
- **Surprising quirk/gotcha?** → `.agents/memory/KNOWN_ISSUES.md` (repo-wide) or `.agents/memory/known-issues/<area>.md` (layer-specific).
- **New pattern/formatting/architecture?** → `.agents/memory/CONVENTIONS.md` (repo-wide) or `.agents/instructions/<area>.md` (layer-specific).
- **Test class/location/command changed?** → `.agents/memory/TESTING_STRATEGY.md` (repo-wide) or `.agents/memory/testing/<area>.md` (layer-specific).
- **Memory file added/removed/renamed?** → `.agents/memory/INDEX.md`.

## Validation Checklist

1. **Read `.agents/memory/INDEX.md`** at start.
2. **Read core architecture, conventions, and area-scoped instructions** (for non-trivial tasks).
3. **Build modified project(s)** (e.g., `yarn build`).
4. **Run targeted tests** for affected project(s).
5. **Follow existing patterns** in similar files.
6. **Mandatory Doc Pass (No Exceptions):** Run `update-agent-docs`, perform all Absolute Doc Update Obligation tasks, and commit synchronized `.agents/` docs with your changes.
