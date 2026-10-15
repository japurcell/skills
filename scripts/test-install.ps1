#!/usr/bin/env pwsh
#Requires -Version 7.0
<#
.SYNOPSIS
    Tests scripts/install.ps1 against a fixture repository in a temp directory.

.DESCRIPTION
    PowerShell port of scripts/test-install.sh. Builds a throwaway fixture repo
    (mirroring create_fixture_repo in scripts/test-install.sh), redirects the
    child pwsh process's HOME and USERPROFILE environment variables to a temp
    home, runs the real scripts/install.ps1, and asserts the installed layout:

     1. Skill excludes/pruning: *-workspace and archive entries are not copied
        (case-sensitive suffix, `[ ] *` in names literal: `weird[1]-workspace`
        stays excluded, a `My-Workspace` skill is copied), installed evals/ is
        removed, pre-existing non-evals content survives.
     2. Symlink/reparse-point safety: fixture file and directory symlinks
        (targets outside the repo) install as link objects with their raw
        targets intact - never as regular files containing the targets'
        contents (like `cp -Rp`); where link creation is unsupported (e.g.
        Windows without privileges) the test reports a deliberate skip.
     3. Hard-link parity for fixed-name files: a fixed-name source installed
         through `Copy-FileTo` becomes a regular file with matching content and
         mode, not a rejected link or a preserved hard link; the test skips
         explicitly if the host cannot create hard links in the fixture.
     4. Junction preservation: directory link entries keep their original
         link type (`Junction` rather than `SymbolicLink`) and raw target when
         the host supports junction creation; otherwise the test skips
         explicitly.
     5. Full Gemini tree copy: nested agents in both agent destinations, hidden
         files, hooks, settings.json overwritten by global-settings.json, and no
         nested .gemini/.gemini directory.
     6. Installed hook scripts are exactly 755 (UserRead/UserWrite/UserExecute/
         GroupRead/GroupExecute/OtherRead/OtherExecute) and the extension match
         is case-sensitive like `find -name` (an uppercase .PY hook keeps its
         input mode; non-Windows only, skipped on Windows).
     7. Source Unix file modes are preserved on install: a fixture skill file
         with a non-default executable mode (skills/default/alpha/tool.sh at 755) keeps
         its exact mode, and the installed skills/alpha/SKILL.md exactly equals
         its source mode (non-Windows only; skipped on Windows).
     8. Copilot config and references: .copilot/copilot-instructions.md and
         .copilot/lsp-config.json content is installed into ~/.copilot, and a
         fixture references/ file is copied into ~/.agents/references.
      9. Missing required source: with the required agents/ source removed, the
          install exits 1 and reports "Missing source directory" on the child's
          stderr stream (captured separately from stdout, so a diagnostic moved
          to stdout fails the suite).
     10. Content comparisons are normalized: Read-FileContent normalizes
         CRLF to LF and strips one trailing newline before comparing, so the
         content-equals-fixture assertions are normalized-content equality, not
         byte equality. This is intentional parity with the Bash suite's
         `$(<file)` comparison, which strips the trailing newline the same way.

    Exits 0 on success and 1 on the first failed assertion. Self-contained:
    does not source scripts/test-common.sh. Requires pwsh on PATH (it spawns
    child `pwsh -NoProfile -File` processes).
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot
$InstallScriptSrc = Join-Path $RepoRoot 'scripts/install.ps1'

function Fail {
    param([string]$Message)

    [Console]::Error.WriteLine($Message)
    exit 1
}

function Assert-Equals {
    param(
        $Expected,
        $Actual,
        [string]$Message
    )

    if ("$Actual" -ne "$Expected") {
        [Console]::Error.WriteLine($Message)
        [Console]::Error.WriteLine("Expected: $Expected")
        [Console]::Error.WriteLine("Actual:   $Actual")
        exit 1
    }
}

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        [Console]::Error.WriteLine($Message)
        exit 1
    }
}

