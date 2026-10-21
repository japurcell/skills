# PowerShell installer rules

## Authoring and copy parity

- For `scripts/*.ps1`, use `#!/usr/bin/env pwsh`, keep `-NoProfile` compatibility, use `$HOME` for home targets, and avoid external modules. Apply shared [CLI/stream/dependency/terminal conventions](scripts-and-installers.md).
- Set executable bits with `[System.IO.File]::SetUnixFileMode` only off Windows, guarded by `$IsWindows`.
- For `cp -Rp` parity use [install.ps1](../../scripts/install.ps1)'s link-safe copier: preserve source symlinks/junctions as links without reading targets, materialize hard links as regular files, and fail closed on other reparse points. Restore Unix modes explicitly after `Copy-Item` where `cp -p` parity is required.
- Source-link preservation does not permit linked configuration destinations or parents; apply [installer preflight/privacy rules](scripts-and-installers.md#registry-and-installation-invariants).
- For exact flags, environment values, filenames, and suffixes use `StringComparison.Ordinal`; use `OrdinalIgnoreCase` only when the interface permits case variation. Keep genuine glob matching explicitly case-sensitive. `-ceq`/`-ieq` and default `.EndsWith` are linguistic comparisons and can ignore invisible characters, so they do not enforce Bash literal parity.
- Resolve one `Get-Command -CommandType Application` result before invoking `.Source`; do not stringify several PATH matches as one executable path.
- Run Codex agent conversion before provider copying; select `$env:CODEX_HOME/agents` when set, otherwise `$HOME/.codex/agents`.
- Check link identity before directory identity in mode walkers; preserve original modes before hook chmod. Use literal-path reads/writes for names containing wildcard characters.

## Fixture isolation and verification

- Before starting fixture `pwsh`, isolate `HOME`, `USERPROFILE`, `APPDATA`, and `LOCALAPPDATA` inside the disposable home. RTK on Windows follows `APPDATA`; `HOME` alone is insufficient. Use `Invoke-InstallProcess` in [test-install.ps1](../../scripts/test-install.ps1) and restore the process environment in `finally`.
- Run syntax checks plus the narrow script suite. For installer changes use `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`, covering excludes/pruning, full Gemini tree copy, link handling, freshness, missing-source stderr, and exact non-Windows modes.
- Preserve old/custom hook entries and nested Gemini settings; cover fresh absence, second-install idempotence, malformed/ambiguous JSON, hard-linked config safety, and linked-parent refusal before any mutation. Use POSIX symlinks and native Windows junctions when supported. See [installer fixture acceptance](installer-testing.md).
- Codex cases decode TOML and cover conversion before copies, exact instructions, managed cleanup, idempotence, malformed-source early failure, `CODEX_HOME`, and replacement of global `.codex/AGENTS.md` from repository `.codex/AGENTS.md`.
- `Test-JunctionHandling` can skip when junction creation is unavailable; obtain Windows-capable follow-up for junction proof. Native Windows is required for junction, ACL, job-object, and cmd/PowerShell quoting evidence; non-Windows skips prove none of those. Emulated Unix mode bits do not prove NTFS access control: keep POSIX assertions on POSIX and inspect ACLs for access-control tests.
- RTK native proof uses `rtk proxy pwsh -NoProfile -File scripts/test-rtk-stable-windows.ps1` in the [dedicated Windows workflow](../../.github/workflows/ready-ideas-windows.yml), with real stable RTK 0.50.0+ on `PATH`. Cover old-version preflight, `%APPDATA%` TOML, backup/idempotence, and actual `copilot`/`gemini` processor diagnostics. The repository installer does not install RTK; the workflow installs official `rtk-ai.rtk` using winget.
- Apply [shared script fixtures](script-testing.md), [hook tests](hook-testing.md), and the owning skill's validation as applicable. Native scanner capture requirements belong in [security testing](security-testing.md).

Evidence: restored PowerShell policy from `.agents/instructions/powershell.md` and `testing/powershell.md` at `092038394a2e3bb0cc21fffdec2eb60a12cece29`; source/contracts checked in linked installer, fixtures, and workflow on 2026-10-21. This is inspection, not a native Windows run. Recheck on copier, comparison, environment, preflight, or platform changes.

Comparison authority (PowerShell 7, no exact deployed minor asserted): [PowerShell comparison operators](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_comparison_operators?view=powershell-7.6) and [.NET string comparison guidance](https://learn.microsoft.com/en-us/dotnet/standard/base-types/best-practices-strings), checked 2026-10-21; these explain linguistic versus ordinal comparison, while local invisible-character fixtures establish the repository contract. Recheck when runtime/globalization behavior changes.
