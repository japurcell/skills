---
coverage: Test guidance for `{.copilot,.gemini}/hooks`.
---

# Hooks - Testing

## Repo checks

- After changing hook source, run `./scripts/install.sh` before any live validation because installed hooks execute from `~/.copilot/hooks` or `~/.gemini/hooks`, not from repo source paths.
- Read official hook docs before non-trivial changes and keep implementation aligned with them.
- Copilot hook checks:
  - `bash scripts/test-hooks-format.sh`
  - `bash scripts/test-hooks-startup.sh`
  - `bash scripts/test-hooks-secrets-scanner.sh`
  - `bash scripts/test-hooks-tool-guard.sh`
- Gemini hook checks:
  - `bash scripts/test-gemini-hooks-format.sh`
  - `bash scripts/test-gemini-hooks-startup.sh`
  - `bash scripts/test-gemini-hooks-secrets-scanner.sh`
  - `bash scripts/test-gemini-hooks-tool-guard.sh`
  - `bash scripts/test-gemini-hooks-rtk.sh`

## Live evidence

- Copilot CLI: verify installed behavior from `~/.copilot/hooks/audit.log` or direct installed-script smoke tests.
- VS Code Copilot: inspect `GitHub Copilot Chat Hooks.log` and `GitHub Copilot Chat.log` for returned hook JSON and applied context.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.
- `scripts/test-hooks-startup.sh` now exercises the Python startup entrypoint directly; keep the shell wrapper as the installed compatibility shim.
- Gemini CLI: verify installed behavior from `~/.gemini/hooks` logs or configured audit targets.
- Hook event compatibility contract lives in `.agents/instructions/hooks.md`.
