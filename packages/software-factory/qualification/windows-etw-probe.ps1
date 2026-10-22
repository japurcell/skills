param(
    [Parameter(Mandatory = $true)][string]$NodePath,
    [Parameter(Mandatory = $true)][string]$EvidenceDir
)

$ErrorActionPreference = 'Stop'
try {
    Add-Type -LiteralPath (Join-Path $PSScriptRoot 'windows-etw-probe.cs')
    exit [WindowsEtwProbe]::Run($NodePath, $EvidenceDir)
} catch {
    [Console]::Error.WriteLine('ETW bridge failed: bridge/operation-failed')
    exit 4
}
