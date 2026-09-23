$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$tag = 'dev-0.50.0-rc.451'
$asset = 'rtk-x86_64-pc-windows-msvc.zip'
$expected = '636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7'
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) ("rtk-m9-" + [guid]::NewGuid().ToString('N'))
$archive = Join-Path $scratch $asset
$oldUserProfile = $env:USERPROFILE
New-Item -ItemType Directory -Path $scratch | Out-Null
try {
  Invoke-WebRequest -Uri "https://github.com/rtk-ai/rtk/releases/download/$tag/$asset" -OutFile $archive
  if ((Get-FileHash -Algorithm SHA256 $archive).Hash.ToLowerInvariant() -ne $expected) {
    throw 'Published Windows RTK checksum mismatch'
  }
  $testHome = Join-Path $scratch 'home'
  New-Item -ItemType Directory -Path $testHome | Out-Null
  & python (Join-Path $repoRoot 'scripts/install-rtk-prerelease.py') --home $testHome --archive $archive --platform windows-amd64
  if ($LASTEXITCODE -ne 0) { throw 'Verified Windows RTK installation failed' }
  $env:USERPROFILE = $testHome
  $hook = Join-Path $repoRoot '.codex/hooks/rtk-explicit-codex.py'
  $payload = @{ hook_event_name = 'PreToolUse'; tool_name = 'Bash'; tool_input = @{ command = 'rtk --version && rtk read absent-file' } } | ConvertTo-Json -Compress -Depth 5
  $result = $payload | & python $hook | ConvertFrom-Json
  if ($null -eq $result.hookSpecificOutput.updatedInput.command) { throw 'Codex RTK rewrite was absent' }
  if (($result.hookSpecificOutput.updatedInput.command | Select-String -Pattern 'rtk-agent-launcher.py' -AllMatches).Matches.Count -ne 2) {
    throw 'Codex RTK rewrite did not preserve both chained invocations'
  }
  $launcher = Join-Path $repoRoot '.codex/hooks/rtk-agent-launcher.py'
  $version = & python $launcher --version
  if ($LASTEXITCODE -ne 0 -or $version -notmatch 'rtk 0\.48\.0') { throw 'Verified Windows RTK executable did not run' }
  $missing = & python $launcher read (Join-Path $scratch 'absent-file') 2>&1 | Out-String
  if ($LASTEXITCODE -eq 0 -or $missing -notmatch 'No such file|cannot find|not found' -or $missing -match 'No hook installed') {
    throw 'RTK missing-file diagnostic or exit code was lost'
  }
  Write-Host 'Native Windows RTK asset, rewrite, and diagnostic checks passed.'
}
finally {
  $env:USERPROFILE = $oldUserProfile
  Remove-Item -LiteralPath $scratch -Recurse -Force -ErrorAction SilentlyContinue
}
