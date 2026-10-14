---
type: Agent Instruction
description: PowerShell (`pwsh`) rules for installer and validation scripts under `scripts/`
---

# PowerShell Conventions

- Use `#!/usr/bin/env pwsh` for PowerShell helper scripts and keep the repo's pwsh scripts `-NoProfile` compatible.
- PowerShell scripts must use `$HOME` for home-directory targets, avoid external modules, and use `[System.IO.File]::SetUnixFileMode` for executable bits (guarded by `$IsWindows`).
- When a tree copy must mirror `cp -Rp`, use the link-safe path from `scripts/install.ps1`: preserve symbolic links and junctions, copy hard links as regular files, and fail closed on other reparse points. Restore Unix modes explicitly after any `Copy-Item` that needs `cp -p` parity.
- Match literal external flags, environment values, filenames, and suffixes with `StringComparison.Ordinal`; use `OrdinalIgnoreCase` only where the interface permits case variation. PowerShell `-ceq`/`-ieq` and default `.EndsWith` comparisons are linguistic and can ignore invisible characters, so they do not enforce Bash literal parity. Keep genuine glob matching explicitly case-sensitive. The [installer fixtures](../../scripts/test-install.ps1) cover invisible-character inputs, exclusions, and hook-extension modes.
- `Get-Command -CommandType Application` can return multiple PATH matches. Select one command explicitly before invoking `.Source`; do not let an array stringify into a combined executable path.
- Keep Codex custom-agent installation equivalent to Bash: invoke `install-codex-agents.py` before provider copy operations and resolve `$env:CODEX_HOME/agents` when set, otherwise `$HOME/.codex/agents`.
- Run syntax check plus narrow script validation from `.agents/instructions/testing/powershell.md`.

## Scope note

This doc covers `scripts/*.ps1` and PowerShell-specific install/test behavior. Apply shared CLI, stream, dependency, executable, and terminal rules from [Shell Scripts Conventions](scripts.md).

For installer fixtures, establish `HOME`, `USERPROFILE`, `APPDATA`, and `LOCALAPPDATA` inside the disposable home before launching `pwsh`; use `Invoke-InstallProcess` in `scripts/test-install.ps1` as the maintained pattern. Windows RTK configuration follows `APPDATA`, so isolating only `HOME` does not isolate those writes. Keep environment restoration in `finally`. Check link identity before directory identity in mode walkers, preserve file modes before hook chmod, and use literal-path reads/writes for names containing wildcard characters.
