import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { validateMetadataWire, validateSdkRegistrationMetadataWire } from './windows-storage-loader-metadata.mjs';

const digest = 'a'.repeat(64);
const wire = value => Buffer.from(`${JSON.stringify(value)}\n`);
const record = (view = 'x64', productCode = '{01234567-89AB-CDEF-0123-456789ABCDEF}') => ({
  view, productCode, displayName: 'Windows Software Development Kit - Windows 10.0.26100.0',
  displayVersion: '10.1.26100.1', publisher: 'Microsoft Corporation',
});
const metadata = () => ({
  scope: 'windows-storage-loader-metadata', schema: 2, state: 'blocked', reason: 'tool-provenance-unproven',
  selectionAuthority: false, buildAuthority: false, nativeAuthority: false, sourceSelectionSha256: digest,
  host: { powershellVersion: '5.1.26100.1', windowsVersion: '10.0.26100.1', architecture: 'x64',
    profile: 'winps-inbox-only', securityCommand: 'captured-inbox-Get-AuthenticodeSignature' },
  installations: [], sdkVersions: [], files: [], sdkCoverage: 'prerequisite-samples-not-consumed-closure',
  sdkRegistration: { version: 1, status: 'single-candidate', reason: 'none', records: [record()] },
});

test('wire v2 accepts one bounded registration clue while v1 remains closed', () => {
  const value = metadata();
  assert.deepEqual(validateSdkRegistrationMetadataWire(wire(value), digest), value);
  assert.throws(() => validateMetadataWire(wire(value), digest), /metadata/);
  const old = structuredClone(value); old.schema = 1; delete old.sdkRegistration;
  assert.deepEqual(validateMetadataWire(wire(old), digest), old);
  assert.throws(() => validateSdkRegistrationMetadataWire(wire(old), digest), /metadata/);
});

test('wire v2 refuses unknown context, authority, status and record fields', () => {
  for (const change of [
    value => { value.untrusted = true; }, value => { value.host.untrusted = true; },
    value => { value.selectionAuthority = true; }, value => { value.buildAuthority = true; },
    value => { value.nativeAuthority = true; }, value => { value.schema = 3; },
    value => { value.sourceSelectionSha256 = 'b'.repeat(64); },
    value => { value.sdkRegistration.extra = true; },
    value => { value.sdkRegistration.records[0].extra = true; },
    value => { value.sdkRegistration.records[0].productCode = '{01234567-89ab-CDEF-0123-456789ABCDEF}'; },
    value => { value.sdkRegistration.records[0].view = 'HKCU'; },
    value => { value.sdkRegistration.records[0].displayName += '\n'; },
    value => { value.sdkRegistration.status = 'selected'; },
    value => { value.sdkRegistration.reason = 'none'; value.sdkRegistration.status = 'blocked'; },
    value => { value.sdkRegistration.records = Array(9).fill(record()); },
    value => { value.sdkRegistration.records[0].displayVersion = 'x'.repeat(129); },
  ]) {
    const value = metadata(); change(value);
    assert.throws(() => validateSdkRegistrationMetadataWire(wire(value), digest), /metadata/);
  }
});

test('wire v2 status cardinality and malformed full wire refuse without partial clues', () => {
  const absent = metadata(); absent.sdkRegistration = { version: 1, status: 'absent', reason: 'none', records: [] };
  assert.equal(validateSdkRegistrationMetadataWire(wire(absent), digest).sdkRegistration.status, 'absent');
  const ambiguous = metadata(); ambiguous.sdkRegistration = { version: 1, status: 'ambiguous', reason: 'none',
    records: [record('x64'), record('x86')] };
  assert.equal(validateSdkRegistrationMetadataWire(wire(ambiguous), digest).sdkRegistration.records.length, 2);
  const blocked = metadata(); blocked.sdkRegistration = { version: 1, status: 'blocked', reason: 'link', records: [] };
  assert.equal(validateSdkRegistrationMetadataWire(wire(blocked), digest).sdkRegistration.reason, 'link');
  for (const change of [
    value => { value.sdkRegistration.status = 'absent'; },
    value => { value.sdkRegistration.status = 'ambiguous'; },
    value => { value.sdkRegistration.status = 'blocked'; value.sdkRegistration.reason = 'link'; },
    value => { value.state = 'observed'; value.reason = 'none'; },
  ]) {
    const value = metadata(); change(value);
    assert.throws(() => validateSdkRegistrationMetadataWire(wire(value), digest), /metadata/);
  }
  for (const bytes of [Buffer.from('{}\n{}\n'), Buffer.from(' ') , Buffer.alloc(1048577)]) {
    assert.throws(() => validateSdkRegistrationMetadataWire(bytes, digest), /metadata/);
  }
});