# Mirrors bash $(<file): full content, CRLF normalized to LF, one trailing newline stripped.
function Read-FileContent {
    param([string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $content = $content -replace "`r`n", "`n"
    if ($content.EndsWith("`n")) {
        $content = $content.Substring(0, $content.Length - 1)
    }
    return $content
}

# Writes each line with a trailing newline, mirroring `printf '%s\n' line1 line2 ...`.
function Write-FixtureFile {
    param(
        [string]$Path,
        [string[]]$Lines
    )

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        # New-Item has no -LiteralPath; -Path is created literally (verified for `[1]` names).
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Set-Content -LiteralPath $Path -Value $Lines -Encoding utf8NoBOM
}

function New-TestWorkdir {
    $path = Join-Path ([System.IO.Path]::GetTempPath()) "test-install-$([System.IO.Path]::GetRandomFileName())"
    New-Item -ItemType Directory -Path $path -Force | Out-Null
    return $path
}

function Remove-Workdir {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function New-FixtureRepo {
    param([string]$Repo)

    $dirs = @(
        (Join-Path $Repo 'scripts'),
        (Join-Path $Repo 'skills/default/alpha/evals'),
        (Join-Path $Repo 'skills/forest-service'),
        (Join-Path $Repo 'skills/default/beta-workspace'),
        (Join-Path $Repo 'skills/default/archive'),
        (Join-Path $Repo 'skills/default/weird[1]-workspace'),
        (Join-Path $Repo 'skills/default/My-Workspace'),
        (Join-Path $Repo 'agents/nested'),
        (Join-Path $Repo 'references'),
        (Join-Path $Repo '.copilot/hooks/scripts'),
        (Join-Path $Repo '.codex/hooks'),
        (Join-Path $Repo '.gemini/policies'),
        (Join-Path $Repo '.gemini/hooks/scripts')
    )
    foreach ($dir in $dirs) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    Copy-Item -LiteralPath $InstallScriptSrc -Destination (Join-Path $Repo 'scripts/install.ps1') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/file_io.py') -Destination (Join-Path $Repo 'scripts/file_io.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/install-codex-agents.py') -Destination (Join-Path $Repo 'scripts/install-codex-agents.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/install-codex-hooks.py') -Destination (Join-Path $Repo 'scripts/install-codex-hooks.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/configure-rtk.py') -Destination (Join-Path $Repo 'scripts/configure-rtk.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/rebase-skill-references.py') -Destination (Join-Path $Repo 'scripts/rebase-skill-references.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/validate-skill-sources.py') -Destination (Join-Path $Repo 'scripts/validate-skill-sources.py') -Force
    $bin = Join-Path $Repo 'bin'
    New-Item -ItemType Directory -Path $bin -Force | Out-Null
    if ($IsWindows) {
        Write-FixtureFile (Join-Path $bin 'rtk.cmd') @('@echo off', 'echo rtk 0.50.0')
    } else {
        Write-FixtureFile (Join-Path $bin 'rtk') @('#!/bin/sh', 'printf "rtk 0.50.0\n"')
        [System.IO.File]::SetUnixFileMode((Join-Path $bin 'rtk'), ([System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite -bor [System.IO.UnixFileMode]::UserExecute))
    }
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/install-provider-hooks.py') -Destination (Join-Path $Repo 'scripts/install-provider-hooks.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.codex/global-hooks.json') -Destination (Join-Path $Repo '.codex/global-hooks.json') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.codex/AGENTS.md') -Destination (Join-Path $Repo '.codex/AGENTS.md') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.codex/hooks/load-required-skills.py') -Destination (Join-Path $Repo '.codex/hooks/load-required-skills.py') -Force

    Write-FixtureFile (Join-Path $Repo 'skills/default/alpha/SKILL.md') @('---', 'name: alpha', '---', 'Standalone.')
    Write-FixtureFile (Join-Path $Repo 'skills/default/alpha/evals/evals.json') @('fixture eval content')
    Write-FixtureFile (Join-Path $Repo 'skills/default/alpha/tool.sh') @('#!/bin/sh', 'echo tool')
    Write-FixtureFile (Join-Path $Repo 'skills/forest-service/.gitkeep') @('')
    # Non-default source mode: Test-PreservesFileModes asserts it survives install (non-Windows only).
    if (-not $IsWindows) {
        $executable = [System.IO.UnixFileMode]::UserRead -bor
            [System.IO.UnixFileMode]::UserWrite -bor
            [System.IO.UnixFileMode]::UserExecute -bor
            [System.IO.UnixFileMode]::GroupRead -bor
            [System.IO.UnixFileMode]::GroupExecute -bor
            [System.IO.UnixFileMode]::OtherRead -bor
            [System.IO.UnixFileMode]::OtherExecute
        [System.IO.File]::SetUnixFileMode((Join-Path $Repo 'skills/default/alpha/tool.sh'), $executable)
    }
    Write-FixtureFile (Join-Path $Repo 'skills/default/beta-workspace/SKILL.md') @('workspace skill should not copy')
    Write-FixtureFile (Join-Path $Repo 'skills/default/archive/README.md') @('archive entry should not copy')
    # Edge-case names: `[ ]` must stay literal (excluded), and the -workspace suffix
    # match must be case-sensitive (My-Workspace is NOT excluded, matching bash).
    Write-FixtureFile (Join-Path $Repo 'skills/default/weird[1]-workspace/SKILL.md') @('bracket workspace skill should not copy')
    Write-FixtureFile (Join-Path $Repo 'skills/default/My-Workspace/SKILL.md') @('case-variant workspace name should copy')
    Write-FixtureFile (Join-Path $Repo 'agents/helper.md') @('---', 'name: helper', 'description: Fixture helper agent.', '---', 'Use alpha.')
    Write-FixtureFile (Join-Path $Repo 'agents/nested/helper.md') @('---', 'name: nested-helper', 'description: Nested fixture helper agent.', '---', 'Use alpha deeply.')
    Write-FixtureFile (Join-Path $Repo 'references/notes.md') @('Reference notes.')
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.gemini/GEMINI.md') -Destination (Join-Path $Repo '.gemini/GEMINI.md') -Force
    Write-FixtureFile (Join-Path $Repo '.gemini/policies/plan-custom-directory.toml') @('Nested policy.')
    Write-FixtureFile (Join-Path $Repo '.gemini/.hidden-note') @('Hidden note.')
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.copilot/copilot-instructions.md') -Destination (Join-Path $Repo '.copilot/copilot-instructions.md') -Force
    Write-FixtureFile (Join-Path $Repo '.copilot/lsp-config.json') @('{}')
    Write-FixtureFile (Join-Path $Repo '.copilot/hooks/test-hook.sh') @('#!/bin/bash', 'echo hook')
    Write-FixtureFile (Join-Path $Repo '.copilot/hooks/hooks.json') @('{"version":1,"hooks":{"preToolUse":[{"type":"command","bash":"$HOME/.copilot/hooks/scripts/tool-guard.py"}]}}')
    Write-FixtureFile (Join-Path $Repo '.gemini/global-settings.json') @('{"global":"settings"}')
    Write-FixtureFile (Join-Path $Repo '.gemini/settings.json') @('{"local":"settings"}')
    Write-FixtureFile (Join-Path $Repo '.gemini/hooks/scripts/test-hook.py') @('print("hook")')
    Write-FixtureFile (Join-Path $Repo '.copilot/hooks/scripts/test-hook.py') @('print("hook")')
    # Uppercase extension: must NOT be treated as a hook script (find -name is case-sensitive).
    Write-FixtureFile (Join-Path $Repo '.copilot/hooks/scripts/test-upper.PY') @('print("upper hook")')
    Write-FixtureFile (Join-Path $Repo '.gemini/hooks/scripts/test-hook.sh') @('#!/bin/bash', 'echo hook')
    Write-FixtureFile (Join-Path $Repo '.copilot/hooks/scripts/test-hook.sh') @('#!/bin/bash', 'echo hook')
    Add-GeneratedHookFixture $Repo
}

function Get-PythonForFixture {
    $python = @(Get-Command python3 -CommandType Application -ErrorAction SilentlyContinue)[0]
    $arguments = @()
    if ($null -eq $python) {
        $python = @(Get-Command py -CommandType Application -ErrorAction SilentlyContinue)[0]
        $arguments = @('-3')
    }
    if ($null -eq $python) {
        Fail 'Missing Python executable: expected python3 or py for generated-hook fixtures.'
    }
    return [pscustomobject]@{
        Path = $python.Source
        Arguments = $arguments
    }
}

function Add-GeneratedHookFixture {
    param([string]$Repo)

    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/generate-hooks.py') -Destination (Join-Path $Repo 'scripts/generate-hooks.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'hooks') -Destination (Join-Path $Repo 'hooks') -Recurse -Force
    Get-ChildItem -LiteralPath (Join-Path $Repo 'hooks') -Force -Recurse -Directory |
        Where-Object { $_.Name -ceq '__pycache__' } |
        Remove-Item -Recurse -Force

    $python = Get-PythonForFixture
    $copyTargets = @'
import os
import shutil
import sys
from pathlib import Path

source_root = Path(sys.argv[1])
fixture_root = Path(sys.argv[2])
sys.path.insert(0, str(fixture_root))
from hooks.manifest import targets

for target in targets():
    source = source_root.joinpath(*target.output_path.parts)
    destination = fixture_root.joinpath(*target.output_path.parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    os.chmod(destination, target.mode)
'@
    $oldBytecode = [System.Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', [System.EnvironmentVariableTarget]::Process)
    try {
        [System.Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', '1', [System.EnvironmentVariableTarget]::Process)
        & $python.Path @($python.Arguments) -c $copyTargets $RepoRoot $Repo
        if ($LASTEXITCODE -ne 0) {
            Fail 'Could not populate generated-hook fixture targets from hooks.manifest.targets().'
        }
    }
    finally {
        [System.Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', $oldBytecode, [System.EnvironmentVariableTarget]::Process)
    }
}

function Get-GeneratedRtkOutputPath {
    param([string]$Repo)

    $python = Get-PythonForFixture
    $script = @'
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from hooks.manifest import targets

for target in targets():
    if target.family == "rtk" and target.provider == "copilot":
        print(target.output_path.as_posix())
        break
else:
    raise SystemExit("fixture manifest did not declare a Copilot RTK target")
'@
    $oldBytecode = [System.Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', [System.EnvironmentVariableTarget]::Process)
    try {
        [System.Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', '1', [System.EnvironmentVariableTarget]::Process)
        $output = & $python.Path @($python.Arguments) -c $script $Repo
        if ($LASTEXITCODE -ne 0) {
            Fail 'Could not resolve the generated Copilot RTK output from hooks.manifest.targets().'
        }
        return $output
    }
    finally {
        [System.Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', $oldBytecode, [System.EnvironmentVariableTarget]::Process)
    }
}

function Get-TreeFingerprint {
    param([string]$Path)

    $python = Get-PythonForFixture
    $script = @'
import hashlib
import os
import stat
import sys
from pathlib import Path

root = Path(sys.argv[1])
digest = hashlib.sha256()
for path in sorted((root, *root.rglob("*")), key=lambda item: item.relative_to(root).as_posix() if item != root else ""):
    relative = "." if path == root else path.relative_to(root).as_posix()
    details = path.lstat()
    digest.update(f"{relative}\0{stat.S_IFMT(details.st_mode)}\0{stat.S_IMODE(details.st_mode)}\0".encode())
    if stat.S_ISLNK(details.st_mode):
        digest.update(os.readlink(path).encode())
    elif stat.S_ISREG(details.st_mode):
        # PowerShell updates this host-owned file on every child launch.
        if relative.casefold() != "appdata/local/microsoft/powershell/startupprofiledata-noninteractive":
            digest.update(path.read_bytes())
    digest.update(b"\0")
print(digest.hexdigest())
'@
    $output = & $python.Path @($python.Arguments) -c $script $Path
    if ($LASTEXITCODE -ne 0) {
        Fail 'Could not fingerprint the pre-populated installer destination tree.'
    }
    return $output
}

function Assert-NoBytecodeCache {
    param([string]$Repo)

    $cache = Get-ChildItem -LiteralPath $Repo -Force -Recurse -Directory |
        Where-Object { $_.Name -ceq '__pycache__' } |
        Select-Object -First 1
    Assert-True -Condition ($null -eq $cache) -Message 'Expected generator preflight to create no __pycache__ directories.'
}

function Test-FreshGeneratedHooksPreflightInstallsWithoutBytecode {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        Assert-NoBytecodeCache $repo
        Assert-True -Condition (Test-Path -LiteralPath (Join-Path $homeDir '.copilot/hooks/scripts/rtk-hook-copilot.py') -PathType Leaf) -Message 'Expected fresh generated Copilot RTK output to be installed.'
        Assert-True -Condition (Test-Path -LiteralPath (Join-Path $homeDir '.gemini/hooks/scripts/rtk-hook-gemini.py') -PathType Leaf) -Message 'Expected fresh generated Gemini RTK output to be installed.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-StaleGeneratedHooksStopBeforeDestinationMutation {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $codex = Join-Path $workdir 'codex'

        New-FixtureRepo $repo
        $outputPath = Get-GeneratedRtkOutputPath $repo
        Add-Content -LiteralPath (Join-Path $repo $outputPath) -Value '# stale fixture output' -Encoding utf8NoBOM
        Write-FixtureFile (Join-Path $homeDir 'preserved/sentinel.txt') @('do not change')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $before = Get-TreeFingerprint $homeDir
        Write-FixtureFile (Join-Path $codex 'sentinel') @('sentinel')
        $beforeCodex = Get-TreeFingerprint $codex

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected stale generated hooks to exit install.ps1 with code 1.'
        Assert-True -Condition (($result.Stderr -join "`n") -match [regex]::Escape($outputPath)) -Message 'Expected stale repository-relative output path on stderr.'
        Assert-Equals '' ($result.Stdout -join "`n") 'Expected no stdout for stale generated hooks.'
        Assert-True -Condition (($result.Stderr -join "`n") -match [regex]::Escape('python3 scripts/generate-hooks.py --write')) -Message 'Expected stale-output recovery command on stderr.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected stale preflight to leave the destination tree byte-for-byte unchanged with no new directories.'
        Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected stale preflight not to mutate external CODEX_HOME.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-GeneratorFailureStopsBeforeDestinationMutation {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $codex = Join-Path $workdir 'codex'

        New-FixtureRepo $repo
        $manifestPath = Join-Path $repo 'hooks/manifest.py'
        $manifest = Get-Content -LiteralPath $manifestPath -Raw
        Set-Content -LiteralPath $manifestPath -Value $manifest.Replace('GeneratedTarget("send_event", "copilot"', 'GeneratedTarget("send_event", "unknown"') -Encoding utf8NoBOM -NoNewline
        Write-FixtureFile (Join-Path $homeDir 'preserved/sentinel.txt') @('do not change')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $before = Get-TreeFingerprint $homeDir
        Write-FixtureFile (Join-Path $codex 'sentinel') @('sentinel')
        $beforeCodex = Get-TreeFingerprint $codex

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected a generator failure to become installer exit 1.'
        Assert-True -Condition (($result.Stderr -join "`n") -match "Unknown provider 'unknown'") -Message 'Expected the generator diagnostic on stderr.'
        Assert-True -Condition (($result.Stderr -join "`n") -notmatch [regex]::Escape('python3 scripts/generate-hooks.py --write')) -Message 'Expected generator failures to omit stale-output recovery advice.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected generator failure preflight to leave the destination tree byte-for-byte unchanged with no new directories.'
        Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected generator failure not to mutate external CODEX_HOME.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

# Runs the fixture's install.ps1 in a child pwsh with HOME/USERPROFILE redirected to $HomeDir.
# The PS7 automatic $HOME is fixed at process start, so the process environment must be
# changed before the child launches. $env:HOME is read-only in pwsh 7.4+, so the .NET
# Environment API is used instead (a $null value removes the variable). Both vars are set
# so the redirect works on Unix (HOME) and Windows (USERPROFILE).
# The child's streams are captured via file redirection (1>/2> into temp files under
# $Workdir), which preserves stream identity regardless of how a pwsh build types merged
# native stderr. Each file is read back as a line array; a missing or empty stream yields
# an empty array (never a phantom $null element). Returns an object with Stdout, Stderr,
# and ExitCode, so callers can assert on expected failing runs without treating them as
# test errors.
function Invoke-InstallProcess {
    param(
        [string]$Repo,
        [string]$HomeDir,
        [string]$Workdir,
        [string]$CodexHome = $null,
        [string[]]$InstallArguments = @(),
        [string]$ForestServiceValue = $null
    )

    $oldForestService = [System.Environment]::GetEnvironmentVariable('INSTALL_FOREST_SERVICE_SKILLS', [System.EnvironmentVariableTarget]::Process)
    $oldAppData = [System.Environment]::GetEnvironmentVariable('APPDATA', [System.EnvironmentVariableTarget]::Process)
    $oldLocalAppData = [System.Environment]::GetEnvironmentVariable('LOCALAPPDATA', [System.EnvironmentVariableTarget]::Process)
    $oldHome = [System.Environment]::GetEnvironmentVariable('HOME', [System.EnvironmentVariableTarget]::Process)
    $oldUserProfile = [System.Environment]::GetEnvironmentVariable('USERPROFILE', [System.EnvironmentVariableTarget]::Process)
    $oldCodexHome = [System.Environment]::GetEnvironmentVariable('CODEX_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldPath = [System.Environment]::GetEnvironmentVariable('PATH', [System.EnvironmentVariableTarget]::Process)
    $oldXdgCacheHome = [System.Environment]::GetEnvironmentVariable('XDG_CACHE_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgConfigHome = [System.Environment]::GetEnvironmentVariable('XDG_CONFIG_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgDataHome = [System.Environment]::GetEnvironmentVariable('XDG_DATA_HOME', [System.EnvironmentVariableTarget]::Process)
    $childStdoutPath = Join-Path $Workdir 'child-stdout.txt'
    $childStderrPath = Join-Path $Workdir 'child-stderr.txt'
    try {
        [System.Environment]::SetEnvironmentVariable('INSTALL_FOREST_SERVICE_SKILLS', $ForestServiceValue, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('APPDATA', (Join-Path $HomeDir 'AppData/Roaming'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('LOCALAPPDATA', (Join-Path $HomeDir 'AppData/Local'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('HOME', $HomeDir, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('USERPROFILE', $HomeDir, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('CODEX_HOME', $CodexHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('PATH', "$(Join-Path $Repo 'bin')$([System.IO.Path]::PathSeparator)$oldPath", [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', (Join-Path $Workdir 'xdg-cache'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', (Join-Path $Workdir 'xdg-config'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', (Join-Path $Workdir 'xdg-data'), [System.EnvironmentVariableTarget]::Process)
        & pwsh -NoProfile -File (Join-Path $Repo 'scripts/install.ps1') @InstallArguments 1> $childStdoutPath 2> $childStderrPath
        $exitCode = $LASTEXITCODE
        $stdout = @()
        if (Test-Path -LiteralPath $childStdoutPath) {
            $stdout = @(Get-Content -LiteralPath $childStdoutPath)
        }
        $stderr = @()
        if (Test-Path -LiteralPath $childStderrPath) {
            $stderr = @(Get-Content -LiteralPath $childStderrPath)
        }
    }
    finally {
        [System.Environment]::SetEnvironmentVariable('INSTALL_FOREST_SERVICE_SKILLS', $oldForestService, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('APPDATA', $oldAppData, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('LOCALAPPDATA', $oldLocalAppData, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('HOME', $oldHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('USERPROFILE', $oldUserProfile, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('CODEX_HOME', $oldCodexHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('PATH', $oldPath, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', $oldXdgCacheHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', $oldXdgConfigHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', $oldXdgDataHome, [System.EnvironmentVariableTarget]::Process)
        Remove-Item -LiteralPath $childStdoutPath -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $childStderrPath -Force -ErrorAction SilentlyContinue
    }
    return [pscustomobject]@{
        Stdout   = $stdout
        Stderr   = $stderr
        ExitCode = $exitCode
    }
}

# A child pwsh initializes startup state under HOME before a preflight mutation snapshot.
# PowerShell updates one host-owned startup-data file on each child launch; its content is
# excluded from the fingerprint while its path, type, and mode remain covered.
function Initialize-ChildPowerShellHome {
    param(
        [string]$HomeDir,
        [string]$Workdir
    )

    $oldAppData = [System.Environment]::GetEnvironmentVariable('APPDATA', [System.EnvironmentVariableTarget]::Process)
    $oldLocalAppData = [System.Environment]::GetEnvironmentVariable('LOCALAPPDATA', [System.EnvironmentVariableTarget]::Process)
    $oldHome = [System.Environment]::GetEnvironmentVariable('HOME', [System.EnvironmentVariableTarget]::Process)
    $oldUserProfile = [System.Environment]::GetEnvironmentVariable('USERPROFILE', [System.EnvironmentVariableTarget]::Process)
    $oldXdgCacheHome = [System.Environment]::GetEnvironmentVariable('XDG_CACHE_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgConfigHome = [System.Environment]::GetEnvironmentVariable('XDG_CONFIG_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgDataHome = [System.Environment]::GetEnvironmentVariable('XDG_DATA_HOME', [System.EnvironmentVariableTarget]::Process)
    try {
        [System.Environment]::SetEnvironmentVariable('APPDATA', (Join-Path $HomeDir 'AppData/Roaming'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('LOCALAPPDATA', (Join-Path $HomeDir 'AppData/Local'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('HOME', $HomeDir, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('USERPROFILE', $HomeDir, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', (Join-Path $Workdir 'xdg-cache'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', (Join-Path $Workdir 'xdg-config'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', (Join-Path $Workdir 'xdg-data'), [System.EnvironmentVariableTarget]::Process)
        & pwsh -NoProfile -Command ''
        if ($LASTEXITCODE -ne 0) {
            Fail 'Could not initialize the child PowerShell home for the fixture snapshot.'
        }
    }
    finally {
        [System.Environment]::SetEnvironmentVariable('APPDATA', $oldAppData, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('LOCALAPPDATA', $oldLocalAppData, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('HOME', $oldHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('USERPROFILE', $oldUserProfile, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', $oldXdgCacheHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', $oldXdgConfigHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', $oldXdgDataHome, [System.EnvironmentVariableTarget]::Process)
    }
}

# Like Invoke-InstallProcess, but fails the test suite when the child exits non-zero.
function Invoke-Install {
    param(
        [string]$Repo,
        [string]$HomeDir,
        [string]$Workdir,
        [string]$CodexHome = $null
    )

    $result = Invoke-InstallProcess -Repo $Repo -HomeDir $HomeDir -Workdir $Workdir -CodexHome $CodexHome
    if ($result.ExitCode -ne 0) {
        foreach ($line in $result.Stdout) {
            [Console]::Error.WriteLine($line)
        }
        foreach ($line in $result.Stderr) {
            [Console]::Error.WriteLine($line)
        }
        Fail "install.ps1 exited with code $($result.ExitCode) (expected 0)."
    }
}

function Test-PreservesFileModes {
    if ($IsWindows) {
        Write-Host "Skipping: Unix file mode assertions do not apply on Windows."
        return
    }

    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        $toolSrc = Join-Path $repo 'skills/default/alpha/tool.sh'
        $toolSrcMode = [System.IO.File]::GetUnixFileMode($toolSrc)
        Assert-True -Condition (([int]$toolSrcMode -band [int][System.IO.UnixFileMode]::UserExecute) -ne 0) -Message "Fixture setup error: $toolSrc should be executable."

        $skillSrc = Join-Path $repo 'skills/default/alpha/SKILL.md'
        $skillSrcMode = [System.IO.File]::GetUnixFileMode($skillSrc)

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        # A non-default (executable) source mode must survive the copy.
        $installedTool = Join-Path $homeDir '.agents/skills/alpha/tool.sh'
        $installedToolMode = [System.IO.File]::GetUnixFileMode($installedTool)
        Assert-Equals -Expected $toolSrcMode -Actual $installedToolMode -Message "Expected the installed tool.sh to keep the source file mode (source: $toolSrcMode)."

        # A default 644 source file must keep its exact source mode (like cp -p).
        $installedSkillMode = [System.IO.File]::GetUnixFileMode((Join-Path $homeDir '.agents/skills/alpha/SKILL.md'))
        Assert-Equals -Expected $skillSrcMode -Actual $installedSkillMode -Message "Expected the installed SKILL.md to keep the exact source file mode (source: $skillSrcMode)."

        # A 644 agent file must keep its default mode in both agent destinations.
        $agentExpectedMode = [System.IO.File]::GetUnixFileMode((Join-Path $repo 'agents/helper.md'))
        $agentDestMode = [System.IO.File]::GetUnixFileMode((Join-Path $homeDir '.gemini/agents/helper.md'))
        Assert-Equals -Expected $agentExpectedMode -Actual $agentDestMode -Message "Expected the installed Gemini agent to keep the source file mode."
        $copilotAgentMode = [System.IO.File]::GetUnixFileMode((Join-Path $homeDir '.copilot/agents/helper.md'))
        Assert-Equals -Expected $agentExpectedMode -Actual $copilotAgentMode -Message "Expected the installed Copilot agent to keep the source file mode."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-RebasesSharedReferenceLinksForFlatInstalledSkills {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        Write-FixtureFile (Join-Path $repo 'skills/default/alpha/SKILL.md') @(
            '---',
            'name: alpha',
            '---',
            'See [single](./../../../references/notes.md) and `[repeated](././../../../references/notes.md)`.',
            'Keep ~/.agents/skills/alpha and example/../../../references/notes.md unchanged.'
        )
        Write-FixtureFile (Join-Path $repo 'skills/default/alpha/nested/note.markdown') @('[nested](./../../../../references/notes.md)')
        $sourceBefore = Get-TreeFingerprint (Join-Path $repo 'skills/default/alpha')

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        Assert-Equals 0 $result.ExitCode ($result.Stderr -join "`n")

        $installedSkillPath = Join-Path $homeDir '.agents/skills/alpha/SKILL.md'
        $installedSkill = Read-FileContent $installedSkillPath
        Assert-Equals -Expected "---`nname: alpha`n---`nSee [single](../../references/notes.md) and ``[repeated](../../references/notes.md)``.`nKeep ~/.agents/skills/alpha and example/../../../references/notes.md unchanged." -Actual $installedSkill -Message 'Expected a shared-reference Markdown link to be rebased for the flat installed skill path.'
        Assert-True -Condition (Test-Path -LiteralPath (Join-Path (Split-Path $installedSkillPath) '../../references/notes.md')) -Message 'Expected the installed shared-reference link to resolve inside ~/.agents/references.'
        Assert-Equals '[nested](../../../references/notes.md)' (Read-FileContent (Join-Path $homeDir '.agents/skills/alpha/nested/note.markdown')) 'Expected leading ./ in nested Markdown to rebase.'
        Assert-True (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/nested/../../../references/notes.md')) 'Expected the nested installed link to resolve.'
        Assert-Equals $sourceBefore (Get-TreeFingerprint (Join-Path $repo 'skills/default/alpha')) 'Expected rebasing not to mutate source bytes or modes.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-RebasesReadOnlyMarkdownAndPreservesModesOnRepeat {
    $workdir = New-TestWorkdir
    $python = Get-PythonForFixture
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        $prepare = @'
from pathlib import Path
import os
import sys
repo, home = map(Path, sys.argv[1:])
source = repo / 'skills/default/locked'
(source / 'nested').mkdir(parents=True)
(source / 'evals/nested').mkdir(parents=True)
(source / 'SKILL.md').write_bytes('See [shared](../../../references/notes.md).\r\nKeep unicode: café.\r\n'.encode())
(source / 'nested/note.md').write_bytes(b'[nested](../../../../references/notes.md)\n')
(source / 'evals/nested/evals.json').write_bytes(b'excluded eval fixture\n')
for name in ('README.md', 'LICENSE.txt', 'LICENSE.md'):
    (source / name).write_bytes(b'excluded fixture\n')
installed = home / '.agents/skills/locked'
installed.mkdir(parents=True)
(installed / 'SKILL.md').write_bytes(b'stale writable copy\n')
os.chmod(installed / 'SKILL.md', 0o640)
os.chmod(installed, 0o770)
for path in (source, *source.rglob('*')):
    if path.is_file():
        os.chmod(path, 0o444)
    elif os.name != 'nt':
        os.chmod(path, 0o555)
'@
        & $python.Path @($python.Arguments) -c $prepare $repo $homeDir
        Assert-Equals 0 $LASTEXITCODE 'Expected read-only fixture creation to succeed.'
        $before = Get-TreeFingerprint (Join-Path $repo 'skills/default/locked')
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        Assert-Equals 0 $result.ExitCode ($result.Stderr -join "`n")
        $verify = @'
from pathlib import Path
import os
import stat
import sys
source = Path(sys.argv[1]) / 'skills/default/locked'
installed = Path(sys.argv[2]) / '.agents/skills/locked'
for relative, prefix in [('SKILL.md', '../../'), ('nested/note.md', '../../../')]:
    target = installed / relative
    expected = (source / relative).read_bytes().replace(b'../../../references/', b'../../references/', 1)
    assert target.read_bytes() == expected, relative
    if os.name == 'nt':
        assert target.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY, relative
    else:
        assert stat.S_IMODE(target.stat().st_mode) == 0o444, relative
    assert (target.parent / f'{prefix}references/notes.md').resolve() == (installed.parent.parent / 'references/notes.md').resolve()
    assert (target.parent / f'{prefix}references/notes.md').is_file()
if os.name != 'nt':
    for path in (installed, installed / 'nested'):
        assert stat.S_IMODE(path.stat().st_mode) == 0o555, path
assert sorted(p.relative_to(installed).as_posix() for p in installed.rglob('*')) == ['SKILL.md', 'nested', 'nested/note.md']
'@
        & $python.Path @($python.Arguments) -c $verify $repo $homeDir
        Assert-Equals 0 $LASTEXITCODE 'Expected exact installed bytes, directory/file modes, references, and no temporary artifacts.'
        $installedBefore = Get-TreeFingerprint (Join-Path $homeDir '.agents/skills/locked')
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        Assert-Equals 0 $result.ExitCode ($result.Stderr -join "`n")
        Assert-Equals $before (Get-TreeFingerprint (Join-Path $repo 'skills/default/locked')) 'Expected read-only source bytes and directory/file modes unchanged.'
        Assert-Equals $installedBefore (Get-TreeFingerprint (Join-Path $homeDir '.agents/skills/locked')) 'Expected repeat installs to preserve rebased bytes and modes without temporary artifacts.'

        if ($IsWindows) {
            Write-Host 'Skipping: POSIX directory/file modes and unreadable000 copy-failure assertions do not prove NTFS ACL behavior.'
            return
        }

        $failCopy = @'
from pathlib import Path
import os
import sys
source = Path(sys.argv[1]) / 'skills/default/locked'
os.chmod(source, 0o755)
(source / 'unreadable.txt').write_bytes(b'unreadable source\n')
os.chmod(source / 'unreadable.txt', 0o000)
os.chmod(source, 0o555)
'@
        & $python.Path @($python.Arguments) -c $failCopy $repo
        Assert-Equals 0 $LASTEXITCODE 'Expected public copy-failure fixture creation to succeed.'
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        Assert-Equals 1 $result.ExitCode 'Expected an unreadable source to stop installation.'
        $verifyModes = @'
from pathlib import Path
import stat
import sys
root = Path(sys.argv[1])
for relative, mode in [('.', 0o555), ('nested', 0o555), ('SKILL.md', 0o444), ('nested/note.md', 0o444)]:
    assert stat.S_IMODE((root / relative).stat().st_mode) == mode, relative
assert not any(p.name.startswith('.rebase-') for p in root.rglob('*'))
'@
        & $python.Path @($python.Arguments) -c $verifyModes (Join-Path $homeDir '.agents/skills/locked')
        Assert-Equals 0 $LASTEXITCODE 'Expected temporary destination permission changes to be restored after public copy failure.'
    }
    finally {
        # Only regular fixture paths need permission repair for cleanup.
        & $python.Path @($python.Arguments) -c 'import os,sys; from pathlib import Path; root=Path(sys.argv[1]); [os.chmod(p,0o755 if p.is_dir() else 0o644) for p in root.rglob("*") if not p.is_symlink()]' $workdir
        Remove-Workdir $workdir
    }
}

function Test-ActualAddySharedReferencesResolveAfterInstall {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        foreach ($name in @('addy-code-review-and-quality', 'addy-performance-optimization', 'addy-security-and-hardening')) {
            $destination = Join-Path $repo "skills/default/$name"
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
            Copy-Item -LiteralPath (Join-Path $RepoRoot "skills/default/$name/SKILL.md") -Destination (Join-Path $destination 'SKILL.md') -Force
        }
        foreach ($name in @('security-checklist.md', 'performance-checklist.md')) {
            Copy-Item -LiteralPath (Join-Path $RepoRoot "references/$name") -Destination (Join-Path $repo "references/$name") -Force
        }
        $before = Get-TreeFingerprint (Join-Path $repo 'skills')
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        Assert-Equals 0 $result.ExitCode ($result.Stderr -join "`n")
        $python = Get-PythonForFixture
        $verify = @'
from pathlib import Path
import re
import sys
repo, home = map(Path, sys.argv[1:])
count = 0
for name in ('addy-code-review-and-quality', 'addy-performance-optimization', 'addy-security-and-hardening'):
    source = repo / 'skills/default' / name / 'SKILL.md'
    installed = home / '.agents/skills' / name / 'SKILL.md'
    links = re.findall(r'`(\.\./\.\./\.\./references/[^`]+)`', source.read_text())
    assert links, name
    assert installed.read_bytes() == source.read_bytes().replace(b'../../../references/', b'../../references/'), name
    for link in links:
        source_target = (source.parent / link).resolve()
        installed_target = (installed.parent / link.removeprefix('../')).resolve()
        assert source_target.parent == (repo / 'references').resolve()
        assert installed_target.parent == (home / '.agents/references').resolve()
        assert source_target.read_bytes() == installed_target.read_bytes()
        count += 1
assert count == 8, count
'@
        & $python.Path @($python.Arguments) -c $verify $repo $homeDir
        Assert-Equals 0 $LASTEXITCODE 'Expected all eight actual Addy pointers to resolve in source and flat installed copies.'
        Assert-Equals $before (Get-TreeFingerprint (Join-Path $repo 'skills')) 'Expected actual Addy skill definitions unchanged in source.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-PrunesWithoutOptionalSharedReferences {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        Remove-Item -LiteralPath (Join-Path $repo 'references') -Recurse -Force
        Write-FixtureFile (Join-Path $repo 'skills/default/alpha/SKILL.md') @('---', 'name: alpha', '---', 'See ../../../references/unavailable.md.')
        foreach ($name in @('README.md', 'LICENSE.txt', 'LICENSE.md')) {
            Write-FixtureFile (Join-Path $repo "skills/default/alpha/$name") @('excluded fixture')
        }
        foreach ($pass in @('first', 'repeat')) {
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
            Assert-Equals 0 $result.ExitCode ($result.Stderr -join "`n")
            Assert-Equals (Read-FileContent (Join-Path $repo 'skills/default/alpha/SKILL.md')) (Read-FileContent (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')) 'Expected absent shared references to skip rebasing.'
            foreach ($name in @('evals', 'README.md', 'LICENSE.txt', 'LICENSE.md')) {
                Assert-True (-not (Test-Path -LiteralPath (Join-Path $homeDir ".agents/skills/alpha/$name"))) 'Expected pruning even without optional shared references.'
            }
        }
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-PruningReadOnlyHardLinkPreservesExternalInode {
    $workdir = New-TestWorkdir
    $python = Get-PythonForFixture
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $outside = Join-Path $workdir 'external.md'
        New-FixtureRepo $repo
        $prepare = @'
from pathlib import Path
import os
import sys
outside, home = map(Path, sys.argv[1:])
outside.write_bytes(b'external bytes must remain untouched\n')
os.chmod(outside, 0o444)
installed = home / '.agents/skills/alpha/evals/stale.md'
installed.parent.mkdir(parents=True)
os.link(outside, installed)
print(outside.stat().st_ino)
'@
        $beforeInode = & $python.Path @($python.Arguments) -c $prepare $outside $homeDir
        Assert-Equals 0 $LASTEXITCODE 'Expected external hard-link fixture creation to succeed.'
        $before = Get-TreeFingerprint $outside
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        if ($IsWindows) {
            Assert-Equals 1 $result.ExitCode 'Expected pruning to refuse a shared Windows ReadOnly attribute.'
            Assert-True (($result.Stderr -join "`n").Contains('Refusing to change read-only hard-linked file')) 'Expected an actionable hard-link refusal.'
            Assert-True (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/evals/stale.md')) 'Expected the shared readonly installed name to remain intact on refusal.'
        }
        else {
            Assert-Equals 0 $result.ExitCode ($result.Stderr -join "`n")
            Assert-True (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/evals'))) 'Expected the stale installed evals name to be pruned.'
        }
        Assert-Equals $before (Get-TreeFingerprint $outside) 'Expected external hard-linked bytes and mode unchanged.'
        $verify = @'
from pathlib import Path
import os
import stat
import sys
outside = Path(sys.argv[1])
assert outside.read_bytes() == b'external bytes must remain untouched\n'
assert outside.stat().st_ino == int(sys.argv[2])
if os.name == 'nt':
    assert outside.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
    assert outside.stat().st_nlink == 2
else:
    assert stat.S_IMODE(outside.stat().st_mode) == 0o444
    assert outside.stat().st_nlink == 1
'@
        & $python.Path @($python.Arguments) -c $verify $outside $beforeInode
        Assert-Equals 0 $LASTEXITCODE 'Expected external inode identity, original bytes, mode, and link count after pruning/refusal.'
    }
    finally {
        & $python.Path @($python.Arguments) -c 'import os,sys; from pathlib import Path; root=Path(sys.argv[1]); [os.chmod(p,0o755 if p.is_dir() else 0o644) for p in root.rglob("*") if not p.is_symlink()]' $workdir
        Remove-Workdir $workdir
    }
}

function Test-ReadOnlyHardLinkCopyRefusesExternalMutation {
    $workdir = New-TestWorkdir
    $python = Get-PythonForFixture
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $outside = Join-Path $workdir 'external.md'
        New-FixtureRepo $repo
        $prepare = @'
from pathlib import Path
import os
import sys
outside, home = map(Path, sys.argv[1:])
outside.write_bytes(b'external bytes must remain untouched; see ../../../references/notes.md.\n')
os.chmod(outside, 0o444)
installed = home / '.agents/skills/alpha/SKILL.md'
installed.parent.mkdir(parents=True)
os.link(outside, installed)
'@
        & $python.Path @($python.Arguments) -c $prepare $outside $homeDir
        Assert-Equals 0 $LASTEXITCODE 'Expected external hard-link fixture creation to succeed.'
        $before = Get-TreeFingerprint $outside
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome (Join-Path $workdir 'codex')
        Assert-Equals 1 $result.ExitCode 'Expected a read-only hard-linked destination to stop copying before external mutation.'
        Assert-True (($result.Stderr -join "`n").Contains('Refusing to change read-only hard-linked file')) 'Expected an actionable hard-link refusal.'
        Assert-Equals $before (Get-TreeFingerprint $outside) 'Expected external hard-linked bytes and mode unchanged after copy refusal.'
        & $python.Path @($python.Arguments) (Join-Path $repo 'scripts/rebase-skill-references.py') `
            --source-dir (Join-Path $repo 'skills/default/alpha') `
            --destination-dir (Join-Path $homeDir '.agents/skills/alpha') `
            --references-source (Join-Path $repo 'references') `
            --references-destination (Join-Path $homeDir '.agents/references') 1>(Join-Path $workdir 'rebase.out') 2>(Join-Path $workdir 'rebase.err')
        Assert-Equals 1 $LASTEXITCODE 'Expected direct rebasing to refuse a read-only shared inode before permission changes.'
        Assert-True ((Read-FileContent (Join-Path $workdir 'rebase.err')).Contains('Refusing to change read-only hard-linked file')) 'Expected the direct rebasing refusal to name the unsafe inode.'
        Assert-Equals $before (Get-TreeFingerprint $outside) 'Expected direct rebasing refusal to leave external bytes and mode unchanged.'
        $verify = @'
from pathlib import Path
import sys
outside, installed = map(Path, sys.argv[1:])
assert outside.stat().st_ino == installed.stat().st_ino
assert outside.stat().st_nlink == 2
'@
        & $python.Path @($python.Arguments) -c $verify $outside (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')
        Assert-Equals 0 $LASTEXITCODE 'Expected both names of the external inode to remain intact after refusal.'
    }
    finally {
        & $python.Path @($python.Arguments) -c 'import os,sys; from pathlib import Path; root=Path(sys.argv[1]); [os.chmod(p,0o755 if p.is_dir() else 0o644) for p in root.rglob("*") if not p.is_symlink()]' $workdir
        Remove-Workdir $workdir
    }
}

function Test-RootLinkedSkillIsPreservedWithoutExternalMutation {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $externalSkill = Join-Path $workdir 'external-skill'
        $nestedTarget = Join-Path $workdir 'nested-link-target'

        New-FixtureRepo $repo
        Write-FixtureFile (Join-Path $externalSkill 'SKILL.md') @(
            '---',
            'name: linked-skill',
            '---',
            'See [the shared reference](../repo/references/shared.md).'
        )
        Write-FixtureFile (Join-Path $externalSkill 'evals/keep.txt') @('external evals must remain untouched')
        Write-FixtureFile (Join-Path $nestedTarget 'note.md') @('See [the shared reference](../../../../references/shared.md).')
        $externalBefore = Get-TreeFingerprint $externalSkill
        $nestedBefore = Get-TreeFingerprint $nestedTarget

        try {
            New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'skills/default/linked-skill') -Target $externalSkill -Force | Out-Null
            New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'skills/default/alpha/linked-dir') -Target $nestedTarget -Force | Out-Null
        }
        catch {
            Write-Host "Skipping: symlink creation is not supported on this host ($($_.Exception.Message))."
            return
        }

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        $installedSkillPath = Join-Path $homeDir '.agents/skills/linked-skill'
        $installedSkill = Get-Item -Force -LiteralPath $installedSkillPath
        Assert-Equals -Expected 'SymbolicLink' -Actual $installedSkill.LinkType -Message 'Expected a root-linked skill to remain a symlink after installation.'
        Assert-Equals -Expected $externalSkill -Actual $installedSkill.Target -Message 'Expected a root-linked skill to retain its raw target.'
        $python = Get-PythonForFixture
        & $python.Path @($python.Arguments) (Join-Path $repo 'scripts/rebase-skill-references.py') `
            --source-dir (Join-Path $repo 'skills/default/linked-skill') `
            --destination-dir $installedSkillPath `
            --references-source (Join-Path $repo 'references') `
            --references-destination (Join-Path $homeDir '.agents/references')
        if ($LASTEXITCODE -ne 0) {
            Fail 'Reference rebasing should skip a root-linked skill.'
        }
        Assert-Equals -Expected $externalBefore -Actual (Get-TreeFingerprint $externalSkill) -Message 'Expected installation to leave a root-linked skill target byte-for-byte unchanged.'
        Assert-Equals -Expected $nestedBefore -Actual (Get-TreeFingerprint $nestedTarget) -Message 'Expected reference rebasing to leave a nested linked directory target byte-for-byte unchanged.'
        Assert-Equals -Expected 'See [the shared reference](../../../../references/shared.md).' -Actual (Read-FileContent (Join-Path $nestedTarget 'note.md')) -Message 'Expected reference rebasing to skip Markdown reached through a nested directory link.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-ExcludesAndPrunesSkillEvals {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        New-Item -ItemType Directory -Path (Join-Path $homeDir '.agents/skills/alpha/evals') -Force | Out-Null
        Write-FixtureFile (Join-Path $homeDir '.agents/skills/alpha/evals/stale.txt') @('stale eval content')
        Write-FixtureFile (Join-Path $homeDir '.agents/skills/alpha/existing-note.txt') @('keep this installed note')

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        Assert-True -Condition (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')) -Message "Expected skills/default/alpha to install at ~/.agents/skills/alpha without a category wrapper."
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/default'))) -Message "Expected category directories not to install as skills."
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/forest-service'))) -Message "Expected the empty Forest Service marker not to install as a skill."

        $copiedSkill = Read-FileContent (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')
        Assert-Equals -Expected "---`nname: alpha`n---`nStandalone." -Actual $copiedSkill -Message "Expected non-evals skill content to remain installed."

        $copiedExistingNote = Read-FileContent (Join-Path $homeDir '.agents/skills/alpha/existing-note.txt')
        Assert-Equals -Expected "keep this installed note" -Actual $copiedExistingNote -Message "Expected existing non-evals installed content to remain after eval cleanup."

        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/evals'))) -Message "Expected ~/.agents/skills/alpha/evals to be removed during install."
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/beta-workspace'))) -Message "Expected *-workspace skills to remain excluded from top-level selection."
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/archive'))) -Message "Expected archive entries to remain excluded from top-level selection."
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/weird[1]-workspace'))) -Message "Expected weird[1]-workspace to remain excluded (brackets in the name must stay literal)."
        $myWorkspaceSkill = Join-Path $homeDir '.agents/skills/My-Workspace/SKILL.md'
        Assert-True -Condition (Test-Path -LiteralPath $myWorkspaceSkill) -Message "Expected the case-variant My-Workspace skill to be installed (the -workspace suffix match is case-sensitive, like bash)."
        Assert-Equals -Expected "case-variant workspace name should copy" -Actual (Read-FileContent $myWorkspaceSkill) -Message "Expected the installed My-Workspace skill to keep its fixture content."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-SymlinkHandling {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        # A secret target outside the repo: the installer must never copy its contents.
        $secretTargetPath = Join-Path $workdir 'secret-target.txt'
        Write-FixtureFile $secretTargetPath @('SECRET-CONTENT-MUST-NOT-BE-COPIED')

        $dirTargetPath = Join-Path $workdir 'linked-dir-target'
        Write-FixtureFile (Join-Path $dirTargetPath 'inner.txt') @('inner content')
        $dirSentinelPath = Join-Path $dirTargetPath 'keep.txt'
        Write-FixtureFile $dirSentinelPath @('directory sentinel must not change')
        $dirSentinelBefore = Read-FileContent $dirSentinelPath
        Write-FixtureFile (Join-Path $dirTargetPath 'note.md') @('See [the shared reference](../../../../references/shared.md).')
        $dirTargetBefore = Get-TreeFingerprint $dirTargetPath

        # Deliberate skip: hosts that cannot create symlinks (e.g. Windows without the
        # link-creation privileges) report a skip instead of a false pass.
        try {
            New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'skills/default/alpha/linked-secret.txt') -Target $secretTargetPath -Force | Out-Null
            New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'skills/default/alpha/linked-dir') -Target $dirTargetPath -Force | Out-Null
        }
        catch {
            Write-Host "Skipping: symlink creation is not supported on this host ($($_.Exception.Message))."
            return
        }

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        # Core regression assertion: the file symlink must be preserved as a link object
        # (the pre-fix installer installed a regular file with the secret's contents).
        $installedSecretPath = Join-Path $homeDir '.agents/skills/alpha/linked-secret.txt'
        $installedSecret = Get-Item -Force -LiteralPath $installedSecretPath
        Assert-Equals -Expected 'SymbolicLink' -Actual $installedSecret.LinkType -Message "Expected the installed linked-secret.txt to be preserved as a symlink, not a regular file with the link target's contents."
        Assert-Equals -Expected $secretTargetPath -Actual $installedSecret.Target -Message "Expected the installed symlink to keep its raw target path."
        Assert-True -Condition (([int]$installedSecret.Attributes -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) -Message "Expected the installed linked-secret.txt to carry the ReparsePoint attribute."

        $installedDirLinkPath = Join-Path $homeDir '.agents/skills/alpha/linked-dir'
        $installedDirLink = Get-Item -Force -LiteralPath $installedDirLinkPath
        Assert-Equals -Expected 'SymbolicLink' -Actual $installedDirLink.LinkType -Message "Expected the installed linked-dir to be preserved as a symlink, not a real directory with copied contents."
        Assert-Equals -Expected $dirTargetPath -Actual $installedDirLink.Target -Message "Expected the installed linked-dir to keep its raw target path."
        Assert-True -Condition (([int]$installedDirLink.Attributes -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) -Message "Expected the installed linked-dir to carry the ReparsePoint attribute."
        Assert-Equals -Expected $dirSentinelBefore -Actual (Read-FileContent $dirSentinelPath) -Message "Expected the external directory target to remain unchanged after install."
        Assert-Equals -Expected $dirTargetBefore -Actual (Get-TreeFingerprint $dirTargetPath) -Message 'Expected reference rebasing to leave a nested linked directory target byte-for-byte unchanged.'

        # Sanity: the normal install still works alongside links (content copied, evals pruned).
        Assert-Equals -Expected "---`nname: alpha`n---`nStandalone." -Actual (Read-FileContent (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')) -Message "Expected non-evals skill content to remain installed alongside symlink entries."
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/evals'))) -Message "Expected ~/.agents/skills/alpha/evals to be removed during install even with symlink entries present."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-FixedNameHardLinkHandling {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        $hardLinkTargetPath = Join-Path $repo 'hardlink-settings-source.json'
        Write-FixtureFile $hardLinkTargetPath @('{"global":"hardlink-settings"}')
        $hardLinkSource = Join-Path $repo '.gemini/global-settings.json'
        Remove-Item -LiteralPath $hardLinkSource -Force
        try {
            New-Item -ItemType HardLink -Path $hardLinkSource -Target $hardLinkTargetPath -Force | Out-Null
        }
        catch {
            Write-Host "Skipping: hard-link creation is not supported on this host ($($_.Exception.Message))."
            return
        }
        if (-not (Test-Path -LiteralPath $hardLinkSource)) {
            Write-Host "Skipping: hard-link creation is not supported on this host."
            return
        }

        Assert-Equals -Expected 'HardLink' -Actual (Get-Item -Force -LiteralPath $hardLinkSource).LinkType -Message "Fixture setup error: expected the source file to be a hard link."

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        $installedSettingsPath = Join-Path $homeDir '.gemini/settings.json'
        $installed = Get-Item -Force -LiteralPath $installedSettingsPath
        Assert-Equals -Expected '' -Actual $installed.LinkType -Message "Expected the fixed-name hard-linked file to install as a regular file, not a preserved hard link."
        Assert-Equals -Expected 'hardlink-settings' -Actual ((Get-Content -LiteralPath $installedSettingsPath -Raw | ConvertFrom-Json -AsHashtable)['global']) -Message "Expected installed settings to retain the hard-linked source value."
        Assert-True -Condition (([int]$installed.Attributes -band [int][System.IO.FileAttributes]::ReparsePoint) -eq 0) -Message "Expected the installed settings.json to be a regular file."
        if (-not $IsWindows) {
            $ownerOnly = [System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite
            Assert-Equals -Expected $ownerOnly -Actual ([System.IO.File]::GetUnixFileMode($installedSettingsPath)) -Message "Expected merged settings.json to be owner-only."
        }
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-JunctionHandling {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        $junctionTargetPath = Join-Path $workdir 'junction-target'
        Write-FixtureFile (Join-Path $junctionTargetPath 'inner.txt') @('junction inner content')
        Write-FixtureFile (Join-Path $junctionTargetPath 'SKILL.md') @('See [the shared reference](../repo/references/shared.md).')
        Write-FixtureFile (Join-Path $junctionTargetPath 'evals/keep.txt') @('junction evals must remain untouched')
        $junctionSentinelPath = Join-Path $junctionTargetPath 'keep.txt'
        Write-FixtureFile $junctionSentinelPath @('junction sentinel must not change')
        $junctionSentinelBefore = Read-FileContent $junctionSentinelPath
        $junctionTargetBefore = Get-TreeFingerprint $junctionTargetPath

        try {
            New-Item -ItemType Junction -Path (Join-Path $repo '.gemini/junction-dir') -Target $junctionTargetPath -Force | Out-Null
            New-Item -ItemType Junction -Path (Join-Path $repo 'skills/default/junction-skill') -Target $junctionTargetPath -Force | Out-Null
        }
        catch {
            Write-Host "Skipping: junction creation is not supported on this host ($($_.Exception.Message))."
            return
        }
        if (-not (Test-Path -LiteralPath (Join-Path $repo '.gemini/junction-dir'))) {
            Write-Host "Skipping: junction creation is not supported on this host."
            return
        }

        Assert-Equals -Expected 'Junction' -Actual (Get-Item -Force -LiteralPath (Join-Path $repo '.gemini/junction-dir')).LinkType -Message "Fixture setup error: expected the source directory link to be a junction."

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        $installedJunctionPath = Join-Path $homeDir '.gemini/junction-dir'
        $installed = Get-Item -Force -LiteralPath $installedJunctionPath
        Assert-Equals -Expected 'Junction' -Actual $installed.LinkType -Message "Expected the installed directory link to keep its junction type."
        Assert-Equals -Expected $junctionTargetPath -Actual $installed.Target -Message "Expected the installed junction to keep its raw target path."
        Assert-True -Condition (([int]$installed.Attributes -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) -Message "Expected the installed junction to carry the ReparsePoint attribute."
        Assert-Equals -Expected $junctionSentinelBefore -Actual (Read-FileContent $junctionSentinelPath) -Message "Expected the external junction target to remain unchanged after install."
        $installedSkillPath = Join-Path $homeDir '.agents/skills/junction-skill'
        $installedSkill = Get-Item -Force -LiteralPath $installedSkillPath
        Assert-Equals -Expected 'Junction' -Actual $installedSkill.LinkType -Message 'Expected a root-linked skill to retain its junction type after installation.'
        Assert-Equals -Expected $junctionTargetPath -Actual $installedSkill.Target -Message 'Expected a root-linked skill junction to retain its raw target.'
        $python = Get-PythonForFixture
        & $python.Path @($python.Arguments) (Join-Path $repo 'scripts/rebase-skill-references.py') `
            --source-dir (Join-Path $repo 'skills/default/junction-skill') `
            --destination-dir $installedSkillPath `
            --references-source (Join-Path $repo 'references') `
            --references-destination (Join-Path $homeDir '.agents/references')
        if ($LASTEXITCODE -ne 0) {
            Fail 'Reference rebasing should skip a root-linked junction skill.'
        }
        Assert-Equals -Expected $junctionTargetBefore -Actual (Get-TreeFingerprint $junctionTargetPath) -Message 'Expected installation to leave a root-linked skill junction target byte-for-byte unchanged.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-CopiesFullGeminiTree {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        $installedGeminiInstructions = Read-FileContent (Join-Path $homeDir '.gemini/GEMINI.md')
        $installedCopilotInstructions = Read-FileContent (Join-Path $homeDir '.copilot/copilot-instructions.md')
        $installedCodexInstructions = Read-FileContent (Join-Path $homeDir '.codex/AGENTS.md')
        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.gemini/GEMINI.md')) -Actual $installedGeminiInstructions -Message "Expected GEMINI.md to be copied into ~/.gemini."
        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.copilot/copilot-instructions.md')) -Actual $installedCopilotInstructions -Message 'Expected Copilot instructions to be copied into ~/.copilot.'
        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.codex/AGENTS.md')) -Actual $installedCodexInstructions -Message 'Expected Codex instructions to be copied into ~/.codex.'
        Assert-Equals -Expected "---`nname: helper`ndescription: Fixture helper agent.`n---`nUse alpha." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/agents/helper.md')) -Message "Expected agents to be copied into ~/.gemini/agents."
        Assert-Equals -Expected "---`nname: nested-helper`ndescription: Nested fixture helper agent.`n---`nUse alpha deeply." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/agents/nested/helper.md')) -Message "Expected nested agents to be copied recursively into ~/.gemini/agents."
        Assert-Equals -Expected "---`nname: helper`ndescription: Fixture helper agent.`n---`nUse alpha." -Actual (Read-FileContent (Join-Path $homeDir '.copilot/agents/helper.md')) -Message "Expected agents to be copied into ~/.copilot/agents."
        Assert-Equals -Expected "---`nname: nested-helper`ndescription: Nested fixture helper agent.`n---`nUse alpha deeply." -Actual (Read-FileContent (Join-Path $homeDir '.copilot/agents/nested/helper.md')) -Message "Expected nested agents to be copied recursively into ~/.copilot/agents."
        Assert-Equals -Expected "Nested policy." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/policies/plan-custom-directory.toml')) -Message "Expected nested Gemini files to be copied recursively."
        Assert-Equals -Expected "Hidden note." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/.hidden-note')) -Message "Expected hidden Gemini files to be copied recursively."
        Assert-Equals -Expected "#!/bin/bash`necho hook" -Actual (Read-FileContent (Join-Path $homeDir '.copilot/hooks/test-hook.sh')) -Message "Expected hooks to be copied into ~/.copilot/hooks."
        Assert-Equals -Expected 'settings' -Actual ((Get-Content -LiteralPath (Join-Path $homeDir '.gemini/settings.json') -Raw | ConvertFrom-Json -AsHashtable)['global']) -Message "Expected global Gemini settings to determine the installed setting."

        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.gemini/.gemini'))) -Message "Expected the installer to copy Gemini contents into ~/.gemini, not nest another .gemini directory."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Set-PostRetirementFixture {
    param([string]$Repo)

    $manifest = Join-Path $Repo 'hooks/manifest.py'
    @(Get-Content -LiteralPath $manifest | Where-Object {
        -not ($_.Contains('GeneratedTarget(') -and
            ($_.Contains('"repository_state"') -or $_.Contains('"markdown_health"')) -and
            ($_.Contains('"copilot"') -or $_.Contains('"gemini"')))
    }) | Set-Content -LiteralPath $manifest
    foreach ($provider in @('copilot', 'gemini')) {
        foreach ($name in @('repository-state.py', 'markdown-health.py')) {
            Remove-Item -LiteralPath (Join-Path $Repo ".$provider/hooks/scripts/$name") -Force -ErrorAction SilentlyContinue
        }
    }
}

function Test-ProviderRefreshPreservesRetiredAndUserEntries {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        Set-PostRetirementFixture $repo
        Write-FixtureFile (Join-Path $repo '.gemini/global-settings.json') @('{"general":{"enableAutoUpdate":false},"hooks":{"BeforeTool":[{"hooks":[{"command":"python \"$HOME/.gemini/hooks/scripts/tool-guard.py\""}]}]}}')
        $copilotPath = Join-Path $homeDir '.copilot/hooks/hooks.json'
        $geminiPath = Join-Path $homeDir '.gemini/settings.json'
        Write-FixtureFile $copilotPath @('{"version":1,"userSetting":{"keep":true},"hooks":{"preToolUse":[{"type":"command","bash":"python3 \"$HOME/.copilot/hooks/scripts/repository-state.py\"","powershell":"python \"$HOME/.copilot/hooks/scripts/repository-state.py\"","timeoutSec":17},{"type":"command","bash":"$HOME/.copilot/hooks/scripts/tool-guard.py"},{"type":"command","bash":"echo custom"}],"agentStop":[{"type":"command","bash":"python3 \"$HOME/.copilot/hooks/scripts/markdown-health.py\"","env":{"MARKDOWN_HEALTH_EVENT":"final"}},{"type":"command","bash":"echo unrelated"}]}}')
        Write-FixtureFile $geminiPath @('{"general":{"enableAutoUpdate":true,"custom":42},"userSetting":{"keep":true},"hooks":{"BeforeTool":[{"matcher":"legacy","hooks":[{"name":"repository-state","type":"command","command":"python \"$HOME/.gemini/hooks/scripts/repository-state.py\"","timeout":17000},{"command":"echo custom"}]}],"AfterAgent":[{"hooks":[{"name":"markdown-health","command":"python \"$HOME/.gemini/hooks/scripts/markdown-health.py\"","env":{"MARKDOWN_HEALTH_EVENT":"final"}}]}]}}')

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir
        $copilot = Get-Content -LiteralPath $copilotPath -Raw | ConvertFrom-Json -AsHashtable
        $gemini = Get-Content -LiteralPath $geminiPath -Raw | ConvertFrom-Json -AsHashtable
        if (-not $IsWindows) {
            $ownerOnly = [System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite
            foreach ($path in @($copilotPath, $geminiPath)) {
                Assert-Equals -Expected $ownerOnly -Actual ([System.IO.File]::GetUnixFileMode($path)) -Message 'Expected merged provider JSON to be owner-only.'
            }
        }
        Assert-True -Condition $copilot['userSetting']['keep'] -Message 'Expected unrelated Copilot settings to survive refresh.'
        Assert-Equals -Expected 17 -Actual $copilot['hooks']['preToolUse'][0]['timeoutSec'] -Message 'Expected the exact old Copilot repository-state registration.'
        Assert-Equals -Expected 'echo custom' -Actual $copilot['hooks']['preToolUse'][1]['bash'] -Message 'Expected custom Copilot hook to survive.'
        Assert-Equals -Expected 1 -Actual @($copilot['hooks']['preToolUse'] | Where-Object { $_['bash'] -clike '*tool-guard.py' }).Count -Message 'Expected one maintained Copilot handler.'
        Assert-Equals -Expected 'final' -Actual $copilot['hooks']['agentStop'][0]['env']['MARKDOWN_HEALTH_EVENT'] -Message 'Expected old Copilot Markdown Health registration.'
        Assert-Equals -Expected 'echo unrelated' -Actual $copilot['hooks']['agentStop'][1]['bash'] -Message 'Expected unrelated Copilot stop handler.'
        Assert-Equals -Expected $false -Actual $gemini['general']['enableAutoUpdate'] -Message 'Expected maintained Gemini setting to update.'
        Assert-Equals -Expected 42 -Actual $gemini['general']['custom'] -Message 'Expected unrelated nested Gemini setting.'
        Assert-True -Condition $gemini['userSetting']['keep'] -Message 'Expected unrelated Gemini settings.'
        Assert-Equals -Expected 17000 -Actual $gemini['hooks']['BeforeTool'][0]['hooks'][0]['timeout'] -Message 'Expected exact old Gemini repository-state registration.'
        Assert-Equals -Expected 'echo custom' -Actual $gemini['hooks']['BeforeTool'][0]['hooks'][1]['command'] -Message 'Expected custom Gemini hook in the same group.'
        Assert-Equals -Expected 'final' -Actual $gemini['hooks']['AfterAgent'][0]['hooks'][0]['env']['MARKDOWN_HEALTH_EVENT'] -Message 'Expected old Gemini Markdown Health registration.'

        $beforeSecond = Get-TreeFingerprint $homeDir
        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected $beforeSecond -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected provider refresh to be idempotent.'
    }
    finally { Remove-Workdir $workdir }
}

function Test-ProviderMalformedJsonStopsBeforeMutation {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $copilotPath = Join-Path $homeDir '.copilot/hooks/hooks.json'
        $geminiPath = Join-Path $homeDir '.gemini/settings.json'
        Write-FixtureFile $copilotPath @('{"hooks":[],"hooks":{}}')
        Write-FixtureFile $geminiPath @('{"userSetting":true}')
        $before = Get-TreeFingerprint $homeDir
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected duplicate Copilot JSON key to fail preflight.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected failed Copilot preflight to leave home untouched.'
        Write-FixtureFile $copilotPath @('{"hooks":{}}')
        Write-FixtureFile $geminiPath @('{bad')
        $before = Get-TreeFingerprint $homeDir
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected malformed Gemini JSON to fail preflight.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected failed Gemini preflight to leave home untouched.'
        Write-FixtureFile $copilotPath @('{"hooks":{"preToolUse":[{"bash":"$HOME/.copilot/hooks/scripts/repository-state.py","powershell":"$HOME/.copilot/hooks/scripts/markdown-health.py"}]}}')
        Write-FixtureFile $geminiPath @('{"hooks":{}}')
        $before = Get-TreeFingerprint $homeDir
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected ambiguous retired commands to fail preflight.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected ambiguous retired commands to leave home untouched.'
    }
    finally { Remove-Workdir $workdir }
}

function Test-ProviderConfigHardLinksDoNotChangeOtherFiles {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir
        foreach ($relative in @('.copilot/hooks/hooks.json', '.gemini/settings.json')) {
            $installed = Join-Path $homeDir $relative
            $outside = Join-Path $workdir ((Split-Path -Leaf (Split-Path -Parent $relative)) + '-outside.json')
            Copy-Item -LiteralPath $installed -Destination $outside -Force
            Remove-Item -LiteralPath $installed -Force
            try {
                New-Item -ItemType HardLink -Path $installed -Target $outside -Force | Out-Null
            }
            catch {
                Write-Host "Skipping: provider hard-link creation is not supported on this host ($($_.Exception.Message))."
                return
            }
            if (-not $IsWindows) {
                $looseMode = [System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite -bor
                    [System.IO.UnixFileMode]::GroupRead -bor [System.IO.UnixFileMode]::OtherRead
                [System.IO.File]::SetUnixFileMode($outside, $looseMode)
            }
            $outsideBefore = Read-FileContent $outside
            Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir
            Assert-Equals -Expected $outsideBefore -Actual (Read-FileContent $outside) -Message 'Expected refresh not to alter the other hard-linked file.'
            Assert-Equals -Expected '' -Actual (Get-Item -Force -LiteralPath $installed).LinkType -Message 'Expected installed config to become an independent regular file.'
            if (-not $IsWindows) {
                $ownerOnly = [System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite
                Assert-Equals -Expected $looseMode -Actual ([System.IO.File]::GetUnixFileMode($outside)) -Message 'Expected external hard-link mode to remain unchanged.'
                Assert-Equals -Expected $ownerOnly -Actual ([System.IO.File]::GetUnixFileMode($installed)) -Message 'Expected installed config mode 600.'
                $python = Get-PythonForFixture
                & $python.Path @($python.Arguments) -c 'import os, sys; assert os.stat(sys.argv[1]).st_ino != os.stat(sys.argv[2]).st_ino' $outside $installed
                Assert-Equals -Expected 0 -Actual $LASTEXITCODE -Message 'Expected the installed config to break the hard link.'
            }
        }
    }
    finally { Remove-Workdir $workdir }
}

function Test-ProviderConfigLinkedParentStopsBeforeMutation {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        New-FixtureRepo $repo
        foreach ($provider in @('copilot', 'gemini')) {
            $homeDir = Join-Path $workdir "home-$provider"
            $outside = Join-Path $workdir "outside-$provider"
            Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
            Write-FixtureFile (Join-Path $outside 'sentinel') @('sentinel')
            if ($provider -ceq 'copilot') {
                $parent = Join-Path $homeDir '.copilot/hooks'
            } else {
                $parent = Join-Path $homeDir '.gemini'
            }
            New-Item -ItemType Directory -Path (Split-Path -Parent $parent) -Force | Out-Null
            try {
                $linkType = if ($IsWindows) { 'Junction' } else { 'SymbolicLink' }
                New-Item -ItemType $linkType -Path $parent -Target $outside -Force | Out-Null
            }
            catch {
                Write-Host "Skipping: provider parent link creation is not supported on this host ($($_.Exception.Message))."
                return
            }
            $homeBefore = Get-TreeFingerprint $homeDir
            $outsideBefore = Get-TreeFingerprint $outside
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
            Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected linked config parent to fail preflight.'
            Assert-Equals -Expected $homeBefore -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected linked-parent preflight to leave home unchanged.'
            Assert-Equals -Expected $outsideBefore -Actual (Get-TreeFingerprint $outside) -Message 'Expected linked-parent preflight to leave link target unchanged.'
        }
    }
    finally { Remove-Workdir $workdir }
}

function Test-InstalledHooksAreExecutable {
    if ($IsWindows) {
        Write-Host "Skipping: executable-bit assertions do not apply on Windows."
        return
    }

    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        $hookRelPaths = @(
            '.gemini/hooks/scripts/test-hook.py',
            '.copilot/hooks/scripts/test-hook.py',
            '.gemini/hooks/scripts/test-hook.sh',
            '.copilot/hooks/scripts/test-hook.sh'
        )

        # Uppercase .PY hook: forced non-executable too, then asserted to KEEP that mode.
        $upperPyRel = '.copilot/hooks/scripts/test-upper.PY'
        $literalNonHooks = @(".copilot/hooks/scripts/not-hook.p$([char]0x00ad)y", ".gemini/hooks/scripts/not-hook.s$([char]0x00ad)h")
        foreach ($rel in $literalNonHooks) {
            Write-FixtureFile (Join-Path $repo $rel) @('Keep original mode.')
        }

        # Force the fixture inputs non-executable (mirrors `chmod 644` in the Bash test).
        $nonExecutable = [System.IO.UnixFileMode]::UserRead -bor
            [System.IO.UnixFileMode]::UserWrite -bor
            [System.IO.UnixFileMode]::OtherRead
        # Set-HookScriptsExecutable chmods hook scripts to exactly 755 (rwxr-xr-x).
        $expectedHookMode = [System.IO.UnixFileMode]::UserRead -bor
            [System.IO.UnixFileMode]::UserWrite -bor
            [System.IO.UnixFileMode]::UserExecute -bor
            [System.IO.UnixFileMode]::GroupRead -bor
            [System.IO.UnixFileMode]::GroupExecute -bor
            [System.IO.UnixFileMode]::OtherRead -bor
            [System.IO.UnixFileMode]::OtherExecute
        foreach ($rel in $hookRelPaths + @($upperPyRel) + $literalNonHooks) {
            [System.IO.File]::SetUnixFileMode((Join-Path $repo $rel), $nonExecutable)
        }

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        foreach ($rel in $hookRelPaths) {
            $installed = Join-Path $homeDir $rel
            $mode = [System.IO.File]::GetUnixFileMode($installed)
            Assert-Equals -Expected $expectedHookMode -Actual $mode -Message "Expected $installed to be installed with mode 755 (mode: $mode)."
        }

        # The extension match is case-sensitive (like `find -name`): the uppercase
        # .PY hook must keep its input mode and must NOT gain the execute bit.
        $upperPyInstalled = Join-Path $homeDir $upperPyRel
        $upperPyMode = [System.IO.File]::GetUnixFileMode($upperPyInstalled)
        Assert-Equals -Expected $nonExecutable -Actual $upperPyMode -Message "Expected $upperPyInstalled to keep its input mode (extension match is case-sensitive; mode: $upperPyMode)."
        foreach ($rel in $literalNonHooks) {
            Assert-Equals $nonExecutable ([System.IO.File]::GetUnixFileMode((Join-Path $homeDir $rel))) "Expected literal non-hook extension to retain original mode: $rel."
        }
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-InstallsCodexHookAndGlobalConfiguration {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        $codexInstructionsPath = Join-Path $homeDir '.codex/AGENTS.md'
        Write-FixtureFile $codexInstructionsPath @('Stale Codex instructions.')
        $unrelatedHook = Join-Path $homeDir '.codex/hooks/unrelated.py'
        Write-FixtureFile $unrelatedHook @('print("preserve mode")')
        if (-not $IsWindows) {
            $ownerOnly = [System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite
            [System.IO.File]::SetUnixFileMode($unrelatedHook, $ownerOnly)
        }
        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.codex/AGENTS.md')) -Actual (Read-FileContent $codexInstructionsPath) -Message 'Expected the global Codex instructions to be replaced from the maintained source.'

        $installedHook = Join-Path $homeDir '.codex/hooks/load-required-skills.py'
        Assert-True -Condition (Test-Path -LiteralPath $installedHook -PathType Leaf) -Message "Expected the Codex required-skills hook to be installed."
        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.codex/hooks/load-required-skills.py')) -Actual (Read-FileContent $installedHook) -Message "Expected the installed Codex hook to match the maintained source."
        foreach ($relative in @('scan-secrets.py', 'tool-guard.py', 'helpers/common.py', 'helpers/audit.py', 'helpers/tool_guard_policy.py')) {
            $installed = Join-Path (Join-Path $homeDir '.codex/hooks') $relative
            Assert-True -Condition (Test-Path -LiteralPath $installed -PathType Leaf) -Message "Expected Codex hook file $relative to be installed."
            Assert-Equals -Expected (Read-FileContent (Join-Path $repo ".codex/hooks/$relative")) -Actual (Read-FileContent $installed) -Message "Expected Codex hook file $relative to match source."
        }

        $configPath = Join-Path $homeDir '.codex/hooks.json'
        Assert-True -Condition (Test-Path -LiteralPath $configPath -PathType Leaf) -Message "Expected Codex global hooks.json to be installed."
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -AsHashtable
        $handler = $config['hooks']['SessionStart'][0]['hooks'][0]
        Assert-Equals -Expected 'python3 ~/.codex/hooks/load-required-skills.py' -Actual $handler['command'] -Message "Expected the Codex handler's POSIX command to target the installed hook."
        Assert-Equals -Expected 'py -3 "%USERPROFILE%\.codex\hooks\load-required-skills.py"' -Actual $handler['commandWindows'] -Message "Expected the exact Windows Codex command."
        $preCommands = @($config['hooks']['PreToolUse'][0]['hooks'] | ForEach-Object { $_['command'] })
        Assert-True -Condition ($preCommands -contains 'python3 ~/.codex/hooks/scan-secrets.py') -Message 'Expected PreToolUse to retain the maintained scanner.'
        Assert-True -Condition ($preCommands -contains 'python3 ~/.codex/hooks/tool-guard.py') -Message 'Expected Codex Tool Guardian registration.'
        $stopCommands = @($config['hooks']['Stop'][0]['hooks'] | ForEach-Object { $_['command'] })
        Assert-True -Condition ($stopCommands -contains 'python3 ~/.codex/hooks/scan-secrets.py') -Message 'Expected Stop to retain the maintained scanner.'
        Assert-True -Condition (@($config['hooks']['PreToolUse'] | ForEach-Object { $_['hooks'] } | Where-Object { $_['command'] -ceq 'python3 ~/.codex/hooks/scan-secrets.py' }).Count -eq 1) -Message 'Expected exactly one PreToolUse scanner registration.'
        Assert-True -Condition (@($config['hooks']['Stop'] | ForEach-Object { $_['hooks'] } | Where-Object { $_['command'] -ceq 'python3 ~/.codex/hooks/scan-secrets.py' }).Count -eq 1) -Message 'Expected exactly one Stop scanner registration.'
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.codex/hooks.json.bak'))) -Message "Expected a fresh Codex install not to create a backup."

        if (-not $IsWindows) {
            $expectedMode = [System.IO.UnixFileMode]::UserRead -bor
                [System.IO.UnixFileMode]::UserWrite -bor
                [System.IO.UnixFileMode]::UserExecute -bor
                [System.IO.UnixFileMode]::GroupRead -bor
                [System.IO.UnixFileMode]::GroupExecute -bor
                [System.IO.UnixFileMode]::OtherRead -bor
                [System.IO.UnixFileMode]::OtherExecute
            Assert-Equals -Expected $expectedMode -Actual ([System.IO.File]::GetUnixFileMode($installedHook)) -Message "Expected the installed Codex hook to be executable with mode 755."
            Assert-Equals -Expected $ownerOnly -Actual ([System.IO.File]::GetUnixFileMode($unrelatedHook)) -Message "Expected installation not to change unrelated Codex hook modes."
        }
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Assert-CodexAgentInstallation {
    param(
        [string]$AgentPath,
        [string]$ManifestPath
    )

    $python = @(Get-Command python3 -CommandType Application -ErrorAction SilentlyContinue)[0]
    $pythonArguments = @()
    if ($null -eq $python) {
        $python = @(Get-Command py -CommandType Application -ErrorAction SilentlyContinue)[0]
        $pythonArguments = @('-3')
    }
    if ($null -eq $python) {
        Fail 'Missing Python executable: expected python3 or py for Codex agent assertions.'
    }

    $assertion = @'
import json
import os
import stat
import sys
import tomllib
from pathlib import Path

agent_path = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
actual_agent = tomllib.loads(agent_path.read_text(encoding="utf-8"))
expected_agent = {
    "name": "helper",
    "description": "Fixture helper agent.",
    "developer_instructions": "Use alpha.\r\n" if os.name == "nt" else "Use alpha.\n",
}
assert actual_agent == expected_agent, f"Expected {expected_agent!r}; got {actual_agent!r}"
assert json.loads(manifest_path.read_text(encoding="utf-8")) == {
    "version": 1,
    "agents": [{"source": "helper.md", "output": "helper.toml", "name": "helper"}],
}
if os.name != "nt":
    assert stat.S_IMODE(agent_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(manifest_path.stat().st_mode) == 0o600
'@
    & $python.Source @pythonArguments -c $assertion $AgentPath $ManifestPath
    if ($LASTEXITCODE -ne 0) {
        Fail 'Expected generated Codex TOML and manifest to parse with the fixture agent identity and exact instructions.'
    }
}

function Test-InstallsCodexAgentsBeforeOtherAssets {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $agentPath = Join-Path $homeDir '.codex/agents/helper.toml'
        $manifestPath = Join-Path $homeDir '.codex/agents/.skills-repo-agents.json'

        New-FixtureRepo $repo
        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-CodexAgentInstallation -AgentPath $agentPath -ManifestPath $manifestPath
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.codex/agents/nested/helper.toml'))) -Message 'Expected Codex conversion to ignore nested Markdown agents.'
        $firstAgent = Get-Content -LiteralPath $agentPath -Raw
        $firstManifest = Get-Content -LiteralPath $manifestPath -Raw

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected $firstAgent -Actual (Get-Content -LiteralPath $agentPath -Raw) -Message 'Expected a second Codex install to leave helper.toml unchanged.'
        Assert-Equals -Expected $firstManifest -Actual (Get-Content -LiteralPath $manifestPath -Raw) -Message 'Expected a second Codex install to leave the agent manifest unchanged.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-CodexAgentsFailBeforeCopyingOtherAssets {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        Write-FixtureFile (Join-Path $repo 'agents/helper.md') @('---', 'name: helper', '---', 'Invalid fixture.')

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected invalid Codex agent source to fail install.ps1.'
        Assert-True -Condition (($result.Stderr -join "`n") -match 'helper.md') -Message 'Expected the invalid Codex source diagnostic on stderr.'
        foreach ($path in @(
            (Join-Path $homeDir '.agents/skills'),
            (Join-Path $homeDir '.gemini/agents'),
            (Join-Path $homeDir '.copilot/agents'),
            (Join-Path $homeDir '.codex/hooks')
        )) {
            Assert-True -Condition (-not (Test-Path -LiteralPath $path)) -Message "Expected invalid Codex source to stop before copying $path."
        }
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-CodexHomeOverrideSelectsOneAgentDestination {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $codexHome = Join-Path $workdir 'custom-codex'
        $agentPath = Join-Path $codexHome 'agents/helper.toml'
        $manifestPath = Join-Path $codexHome 'agents/.skills-repo-agents.json'

        New-FixtureRepo $repo
        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codexHome
        Assert-CodexAgentInstallation -AgentPath $agentPath -ManifestPath $manifestPath
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.codex/agents/helper.toml'))) -Message 'Expected CODEX_HOME not to create a duplicate agent under the default home destination.'
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-PreservesCodexConfigurationAndIsIdempotent {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo
        $configPath = Join-Path $homeDir '.codex/hooks.json'
        Write-FixtureFile $configPath @(
            '{',
            '  "setting": {"keep": true},',
            '  "hooks": {',
            '    "BeforeTool": [{"hooks": [{"type": "command", "command": "echo preserve"}]}],',
            '    "SessionStart": [{"matcher": "startup", "hooks": [',
            '      {"type": "command", "command": "echo preserve"},',
            '      {"type": "command", "command": "python3 ~/.codex/hooks/load-required-skills.py"}',
            '    ]}]',
            '  }',
            '}'
        )
        $originalConfig = Get-Content -LiteralPath $configPath -Raw

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -AsHashtable
        Assert-True -Condition ($config['setting']['keep']) -Message "Expected unrelated top-level Codex configuration to be preserved."
        Assert-Equals -Expected 'echo preserve' -Actual $config['hooks']['BeforeTool'][0]['hooks'][0]['command'] -Message "Expected unrelated Codex hook events to be preserved."
        Assert-Equals -Expected 'echo preserve' -Actual $config['hooks']['SessionStart'][0]['hooks'][0]['command'] -Message "Expected unrelated SessionStart handlers to be preserved."
        Assert-Equals -Expected 'python3 ~/.codex/hooks/load-required-skills.py' -Actual $config['hooks']['SessionStart'][-1]['hooks'][0]['command'] -Message "Expected the owned SessionStart handler to be replaced by the maintained handler."

        $backupPath = Join-Path $homeDir '.codex/hooks.json.bak'
        Assert-True -Condition (Test-Path -LiteralPath $backupPath -PathType Leaf) -Message "Expected a backup when a valid Codex configuration changes."
        Assert-Equals -Expected $originalConfig -Actual (Get-Content -LiteralPath $backupPath -Raw) -Message "Expected the backup to contain the immediately previous Codex configuration."
        $installedConfig = Get-Content -LiteralPath $configPath -Raw
        $backupBeforeSecondInstall = Get-Content -LiteralPath $backupPath -Raw

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        Assert-Equals -Expected $installedConfig -Actual (Get-Content -LiteralPath $configPath -Raw) -Message "Expected a second Codex install to leave the merged configuration unchanged."
        Assert-Equals -Expected $backupBeforeSecondInstall -Actual (Get-Content -LiteralPath $backupPath -Raw) -Message "Expected an idempotent Codex install not to churn the backup."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-RefusesSymlinkedCodexHookDestination {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $outsideHook = Join-Path $workdir 'outside-hook.py'
        $installedHook = Join-Path $homeDir '.codex/hooks/load-required-skills.py'

        New-FixtureRepo $repo
        Write-FixtureFile $outsideHook @('external hook')
        try {
            New-Item -ItemType Directory -Path (Split-Path -Parent $installedHook) -Force | Out-Null
            New-Item -ItemType SymbolicLink -Path $installedHook -Target $outsideHook -Force | Out-Null
        }
        catch {
            Write-Host "Skipping: Codex destination symlink creation is not supported on this host ($($_.Exception.Message))."
            return
        }

        $beforeMode = $null
        if (-not $IsWindows) {
            $ownerOnly = [System.IO.UnixFileMode]::UserRead -bor [System.IO.UnixFileMode]::UserWrite
            [System.IO.File]::SetUnixFileMode($outsideHook, $ownerOnly)
            $beforeMode = [System.IO.File]::GetUnixFileMode($outsideHook)
        }

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message "Expected installation to refuse a symlinked Codex hook destination."
        Assert-Equals -Expected 'external hook' -Actual (Read-FileContent $outsideHook) -Message "Expected the external hook target to remain unchanged."
        Assert-Equals -Expected 'SymbolicLink' -Actual (Get-Item -Force -LiteralPath $installedHook).LinkType -Message "Expected the destination symlink to remain intact after refusal."
        if (-not $IsWindows) {
            Assert-Equals -Expected $beforeMode -Actual ([System.IO.File]::GetUnixFileMode($outsideHook)) -Message "Expected the external hook target mode to remain unchanged."
        }
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-CopiesCopilotConfigAndReferences {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        Invoke-Install -Repo $repo -HomeDir $homeDir -Workdir $workdir

        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.copilot/copilot-instructions.md')) -Actual (Read-FileContent (Join-Path $homeDir '.copilot/copilot-instructions.md')) -Message "Expected .copilot/copilot-instructions.md to be installed into ~/.copilot."
        Assert-Equals -Expected "{}" -Actual (Read-FileContent (Join-Path $homeDir '.copilot/lsp-config.json')) -Message "Expected .copilot/lsp-config.json to be installed into ~/.copilot."
        Assert-Equals -Expected "Reference notes." -Actual (Read-FileContent (Join-Path $homeDir '.agents/references/notes.md')) -Message "Expected references content to be copied into ~/.agents/references."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-MissingSourceFails {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'

        New-FixtureRepo $repo

        # agents/ is a required source directory; removing it must fail the install before copying.
        Remove-Item -LiteralPath (Join-Path $repo 'agents') -Recurse -Force

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message "Expected install.ps1 to exit 1 when a required source directory is missing."
        Assert-True -Condition (($result.Stderr -join "`n") -match 'Missing source directory') -Message "Expected the missing-source diagnostic on the child's stderr stream (stderr: $($result.Stderr -join ' | '); stdout: $($result.Stdout -join ' | '))."
    }
    finally {
        Remove-Workdir $workdir
    }
}

function Test-HelpWithoutSourcesOrDependencies {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $codex = Join-Path $workdir 'codex'
        Write-FixtureFile (Join-Path $repo 'scripts/install.ps1') @(Get-Content -LiteralPath $InstallScriptSrc)
        Write-FixtureFile (Join-Path $homeDir 'sentinel') @('sentinel')
        Write-FixtureFile (Join-Path $codex 'sentinel') @('sentinel')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $before = Get-TreeFingerprint $homeDir
        $beforeCodex = Get-TreeFingerprint $codex
        foreach ($arguments in @(@('-h'), @('--help'), @('--fs', '--help', '--forest-service'), @('--help', '--no-forest-service', '--no-forest-service'))) {
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex -ForestServiceValue 'banana' -InstallArguments $arguments
            Assert-Equals 0 $result.ExitCode 'Expected help to bypass missing sources/dependencies and invalid environment.'
            Assert-True (($result.Stdout -join "`n").Contains('Usage:')) 'Expected usage on stdout.'
            Assert-True (($result.Stdout -join "`n").Contains('--forest-service')) 'Expected options in help.'
            Assert-True (($result.Stdout -join "`n").Contains('Examples:')) 'Expected examples in help.'
            Assert-Equals '' ($result.Stderr -join "`n") 'Expected help stderr to be empty.'
            Assert-Equals $before (Get-TreeFingerprint $homeDir) 'Expected help not to mutate home.'
            Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected help not to mutate CODEX_HOME.'
        }
    }
    finally { Remove-Workdir $workdir }
}

function Test-ExplicitForestServiceSelection {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        New-FixtureRepo $repo
        Write-FixtureFile (Join-Path $repo 'skills/forest-service/agency-priorities/SKILL.md') @('---', 'name: unrelated-frontmatter-identity', '---', 'Agency priorities.')
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue 'banana' -InstallArguments @('--fs')
        Assert-Equals 0 $result.ExitCode 'Expected explicit selection to override invalid environment.'
        Assert-Equals '' ($result.Stdout -join "`n") 'Expected successful installation status only on stderr.'
        Assert-True (($result.Stderr -join "`n").Contains('Installed skills to')) 'Expected installation progress on stderr.'
        Assert-True (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/agency-priorities/SKILL.md')) 'Expected flat Forest Service skill installation.'
        Assert-True (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')) 'Expected default skills with Forest Service selection.'
    }
    finally { Remove-Workdir $workdir }
}

function Test-SelectionEnvironmentAndRepeats {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        New-FixtureRepo $repo
        Write-FixtureFile (Join-Path $repo 'skills/forest-service/agency-priorities/SKILL.md') @('Forest Service.')
        $cases = @(
            @{ Both = $true; Value = 'TrUe'; Arguments = @() },
            @{ Both = $true; Value = '1'; Arguments = @() },
            @{ Both = $false; Value = $null; Arguments = @() },
            @{ Both = $false; Value = ''; Arguments = @() },
            @{ Both = $false; Value = '0'; Arguments = @() },
            @{ Both = $false; Value = 'FaLsE'; Arguments = @() },
            @{ Both = $true; Value = '0'; Arguments = @('--forest-service') },
            @{ Both = $true; Value = 'false'; Arguments = @('--fs') },
            @{ Both = $true; Value = 'banana'; Arguments = @('--forest-service') },
            @{ Both = $true; Value = 'banana'; Arguments = @('--fs', '--forest-service', '--fs') },
            @{ Both = $false; Value = 'true'; Arguments = @('--no-forest-service') },
            @{ Both = $false; Value = 'banana'; Arguments = @('--no-forest-service') },
            @{ Both = $false; Value = 'banana'; Arguments = @('--no-forest-service', '--no-forest-service') }
        )
        $index = 0
        foreach ($case in $cases) {
            $homeDir = Join-Path $workdir "home-$index"
            $index++
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue $case.Value -InstallArguments $case.Arguments
            Assert-Equals 0 $result.ExitCode "Expected successful selection: $($case.Value) $($case.Arguments)."
            Assert-True (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')) 'Expected default skill.'
            Assert-Equals $case.Both (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/agency-priorities/SKILL.md')) "Expected selected Forest Service outcome: $($case.Value) $($case.Arguments)."
        }
        $homeDir = Join-Path $workdir 'repeat-home'
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue 'banana' -InstallArguments @('--fs')
        Assert-Equals 0 $result.ExitCode 'Expected opted-in install.'
        $first = Read-FileContent (Join-Path $homeDir '.agents/skills/agency-priorities/SKILL.md')
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue '0'
        Assert-Equals 0 $result.ExitCode 'Expected default repeat.'
        Assert-Equals $first (Read-FileContent (Join-Path $homeDir '.agents/skills/agency-priorities/SKILL.md')) 'Expected default repeat to preserve installed Forest Service skills.'
    }
    finally { Remove-Workdir $workdir }
}

function Test-InvalidSelectionIsImmutable {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $codex = Join-Path $workdir 'codex'
        Write-FixtureFile (Join-Path $repo 'scripts/install.ps1') @(Get-Content -LiteralPath $InstallScriptSrc)
        Write-FixtureFile (Join-Path $homeDir 'sentinel') @('sentinel')
        Write-FixtureFile (Join-Path $codex 'sentinel') @('sentinel')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $before = Get-TreeFingerprint $homeDir
        $beforeCodex = Get-TreeFingerprint $codex
        foreach ($arguments in @(
            @('--fs', '--no-forest-service'), @('--no-forest-service', '--forest-service'),
            @('--help', '--fs', '--no-forest-service'), @('-h', '--no-forest-service', '--fs'),
            @('--wat'), @('operand'), @('--fs=true'), @('--forest-service=1'), @('--no-forest-service=false'),
            @('--help', '--wat'), @('--wat', '--help'), @('--help', 'operand'), @('--help', '--fs=true'),
            @('-fs'), @('-ForestService'), @('-help'), @('-?'), @('--FS'), @('--'),
            @("--f$([char]0x00ad)s"), @("--hel$([char]0x200b)p")
        )) {
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex -InstallArguments $arguments
            Assert-Equals 2 $result.ExitCode "Expected invalid arguments to exit 2: $arguments."
            Assert-True (($result.Stderr -join "`n") -match 'Conflicting|Unknown argument') 'Expected actionable argument stderr.'
            Assert-Equals '' ($result.Stdout -join "`n") 'Expected no stdout for invalid arguments.'
            Assert-Equals $before (Get-TreeFingerprint $homeDir) 'Expected invalid arguments not to mutate home.'
            Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected invalid arguments not to mutate CODEX_HOME.'
        }
        foreach ($value in @('banana', ' true', 'false ', 'yes', 'on', '2', "tr$([char]0x00ad)ue", "tru$([char]0x200b)e", "1$([char]0x00ad)")) {
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex -ForestServiceValue $value
            Assert-Equals 2 $result.ExitCode "Expected invalid environment to exit 2: $value."
            Assert-True (($result.Stderr -join "`n").Contains('INSTALL_FOREST_SERVICE_SKILLS')) 'Expected actionable variable stderr.'
            Assert-Equals '' ($result.Stdout -join "`n") 'Expected no stdout for invalid environment.'
            Assert-Equals $before (Get-TreeFingerprint $homeDir) 'Expected invalid environment not to mutate home.'
            Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected invalid environment not to mutate CODEX_HOME.'
        }
    }
    finally { Remove-Workdir $workdir }
}

function Test-SourcePreflightIsImmutable {
    param(
        [string[]]$Scenarios = @('missing-default', 'missing-forest-disabled', 'missing-forest-enabled', 'malformed-default', 'malformed-forest', 'equal-name', 'case-name', 'nfc-nfd-disabled', 'nfc-nfd-enabled')
    )

    $workdir = New-TestWorkdir
    try {
        $nfcName = "caf$([char]0x00e9)"
        $nfdName = "cafe$([char]0x0301)"
        foreach ($scenario in $Scenarios) {
            $repo = Join-Path $workdir "$scenario/repo"
            $homeDir = Join-Path $workdir "$scenario/home"
            $codex = Join-Path $workdir "$scenario/codex"
            New-FixtureRepo $repo
            Write-FixtureFile (Join-Path $homeDir 'sentinel') @('sentinel')
            Write-FixtureFile (Join-Path $codex 'sentinel') @('sentinel')
            $marker = Join-Path $workdir 'stage-reached'
            $literalMarker = $marker | ConvertTo-Json -Compress
            Write-FixtureFile (Join-Path $repo 'scripts/configure-rtk.py') @('from pathlib import Path', "Path($literalMarker).write_text('reached')", 'raise SystemExit(98)')
            Copy-Item -LiteralPath (Join-Path $repo 'scripts/configure-rtk.py') -Destination (Join-Path $repo 'scripts/install-codex-agents.py')
            $arguments = @()
            $defaultDiagnostic = 'skills/default/alpha'
            switch ($scenario) {
                'missing-default' { Remove-Item -LiteralPath (Join-Path $repo 'skills/default') -Recurse -Force; $diagnostic = 'skills/default' }
                'missing-forest-disabled' { Remove-Item -LiteralPath (Join-Path $repo 'skills/forest-service') -Recurse -Force; $diagnostic = 'skills/forest-service' }
                'missing-forest-enabled' { Remove-Item -LiteralPath (Join-Path $repo 'skills/forest-service') -Recurse -Force; $diagnostic = 'skills/forest-service'; $arguments = @('--fs') }
                'malformed-default' { $diagnostic = 'skills/default/incomplete'; New-Item -ItemType Directory -Path (Join-Path $repo $diagnostic) | Out-Null }
                'malformed-forest' { $diagnostic = 'skills/forest-service/incomplete'; New-Item -ItemType Directory -Path (Join-Path $repo $diagnostic) | Out-Null }
                'equal-name' { $diagnostic = 'skills/forest-service/alpha'; Write-FixtureFile (Join-Path $repo "$diagnostic/SKILL.md") @('A different frontmatter name.') }
                'case-name' { $diagnostic = 'skills/forest-service/ALPHA'; Write-FixtureFile (Join-Path $repo "$diagnostic/SKILL.md") @('A different frontmatter name.') }
                { $_ -in @('nfc-nfd-disabled', 'nfc-nfd-enabled') } {
                    # Separate category parents support both names on filesystems
                    # that collapse canonically equivalent destination spellings.
                    $defaultDiagnostic = "skills/default/$nfcName"
                    $diagnostic = "skills/forest-service/$nfdName"
                    Write-FixtureFile (Join-Path $repo "$defaultDiagnostic/SKILL.md") @('---', 'name: default-unicode', '---', 'Default Unicode skill.')
                    Write-FixtureFile (Join-Path $repo "$diagnostic/SKILL.md") @('---', 'name: forest-unicode', '---', 'Forest Unicode skill.')
                    if ($scenario -eq 'nfc-nfd-enabled') { $arguments = @('--fs') }
                }
            }
            Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
            $before = Get-TreeFingerprint $homeDir
            $beforeCodex = Get-TreeFingerprint $codex
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex -ForestServiceValue '0' -InstallArguments $arguments
            Assert-Equals 1 $result.ExitCode "Expected source error exit 1: $scenario."
            $stderr = ($result.Stderr -join "`n").Replace('\', '/')
            Assert-True ($stderr.Contains($diagnostic)) "Expected bad source path: $scenario. Actual stderr: $stderr"
            if ($scenario -in @('equal-name', 'case-name', 'nfc-nfd-disabled', 'nfc-nfd-enabled')) {
                Assert-True ($stderr.Contains($defaultDiagnostic)) "Expected both original collision paths: $scenario. Actual stderr: $stderr"
            }
            Assert-Equals '' ($result.Stdout -join "`n") 'Expected no stdout for source errors.'
            Assert-Equals $before (Get-TreeFingerprint $homeDir) 'Expected source error not to mutate home.'
            Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected source error not to mutate CODEX_HOME.'
            Assert-True (-not (Test-Path -LiteralPath $marker)) 'Expected validation before dependency, RTK, or converter stages.'
        }
    }
    finally { Remove-Workdir $workdir }
}

function Test-SourceDiagnosticsWithLegacyEncoding {
    $oldEncoding = [System.Environment]::GetEnvironmentVariable('PYTHONIOENCODING', [System.EnvironmentVariableTarget]::Process)
    try {
        # Windows redirected Python streams can use a legacy encoding. Exercise
        # the real installer with that same producer constraint on every host.
        [System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'cp1252', [System.EnvironmentVariableTarget]::Process)
        Test-SourcePreflightIsImmutable -Scenarios @('nfc-nfd-disabled', 'nfc-nfd-enabled')
    }
    finally {
        [System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING', $oldEncoding, [System.EnvironmentVariableTarget]::Process)
    }
}

function Test-HelperFailuresAreInstallerErrors {
    $workdir = New-TestWorkdir
    try {
        foreach ($helper in @('validate-skill-sources.py', 'configure-rtk.py', 'generate-hooks.py', 'install-provider-hooks.py', 'install-codex-agents.py', 'rebase-skill-references.py')) {
            $repo = Join-Path $workdir "$helper/repo"
            $homeDir = Join-Path $workdir "$helper/home"
            $codex = Join-Path $workdir "$helper/codex"
            New-FixtureRepo $repo
            Write-FixtureFile (Join-Path $homeDir 'sentinel') @('sentinel')
            Write-FixtureFile (Join-Path $codex 'sentinel') @('sentinel')
            Write-FixtureFile (Join-Path $repo "scripts/$helper") @('import sys', 'print("Fixture helper status")', 'print("Fixture helper failed; repair its input.", file=sys.stderr)', 'raise SystemExit(2)')
            Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
            $before = Get-TreeFingerprint $homeDir
            $beforeCodex = Get-TreeFingerprint $codex
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -CodexHome $codex -ForestServiceValue '0'
            Assert-Equals 1 $result.ExitCode "Expected helper exit 2 to become installer exit 1: $helper."
            Assert-True (($result.Stderr -join "`n").Contains('Fixture helper failed; repair its input.')) 'Expected helper diagnostic and recovery preserved.'
            Assert-Equals '' ($result.Stdout -join "`n") 'Expected helper status not to leak stdout.'
            if ($helper -notin @('install-codex-agents.py', 'rebase-skill-references.py')) {
                Assert-Equals $before (Get-TreeFingerprint $homeDir) 'Expected preflight helper failure not to mutate home.'
                Assert-Equals $beforeCodex (Get-TreeFingerprint $codex) 'Expected preflight helper failure not to mutate CODEX_HOME.'
            }
        }
    }
    finally { Remove-Workdir $workdir }
}

function Test-EmptyCategoriesMarkersAndExclusions {
    $workdir = New-TestWorkdir
    try {
        $repo = Join-Path $workdir 'repo'
        New-FixtureRepo $repo
        foreach ($category in @('default', 'forest-service')) {
            foreach ($name in @('archive', 'agency-workspace', 'weird[1]-workspace')) {
                New-Item -ItemType Directory -Path (Join-Path $repo "skills/$category/$name") -Force | Out-Null
            }
            Write-FixtureFile (Join-Path $repo "skills/$category/notes.txt") @('Non-directory marker.')
        }
        foreach ($selection in @('--fs', '--no-forest-service')) {
            $homeDir = Join-Path $workdir "home-$selection"
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue 'banana' -InstallArguments @($selection)
            Assert-Equals 0 $result.ExitCode 'Expected empty Forest Service category valid when enabled or disabled.'
            Assert-True (Test-Path -LiteralPath (Join-Path $homeDir '.agents/skills/alpha/SKILL.md')) 'Expected flat default alpha.'
            foreach ($name in @('default', 'forest-service', '.gitkeep', 'notes.txt', 'archive', 'agency-workspace', 'weird[1]-workspace')) {
                Assert-True (-not (Test-Path -LiteralPath (Join-Path $homeDir ".agents/skills/$name"))) "Expected marker/category/exclusion omitted: $name."
            }
        }
        Remove-Item -LiteralPath (Join-Path $repo 'skills/default/archive') -Recurse -Force
        Write-FixtureFile (Join-Path $repo 'skills/default/Archive/SKILL.md') @('Not excluded.')
        Write-FixtureFile (Join-Path $repo 'skills/default/My-Workspace/SKILL.md') @('Not excluded.')
        Write-FixtureFile (Join-Path $repo 'skills/forest-service/second-name/SKILL.md') @(Get-Content -LiteralPath (Join-Path $repo 'skills/default/alpha/SKILL.md'))
        $unicodeArchive = "archiv$([char]0x00ad)e"
        $unicodeWorkspace = "x-work$([char]0x00ad)space"
        Write-FixtureFile (Join-Path $repo "skills/default/$unicodeArchive/SKILL.md") @('Not excluded.')
        Write-FixtureFile (Join-Path $repo "skills/default/$unicodeWorkspace/SKILL.md") @('Not excluded.')
        $homeDir = Join-Path $workdir 'case-home'
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -InstallArguments @('--fs')
        Assert-Equals 0 $result.ExitCode 'Expected case-sensitive exclusions and basename identities.'
        foreach ($name in @('Archive', 'My-Workspace', 'second-name', $unicodeArchive, $unicodeWorkspace)) {
            Assert-True (Test-Path -LiteralPath (Join-Path $homeDir ".agents/skills/$name/SKILL.md")) "Expected case/frontmatter candidate: $name."
        }
        Remove-Item -LiteralPath (Join-Path $repo 'skills/default') -Recurse -Force
        Remove-Item -LiteralPath (Join-Path $repo 'skills/forest-service') -Recurse -Force
        foreach ($category in @('default', 'forest-service')) {
            New-Item -ItemType Directory -Path (Join-Path $repo "skills/$category") | Out-Null
        }
        $homeDir = Join-Path $workdir 'empty-home'
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -InstallArguments @('--fs')
        Assert-Equals 0 $result.ExitCode 'Expected both empty categories valid.'
        Assert-Equals 0 @(Get-ChildItem -Force -LiteralPath (Join-Path $homeDir '.agents/skills')).Count 'Expected no leaf copies from empty categories.'
    }
    finally { Remove-Workdir $workdir }
}

function Test-ChildProfileEnvironmentIsIsolated {
    $workdir = New-TestWorkdir
    $oldAppData = [System.Environment]::GetEnvironmentVariable('APPDATA', [System.EnvironmentVariableTarget]::Process)
    $oldLocalAppData = [System.Environment]::GetEnvironmentVariable('LOCALAPPDATA', [System.EnvironmentVariableTarget]::Process)
    try {
        $repo = Join-Path $workdir 'repo'
        $homeDir = Join-Path $workdir 'home'
        $outside = Join-Path $workdir 'external-profile'
        $outsideLocal = Join-Path $workdir 'external-local-profile'
        Write-FixtureFile (Join-Path $outside 'sentinel') @('Keep external profile.')
        Write-FixtureFile (Join-Path $outsideLocal 'sentinel') @('Keep external local profile.')
        [System.Environment]::SetEnvironmentVariable('APPDATA', $outside, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('LOCALAPPDATA', $outsideLocal, [System.EnvironmentVariableTarget]::Process)
        $before = Get-TreeFingerprint $outside
        $beforeLocal = Get-TreeFingerprint $outsideLocal
        # Observe routing through the same child process boundary used by real installer fixtures.
        Write-FixtureFile (Join-Path $repo 'scripts/install.ps1') @('[Console]::Out.WriteLine($env:APPDATA)', '[Console]::Out.WriteLine($env:LOCALAPPDATA)')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals 0 $result.ExitCode 'Expected the child environment probe to succeed.'
        Assert-Equals (Join-Path $homeDir 'AppData/Roaming') $result.Stdout[0] 'Expected child APPDATA routed inside disposable home.'
        Assert-Equals (Join-Path $homeDir 'AppData/Local') $result.Stdout[1] 'Expected child LOCALAPPDATA routed inside disposable home.'
        Assert-Equals $outside ([System.Environment]::GetEnvironmentVariable('APPDATA', [System.EnvironmentVariableTarget]::Process)) 'Expected parent APPDATA restored.'
        Assert-Equals $outsideLocal ([System.Environment]::GetEnvironmentVariable('LOCALAPPDATA', [System.EnvironmentVariableTarget]::Process)) 'Expected parent LOCALAPPDATA restored.'
        Assert-Equals $before (Get-TreeFingerprint $outside) 'Expected external profile bytes and modes unchanged.'
        Assert-Equals $beforeLocal (Get-TreeFingerprint $outsideLocal) 'Expected external local profile bytes and modes unchanged.'
    }
    finally {
        [System.Environment]::SetEnvironmentVariable('APPDATA', $oldAppData, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('LOCALAPPDATA', $oldLocalAppData, [System.EnvironmentVariableTarget]::Process)
        Remove-Workdir $workdir
    }
}

Test-ChildProfileEnvironmentIsIsolated
Test-HelperFailuresAreInstallerErrors
Test-EmptyCategoriesMarkersAndExclusions
Test-SourcePreflightIsImmutable
Test-SourceDiagnosticsWithLegacyEncoding
Test-InvalidSelectionIsImmutable
Test-SelectionEnvironmentAndRepeats
Test-ExplicitForestServiceSelection
Test-HelpWithoutSourcesOrDependencies
Test-FreshGeneratedHooksPreflightInstallsWithoutBytecode
Test-ProviderConfigHardLinksDoNotChangeOtherFiles
Test-ProviderConfigLinkedParentStopsBeforeMutation
Test-ProviderRefreshPreservesRetiredAndUserEntries
Test-ProviderMalformedJsonStopsBeforeMutation
Test-StaleGeneratedHooksStopBeforeDestinationMutation
Test-GeneratorFailureStopsBeforeDestinationMutation
Test-RebasesSharedReferenceLinksForFlatInstalledSkills
Test-RebasesReadOnlyMarkdownAndPreservesModesOnRepeat
Test-ActualAddySharedReferencesResolveAfterInstall
Test-PrunesWithoutOptionalSharedReferences
Test-PruningReadOnlyHardLinkPreservesExternalInode
Test-ReadOnlyHardLinkCopyRefusesExternalMutation
Test-RootLinkedSkillIsPreservedWithoutExternalMutation
Test-ExcludesAndPrunesSkillEvals
Test-SymlinkHandling
Test-FixedNameHardLinkHandling
Test-JunctionHandling
Test-CopiesFullGeminiTree
Test-InstalledHooksAreExecutable
Test-InstallsCodexAgentsBeforeOtherAssets
Test-CodexAgentsFailBeforeCopyingOtherAssets
Test-CodexHomeOverrideSelectsOneAgentDestination
Test-InstallsCodexHookAndGlobalConfiguration
Test-PreservesCodexConfigurationAndIsIdempotent
Test-RefusesSymlinkedCodexHookDestination
Test-PreservesFileModes
Test-CopiesCopilotConfigAndReferences
Test-MissingSourceFails

Write-Host "test-install.ps1: all tests passed."
exit 0
