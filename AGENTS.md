# AGENTS.md

This repository publishes custom coding skills from `skills/` and custom agent definitions from `agents/`.

## Essentials

- Install or refresh the locally loaded copies with `./scripts/copilot-install.sh`.
- Run helper scripts with `python3`; there is no repo-wide package manifest or single test runner.
- Edit repository source first, then rerun `./scripts/copilot-install.sh` before live model spot checks so `~/.agents/skills` and `~/.copilot/agents` reflect the repo changes.
- Ignore `skills/*-workspace/**/outputs/` during normal audits and edits; those files are benchmark fixtures, not maintained source.

## Guides

- [Repo layout](docs/agent-guides/repo-layout.md)
- [Authoring rules](docs/agent-guides/authoring.md)
- [Validation commands](docs/agent-guides/validation.md)
