# Explicit candidate, private metadata checks and fixed facts only.
$script:ownedImageSignatureBinding = $null
function Test-OwnedImageSecurityOrigin {
    param([string]$HostHome, [object]$Snapshot, [object]$Authority, [Collections.IDictionary]$Facts = $null)
    if ($null -eq $Facts) { $Facts = @{} }
    try {
        $Facts.field = 'authority'
        if ($null -eq $Authority -or $Authority.GetType() -ne [Collections.ObjectModel.ReadOnlyDictionary[string,object]] -or
            -not (Test-OwnedImageInboxModuleOrigin $HostHome 'Microsoft.PowerShell.Security' $Authority)) { return $false }
        $Facts.field = 'capture'
        if ($Snapshot -isnot [Collections.IDictionary] -or $Snapshot.Count -ne 3 -or
            @($Snapshot.Keys | Where-Object { $_ -cnotin @('Name', 'CommandType', 'Module') }).Count -ne 0 -or
            $Snapshot.Module -isnot [Collections.IDictionary] -or $Snapshot.Module.Count -ne 4 -or
            @($Snapshot.Module.Keys | Where-Object { $_ -cnotin @('Name', 'ModuleType', 'Path', 'ModuleBase') }).Count -ne 0) { return $false }
        $Facts.field = 'cmdlet-name'
        if ($Snapshot.Name -isnot [string] -or $Snapshot.Name -cne 'Get-AuthenticodeSignature') { return $false }
        $Facts.field = 'cmdlet-type'
        if ($Snapshot.CommandType -isnot [Management.Automation.CommandTypes] -or $Snapshot.CommandType -ne [Management.Automation.CommandTypes]::Cmdlet) { return $false }
        $Facts.field = 'module-name'
        if ($Snapshot.Module.Name -isnot [string] -or $Snapshot.Module.Name -cne $Authority['Name']) { return $false }
        $Facts.field = 'module-kind'
        if ($Snapshot.Module.ModuleType -isnot [Management.Automation.ModuleType] -or $Snapshot.Module.ModuleType -ne $Authority['ModuleType']) { return $false }
        $Facts.field = 'manifest'
        if ($Snapshot.Module.Path -isnot [string] -or -not [string]::Equals($Snapshot.Module.Path, $Authority['Path'], [StringComparison]::OrdinalIgnoreCase)) { return $false }
        $Facts.field = 'base'
        return $Snapshot.Module.ModuleBase -is [string] -and
            [string]::Equals($Snapshot.Module.ModuleBase, $Authority['ModuleBase'], [StringComparison]::OrdinalIgnoreCase)
    } catch { return $false }
}

function Get-OwnedImageModuleSnapshot {
    param([object]$Module)
    try {
        # Copy each relevant property once. Only typed immutable values can pass.
        return @{ Name = $Module.Name; ModuleType = $Module.ModuleType; Path = $Module.Path; ModuleBase = $Module.ModuleBase }
    } catch { return $null }
}

function Get-OwnedImageCommandSnapshot {
    param([object]$Command)
    try {
        $name = $Command.Name
        $type = $Command.CommandType
        $module = $Command.Module
        $snapshot = Get-OwnedImageModuleSnapshot $module
        if ($null -eq $snapshot) { return $null }
        return @{ Name = $name; CommandType = $type; Module = $snapshot }
    } catch { return $null }
}

function New-OwnedImageSecurityAuthority {
    param([string]$HostHome, [object]$Snapshot)
    try {
        if (-not (Test-OwnedImageInboxModuleOrigin $HostHome 'Microsoft.PowerShell.Security' $Snapshot)) { return $null }
        # The backing dictionary never escapes; admitted values are immutable.
        $values = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
        foreach ($key in @('Name', 'ModuleType', 'Path', 'ModuleBase')) { $values.Add($key, $Snapshot[$key]) }
        return [Collections.ObjectModel.ReadOnlyDictionary[string,object]]::new($values)
    } catch { return $null }
}

