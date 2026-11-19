# Native Windows qualification. No fixture condition is skipped.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $IsWindows) { throw 'This fixture requires native Windows.' }
$RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$InstallScriptSrc = Join-Path $RepoRoot 'scripts/install.ps1'
$suite = Join-Path $RepoRoot 'scripts/tests/installers/test-install.ps1'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($suite, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Cannot parse installer fixture suite.' }
foreach ($function in $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)) {
    Invoke-Expression $function.Extent.Text
}
$workdir = New-TestWorkdir
$repo = Join-Path $workdir 'repo'
New-FixtureRepo $repo
$source = Join-Path $repo 'skills/default/alpha'
$external = Join-Path $workdir 'external'
Write-FixtureFile (Join-Path $external 'sentinel.txt') @('external sentinel')
Write-FixtureFile (Join-Path $external 'evals/keep.txt') @('external cache must remain')
Write-FixtureFile (Join-Path $source '__pycache__/excluded.pyc') @('excluded')
Write-FixtureFile (Join-Path $source 'blocked/inside.txt') @('regular')
Write-FixtureFile (Join-Path $source 'replace.txt') @('replacement')
$sourceJunction = Join-Path $source 'junction'
New-Item -ItemType Junction -Path $sourceJunction -Target $external | Out-Null
Assert-Equals 'Junction' (Get-Item -Force -LiteralPath $sourceJunction).LinkType 'Source junction was not created.'
$before = Get-TreeFingerprint $external
$env:ADAPTER_SCAN_TRACE = Join-Path $workdir 'scandir.jsonl'
$homes = @{}
foreach ($name in @('public', 'prototype')) {
    $homeDir = Join-Path $workdir $name
    $dest = Join-Path $homeDir '.agents/skills/alpha'
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Write-FixtureFile (Join-Path $dest 'destination-only.txt') @('keep')
    # Require a real file symlink: no skip if the runner lacks privilege.
    New-Item -ItemType SymbolicLink -Path (Join-Path $dest 'replace.txt') -Target (Join-Path $external 'sentinel.txt') | Out-Null
    Assert-Equals 'SymbolicLink' (Get-Item -Force -LiteralPath (Join-Path $dest 'replace.txt')).LinkType 'Destination symlink was not created.'
    $homes[$name] = $homeDir
    foreach ($iteration in 1..2) {
        if ($name -eq 'public') {
            $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue '0'
            if ($result.ExitCode -ne 0) { throw "Public install failed: $($result.Stderr -join "`n")" }
        } else {
            & python (Join-Path $PSScriptRoot 'copy.py') $source $dest
            if ($LASTEXITCODE -ne 0) { throw 'Prototype copy failed.' }
            & python (Join-Path $repo 'scripts/rebase-skill-references.py') --source-dir $source --destination-dir $dest --prune
            if ($LASTEXITCODE -ne 0) { throw 'Prototype prune failed.' }
        }
        $junction = Get-Item -Force -LiteralPath (Join-Path $dest 'junction')
        Assert-Equals 'Junction' $junction.LinkType 'Installed junction lost its type.'
        Assert-Equals $external $junction.Target 'Installed junction target changed.'
        Assert-Equals $before (Get-TreeFingerprint $external) 'External target changed or was traversed.'
        Assert-Equals 'replacement' (Read-FileContent (Join-Path $dest 'replace.txt')) 'Destination link was not replaced with source file.'
        Assert-True (-not [string](Get-Item -Force -LiteralPath (Join-Path $dest 'replace.txt')).LinkType) 'Destination is still a link.'
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $dest '__pycache__'))) 'Excluded cache was copied.'
        Assert-Equals 'keep' (Read-FileContent (Join-Path $dest 'destination-only.txt')) 'Overlay lost destination file.'
        Assert-Equals 'regular' (Read-FileContent (Join-Path $dest 'blocked/inside.txt')) 'Regular file differs.'
        Write-Host "$name iteration $iteration passed: junction=$($junction.Target), file=replace.txt, cache absent"
    }
}
if ((Get-Content -Raw -LiteralPath $env:ADAPTER_SCAN_TRACE).Contains('__pycache__')) { throw 'Prototype enumerated an excluded cache.' }
Remove-Item Env:ADAPTER_SCAN_TRACE
# A destination directory junction must cause failure without changing the external tree.
foreach ($name in @('public', 'prototype')) {
    $homeDir = $homes[$name]
    $dest = Join-Path $homeDir '.agents/skills/alpha'
    Remove-Item -LiteralPath (Join-Path $dest 'blocked') -Recurse -Force
    New-Item -ItemType Junction -Path (Join-Path $dest 'blocked') -Target $external | Out-Null
    if ($name -eq 'public') {
        $result = Invoke-InstallProcess -Repo $repo -HomeDir $homeDir -Workdir $workdir -ForestServiceValue '0'
        $code = $result.ExitCode
    } else {
        & python (Join-Path $PSScriptRoot 'copy.py') $source $dest
        $code = $LASTEXITCODE
    }
    if ($code -eq 0) { throw "$name accepted a linked destination directory." }
    Assert-Equals 'Junction' (Get-Item -Force -LiteralPath (Join-Path $dest 'blocked')).LinkType 'Failure removed destination junction.'
    Assert-Equals $before (Get-TreeFingerprint $external) 'Failure modified external target.'
    Write-Host "$name failure recovery passed: exit=$code, destination junction and external fingerprint preserved"
}
Write-Host "PASS: native Windows adapter comparison; retained fixture: $workdir"
