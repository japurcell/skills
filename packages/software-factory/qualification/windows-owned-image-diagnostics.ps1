# Qualification query/projection helpers. Never return a message/path/signature.
function Get-OwnedImageCompilerDiagnostic {
    param([string]$Text)
    $empty = @{ code = 'none'; source = 'none'; line = 0 }
    if ($null -eq $Text -or [Text.Encoding]::UTF8.GetByteCount($Text) -gt 1048576) { return $empty }
    $lines = @($Text -split "`r?`n")
    if ($lines.Count -gt 8192) { return $empty }
    foreach ($row in $lines) {
        if ($row.Length -gt 4096) { continue }
        if ($row -match '(?:^|[\\/])windows-owned-image-(probe\.cpp|shared\.h|fixture\.cpp|fixture-dll\.cpp)\(([1-9][0-9]{0,3})(?:,[0-9]+)?\)\s*:\s*(?:fatal )?error (C[1-9][0-9]{3})\s*:') {
            $number = [int]$Matches[2]
            if ($number -le 4096) {
                $kind = @{ 'probe.cpp' = 'probe'; 'shared.h' = 'shared'; 'fixture.cpp' = 'fixture'; 'fixture-dll.cpp' = 'fixture-dll' }[$Matches[1]]
                return @{ code = $Matches[3]; source = $kind; line = $number }
            }
        }
        if ($row -cmatch '(?:^|\s)(?:fatal )?error (LNK[1-9][0-9]{3}|C[1-9][0-9]{3})\s*:') {
            return @{ code = $Matches[1]; source = 'none'; line = 0 }
        }
    }
    return $empty
}

function Get-OwnedImageSignatureCondition {
    param([object]$Signature)
    try {
        if ($Signature.Status -ne 'Valid') { return 'status-not-valid' }
        if ($null -eq $Signature.SignerCertificate) { return 'signer-absent' }
        if ($Signature.SignerCertificate.Subject -notmatch '(?:^|, )O=Microsoft Corporation(?:,|$)') { return 'subject-mismatch' }
        return 'none'
    } catch { return 'classification-failure' }
}

