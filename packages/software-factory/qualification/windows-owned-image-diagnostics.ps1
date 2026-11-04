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

function Invoke-OwnedImageSignatureCondition {
    param([string]$Path)
    try {
        $signature = Get-AuthenticodeSignature -LiteralPath $Path
    } catch [System.Management.Automation.CommandNotFoundException] {
        return 'command-unavailable'
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
            'parameter-binding', 'invocation-failure', 'classification-failure')) { return $unexpected }
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
