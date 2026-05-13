# AGENTS.md

This repository publishes custom coding skills from `skills/` and custom agent definitions from `agents/`.

## Getting Started

- **Install or refresh** locally loaded copies with `./scripts/copilot-install.sh` or `scripts/addy-install.sh`.
- **Run scripts** with `python3`; there is no repo-wide package manifest or single test runner.
- **Refresh after edits** by rerunning the install script so installed skills, references, hooks, agents, and Copilot instructions reflect your changes.
- **Hook scripts** should resolve repo-relative paths from `BASH_SOURCE[0]`; don't rely on the installed hook `cwd`.
- **postToolUse hooks** should read camelCase `toolName`/`toolArgs` first and keep snake_case fallbacks only for compatibility.
- **read_agent** hook inputs may use `agentId` or `agent_id`; accept both when recovering subagent file paths.
- **Task `postToolUse` hooks** must inspect `$COPILOT_HOME/session-state/<session>/events.jsonl` to recover subagent `create`/`edit`/`apply_patch` file paths; child tool calls are not emitted to hooks separately.
- **Shared hook logs** should use `flock` plus explicit rollover thresholds to stay safe under concurrent sessions.
- **Hook formatter failures** should append a failure line to `audit.log` before the hook exits.
- **Ignore fixture outputs** — treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- **TDD applies to app code AND shell scripts**

## Documentation

- [Repo layout](docs/agent-guides/repo-layout.md) — directory structure and key files
- [Authoring rules](docs/agent-guides/authoring.md) — skill, agent, and script conventions
- [Validation & workflow](docs/agent-guides/validation.md) — targeted validation commands and narrowest checks per area
- [Benchmarking](docs/agent-guides/benchmarking.md) — snapshot, iteration, and grading workflows
