# Validation commands

This document is the canonical source for targeted validation commands and live-validation references.

There is no single repo-wide test command. Run the narrowest command that exercises the area you changed.

## CLI prerequisites

- Base commands in this repo assume `bash`, `python3`, and `git` are available.
- Hook scripts require `jq` and `flock`.
- Hook formatting paths require `npx` (with `oxfmt`) for JS/TS and `dotnet` for C#.
- For interactive agent terminal work, prefer wrapping commands with `rtk`.

## Installer scripts

- `./scripts/install.sh`: refresh installed skills, references, hooks, agents, Gemini instructions, and Copilot instructions after editing repo source and before checking live model behavior
- `bash -n scripts/install.sh && bash scripts/test-install.sh`: syntax-check and exercise the local installer, including recursive Gemini copying and dual Gemini/Copilot agent installation
- `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`: syntax-check and exercise the addy importer, including upstream sync, dependency-copying, and reference-copying behavior

## Skill validation and packaging

- `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`: validate a skill definition
- `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`: package a skill into a `.skill` archive

## Other targeted checks

- `bash skills/agent-sop-author/validate-sop.sh path/to/file.sop.md`: validate an Agent SOP file
- `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py`: syntax-check a skill-local Python benchmark grader after editing it
- `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>`: grade benchmark-style eval artifacts when a skill ships a local `grade_benchmark.py` helper
- `bash scripts/test-hooks-format.sh`: validate Copilot hook audit logging (including passive-log default + additive shadow mode), rollover, and locking behavior
- `bash scripts/test-hooks-startup.sh`: validate startup hook context emission across Copilot CLI and VS Code payload schemas, including direct `SubagentStart` registration
- `bash scripts/test-hooks-secrets-scanner.sh`: validate Copilot `sessionEnd` secrets scanning detects diff secrets, respects block mode, and is wired in `.copilot/hooks/hooks.json`
- `bash scripts/test-hooks-tool-guard.sh`: validate `preToolUse` guard output stays JSON-safe while handling both Copilot CLI and VS Code payload schemas
- `bash scripts/test-gemini-hooks-startup.sh`: validate Gemini startup/context injection payloads, including caveman-only required-skill loading
- `bash scripts/test-gemini-hooks-tool-guard.sh`: validate Gemini `BeforeTool` guard output stays JSON-safe and is wired in `.gemini/settings.json`
- `bash scripts/test-gemini-hooks-secrets-scanner.sh`: validate Gemini `SessionEnd` secrets scanning logs env-file access, detects credential paths and token-shaped secrets, and is wired in `.gemini/settings.json`
- `bash scripts/test-gemini-hooks-format.sh`: validate Gemini passive-log mode defaults plus additive shadow-log behavior
- `bash scripts/test-gemini-hooks-rtk.sh`: validate Gemini `BeforeTool` RTK rewrite hook degrades to JSON-safe no-op behavior on invalid input or rewrite failure and remains wired in `.gemini/settings.json`

## Cross-surface live hook validation contracts

- Hook source changes: run `./scripts/install.sh` before live validation; Copilot CLI and VS Code execute installed hooks from `~/.copilot/hooks`, and Gemini CLI executes installed hooks from `~/.gemini/hooks`, not repository source files.
- Required-skill injection coverage:
  - Copilot surfaces: `bash scripts/test-hooks-startup.sh`
  - Gemini CLI: `bash scripts/test-gemini-hooks-startup.sh`
- Passive-log mode coverage:
  - Copilot surfaces: `bash scripts/test-hooks-format.sh`
  - Gemini CLI: `bash scripts/test-gemini-hooks-format.sh`
- Hook event compatibility contract lives in `docs/agent-guides/hooks.md` (canonical); keep this guide focused on validation commands and live-debug evidence.

### Copilot CLI live evidence

- Launch a no-op `task` subagent if needed, then verify `~/.copilot/hooks/audit.log` contains `[subagent-start.sh]` and `[log-subagent-stop.sh]`.
- Smoke-test installed CLI schema with `~/.copilot/hooks/scripts/subagent-start.sh`; expect top-level `additionalContext`.

### VS Code Copilot live evidence

- Inspect matching `exthost*/GitHub.copilot-chat/GitHub Copilot Chat Hooks.log` for returned `SessionStart`/`SubagentStart` hook JSON.
- Confirm `GitHub Copilot Chat.log` records `SessionStart hook provided context for session` or `SubagentStart hook provided context for subagent ...`.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.

### Gemini CLI live evidence

- Run Gemini targeted checks first (`bash scripts/test-gemini-hooks-startup.sh` and `bash scripts/test-gemini-hooks-format.sh`).
- Verify installed Gemini hook behavior from `~/.gemini/hooks` audit output/log targets configured by the affected script paths.

## Workflow

- If you change a helper script, run the most specific command that covers that script instead of looking for a nonexistent monorepo test runner.
- `scripts/test-common.sh` `mock_bin` must keep `printf "%b\n"` so escaped newlines render into executable mock scripts.
- Static review findings based on file inspection or sub-review output, without live reproduction, must be labeled likely/candidate and include `Evidence:` plus `Uncertainty:` grounded in inspected files, tool outputs, and remaining assumptions.
- If asked to strengthen certainty or add evidence, gather at least one new concrete artifact first (for example a targeted `rg`, exact `view`, or narrower validation command). If no new artifact exists, say that directly instead of rewriting same claim with stronger wording.
- Distinguish repo-source proof from installed/live proof. File reads and repo-local tests only prove repository state; installed hook behavior still requires `./scripts/install.sh` plus the live-evidence checks above.
- To prove a mode or branch is gone, prefer one targeted search over repeated full-file rereads or rerunning same validation loop.
