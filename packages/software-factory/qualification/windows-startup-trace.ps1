param([Parameter(Mandatory = $true)][string]$SpecPath)

$ErrorActionPreference = 'Stop'
$spec = Get-Content -LiteralPath $SpecPath -Raw | ConvertFrom-Json
$source = Join-Path $PSScriptRoot 'windows-startup-trace.cs'
Add-Type -Path $source
$launch = [string[]]@(
    [string]$spec.executable,
    [string]$spec.cwd,
    [string]$spec.stdout,
    [string]$spec.stderr,
    [string]$spec.trace,
    [string]$spec.timeoutMs
) + [string[]]@($spec.args)
$result = [WindowsStartupTrace]::Main($launch)
exit $result
