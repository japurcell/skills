import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Invoke with the exact pinned Windows x64 Node binary before the ETW probe.
// This exercises the real held-fixture bridge without starting ETW or retaining an ETL.
async function qualifyForeignPidRejection() {
  assert.equal(process.platform, 'win32');
  assert.equal(process.arch, 'x64');
  assert.equal(process.version, 'v24.22.1');
  assert.ok(isAbsolute(process.execPath));
  const source = fileURLToPath(new URL('./windows-etw-probe.cs', import.meta.url));
  const fixedFixture = fileURLToPath(new URL('./windows-etw-child-fixture.cjs', import.meta.url));
  assert.ok(existsSync(source) && existsSync(fixedFixture));
  assert.ok(process.env.SystemRoot && isAbsolute(process.env.SystemRoot));
  const powershell = join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  assert.ok(existsSync(powershell));

  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-foreign-child-'));
  const request = join(evidence, 'request');
  const response = join(evidence, 'response');
  const fixture = join(evidence, 'hostile.cjs');
  const driver = join(evidence, 'check.ps1');
  let bridge, foreign, closed;
  try {
    const digest = createHash('sha256').update(readFileSync(process.execPath)).digest('hex');
    writeFileSync(fixture, `const fs=require('node:fs');fs.writeFileSync(${JSON.stringify(request)},'ready');` +
      `const wait=setInterval(()=>{if(fs.existsSync(${JSON.stringify(response)})){` +
      `clearInterval(wait);process.stdout.write(fs.readFileSync(${JSON.stringify(response)},'utf8'));` +
      `process.stdin.resume();process.stdin.on('end',()=>process.exit(0));}},10);` +
      `setTimeout(()=>process.exit(2),12000);`);
    writeFileSync(driver, `param($Source,$Node,$Evidence,$Fixture,$Digest)
$ErrorActionPreference='Stop'
Add-Type -LiteralPath $Source
$type=[WindowsEtwProbe]
$flags=[Reflection.BindingFlags]'NonPublic,Static'
$watch=[Diagnostics.Stopwatch]::StartNew()
$type.GetMethod('HoldPinnedFile',$flags).Invoke($null,@($Node,$Digest,$watch)) | Out-Null
try {
  try { $type.GetMethod('RunFixture',$flags).Invoke($null,@($Node,$Evidence,$Fixture,$watch)) | Out-Null
        throw 'foreign PID was accepted' }
  catch {
    $cause=$_.Exception
    while($cause.InnerException){$cause=$cause.InnerException}
    if($cause.Message -cne 'fixture child is not live child of held root'){throw}
  }
  [Console]::WriteLine('PARENT_REJECTED')
} finally {
  $type.GetMethod('StopFixture',$flags).Invoke($null,@()) | Out-Null
  $pin=$type.GetField('PinnedFile',$flags).GetValue($null)
  $root=$type.GetField('RootProcess',$flags).GetValue($null)
  $pinHandle=$pin.SafeFileHandle
  $rootHandle=$root.SafeHandle
  $closed=$type.GetMethod('CloseOwnedResources',$flags).Invoke($null,@())
  if(-not $closed -or -not $pinHandle.IsClosed -or -not $rootHandle.IsClosed -or
     $type.GetField('ChildHandle',$flags).GetValue($null) -ne [IntPtr]::Zero){throw 'owned handles not closed'}
}
`);
    bridge = spawn(powershell, ['-NoProfile', '-NonInteractive', '-File', driver,
      source, process.execPath, evidence, fixture, digest], { stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '', hadError = false;
    bridge.stdout.on('data', (chunk) => { output = (output + chunk).slice(0, 1024); });
    bridge.stderr.on('data', () => { hadError = true; });
    closed = new Promise((resolve) => {
      bridge.once('close', resolve);
      bridge.once('error', () => resolve(-1));
    });
    const deadline = Date.now() + 7000;
    while (!existsSync(request) && Date.now() < deadline && bridge.exitCode === null)
      await new Promise((resolve) => setTimeout(resolve, 20));
    assert.ok(existsSync(request));
    foreign = spawn(process.execPath, ['-e', 'setTimeout(()=>{},30000)'],
      { stdio: 'ignore', windowsHide: true });
    foreign.once('error', () => {});
    assert.ok(foreign.pid > 0);
    writeFileSync(response, `${foreign.pid}\n`);
    const result = await Promise.race([closed,
      new Promise((_, reject) => setTimeout(() => reject(new Error('bridge timeout')), 8000))]);
    assert.equal(result, 0);
    assert.match(output, /^PARENT_REJECTED\r?\n$/);
    assert.equal(hadError, false);
    assert.doesNotThrow(() => process.kill(foreign.pid, 0));
  } finally {
    if (bridge?.exitCode === null) {
      bridge.kill();
      await Promise.race([closed, new Promise((resolve) => setTimeout(resolve, 2000))]);
    }
    if (foreign?.exitCode === null) foreign.kill();
    // The native check never opens ETW; remove any unexpected trace before output.
    rmSync(evidence, { recursive: true, force: true });
  }
}

try {
  await qualifyForeignPidRejection();
  process.stdout.write('HELD_NATIVE_PARENT_REJECTION_OK\n');
} catch {
  process.stderr.write('HELD_NATIVE_FAIL\n');
  process.exitCode = 1;
}
