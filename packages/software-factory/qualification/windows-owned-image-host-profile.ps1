# Explicit candidate, private metadata checks and fixed facts only.
function Test-OwnedImageSecurityOrigin {
    param([string]$Inbox, [object]$Command)
    try {
        $manifest = [IO.Path]::GetFullPath([IO.Path]::Combine($Inbox, 'Microsoft.PowerShell.Security', 'Microsoft.PowerShell.Security.psd1'))
        $base = [IO.Path]::GetDirectoryName($manifest)
        return $Command.Name -ceq 'Get-AuthenticodeSignature' -and $Command.CommandType -eq 'Cmdlet' -and
            $Command.Module.Name -ceq 'Microsoft.PowerShell.Security' -and
            [string]::Equals([IO.Path]::GetFullPath($Command.Module.Path), $manifest, [StringComparison]::OrdinalIgnoreCase) -and
            [string]::Equals([IO.Path]::GetFullPath($Command.Module.ModuleBase), $base, [StringComparison]::OrdinalIgnoreCase)
    } catch { return $false }
}

function Initialize-OwnedImageInboxProfile {
    param([string]$HostHome, [string]$ExpectedInbox, [string]$Profile)
    $facts = @{ profile = 'winps-inbox-only'; origin = 'unverified'; availability = 'unavailable' }
    try {
        $inbox = [IO.Path]::GetFullPath([IO.Path]::Combine($HostHome, 'Modules'))
        if ($inbox -match '[;*?\[\]\x00-\x1f\x7f]' -or $Profile -cne 'winps-inbox-only' -or
            -not [string]::Equals([IO.Path]::GetFullPath($ExpectedInbox), $inbox, [StringComparison]::OrdinalIgnoreCase)) {
            $facts.origin = 'refused'; return $facts
        }
        # Startup can augment the inherited variable. Narrow it again before imports.
        $env:PSModulePath = $inbox
        $script:PSModuleAutoLoadingPreference = 'None'
        if (([IO.File]::GetAttributes($inbox) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $facts.origin = 'refused'; return $facts }
        foreach ($name in @('Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Security')) {
            $directory = [IO.Path]::Combine($inbox, $name)
            $manifest = [IO.Path]::Combine($directory, $name + '.psd1')
            if (-not [IO.File]::Exists($manifest) -or
                ([IO.File]::GetAttributes($directory) -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
                ([IO.File]::GetAttributes($manifest) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $facts.origin = 'refused'; return $facts }
            # Global means only this disposable child session, never a saved profile.
            $loaded = @(Import-Module -Name $manifest -Scope Global -PassThru -ErrorAction Stop)
            if ($loaded.Count -ne 1 -or $loaded[0].Name -cne $name -or
                -not [string]::Equals([IO.Path]::GetFullPath($loaded[0].Path), $manifest, [StringComparison]::OrdinalIgnoreCase) -or
                -not [string]::Equals([IO.Path]::GetFullPath($loaded[0].ModuleBase), $directory, [StringComparison]::OrdinalIgnoreCase)) {
                $facts.origin = 'refused'; return $facts
            }
        }
        $commands = @(Get-Command -Name 'Get-AuthenticodeSignature' -CommandType Cmdlet -ListImported -All -ErrorAction Stop)
        if ($commands.Count -ne 1) { $facts.origin = 'refused'; return $facts }
        $facts.availability = 'available'
        if (-not (Test-OwnedImageSecurityOrigin $inbox $commands[0])) { $facts.origin = 'refused'; return $facts }
        $facts.origin = 'inbox'
        return $facts
    } catch { return $facts }
}

function Format-OwnedImageHostProfile {
    param([object]$Facts)
    $fallback = "OWNED_IMAGE_PROFILE`t1`twinps-inbox-only`tunverified`tunavailable"
    if ($Facts -isnot [Collections.IDictionary] -or $Facts.Count -ne 3 -or
        @($Facts.Keys | Where-Object { $_ -cnotin @('profile', 'origin', 'availability') }).Count -ne 0 -or
        $Facts.profile -cne 'winps-inbox-only' -or $Facts.origin -cnotin @('inbox', 'refused', 'unverified') -or
        $Facts.availability -cnotin @('available', 'unavailable')) { return $fallback }
    if (($Facts.origin -ceq 'inbox' -and $Facts.availability -cne 'available') -or
        ($Facts.origin -ceq 'unverified' -and $Facts.availability -cne 'unavailable')) { return $fallback }
    return "OWNED_IMAGE_PROFILE`t1`twinps-inbox-only`t$($Facts.origin)`t$($Facts.availability)"
}
