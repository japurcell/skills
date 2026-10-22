import { execFileSync } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { hostname } from 'node:os';
import { setTimeout as delay } from 'node:timers/promises';
import type { Owner } from '../store.js';

export type Inspection = { state: 'known_live' | 'not_live' | 'unknown'; limitation: string };
function identity(pid: number): string | null {
  try {
    if (process.platform === 'linux') {
      const boot = readFileSync('/proc/sys/kernel/random/boot_id', 'utf8').trim();
      const stat = readFileSync(`/proc/${pid}/stat`, 'utf8');
      const start = stat.slice(stat.lastIndexOf(')') + 2).split(' ')[19];
      return start ? `linux:${boot}:${start}` : null;
    }
    if (process.platform === 'darwin') {
      const boot = execFileSync('/usr/sbin/sysctl', ['-n', 'kern.boottime'], {encoding:'utf8', timeout:1000,maxBuffer:4096}).trim();
      const start = execFileSync('/bin/ps', ['-p', String(pid), '-o', 'lstart='], {encoding:'utf8',timeout:1000,maxBuffer:4096,stdio:['ignore','pipe','ignore']}).trim();
      return start ? `darwin:${boot}:${start}` : null;
    }
  } catch { /* Unavailable metadata is uncertainty, never a license to signal. */ }
  return null;
}
export function currentOwner(pid = process.pid): Owner { return {host:hostname(),pid,start:identity(pid)}; }
export function inspectOwner(owner: Owner): Inspection {
  if (owner.host !== hostname()) return {state:'unknown',limitation:'owner host differs; no remote process inspection'};
  let present = true;
  try { process.kill(owner.pid, 0); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ESRCH') present = false;
    else return {state:'unknown',limitation:'process presence inaccessible'};
  }
  if (!present) return {state:'not_live',limitation:'local PID is absent; descendant activity is not established'};
  const observed = identity(owner.pid);
  const recognized = owner.start !== null && (process.platform === 'linux' ? /^linux:[0-9a-f-]{36}:\d+$/.test(owner.start) : process.platform === 'darwin' ? /^darwin:\{ sec = \d+, usec = \d+ \} [^\r\n]+:[^\r\n]+$/.test(owner.start) : false);
  if (!recognized || !observed) return {state:'unknown',limitation:'boot/start identity unavailable; PID alone is insufficient'};
  if (owner.start !== observed) return {state:'not_live',limitation:'boot/start identity differs; saved owner is absent (PID reuse or reboot)'};
  return {state:'known_live',limitation:'local boot/start identity matches; no universal descendant inspection'};
}
export function duration(value: number | undefined, fallback: number, maximum = 86400000) {
  const result = value ?? fallback;
  if (!Number.isSafeInteger(result) || result < 1 || result > maximum) throw new Error(`duration must be an integer from 1 to ${maximum} milliseconds`);
  return result;
}
export class LiveProcessScope {
  readonly exited: Promise<{code:number|null;signal:NodeJS.Signals|null;error?:Error}>;
  private readonly closed: Promise<void>;
  private closedFlag = false;
  private exitedFlag = false;
  private absent = false;
  private readonly stopped: Promise<void>;
  private stoppedResolve!: () => void;
  private stopTask: Promise<void> | undefined;
  interrupted = false;
  uncertain: boolean;
  constructor(readonly child: ChildProcess, unknownScope: boolean) {
    this.stopped = new Promise(resolve => { this.stoppedResolve = resolve; });
    this.uncertain = unknownScope || process.platform === 'win32';
    this.exited = new Promise(resolve => {
      child.once('error', error => { this.exitedFlag = true; resolve({code:null,signal:null,error}); });
      child.once('exit', (code, signal) => { this.exitedFlag = true; resolve({code,signal}); });
    });
    this.closed = new Promise(resolve => child.once('close', () => { this.closedFlag = true; resolve(); }));
  }
  groupAbsent() {
    if (this.absent) return true;
    if (!this.child.pid) return this.closedFlag;
    if (process.platform === 'win32') return false;
    try { process.kill(-this.child.pid, 0); return false; }
    catch (error) { if ((error as NodeJS.ErrnoException).code === 'ESRCH') { this.absent = true; return true; } this.uncertain = true; return false; }
  }
  private signal(signal: NodeJS.Signals) {
    if (!this.child.pid) return;
    try {
      if (process.platform === 'win32') { if (!this.exitedFlag && this.child.kill(signal)) this.interrupted = true; }
      else if (!this.groupAbsent()) { process.kill(-this.child.pid, signal); if (!this.exitedFlag) this.interrupted = true; }
    } catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ESRCH') this.uncertain = true; }
  }
  stop(grace: number) {
    return this.stopTask ??= (async () => {
      this.signal('SIGTERM');
      await Promise.race([this.closed, delay(grace, undefined, {ref:false})]);
      if (!this.closedFlag || !this.groupAbsent()) this.signal('SIGKILL');
      const deadline = performance.now() + 500;
      while ((!this.closedFlag || !this.groupAbsent()) && performance.now() < deadline) await delay(20);
      if (!this.closedFlag) { this.uncertain = true; this.child.stdout?.destroy(); this.child.stderr?.destroy(); }
    })().finally(() => this.stoppedResolve());
  }
  async result(grace: number): Promise<{code:number|null;signal:NodeJS.Signals|null;error?:Error;quiescent:boolean}> {
    const result = await Promise.race([this.exited, this.stopped.then(() => ({code:null,signal:null}))]);
    if (!this.interrupted && !this.groupAbsent()) this.uncertain = true;
    const closed = await Promise.race([this.closed.then(()=>true), delay(grace, undefined, {ref:false}).then(()=>false)]);
    if (!closed) { this.uncertain = true; await this.stop(0); }
    return {...result, quiescent: !this.uncertain && this.groupAbsent() && this.closedFlag};
  }
}
