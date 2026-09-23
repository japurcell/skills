$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { throw 'Markdown health native Windows test requires Windows.' }
foreach ($name in @('python', 'git', 'pwsh')) {
  Get-Command $name -CommandType Application -ErrorAction Stop | Out-Null
}
& python scripts/test-markdown-health.py
if ($LASTEXITCODE -ne 0) { throw "Markdown health Windows tests failed: $LASTEXITCODE" }
