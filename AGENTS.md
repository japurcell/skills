# AGENTS.md

This repository publishes custom coding skills from `skills/`, custom agent definitions from `agents/`, Copilot specific instructions from `.copilot/`, and Gemini specific hooks and configs from `.gemini/`.

## Getting Started

- **Install or refresh** locally loaded copies with `./scripts/install.sh` or `scripts/addy-install.sh`.
- **Validate with the narrowest documented command** in `docs/agent-guides/validation.md`; there is no repo-wide package manifest or single test runner.
- **Install CLI prerequisites** listed in `docs/agent-guides/validation.md` before running hook, installer, or formatter checks.
- **Ignore fixture outputs** — treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- **Ignore fixture AGENTS files** — treat `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` as test fixtures unless the task explicitly targets them.
- **TDD applies to app code AND shell scripts**

## Quick Validation

- Installer changes: `bash -n scripts/install.sh && bash scripts/test-install.sh` and `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- Skill definition changes: `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`; use `docs/agent-guides/validation.md` for any narrower skill-local grader or benchmark checks.
- Hook changes: `docs/agent-guides/validation.md` is the canonical command list and live-validation guide; after changing `.copilot/hooks/` or `.gemini/hooks/`, run `./scripts/install.sh` before checking installed hook behavior.

## Documentation

- [Repo layout](docs/agent-guides/repo-layout.md) — directory structure and key files
- [Hook implementation guidance](docs/agent-guides/hooks.md) - important implementation guidance and references for hooks
- [Authoring rules](docs/agent-guides/authoring.md) — skill, agent, and script conventions
- [Validation & workflow](docs/agent-guides/validation.md) — targeted validation commands and narrowest checks per area
- Keep `README.md` in sync with the linked docs when install, validation, or hook behavior changes.

## Refactor boundaries

- Large-skill refactors follow `docs/agent-guides/authoring.md`; preserve any explicit exclusions or approval requirements documented there.

## ExecPlans

When writing complex features or significant refactors, use an ExecPlan from design to implementation by activating the `exec-plans` skill.

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
