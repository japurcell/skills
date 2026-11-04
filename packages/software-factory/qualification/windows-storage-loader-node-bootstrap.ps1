# Fixed source-only bootstrap. The root-selected hosted OS/source profile is external.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($args.Count -ne 0 -or [string]::IsNullOrEmpty($env:FACTORY_PRIVATE_ROOT)) { throw 'Fixed bootstrap context refused' }
$private = [IO.Path]::Combine($env:FACTORY_PRIVATE_ROOT, 'factory-metadata-collect-node-' + [Guid]::NewGuid().ToString('N'))
if ([IO.Directory]::Exists($private)) { throw 'Private runtime already exists' }
[void][IO.Directory]::CreateDirectory($private)
$archivePath = [IO.Path]::Combine($private, 'node-v24.22.1-win-x64.zip')
$handler = [Net.Http.HttpClientHandler]::new()
$handler.AllowAutoRedirect = $false
$client = [Net.Http.HttpClient]::new($handler)
$deadline = [Threading.CancellationTokenSource]::new(120000)
$response = $null; $inputStream = $null; $outputStream = $null; $archiveStream = $null; $zip = $null; $sha = $null
try {
    $response = $client.GetAsync('https://nodejs.org/download/release/v24.22.1/node-v24.22.1-win-x64.zip', [Net.Http.HttpCompletionOption]::ResponseHeadersRead, $deadline.Token).GetAwaiter().GetResult()
    if ([int]$response.StatusCode -ne 200) { throw 'Fixed Node archive unavailable' }
    $inputStream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    $outputStream = [IO.FileStream]::new($archivePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $buffer = [byte[]]::new(65536); $total = 0L
    while (($size = $inputStream.ReadAsync($buffer, 0, $buffer.Length, $deadline.Token).GetAwaiter().GetResult()) -ne 0) {
        $total += $size
        if ($total -gt 150000000) { throw 'Fixed Node archive bounds' }
        $outputStream.Write($buffer, 0, $size)
    }
    $outputStream.Dispose(); $outputStream = $null
    $archiveStream = [IO.FileStream]::new($archivePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $sha = [Security.Cryptography.SHA256]::Create()
    $archiveHash = ([BitConverter]::ToString($sha.ComputeHash($archiveStream))).Replace('-', '').ToLowerInvariant()
    if ($archiveHash -cne 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5') { throw 'Fixed Node archive integrity' }
    $archiveStream.Position = 0
    $zip = [IO.Compression.ZipArchive]::new($archiveStream, [IO.Compression.ZipArchiveMode]::Read, $true)
    if ($zip.Entries.Count -gt 4096) { throw 'Fixed Node archive entries' }
    $entries = @($zip.Entries | Where-Object { $_.FullName -ceq 'node-v24.22.1-win-x64/node.exe' })
    if ($entries.Count -ne 1 -or $entries[0].Length -lt 1 -or $entries[0].Length -gt 134217728) { throw 'Fixed Node executable entry' }
    # No broad extraction: only the authenticated fixed node.exe entry is written.
    $runtime = [IO.Path]::Combine($private, 'node-v24.22.1-win-x64')
    [void][IO.Directory]::CreateDirectory($runtime)
    $binary = [IO.Path]::Combine($runtime, 'node.exe')
    $nodeInput = $entries[0].Open()
    $nodeOutput = [IO.FileStream]::new($binary, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $nodeInput.CopyTo($nodeOutput) } finally { $nodeInput.Dispose(); $nodeOutput.Dispose() }
    $nodeStream = [IO.FileStream]::new($binary, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        $nodeHash = ([BitConverter]::ToString($sha.ComputeHash($nodeStream))).Replace('-', '').ToLowerInvariant()
        if ($nodeStream.Length -ne $entries[0].Length -or $nodeHash -cne 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5') { throw 'Fixed Node executable integrity' }
    } finally { $nodeStream.Dispose() }
    $location = [IO.Path]::Combine($env:FACTORY_PRIVATE_ROOT, 'factory-metadata-collect-node-location.txt')
    $locationStream = [IO.FileStream]::new($location, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $locationBytes = [Text.UTF8Encoding]::new($false).GetBytes($private)
        $locationStream.Write($locationBytes, 0, $locationBytes.Length)
    } finally { $locationStream.Dispose() }
} finally {
    foreach ($resource in @($zip, $archiveStream, $outputStream, $inputStream, $response, $sha, $deadline, $client, $handler)) {
        if ($null -ne $resource) { $resource.Dispose() }
    }
}
