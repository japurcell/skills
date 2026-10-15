#!/usr/bin/env pwsh
#Requires -Version 7.0
<#
.SYNOPSIS
    Installs repo skills, agents, references, hooks, and Gemini/Copilot configs into the user home.

.DESCRIPTION
    PowerShell 7 port of scripts/install.sh. Produces the same installed layout:

    - skills/default/* plus opted-in skills/forest-service/* -> ~/.agents/skills
      (skips *-workspace and archive; prunes evals/, README.md, and LICENSE.*)

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

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Leave arguments unbound so only the documented literal spellings are accepted.
$helpRequested = $false
$forestService = $false
$selection = ''
foreach ($argument in $args) {
    if ([string]::Equals($argument, '-h', [StringComparison]::Ordinal) -or [string]::Equals($argument, '--help', [StringComparison]::Ordinal)) {
        $helpRequested = $true
    } elseif ([string]::Equals($argument, '--forest-service', [StringComparison]::Ordinal) -or [string]::Equals($argument, '--fs', [StringComparison]::Ordinal)) {
        if ($selection -ceq 'disable') {
            [Console]::Error.WriteLine('Conflicting selection flags: choose --forest-service or --no-forest-service.')
            exit 2
        }
        $selection = 'enable'
        $forestService = $true
    } elseif ([string]::Equals($argument, '--no-forest-service', [StringComparison]::Ordinal)) {
        if ($selection -ceq 'enable') {
            [Console]::Error.WriteLine('Conflicting selection flags: choose --forest-service or --no-forest-service.')
            exit 2
        }
        $selection = 'disable'
        $forestService = $false
    } else {
        [Console]::Error.WriteLine("Unknown argument: $argument. Use --help for usage.")
        exit 2
    }
}
if ($helpRequested) {
    [Console]::Out.WriteLine(@'
Usage: pwsh -NoProfile -File scripts/install.ps1 [--forest-service | --fs | --no-forest-service] [-h | --help]

Install default skills, agents, references, and provider configuration.
Use --forest-service or --fs to include Forest Service skills.
Use --no-forest-service to install default skills only.
Without a selection flag, INSTALL_FOREST_SERVICE_SKILLS accepts 1/true or
0/false (case-insensitive); unset or empty disables Forest Service skills.
Explicit selection flags override the environment. Existing skills remain.

Examples:
  pwsh -NoProfile -File scripts/install.ps1
  pwsh -NoProfile -File scripts/install.ps1 --fs
  $env:INSTALL_FOREST_SERVICE_SKILLS = 'true'; pwsh -NoProfile -File scripts/install.ps1
  pwsh -NoProfile -File scripts/install.ps1 --no-forest-service
'@)
    exit 0
}

if ($selection -ceq '') {
    $value = $env:INSTALL_FOREST_SERVICE_SKILLS
    if ([string]::Equals($value, '1', [StringComparison]::Ordinal) -or [string]::Equals($value, 'true', [StringComparison]::OrdinalIgnoreCase)) {
        $forestService = $true
    } elseif ([string]::IsNullOrEmpty($value) -or [string]::Equals($value, '0', [StringComparison]::Ordinal) -or [string]::Equals($value, 'false', [StringComparison]::OrdinalIgnoreCase)) {
        $forestService = $false
    } else {
        [Console]::Error.WriteLine('Invalid INSTALL_FOREST_SERVICE_SKILLS: use 1, true, 0, false, or empty; alternatively choose --forest-service or --no-forest-service.')
        exit 2
    }
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SkillsSrc = Join-Path $RepoRoot 'skills'
$AgentsSrc = Join-Path $RepoRoot 'agents'
$ReferencesSrc = Join-Path $RepoRoot 'references'
$HooksSrc = Join-Path $RepoRoot '.copilot/hooks'
$CopilotHookTemplateSrc = Join-Path $HooksSrc 'hooks.json'
$GeminiSrc = Join-Path $RepoRoot '.gemini'
$GeminiGlobalSettingsSrc = Join-Path $RepoRoot '.gemini/global-settings.json'
$ProviderHookMergerSrc = Join-Path $RepoRoot 'scripts/install-provider-hooks.py'
$CopilotInstructionsSrc = Join-Path $RepoRoot '.copilot/copilot-instructions.md'
$CopilotLspSrc = Join-Path $RepoRoot '.copilot/lsp-config.json'
$CodexHookSrcDir = Join-Path $RepoRoot '.codex/hooks'
$CodexHookFiles = @('load-required-skills.py', 'scan-secrets.py', 'tool-guard.py', 'helpers/common.py', 'helpers/audit.py', 'helpers/tool_guard_policy.py')
$CodexInstructionsSrc = Join-Path $RepoRoot '.codex/AGENTS.md'
$CodexHookTemplateSrc = Join-Path $RepoRoot '.codex/global-hooks.json'
$CodexHookMergerSrc = Join-Path $RepoRoot 'scripts/install-codex-hooks.py'
$CodexAgentInstallerSrc = Join-Path $RepoRoot 'scripts/install-codex-agents.py'
$RebaseSkillReferencesSrc = Join-Path $RepoRoot 'scripts/rebase-skill-references.py'
$ValidateSkillSourcesSrc = Join-Path $RepoRoot 'scripts/validate-skill-sources.py'
$GenerateHooksSrc = Join-Path $RepoRoot 'scripts/generate-hooks.py'
$ConfigureRtkSrc = Join-Path $RepoRoot 'scripts/configure-rtk.py'
$CanonicalHooksSrc = Join-Path $RepoRoot 'hooks'

$SkillsDest = Join-Path $HOME '.agents/skills'
$ReferencesDest = Join-Path $HOME '.agents/references'
$GeminiDest = Join-Path $HOME '.gemini'
$CopilotDest = Join-Path $HOME '.copilot'
$AgentsDest = Join-Path $GeminiDest 'agents'
$CopilotAgentsDest = Join-Path $CopilotDest 'agents'
$HooksDest = Join-Path $CopilotDest 'hooks'
$CopilotHookConfigDest = Join-Path $HooksDest 'hooks.json'
$GeminiSettingsDest = Join-Path $GeminiDest 'settings.json'
$CodexDest = Join-Path $HOME '.codex'
$CodexHooksDest = Join-Path $CodexDest 'hooks'
$CodexHookConfigDest = Join-Path $CodexDest 'hooks.json'
$CodexInstructionsDest = Join-Path $CodexDest 'AGENTS.md'
$CodexAgentsDest = Join-Path $(if ([string]::IsNullOrEmpty($env:CODEX_HOME)) { $CodexDest } else { $env:CODEX_HOME }) 'agents'

function Fail {
    param([string]$Message)

    [Console]::Error.WriteLine($Message)
    exit 1
}

function Write-InstallStatus {
    process { [Console]::Error.WriteLine($_) }
}

trap {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}

function Get-PythonCommand {
    $python = @(Get-Command python3 -CommandType Application -ErrorAction SilentlyContinue)[0]
    $arguments = @('-B')
    if ($null -eq $python) {
        $python = @(Get-Command py -CommandType Application -ErrorAction SilentlyContinue)[0]
        $arguments = @('-3', '-B')
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

function Complete-CopyMode {
    param(
        [string]$Source,
        [string]$Destination,
        [bool]$Copied,
        $OriginalMode
    )

    if ($Copied) {
        Set-FileModeFrom -Source $Source -Destination $Destination
    }
    elseif ($null -ne $OriginalMode) {
        [System.IO.File]::SetUnixFileMode($Destination, $OriginalMode)
    }
}

# Copies a regular file while preserving its Unix file mode.
function Copy-FileWithMode {
    param(
        [string]$Source,
        [string]$Destination
    )

    $originalMode = $null
    $copied = $false
    try {
        $destinationEntry = $null
        if (Test-Path -LiteralPath $Destination) {
            $destinationEntry = Get-Item -Force -LiteralPath $Destination
            if ([string]$destinationEntry.LinkType -ceq 'HardLink' -and $destinationEntry.IsReadOnly) {
                Fail "Refusing to change read-only hard-linked file: $Destination"
            }
        }
        if (-not $IsWindows -and $null -ne $destinationEntry -and -not $destinationEntry.LinkType) {
            $originalMode = [System.IO.File]::GetUnixFileMode($Destination)
            [System.IO.File]::SetUnixFileMode($Destination, ($originalMode -bor [System.IO.UnixFileMode]::UserWrite))
        }
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        $copied = $true
    }
    finally {
        Complete-CopyMode -Source $Source -Destination $Destination -Copied $copied -OriginalMode $originalMode
    }
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
    if ($linkType -ceq 'SymbolicLink' -or $linkType -ceq 'Junction') {
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
        $originalMode = $null
        $copied = $false
        try {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            if (-not $IsWindows -and -not (Get-Item -Force -LiteralPath $destPath).LinkType) {
                $originalMode = [System.IO.File]::GetUnixFileMode($destPath)
                [System.IO.File]::SetUnixFileMode($destPath, ($originalMode -bor [System.IO.UnixFileMode]::UserWrite))
            }
            Copy-DirectoryContents -Source $Entry.FullName -Destination $destPath
            $copied = $true
        }
        finally {
            Complete-CopyMode -Source $Entry.FullName -Destination $destPath -Copied $copied -OriginalMode $originalMode
        }
        return
    }
    Copy-FileWithMode -Source $Entry.FullName -Destination (Join-Path $DestinationDir $Entry.Name)
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

function Set-HookScriptsExecutable {
    param([string]$Root)

    if ($IsWindows -or -not (Test-Path -LiteralPath $Root)) {
        return
    }

    # Mirrors `find <root> -type f \( -name "*.py" -o -name "*.sh" \) -exec chmod 755 {} +`.
    # Ordinal matching preserves literal extensions: test.PY and .p<soft-hyphen>y are not hook scripts.
    # Link entries are skipped: chmod through a reparse point would change the target's mode.
    Get-ChildItem -Force -Path $Root -Recurse -File |
        Where-Object { -not $_.LinkType -and ($_.Extension.Equals('.py', [StringComparison]::Ordinal) -or $_.Extension.Equals('.sh', [StringComparison]::Ordinal)) } |
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
        [string]$Destination,
        [string[]]$ExcludedRelativePaths = @()
    )

    if ($IsWindows -or -not (Test-Path -LiteralPath $Source) -or -not (Test-Path -LiteralPath $Destination)) {
        return
    }

    # Link entries are skipped: chmod through a reparse point would change the target's mode.
    Get-ChildItem -Force -Path $Source -Recurse -File |
        Where-Object { -not $_.LinkType } | ForEach-Object {
        $relativePath = $_.FullName.Substring($Source.Length).TrimStart('/', '\')
        if ($ExcludedRelativePaths -ccontains $relativePath) {
            return
        }
        $installedPath = Join-Path $Destination $relativePath
        Set-FileModeFrom -Source $_.FullName -Destination $installedPath
    }
}

function Copy-Skills {
    param([string]$Category)
    foreach ($entry in (Get-ChildItem -Force -LiteralPath (Join-Path $SkillsSrc $Category))) {
        if (-not $entry.PSIsContainer) {
            continue
        }
        # Mirrors bash `[[ $name == "archive" || $name == *-workspace ]]` case-sensitively:
        # `[ ] * ?` in the name are literal, and `My-Workspace` is not a workspace entry.
        if ($entry.Name.Equals('archive', [StringComparison]::Ordinal) -or $entry.Name.EndsWith('-workspace', [StringComparison]::Ordinal)) {
            continue
        }

        Copy-Entry -Entry $entry -DestinationDir $SkillsDest

        # Pruning and mode sync must not resolve a preserved link's target.
        if ([string]$entry.LinkType) {
            continue
        }
        $installedSkill = Join-Path $SkillsDest $entry.Name
        Set-CopiedFileModes -Source $entry.FullName -Destination $installedSkill
        & $pythonCommand.Path @($pythonCommand.Arguments) $RebaseSkillReferencesSrc `
            --source-dir $entry.FullName `
            --destination-dir $installedSkill `
            --references-source $ReferencesSrc `
            --references-destination $ReferencesDest `
            --prune | Write-InstallStatus
        if ($LASTEXITCODE -ne 0) {
            Fail "Shared reference rebasing exited with code $LASTEXITCODE for skill $($entry.Name)."
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
    Get-ChildItem -Force -Path $HooksSrc |
        Where-Object { $_.Name -cne 'hooks.json' } |
        ForEach-Object { Copy-Entry -Entry $_ -DestinationDir $HooksDest }
    Set-CopiedFileModes -Source $HooksSrc -Destination $HooksDest -ExcludedRelativePaths @('hooks.json')
    Set-HookScriptsExecutable -Root $HooksDest
}

function Copy-Gemini {
    Get-ChildItem -Force -Path $GeminiSrc |
        Where-Object { $_.Name -cne 'hooks' -and $_.Name -cne 'global-settings.json' -and $_.Name -cne 'settings.json' } |
        ForEach-Object { Copy-Entry -Entry $_ -DestinationDir $GeminiDest }

    $geminiHooksSrc = Join-Path $GeminiSrc 'hooks'
    $geminiHooksDest = Join-Path $GeminiDest 'hooks'
    New-Item -ItemType Directory -Path $geminiHooksDest -Force | Out-Null
    Get-ChildItem -Force -Path $geminiHooksSrc |
        Where-Object { $_.Name -cne 'logs' } |
        ForEach-Object { Copy-Entry -Entry $_ -DestinationDir $geminiHooksDest }

    Set-CopiedFileModes -Source $GeminiSrc -Destination $GeminiDest -ExcludedRelativePaths @('settings.json', 'global-settings.json')
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
    & $pythonCommand.Path @($pythonCommand.Arguments) $ProviderHookMergerSrc --provider gemini --template $GeminiGlobalSettingsSrc --destination $GeminiSettingsDest --home $HOME | Write-InstallStatus
    if ($LASTEXITCODE -ne 0) { Fail "Gemini settings merger exited with code $LASTEXITCODE." }
}

function Install-CopilotHookConfig {
    & $pythonCommand.Path @($pythonCommand.Arguments) $ProviderHookMergerSrc --provider copilot --template $CopilotHookTemplateSrc --destination $CopilotHookConfigDest --home $HOME | Write-InstallStatus
    if ($LASTEXITCODE -ne 0) { Fail "Copilot hooks merger exited with code $LASTEXITCODE." }
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

    & $PythonPath @PythonArguments $CodexHookMergerSrc --template $CodexHookTemplateSrc --destination $CodexHookConfigDest --check | Write-InstallStatus
    if ($LASTEXITCODE -ne 0) {
        Fail "Codex hook configuration preflight exited with code $LASTEXITCODE."
    }
    foreach ($directory in @($CodexHooksDest, (Join-Path $CodexHooksDest 'helpers'))) {
        $existingDirectory = Get-Item -Force -LiteralPath $directory -ErrorAction SilentlyContinue
        if ($null -ne $existingDirectory -and [string]$existingDirectory.LinkType) {
            Fail "Refusing linked Codex hook directory: $directory"
        }
    }
    foreach ($relative in $CodexHookFiles) {
        $installedHook = Join-Path $CodexHooksDest $relative
        $existingHook = Get-Item -Force -LiteralPath $installedHook -ErrorAction SilentlyContinue
        if ($null -ne $existingHook -and ([string]$existingHook.LinkType -or $existingHook.PSIsContainer)) {
            Fail "Refusing linked or non-file Codex hook destination: $installedHook"
        }
    }
    New-Item -ItemType Directory -Path (Join-Path $CodexHooksDest 'helpers') -Force | Out-Null
    foreach ($relative in $CodexHookFiles) {
        $installedHook = Join-Path $CodexHooksDest $relative
        Copy-FileTo -Source (Join-Path $CodexHookSrcDir $relative) -Destination $installedHook
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
    }

    & $PythonPath @PythonArguments $CodexHookMergerSrc --template $CodexHookTemplateSrc --destination $CodexHookConfigDest | Write-InstallStatus
    if ($LASTEXITCODE -ne 0) {
        Fail "Codex hook configuration merger exited with code $LASTEXITCODE."
    }
}

function Install-CodexInstructions {
    New-Item -ItemType Directory -Path $CodexDest -Force | Out-Null
    Copy-FileTo -Source $CodexInstructionsSrc -Destination $CodexInstructionsDest
}

foreach ($src in @((Join-Path $SkillsSrc 'default'), (Join-Path $SkillsSrc 'forest-service'), $AgentsSrc, $GeminiSrc, $CanonicalHooksSrc)) {
    if (-not (Test-Path -LiteralPath $src -PathType Container)) {
        Fail "Missing source directory: $src"
    }
}

foreach ($src in @(
    $CopilotInstructionsSrc, $CopilotLspSrc, $GeminiGlobalSettingsSrc, $CopilotHookTemplateSrc, $ProviderHookMergerSrc,
    $CodexInstructionsSrc, $CodexHookTemplateSrc, $CodexHookMergerSrc, $CodexAgentInstallerSrc, $RebaseSkillReferencesSrc, $ValidateSkillSourcesSrc, $GenerateHooksSrc, $ConfigureRtkSrc
)) {
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
        Fail "Missing source file: $src"
    }
}
foreach ($relative in $CodexHookFiles) {
    $source = Join-Path $CodexHookSrcDir $relative
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        Fail "Missing source file: $source"
    }
}

$pythonCommand = Get-PythonCommand
# Python uses the Windows ANSI codepage for redirected stderr by default.
# Pair its stream encoding with PowerShell's native-output decoder so original
# Unicode source paths survive the validation boundary without replacement.
$previousPythonIoEncoding = [Environment]::GetEnvironmentVariable('PYTHONIOENCODING', 'Process')
$previousConsoleOutputEncoding = [Console]::OutputEncoding
try {
    [Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'Process')
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    & $pythonCommand.Path @($pythonCommand.Arguments) $ValidateSkillSourcesSrc $SkillsSrc | Write-InstallStatus
}
finally {
    [Console]::OutputEncoding = $previousConsoleOutputEncoding
    [Environment]::SetEnvironmentVariable('PYTHONIOENCODING', $previousPythonIoEncoding, 'Process')
}
if ($LASTEXITCODE -ne 0) { Fail "Skill source validation exited with code $LASTEXITCODE." }
& $pythonCommand.Path @($pythonCommand.Arguments) $ConfigureRtkSrc --home $HOME --check | Write-InstallStatus
if ($LASTEXITCODE -ne 0) { Fail "RTK preflight exited with code $LASTEXITCODE." }
& $pythonCommand.Path @($pythonCommand.Arguments) $GenerateHooksSrc --check | Write-InstallStatus
$preflightExitCode = $LASTEXITCODE
if ($preflightExitCode -ne 0) {
    if ($preflightExitCode -eq 1) {
        [Console]::Error.WriteLine('Generated hooks are stale. Run: python3 scripts/generate-hooks.py --write')
        exit 1
    }
    [Console]::Error.WriteLine('Generated hook freshness preflight failed.')
    exit 1
}

foreach ($config in @(
    @{ Provider = 'copilot'; Template = $CopilotHookTemplateSrc; Destination = $CopilotHookConfigDest },
    @{ Provider = 'gemini'; Template = $GeminiGlobalSettingsSrc; Destination = $GeminiSettingsDest }
)) {
    & $pythonCommand.Path @($pythonCommand.Arguments) $ProviderHookMergerSrc --provider $config.Provider --template $config.Template --destination $config.Destination --home $HOME --check | Write-InstallStatus
    if ($LASTEXITCODE -ne 0) { Fail "$($config.Provider) configuration preflight exited with code $LASTEXITCODE." }
}

& $pythonCommand.Path @($pythonCommand.Arguments) $ConfigureRtkSrc --home $HOME | Write-InstallStatus
if ($LASTEXITCODE -ne 0) { Fail "RTK configuration exited with code $LASTEXITCODE." }
& $pythonCommand.Path @($pythonCommand.Arguments) $CodexAgentInstallerSrc --source-dir $AgentsSrc --destination-dir $CodexAgentsDest | Write-InstallStatus
if ($LASTEXITCODE -ne 0) {
    Fail "Codex agent converter exited with code $LASTEXITCODE."
}

foreach ($dest in @($SkillsDest, $CopilotDest, $GeminiDest, $AgentsDest, $CopilotAgentsDest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

Copy-Skills -Category 'default'
if ($forestService) {
    Copy-Skills -Category 'forest-service'
}
Copy-Agents
if (Test-Path -LiteralPath $ReferencesSrc) {
    New-Item -ItemType Directory -Path $ReferencesDest -Force | Out-Null
    Copy-References
}
if (Test-Path -LiteralPath $HooksSrc) {
    New-Item -ItemType Directory -Path $HooksDest -Force | Out-Null
    Copy-Hooks
}
Install-CopilotHookConfig
Copy-Gemini
Copy-GeminiGlobalSettings
Copy-CopilotInstructions
Copy-CopilotLsp
Install-CodexInstructions
Install-CodexHook -PythonPath $pythonCommand.Path -PythonArguments $pythonCommand.Arguments

[Console]::Error.WriteLine("Installed skills to $SkillsDest")
[Console]::Error.WriteLine("Installed agents to $AgentsDest and $CopilotAgentsDest")
[Console]::Error.WriteLine("Installed Codex agents to $CodexAgentsDest")
if (Test-Path -LiteralPath $ReferencesSrc) {
    [Console]::Error.WriteLine("Installed references to $ReferencesDest")
}
if (Test-Path -LiteralPath $HooksSrc) {
    [Console]::Error.WriteLine("Installed hooks to $HooksDest")
}
[Console]::Error.WriteLine("Installed Gemini instructions to $GeminiDest")
[Console]::Error.WriteLine("Installed Gemini settings to $(Join-Path $GeminiDest 'settings.json')")
[Console]::Error.WriteLine("Installed Copilot instructions to $(Join-Path $CopilotDest 'copilot-instructions.md')")
[Console]::Error.WriteLine("Installed Copilot LSP config to $(Join-Path $CopilotDest 'lsp-config.json')")
[Console]::Error.WriteLine("Installed Codex instructions to $CodexInstructionsDest")
[Console]::Error.WriteLine("Installed Codex hook to $(Join-Path $CodexHooksDest 'load-required-skills.py')")
[Console]::Error.WriteLine("Installed Codex hook configuration to $CodexHookConfigDest")
exit 0
