param(
    [Parameter(Mandatory = $true)][string]$NodePath,
    [Parameter(Mandatory = $true)][string]$EvidenceDir,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-f0-9]{64}$')][string]$ExpectedExecutableSha256
)

$ErrorActionPreference = 'Stop'
try {
    Add-Type -LiteralPath (Join-Path $PSScriptRoot 'windows-etw-probe.cs')
    exit [WindowsEtwProbe]::Run($NodePath, $EvidenceDir, $ExpectedExecutableSha256,
        (Join-Path $PSScriptRoot 'windows-etw-child-fixture.cjs'))
} catch {
    [Console]::Error.WriteLine('ETW bridge failed: bridge/operation-failed')
    exit 4
}