function Get-OwnedImageModuleProfile {
    param([string]$ModulePath, [string]$InboxModules, [string]$CoreModules, [object]$AutoLoadingPreference)
    $result = @{ inbox = 'unknown'; core = 'unknown'; autoload = 'unknown'; direct = 'unknown' }
    if ($null -eq $AutoLoadingPreference) { $result.autoload = 'all' }
    elseif ($AutoLoadingPreference -is [string] -or $AutoLoadingPreference -is [System.Management.Automation.PSModuleAutoLoadingPreference]) {
        if ($AutoLoadingPreference -eq 'All') { $result.autoload = 'all' }
        elseif ($AutoLoadingPreference -eq 'ModuleQualified') { $result.autoload = 'qualified' }
        elseif ($AutoLoadingPreference -eq 'None') { $result.autoload = 'none' }
    }
    if ($ModulePath.Length -gt 32768) { return $result }
    $entries = @($ModulePath -split ';')
    if ($entries.Count -gt 128) { return $result }
    foreach ($field in @('inbox', 'core')) {
        $target = if ($field -eq 'inbox') { $InboxModules } else { $CoreModules }
        if (-not [string]::IsNullOrEmpty($target)) {
            $target = $target.Replace('/', '\').TrimEnd('\')
            $result[$field] = 'absent'
            foreach ($entry in $entries) {
                if ([string]::Equals($entry.Replace('/', '\').TrimEnd('\'), $target, [StringComparison]::OrdinalIgnoreCase)) {
                    $result[$field] = 'present'
                }
            }
        }
    }
    return $result
}

function Invoke-OwnedImageSignatureCondition {
    param([string]$Path, [hashtable]$Context = @{}, [object]$Binding = $null)
    foreach ($field in @('inbox', 'core', 'autoload', 'direct')) { $Context[$field] = 'unknown' }
    try {
        $preference = $ExecutionContext.SessionState.PSVariable.Get('PSModuleAutoLoadingPreference')
        $value = if ($null -eq $preference) { $null } else { $preference.Value }
        $core = if ([string]::IsNullOrEmpty($env:ProgramFiles)) { '' } else { [IO.Path]::Combine($env:ProgramFiles, 'PowerShell', '7', 'Modules') }
        $profile = Get-OwnedImageModuleProfile ([Environment]::GetEnvironmentVariable('PSModulePath')) ([IO.Path]::Combine($PSHOME, 'Modules')) $core $value
        foreach ($field in @('inbox', 'core', 'autoload')) { $Context[$field] = $profile[$field] }
    } catch { }
    try {
        $command = Get-OwnedImageBoundSignatureCommand $Binding
    } catch { return 'command-probe-failure' }
    if ($command -isnot [System.Management.Automation.CmdletInfo]) { return 'command-probe-failure' }
    $Context.direct = 'imported'
    try {
        $signature = & $command -LiteralPath $Path
    } catch [System.Management.Automation.CommandNotFoundException] {
        return 'nested-command-unavailable'
    } catch [System.Management.Automation.ParameterBindingException] {
        return 'parameter-binding'
    } catch {
        return 'invocation-failure'
    }
    return (Get-OwnedImageSignatureCondition $signature)
}

function Format-OwnedImageBuildDiagnostic {
    param([string]$Category, [object]$Compiler = @{ code = 'none'; source = 'none'; line = 0 }, [object]$Tool = 'none', [object]$Condition = 'none')
    $unexpected = "OWNED_IMAGE_BUILD`t3`tunexpected`tnone`tnone`t0`tnone`tnone"
    if ($Category -cnotin @('host', 'path', 'existing-build', 'missing-msvc', 'tool-signature', 'compiler-version',
        'source', 'compile', 'build-cap', 'source-changed', 'binary', 'report', 'unexpected')) { return $unexpected }
    if ($Tool -isnot [string] -or $Condition -isnot [string]) { return $unexpected }
    if ($Category -ceq 'tool-signature') {
        if ($Tool -cnotin @('vswhere', 'compiler', 'linker')) { return $unexpected }
        if ($Condition -cnotin @('status-not-valid', 'signer-absent', 'subject-mismatch', 'api-failure', 'command-unavailable',
            'parameter-binding', 'invocation-failure', 'classification-failure', 'unresolved-command-unavailable',
            'nested-command-unavailable', 'command-probe-failure')) { return $unexpected }
    } elseif ($Tool -cne 'none' -or $Condition -cne 'none') { return $unexpected }
    if ($Compiler -isnot [Collections.IDictionary] -or $Compiler.Count -ne 3 -or
        @($Compiler.Keys | Where-Object { $_ -cnotin @('code', 'source', 'line') }).Count -ne 0) { return $unexpected }
    $code = $Compiler['code']; $source = $Compiler['source']; $number = $Compiler['line']
    if ($code -isnot [string] -or $source -isnot [string] -or $number -isnot [int]) { return $unexpected }
    if ($code -ceq 'none') {
        if ($source -cne 'none' -or $number -ne 0) { return $unexpected }
    } elseif ($Category -cne 'compile') { return $unexpected }
    elseif ($code -cmatch '^LNK[1-9][0-9]{3}\z') {
        if ($source -cne 'none' -or $number -ne 0) { return $unexpected }
    } elseif ($code -cmatch '^C[1-9][0-9]{3}\z') {
        if ($source -ceq 'none') { if ($number -ne 0) { return $unexpected } }
        elseif ($source -cnotin @('probe', 'shared', 'fixture', 'fixture-dll') -or $number -lt 1 -or $number -gt 4096) { return $unexpected }
    } else { return $unexpected }
    return "OWNED_IMAGE_BUILD`t3`t$Category`t$code`t$source`t$number`t$Tool`t$Condition"
}

function Format-OwnedImageModuleDiagnostic {
    param([object]$Context, [string]$Condition)
    if ($Context -isnot [Collections.IDictionary] -or $Context.Count -ne 4 -or
        @($Context.Keys | Where-Object { $_ -cnotin @('inbox', 'core', 'autoload', 'direct') }).Count -ne 0) { return $null }
    foreach ($field in @('inbox', 'core', 'autoload', 'direct')) { if ($Context[$field] -isnot [string]) { return $null } }
    if ($Context.inbox -cnotin @('present', 'absent', 'unknown') -or $Context.core -cnotin @('present', 'absent', 'unknown') -or
        $Context.autoload -cnotin @('all', 'qualified', 'none', 'unknown') -or $Context.direct -cnotin @('imported', 'not-imported', 'unknown')) { return $null }
    if (($Condition -ceq 'nested-command-unavailable' -and $Context.direct -cne 'imported') -or
        ($Condition -ceq 'unresolved-command-unavailable' -and $Context.direct -cne 'not-imported') -or
        ($Condition -ceq 'command-probe-failure' -and $Context.direct -cne 'unknown')) { return $null }
    return "OWNED_IMAGE_MODULE`t1`t$($Context.inbox)`t$($Context.core)`t$($Context.autoload)`t$($Context.direct)"
}

function Format-OwnedImageBuildObservation {
    param([string]$Category, [object]$Compiler, [object]$Tool, [object]$Condition, [object]$Context)
    $unexpected = "OWNED_IMAGE_BUILD`t3`tunexpected`tnone`tnone`t0`tnone`tnone"
    $first = Format-OwnedImageBuildDiagnostic $Category $Compiler $Tool $Condition
    if ($first -ceq $unexpected) { return $unexpected }
    if ($null -eq $Context) {
        if ($Condition -cin @('nested-command-unavailable', 'unresolved-command-unavailable', 'command-probe-failure')) { return $unexpected }
        return $first
    }
    if ($Category -cne 'tool-signature') { return $unexpected }
    $second = Format-OwnedImageModuleDiagnostic $Context $Condition
    if ($null -eq $second) { return $unexpected }
    return "$first`n$second"
}
