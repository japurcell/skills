# Pure qualification diagnostic projection. Never return a compiler message/path.
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

function Format-OwnedImageBuildDiagnostic {
    param([string]$Category, [object]$Compiler = @{ code = 'none'; source = 'none'; line = 0 })
    $unexpected = "OWNED_IMAGE_BUILD`t1`tunexpected`tnone`tnone`t0"
    if ($Category -cnotin @('host', 'path', 'existing-build', 'missing-msvc', 'tool-signature', 'compiler-version',
        'source', 'compile', 'build-cap', 'source-changed', 'binary', 'report', 'unexpected')) { return $unexpected }
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
    return "OWNED_IMAGE_BUILD`t1`t$Category`t$code`t$source`t$number"
}
