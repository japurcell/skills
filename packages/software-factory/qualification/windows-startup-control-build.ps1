param(
    [Parameter(Mandatory = $true)][string]$SourcePath,
    [Parameter(Mandatory = $true)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'
Add-Type -LiteralPath $SourcePath -OutputAssembly $OutputPath -OutputType ConsoleApplication
if (-not [IO.File]::Exists($OutputPath)) {
    throw 'detached control executable was not created'
}
[Console]::Out.Write('control-built')
