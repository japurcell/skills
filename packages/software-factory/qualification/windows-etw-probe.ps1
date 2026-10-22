param(
    [Parameter(Mandatory = $true)][string]$NodePath,
    [Parameter(Mandatory = $true)][string]$EvidenceDir
)

$ErrorActionPreference = 'Stop'
try {
    Add-Type -LiteralPath (Join-Path $PSScriptRoot 'windows-etw-probe.cs')
    exit [WindowsEtwProbe]::Run($NodePath, $EvidenceDir)
} catch {
    $message = $_.Exception.Message
    if ($message.Length -gt 1024) { $message = $message.Substring(0, 1024) }
    [Console]::Error.WriteLine('ETW bridge: {0}', $message)
    exit 4
}
