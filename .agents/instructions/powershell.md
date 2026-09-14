---
type: Agent Instruction
description: PowerShell (`pwsh`) rules for installer and validation scripts under `scripts/`
---

# PowerShell Conventions

- Use `#!/usr/bin/env pwsh` for PowerShell helper scripts and keep the repo's pwsh scripts `-NoProfile` compatible.
- PowerShell scripts must use `$HOME` for home-directory targets, avoid external modules, and use `[System.IO.File]::SetUnixFileMode` for executable bits (guarded by `$IsWindows`).
- When a tree copy must mirror `cp -Rp`, use the link-safe path from `scripts/install.ps1`: preserve symbolic links and junctions, copy hard links as regular files, and fail closed on other reparse points. Restore Unix modes explicitly after any `Copy-Item` that needs `cp -p` parity.
- PowerShell matching that must mirror case-sensitive Bash `[[ == pattern ]]` or `find -name` must use explicit case-sensitive primitives (`-ceq`, `-clike`, `.EndsWith`); see `.agents/memory/known-issues/powershell.md` for host-specific quirks.
- `Get-Command -CommandType Application` can return multiple PATH matches. Select one command explicitly before invoking `.Source`; do not let an array stringify into a combined executable path.
- Keep scripts directly executable and simple.
- Prefer standard-library solutions unless an existing script already implies dependency use.
- Treat user-facing helper scripts as CLIs: reserve `-h`/`--help` for help, prefer descriptive long flags over multiple positional argument types, and keep interactive prompts optional rather than mandatory.
- Use stdout for primary or machine-readable output and stderr for status, warnings, progress, and errors so piping and redirection stay predictable.
- Gate decorative terminal behavior on TTY detection; if a script introduces color or spinners, it should also respect `TERM=dumb`, `NO_COLOR`, and a direct opt-out flag.
- Run syntax check plus narrow script validation from `.agents/memory/testing/powershell.md`.

## Scope note

This doc covers `scripts/*.ps1` and PowerShell-specific install/test behavior. Shared shell helper guidance stays in `.agents/instructions/scripts.md`.
