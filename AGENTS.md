# AGENTS.md

This repository publishes custom coding skills from `skills/` and custom agent definitions from `agents/`.

## Getting Started

- **Install or refresh** locally loaded copies with `./scripts/copilot-install.sh` or `scripts/addy-install.sh`.
- **Run scripts** with `python3`; there is no repo-wide package manifest or single test runner.
- **Refresh after edits** by rerunning the install script so installed skills, references, hooks, agents, and Copilot instructions reflect your changes.
- **Ignore fixture outputs** — treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- **TDD applies to app code AND shell scripts**

## Documentation

- [Repo layout](docs/agent-guides/repo-layout.md) — directory structure and key files
- [Authoring rules](docs/agent-guides/authoring.md) — skill, agent, and script conventions
- [Validation & workflow](docs/agent-guides/validation.md) — targeted validation commands and narrowest checks per area
- [Benchmarking](docs/agent-guides/benchmarking.md) — snapshot, iteration, and grading workflows
