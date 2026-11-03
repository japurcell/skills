param(
    [Parameter(Mandatory = $true)][string]$SpecPath,
    [Parameter(Mandatory = $true)][string]$EvidenceDir
)
$ErrorActionPreference = 'Stop'
try {
    $item = Get-Item -LiteralPath $SpecPath -ErrorAction Stop
    if ($item.Length -gt 65536 -or $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'spec' }
    $spec = [IO.File]::ReadAllText($SpecPath) | ConvertFrom-Json
    Add-Type -Path (Join-Path $PSScriptRoot 'windows-etw-route.cs') -ErrorAction Stop
    $paths = [string[]]@($spec.pins | ForEach-Object { $_.path })
    $digests = [string[]]@($spec.pins | ForEach-Object { $_.sha256 })
    $labels = [string[]]@($spec.pins | ForEach-Object { $_.label })
    $result = [WindowsEtwRoute]::Run([string]$spec.case, [string]$spec.node,
        $EvidenceDir, [string]$spec.launcher, $SpecPath, $paths, $digests, $labels)
    exit $result
} catch {
    [Console]::Error.WriteLine('ETW route bridge failed')
    exit 4
}
