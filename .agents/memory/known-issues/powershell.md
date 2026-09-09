---
type: Known Issue
description: PowerShell (`pwsh`) gotchas hit while writing `scripts/install.ps1` and `scripts/test-install.ps1`
---

# PowerShell - Known Issues

- The PS7 automatic `$HOME` is fixed at process start. Setting `$env:HOME` inside a running pwsh session does not change `$HOME`, so tests cannot redirect the installer's home in-session. Redirect by setting the `HOME` (and `USERPROFILE`, for Windows) environment variable for the child process before launch.
- In pwsh 7.4+, `$env:HOME` is read-only; assign via `[System.Environment]::SetEnvironmentVariable('HOME', $dir, [System.EnvironmentVariableTarget]::Process)` in a try/finally that restores the original (`scripts/test-install.ps1` `Invoke-InstallProcess` shows the pattern).
- `Set-Item -UnixFileMode` does not exist in pwsh 7.6.5. Use `[System.IO.File]::SetUnixFileMode(path, mode)`; flag names are `UserRead`, `UserWrite`, `UserExecute`, `GroupRead`, `GroupExecute`, `OtherRead`, `OtherExecute`.
- The parse-check one-liner `[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$null, [ref]$null)` throws on pwsh 7.6.5 (`PSReference` to null cannot convert to `ParseError[]`). Use untyped variables: `$t=$null; $e=$null; ... ParseFile($path, [ref]$t, [ref]$e)`.
- `Copy-Item -Recurse -Force` does not preserve Unix file modes and also follows symlinks. The installer therefore restores modes explicitly and uses a link-safe tree copy that preserves links, copies hard links as regular files, and fails closed on other reparse data.
- PowerShell link handling (verified on pwsh 7.6.5, Linux): `Get-Item`/`Get-ChildItem` expose `.LinkType` and `.Target`; check `LinkType` before `PSIsContainer`, and skip non-empty `LinkType` entries in mode walkers.
- GNU `grep -R` follows symlinks by default, so `grep -R <needle> <tree>` false-positives through preserved symlinks when proving "no regular file under the tree contains X"; use `find <tree> -type f -exec grep -l <needle> {} +` instead.
- Mode preservation in `scripts/install.ps1` applies to files only, walks the source tree, and runs before hook chmod so the explicit hook mode wins.
- Case-sensitivity on this host's pwsh 7.6.5 is case-insensitive by default for string `-eq`/`-contains`/`-like`; use explicit case-sensitive primitives when matching Bash semantics.
- `New-Item` has no `-LiteralPath` parameter; its `-Path` creates the target name literally (including `[ ]` in the name), so literal-path discipline is needed only on the read/write side (`Test-Path -LiteralPath`, `Get-Content -LiteralPath`, `Set-Content -LiteralPath`).