function New-OwnedImageSignatureBinding {
    param([string]$HostHome, [object]$Command, [object]$Authority, [Collections.IDictionary]$Facts = $null)
    $script:ownedImageSignatureBinding = $null
    if ($null -eq $Facts) { $Facts = @{} }
    try {
        $Facts.field = 'capture'
        $snapshot = Get-OwnedImageCommandSnapshot $Command
        if (-not (Test-OwnedImageSecurityOrigin $HostHome $snapshot $Authority $Facts)) { return $null }
        $moduleValues = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
        foreach ($key in @('Name', 'ModuleType', 'Path', 'ModuleBase')) { $moduleValues.Add($key, $snapshot.Module[$key]) }
        $snapshotValues = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
        $snapshotValues.Add('Name', $snapshot.Name)
        $snapshotValues.Add('CommandType', $snapshot.CommandType)
        $snapshotValues.Add('Module', [Collections.ObjectModel.ReadOnlyDictionary[string,object]]::new($moduleValues))
        $values = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
        $values.Add('HostHome', [IO.Path]::GetFullPath($HostHome))
        $values.Add('Command', $Command)
        $values.Add('Snapshot', [Collections.ObjectModel.ReadOnlyDictionary[string,object]]::new($snapshotValues))
        $values.Add('Authority', $Authority)
        $script:ownedImageSignatureBinding = [Collections.ObjectModel.ReadOnlyDictionary[string,object]]::new($values)
        return $script:ownedImageSignatureBinding
    } catch { return $null }
}

function Get-OwnedImageBoundSignatureCommand {
    param([object]$Binding)
    try {
        if ($null -eq $Binding -or -not [object]::ReferenceEquals($Binding, $script:ownedImageSignatureBinding) -or
            $Binding.GetType() -ne [Collections.ObjectModel.ReadOnlyDictionary[string,object]] -or $Binding.Count -ne 4 -or
            @($Binding.Keys | Where-Object { $_ -cnotin @('HostHome', 'Command', 'Snapshot', 'Authority') }).Count -ne 0 -or
            $Binding['HostHome'] -isnot [string] -or $Binding['Command'] -isnot [Management.Automation.CmdletInfo] -or
            $Binding['Snapshot'].GetType() -ne [Collections.ObjectModel.ReadOnlyDictionary[string,object]] -or
            $Binding['Snapshot']['Module'].GetType() -ne [Collections.ObjectModel.ReadOnlyDictionary[string,object]] -or
            -not (Test-OwnedImageSecurityOrigin $Binding['HostHome'] $Binding['Snapshot'] $Binding['Authority'])) { return $null }
        return $Binding['Command']
    } catch { return $null }
}

function Test-OwnedImageInboxModuleOrigin {
    param([string]$HostHome, [string]$Name, [object]$Snapshot, [Collections.IDictionary]$Facts = $null)
    if ($null -eq $Facts) { $Facts = @{} }
    $Facts.field = 'capture'
    try {
        if ($Snapshot -isnot [Collections.IDictionary] -or $Snapshot.Count -ne 4 -or
            @($Snapshot.Keys | Where-Object { $_ -cnotin @('Name', 'ModuleType', 'Path', 'ModuleBase') }).Count -ne 0) { return $false }
        $hostDirectory = [IO.Path]::GetFullPath($HostHome)
        $Facts.field = 'name'
        if ($Name -cnotin @('Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Security') -or
            $Snapshot.Name -isnot [string] -or $Snapshot.Name -cne $Name) { return $false }
        $directory = [IO.Path]::Combine($hostDirectory, 'Modules', $Name)
        $manifest = [IO.Path]::Combine($directory, $Name + '.psd1')
        $Facts.field = 'kind'
        if ($Snapshot.ModuleType -isnot [Management.Automation.ModuleType] -or $Snapshot.ModuleType -ne [Management.Automation.ModuleType]::Manifest) { return $false }
        $Facts.field = 'manifest'
        if ($Snapshot.Path -isnot [string] -or -not [string]::Equals($Snapshot.Path, $manifest, [StringComparison]::OrdinalIgnoreCase)) { return $false }
        $Facts.field = 'base'
        return $Snapshot.ModuleBase -is [string] -and
            ([string]::Equals($Snapshot.ModuleBase, $directory, [StringComparison]::OrdinalIgnoreCase) -or
             [string]::Equals($Snapshot.ModuleBase, $hostDirectory, [StringComparison]::OrdinalIgnoreCase))
    } catch { return $false }
}

