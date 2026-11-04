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
    $script:failModule = ''; $script:failField = ''; $script:commandField = ''; $script:hostBase = $false
    $script:countSnapshots = $false; $script:captureCounts = @{}
    function Import-Module {
        [CmdletBinding()]
        param([string]$Name, [string]$Scope, [switch]$PassThru)
        $base = [IO.Path]::GetDirectoryName($Name)
        $moduleName = [IO.Path]::GetFileName($base)
        if ($Scope -cne 'Global' -or -not $PassThru -or
            [IO.Path]::GetDirectoryName($base) -cne $script:expectedInbox) { throw 'import-contract' }
        $script:imports += $moduleName
        if ($moduleName -ceq $script:failModule) {
            if ($script:failField -ceq 'import') { throw 'synthetic-private-import' }
            if ($script:failField -ceq 'count') { return }
            if ($script:failField -ceq 'name') { return [pscustomobject]@{ Name = 'other'; ModuleType = [Management.Automation.ModuleType]::Manifest; Path = $Name; ModuleBase = $base } }
            if ($script:failField -ceq 'manifest') { return [pscustomobject]@{ Name = $moduleName; ModuleType = [Management.Automation.ModuleType]::Manifest; Path = $Name + '.other'; ModuleBase = $base } }
            if ($script:failField -ceq 'base') { return [pscustomobject]@{ Name = $moduleName; ModuleType = [Management.Automation.ModuleType]::Manifest; Path = $Name; ModuleBase = [IO.Path]::Combine($homeRoot, 'foreign-child') } }
        }
        $selectedBase = if ($script:hostBase) { $homeRoot } else { $base }
        if ($script:countSnapshots) {
            $counter = @{ Name = 0; ModuleType = 0; Path = 0; ModuleBase = 0 }
            $metadata = @{ Name = $moduleName; ModuleType = [Management.Automation.ModuleType]::Manifest; Path = $Name; ModuleBase = $selectedBase }
            $script:captureCounts[$moduleName] = $counter
            $object = [pscustomobject]@{}
            foreach ($property in @('Name', 'ModuleType', 'Path', 'ModuleBase')) {
                $getter = { $counter[$property]++; if ($counter[$property] -gt 1) { throw 'metadata-read-twice' }; return $metadata[$property] }.GetNewClosure()
                $object.PSObject.Properties.Add([Management.Automation.PSScriptProperty]::new($property, $getter))
            }
            return $object
        }
        return [pscustomobject]@{ Name = $moduleName; ModuleType = [Management.Automation.ModuleType]::Manifest; Path = $Name; ModuleBase = $selectedBase }
    }
    function Get-Command {
        [CmdletBinding()]
        param([string]$Name, [string]$CommandType, [switch]$ListImported, [switch]$All)
        if ($Name -cne 'Get-AuthenticodeSignature' -or $CommandType -cne 'Cmdlet' -or -not $ListImported -or -not $All) { throw 'command-contract' }
        if ($script:commandField -ceq 'resolution') { throw 'synthetic-private-resolution' }
        if ($script:commandField -ceq 'count') { return }
        $base = [IO.Path]::Combine($script:expectedInbox, 'Microsoft.PowerShell.Security')
        $path = if ($script:origin -eq 'inbox') { [IO.Path]::Combine($base, 'Microsoft.PowerShell.Security.psd1') } else { [IO.Path]::Combine($homeRoot, 'foreign.psd1') }
        $command = [pscustomobject]@{ Name = 'Get-AuthenticodeSignature'; CommandType = 'Cmdlet';
            Module = [pscustomobject]@{ Name = 'Microsoft.PowerShell.Security'; Path = $path; ModuleBase = $base } }
        if ($script:commandField -ceq 'cmdlet-name') { $command.Name = 'other' }
        if ($script:commandField -ceq 'cmdlet-type') { $command.CommandType = 'Function' }
        if ($script:commandField -ceq 'module-name') { $command.Module.Name = 'other' }
        if ($script:commandField -ceq 'manifest') { $command.Module.Path = $path + '.other' }
        if ($script:commandField -ceq 'base') { $command.Module.ModuleBase = $homeRoot }
        return $command
    }
    $stage = 'candidate'
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'inbox' -or $facts.availability -cne 'available' -or $env:PSModulePath -cne $inbox -or
        $script:PSModuleAutoLoadingPreference -cne 'None' -or $script:imports.Count -ne 3) { throw 'candidate' }
    if ((Format-OwnedImageHostProfile $facts) -cne "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`tinbox`tavailable`tready`tnone") { throw 'fixed-facts' }
    $stage = 'observed-complete-tuple'; $script:hostBase = $true; $script:imports = @(); $script:countSnapshots = $true
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'inbox' -or $facts.stage -cne 'ready' -or $script:imports.Count -ne 3) { throw 'observed-tuple' }
    if ($script:captureCounts.Count -ne 3) { throw 'import-capture-count' }
    foreach ($counts in $script:captureCounts.Values) {
        foreach ($property in @('Name', 'ModuleType', 'Path', 'ModuleBase')) { if ($counts[$property] -ne 1) { throw 'import-property-count' } }
    }
    $script:hostBase = $false; $script:countSnapshots = $false
    $stage = 'fixed-origin-tuples'
    foreach ($role in @('Management', 'Utility', 'Security')) {
        $name = 'Microsoft.PowerShell.' + $role
        $directory = [IO.Path]::Combine($inbox, $name)
        $manifest = [IO.Path]::Combine($directory, $name + '.psd1')
        foreach ($base in @($directory, $homeRoot)) {
            $snapshot = @{ Name = $name; ModuleType = [Management.Automation.ModuleType]::Manifest; Path = $manifest; ModuleBase = $base }
            if (-not (Test-OwnedImageInboxModuleOrigin $homeRoot $name $snapshot)) { throw 'safe-tuple' }
            foreach ($badCase in @('name', 'binary', 'script', 'unknown', 'kind-string', 'kind-array', 'path', 'path-child', 'path-type',
                'base', 'base-child', 'base-prefix', 'base-traversal', 'base-type', 'base-null', 'name-type', 'missing-kind', 'extra')) {
                $bad = $snapshot.Clone()
                if ($badCase -ceq 'name') { $bad.Name = $name + '-other' }
                if ($badCase -ceq 'binary') { $bad.ModuleType = [Management.Automation.ModuleType]::Binary }
                if ($badCase -ceq 'script') { $bad.ModuleType = [Management.Automation.ModuleType]::Script }
                if ($badCase -ceq 'unknown') { $bad.ModuleType = $null }
                if ($badCase -ceq 'kind-string') { $bad.ModuleType = 'Manifest' }
                if ($badCase -ceq 'kind-array') { $bad.ModuleType = @([Management.Automation.ModuleType]::Manifest) }
                if ($badCase -ceq 'path') { $bad.Path = $manifest + '.other' }
                if ($badCase -ceq 'path-child') { $bad.Path = [IO.Path]::Combine($directory, 'child', $name + '.psd1') }
                if ($badCase -ceq 'path-type') { $bad.Path = @($manifest) }
                if ($badCase -ceq 'base') { $bad.ModuleBase = $inbox }
                if ($badCase -ceq 'base-child') { $bad.ModuleBase = [IO.Path]::Combine($base, 'child') }
                if ($badCase -ceq 'base-prefix') { $bad.ModuleBase = $base + '-other' }
                if ($badCase -ceq 'base-traversal') { $bad.ModuleBase = [IO.Path]::Combine($base, 'child', '..') }
                if ($badCase -ceq 'base-type') { $bad.ModuleBase = @($base) }
                if ($badCase -ceq 'base-null') { $bad.ModuleBase = $null }
                if ($badCase -ceq 'name-type') { $bad.Name = @($name) }
                if ($badCase -ceq 'missing-kind') { $bad.Remove('ModuleType') }
                if ($badCase -ceq 'extra') { $bad.extra = 'private' }
                if (Test-OwnedImageInboxModuleOrigin $homeRoot $name $bad) { throw 'unsafe-tuple' }
            }
        }
    }
    $stage = 'single-snapshot'
    $missingKind = Get-OwnedImageModuleSnapshot ([pscustomobject]@{ Name = 'Microsoft.PowerShell.Management'
        Path = [IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Management.psd1'); ModuleBase = $homeRoot })
    if (Test-OwnedImageInboxModuleOrigin $homeRoot 'Microsoft.PowerShell.Management' $missingKind) { throw 'missing-kind-host-base' }
    $script:reads = @{ Name = 0; ModuleType = 0; Path = 0; ModuleBase = 0 }
    $script:capturedValues = @{ Name = 'Microsoft.PowerShell.Management'; ModuleType = [Management.Automation.ModuleType]::Manifest
        Path = [IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Management.psd1'); ModuleBase = $homeRoot }
    $changing = [pscustomobject]@{}
    $reads = $script:reads; $values = $script:capturedValues
    foreach ($property in @('Name', 'ModuleType', 'Path', 'ModuleBase')) {
        $getter = { $reads[$property]++; if ($reads[$property] -gt 1) { throw 'read-twice' }; return $values[$property] }.GetNewClosure()
        $changing.PSObject.Properties.Add([Management.Automation.PSScriptProperty]::new($property, $getter))
    }
    $captured = Get-OwnedImageModuleSnapshot $changing
    $script:capturedValues.ModuleBase = [IO.Path]::Combine($homeRoot, 'foreign-child')
    if (-not (Test-OwnedImageInboxModuleOrigin $homeRoot 'Microsoft.PowerShell.Management' $captured)) { throw 'captured-admission' }
    $observed = Get-OwnedImageManagementRelation $homeRoot $captured
    if ($observed.base -cne 'selected-WinPS-host-directory') { throw 'captured-projection' }
    foreach ($property in @('Name', 'ModuleType', 'Path', 'ModuleBase')) { if ($script:reads[$property] -ne 1) { throw 'capture-count' } }
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
    $stage = 'fixed-relations'
    $manifestBase = [IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Management')
    $manifestPath = [IO.Path]::Combine($manifestBase, 'Microsoft.PowerShell.Management.psd1')
    $binaryPath = [IO.Path]::Combine($homeRoot, 'Microsoft.PowerShell.Commands.Management.dll')
    foreach ($kind in @('Manifest', 'Binary', 'Script', 'SyntheticOther')) {
        foreach ($baseCase in @('selected-manifest-directory', 'selected-WinPS-host-directory', 'inbox-root', 'other')) {
            foreach ($pathCase in @('exact-selected-manifest', 'known-fixed-Management-binary-under-selected-host', 'other')) {
                $observedBase = switch ($baseCase) {
                    'selected-manifest-directory' { $manifestBase }; 'selected-WinPS-host-directory' { $homeRoot }
                    'inbox-root' { $inbox }; 'other' { $manifestBase + '-other' }
                }
                $observedPath = switch ($pathCase) {
                    'exact-selected-manifest' { $manifestPath }; 'known-fixed-Management-binary-under-selected-host' { $binaryPath }
                    'other' { $binaryPath + '.other' }
                }
                $module = [pscustomobject]@{ ModuleType = $kind; ModuleBase = $observedBase; Path = $observedPath }
                $relation = Get-OwnedImageManagementRelation $homeRoot $module
                $expectedKind = if ($kind -ceq 'SyntheticOther') { 'unknown' } else { $kind.ToLowerInvariant() }
                if ($relation.kind -cne $expectedKind -or $relation.base -cne $baseCase -or $relation.path -cne $pathCase -or $relation.baseType -cne 'string') { throw 'relations' }
            }
        }
    }
    $relationFacts = @{ profile = 'winps-inbox-only'; origin = 'refused'; availability = 'unavailable'; stage = 'management-origin'; field = 'base'
        relation = @{ kind = 'binary'; base = 'selected-WinPS-host-directory'; path = 'exact-selected-manifest'; baseType = 'string' } }
    $relationExpected = "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`trefused`tunavailable`tmanagement-origin`tbase" + [Environment]::NewLine +
        "OWNED_IMAGE_RELATION`t1`tbinary`tselected-WinPS-host-directory`texact-selected-manifest`tstring"
    if ((Format-OwnedImageHostProfile $relationFacts) -cne $relationExpected) { throw 'relation-wire' }
    foreach ($change in @('context', 'kind', 'base', 'path', 'type', 'extra')) {
        $forged = @{ profile = 'winps-inbox-only'; origin = 'refused'; availability = 'unavailable'; stage = 'management-origin'; field = 'base'
            relation = @{ kind = 'binary'; base = 'selected-WinPS-host-directory'; path = 'exact-selected-manifest'; baseType = 'string' } }
        if ($change -ceq 'context') { $forged.stage = 'utility-origin' }
        if ($change -ceq 'kind') { $forged.relation.kind = 'C:\private' }
        if ($change -ceq 'base') { $forged.relation.base = "other`nprivate" }
        if ($change -ceq 'path') { $forged.relation.path = 'x' * 513 }
        if ($change -ceq 'type') { $forged.relation.kind = @('binary') }
        if ($change -ceq 'extra') { $forged.relation.extra = 'private' }
        if ((Format-OwnedImageHostProfile $forged) -cne "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`tunverified`tunavailable`tunknown`tunknown") { throw 'forged-relation' }
    }
    $uninspectable = Get-OwnedImageManagementRelation $homeRoot $null
    if ($uninspectable.kind -cne 'unknown' -or $uninspectable.base -cne 'other' -or $uninspectable.path -cne 'other' -or $uninspectable.baseType -cne 'other') { throw 'unknown-relation' }
    $partial = Get-OwnedImageManagementRelation $homeRoot ([pscustomobject]@{ ModuleBase = $inbox; Path = $manifestPath })
    if ($partial.kind -cne 'unknown' -or $partial.base -cne 'inbox-root' -or $partial.path -cne 'exact-selected-manifest') { throw 'independent-relation' }
    foreach ($tag in @('null', 'single-string-array', 'other')) {
        $rawBase = switch ($tag) { 'null' { $null }; 'single-string-array' { ,@($homeRoot) }; 'other' { [pscustomobject]@{ private = 'value' } } }
        $typed = Get-OwnedImageManagementRelation $homeRoot ([pscustomobject]@{ ModuleType = @('Binary'); ModuleBase = $rawBase; Path = [pscustomobject]@{ private = 'value' } })
        if ($typed.baseType -cne $tag -or $typed.base -cne 'other' -or $typed.path -cne 'other' -or $typed.kind -cne 'unknown') { throw 'typed-relation' }
    }
    $stage = 'fixed-stage-projection'
    foreach ($role in @('Management', 'Utility', 'Security')) {
        $script:failModule = 'Microsoft.PowerShell.' + $role
        foreach ($field in @('import', 'count', 'name', 'manifest', 'base')) {
            $script:failField = $field
            $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
            $suffix = if ($field -ceq 'import') { '-import' } else { '-origin' }
            if ($facts.stage -cne ($role.ToLowerInvariant() + $suffix) -or $facts.field -cne $field -or
                $facts.availability -cne 'unavailable' -or $facts.origin -ceq 'inbox') { throw 'module-stage' }
            if ($role -ceq 'Management' -and $field -ceq 'base') {
                if ($facts.relation.base -cne 'other' -or $facts.relation.path -cne 'exact-selected-manifest') { throw 'refusal-relation' }
            } elseif ((Format-OwnedImageHostProfile $facts) -notmatch '^OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\t(refused|unverified)\tunavailable\t[a-z-]+\t[a-z-]+$') { throw 'module-wire' }
        }
    }
    $script:failModule = ''; $script:failField = ''
    foreach ($field in @('resolution', 'count', 'cmdlet-name', 'cmdlet-type', 'module-name', 'manifest', 'base')) {
        $script:commandField = $field
        $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
        $expectedStage = if ($field -cin @('resolution', 'count')) { 'cmdlet-resolution' } else { 'cmdlet-origin' }
        if ($facts.stage -cne $expectedStage -or $facts.field -cne $field -or $facts.origin -ceq 'inbox') { throw 'cmdlet-stage' }
    }
    $script:commandField = ''
    $fallback = "OWNED_IMAGE_PROFILE`t2`twinps-inbox-only`tunverified`tunavailable`tunknown`tunknown"
    foreach ($patch in @(@{ stage = 'C:\private' }, @{ field = "manifest`nprivate" }, @{ field = ('x' * 513) },
        @{ availability = 'available' }, @{ field = 'cmdlet-type' }, @{ stage = @('security-origin') }, @{ field = @('manifest') }, @{ extra = 'private' })) {
        $forged = @{ profile = 'winps-inbox-only'; origin = 'refused'; availability = 'unavailable'; stage = 'security-origin'; field = 'manifest' }
        foreach ($key in $patch.Keys) { $forged[$key] = $patch[$key] }
        if ((Format-OwnedImageHostProfile $forged) -cne $fallback) { throw 'forged-wire' }
    }
    $stage = 'origin-refusal'; $script:origin = 'foreign'
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'refused' -or $facts.availability -cne 'available' -or
        $facts.stage -cne 'cmdlet-origin' -or $facts.field -cne 'manifest') { throw 'foreign-origin' }
    $stage = 'profile-refusal'
    $facts = Initialize-OwnedImageInboxProfile $homeRoot ([IO.Path]::Combine($homeRoot, 'foreign')) 'winps-inbox-only'
    if ($facts.origin -cne 'refused' -or $facts.availability -cne 'unavailable' -or
        $facts.stage -cne 'environment' -or $facts.field -cne 'inbox') { throw 'foreign-root' }
    $stage = 'missing-manifest'
    [IO.File]::Delete([IO.Path]::Combine($inbox, 'Microsoft.PowerShell.Security', 'Microsoft.PowerShell.Security.psd1'))
    $facts = Initialize-OwnedImageInboxProfile $homeRoot $inbox 'winps-inbox-only'
    if ($facts.origin -cne 'refused' -or $facts.availability -cne 'unavailable' -or
        $facts.stage -cne 'security-import' -or $facts.field -cne 'manifest') { throw 'missing-manifest' }
    'PowerShell 7 candidate environment/import/origin checks passed (synthetic, not native host proof)'
    exit 0
} catch {
    "PowerShell candidate proof failed stage=$stage"
    exit 1
} finally {
    if ($null -ne $homeRoot -and [IO.Directory]::Exists($homeRoot)) { [IO.Directory]::Delete($homeRoot, $true) }
}
