# Qualification only. No discovered executable is ever invoked, even for version/help.
param([string]$Mode)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$script:metadataReason = 'none'
$script:metadataBytes = 0L
$script:metadataFiles = [Collections.Generic.List[object]]::new()
$script:metadataInstallations = [Collections.Generic.List[string]]::new()
$script:metadataSdkVersions = [Collections.Generic.List[string]]::new()
$script:metadataSignatureCommand = $null
$script:sdkRegistration = [ordered]@{ version = 1; status = 'blocked'; reason = 'unreadable'; records = @() }

function Set-MetadataReason([string]$Reason) {
    if ($script:metadataReason -ceq 'none') { $script:metadataReason = $Reason }
}
function Assert-MetadataPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if ($full.Length -gt 1024 -or $full -cnotmatch '^[A-Z]:\\' -or
        $full -match '[;*?\[\]<>"|\x00-\x1f\x7f]' -or $full.Substring(2).Contains(':') -or
        $full -match '(?:[ .]\\|[ .]$)' -or -not [string]::Equals($full, $Path, [StringComparison]::OrdinalIgnoreCase)) { throw 'filesystem' }
    $current = $full
    for ($depth = 0; $depth -lt 64; $depth++) {
        $attributes = [IO.File]::GetAttributes($current)
        if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'filesystem' }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { return $full }
        $current = $parent.FullName
    }
    throw 'bounds'
}
function Get-MetadataDirectories([string]$Path, [int]$Cap) {
    $result = [Collections.Generic.List[string]]::new()
    if (-not [IO.Directory]::Exists($Path)) { return ,$result.ToArray() }
    [void](Assert-MetadataPath $Path)
    foreach ($directory in [IO.Directory]::EnumerateDirectories($Path)) {
        if ($result.Count -ge $Cap) { throw 'bounds' }
        [void](Assert-MetadataPath $directory)
        $result.Add($directory)
    }
    $array = $result.ToArray()
    [Array]::Sort($array, [StringComparer]::OrdinalIgnoreCase)
    return ,$array
}
function Get-MetadataHash([IO.Stream]$Stream) {
    $hash = [Security.Cryptography.SHA256]::Create()
    try {
        $Stream.Position = 0
        return ([BitConverter]::ToString($hash.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    } finally { $hash.Dispose() }
}
function Get-MetadataSignature([string]$Path) {
    # This exact CmdletInfo came from the source-frozen inbox profile binding.
    # No lookup, module reload, function fallback or candidate invocation occurs.
    $signature = & $script:metadataSignatureCommand -LiteralPath $Path -ErrorAction Stop
    if ($signature -isnot [Management.Automation.Signature] -or
        -not [string]::Equals($signature.Path, $Path, [StringComparison]::OrdinalIgnoreCase)) { throw 'filesystem' }
    $condition = Get-OwnedImageSignatureCondition $signature
    $subject = ''; $issuer = ''; $thumbprint = ''; $certificateSha256 = ''
    $certificate = $signature.SignerCertificate
    if ($null -ne $certificate) {
        if ($certificate -isnot [Security.Cryptography.X509Certificates.X509Certificate2]) { throw 'filesystem' }
        $subject = $certificate.Subject; $issuer = $certificate.Issuer
        if ($subject.Length -gt 2048 -or $issuer.Length -gt 2048 -or ($subject + $issuer) -match '[\x00-\x1f\x7f]') { throw 'bounds' }
        $thumbprint = $certificate.Thumbprint.ToLowerInvariant()
        $hash = [Security.Cryptography.SHA256]::Create()
        try { $certificateSha256 = ([BitConverter]::ToString($hash.ComputeHash($certificate.RawData))).Replace('-', '').ToLowerInvariant() }
        finally { $hash.Dispose() }
    }
    return [ordered]@{ path = [string]$signature.Path; status = [string]$signature.Status; type = [string]$signature.SignatureType
        condition = $condition; subject = $subject; issuer = $issuer; thumbprint = $thumbprint; certificateSha256 = $certificateSha256 }
}
function Get-MetadataFile([string]$Path, [string]$Role, [string]$Target, [string]$Installation, [string]$Toolset, [string]$SdkVersion) {
    $full = Assert-MetadataPath $Path
    $item = [IO.FileInfo]::new($full)
    if (-not $item.Exists -or ($item.Attributes -band [IO.FileAttributes]::Directory) -ne 0) { throw 'filesystem' }
    $cap = if ($Role -ceq 'installation-metadata') { 65536L } else { 134217728L }
    # FileShare.Read permits the literal-path signature/version readers while
    # denying new writers/deleters for this held snapshot. The OS is prerequisite.
    $stream = [IO.FileStream]::new($full, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        $size = $stream.Length
        if ($size -le 0 -or $size -gt $cap) { throw 'bounds' }
        $beforeTime = [IO.File]::GetLastWriteTimeUtc($full).Ticks
        $sha256 = Get-MetadataHash $stream
        $version = [Diagnostics.FileVersionInfo]::GetVersionInfo($full).FileVersion
        if ($null -eq $version) { $version = '' }
        if ($version.Length -gt 128 -or $version -match '[\x00-\x1f\x7f]') { throw 'bounds' }
        $signature = Get-MetadataSignature $full
        [void](Assert-MetadataPath $full)
        if ($stream.Length -ne $size -or [IO.File]::GetLastWriteTimeUtc($full).Ticks -ne $beforeTime -or
            (Get-MetadataHash $stream) -cne $sha256) { throw 'changed' }
        return [ordered]@{ role = $Role; target = $Target; installation = $Installation; toolset = $Toolset; sdkVersion = $SdkVersion
            path = $full; bytes = $size; sha256 = $sha256; fileVersion = $version; regular = $true; reparse = $false
            stability = 'observed-equal'; signature = $signature }
    } finally { $stream.Dispose() }
}
function Add-MetadataFile([string]$Path, [string]$Role, [string]$Target, [string]$Installation = '', [string]$Toolset = '', [string]$SdkVersion = '') {
    if ($script:metadataFiles.Count -ge 256) { throw 'bounds' }
    if (-not [IO.File]::Exists($Path)) {
        if ($Role -cin @('sdk-header', 'sdk-library')) { Set-MetadataReason 'missing-sdk' }
        else { Set-MetadataReason 'missing-tools' }
        return
    }
    $file = Get-MetadataFile $Path $Role $Target $Installation $Toolset $SdkVersion
    $script:metadataBytes += $file.bytes
    if ($script:metadataBytes -gt 536870912L) { throw 'bounds' }
    $script:metadataFiles.Add($file)
    if ($Role -cne 'installation-metadata' -and
        ($file.signature.condition -cne 'none' -or $file.signature.type -cnotin @('Authenticode', 'Catalog') -or
         ($Role -cnotin @('sdk-header', 'sdk-library') -and $file.fileVersion -ceq ''))) {
        if ($Role -cin @('sdk-header', 'sdk-library')) { Set-MetadataReason 'sdk-provenance-unproven' }
        else { Set-MetadataReason 'tool-provenance-unproven' }
    }
}
function Test-MetadataReleaseName([object]$Name) {
    return $Name -is [string] -and $Name -cmatch '^(?:18|20[0-9]{2})$'
}
function Find-MetadataTools([string]$Drive) {
    $toolsetsSeen = 0
    foreach ($programFiles in @('Program Files', 'Program Files (x86)')) {
        $root = [IO.Path]::Combine($Drive, $programFiles, 'Microsoft Visual Studio')
        foreach ($year in (Get-MetadataDirectories $root 16)) {
            if (-not (Test-MetadataReleaseName ([IO.Path]::GetFileName($year)))) { continue }
            foreach ($installation in (Get-MetadataDirectories $year 8)) {
                if ([IO.Path]::GetFileName($installation) -cnotin @('BuildTools', 'Community', 'Professional', 'Enterprise')) { continue }
                $toolsetRoot = [IO.Path]::Combine($installation, 'VC', 'Tools', 'MSVC')
                if (-not [IO.Directory]::Exists($toolsetRoot)) { continue }
                if ($script:metadataInstallations.Count -ge 16) { throw 'bounds' }
                $script:metadataInstallations.Add($installation)
                Add-MetadataFile ([IO.Path]::Combine([string[]]@($installation, 'VC', 'Auxiliary', 'Build', 'Microsoft.VCToolsVersion.default.txt'))) 'installation-metadata' 'none' $installation
                foreach ($toolset in (Get-MetadataDirectories $toolsetRoot 8)) {
                    $version = [IO.Path]::GetFileName($toolset)
                    if ($version -cnotmatch '^14\.[0-9]{2}\.[0-9]{5}$') { throw 'missing-tools' }
                    $toolsetsSeen++
                    foreach ($target in @('x64', 'x86')) {
                        $bin = [IO.Path]::Combine($toolset, 'bin', 'Hostx64', $target)
                        foreach ($pair in @(@('cl.exe', 'compiler'), @('link.exe', 'linker'))) {
                            Add-MetadataFile ([IO.Path]::Combine($bin, $pair[0])) $pair[1] $target $installation $version
                        }
                        if ($target -ceq 'x64') { Add-MetadataFile ([IO.Path]::Combine($bin, 'dumpbin.exe')) 'inspector' $target $installation $version }
                        else { Add-MetadataFile ([IO.Path]::Combine($bin, 'lib.exe')) 'library-tool' $target $installation $version }
                        if (-not [IO.Directory]::Exists($bin)) { Set-MetadataReason 'missing-tools'; continue }
                        [void](Assert-MetadataPath $bin)
                        $dlls = [Collections.Generic.List[string]]::new()
                        foreach ($dll in [IO.Directory]::EnumerateFiles($bin, '*.dll')) {
                            if ($dlls.Count -ge 64) { throw 'bounds' }
                            $dlls.Add($dll)
                        }
                        $ordered = $dlls.ToArray(); [Array]::Sort($ordered, [StringComparer]::OrdinalIgnoreCase)
                        foreach ($dll in $ordered) { Add-MetadataFile $dll 'compiler-companion' $target $installation $version }
                        foreach ($required in @('c1.dll', 'c1xx.dll', 'c2.dll')) {
                            if (-not [IO.File]::Exists([IO.Path]::Combine($bin, $required))) { Set-MetadataReason 'missing-tools' }
                        }
                    }
                }
            }
        }
    }
    if ($toolsetsSeen -eq 0) { Set-MetadataReason 'missing-tools' }
    elseif ($toolsetsSeen -ne 1 -or $script:metadataInstallations.Count -ne 1) { Set-MetadataReason 'ambiguous-tools' }
}
function Find-MetadataSdk([string]$Drive) {
    $root = [IO.Path]::Combine($Drive, 'Program Files (x86)', 'Windows Kits', '10')
    foreach ($include in (Get-MetadataDirectories ([IO.Path]::Combine($root, 'Include')) 8)) {
        $version = [IO.Path]::GetFileName($include)
        if ($version -cnotmatch '^10\.0\.[0-9]{4,6}\.[0-9]{1,6}$') { throw 'missing-sdk' }
        $script:metadataSdkVersions.Add($version)
        # Samples are not a guessed complete header/library dependency closure.
        foreach ($sample in @(@('ucrt', 'stdio.h'), @('shared', 'sdkddkver.h'), @('um', 'Windows.h'))) {
            Add-MetadataFile ([IO.Path]::Combine($include, $sample[0], $sample[1])) 'sdk-header' 'none' '' '' $version
        }
        foreach ($target in @('x64', 'x86')) {
            Add-MetadataFile ([IO.Path]::Combine([string[]]@($root, 'Lib', $version, 'ucrt', $target, 'ucrt.lib'))) 'sdk-library' $target '' '' $version
            Add-MetadataFile ([IO.Path]::Combine([string[]]@($root, 'Lib', $version, 'um', $target, 'kernel32.lib'))) 'sdk-library' $target '' '' $version
        }
    }
    if ($script:metadataSdkVersions.Count -eq 0) { Set-MetadataReason 'missing-sdk' }
    elseif ($script:metadataSdkVersions.Count -ne 1) { Set-MetadataReason 'ambiguous-sdk' }
}

function New-SdkRegistryApi {
    # Fixed, memory-only .NET Framework P/Invoke binding. No caller-controlled DLL,
    # method, path, or registry namespace enters this declaration.
    $dll = 'C:\Windows\System32\advapi32.dll'
    $name = [Reflection.AssemblyName]::new('FactorySdkRegistrationPrivate')
    $assembly = [AppDomain]::CurrentDomain.DefineDynamicAssembly($name, [Reflection.Emit.AssemblyBuilderAccess]::Run)
    $module = $assembly.DefineDynamicModule('FactorySdkRegistrationPrivate')
    $type = $module.DefineType('FactorySdkRegistrationPrivate.Native',
        ([Reflection.TypeAttributes]::NotPublic -bor [Reflection.TypeAttributes]::Sealed -bor [Reflection.TypeAttributes]::Abstract))
    $flags = [Reflection.MethodAttributes]::Private -bor [Reflection.MethodAttributes]::Static -bor [Reflection.MethodAttributes]::PinvokeImpl
    $declarations = @(
        @('RegOpenKeyExW', [type[]]@([IntPtr], [string], [uint32], [uint32], [IntPtr].MakeByRefType())),
        @('RegEnumKeyExW', [type[]]@([IntPtr], [uint32], [Text.StringBuilder], [uint32].MakeByRefType(), [IntPtr], [IntPtr], [IntPtr], [IntPtr])),
        @('RegQueryValueExW', [type[]]@([IntPtr], [string], [IntPtr], [uint32].MakeByRefType(), [byte[]], [uint32].MakeByRefType())),
        @('RegCloseKey', [type[]]@([IntPtr]))
    )
    foreach ($declaration in $declarations) {
        $method = $type.DefinePInvokeMethod($declaration[0], $dll, $declaration[0], $flags,
            [Reflection.CallingConventions]::Standard, [int], $declaration[1],
            [Runtime.InteropServices.CallingConvention]::Winapi, [Runtime.InteropServices.CharSet]::Unicode)
        $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor [Reflection.MethodImplAttributes]::PreserveSig)
    }
    $native = $type.CreateType()
    $binding = [Reflection.BindingFlags]::NonPublic -bor [Reflection.BindingFlags]::Static
    $open = $native.GetMethod('RegOpenKeyExW', $binding); $enumerate = $native.GetMethod('RegEnumKeyExW', $binding)
    $query = $native.GetMethod('RegQueryValueExW', $binding); $close = $native.GetMethod('RegCloseKey', $binding)
    if (@($open, $enumerate, $query, $close) -contains $null) { throw 'unsupported-binding' }
    return @{
        Open = { param([IntPtr]$h, [string]$path, [uint32]$option, [uint32]$access)
            $arguments = [object[]]@($h, $path, $option, $access, [IntPtr]::Zero)
            $code = [int]$open.Invoke($null, $arguments)
            return @{ code = $code; handle = [IntPtr]$arguments[4] }
        }.GetNewClosure()
        Enum = { param([IntPtr]$h, [uint32]$index)
            $nameBuffer = [Text.StringBuilder]::new(256)
            $arguments = [object[]]@($h, $index, $nameBuffer, [uint32]256,
                [IntPtr]::Zero, [IntPtr]::Zero, [IntPtr]::Zero, [IntPtr]::Zero)
            $code = [int]$enumerate.Invoke($null, $arguments)
            $length = if ($code -eq 0) { [uint32]$arguments[3] } else { [uint32]0 }
            if ($length -gt 256) { throw 'bounds' }
            return @{ code = $code; name = if ($code -eq 0) { $nameBuffer.ToString(0, [int]$length) } else { '' } }
        }.GetNewClosure()
        Query = { param([IntPtr]$h, [string]$valueName, [int]$capacity)
            $buffer = [byte[]]::new($capacity)
            $arguments = [object[]]@($h, $valueName, [IntPtr]::Zero, [uint32]0, $buffer, [uint32]$capacity)
            $code = [int]$query.Invoke($null, $arguments)
            $length = if ($code -eq 0) { [uint32]$arguments[5] } else { [uint32]0 }
            if ($length -gt $capacity) { throw 'bounds' }
            $data = [byte[]]::new([int]$length)
            if ($length -gt 0) { [Array]::Copy($buffer, $data, [int]$length) }
            return @{ code = $code; type = if ($code -eq 0) { [uint32]$arguments[3] } else { [uint32]0 }; bytes = [int]$length
                data = $data }
        }.GetNewClosure()
        Close = { param([IntPtr]$h)
            return [int]$close.Invoke($null, [object[]]@($h))
        }.GetNewClosure()
    }
}

function Assert-SdkDeadline([scriptblock]$Now, [long]$Start) {
    $elapsed = [long](& $Now) - $Start
    if ($elapsed -lt 0 -or $elapsed -gt 5000) { throw 'bounds' }
}
function Read-SdkRegistryString([hashtable]$Result, [int]$Capacity, [bool]$MissingAllowed) {
    if ($Result.code -eq 2 -and $MissingAllowed) { return $null }
    if ($Result.code -eq 234) { throw 'bounds' } # ERROR_MORE_DATA: buffer is undefined.
    if ($Result.code -ne 0) { throw 'unreadable' }
    if ($Result.type -ne 1 -or $Result.bytes -lt 2 -or $Result.bytes -gt $Capacity -or
        ($Result.bytes % 2) -ne 0 -or $Result.data -isnot [byte[]] -or $Result.data.Length -ne $Result.bytes) { throw 'malformed' }
    try { $value = [Text.UnicodeEncoding]::new($false, $false, $true).GetString($Result.data) }
    catch { throw 'malformed' }
    for ($unit = 0; $unit -lt $value.Length; $unit++) {
        if ([char]::IsHighSurrogate($value[$unit])) {
            if ($unit + 1 -ge $value.Length -or -not [char]::IsLowSurrogate($value[$unit + 1])) { throw 'malformed' }
            $unit++
        } elseif ([char]::IsLowSurrogate($value[$unit])) { throw 'malformed' }
    }
    if ($value.Length -lt 2 -or $value[$value.Length - 1] -ne [char]0 -or
        $value.IndexOf([char]0) -ne $value.Length - 1) { throw 'malformed' }
    $value = $value.Substring(0, $value.Length - 1)
    if ($value -cmatch '[\x00-\x1f\x7f]') { throw 'malformed' }
    return $value
}
function Get-SdkNameHash([string]$Value) {
    if ($null -eq $Value) { return 'missing' }
    $hash = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::Unicode.GetBytes($Value)))).Replace('-', '') }
    finally { $hash.Dispose() }
}
function Invoke-SdkRegistrationObservation([hashtable]$Api, [scriptblock]$Now) {
    $start = [long](& $Now)
    $raw = 0L; $closureFailed = $false
    $passes = [Collections.Generic.List[object]]::new()
    $rootPath = 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    $hklm = [IntPtr]::new(-2147483646)
    try {
        foreach ($pass in 1..2) {
            $markers = [Collections.Generic.List[string]]::new()
            $matchedRecords = [Collections.Generic.Dictionary[string, object]]::new([StringComparer]::Ordinal)
            foreach ($view in @(@{ name = 'x64'; flag = 0x100 }, @{ name = 'x86'; flag = 0x200 })) {
                Assert-SdkDeadline $Now $start
                $rootAccess = [uint32](0x9 -bor $view.flag) # KEY_QUERY_VALUE | KEY_ENUMERATE_SUB_KEYS | explicit view
                $opened = & $Api.Open $hklm $rootPath ([uint32]8) $rootAccess # REG_OPTION_OPEN_LINK
                if ($opened.code -ne 0 -or $opened.handle -eq [IntPtr]::Zero) {
                    Assert-SdkDeadline $Now $start
                    throw 'unreadable'
                }
                $rootHandle = [IntPtr]$opened.handle
                try {
                    Assert-SdkDeadline $Now $start
                    $rootLink = & $Api.Query $rootHandle 'SymbolicLinkValue' 2
                    Assert-SdkDeadline $Now $start
                    if ($rootLink.code -eq 0 -or $rootLink.code -eq 234) { throw 'link' }
                    if ($rootLink.code -ne 2) { throw 'unreadable' }
                    $names = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
                    for ($index = 0; $index -le 512; $index++) {
                        Assert-SdkDeadline $Now $start
                        $entry = & $Api.Enum $rootHandle ([uint32]$index)
                        Assert-SdkDeadline $Now $start
                        if ($index -eq 512) {
                            if ($entry.code -ne 259) { throw 'bounds' } # sentinel requires ERROR_NO_MORE_ITEMS
                            break
                        }
                        if ($entry.code -eq 259) { break }
                        if ($entry.code -eq 234) { throw 'bounds' }
                        if ($entry.code -ne 0) { throw 'unreadable' }
                        $keyName = $entry.name
                        if ($keyName -isnot [string] -or $keyName.Length -lt 1 -or $keyName.Length -ge 256 -or
                            $keyName -match '[\\/\x00-\x1f\x7f]' -or -not $names.Add($keyName)) { throw 'malformed' }
                        try { $nameBytes = [Text.UnicodeEncoding]::new($false, $false, $true).GetBytes($keyName) }
                        catch { throw 'malformed' }
                        $raw += $nameBytes.Length + 2 # includes the fixed Unicode terminator in the native buffer
                        if ($raw -gt 262144) { throw 'bounds' }
                        $childAccess = [uint32](0x1 -bor $view.flag) # KEY_QUERY_VALUE | same explicit view
                        Assert-SdkDeadline $Now $start
                        $child = & $Api.Open $rootHandle $keyName ([uint32]8) $childAccess
                        if ($child.code -ne 0 -or $child.handle -eq [IntPtr]::Zero) {
                            Assert-SdkDeadline $Now $start
                            throw 'unreadable'
                        }
                        $childHandle = [IntPtr]$child.handle
                        try {
                            Assert-SdkDeadline $Now $start
                            $link = & $Api.Query $childHandle 'SymbolicLinkValue' 2
                            Assert-SdkDeadline $Now $start
                            if ($link.code -eq 0 -or $link.code -eq 234) { throw 'link' }
                            if ($link.code -ne 2) { throw 'unreadable' }
                            $nameResult = & $Api.Query $childHandle 'DisplayName' 1024
                            Assert-SdkDeadline $Now $start
                            $displayName = Read-SdkRegistryString $nameResult 1024 $true
                            if ($null -ne $displayName) { $raw += $nameResult.bytes }
                            if ($raw -gt 262144) { throw 'bounds' }
                            $matched = $false; $record = $null
                            if ($null -ne $displayName -and $displayName -cmatch '\AWindows Software Development Kit - Windows 10\.0\.26100\.[0-9]{1,6}\z') {
                                $matched = $true
                                $versionResult = & $Api.Query $childHandle 'DisplayVersion' 256
                                Assert-SdkDeadline $Now $start
                                $displayVersion = Read-SdkRegistryString $versionResult 256 $false
                                $raw += $versionResult.bytes
                                $publisherResult = & $Api.Query $childHandle 'Publisher' 512
                                Assert-SdkDeadline $Now $start
                                $publisher = Read-SdkRegistryString $publisherResult 512 $false
                                $raw += $publisherResult.bytes
                                if ($raw -gt 262144) { throw 'bounds' }
                                $productCode = $null
                                if ($keyName -match '^\{[0-9A-Fa-f]{8}-(?:[0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12}\}$') { $productCode = $keyName.ToUpperInvariant() }
                                $record = [ordered]@{ view = $view.name; productCode = $productCode
                                    displayName = $displayName; displayVersion = $displayVersion; publisher = $publisher }
                                if ($matchedRecords.Count -ge 8) { throw 'bounds' }
                                $matchedRecords.Add(($view.name + '/' + $keyName), $record)
                            }
                            $markers.Add((ConvertTo-Json -InputObject ([ordered]@{ view = $view.name; key = $keyName
                                displayNameSha256 = Get-SdkNameHash $displayName; matched = $matched; record = $record }) -Depth 5 -Compress))
                        } finally {
                            try { if ((& $Api.Close $childHandle) -ne 0) { $closureFailed = $true } }
                            catch { $closureFailed = $true }
                            Assert-SdkDeadline $Now $start
                        }
                        if ($closureFailed) { throw 'closure' }
                    }
                } finally {
                    try { if ((& $Api.Close $rootHandle) -ne 0) { $closureFailed = $true } }
                    catch { $closureFailed = $true }
                    Assert-SdkDeadline $Now $start
                }
                if ($closureFailed) { throw 'closure' }
            }
            $orderedMarkers = $markers.ToArray(); [Array]::Sort($orderedMarkers, [StringComparer]::Ordinal)
            $orderedMatchKeys = [string[]]@($matchedRecords.Keys); [Array]::Sort($orderedMatchKeys, [StringComparer]::Ordinal)
            $orderedMatches = [Collections.Generic.List[object]]::new()
            foreach ($key in $orderedMatchKeys) { $orderedMatches.Add($matchedRecords[$key]) }
            $passes.Add(@{ markers = $orderedMarkers; records = $orderedMatches.ToArray() })
        }
        if ($closureFailed) { throw 'closure' }
        if ((ConvertTo-Json -InputObject $passes[0].markers -Compress) -cne
            (ConvertTo-Json -InputObject $passes[1].markers -Compress)) { throw 'changed' }
        $records = $passes[0].records
        $status = if ($records.Length -eq 0) { 'absent' } elseif ($records.Length -eq 1) { 'single-candidate' } else { 'ambiguous' }
        $section = [ordered]@{ version = 1; status = $status; reason = 'none'; records = $records }
        if ([Text.Encoding]::UTF8.GetByteCount((ConvertTo-Json -InputObject $section -Depth 5 -Compress)) -gt 32768) { throw 'bounds' }
        return @{ section = $section; rawBytes = $raw }
    } catch {
        $reason = [string]$_.Exception.Message
        if ($closureFailed) { $reason = 'closure' }
        elseif ($reason -cnotin @('bounds', 'unreadable', 'malformed', 'changed', 'link', 'closure')) { $reason = 'unreadable' }
        return @{ section = [ordered]@{ version = 1; status = 'blocked'; reason = $reason; records = @() }; rawBytes = $raw }
    }
}

