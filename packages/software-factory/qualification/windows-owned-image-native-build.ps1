# Qualification-only build using the already installed disposable-runner MSVC.
# Operational paths, tool identities, versions and build output stay private.
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$Evidence)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$diagnosticCategory = 'host'
$diagnosticTool = 'none'
$diagnosticCondition = 'none'
$compilerDiagnostic = @{ code = 'none'; source = 'none'; line = 0 }
$diagnosticHelpersLoaded = $false
try {
    . (Join-Path $PSScriptRoot 'windows-owned-image-diagnostics.ps1')
    $diagnosticHelpersLoaded = $true
    if ($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitProcess -or $PSVersionTable.PSVersion.Major -ne 5) { throw 'host' }
    $diagnosticCategory = 'path'
    $evidenceRoot = [IO.Path]::GetFullPath($Evidence)
    $sourceRoot = $PSScriptRoot
    foreach ($value in @($evidenceRoot, $sourceRoot)) {
        if ($value -match '[&|<>\r\n"%!]' -or $value -match '[^\x20-\x7e]') { throw 'path' }
    }
    $native = Join-Path $evidenceRoot 'native'
    $diagnosticCategory = 'existing-build'
    if (Test-Path -LiteralPath $native) { throw 'existing-build' }
    $diagnosticCategory = 'path'
    [void][IO.Directory]::CreateDirectory($native)
    $diagnosticCategory = 'missing-msvc'
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    function Assert-MicrosoftTool([string]$Path, [string]$Role) {
        $script:diagnosticTool = 'none'
        $script:diagnosticCondition = 'none'
        $script:diagnosticCategory = 'missing-msvc'
        if (-not [IO.File]::Exists($Path) -or ((Get-Item -LiteralPath $Path).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'tool' }
        $script:diagnosticCategory = 'tool-signature'
        $script:diagnosticTool = $Role
        $script:diagnosticCondition = 'api-failure'
        $signature = Get-AuthenticodeSignature -LiteralPath $Path
        $script:diagnosticCondition = Get-OwnedImageSignatureCondition $signature
        if ($script:diagnosticCondition -cne 'none') { throw 'tool-signature' }
        $script:diagnosticTool = 'none'
        $script:diagnosticCondition = 'none'
    }
    Assert-MicrosoftTool $vswhere 'vswhere'
    $diagnosticCategory = 'missing-msvc'
    $installation = @(& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath)
    if ($LASTEXITCODE -ne 0 -or $installation.Count -ne 1) { throw 'toolchain' }
    $diagnosticCategory = 'path'
    $installationRoot = [IO.Path]::GetFullPath([string]$installation[0])
    if ($installationRoot -notmatch '^[A-Za-z]:\\Program Files(?: \(x86\))?\\Microsoft Visual Studio\\' -or $installationRoot -match '[&|<>\r\n"%!]' -or $installationRoot -match '[^\x20-\x7e]') { throw 'toolchain-root' }
    $toolsetRoot = Join-Path $installationRoot 'VC\Tools\MSVC'
    $diagnosticCategory = 'missing-msvc'
    $toolsets = @(Get-ChildItem -LiteralPath $toolsetRoot -Directory | Where-Object { $_.Name -match '^14\.[0-9]{2}\.[0-9]{5}$' } | Sort-Object { [version]$_.Name } -Descending)
    if ($toolsets.Count -eq 0) { throw 'missing-compiler' }
    $toolset = $toolsets[0]
    if ($toolset.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'toolset' }
    $tools = Join-Path $toolset.FullName 'bin\Hostx64\x64'
    $compiler = Join-Path $tools 'cl.exe'
    $linker = Join-Path $tools 'link.exe'
    Assert-MicrosoftTool $compiler 'compiler'
    Assert-MicrosoftTool $linker 'linker'
    $diagnosticCategory = 'compiler-version'
    $compilerVersion = (Get-Item -LiteralPath $compiler).VersionInfo.FileVersion
    if ($compilerVersion -notmatch '^19\.[0-9]+\.[0-9]+(?:\.[0-9]+)?(?: .*)?$') { throw 'compiler-version' }
    $vcvars = Join-Path $installationRoot 'VC\Auxiliary\Build\vcvars64.bat'
    $diagnosticCategory = 'missing-msvc'
    if (-not [IO.File]::Exists($vcvars)) { throw 'missing-environment' }
    $sources = @('windows-owned-image-probe.cpp', 'windows-owned-image-shared.h', 'windows-owned-image-fixture.cpp', 'windows-owned-image-fixture-dll.cpp')
    $diagnosticCategory = 'source'
    $pins = @($sources | ForEach-Object {
        $file = Join-Path $sourceRoot $_
        $item = Get-Item -LiteralPath $file
        if ($item.Length -le 0 -or $item.Length -gt 131072 -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'source' }
        [ordered]@{ name = $_; sha256 = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() }
    })
    foreach ($directory in @('fixture', 'alternate', 'copy')) { [void][IO.Directory]::CreateDirectory((Join-Path $native $directory)) }
    $command = @(
        '@echo off',
        ('call "{0}" >nul 2>&1' -f $vcvars),
        'if errorlevel 1 exit /b 1',
        ('if not "%VCToolsVersion%"=="{0}" exit /b 1' -f $toolset.Name),
        ('"{0}" /Bv 2>&1' -f $compiler),
        ('cd /d "{0}"' -f $native),
        ('"{0}" /nologo /W4 /WX /std:c++17 /EHsc /MT /DUNICODE /D_UNICODE /D_WIN32_WINNT=0x0A00 /I"{1}" "{1}\windows-owned-image-probe.cpp" /Fe:probe.exe /Fo:probe.obj /link /INCREMENTAL:NO bcrypt.lib' -f $compiler, $sourceRoot),
        'if errorlevel 1 exit /b 1',
        'cd fixture',
        ('"{0}" /nologo /W4 /WX /std:c++17 /EHsc /MT /DUNICODE /D_UNICODE /I"{1}" /LD "{1}\windows-owned-image-fixture-dll.cpp" /Fe:canary.dll /Fo:dll.obj /link /INCREMENTAL:NO /IMPLIB:canary.lib' -f $compiler, $sourceRoot),
        'if errorlevel 1 exit /b 1',
        ('"{0}" /nologo /W4 /WX /std:c++17 /EHsc /MT /DUNICODE /D_UNICODE /I"{1}" "{1}\windows-owned-image-fixture.cpp" canary.lib /Fe:canary.exe /Fo:fixture.obj /link /INCREMENTAL:NO' -f $compiler, $sourceRoot),
        'if errorlevel 1 exit /b 1',
        'cd ..\alternate',
        ('"{0}" /nologo /W4 /WX /std:c++17 /EHsc /MT /DUNICODE /D_UNICODE /DFACTORY_ALTERNATE /I"{1}" "{1}\windows-owned-image-fixture.cpp" ..\fixture\canary.lib /Fe:canary.exe /Fo:alternate.obj /link /INCREMENTAL:NO' -f $compiler, $sourceRoot),
        'if errorlevel 1 exit /b 1',
        'exit /b 0'
    ) -join "`r`n"
    $diagnosticCategory = 'compile'
    $batch = Join-Path $evidenceRoot 'build.private.cmd'
    [IO.File]::WriteAllText($batch, $command + "`r`n", [Text.Encoding]::ASCII)
    $buildLog = Join-Path $evidenceRoot 'build.private.log'
    $cmd = Join-Path $env:SystemRoot 'System32\cmd.exe'
    & $cmd /d /s /c ('""{0}" >"{1}" 2>&1"' -f $batch, $buildLog)
    if ($LASTEXITCODE -ne 0) {
        if ([IO.File]::Exists($buildLog) -and (Get-Item -LiteralPath $buildLog).Length -le 1048576) {
            $compilerDiagnostic = Get-OwnedImageCompilerDiagnostic ([IO.File]::ReadAllText($buildLog))
        }
        throw 'compile'
    }
    $diagnosticCategory = 'build-cap'
    if ((Get-Item -LiteralPath $buildLog).Length -gt 1048576) { throw 'build-cap' }
    $diagnosticCategory = 'source-changed'
    foreach ($pin in $pins) {
        if ((Get-FileHash -LiteralPath (Join-Path $sourceRoot $pin.name) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pin.sha256) { throw 'source-changed' }
    }
    $diagnosticCategory = 'binary'
    [IO.File]::Copy((Join-Path $native 'fixture\canary.exe'), (Join-Path $native 'copy\canary.exe'), $false)
    foreach ($directory in @('alternate', 'copy')) {
        [IO.File]::Copy((Join-Path $native 'fixture\canary.dll'), (Join-Path $native ($directory + '\canary.dll')), $false)
    }
    $binaries = @('probe.exe', 'fixture\canary.exe', 'fixture\canary.dll', 'alternate\canary.exe', 'alternate\canary.dll', 'copy\canary.exe', 'copy\canary.dll')
    $binaryPins = @($binaries | ForEach-Object {
        $path = Join-Path $native $_
        $item = Get-Item -LiteralPath $path
        if ($item.Length -le 0 -or $item.Length -gt 16777216) { throw 'binary-cap' }
        [ordered]@{ name = $_; sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
    })
    $diagnosticCategory = 'report'
    $report = [ordered]@{ protocol = 1; complete = $true; architecture = 'x64'; powershell = $PSVersionTable.PSVersion.ToString();
        operatingSystem = [Environment]::OSVersion.VersionString; compiler = $compiler; compilerVersion = $compilerVersion;
        toolset = $toolset.Name; compilerSha256 = (Get-FileHash -LiteralPath $compiler -Algorithm SHA256).Hash.ToLowerInvariant();
        linkerSha256 = (Get-FileHash -LiteralPath $linker -Algorithm SHA256).Hash.ToLowerInvariant(); sources = $pins; binaries = $binaryPins }
    [IO.File]::WriteAllText((Join-Path $evidenceRoot 'build.private.json'), ($report | ConvertTo-Json -Depth 8), (New-Object Text.UTF8Encoding($false)))
    exit 0
} catch {
    # No exception text or operational tool/path inventory in console output.
    $safeDiagnostic = "OWNED_IMAGE_BUILD`t3`tunexpected`tnone`tnone`t0`tnone`tnone"
    if ($diagnosticHelpersLoaded) {
        try { $safeDiagnostic = Format-OwnedImageBuildDiagnostic $diagnosticCategory $compilerDiagnostic $diagnosticTool $diagnosticCondition }
        catch { $safeDiagnostic = "OWNED_IMAGE_BUILD`t3`tunexpected`tnone`tnone`t0`tnone`tnone" }
    }
    [Console]::Error.WriteLine($safeDiagnostic)
    exit 1
}
