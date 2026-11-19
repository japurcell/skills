param([string]$Installer)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
# Reuse native operations from the current installer without executing its entry point.
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Installer, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Cannot parse installer' }
$names = @('Fail', 'Install-PreservedLink', 'Complete-CopyMode', 'Assert-SkillDirectoryIsSafe', 'Copy-FileWithMode', 'Set-FileModeFrom')
foreach ($name in $names) {
    $function = $ast.Find({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq $name }, $true)
    if ($null -eq $function) { throw "Missing native operation: $name" }
    Invoke-Expression $function.Extent.Text
}
# This also protects source-file-over-destination-link, before Copy-Item runs.
function Remove-UnsafeSkillFileDestination {
    param([string]$Path)
    $entry = Get-Item -Force -LiteralPath $Path -ErrorAction SilentlyContinue
    if ($null -eq $entry -or -not [string]$entry.LinkType) { return }
    if ([string]$entry.LinkType -ceq 'HardLink' -and $entry.IsReadOnly) {
        Fail "Refusing to change read-only hard-linked file: $Path"
    }
    if ([string]$entry.LinkType -cin @('SymbolicLink', 'Junction')) {
        if ($IsWindows -and $entry.PSIsContainer) { [System.IO.Directory]::Delete($Path) }
        else { [System.IO.File]::Delete($Path) }
    } else { Remove-Item -Force -LiteralPath $Path }
}
$stack = [System.Collections.Generic.Stack[object]]::new()
try {
    $operations = @(ConvertFrom-Json -InputObject ([Console]::In.ReadToEnd()))
    foreach ($op in $operations) {
        switch ($op.kind) {
            'enter' {
                Assert-SkillDirectoryIsSafe -Path $op.destination
                New-Item -ItemType Directory -Path $op.destination -Force | Out-Null
                $mode = $null
                if (-not $IsWindows) {
                    $mode = [System.IO.File]::GetUnixFileMode($op.destination)
                    [System.IO.File]::SetUnixFileMode($op.destination, ($mode -bor [System.IO.UnixFileMode]::UserWrite))
                }
                $stack.Push(@{source=$op.source; destination=$op.destination; mode=$mode})
            }
            'leave' {
                $entry = $stack.Peek()
                Complete-CopyMode -Source $entry.source -Destination $entry.destination -Copied $true -OriginalMode $entry.mode
                $null = $stack.Pop()
            }
            'file' { Copy-FileWithMode -Source $op.source -Destination $op.destination -FilterSkillArtifacts }
            'link' {
                $entry = Get-Item -Force -LiteralPath $op.source
                if ([string]$entry.LinkType -cnotin @('SymbolicLink', 'Junction')) { throw "Unsupported reparse point: $($op.source)" }
                Remove-UnsafeSkillFileDestination -Path $op.destination
                Install-PreservedLink -SourceDescription $op.source -Destination $op.destination -LinkType $entry.LinkType -Target $entry.Target
            }
            default { throw "Unknown operation: $($op.kind)" }
        }
    }
    if ($stack.Count) { throw 'Unbalanced directory operations' }
    [Console]::Out.WriteLine('{"success":true}')
}
finally {
    while ($stack.Count) {
        $entry = $stack.Pop()
        Complete-CopyMode -Source $entry.source -Destination $entry.destination -Copied $false -OriginalMode $entry.mode
    }
}