$profileReady = $false
try {
    if ($Mode -cne 'metadata-only' -or $args.Count -ne 0) { throw 'arguments' }
    if ($env:OS -cne 'Windows_NT' -or -not [Environment]::Is64BitProcess -or
        $PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) { throw 'host' }
    $expectedHost = [IO.Path]::Combine($env:SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0')
    if (-not [string]::Equals($PSHOME, $expectedHost, [StringComparison]::OrdinalIgnoreCase) -or
        $env:FACTORY_WINDOWS_LOADER_METADATA_SELECTION_SHA256 -cnotmatch '^[0-9a-f]{64}$' -or
        [Environment]::OSVersion.Version.ToString() -cne $env:FACTORY_WINDOWS_LOADER_METADATA_WINDOWS_VERSION) { throw 'host' }
    foreach ($source in @($PSHOME, $PSScriptRoot, [IO.Path]::Combine($PSHOME, 'powershell.exe'),
        [IO.Path]::Combine($PSScriptRoot, 'windows-owned-image-host-profile.ps1'),
        [IO.Path]::Combine($PSScriptRoot, 'windows-owned-image-diagnostics.ps1'))) { [void](Assert-MetadataPath $source) }
    $env:PSModulePath = [IO.Path]::Combine($PSHOME, 'Modules')
    $script:PSModuleAutoLoadingPreference = 'None'
    . ([IO.Path]::Combine($PSScriptRoot, 'windows-owned-image-host-profile.ps1'))
    . ([IO.Path]::Combine($PSScriptRoot, 'windows-owned-image-diagnostics.ps1'))
    $binding = $null
    $profile = Initialize-OwnedImageInboxProfile $PSHOME $env:FACTORY_OWNED_IMAGE_INBOX $env:FACTORY_OWNED_IMAGE_PROFILE ([ref]$binding)
    if ($profile.origin -cne 'inbox' -or $profile.availability -cne 'available' -or $profile.stage -cne 'ready') { throw 'host-profile' }
    $script:metadataSignatureCommand = Get-OwnedImageBoundSignatureCommand $binding
    if ($script:metadataSignatureCommand -isnot [Management.Automation.CmdletInfo]) { throw 'host-profile' }
    $profileReady = $true
    $drive = [IO.Path]::GetPathRoot($env:SystemRoot)
    Find-MetadataTools $drive
    Find-MetadataSdk $drive
    foreach ($file in $script:metadataFiles) {
        $after = Get-MetadataFile $file.path $file.role $file.target $file.installation $file.toolset $file.sdkVersion
        if (($file | ConvertTo-Json -Depth 8 -Compress) -cne ($after | ConvertTo-Json -Depth 8 -Compress)) { throw 'changed' }
    }
    try {
        $api = New-SdkRegistryApi
        $clock = { [long]([Diagnostics.Stopwatch]::GetTimestamp() * 1000 / [Diagnostics.Stopwatch]::Frequency) }
        $observation = Invoke-SdkRegistrationObservation $api $clock
        $script:sdkRegistration = $observation.section
        $script:metadataBytes += $observation.rawBytes
        if ($script:metadataBytes -gt 536870912L) {
            $script:sdkRegistration = [ordered]@{ version = 1; status = 'blocked'; reason = 'bounds'; records = @() }
            throw 'bounds'
        }
        if ($script:sdkRegistration.status -cne 'single-candidate') {
            Set-MetadataReason ('sdk-registration-' + $(if ($script:sdkRegistration.status -ceq 'blocked') { 'blocked' } else { $script:sdkRegistration.status }))
        }
    } catch {
        if ([string]$_.Exception.Message -ceq 'bounds') { throw }
        $script:sdkRegistration = [ordered]@{ version = 1; status = 'blocked'; reason = 'unsupported-binding'; records = @() }
        Set-MetadataReason 'sdk-registration-blocked'
    }
} catch {
    $reason = [string]$_.Exception.Message
    if ($reason -cnotin @('arguments', 'host', 'host-profile', 'bounds', 'missing-tools', 'ambiguous-tools', 'missing-sdk',
        'ambiguous-sdk', 'tool-provenance-unproven', 'sdk-provenance-unproven', 'changed', 'filesystem',
        'sdk-registration-absent', 'sdk-registration-ambiguous', 'sdk-registration-blocked')) { $reason = 'filesystem' }
    # Bounds/change failures dominate incomplete discovery observations.
    $script:metadataReason = $reason
}

$encoding = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $encoding
if (-not $profileReady) {
    # No rejected host/profile can trigger a module-dependent serializer lookup.
    [Console]::Out.Write('{"scope":"windows-storage-loader-metadata","state":"blocked","reason":"' + $script:metadataReason +
        '","selectionAuthority":false,"buildAuthority":false,"nativeAuthority":false}' + "`n")
    exit 1
} else {
    $state = if ($script:metadataReason -ceq 'none') { 'observed' } else { 'blocked' }
    $out = [ordered]@{ scope = 'windows-storage-loader-metadata'; schema = 2; state = $state; reason = $script:metadataReason
        selectionAuthority = $false; buildAuthority = $false; nativeAuthority = $false
        sourceSelectionSha256 = $env:FACTORY_WINDOWS_LOADER_METADATA_SELECTION_SHA256
        host = [ordered]@{ powershellVersion = $PSVersionTable.PSVersion.ToString(); windowsVersion = [Environment]::OSVersion.Version.ToString()
            architecture = 'x64'; profile = 'winps-inbox-only'; securityCommand = 'captured-inbox-Get-AuthenticodeSignature' }
        installations = $script:metadataInstallations.ToArray(); sdkVersions = $script:metadataSdkVersions.ToArray()
        files = $script:metadataFiles.ToArray(); sdkCoverage = 'prerequisite-samples-not-consumed-closure'
        sdkRegistration = $script:sdkRegistration }
}
$wire = ConvertTo-Json -InputObject $out -Depth 10 -Compress
if ($encoding.GetByteCount($wire) + 1 -gt 1048576) {
    $wire = '{"scope":"windows-storage-loader-metadata","state":"blocked","reason":"bounds","selectionAuthority":false,"buildAuthority":false,"nativeAuthority":false}'
    $script:metadataReason = 'bounds'
}
[Console]::Out.Write($wire + "`n")
if ($script:metadataReason -ceq 'none') { exit 0 } else { exit 1 }
