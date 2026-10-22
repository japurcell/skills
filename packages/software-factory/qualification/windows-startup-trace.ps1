param(
    [Parameter(Mandatory = $true)][string]$SpecPath,
    [Parameter(Mandatory = $true)][string]$StagePath
)

$ErrorActionPreference = 'Stop'
function Write-Stage([string]$Label) {
    $line = "{0}`t{1}`n" -f [DateTime]::UtcNow.ToString('O'), $Label
    [IO.File]::AppendAllText($StagePath, $line, [Text.UTF8Encoding]::new($false))
}

try {
    Write-Stage 'ps-entry'
    $spec = Get-Content -LiteralPath $SpecPath -Raw | ConvertFrom-Json
    Write-Stage 'spec-read'
    $launchMode = [string]$spec.launchMode
    if ($launchMode -cne 'no-window' -and $launchMode -cne 'detached-process') {
        throw "unsupported qualification launch mode: $launchMode"
    }
    $source = Join-Path $PSScriptRoot 'windows-startup-trace.cs'
    Write-Stage 'add-type-start'
    Add-Type -Path $source
    Write-Stage 'add-type-end'
    $launch = [string[]]@(
        [string]$spec.executable,
        [string]$spec.cwd,
        [string]$spec.stdout,
        [string]$spec.stderr,
        [string]$spec.trace,
        [string]$spec.timeoutMs
    ) + [string[]]@($spec.args)
    Write-Stage 'native-call'
    $result = [WindowsStartupTrace]::Trace($launch, $StagePath, $launchMode)
    Write-Stage 'native-return'
    exit $result
} catch {
    $failure = $_.Exception
    try { Write-Stage 'ps-error' } catch { }
    $message = $failure.Message
    if ($message.Length -gt 1024) { $message = $message.Substring(0, 1024) }
    [Console]::Error.WriteLine('{0}: {1}', $failure.GetType().FullName, $message)
    exit 4
}
