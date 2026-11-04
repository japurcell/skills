// Qualification-only transport. Retains the controller driver's existing bounds.
import { spawn } from 'node:child_process';

export function runOwnedImageTransport(application, args, maximum, timeout, setActive = () => {}) {
  return new Promise(resolveRun => {
    let child;
    const result = { exitCode: null, signal: null, capped: false, timedOut: false, stdout: '', stderr: '' };
    let bytes = 0;
    try { child = spawn(application, args, { windowsHide: true, shell: false, stdio: ['ignore', 'pipe', 'pipe'] }); }
    catch { resolveRun({ ...result, capped: true }); return; }
    setActive(child);
    const timer = setTimeout(() => { result.timedOut = true; child.kill(); }, timeout);
    const collect = stream => chunk => {
      bytes += chunk.length;
      if (bytes > maximum) { result.capped = true; child.kill(); return; }
      result[stream] += chunk.toString('utf8');
    };
    child.stdout.on('data', collect('stdout')); child.stderr.on('data', collect('stderr'));
    child.on('error', () => { result.capped = true; });
    child.on('close', (code, sig) => {
      clearTimeout(timer); setActive(null); result.exitCode = code; result.signal = sig; resolveRun(result);
    });
  });
}
