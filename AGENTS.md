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
- [Benchmarking](docs/agent-guides/benchmarking.md) — snapshot, iteration, and grading workflows
- Keep `README.md` in sync with the linked docs when install, validation, or hook behavior changes.

## Refactor boundaries

- Large-skill refactors follow `docs/agent-guides/authoring.md`; preserve any explicit exclusions or approval requirements documented there.
