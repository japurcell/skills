# Explicit candidate, private metadata checks and fixed facts only.
function Test-OwnedImageSecurityOrigin {
    param([string]$Inbox, [object]$Command, [Collections.IDictionary]$Facts = $null)
    if ($null -eq $Facts) { $Facts = @{} }
    try {
        $Facts.field = 'path'
        $manifest = [IO.Path]::GetFullPath([IO.Path]::Combine($Inbox, 'Microsoft.PowerShell.Security', 'Microsoft.PowerShell.Security.psd1'))
        $base = [IO.Path]::GetDirectoryName($manifest)
        $Facts.field = 'cmdlet-name'
        if ($Command.Name -cne 'Get-AuthenticodeSignature') { return $false }
        $Facts.field = 'cmdlet-type'
        if ($Command.CommandType -ne 'Cmdlet') { return $false }
        $Facts.field = 'module-name'
        if ($Command.Module.Name -cne 'Microsoft.PowerShell.Security') { return $false }
        $Facts.field = 'manifest'
        if (-not [string]::Equals([IO.Path]::GetFullPath($Command.Module.Path), $manifest, [StringComparison]::OrdinalIgnoreCase)) { return $false }
        $Facts.field = 'base'
        return [string]::Equals([IO.Path]::GetFullPath($Command.Module.ModuleBase), $base, [StringComparison]::OrdinalIgnoreCase)
    } catch { return $false }
}

function Initialize-OwnedImageInboxProfile {
    param([string]$HostHome, [string]$ExpectedInbox, [string]$Profile)
    $facts = @{ profile = 'winps-inbox-only'; origin = 'unverified'; availability = 'unavailable'; stage = 'environment'; field = 'path' }
    try {
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
            $facts.field = 'name'
            if ($loaded[0].Name -cne $name) { $facts.origin = 'refused'; return $facts }
            $facts.field = 'manifest'
            if (-not [string]::Equals([IO.Path]::GetFullPath($loaded[0].Path), $manifest, [StringComparison]::OrdinalIgnoreCase)) { $facts.origin = 'refused'; return $facts }
            $facts.field = 'base'
            if (-not [string]::Equals([IO.Path]::GetFullPath($loaded[0].ModuleBase), $directory, [StringComparison]::OrdinalIgnoreCase)) { $facts.origin = 'refused'; return $facts }
        }
        $facts.stage = 'cmdlet-resolution'; $facts.field = 'resolution'
        $commands = @(Get-Command -Name 'Get-AuthenticodeSignature' -CommandType Cmdlet -ListImported -All -ErrorAction Stop)
        $facts.field = 'count'
        if ($commands.Count -ne 1) { $facts.origin = 'refused'; return $facts }
        $facts.availability = 'available'
        $facts.stage = 'cmdlet-origin'
        if (-not (Test-OwnedImageSecurityOrigin $inbox $commands[0] $facts)) { $facts.origin = 'refused'; return $facts }
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
        'management-origin' = @('count', 'name', 'manifest', 'base'); 'utility-origin' = @('count', 'name', 'manifest', 'base'); 'security-origin' = @('count', 'name', 'manifest', 'base')
        'cmdlet-resolution' = @('resolution', 'count'); 'cmdlet-origin' = @('path', 'cmdlet-name', 'cmdlet-type', 'module-name', 'manifest', 'base')
        ready = @('none'); unknown = @('unknown') }
    if ($Facts -isnot [Collections.IDictionary] -or $Facts.Count -ne 5 -or
        @($Facts.Keys | Where-Object { $_ -cnotin @('profile', 'origin', 'availability', 'stage', 'field') }).Count -ne 0 -or
        $Facts.profile -cne 'winps-inbox-only' -or $Facts.origin -cnotin @('inbox', 'refused', 'unverified') -or
        $Facts.availability -cnotin @('available', 'unavailable') -or $Facts.stage -isnot [string] -or $Facts.field -isnot [string] -or
        @($checks.Keys) -cnotcontains $Facts.stage -or
        $checks[$Facts.stage] -cnotcontains $Facts.field) { return $fallback }
    if ($Facts.stage -ceq 'ready') {
        if ($Facts.origin -cne 'inbox' -or $Facts.availability -cne 'available') { return $fallback }
    } elseif ($Facts.stage -ceq 'unknown') {
        if ($Facts.origin -cne 'unverified' -or $Facts.availability -cne 'unavailable') { return $fallback }
    } elseif ($Facts.stage -ceq 'cmdlet-origin') {
        if ($Facts.origin -cne 'refused' -or $Facts.availability -cne 'available') { return $fallback }
    } elseif ($Facts.availability -cne 'unavailable' -or $Facts.origin -ceq 'inbox' -or
        ($Facts.origin -ceq 'refused' -and $Facts.field -cin @('assignment', 'import', 'resolution'))) { return $fallback }
    return "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`t$($Facts.origin)`t$($Facts.availability)`t$($Facts.stage)`t$($Facts.field)"
}
