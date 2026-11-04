$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$stage = 'parse'; $homeRoot = $null
try {
    $source = $PSScriptRoot
    foreach ($name in @('windows-owned-image-native-build.ps1', 'windows-owned-image-host-profile.ps1')) {
        $tokens = $null; $errors = $null
        [void][Management.Automation.Language.Parser]::ParseFile((Join-Path $source $name), [ref]$tokens, [ref]$errors)
        if ($errors.Count -ne 0) { throw 'parse' }
    }
    . (Join-Path $source 'windows-owned-image-host-profile.ps1')
    $stage = 'fixture'
    $homeRoot = [IO.Path]::Combine([IO.Path]::GetTempPath(), 'owned-image-profile-' + [Guid]::NewGuid().ToString('N'))
    $inbox = [IO.Path]::Combine($homeRoot, 'Modules')
    foreach ($name in @('Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Security')) {
        $directory = [IO.Path]::Combine($inbox, $name)
        [void][IO.Directory]::CreateDirectory($directory)
        [IO.File]::WriteAllText([IO.Path]::Combine($directory, $name + '.psd1'), '# synthetic inert fixture')
    }
    $script:expectedInbox = $inbox; $script:origin = 'inbox'; $script:imports = @()
    function Import-Module {
        [CmdletBinding()]
        param([string]$Name, [string]$Scope, [switch]$PassThru)
        $base = [IO.Path]::GetDirectoryName($Name)
        $moduleName = [IO.Path]::GetFileName($base)
        if ($Scope -cne 'Global' -or -not $PassThru -or
            [IO.Path]::GetDirectoryName($base) -cne $script:expectedInbox) { throw 'import-contract' }
        $script:imports += $moduleName
        return [pscustomobject]@{ Name = $moduleName; Path = $Name; ModuleBase = $base }
    }
    function Get-Command {
        [CmdletBinding()]
        param([string]$Name, [string]$CommandType, [switch]$ListImported, [switch]$All)
        if ($Name -cne 'Get-AuthenticodeSignature' -or $CommandType -cne 'Cmdlet' -or -not $ListImported -or -not $All) { throw 'command-contract' }
        $base = [IO.Path]::Combine($script:expectedInbox, 'Microsoft.PowerShell.Security')
        $path = if ($script:origin -eq 'inbox') { [IO.Path]::Combine($base, 'Microsoft.PowerShell.Security.psd1') } else { [IO.Path]::Combine($homeRoot, 'foreign.psd1') }
        return [pscustomobject]@{ Name = 'Get-AuthenticodeSignature'; CommandType = 'Cmdlet';
            Module = [pscustomobject]@{ Name = 'Microsoft.PowerShell.Security'; Path = $path; ModuleBase = $base } }
    }
    $stage = 'candidate'
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'inbox' -or $facts.availability -cne 'available' -or $env:PSModulePath -cne $inbox -or
        $script:PSModuleAutoLoadingPreference -cne 'None' -or $script:imports.Count -ne 3) { throw 'candidate' }
    if ((Format-OwnedImageHostProfile $facts) -cne "OWNED_IMAGE_PROFILE`t1`twinps-inbox-only`tinbox`tavailable") { throw 'fixed-facts' }
    $stage = 'strict-origin'
    $good = Get-Command -Name 'Get-AuthenticodeSignature' -CommandType Cmdlet -ListImported -All
    if (-not (Test-OwnedImageSecurityOrigin $inbox $good)) { throw 'good-origin' }
    foreach ($field in @('name', 'type', 'module', 'base', 'sibling')) {
        $bad = [pscustomobject]@{ Name = $good.Name; CommandType = $good.CommandType;
            Module = [pscustomobject]@{ Name = $good.Module.Name; Path = $good.Module.Path; ModuleBase = $good.Module.ModuleBase } }
        if ($field -eq 'name') { $bad.Name = 'synthetic-other' }
        if ($field -eq 'type') { $bad.CommandType = 'Function' }
        if ($field -eq 'module') { $bad.Module.Name = 'synthetic-other' }
        if ($field -eq 'base') { $bad.Module.ModuleBase = $homeRoot }
        if ($field -eq 'sibling') { $bad.Module.Path = [IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Security-other', 'Microsoft.PowerShell.Security.psd1') }
        if (Test-OwnedImageSecurityOrigin $inbox $bad) { throw 'bad-origin' }
    }
    $stage = 'origin-refusal'; $script:origin = 'foreign'
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'refused' -or $facts.availability -cne 'available') { throw 'foreign-origin' }
    $stage = 'profile-refusal'
    $facts = Initialize-OwnedImageInboxProfile $homeRoot ([IO.Path]::Combine($homeRoot, 'foreign')) 'winps-inbox-only'
    if ($facts.origin -cne 'refused' -or $facts.availability -cne 'unavailable') { throw 'foreign-root' }
    $stage = 'missing-manifest'
    [IO.File]::Delete([IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Security', 'Microsoft.PowerShell.Security.psd1'))
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'refused' -or $facts.availability -cne 'unavailable') { throw 'missing-manifest' }
    'PowerShell 7 candidate environment/import/origin checks passed (synthetic, not native host proof)'
    exit 0
} catch {
    "PowerShell candidate proof failed stage=$stage"
    exit 1
} finally {
    if ($null -ne $homeRoot -and [IO.Directory]::Exists($homeRoot)) { [IO.Directory]::Delete($homeRoot, $true) }
}
