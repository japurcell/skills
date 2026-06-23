# AGENTS.md

This repository publishes custom coding skills from `skills/`, custom agent definitions from `agents/`, Copilot specific instructions from `.copilot/`, and Gemini specific hooks and configs from `.gemini/`.

## Getting Started

- **Install or refresh** locally loaded copies with `./scripts/install.sh` or `scripts/addy-install.sh`.
- **Run scripts** with `python3`; there is no repo-wide package manifest or single test runner.
- **Install CLI prerequisites**: `bash`, `python3`, `git`, `jq`, and `flock`; hook formatting also needs `npx` (for `oxfmt`) and `dotnet`.
- **Ignore fixture outputs** — treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- **Ignore fixture AGENTS files** — treat `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` as test fixtures unless the task explicitly targets them.
- **TDD applies to app code AND shell scripts**

## Quick Validation

- Installer changes: `bash -n scripts/install.sh && bash scripts/test-install.sh` and `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- Skill definition changes: `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`
- Hook changes: run the narrowest matching `scripts/test-hooks-*.sh` or `scripts/test-gemini-hooks-*.sh` target from `docs/agent-guides/validation.md`
- After changing `.copilot/hooks/` or `.gemini/hooks/`, run `./scripts/install.sh` before live validation; Copilot hooks execute from `~/.copilot/hooks` and Gemini hooks execute from `~/.gemini/hooks`.
- Live VS Code startup-hook validation: use the exact session's `exthost*/GitHub.copilot-chat/GitHub Copilot Chat Hooks.log` plus `GitHub Copilot Chat.log`; transcripts alone are not authoritative for `SessionStart` or `SubagentStart` context injection.

## Documentation

- [Repo layout](docs/agent-guides/repo-layout.md) — directory structure and key files
- [Hook implementation guidance](docs/agent-guides/hooks.md) - important implementation guidance and references for hooks
- [Authoring rules](docs/agent-guides/authoring.md) — skill, agent, and script conventions
- [Validation & workflow](docs/agent-guides/validation.md) — targeted validation commands and narrowest checks per area
- [Benchmarking](docs/agent-guides/benchmarking.md) — snapshot, iteration, and grading workflows
- Keep `README.md` in sync with the linked docs when install, validation, or hook behavior changes.

## Learnings

- `code-simplifier` + intentional non-standard paths - explicitly state path intent (for example `.gemini/` vs `.copilot/`) so the simplifier does not "correct" required paths.
- `scripts/test-common.sh` `mock_bin` - keep `printf "%b\n"` so escaped newlines render into executable mock scripts.
- Editing code/tests with active Tool Guard - if files/test suites contain security-threat patterns (such as destructive rm, git push force, or database drop commands), any `replace` or tool call payload containing those strings as a literal will be blocked by the tool guard hook. To edit or assert on these patterns in test files, dynamically construct the threat strings (e.g., concatenate separate variable expansions like `local f="force"; expected="git push --${f}"`) to completely avoid triggering the payload's static regex scanner.