test('fixed native binding declarations and absent executable fallback are visible in source', () => {
  const source = readFileSync(fileURLToPath(new URL('./windows-storage-loader-metadata.ps1', import.meta.url)), 'utf8');
  for (const name of ['RegOpenKeyExW', 'RegEnumKeyExW', 'RegQueryValueExW', 'RegCloseKey']) {
    assert.match(source, new RegExp(`@\\('${name}', \\[type\\[\\]\\]`));
  }
  assert.match(source, /RegOpenKeyExW', \[type\[\]\]@\(\[IntPtr\], \[string\], \[uint32\], \[uint32\], \[IntPtr\]\.MakeByRefType\(\)\)/);
  assert.match(source, /RegEnumKeyExW', \[type\[\]\]@\(\[IntPtr\], \[uint32\], \[Text\.StringBuilder\], \[uint32\]\.MakeByRefType\(\)/);
  assert.match(source, /RegQueryValueExW', \[type\[\]\]@\(\[IntPtr\], \[string\], \[IntPtr\], \[uint32\]\.MakeByRefType\(\), \[byte\[\]\], \[uint32\]\.MakeByRefType\(\)\)/);
  assert.match(source, /RegCloseKey', \[type\[\]\]@\(\[IntPtr\]\)/);
  assert.match(source, /DefinePInvokeMethod\(\$declaration\[0\]/);
  assert.match(source, /SetImplementationFlags/);
  assert.match(source, /MethodImplAttributes\]::PreserveSig/);
  assert.match(source, /CallingConvention\]::Winapi, \[Runtime\.InteropServices\.CharSet\]::Unicode/);
  assert.match(source, /MethodAttributes\]::Private/);
  assert.match(source, /C:\\Windows\\System32\\advapi32\.dll/);
  assert.match(source, /REG_OPTION_OPEN_LINK/);
  assert.doesNotMatch(source, /Wow6432Node|Add-Type|\bcsc(?:\.exe)?\b|\breg\.exe\b/);
  const collector = readFileSync(fileURLToPath(new URL('./windows-storage-loader-metadata.mjs', import.meta.url)), 'utf8');
  assert.match(collector, /const metadata = validateSdkRegistrationMetadataWire\(captured\.bytes, selectedSha256\)/);
});

const psPath = fileURLToPath(new URL('./windows-storage-loader-metadata.ps1', import.meta.url));
const ps = String.raw`
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$tokens = $null; $errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($env:SDK_TEST_SOURCE, [ref]$tokens, [ref]$errors)
if ($errors.Count -ne 0) { throw 'ast' }
foreach ($name in @('Assert-SdkDeadline', 'Read-SdkRegistryString', 'Get-SdkNameHash', 'Invoke-SdkRegistrationObservation')) {
  $definition = $ast.FindAll({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq $name }, $true)
  if ($definition.Count -ne 1) { throw 'definition' }
  Invoke-Expression $definition[0].Extent.Text
}
$fixture = ConvertFrom-Json $env:SDK_TEST_FIXTURE -AsHashtable
$state = @{ handles = @{}; next = 1; passes = @{ x64 = 0; x86 = 0 }; opens = @(); closes = @(); queries = @(); queryCaps = @(); enums = 0; tick = 0L; clockCalls = 0 }
$api = @{
  Open = { param([IntPtr]$h, [string]$path, [uint32]$option, [uint32]$access)
    if ($option -ne 8) { throw 'rawcanary' }
    if ($h -eq [IntPtr]::new(-2147483646)) {
      if ($path -cne 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall') { throw 'rawcanary' }
      $view = if ($access -eq 0x109) { 'x64' } elseif ($access -eq 0x209) { 'x86' } else { throw 'rawcanary' }
      $pass = $state.passes[$view]; $state.passes[$view]++
      $item = @{ view = $view; pass = $pass; root = $true }
    } else {
      $parent = $state.handles[[int]$h]
      if ($null -eq $parent -or -not $parent.root -or $access -ne $(if ($parent.view -ceq 'x64') { 0x101 } else { 0x201 })) { throw 'rawcanary' }
      $item = @{ view = $parent.view; pass = $parent.pass; root = $false; key = $path }
    }
    $id = $state.next; $state.next++
    $state.handles[$id] = $item
    $state.opens += @{ view = $item.view; root = $item.root; option = $option; access = $access }
    return @{ code = 0; handle = [IntPtr]::new($id) }
  }.GetNewClosure()
  Enum = { param([IntPtr]$h, [uint32]$index)
    $state.enums++
    $item = $state.handles[[int]$h]
    if ($null -eq $item -or -not $item.root) { throw 'rawcanary' }
    $rows = @($fixture.passes[$item.pass][$item.view])
    if ($fixture.enumMoreData -and $index -eq 0) { return @{ code = 234; name = 'rawcanary' } }
    if ($fixture.sentinelExtra -and $index -eq 512) { return @{ code = 0; name = 'overflow' } }
    if ($index -ge $rows.Length) { return @{ code = 259; name = '' } }
    return @{ code = 0; name = [string]$rows[$index].key }
  }.GetNewClosure()
  Query = { param([IntPtr]$h, [string]$name, [int]$capacity)
    $item = $state.handles[[int]$h]
    if ($null -eq $item) { throw 'rawcanary' }
    $state.queries += $name
    $state.queryCaps += @{ name = $name; capacity = $capacity }
    if ($item.root) {
      if ($name -cne 'SymbolicLinkValue') { throw 'rawcanary' }
      if ($fixture.rootLink) { return @{ code = 0; type = 6; bytes = 2; data = [byte[]]@(0, 0) } }
      return @{ code = 2; type = 0; bytes = 0; data = [byte[]]@() }
    }
    $row = @($fixture.passes[$item.pass][$item.view]) | Where-Object { $_.key -ceq $item.key } | Select-Object -First 1
    if ($name -ceq 'SymbolicLinkValue') {
      if ($row.link) { return @{ code = 234; type = 6; bytes = 30; data = [byte[]]@() } }
      return @{ code = 2; type = 0; bytes = 0; data = [byte[]]@() }
    }
    if ($row.throwCanary) { throw 'rawcanary' }
    if ($row.moreData -ceq $name) { return @{ code = 234; type = 1; bytes = $capacity + 2; data = [byte[]]@() } }
    if ($row.missing -ceq $name -or $null -eq $row[$name]) { return @{ code = 2; type = 0; bytes = 0; data = [byte[]]@() } }
    $data = [Text.Encoding]::Unicode.GetBytes(([string]$row[$name]) + [char]0)
    if ($row.unterminated -ceq $name) { $data = [Text.Encoding]::Unicode.GetBytes([string]$row[$name]) }
    if ($row.oddBytes -ceq $name) { $data = [byte[]]@($data[0..($data.Length - 2)]) }
    if ($row.loneSurrogate -ceq $name) { $data = [byte[]]@(0, 216, 0, 0) }
    $type = if ($row.expand -ceq $name) { 2 } elseif ($row.regLink -ceq $name) { 6 } else { 1 }
    return @{ code = 0; type = $type; bytes = $data.Length; data = [byte[]]$data }
  }.GetNewClosure()
  Close = { param([IntPtr]$h)
    $id = [int]$h
    if (-not $state.handles.ContainsKey($id)) { throw 'rawcanary' }
    $state.closes += $id
    [void]$state.handles.Remove($id)
    if ($fixture.closeFailure) { return 5 }
    return 0
  }.GetNewClosure()
}
$now = { $state.clockCalls++
  $state.tick += $(if ($fixture.slowClock) { 3000L } elseif ($fixture.slowAtCall -eq $state.clockCalls) { 6000L } else { 0L })
  return [long]$state.tick
}.GetNewClosure()
$result = Invoke-SdkRegistrationObservation $api $now
[Console]::Out.WriteLine((ConvertTo-Json -InputObject @{ result = $result; opens = $state.opens; closes = $state.closes;
  remaining = $state.handles.Count; queries = $state.queries; queryCaps = $state.queryCaps; enums = $state.enums } -Depth 12 -Compress))
`;
const sdkName = 'Windows Software Development Kit - Windows 10.0.26100.0';
const row = (key = '{01234567-89AB-CDEF-0123-456789ABCDEF}') => ({ key, DisplayName: sdkName,
  DisplayVersion: '10.1.26100.1', Publisher: 'Microsoft Corporation' });
const fixture = (x64 = [row()], x86 = []) => ({ passes: [{ x64, x86 }, { x64, x86 }] });
function observe(value) {
  const result = spawnSync('/Users/adam/homebrew/bin/pwsh', ['-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand',
    Buffer.from(ps, 'utf16le').toString('base64')], { encoding: 'utf8', timeout: 30000, maxBuffer: 1024 * 1024,
    env: { SDK_TEST_SOURCE: psPath, SDK_TEST_FIXTURE: JSON.stringify(value) } });
  assert.equal(result.error, undefined);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '');
  return JSON.parse(result.stdout);
}

test('pure registry query uses both explicit views, two passes and closes all owned handles', () => {
  const got = observe(fixture());
  assert.equal(got.result.section.status, 'single-candidate');
  assert.equal(got.result.section.records.length, 1);
  assert.equal(got.result.section.records[0].productCode, '{01234567-89AB-CDEF-0123-456789ABCDEF}');
  assert.equal(got.opens.filter(open => open.root).length, 4);
  assert.deepEqual(new Set(got.opens.filter(open => open.root).map(open => open.access)), new Set([0x109, 0x209]));
  assert.deepEqual(new Set(got.opens.filter(open => !open.root).map(open => open.access)), new Set([0x101]));
  assert.equal(got.closes.length, got.opens.length);
  assert.equal(got.remaining, 0);
  assert.equal(got.queries.filter(name => name === 'DisplayVersion').length, 2);
  assert.deepEqual(new Set(got.queryCaps.map(query => `${query.name}:${query.capacity}`)),
    new Set(['SymbolicLinkValue:2', 'DisplayName:1024', 'DisplayVersion:256', 'Publisher:512']));
});

test('pure registry query classifies absent, ambiguous, non-GUID and observed drift', () => {
  assert.equal(observe(fixture([], [])).result.section.status, 'absent');
  const unnamed = observe(fixture([{ key: 'OtherProduct' }]));
  assert.equal(unnamed.result.section.status, 'absent');
  assert.equal(unnamed.queries.filter(name => name === 'DisplayVersion').length, 0);
  assert.equal(observe(fixture([row()], [row()])).result.section.status, 'ambiguous');
  const nonGuid = observe(fixture([row('private-subkey-canary')])).result.section;
  assert.equal(nonGuid.status, 'single-candidate');
  assert.equal(nonGuid.records[0].productCode, null);
  assert.doesNotMatch(JSON.stringify(nonGuid), /private-subkey-canary/);
  const changed = fixture(); changed.passes[1].x64 = [row('different-key')];
  assert.deepEqual(observe(changed).result.section, { version: 1, status: 'blocked', reason: 'changed', records: [] });
  const changedName = fixture(); changedName.passes[1].x64 = [{ key: row().key, DisplayName: 'Other' }];
  assert.equal(observe(changedName).result.section.reason, 'changed');
  assert.equal(observe(fixture([row(), row()])).result.section.reason, 'malformed');
  assert.equal(observe(fixture([row(), row(row().key.toLowerCase())])).result.section.reason, 'malformed');
});

test('pure registry query refuses links, malformed values, changed bounds and close errors', () => {
  for (const [caseIndex, [change, reason]] of [
    [v => { v.passes[0].x64[0].link = true; }, 'link'],
    [v => { v.passes[0].x64[0].moreData = 'DisplayName'; }, 'bounds'],
    [v => { v.passes[0].x64[0].unterminated = 'DisplayVersion'; }, 'malformed'],
    [v => { v.passes[0].x64[0].oddBytes = 'Publisher'; }, 'malformed'],
    [v => { v.passes[0].x64[0].loneSurrogate = 'Publisher'; }, 'malformed'],
    [v => { v.passes[0].x64[0].DisplayName = `${sdkName}\0extra`; }, 'malformed'],
    [v => { v.passes[0].x64[0].expand = 'DisplayName'; }, 'malformed'],
    [v => { v.passes[0].x64[0].regLink = 'DisplayName'; }, 'malformed'],
    [v => { v.passes[0].x64[0].missing = 'DisplayVersion'; }, 'unreadable'],
    [v => { v.passes[0].x64[0].throwCanary = true; }, 'unreadable'],
    [v => { v.rootLink = true; }, 'link'],
    [v => { v.closeFailure = true; }, 'closure'],
    [v => { v.enumMoreData = true; }, 'bounds'],
    [v => { v.slowClock = true; }, 'bounds'],
    [v => { v.slowAtCall = 8; }, 'bounds'],
  ].entries()) {
    const v = fixture(); change(v);
    const got = observe(v);
    assert.equal(got.result.section.status, 'blocked', `case ${caseIndex}`);
    assert.equal(got.result.section.reason, reason, `case ${caseIndex}`);
    assert.deepEqual(got.result.section.records, []);
    assert.doesNotMatch(JSON.stringify(got.result), /private-subkey-canary|rawcanary/);
    assert.equal(got.remaining, 0);
  }
});

test('pure query caps key sentinel, raw bytes, and matching records', () => {
  const exactly512 = fixture(Array.from({ length: 512 }, (_, i) => ({ key: `Other${i}`, DisplayName: 'Other' })));
  assert.equal(observe(exactly512).result.section.status, 'absent');
  exactly512.sentinelExtra = true;
  assert.equal(observe(exactly512).result.section.reason, 'bounds');
  const raw = fixture(Array.from({ length: 140 }, (_, i) => ({ key: `Other${i}`, DisplayName: 'x'.repeat(500) })));
  assert.equal(observe(raw).result.section.reason, 'bounds');
  const many = fixture(Array.from({ length: 9 }, (_, i) => row(`{00000000-0000-0000-0000-${String(i).padStart(12, '0')}}`)));
  assert.equal(observe(many).result.section.reason, 'bounds');
});
