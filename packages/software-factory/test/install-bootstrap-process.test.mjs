import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const script = resolve(fileURLToPath(new URL('../../../skills/software-factory/scripts/install.py', import.meta.url)));
const python = process.env.FACTORY_TEST_PYTHON ?? 'python3';
const prerequisite = spawnSync(python, ['-c', 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'], { encoding: 'utf8' });
assert.equal(prerequisite.status, 0, `Python 3.11+ prerequisite failed: ${prerequisite.error?.message ?? prerequisite.stderr}`);

test('private stage cleanup preserves an unexpected foreign file', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-ownership-')));
  try {
    const driver = `import importlib.util,os,sys\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `stage=m.PrivateStage(); stage.mkdir('node'); owned=stage.root/'node'/'owned'; foreign=stage.root/'foreign'; stage.create('node/owned').close(); foreign.write_text('keep')\n` +
      `try: stage.cleanup()\n` +
      `except ValueError: pass\n` +
      `else: raise AssertionError('foreign file was silently removed')\n` +
      `assert foreign.read_text()=='keep' and not owned.exists()\n` +
      `foreign.unlink(); stage.root.rmdir(); print('preserved')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'preserved');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator refuses inherited descendant pipes and preserves uncertain stages', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-process-')));
  try {
    const driver = `import importlib.util,os,subprocess,sys,threading,time\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for escaped in (False,True):\n` +
      ` stage=m.PrivateStage()\n` +
      ` child='import time; time.sleep(2)'\n` +
      ` program='import subprocess,sys; subprocess.Popen([sys.executable,"-c",'+repr(child)+'],stdout=subprocess.DEVNULL,start_new_session='+repr(escaped)+'); print("{}")'\n` +
      ` begin=time.monotonic()\n` +
      ` try: m.bounded_child([sys.executable,'-c',program],stage,1)\n` +
      ` except ValueError: pass\n` +
      ` else: raise AssertionError('receipt returned with inherited pipe open')\n` +
      ` assert time.monotonic()-begin<2 and stage.preserved and stage.root.exists()\n` +
      ` if escaped:\n` +
      `  assert any(t.name.startswith('factory-install-drain') for t in threading.enumerate())\n` +
      ` if any(t.name.startswith('factory-install-drain') for t in threading.enumerate()): time.sleep(2.2)\n` +
      ` assert not any(t.name.startswith('factory-install-drain') for t in threading.enumerate())\n` +
      ` stage.cleanup()\n` +
      `with m.private_stage() as managed: managed.preserved=True\n` +
      `assert managed.root.exists()\n` +
      `managed.cleanup()\n` +
      `print('refused and owned cleanup completed')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'refused and owned cleanup completed');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator preserves its stage if either drain thread fails to start', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-thread-fault-')));
  try {
    const driver = `import importlib.util,subprocess,sys,threading\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for fault_at in (1,2):\n` +
      ` owned=[]; real_popen=subprocess.Popen; real_start=threading.Thread.start; starts=[0]; stage=None\n` +
      ` def capture(*args,**kwargs):\n` +
      `  process=real_popen(*args,**kwargs); owned.append(process); return process\n` +
      ` def fault(self):\n` +
      `  if self.name.startswith('factory-install-drain'):\n` +
      `   starts[0]+=1\n` +
      `   if starts[0]==fault_at: raise RuntimeError('controlled thread start failure')\n` +
      `  return real_start(self)\n` +
      ` try:\n` +
      `  with m.private_stage() as stage:\n` +
      `   with patch.object(m.subprocess,'Popen',capture),patch.object(threading.Thread,'start',fault):\n` +
      `    try: m.bounded_child([sys.executable,'-c','import time; time.sleep(5)'],stage,1)\n` +
      `    except RuntimeError: pass\n` +
      `    else: raise AssertionError('thread fault produced a receipt')\n` +
      `  assert stage.preserved and stage.root.exists() and owned[0].poll() is not None\n` +
      ` finally:\n` +
      `  for process in owned:\n` +
      `   if process.poll() is None: process.kill()\n` +
      `   process.wait(timeout=5); process.stdout.close(); process.stderr.close()\n` +
      `  if stage is not None and stage.root.exists(): stage.cleanup()\n` +
      `print('both startup faults refused without a surviving child')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'both startup faults refused without a surviving child');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator preserves its stage if waiting or joining raises unexpectedly', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-wait-fault-')));
  try {
    const driver = `import importlib.util,subprocess,sys,threading\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for mode in ('wait','join'):\n` +
      ` owned=[]; real_popen=subprocess.Popen; real_wait=subprocess.Popen.wait; real_join=threading.Thread.join; calls=[0]; stage=None\n` +
      ` def capture(*args,**kwargs):\n` +
      `  process=real_popen(*args,**kwargs); owned.append(process); return process\n` +
      ` def fault_wait(self,*args,**kwargs):\n` +
      `  if self in owned and calls[0]==0:\n` +
      `   calls[0]+=1; raise RuntimeError('controlled wait failure')\n` +
      `  return real_wait(self,*args,**kwargs)\n` +
      ` def fault_join(self,*args,**kwargs):\n` +
      `  if self.name.startswith('factory-install-drain'): raise ValueError('controlled join failure')\n` +
      `  return real_join(self,*args,**kwargs)\n` +
      ` try:\n` +
      `  with m.private_stage() as stage:\n` +
      `   with patch.object(m.subprocess,'Popen',capture):\n` +
      `    target=real_popen if mode=='wait' else threading.Thread\n` +
      `    attribute='wait' if mode=='wait' else 'join'\n` +
      `    replacement=fault_wait if mode=='wait' else fault_join\n` +
      `    with patch.object(target,attribute,replacement):\n` +
      `     try: m.bounded_child([sys.executable,'-c','print("{}")'],stage,1)\n` +
      `     except RuntimeError: pass\n` +
      `     else: raise AssertionError('unexpected lifecycle fault produced a receipt')\n` +
      `  assert stage.preserved and stage.root.exists() and owned[0].poll() is not None\n` +
      ` finally:\n` +
      `  for process in owned:\n` +
      `   if process.poll() is None: process.kill()\n` +
      `   process.wait(timeout=5); process.stdout.close(); process.stderr.close()\n` +
      `  if stage is not None and stage.root.exists(): stage.cleanup()\n` +
      `print('wait and join faults preserved owned stages')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'wait and join faults preserved owned stages');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('validator accepts pipe completion between event checks', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-event-race-')));
  try {
    const driver = `import builtins,importlib.util,os,sys,threading\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `started=[]; real_start=threading.Thread.start; absent=object()\n` +
      `def capture_start(self):\n` +
      ` result=real_start(self)\n` +
      ` if self.name.startswith('factory-install-drain'): started.append(self)\n` +
      ` return result\n` +
      `def complete_before_next(iterator,default=absent):\n` +
      ` assert len(started)==2\n` +
      ` for thread in started: thread.join(timeout=3)\n` +
      ` assert all(not thread.is_alive() for thread in started)\n` +
      ` if default is absent: return builtins.next(iterator)\n` +
      ` return builtins.next(iterator,default)\n` +
      `def run(stage):\n` +
      ` started.clear()\n` +
      ` with patch.object(threading.Thread,'start',capture_start):\n` +
      `  m.next=complete_before_next\n` +
      `  return m.bounded_child([sys.executable,'-c','print("{}")'],stage,3)\n` +
      `if os.name=='posix':\n` +
      ` stage=m.PrivateStage()\n` +
      ` try:\n` +
      `  receipt=run(stage)\n` +
      `  assert receipt==b'{}\\n' and not stage.preserved\n` +
      ` finally: stage.cleanup()\n` +
      `stage=m.PrivateStage()\n` +
      `try:\n` +
      ` with patch.object(m.os,'name','nt'):\n` +
      `  try: run(stage)\n` +
      `  except ValueError as error:\n` +
      `   assert str(error).startswith('validator closure uncertain')\n` +
      `   assert isinstance(error.__cause__,ValueError) and str(error.__cause__)=='validator descendant closure unsupported'\n` +
      `  else: raise AssertionError('Windows branch returned a receipt')\n` +
      ` assert stage.preserved and stage.root.exists()\n` +
      ` print('platform-specific event race behavior accepted')\n` +
      `finally: stage.cleanup()\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'platform-specific event race behavior accepted');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('private stage refuses unavailable file-mode capability before creation', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-capability-')));
  try {
    const driver = `import importlib.util,sys\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `with patch.object(m.os,'fchmod',None),patch.object(m.tempfile,'mkdtemp',side_effect=AssertionError('stage was created')):\n` +
      ` try: m.PrivateStage()\n` +
      ` except ValueError as error: assert str(error)=='private stage requires os.fchmod'\n` +
      ` else: raise AssertionError('missing fchmod accepted')\n` +
      `stage=m.PrivateStage()\n` +
      `try:\n` +
      ` with patch.object(m.os,'fchmod',None),patch.object(m.os,'open',side_effect=AssertionError('file was created')):\n` +
      `  try: stage.create('sample')\n` +
      `  except ValueError as error: assert str(error)=='private stage requires os.fchmod'\n` +
      `  else: raise AssertionError('missing fchmod accepted for new file')\n` +
      ` assert not (stage.root/'sample').exists()\n` +
      `finally: stage.cleanup()\n` +
      `print('missing capability refused before stage and file creation')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'missing capability refused before stage and file creation');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('private stage closes and owns files after setup faults', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-bootstrap-create-fault-')));
  try {
    const driver = `import errno,importlib.util,os,sys\n` +
      `from unittest.mock import patch\n` +
      `s=importlib.util.spec_from_file_location('factory_install',sys.argv[1]); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)\n` +
      `for mode in ('fchmod','fdopen'):\n` +
      ` stage=m.PrivateStage(); opened=[]; real_open=m.os.open\n` +
      ` def capture_open(*args,**kwargs):\n` +
      `  fd=real_open(*args,**kwargs); opened.append(fd); return fd\n` +
      ` try:\n` +
      `  with patch.object(m.os,'open',capture_open),patch.object(m.os,mode,side_effect=OSError('controlled setup fault')):\n` +
      `   try: stage.create('sample')\n` +
      `   except ValueError as error: assert str(error)=='private stage file setup refused'\n` +
      `   else: raise AssertionError(mode+' fault accepted')\n` +
      `  assert len(opened)==1 and 'sample' in stage.owned\n` +
      `  try: os.fstat(opened[0])\n` +
      `  except OSError as error: assert error.errno==errno.EBADF\n` +
      `  else: raise AssertionError(mode+' descriptor leaked')\n` +
      `  stage.cleanup()\n` +
      `  assert not stage.root.exists()\n` +
      ` finally:\n` +
      `  if stage.root.exists():\n` +
      `   if 'sample' not in stage.owned: (stage.root/'sample').unlink(missing_ok=True)\n` +
      `   stage.cleanup()\n` +
      `stage=m.PrivateStage()\n` +
      `try:\n` +
      ` stage.create('sample').close()\n` +
      ` foreign=stage.root/'foreign'; foreign.write_text('keep')\n` +
      ` (stage.root/'sample').unlink(); foreign.rename(stage.root/'sample')\n` +
      ` try: stage.cleanup()\n` +
      ` except ValueError: pass\n` +
      ` else: raise AssertionError('foreign replacement was removed')\n` +
      ` assert (stage.root/'sample').read_text()=='keep'\n` +
      `finally:\n` +
      ` (stage.root/'sample').unlink(missing_ok=True); stage.root.rmdir()\n` +
      `print('setup fault descriptors closed and exact stage cleaned')\n`;
    const path = join(root, 'driver.py');
    writeFileSync(path, driver);
    const result = spawnSync(python, [path, script], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'setup fault descriptors closed and exact stage cleaned');
  } finally { rmSync(root, { recursive: true, force: true }); }
});
