#!/usr/bin/env pwsh
#Requires -Version 7.0
<#
.SYNOPSIS
    Installs repo skills, agents, references, hooks, and Gemini/Copilot configs into the user home.

.DESCRIPTION
    PowerShell 7 port of scripts/install.sh. Produces the same installed layout:

    - skills/*                        -> ~/.agents/skills (skips *-workspace and archive; prunes evals/, README.md, and LICENSE.* from each installed skill)

    Source Unix file modes are preserved on every copied file (like `cp -p`); on Windows the
    executable bit does not apply and mode handling is a no-op. Symlinks and junctions are
    preserved as link objects and never followed (like `cp -Rp`); hard links are copied as
    regular files; any other reparse point fails the install with a stderr diagnostic and
    exit code 1.
    - agents/*                        -> ~/.gemini/agents and ~/.copilot/agents
    - references/*                    -> ~/.agents/references (optional)
    - .copilot/hooks/*                -> ~/.copilot/hooks (optional; hook scripts made executable on non-Windows)
    - .gemini/*                       -> ~/.gemini (hook scripts made executable on non-Windows)
    - .gemini/global-settings.json    -> ~/.gemini/settings.json
    - .copilot/copilot-instructions.md -> ~/.copilot/copilot-instructions.md
    - .copilot/lsp-config.json        -> ~/.copilot/lsp-config.json

    Requires PowerShell 7+ and runs with -NoProfile; no external modules are used.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SkillsSrc = Join-Path $RepoRoot 'skills'
$AgentsSrc = Join-Path $RepoRoot 'agents'
$ReferencesSrc = Join-Path $RepoRoot 'references'
$HooksSrc = Join-Path $RepoRoot '.copilot/hooks'
$GeminiSrc = Join-Path $RepoRoot '.gemini'
$GeminiGlobalSettingsSrc = Join-Path $RepoRoot '.gemini/global-settings.json'
$CopilotInstructionsSrc = Join-Path $RepoRoot '.copilot/copilot-instructions.md'
$CopilotLspSrc = Join-Path $RepoRoot '.copilot/lsp-config.json'
$CodexHookSrc = Join-Path $RepoRoot '.codex/hooks/load-required-skills.py'
$CodexHookTemplateSrc = Join-Path $RepoRoot '.codex/global-hooks.json'
$CodexHookMergerSrc = Join-Path $RepoRoot 'scripts/install-codex-hooks.py'
$CodexAgentInstallerSrc = Join-Path $RepoRoot 'scripts/install-codex-agents.py'

$SkillsDest = Join-Path $HOME '.agents/skills'
$ReferencesDest = Join-Path $HOME '.agents/references'
$GeminiDest = Join-Path $HOME '.gemini'
$CopilotDest = Join-Path $HOME '.copilot'
$AgentsDest = Join-Path $GeminiDest 'agents'
$CopilotAgentsDest = Join-Path $CopilotDest 'agents'
$HooksDest = Join-Path $CopilotDest 'hooks'
$CodexDest = Join-Path $HOME '.codex'
$CodexHooksDest = Join-Path $CodexDest 'hooks'
$CodexHookConfigDest = Join-Path $CodexDest 'hooks.json'
$CodexAgentsDest = Join-Path $(if ([string]::IsNullOrEmpty($env:CODEX_HOME)) { $CodexDest } else { $env:CODEX_HOME }) 'agents'

function Fail {
    param([string]$Message)

    [Console]::Error.WriteLine($Message)
    exit 1
}

function Get-PythonCommand {
    $python = @(Get-Command python3 -CommandType Application -ErrorAction SilentlyContinue)[0]
    $arguments = @()
    if ($null -eq $python) {
        $python = @(Get-Command py -CommandType Application -ErrorAction SilentlyContinue)[0]
        $arguments = @('-3')
    }
    if ($null -eq $python) {
        Fail 'Missing Python executable: expected python3 or py.'
    }
    return [pscustomobject]@{
        Path = $python.Source
        Arguments = $arguments
    }
}

# Recreates a preserved link object at $Destination without following it.
function Install-PreservedLink {
    param(
        [string]$SourceDescription,
        [string]$Destination,
        [string]$LinkType,
        $Target
    )

    if ($null -eq $Target -or $Target -isnot [string]) {
        Fail "Refusing to follow reparse point with unreadable target data during install: $SourceDescription."
    }

    try {
        New-Item -ItemType $LinkType -Path $Destination -Target $Target -Force | Out-Null
    }
    catch {
        Fail "Cannot recreate the link during install; refusing to follow it: $SourceDescription ($($_.Exception.Message))."
    }
}

# Copies a regular file while preserving its Unix file mode.
function Copy-FileWithMode {
    param(
        [string]$Source,
        [string]$Destination
    )

    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    Set-FileModeFrom -Source $Source -Destination $Destination
}

# Copies one source entry into $DestinationDir, mirroring `cp -Rp`: symlinks and junctions
# are preserved as link objects without reading their targets; hard links are copied as
# regular files; unsupported reparse points fail closed. Never calls Copy-Item on a link.
function Copy-Entry {
    param(
        $Entry,
        [string]$DestinationDir
    )

    # LinkType must be checked before PSIsContainer: a symlink to a directory reports PSIsContainer = $true.
    $linkType = [string]$Entry.LinkType
    if ($linkType -ceq 'SymbolicLink') {
        Install-PreservedLink -SourceDescription $Entry.FullName -Destination (Join-Path $DestinationDir $Entry.Name) -LinkType $linkType -Target $Entry.Target
        return
    }
    if ($linkType -ceq 'Junction') {
        Install-PreservedLink -SourceDescription $Entry.FullName -Destination (Join-Path $DestinationDir $Entry.Name) -LinkType $linkType -Target $Entry.Target
        return
    }
    if ($linkType -ceq 'HardLink') {
        # cp -Rp copies a hard link as a regular file.
        Copy-FileWithMode -Source $Entry.FullName -Destination (Join-Path $DestinationDir $Entry.Name)
        return
    }
    if ($linkType) {
        Fail "Refusing to follow unsupported reparse point during install: $($Entry.FullName) (type: $linkType)."
    }
    if ($Entry.PSIsContainer) {
        $destPath = Join-Path $DestinationDir $Entry.Name
        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        Copy-DirectoryContents -Source $Entry.FullName -Destination $destPath
        return
    }
    Copy-Item -LiteralPath $Entry.FullName -Destination (Join-Path $DestinationDir $Entry.Name) -Force
    Set-FileModeFrom -Source $Entry.FullName -Destination (Join-Path $DestinationDir $Entry.Name)
}

function Copy-DirectoryContents {
    param(
        [string]$Source,
        [string]$Destination
    )

    # -Force so hidden entries (e.g. .gemini/.hidden-note) are copied, mirroring `cp -Rp src/. dest/`.
    Get-ChildItem -Force -Path $Source | ForEach-Object {
        Copy-Entry -Entry $_ -DestinationDir $Destination
    }
}

function Remove-IfExists {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Set-HookScriptsExecutable {
    param([string]$Root)

    if ($IsWindows -or -not (Test-Path -LiteralPath $Root)) {
        return
    }

    # Mirrors `find <root> -type f \( -name "*.py" -o -name "*.sh" \) -exec chmod 755 {} +`.
    # -ceq is explicitly case-sensitive (like `find -name`): `test.PY` is not a hook script.
    # Link entries are skipped: chmod through a reparse point would change the target's mode.
    Get-ChildItem -Force -Path $Root -Recurse -File |
        Where-Object { -not $_.LinkType -and ($_.Extension -ceq '.py' -or $_.Extension -ceq '.sh') } |
        ForEach-Object {
            $mode = [System.IO.UnixFileMode]::UserRead -bor
                [System.IO.UnixFileMode]::UserWrite -bor
                [System.IO.UnixFileMode]::UserExecute -bor
                [System.IO.UnixFileMode]::GroupRead -bor
                [System.IO.UnixFileMode]::GroupExecute -bor
                [System.IO.UnixFileMode]::OtherRead -bor
                [System.IO.UnixFileMode]::OtherExecute
            [System.IO.File]::SetUnixFileMode($_.FullName, $mode)
        }
}

# Mirrors `cp -p`: apply the source file's Unix mode to the installed copy (no-op on Windows).
function Set-FileModeFrom {
    param(
        [string]$Source,
        [string]$Destination
    )

    if ($IsWindows -or -not (Test-Path -LiteralPath $Source) -or -not (Test-Path -LiteralPath $Destination)) {
        return
    }

    # Never chmod through a link: it would change the target's mode.
    if ((Get-Item -Force -LiteralPath $Destination).LinkType) {
        return
    }

    [System.IO.File]::SetUnixFileMode($Destination, [System.IO.File]::GetUnixFileMode($Source))
}

# Mirrors `cp -Rp` mode handling: walk the source tree and apply each source file's Unix mode
# to the corresponding installed file. Files pruned from the destination (e.g. skill evals/) are
# skipped because the installed path no longer exists. No-op on Windows.
function Set-CopiedFileModes {
    param(
        [string]$Source,
        [string]$Destination
    )

    if ($IsWindows -or -not (Test-Path -LiteralPath $Source) -or -not (Test-Path -LiteralPath $Destination)) {
        return
    }

    # Link entries are skipped: chmod through a reparse point would change the target's mode.
    Get-ChildItem -Force -Path $Source -Recurse -File |
        Where-Object { -not $_.LinkType } | ForEach-Object {
        $relativePath = $_.FullName.Substring($Source.Length).TrimStart('/', '\')
        $installedPath = Join-Path $Destination $relativePath
        Set-FileModeFrom -Source $_.FullName -Destination $installedPath
    }
}

function Copy-Skills {
    foreach ($entry in (Get-ChildItem -Force -Path $SkillsSrc)) {
        # Mirrors bash `[[ $name == "archive" || $name == *-workspace ]]` case-sensitively:
        # `[ ] * ?` in the name are literal, and `My-Workspace` is not a workspace entry.
        if ($entry.Name -ceq 'archive' -or $entry.Name.EndsWith('-workspace')) {
            continue
        }

        Copy-Entry -Entry $entry -DestinationDir $SkillsDest

        # Pruning and mode sync must not resolve a path through a preserved link:
        # Remove-IfExists would otherwise delete files inside the link target.
        if ([string]$entry.LinkType) {
            continue
        }
        Remove-IfExists (Join-Path $SkillsDest "$($entry.Name)/evals")
        Remove-IfExists (Join-Path $SkillsDest "$($entry.Name)/README.md")
        Remove-IfExists (Join-Path $SkillsDest "$($entry.Name)/LICENSE.txt")
        Remove-IfExists (Join-Path $SkillsDest "$($entry.Name)/LICENSE.md")
        if ($entry.PSIsContainer) {
            Set-CopiedFileModes -Source $entry.FullName -Destination (Join-Path $SkillsDest $entry.Name)
        } else {
            Set-FileModeFrom -Source $entry.FullName -Destination (Join-Path $SkillsDest $entry.Name)
        }
    }
}

function Copy-Agents {
    Copy-DirectoryContents -Source $AgentsSrc -Destination $AgentsDest
    Copy-DirectoryContents -Source $AgentsSrc -Destination $CopilotAgentsDest
    Set-CopiedFileModes -Source $AgentsSrc -Destination $AgentsDest
    Set-CopiedFileModes -Source $AgentsSrc -Destination $CopilotAgentsDest
}

function Copy-References {
    Copy-DirectoryContents -Source $ReferencesSrc -Destination $ReferencesDest
    Set-CopiedFileModes -Source $ReferencesSrc -Destination $ReferencesDest
}

function Copy-Hooks {
    Copy-DirectoryContents -Source $HooksSrc -Destination $HooksDest
    Set-CopiedFileModes -Source $HooksSrc -Destination $HooksDest
    Set-HookScriptsExecutable -Root $HooksDest
}

function Copy-Gemini {
    Get-ChildItem -Force -Path $GeminiSrc |
        Where-Object { $_.Name -cne 'hooks' } |
        ForEach-Object { Copy-Entry -Entry $_ -DestinationDir $GeminiDest }

    $geminiHooksSrc = Join-Path $GeminiSrc 'hooks'
    $geminiHooksDest = Join-Path $GeminiDest 'hooks'
    New-Item -ItemType Directory -Path $geminiHooksDest -Force | Out-Null
    Get-ChildItem -Force -Path $geminiHooksSrc |
        Where-Object { $_.Name -cne 'logs' } |
        ForEach-Object { Copy-Entry -Entry $_ -DestinationDir $geminiHooksDest }

    Remove-IfExists (Join-Path $GeminiDest 'global-settings.json')
    Remove-IfExists (Join-Path $GeminiDest 'settings.json')
    Set-CopiedFileModes -Source $GeminiSrc -Destination $GeminiDest
    Set-HookScriptsExecutable -Root (Join-Path $GeminiDest 'hooks')
}

# Installs one fixed-name file, preserving a link object if the source is one (never follows it).
function Copy-FileTo {
    param(
        [string]$Source,
        [string]$Destination
    )

    $entry = Get-Item -Force -LiteralPath $Source
    $linkType = [string]$entry.LinkType
    if ($linkType -ceq 'SymbolicLink') {
        Install-PreservedLink -SourceDescription $Source -Destination $Destination -LinkType $linkType -Target $entry.Target
        return
    }
    if ($linkType -ceq 'Junction') {
        Install-PreservedLink -SourceDescription $Source -Destination $Destination -LinkType $linkType -Target $entry.Target
        return
    }
    if ($linkType -ceq 'HardLink') {
        Copy-FileWithMode -Source $Source -Destination $Destination
        return
    }
    if ($linkType) {
        Fail "Refusing to follow unsupported reparse point during install: $Source (type: $linkType)."
    }
    Copy-FileWithMode -Source $Source -Destination $Destination
}

function Copy-GeminiGlobalSettings {
    Copy-FileTo -Source $GeminiGlobalSettingsSrc -Destination (Join-Path $GeminiDest 'settings.json')
}

function Copy-CopilotInstructions {
    Copy-FileTo -Source $CopilotInstructionsSrc -Destination (Join-Path $CopilotDest 'copilot-instructions.md')
}

function Copy-CopilotLsp {
    Copy-FileTo -Source $CopilotLspSrc -Destination (Join-Path $CopilotDest 'lsp-config.json')
}

function Install-CodexHook {
    param(
        [string]$PythonPath,
        [string[]]$PythonArguments
    )

    New-Item -ItemType Directory -Path $CodexHooksDest -Force | Out-Null
    $installedHook = Join-Path $CodexHooksDest 'load-required-skills.py'
    $existingHook = Get-Item -Force -LiteralPath $installedHook -ErrorAction SilentlyContinue
    if ($null -ne $existingHook -and [string]$existingHook.LinkType) {
        Fail "Refusing to overwrite linked Codex hook destination: $installedHook"
    }
    Copy-FileTo -Source $CodexHookSrc -Destination $installedHook
    if (-not $IsWindows) {
        $executable = [System.IO.UnixFileMode]::UserRead -bor
            [System.IO.UnixFileMode]::UserWrite -bor
            [System.IO.UnixFileMode]::UserExecute -bor
            [System.IO.UnixFileMode]::GroupRead -bor
            [System.IO.UnixFileMode]::GroupExecute -bor
            [System.IO.UnixFileMode]::OtherRead -bor
            [System.IO.UnixFileMode]::OtherExecute
        [System.IO.File]::SetUnixFileMode($installedHook, $executable)
    }

    & $PythonPath @PythonArguments $CodexHookMergerSrc --template $CodexHookTemplateSrc --destination $CodexHookConfigDest
    if ($LASTEXITCODE -ne 0) {
        Fail "Codex hook configuration merger exited with code $LASTEXITCODE."
    }
}

foreach ($src in @($SkillsSrc, $AgentsSrc, $GeminiSrc)) {
    if (-not (Test-Path -LiteralPath $src -PathType Container)) {
        Fail "Missing source directory: $src"
    }
}

foreach ($src in @($CopilotInstructionsSrc, $CopilotLspSrc, $GeminiGlobalSettingsSrc)) {
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
        Fail "Missing source file: $src"
    }
}

foreach ($src in @($CodexHookSrc, $CodexHookTemplateSrc, $CodexHookMergerSrc, $CodexAgentInstallerSrc)) {
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
        Fail "Missing source file: $src"
    }
}

$pythonCommand = Get-PythonCommand
& $pythonCommand.Path @($pythonCommand.Arguments) $CodexAgentInstallerSrc --source-dir $AgentsSrc --destination-dir $CodexAgentsDest
if ($LASTEXITCODE -ne 0) {
    Fail "Codex agent converter exited with code $LASTEXITCODE."
}

foreach ($dest in @($SkillsDest, $CopilotDest, $GeminiDest, $AgentsDest, $CopilotAgentsDest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

Copy-Skills
Copy-Agents
if (Test-Path -LiteralPath $ReferencesSrc) {
    New-Item -ItemType Directory -Path $ReferencesDest -Force | Out-Null
    Copy-References
}
if (Test-Path -LiteralPath $HooksSrc) {
    New-Item -ItemType Directory -Path $HooksDest -Force | Out-Null
    Copy-Hooks
}
Copy-Gemini
Copy-GeminiGlobalSettings
Copy-CopilotInstructions
Copy-CopilotLsp
Install-CodexHook -PythonPath $pythonCommand.Path -PythonArguments $pythonCommand.Arguments

Write-Output "Installed skills to $SkillsDest"
Write-Output "Installed agents to $AgentsDest and $CopilotAgentsDest"
Write-Output "Installed Codex agents to $CodexAgentsDest"
if (Test-Path -LiteralPath $ReferencesSrc) {
    Write-Output "Installed references to $ReferencesDest"
}
if (Test-Path -LiteralPath $HooksSrc) {
    Write-Output "Installed hooks to $HooksDest"
}
Write-Output "Installed Gemini instructions to $GeminiDest"
Write-Output "Installed Gemini settings to $(Join-Path $GeminiDest 'settings.json')"
Write-Output "Installed Copilot instructions to $(Join-Path $CopilotDest 'copilot-instructions.md')"
Write-Output "Installed Copilot LSP config to $(Join-Path $CopilotDest 'lsp-config.json')"
Write-Output "Installed Codex hook to $(Join-Path $CodexHooksDest 'load-required-skills.py')"
Write-Output "Installed Codex hook configuration to $CodexHookConfigDest"
