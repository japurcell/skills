# Copilot hooks

- `.copilot/hooks` supplies user-level hooks; `.github/hooks` supplies repository hooks. Brain hooks belong only in `.github/hooks`.
- CLI hooks combine user and project configuration; cloud agent reads `.github/hooks/*.json` in its Linux sandbox.
- `sessionStart` receives `cwd` and startup/resume/new source; return top-level `additionalContext`.
- `postToolUse` carries successful `toolResult.resultType`; failure has a separate event. PascalCase compatibility uses snake_case payloads.
- Use `bash` and `powershell` launch commands; cloud honors POSIX commands. `timeoutSec` is seconds.
- CLI progress output and VS Code compatibility differ. Use final provider JSON and verify user-visible delivery separately.
- Command pre-tool errors deny tools, but timeouts fail open; do not treat all command failures as equivalent.
- Preserve stop-loop guards in validators. Keep diagnostic stdout separate from protocol output.

Source: [official hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference), checked 2026-10-20. CLI 1.0.100 is installed; no live brain delivery is proven. Recheck after provider changes. See [hooks-vscode](hooks-vscode.md) for cross-client limits.
