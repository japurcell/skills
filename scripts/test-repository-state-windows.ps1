#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) {
    Write-Output 'SKIP: native Windows repository-state tests require Windows'
    exit 0
}
$repoRoot = Split-Path $PSScriptRoot -Parent
$workdir = Join-Path ([System.IO.Path]::GetTempPath()) ("repo-state-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $workdir | Out-Null
try {
    $repo = Join-Path $workdir 'repo'
    New-Item -ItemType Directory -Path $repo | Out-Null
    & git -C $repo init -q
    if ($LASTEXITCODE -ne 0) { throw 'git init failed' }
    $linked = Join-Path $workdir 'linked'
    $gitdir = Join-Path $workdir 'external-git'
    $common = Join-Path $workdir 'common-git'
    foreach ($directory in @($linked, $gitdir, $common)) { New-Item -ItemType Directory -Path $directory | Out-Null }
    [System.IO.File]::WriteAllText((Join-Path $linked '.git'), "gitdir: $gitdir`n")
    [System.IO.File]::WriteAllText((Join-Path $gitdir 'commondir'), "../common-git`n")
    $providers = @(
        @{ Name='copilot'; Hook='.copilot/hooks/scripts/repository-state.py'; Tool='powershell'; Key='toolArgs' },
        @{ Name='gemini'; Hook='.gemini/hooks/scripts/repository-state.py'; Tool='run_shell_command'; Key='tool_input' },
        @{ Name='codex'; Hook='.codex/hooks/repository-state.py'; Tool='Bash'; Key='tool_input' }
    )
    foreach ($provider in $providers) {
        $hook = Join-Path $repoRoot $provider.Hook
        foreach ($command in @('Set-Content .GIT\config bad', 'git restore tracked.txt', 'git clean -fd',
                            'sed.exe -Ei -e s/a/b/ .GIT\config', 'perl.exe -pi -e s/a/b/ .GIT\config',
                            'truncate.exe -s 0 .GIT\config', 'install.exe source.txt .GIT\config')) {
            if ($provider.Name -eq 'copilot') { $hookPayload = @{ cwd=$repo; toolName=$provider.Tool; toolArgs=@{ command=$command } } }
            else { $hookPayload = @{ cwd=$repo; tool_name=$provider.Tool; tool_input=@{ command=$command } } }
            $json = $hookPayload | ConvertTo-Json -Compress -Depth 5
            $result = $json | & python -I -S -B $hook | ConvertFrom-Json
            if ($LASTEXITCODE -ne 0) { throw "hook failed for $($provider.Name)" }
            if ($provider.Name -eq 'copilot' -and $result.permissionDecision -cne 'deny') { throw 'Copilot denial missing' }
            if ($provider.Name -eq 'gemini' -and $result.decision -cne 'deny') { throw 'Gemini denial missing' }
            if ($provider.Name -eq 'codex' -and $result.hookSpecificOutput.permissionDecision -cne 'deny') { throw 'Codex denial missing' }
        }
        foreach ($target in @((Join-Path $linked '.GIT'), (Join-Path $gitdir 'index'), (Join-Path $common 'config'))) {
            $editor = if ($provider.Name -eq 'copilot') { @{ cwd=$linked; toolName='edit'; toolArgs=@{ file_path=$target; content='bad' } } }
                      else { @{ cwd=$linked; tool_name='write_file'; tool_input=@{ file_path=$target; content='bad' } } }
            $editorResult = ($editor | ConvertTo-Json -Compress -Depth 5) | & python -I -S -B $hook | ConvertFrom-Json
            $decision = if ($provider.Name -eq 'copilot') { $editorResult.permissionDecision }
                        elseif ($provider.Name -eq 'gemini') { $editorResult.decision }
                        else { $editorResult.hookSpecificOutput.permissionDecision }
            if ($LASTEXITCODE -ne 0 -or $decision -cne 'deny') { throw "linked Git metadata write was not denied for $($provider.Name)" }
        }
        foreach ($quotedCommand in @("echo 'git checkout branch'", "echo '.git/config > file'")) {
            $quotedPayload = if ($provider.Name -eq 'copilot') { @{ cwd=$repo; toolName=$provider.Tool; toolArgs=@{ command=$quotedCommand } } }
                             else { @{ cwd=$repo; tool_name=$provider.Tool; tool_input=@{ command=$quotedCommand } } }
            $quotedResult = ($quotedPayload | ConvertTo-Json -Compress -Depth 5) | & python -I -S -B $hook | ConvertFrom-Json
            $quotedExitCode = $LASTEXITCODE
            $quotedPropertyCount = @($quotedResult.PSObject.Properties).Count
            if ($quotedExitCode -ne 0 -or $quotedPropertyCount -ne 0) { throw "quoted prose was denied for $($provider.Name)" }
        }
        foreach ($readCommand in @('git status', 'sed.exe -n -e p .GIT\config', 'perl.exe -ne print .GIT\config')) {
            $read = if ($provider.Name -eq 'copilot') { @{ cwd=$repo; toolName=$provider.Tool; toolArgs=@{ command=$readCommand } } }
                    else { @{ cwd=$repo; tool_name=$provider.Tool; tool_input=@{ command=$readCommand } } }
            $readResult = ($read | ConvertTo-Json -Compress -Depth 5) | & python -I -S -B $hook | ConvertFrom-Json
            $readExitCode = $LASTEXITCODE
            $readPropertyCount = @($readResult.PSObject.Properties).Count
            if ($readExitCode -ne 0 -or $readPropertyCount -ne 0) { throw "safe read blocked for $($provider.Name): $readCommand" }
        }
    }
    Write-Output 'PASS: native Windows repository-state hook envelopes'
}
finally {
    Remove-Item -LiteralPath $workdir -Recurse -Force -ErrorAction SilentlyContinue
}
