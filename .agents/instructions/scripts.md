---
coverage: Rules and conventions for repository helper scripts under `scripts/`
---

# Scripts Conventions

- Follow existing shebang style: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
- Keep scripts directly executable and simple.
- **Agent-restricted scripts:** Never run human-only orchestration scripts (such as `import-skill-repos.sh` or `pull-skill-repos.sh`). Agents must strictly run only targeted verification and test scripts (such as `test-*.sh`).
- Prefer standard-library solutions unless an existing script already implies dependency use.
- Treat user-facing helper scripts as CLIs: reserve `-h`/`--help` for help, prefer descriptive long flags over multiple positional argument types, and keep interactive prompts optional rather than mandatory.
- Use stdout for primary or machine-readable output and stderr for status, warnings, progress, and errors so piping and redirection stay predictable.
- Gate decorative terminal behavior on TTY detection; if a script introduces color or spinners, it should also respect `TERM=dumb`, `NO_COLOR`, and a direct opt-out flag.
- Use `scripts/common.sh` as shared repo-root helper for shell tests and other small shell utilities that need `REPO_ROOT`.
- Run syntax check plus narrow script validation from `.agents/memory/testing/scripts.md`.
