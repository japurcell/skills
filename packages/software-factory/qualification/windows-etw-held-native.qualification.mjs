import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';

async function waitForBridge(closed, milliseconds) {
  let timer;
  try {
    return await Promise.race([closed, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error('bridge timeout')), milliseconds);
    })]);
  } finally { clearTimeout(timer); }
}

// Invoke with the exact pinned Windows x64 Node binary independently of ETW.
// This exercises the real held-fixture bridge without starting ETW or retaining an ETL.
async function qualifyHeldFixtures() {
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
    const result = await waitForBridge(closed, 8000);
    assert.equal(result, 0);
    assert.match(output, /^PARENT_REJECTED\r?\n$/);
    assert.equal(hadError, false);
    assert.doesNotThrow(() => process.kill(foreign.pid, 0));
    process.stdout.write('HELD_NATIVE_PARENT_REJECTION_OK\n');

    // Exercise the unchanged positive path separately from ETW decoding. Never
    // print exception text, paths, file identities or other ambient metadata.
    writeFileSync(driver, `param($Source,$Node,$Evidence,$Fixture,$Digest)
$ErrorActionPreference='Stop'
Add-Type -LiteralPath $Source
$type=[WindowsEtwProbe]
$flags=[Reflection.BindingFlags]'NonPublic,Static'
$watch=[Diagnostics.Stopwatch]::StartNew()
$category='other'
$passed=$false
try {
  $type.GetMethod('HoldPinnedFile',$flags).Invoke($null,@($Node,$Digest,$watch)) | Out-Null
  $type.GetMethod('RunFixture',$flags).Invoke($null,@($Node,$Evidence,$Fixture,$watch)) | Out-Null
  $passed=$true
} catch {
  $cause=$_.Exception
  while($cause.InnerException){$cause=$cause.InnerException}
  $category=switch -Exact ($cause.Message) {
    'fixture PID malformed' {'pid-shape'}
    'fixture PID over cap' {'pid-cap'}
    'fixture PID line unavailable' {'pid-unavailable'}
    'fixture child PID invalid' {'child-pid'}
    'fixture child handle invalid or exited' {'child-handle'}
    'fixture child timing invalid' {'child-timing'}
    'process handle image differs from pin' {'image-path'}
    'process image file identity differs from pin' {'image-file'}
    'fixture child is not live child of held root' {'parent'}
    'held child exit unobserved' {'child-exit'}
    'root fixture exit unobserved' {'root-exit'}
    'held fixture exit or output invalid' {'exit-output'}
    default {'other'}
  }
} finally {
  try {
    if(-not $type.GetMethod('StopFixture',$flags).Invoke($null,@())){$passed=$false;$category='stop'}
  } finally {
    if(-not $type.GetMethod('CloseOwnedResources',$flags).Invoke($null,@())){$passed=$false;$category='close'}
  }
}
if($passed){[Console]::WriteLine('POSITIVE_OK');exit 0}
$step=$type.GetMethod('ReadFixtureStep',$flags).Invoke($null,@())
if($step -cnotmatch '^(not-started|start|root-handle|root-timing|root-image|pid-line|child-handle|child-timing|child-image|parent|release|child-wait|root-wait|exit-output|complete)$'){$step='other'}
[Console]::WriteLine('POSITIVE_FAIL '+$category+' '+$step)
exit 1
`);
    bridge = spawn(powershell, ['-NoProfile', '-NonInteractive', '-File', driver,
      source, process.execPath, evidence, fixedFixture, digest], { stdio: ['ignore', 'pipe', 'pipe'] });
    output = ''; hadError = false;
    let overflow = false;
    bridge.stdout.on('data', (chunk) => {
      if (Buffer.byteLength(output) + chunk.length > 1024) overflow = true;
      output = (output + chunk).slice(0, 1024);
    });
    bridge.stderr.on('data', () => { hadError = true; });
    closed = new Promise((resolve) => {
      bridge.once('close', resolve);
      bridge.once('error', () => resolve(-1));
    });
    const positiveResult = await waitForBridge(closed, 35000);
    if (!overflow && !hadError && positiveResult === 1 &&
        /^POSITIVE_FAIL (?:pid-shape|pid-cap|pid-unavailable|child-pid|child-handle|child-timing|image-path|image-file|parent|child-exit|root-exit|exit-output|other|stop|close) (?:not-started|start|root-handle|root-timing|root-image|pid-line|child-handle|child-timing|child-image|parent|release|child-wait|root-wait|exit-output|complete|other)\r?\n$/.test(output))
      process.stderr.write(`HELD_NATIVE_${output.trim()}\n`);
    assert.equal(positiveResult, 0);
    assert.equal(overflow, false);
    assert.equal(hadError, false);
    assert.match(output, /^POSITIVE_OK\r?\n$/);
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
  await qualifyHeldFixtures();
  process.stdout.write('HELD_NATIVE_POSITIVE_OK\n');
} catch {
  process.stderr.write('HELD_NATIVE_FAIL\n');
  process.exitCode = 1;
}
