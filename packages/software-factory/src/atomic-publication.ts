import { createHash } from 'node:crypto';
import { constants, closeSync, fstatSync, lstatSync, openSync, readSync, realpathSync } from 'node:fs';
import { spawn } from 'node:child_process';
import type { Stats } from 'node:fs';
import { dirname, isAbsolute, normalize } from 'node:path';

export type AtomicPublicationResult = 'moved' | 'collision' | 'unsupported' | 'refused' | 'unknown';
export type AtomicPublicationFileBinding = { path: string; identity: string; sha256: string };
export type AtomicPublicationInput = {
  source: string; destination: string; sourceIdentity: string; sourceParentIdentity: string;
  destinationParentIdentity: string;
  binding: { interpreter: AtomicPublicationFileBinding; helper: AtomicPublicationFileBinding };
};
const identity = (s: Stats) => `${s.dev}:${s.ino}`;
function canonical(path: string): boolean {
  return typeof path === 'string' && isAbsolute(path) && normalize(path) === path && !path.includes('\0');
}
function checkedFile(binding: AtomicPublicationFileBinding): number {
  if (!binding || !canonical(binding.path) || !/^[0-9]+:[0-9]+$/.test(binding.identity) || !/^[a-f0-9]{64}$/.test(binding.sha256)
    || realpathSync(binding.path) !== binding.path) throw new Error('binding');
  const fd = openSync(binding.path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const before = fstatSync(fd), current = lstatSync(binding.path);
    if (!before.isFile() || !current.isFile() || identity(before) !== binding.identity || identity(current) !== binding.identity
      || before.size > 128 * 1024 * 1024) throw new Error('binding');
    const digest = createHash('sha256'), buffer = Buffer.alloc(65536);
    for (let offset = 0; offset < before.size;) {
      const count = readSync(fd, buffer, 0, Math.min(buffer.length, before.size - offset), offset);
      if (!count) throw new Error('binding');
      digest.update(buffer.subarray(0, count)); offset += count;
    }
    const after = fstatSync(fd), named = lstatSync(binding.path);
    if (digest.digest('hex') !== binding.sha256 || identity(after) !== binding.identity || identity(named) !== binding.identity
      || before.size !== after.size || before.mtimeMs !== after.mtimeMs || before.ctimeMs !== after.ctimeMs
      || before.size !== named.size || before.mtimeMs !== named.mtimeMs || before.ctimeMs !== named.ctimeMs) throw new Error('binding');
    return fd;
  } catch (error) { closeSync(fd); throw error; }
}
/** The caller authenticates stage/runtime bindings, owns the claim, checks full inventories,
 * flushes both parents and issues receipts. POSIX source lookup is not identity-conditional.
 * Unknown means preserve evidence and claim, with no retry, rollback or adoption. */
export async function atomicPublicationMove(input: AtomicPublicationInput): Promise<AtomicPublicationResult> {
  if (process.platform !== 'darwin' && process.platform !== 'linux') return 'unsupported';
  let helperFd: number | undefined, interpreterFd: number | undefined;
  try {
    if (!input || !canonical(input.source) || !canonical(input.destination) || input.source === input.destination
      || [input.sourceIdentity, input.sourceParentIdentity, input.destinationParentIdentity].some(x => typeof x !== 'string' || !/^[0-9]+:[0-9]+$/.test(x))) return 'refused';
    const request = JSON.stringify({ source: input.source, destination: input.destination, sourceIdentity: input.sourceIdentity,
      sourceParentIdentity: input.sourceParentIdentity, destinationParentIdentity: input.destinationParentIdentity });
    if (Buffer.byteLength(request) > 16384) return 'refused';
    helperFd = checkedFile(input.binding.helper);
    interpreterFd = checkedFile(input.binding.interpreter);
    // Pass the already authenticated helper descriptor; no pathname is reopened by Python.
    const deadline = Date.now() + 12000;
    const child = spawn(input.binding.interpreter.path, ['-I', '-S', '-B', '/dev/fd/3'], {
      cwd: dirname(input.binding.helper.path), env: {}, detached: true, shell: false,
      stdio: ['pipe', 'pipe', 'pipe', helperFd],
    });
    let bytes = 0, output = '', bad = false, expired = false;
    child.stdout!.on('data', (b: Buffer) => { bytes += b.length; if (bytes <= 128) output += b.toString('utf8'); else bad = true; });
    child.stderr!.on('data', (b: Buffer) => { bytes += b.length; bad = true; });
    child.stdin!.on('error', () => { bad = true; });
    child.stdin!.end(request);
    const result = await new Promise<{ code: number | null; signal: NodeJS.Signals | null } | null>(resolve => {
      let done = false;
      const finish = (v: { code: number | null; signal: NodeJS.Signals | null } | null) => { if (!done) { done = true; clearTimeout(timer); clearTimeout(limit); resolve(v); } };
      const kill = () => { expired = true; if (child.pid) try { process.kill(-child.pid, 'SIGKILL'); } catch { /* uncertain */ } };
      const timer = setTimeout(kill, 10000);
      const limit = setTimeout(() => { kill(); finish(null); }, 12000);
      child.once('error', () => finish(null));
      child.once('close', (code, signal) => finish({ code, signal }));
    });
    if (!child.pid) return 'unknown';
    // A direct child can close its pipes while an owned descendant remains.
    // Terminate only this invocation's detached process group, then wait within
    // the original overall deadline. Any lingering group makes the result unknown.
    let lingering = false;
    try { process.kill(-child.pid, 0); lingering = true; }
    catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ESRCH') lingering = true; }
    if (lingering) {
      try { process.kill(-child.pid, 'SIGKILL'); } catch { /* closure check decides */ }
      while (Date.now() < deadline) {
        try { process.kill(-child.pid, 0); }
        catch (error) { if ((error as NodeJS.ErrnoException).code === 'ESRCH') break; return 'unknown'; }
        await new Promise(resolve => setTimeout(resolve, Math.min(10, Math.max(1, deadline - Date.now()))));
      }
      return 'unknown';
    }
    if (!result || expired || bad || result.code !== 0 || result.signal) return 'unknown';
    const values: AtomicPublicationResult[] = ['moved', 'collision', 'unsupported', 'refused', 'unknown'];
    const category = output.endsWith('\n') ? output.slice(0, -1) : '';
    if (!values.includes(category as AtomicPublicationResult)) return 'unknown';
    if (category === 'moved') {
      try {
        const sp = dirname(input.source), dp = dirname(input.destination);
        const a = lstatSync(sp), b = lstatSync(dp), dest = lstatSync(input.destination);
        if (!a.isDirectory() || !b.isDirectory() || !dest.isDirectory() || identity(a) !== input.sourceParentIdentity
          || identity(b) !== input.destinationParentIdentity || identity(dest) !== input.sourceIdentity
          || realpathSync(sp) !== sp || realpathSync(dp) !== dp) return 'unknown';
        try { lstatSync(input.source); return 'unknown'; }
        catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') return 'unknown'; }
      } catch { return 'unknown'; }
    }
    return category as AtomicPublicationResult;
  } catch { return 'refused'; }
  finally { if (helperFd !== undefined) closeSync(helperFd); if (interpreterFd !== undefined) closeSync(interpreterFd); }
}
