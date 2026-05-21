# AGENTS.md

This repository publishes custom coding skills from `skills/`, custom agent definitions from `agents/`, and local Copilot instructions in `.copilot/copilot-instructions.md`.

## Getting Started

- **Install or refresh** locally loaded copies with `./scripts/copilot-install.sh` or `scripts/addy-install.sh`.
- **Run scripts** with `python3`; there is no repo-wide package manifest or single test runner.
- **Install CLI prerequisites**: `bash`, `python3`, `git`, `jq`, and `flock`; hook formatting also needs `npx` (for `oxfmt`) and `dotnet`.
- **Ignore fixture outputs** — treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- **TDD applies to app code AND shell scripts**

## Quick Validation

- Installer changes: `bash -n scripts/copilot-install.sh` and `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- Skill definition changes: `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`
- Hook formatter/audit changes: `bash scripts/test-hooks-format.sh`
- Startup hook context/output changes: `bash scripts/test-hooks-startup.sh`
- After hook source changes, run `./scripts/copilot-install.sh` before live CLI/VS Code validation because hooks execute from `~/.copilot/hooks`.
- Live VS Code startup-hook validation: use the exact session's `exthost*/GitHub.copilot-chat/GitHub Copilot Chat Hooks.log` plus `GitHub Copilot Chat.log`; transcripts alone are not authoritative for `SessionStart` or `SubagentStart` context injection.

## Documentation

- [Repo layout](docs/agent-guides/repo-layout.md) — directory structure and key files
- [Authoring rules](docs/agent-guides/authoring.md) — skill, agent, and script conventions
- [Validation & workflow](docs/agent-guides/validation.md) — targeted validation commands and narrowest checks per area
- [Benchmarking](docs/agent-guides/benchmarking.md) — snapshot, iteration, and grading workflows
