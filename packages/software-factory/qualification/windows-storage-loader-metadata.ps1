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
function Find-MetadataTools([string]$Drive) {
    $toolsetsSeen = 0
    foreach ($programFiles in @('Program Files', 'Program Files (x86)')) {
        $root = [IO.Path]::Combine($Drive, $programFiles, 'Microsoft Visual Studio')
        foreach ($year in (Get-MetadataDirectories $root 16)) {
            if ([IO.Path]::GetFileName($year) -cnotmatch '^20[0-9]{2}$') { continue }
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
} catch {
    $reason = [string]$_.Exception.Message
    if ($reason -cnotin @('arguments', 'host', 'host-profile', 'bounds', 'missing-tools', 'ambiguous-tools', 'missing-sdk',
        'ambiguous-sdk', 'tool-provenance-unproven', 'sdk-provenance-unproven', 'changed', 'filesystem')) { $reason = 'filesystem' }
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
    $out = [ordered]@{ scope = 'windows-storage-loader-metadata'; schema = 1; state = $state; reason = $script:metadataReason
        selectionAuthority = $false; buildAuthority = $false; nativeAuthority = $false
        sourceSelectionSha256 = $env:FACTORY_WINDOWS_LOADER_METADATA_SELECTION_SHA256
        host = [ordered]@{ powershellVersion = $PSVersionTable.PSVersion.ToString(); windowsVersion = [Environment]::OSVersion.Version.ToString()
            architecture = 'x64'; profile = 'winps-inbox-only'; securityCommand = 'captured-inbox-Get-AuthenticodeSignature' }
        installations = $script:metadataInstallations.ToArray(); sdkVersions = $script:metadataSdkVersions.ToArray()
        files = $script:metadataFiles.ToArray(); sdkCoverage = 'prerequisite-samples-not-consumed-closure' }
}
$wire = ConvertTo-Json -InputObject $out -Depth 10 -Compress
if ($encoding.GetByteCount($wire) + 1 -gt 1048576) {
    $wire = '{"scope":"windows-storage-loader-metadata","state":"blocked","reason":"bounds","selectionAuthority":false,"buildAuthority":false,"nativeAuthority":false}'
    $script:metadataReason = 'bounds'
}
[Console]::Out.Write($wire + "`n")
if ($script:metadataReason -ceq 'none') { exit 0 } else { exit 1 }
