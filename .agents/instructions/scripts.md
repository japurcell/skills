---
coverage: Rules and conventions for repository helper scripts under `scripts/` that run in the shell
---

# Shell Scripts Conventions

- Follow existing shebang style for shell helper scripts: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
- Keep scripts directly executable and simple.
- Shell-focused helper scripts should stay in the repo-root `scripts/` tree and use `scripts/common.sh` for shared repo-root helpers that require `REPO_ROOT`.
- Use stdout for primary or machine-readable output and stderr for status, warnings, progress, and errors so piping and redirection stay predictable.
- Prefer standard-library solutions unless an existing script already implies dependency use.
- Register cleanup functions by name (for example, `trap cleanup EXIT`) instead of interpolating temporary paths into trap command strings. Quote the exact `mktemp`-created path and pass `--` to recursive cleanup commands.
- Treat user-facing helper scripts as CLIs: reserve `-h`/`--help` for help, prefer descriptive long flags over multiple positional argument types, and keep interactive prompts optional rather than mandatory.
- Gate decorative terminal behavior on TTY detection; if a script introduces color or spinners, it should also respect `TERM=dumb`, `NO_COLOR`, and a direct opt-out flag.
- **Agent-restricted scripts:** Never run human-only orchestration scripts (such as `import-skill-repos.sh` or `pull-skill-repos.sh`). Agents must strictly run only targeted verification and test scripts (such as `test-*.sh`).
- PowerShell-specific guidance lives in `.agents/instructions/powershell.md`; shell-focused validation lives in `.agents/memory/testing/scripts.md`.
- If the change also affects repo-local hook behavior, read `.agents/instructions/hooks.md` and the matching hook validation docs instead of treating hooks as generic shell scripts.
