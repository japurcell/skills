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
         with a non-default executable mode (skills/alpha/tool.sh at 755) keeps
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
        (Join-Path $Repo 'skills/alpha/evals'),
        (Join-Path $Repo 'skills/beta-workspace'),
        (Join-Path $Repo 'skills/archive'),
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
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/install-codex-agents.py') -Destination (Join-Path $Repo 'scripts/install-codex-agents.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'scripts/install-codex-hooks.py') -Destination (Join-Path $Repo 'scripts/install-codex-hooks.py') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.codex/global-hooks.json') -Destination (Join-Path $Repo '.codex/global-hooks.json') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.codex/AGENTS.md') -Destination (Join-Path $Repo '.codex/AGENTS.md') -Force
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.codex/hooks/load-required-skills.py') -Destination (Join-Path $Repo '.codex/hooks/load-required-skills.py') -Force

    Write-FixtureFile (Join-Path $Repo 'skills/alpha/SKILL.md') @('---', 'name: alpha', '---', 'Standalone.')
    Write-FixtureFile (Join-Path $Repo 'skills/alpha/evals/evals.json') @('fixture eval content')
    Write-FixtureFile (Join-Path $Repo 'skills/alpha/tool.sh') @('#!/bin/sh', 'echo tool')
    # Non-default source mode: Test-PreservesFileModes asserts it survives install (non-Windows only).
    if (-not $IsWindows) {
        $executable = [System.IO.UnixFileMode]::UserRead -bor
            [System.IO.UnixFileMode]::UserWrite -bor
            [System.IO.UnixFileMode]::UserExecute -bor
            [System.IO.UnixFileMode]::GroupRead -bor
            [System.IO.UnixFileMode]::GroupExecute -bor
            [System.IO.UnixFileMode]::OtherRead -bor
            [System.IO.UnixFileMode]::OtherExecute
        [System.IO.File]::SetUnixFileMode((Join-Path $Repo 'skills/alpha/tool.sh'), $executable)
    }
    Write-FixtureFile (Join-Path $Repo 'skills/beta-workspace/SKILL.md') @('workspace skill should not copy')
    Write-FixtureFile (Join-Path $Repo 'skills/archive/README.md') @('archive entry should not copy')
    # Edge-case names: `[ ]` must stay literal (excluded), and the -workspace suffix
    # match must be case-sensitive (My-Workspace is NOT excluded, matching bash).
    Write-FixtureFile (Join-Path $Repo 'skills/weird[1]-workspace/SKILL.md') @('bracket workspace skill should not copy')
    Write-FixtureFile (Join-Path $Repo 'skills/My-Workspace/SKILL.md') @('case-variant workspace name should copy')
    Write-FixtureFile (Join-Path $Repo 'agents/helper.md') @('---', 'name: helper', 'description: Fixture helper agent.', '---', 'Use alpha.')
    Write-FixtureFile (Join-Path $Repo 'agents/nested/helper.md') @('---', 'name: nested-helper', 'description: Nested fixture helper agent.', '---', 'Use alpha deeply.')
    Write-FixtureFile (Join-Path $Repo 'references/notes.md') @('Reference notes.')
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.gemini/GEMINI.md') -Destination (Join-Path $Repo '.gemini/GEMINI.md') -Force
    Write-FixtureFile (Join-Path $Repo '.gemini/policies/plan-custom-directory.toml') @('Nested policy.')
    Write-FixtureFile (Join-Path $Repo '.gemini/.hidden-note') @('Hidden note.')
    Copy-Item -LiteralPath (Join-Path $RepoRoot '.copilot/copilot-instructions.md') -Destination (Join-Path $Repo '.copilot/copilot-instructions.md') -Force
    Write-FixtureFile (Join-Path $Repo '.copilot/lsp-config.json') @('{}')
    Write-FixtureFile (Join-Path $Repo '.copilot/hooks/test-hook.sh') @('#!/bin/bash', 'echo hook')
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

        New-FixtureRepo $repo
        $outputPath = Get-GeneratedRtkOutputPath $repo
        Add-Content -LiteralPath (Join-Path $repo $outputPath) -Value '# stale fixture output' -Encoding utf8NoBOM
        Write-FixtureFile (Join-Path $homeDir 'preserved/sentinel.txt') @('do not change')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $before = Get-TreeFingerprint $homeDir

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 1 -Actual $result.ExitCode -Message 'Expected stale generated hooks to exit install.ps1 with code 1.'
        Assert-True -Condition (($result.Stdout -join "`n") -match [regex]::Escape($outputPath)) -Message 'Expected stale repository-relative output path on stdout.'
        Assert-True -Condition (($result.Stderr -join "`n") -match [regex]::Escape('python3 scripts/generate-hooks.py --write')) -Message 'Expected stale-output recovery command on stderr.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected stale preflight to leave the destination tree byte-for-byte unchanged with no new directories.'
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

        New-FixtureRepo $repo
        $manifestPath = Join-Path $repo 'hooks/manifest.py'
        $manifest = Get-Content -LiteralPath $manifestPath -Raw
        Set-Content -LiteralPath $manifestPath -Value $manifest.Replace('GeneratedTarget("send_event", "copilot"', 'GeneratedTarget("send_event", "unknown"') -Encoding utf8NoBOM -NoNewline
        Write-FixtureFile (Join-Path $homeDir 'preserved/sentinel.txt') @('do not change')
        Initialize-ChildPowerShellHome -HomeDir $homeDir -Workdir $workdir
        $before = Get-TreeFingerprint $homeDir

        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir
        Assert-Equals -Expected 2 -Actual $result.ExitCode -Message 'Expected a generator failure to exit install.ps1 with code 2.'
        Assert-True -Condition (($result.Stderr -join "`n") -match "Unknown provider 'unknown'") -Message 'Expected the generator diagnostic on stderr.'
        Assert-True -Condition (($result.Stderr -join "`n") -notmatch [regex]::Escape('python3 scripts/generate-hooks.py --write')) -Message 'Expected generator failures to omit stale-output recovery advice.'
        Assert-Equals -Expected $before -Actual (Get-TreeFingerprint $homeDir) -Message 'Expected generator failure preflight to leave the destination tree byte-for-byte unchanged with no new directories.'
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
        [string]$CodexHome = $null
    )

    $oldHome = [System.Environment]::GetEnvironmentVariable('HOME', [System.EnvironmentVariableTarget]::Process)
    $oldUserProfile = [System.Environment]::GetEnvironmentVariable('USERPROFILE', [System.EnvironmentVariableTarget]::Process)
    $oldCodexHome = [System.Environment]::GetEnvironmentVariable('CODEX_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgCacheHome = [System.Environment]::GetEnvironmentVariable('XDG_CACHE_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgConfigHome = [System.Environment]::GetEnvironmentVariable('XDG_CONFIG_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgDataHome = [System.Environment]::GetEnvironmentVariable('XDG_DATA_HOME', [System.EnvironmentVariableTarget]::Process)
    $childStdoutPath = Join-Path $Workdir 'child-stdout.txt'
    $childStderrPath = Join-Path $Workdir 'child-stderr.txt'
    try {
        [System.Environment]::SetEnvironmentVariable('HOME', $HomeDir, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('USERPROFILE', $HomeDir, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('CODEX_HOME', $CodexHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', (Join-Path $Workdir 'xdg-cache'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', (Join-Path $Workdir 'xdg-config'), [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', (Join-Path $Workdir 'xdg-data'), [System.EnvironmentVariableTarget]::Process)
        & pwsh -NoProfile -File (Join-Path $Repo 'scripts/install.ps1') 1> $childStdoutPath 2> $childStderrPath
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
        [System.Environment]::SetEnvironmentVariable('HOME', $oldHome, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('USERPROFILE', $oldUserProfile, [System.EnvironmentVariableTarget]::Process)
        [System.Environment]::SetEnvironmentVariable('CODEX_HOME', $oldCodexHome, [System.EnvironmentVariableTarget]::Process)
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

# A child pwsh initializes user-module and telemetry state under HOME before it runs the
# installer. Establish that host-owned state before a preflight mutation snapshot so the
# snapshot covers only paths install.ps1 can change.
function Initialize-ChildPowerShellHome {
    param(
        [string]$HomeDir,
        [string]$Workdir
    )

    $oldHome = [System.Environment]::GetEnvironmentVariable('HOME', [System.EnvironmentVariableTarget]::Process)
    $oldUserProfile = [System.Environment]::GetEnvironmentVariable('USERPROFILE', [System.EnvironmentVariableTarget]::Process)
    $oldXdgCacheHome = [System.Environment]::GetEnvironmentVariable('XDG_CACHE_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgConfigHome = [System.Environment]::GetEnvironmentVariable('XDG_CONFIG_HOME', [System.EnvironmentVariableTarget]::Process)
    $oldXdgDataHome = [System.Environment]::GetEnvironmentVariable('XDG_DATA_HOME', [System.EnvironmentVariableTarget]::Process)
    try {
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

        $toolSrc = Join-Path $repo 'skills/alpha/tool.sh'
        $toolSrcMode = [System.IO.File]::GetUnixFileMode($toolSrc)
        Assert-True -Condition (([int]$toolSrcMode -band [int][System.IO.UnixFileMode]::UserExecute) -ne 0) -Message "Fixture setup error: $toolSrc should be executable."

        $skillSrc = Join-Path $repo 'skills/alpha/SKILL.md'
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

        # Deliberate skip: hosts that cannot create symlinks (e.g. Windows without the
        # link-creation privileges) report a skip instead of a false pass.
        try {
            New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'skills/alpha/linked-secret.txt') -Target $secretTargetPath -Force | Out-Null
            New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'skills/alpha/linked-dir') -Target $dirTargetPath -Force | Out-Null
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
        Assert-Equals -Expected '{"global":"hardlink-settings"}' -Actual (Read-FileContent $installedSettingsPath) -Message "Expected the installed settings.json to keep the hard-linked source content."
        Assert-True -Condition (([int]$installed.Attributes -band [int][System.IO.FileAttributes]::ReparsePoint) -eq 0) -Message "Expected the installed settings.json to be a regular file."
        if (-not $IsWindows) {
            $targetMode = [System.IO.File]::GetUnixFileMode($hardLinkSource)
            Assert-Equals -Expected $targetMode -Actual ([System.IO.File]::GetUnixFileMode($installedSettingsPath)) -Message "Expected the installed settings.json to keep the hard-linked source file mode."
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
        $junctionSentinelPath = Join-Path $junctionTargetPath 'keep.txt'
        Write-FixtureFile $junctionSentinelPath @('junction sentinel must not change')
        $junctionSentinelBefore = Read-FileContent $junctionSentinelPath

        try {
            New-Item -ItemType Junction -Path (Join-Path $repo '.gemini/junction-dir') -Target $junctionTargetPath -Force | Out-Null
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
        Assert-True -Condition $installedGeminiInstructions.Contains('use `write_file` to create the complete script as a saved file, then execute that saved file.') -Message 'Expected installed Gemini guidance to require file-first PowerShell authoring.'
        Assert-Equals -Expected (Read-FileContent (Join-Path $repo '.copilot/copilot-instructions.md')) -Actual $installedCopilotInstructions -Message 'Expected Copilot instructions to be copied into ~/.copilot.'
        Assert-True -Condition $installedCopilotInstructions.Contains("use Copilot's native file-create or file-edit tool to create the complete script as a saved file, then execute that saved file.") -Message 'Expected installed Copilot guidance to require file-first PowerShell authoring.'
        Assert-True -Condition $installedCodexInstructions.Contains('use Codex''s native file-write or file-edit tool, such as `apply_patch`, to create the complete script as a saved file, then execute that saved file.') -Message 'Expected installed Codex guidance to require file-first PowerShell authoring.'
        Assert-Equals -Expected "---`nname: helper`ndescription: Fixture helper agent.`n---`nUse alpha." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/agents/helper.md')) -Message "Expected agents to be copied into ~/.gemini/agents."
        Assert-Equals -Expected "---`nname: nested-helper`ndescription: Nested fixture helper agent.`n---`nUse alpha deeply." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/agents/nested/helper.md')) -Message "Expected nested agents to be copied recursively into ~/.gemini/agents."
        Assert-Equals -Expected "---`nname: helper`ndescription: Fixture helper agent.`n---`nUse alpha." -Actual (Read-FileContent (Join-Path $homeDir '.copilot/agents/helper.md')) -Message "Expected agents to be copied into ~/.copilot/agents."
        Assert-Equals -Expected "---`nname: nested-helper`ndescription: Nested fixture helper agent.`n---`nUse alpha deeply." -Actual (Read-FileContent (Join-Path $homeDir '.copilot/agents/nested/helper.md')) -Message "Expected nested agents to be copied recursively into ~/.copilot/agents."
        Assert-Equals -Expected "Nested policy." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/policies/plan-custom-directory.toml')) -Message "Expected nested Gemini files to be copied recursively."
        Assert-Equals -Expected "Hidden note." -Actual (Read-FileContent (Join-Path $homeDir '.gemini/.hidden-note')) -Message "Expected hidden Gemini files to be copied recursively."
        Assert-Equals -Expected "#!/bin/bash`necho hook" -Actual (Read-FileContent (Join-Path $homeDir '.copilot/hooks/test-hook.sh')) -Message "Expected hooks to be copied into ~/.copilot/hooks."
        Assert-Equals -Expected '{"global":"settings"}' -Actual (Read-FileContent (Join-Path $homeDir '.gemini/settings.json')) -Message "Expected global Gemini settings to overwrite repo-local settings during install."

        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $homeDir '.gemini/.gemini'))) -Message "Expected the installer to copy Gemini contents into ~/.gemini, not nest another .gemini directory."
    }
    finally {
        Remove-Workdir $workdir
    }
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
        foreach ($rel in $hookRelPaths + @($upperPyRel)) {
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
        foreach ($relative in @('scan-secrets.py', 'tool-guard.py', 'markdown-health.py', 'helpers/common.py', 'helpers/audit.py')) {
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
        Assert-Equals -Expected 'python3 ~/.codex/hooks/rtk-explicit-codex.py' -Actual $config['hooks']['PreToolUse'][0]['hooks'][0]['command'] -Message 'Expected PreToolUse to register explicit RTK rewriting.'
        $preCommands = @($config['hooks']['PreToolUse'][1]['hooks'] | ForEach-Object { $_['command'] })
        Assert-True -Condition ($preCommands -contains 'python3 ~/.codex/hooks/scan-secrets.py') -Message 'Expected PreToolUse to retain the maintained scanner.'
        Assert-True -Condition ($preCommands -contains 'python3 ~/.codex/hooks/tool-guard.py') -Message 'Expected Codex Tool Guardian registration.'
        $stopCommands = @($config['hooks']['Stop'][0]['hooks'] | ForEach-Object { $_['command'] })
        Assert-True -Condition ($stopCommands -contains 'python3 ~/.codex/hooks/scan-secrets.py') -Message 'Expected Stop to retain the maintained scanner.'
        foreach ($event in @('PreToolUse', 'PostToolUse', 'Stop')) {
            $commands = @($config['hooks'][$event] | ForEach-Object { $_['hooks'] } | ForEach-Object { $_['command'] })
            Assert-True -Condition ($commands -contains 'python3 ~/.codex/hooks/markdown-health.py') -Message "Expected $event to use the Markdown hook."
        }
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
assert tomllib.loads(agent_path.read_text(encoding="utf-8")) == {
    "name": "helper",
    "description": "Fixture helper agent.",
    "developer_instructions": "Use alpha.\n",
}
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

Test-FreshGeneratedHooksPreflightInstallsWithoutBytecode
Test-StaleGeneratedHooksStopBeforeDestinationMutation
Test-GeneratorFailureStopsBeforeDestinationMutation
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
