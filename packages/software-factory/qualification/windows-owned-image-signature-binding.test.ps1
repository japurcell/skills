$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$stage = 'parse'
try {
    foreach ($file in @('windows-owned-image-host-profile.ps1', 'windows-owned-image-diagnostics.ps1', 'windows-owned-image-native-build.ps1')) {
        $tokens = $null; $errors = $null
        [void][Management.Automation.Language.Parser]::ParseFile([IO.Path]::Combine($PSScriptRoot, $file), [ref]$tokens, [ref]$errors)
        if ($errors.Count -ne 0) { throw 'parse' }
    }
    . ([IO.Path]::Combine($PSScriptRoot, 'windows-owned-image-host-profile.ps1'))
    . ([IO.Path]::Combine($PSScriptRoot, 'windows-owned-image-diagnostics.ps1'))
    $stage = 'binding'
    $homeRoot = [IO.Path]::Combine([IO.Path]::GetTempPath(), 'owned-image-binding-synthetic')
    $securityBase = [IO.Path]::Combine($homeRoot, 'Modules', 'Microsoft.PowerShell.Security')
    $tuple = @{ Name = 'Microsoft.PowerShell.Security'; ModuleType = [Management.Automation.ModuleType]::Manifest
        Path = [IO.Path]::Combine($securityBase, 'Microsoft.PowerShell.Security.psd1'); ModuleBase = $securityBase }
    $authority = New-OwnedImageSecurityAuthority $homeRoot $tuple
    $stage = 'command-construction'
    # A core cmdlet rejects LiteralPath before executing. No signature API runs.
    $script:expectedCommand = [Management.Automation.CmdletInfo]::new('Get-AuthenticodeSignature', [Microsoft.PowerShell.Commands.GetCommandCommand])
    $script:expectedSnapshot = @{ Name = 'Get-AuthenticodeSignature'; CommandType = [Management.Automation.CommandTypes]::Cmdlet; Module = $tuple.Clone() }
    $script:lookupCalls = 0
    & {
        function Get-OwnedImageCommandSnapshot {
            param([object]$Command)
            if (-not [object]::ReferenceEquals($Command, $script:expectedCommand)) { throw 'identity' }
            return $script:expectedSnapshot
        }
        function Get-Command { $script:lookupCalls++; throw 'changed-catalog' }
        $script:stage = 'binding-construction'
        $binding = New-OwnedImageSignatureBinding $homeRoot $script:expectedCommand $authority
        $script:stage = 'binding-access'
        if ($null -eq $binding -or -not [object]::ReferenceEquals((Get-OwnedImageBoundSignatureCommand $binding), $script:expectedCommand)) { throw 'binding-identity' }
        $script:stage = 'binding-dispatch'
        $context = @{}
        $result = Invoke-OwnedImageSignatureCondition 'synthetic-literal' $context $binding
        if ($result -cnotin @('parameter-binding', 'invocation-failure') -or
            $context.direct -cne 'imported' -or $script:lookupCalls -ne 0) { throw 'bound-dispatch' }
        $forgedValues = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
        foreach ($key in $binding.Keys) { $forgedValues.Add($key, $binding[$key]) }
        $forged = [Collections.ObjectModel.ReadOnlyDictionary[string,object]]::new($forgedValues)
        if ($null -ne (Get-OwnedImageBoundSignatureCommand $forged) -or
            (Invoke-OwnedImageSignatureCondition 'synthetic-literal' @{} $forged) -cne 'command-probe-failure') { throw 'forged-binding' }
        if ((Invoke-OwnedImageSignatureCondition 'synthetic-literal' @{} $null) -cne 'command-probe-failure') { throw 'missing-binding' }
        $mutable = $false
        try { $binding['Snapshot']['Module']['ModuleBase'] = $homeRoot; $mutable = $true } catch { }
        if ($mutable) { throw 'nested-snapshot-mutation' }
        $script:expectedSnapshot.Module.ModuleBase = $homeRoot
        $script:expectedSnapshot.Name = 'other'
        if (-not [object]::ReferenceEquals((Get-OwnedImageBoundSignatureCommand $binding), $script:expectedCommand)) { throw 'binding-snapshot-copy' }
        if ((Invoke-OwnedImageSignatureCondition 'synthetic-literal' @{} $binding) -cnotin @('parameter-binding', 'invocation-failure')) { throw 'immutable-dispatch' }
        $other = [Management.Automation.CmdletInfo]::new('Get-AuthenticodeSignature', [Microsoft.PowerShell.Commands.GetCommandCommand])
        if ($null -ne (New-OwnedImageSignatureBinding $homeRoot $other $authority) -or
            $null -ne (Get-OwnedImageBoundSignatureCommand $binding)) { throw 'changed-identity' }
        if ((Invoke-OwnedImageSignatureCondition 'synthetic-literal' @{} $binding) -cne 'command-probe-failure' -or $script:lookupCalls -ne 0) { throw 'no-fallback' }
    }
    'PowerShell 7 same-object binding/catalog trap passed (synthetic capture, no certificate query)'
    exit 0
} catch {
    "PowerShell binding proof failed stage=$stage"
    exit 1
}
