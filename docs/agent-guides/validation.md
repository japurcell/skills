# Validation commands

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
- `bash scripts/test-hooks-format.sh`: validate hook audit logging, rollover, and locking behavior
- `bash scripts/test-hooks-startup.sh`: validate startup hook context emission across Copilot CLI and VS Code payload schemas, including direct `SubagentStart` registration
- Hook source changes: run `./scripts/install.sh` before live validation; Copilot CLI and VS Code execute installed hooks from `~/.copilot/hooks`, not repository source files.
- Hook event compatibility: keep CLI camelCase `subagentStart` and VS Code PascalCase `SubagentStart`; CLI returns top-level `additionalContext`, while VS Code returns `hookSpecificOutput.hookEventName` plus `additionalContext`.
- Live VS Code hook debugging: inspect the matching `exthost*/GitHub.copilot-chat/GitHub Copilot Chat Hooks.log` for returned `SessionStart`/`SubagentStart` hook JSON, then confirm `GitHub Copilot Chat.log` records `SessionStart hook provided context for session` or `SubagentStart hook provided context for subagent ...`.
- Live Copilot CLI hook debugging: launch a no-op `task` subagent if needed, then verify `~/.copilot/hooks/audit.log` contains `[subagent-start.sh]` and `[log-subagent-stop.sh]`; smoke-test installed CLI schema with `~/.copilot/hooks/scripts/subagent-start.sh` returning top-level `additionalContext`.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.

## Workflow

- If you change a helper script, run the most specific command that covers that script instead of looking for a nonexistent monorepo test runner.