function Get-OwnedImageManagementRelation {
    param([string]$HostHome, [object]$Module)
    $relation = @{ kind = 'unknown'; base = 'other'; path = 'other'; baseType = 'other' }
    try {
        $hostDirectory = [IO.Path]::GetFullPath($HostHome)
        $inbox = [IO.Path]::Combine($hostDirectory, 'Modules')
        $manifestDirectory = [IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Management')
        $manifest = [IO.Path]::Combine($manifestDirectory, 'Microsoft.PowerShell.Management.psd1')
        $binary = [IO.Path]::Combine($hostDirectory, 'Microsoft.PowerShell.Commands.Management.dll')
    } catch { return $relation }
    # Independent observations never change the predicate or emit raw metadata.
    try {
        $kind = $Module.ModuleType
        if ($kind -is [string] -or $kind -is [Management.Automation.ModuleType]) {
            if ($kind -eq 'Manifest') { $relation.kind = 'manifest' }
            elseif ($kind -eq 'Binary') { $relation.kind = 'binary' }
            elseif ($kind -eq 'Script') { $relation.kind = 'script' }
        }
    } catch { }
    try {
        $baseValue = $Module.ModuleBase
        if ($null -eq $baseValue) { $relation.baseType = 'null' }
        elseif ($baseValue -is [string]) {
            $relation.baseType = 'string'
            $base = [IO.Path]::GetFullPath($baseValue)
            if ([string]::Equals($base, $manifestDirectory, [StringComparison]::OrdinalIgnoreCase)) { $relation.base = 'selected-manifest-directory' }
            elseif ([string]::Equals($base, $hostDirectory, [StringComparison]::OrdinalIgnoreCase)) { $relation.base = 'selected-WinPS-host-directory' }
            elseif ([string]::Equals($base, $inbox, [StringComparison]::OrdinalIgnoreCase)) { $relation.base = 'inbox-root' }
        } elseif ($baseValue -is [Array] -and $baseValue.Rank -eq 1 -and $baseValue.Length -eq 1 -and $baseValue[0] -is [string]) {
            $relation.baseType = 'single-string-array'
        }
    } catch { }
    try {
        $pathValue = $Module.Path
        if ($pathValue -is [string]) {
            $path = [IO.Path]::GetFullPath($pathValue)
            if ([string]::Equals($path, $manifest, [StringComparison]::OrdinalIgnoreCase)) { $relation.path = 'exact-selected-manifest' }
            elseif ([string]::Equals($path, $binary, [StringComparison]::OrdinalIgnoreCase)) { $relation.path = 'known-fixed-Management-binary-under-selected-host' }
        }
    } catch { }
    return $relation
}

function Initialize-OwnedImageInboxProfile {
    param([string]$HostHome, [string]$ExpectedInbox, [string]$Profile, [object]$SignatureBinding = $null)
    $script:ownedImageSignatureBinding = $null
    $facts = @{ profile = 'winps-inbox-only'; origin = 'unverified'; availability = 'unavailable'; stage = 'environment'; field = 'path' }
    try {
        if ($null -ne $SignatureBinding) {
            $facts.field = 'profile'
            if ($SignatureBinding -isnot [Management.Automation.PSReference]) { $facts.origin = 'refused'; return $facts }
            $SignatureBinding.Value = $null
        }
        $facts.field = 'path'
        $inbox = [IO.Path]::GetFullPath([IO.Path]::Combine($HostHome, 'Modules'))
        if ($inbox -match '[;*?\[\]\x00-\x1f\x7f]') { $facts.origin = 'refused'; return $facts }
        $facts.field = 'profile'
        if ($Profile -cne 'winps-inbox-only') { $facts.origin = 'refused'; return $facts }
        $facts.field = 'inbox'
        if (-not [string]::Equals([IO.Path]::GetFullPath($ExpectedInbox), $inbox, [StringComparison]::OrdinalIgnoreCase)) { $facts.origin = 'refused'; return $facts }
        # Startup can augment the inherited variable. Narrow it again before imports.
        $facts.field = 'assignment'
        $env:PSModulePath = $inbox
        $script:PSModuleAutoLoadingPreference = 'None'
        $facts.field = 'reparse'
        if (([IO.File]::GetAttributes($inbox) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $facts.origin = 'refused'; return $facts }
        $securityAuthority = $null
        foreach ($name in @('Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Security')) {
            $role = @{ 'Microsoft.PowerShell.Management' = 'management'; 'Microsoft.PowerShell.Utility' = 'utility'; 'Microsoft.PowerShell.Security' = 'security' }[$name]
            $facts.stage = $role + '-import'; $facts.field = 'manifest'
            $directory = [IO.Path]::Combine($inbox, $name)
            $manifest = [IO.Path]::Combine($directory, $name + '.psd1')
            if (-not [IO.File]::Exists($manifest)) { $facts.origin = 'refused'; return $facts }
            $facts.field = 'reparse'
            if (([IO.File]::GetAttributes($directory) -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
                ([IO.File]::GetAttributes($manifest) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $facts.origin = 'refused'; return $facts }
            # Global means only this disposable child session, never a saved profile.
            $facts.field = 'import'
            $loaded = @(Import-Module -Name $manifest -Scope Global -PassThru -ErrorAction Stop)
            $facts.stage = $role + '-origin'; $facts.field = 'count'
            if ($loaded.Count -ne 1) { $facts.origin = 'refused'; return $facts }
            $facts.field = 'capture'
            $snapshot = Get-OwnedImageModuleSnapshot $loaded[0]
            if (-not (Test-OwnedImageInboxModuleOrigin $HostHome $name $snapshot $facts)) {
                $facts.origin = 'refused'
                if ($role -ceq 'management' -and $facts.field -ceq 'base') { $facts.relation = Get-OwnedImageManagementRelation $HostHome $snapshot }
                return $facts
            }
            if ($role -ceq 'security') {
                $facts.field = 'authority'
                $securityAuthority = New-OwnedImageSecurityAuthority $HostHome $snapshot
                if ($null -eq $securityAuthority) { $facts.origin = 'refused'; return $facts }
            }
        }
        $facts.stage = 'cmdlet-resolution'; $facts.field = 'resolution'
        $commands = @(Get-Command -Name 'Get-AuthenticodeSignature' -CommandType Cmdlet -ListImported -All -ErrorAction Stop)
        $facts.field = 'count'
        if ($commands.Count -ne 1) { $facts.origin = 'refused'; return $facts }
        $facts.availability = 'available'
        $facts.stage = 'cmdlet-origin'; $facts.field = 'capture'
        $binding = New-OwnedImageSignatureBinding $HostHome $commands[0] $securityAuthority $facts
        if ($null -eq $binding) { $facts.origin = 'refused'; return $facts }
        if ($null -ne $SignatureBinding) { $SignatureBinding.Value = $binding }
        $facts.origin = 'inbox'
        $facts.stage = 'ready'; $facts.field = 'none'
        return $facts
    } catch { return $facts }
}

function Format-OwnedImageHostProfile {
    param([object]$Facts)
    $fallback = "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`tunverified`tunavailable`tunknown`tunknown"
    $checks = @{ environment = @('path', 'profile', 'inbox', 'assignment', 'reparse')
        'management-import' = @('manifest', 'reparse', 'import'); 'utility-import' = @('manifest', 'reparse', 'import'); 'security-import' = @('manifest', 'reparse', 'import')
        'management-origin' = @('count', 'capture', 'name', 'kind', 'manifest', 'base'); 'utility-origin' = @('count', 'capture', 'name', 'kind', 'manifest', 'base'); 'security-origin' = @('count', 'capture', 'name', 'kind', 'manifest', 'base', 'authority')
        'cmdlet-resolution' = @('resolution', 'count'); 'cmdlet-origin' = @('path', 'capture', 'authority', 'cmdlet-name', 'cmdlet-type', 'module-name', 'module-kind', 'manifest', 'base')
        ready = @('none'); unknown = @('unknown') }
    if ($Facts -isnot [Collections.IDictionary]) { return $fallback }
    $hasRelation = $Facts.Contains('relation')
    $expectedCount = if ($hasRelation) { 6 } else { 5 }
    if ($Facts.Count -ne $expectedCount -or
        @($Facts.Keys | Where-Object { $_ -cnotin @('profile', 'origin', 'availability', 'stage', 'field', 'relation') }).Count -ne 0 -or
        $Facts.profile -cne 'winps-inbox-only' -or $Facts.origin -cnotin @('inbox', 'refused', 'unverified') -or
        $Facts.availability -cnotin @('available', 'unavailable') -or $Facts.stage -isnot [string] -or $Facts.field -isnot [string] -or
        @($checks.Keys) -cnotcontains $Facts.stage -or
        $checks[$Facts.stage] -cnotcontains $Facts.field) { return $fallback }
    if ($hasRelation) {
        $relation = $Facts.relation
        if ($Facts.origin -cne 'refused' -or $Facts.availability -cne 'unavailable' -or $Facts.stage -cne 'management-origin' -or $Facts.field -cne 'base' -or
            $relation -isnot [Collections.IDictionary] -or $relation.Count -ne 4 -or
            @($relation.Keys | Where-Object { $_ -cnotin @('kind', 'base', 'path', 'baseType') }).Count -ne 0 -or
            $relation.kind -isnot [string] -or $relation.base -isnot [string] -or $relation.path -isnot [string] -or $relation.baseType -isnot [string] -or
            $relation.kind -cnotin @('manifest', 'binary', 'script', 'unknown') -or
            $relation.base -cnotin @('selected-manifest-directory', 'selected-WinPS-host-directory', 'inbox-root', 'other') -or
            $relation.path -cnotin @('exact-selected-manifest', 'known-fixed-Management-binary-under-selected-host', 'other') -or
            $relation.baseType -cnotin @('string', 'null', 'single-string-array', 'other') -or
            ($relation.baseType -cne 'string' -and $relation.base -cne 'other')) { return $fallback }
    }
    if ($Facts.stage -ceq 'ready') {
        if ($Facts.origin -cne 'inbox' -or $Facts.availability -cne 'available') { return $fallback }
    } elseif ($Facts.stage -ceq 'unknown') {
        if ($Facts.origin -cne 'unverified' -or $Facts.availability -cne 'unavailable') { return $fallback }
    } elseif ($Facts.stage -ceq 'cmdlet-origin') {
        if ($Facts.origin -cne 'refused' -or $Facts.availability -cne 'available') { return $fallback }
    } elseif ($Facts.availability -cne 'unavailable' -or $Facts.origin -ceq 'inbox' -or
        ($Facts.origin -ceq 'refused' -and $Facts.field -cin @('assignment', 'import', 'resolution'))) { return $fallback }
    $wire = "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`t$($Facts.origin)`t$($Facts.availability)`t$($Facts.stage)`t$($Facts.field)"
    if ($hasRelation) { $wire += [Environment]::NewLine + "OWNED_IMAGE_RELATION`t1`t$($relation.kind)`t$($relation.base)`t$($relation.path)`t$($relation.baseType)" }
    return $wire
}
