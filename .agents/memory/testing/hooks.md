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
- `scripts/test-hooks-tool-guard.sh` exercises `.copilot/hooks/scripts/tool-guard.py` directly; keep the shell wrapper as the installed compatibility shim.
- `scripts/test-hooks-rtk.sh` exercises `.copilot/hooks/scripts/rtk-hook-copilot.py` directly; keep `.copilot/hooks/rtk-rewrite.json` pointed at the Python wrapper and cover payload forwarding plus no-op fallback for invalid input, non-zero exits, and timeouts.
- `scripts/test-hooks-format.sh` exercises the Copilot lifecycle logging Python entrypoints directly (`log-agent-stop.py`, `log-error-occurred.py`, `log-notification.py`, `log-tooluse-failure.py`, and `log-subagent-stop.py`); keep the shell wrappers as installed compatibility shims.
- `scripts/test-hooks-secrets-scanner.sh` exercises `.copilot/hooks/scripts/scan-secrets.py` directly; keep the session-end `bell.py` and `log-session-end.py` entries in `hooks.json` and cover diff-only secret scanning, unchanged-secret suppression, and secret-like diff header paths.
- `.copilot/hooks/hooks.json` should point at the Python entrypoints for retained Copilot operational hooks; keep the shell scripts only as compatibility shims.
- `scripts/test-gemini-hooks-startup.sh` now exercises the Python startup entrypoint directly; keep the shell wrapper as the installed compatibility shim.
- `scripts/test-gemini-hooks-format.sh` should validate the Python passive logging hooks (`log-after-agent.py` and `log-notification.py`) plus the Python startup hooks as the implementation source and keep the thin shell wrappers as compatibility shims.
- `scripts/test-gemini-hooks-tool-guard.sh` exercises the Gemini tool-guard path through the installed shell shim; keep `.gemini/hooks/scripts/tool-guard.py` as the implementation source and `.gemini/hooks/scripts/tool-guard.sh` as the compatibility wrapper.
- `scripts/test-gemini-hooks-rtk.sh` exercises the Gemini RTK rewrite shell entrypoint; keep `.gemini/hooks/scripts/rtk-hook-gemini.sh` pointed at the inline Python implementation and cover invalid input plus rewrite-failure no-op fallback.
- `scripts/test-gemini-hooks-secrets-scanner.sh` exercises `.gemini/hooks/scripts/scan-secrets.py` directly; keep `.gemini/hooks/scripts/log-session-end.py` in sync with the shell compatibility shim and cover diff-only secret scanning, unchanged-secret suppression, and secret-like unified-diff header paths.
- Gemini CLI: verify installed behavior from `~/.gemini/hooks` logs or configured audit targets.
- Hook event compatibility contract lives in `.agents/instructions/hooks.md`.
