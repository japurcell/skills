import { spawn } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { win32 } from 'node:path';

export type NotificationState = 'submitted' | 'failed' | 'timed_out' | 'unknown';
export type NotificationReason = 'invalid_request' | 'unsupported_platform' | 'missing_executable' | 'registration_missing' | 'service_unavailable' | 'denied' | 'sender_exit_nonzero' | 'spawn_error' | 'deadline_exceeded' | 'cleanup_unconfirmed';
export type NotificationResult = { state: NotificationState; reason?: NotificationReason; cleanup: 'complete' | 'unknown' };
export interface NativeNotificationCommand { file: string; args: string[] }

const MAX_LIFETIME_MS = 5000;

function failureReason(command: NativeNotificationCommand, code: number | null, stderr: string): NotificationReason {
  const windowsHelper = win32.basename(command.file).toLowerCase() === 'windows-notify.exe';
  if ((windowsHelper && code === 4) || /access denied|permission denied|not authorized|not permitted|notifications disabled/i.test(stderr)) return 'denied';
  if (windowsHelper && code === 3) return 'registration_missing';
  if (/could not connect|cannot connect|notification daemon|session bus|display not found|name has no owner/i.test(stderr)) return 'service_unavailable';
  return 'sender_exit_nonzero';
}

function killOwned(child: ChildProcess) {
  if (!child.pid) return;
  try {
    if (process.platform !== 'win32') process.kill(-child.pid, 'SIGKILL');
    else child.kill('SIGKILL');
  } catch {
    try { child.kill('SIGKILL'); } catch { /* Final result remains unknown unless close is observed. */ }
  }
}

/** Internal transport seam. Tests run disposable real executables through this function. */
export function executeNotificationProcess(command: NativeNotificationCommand, timeoutMs = MAX_LIFETIME_MS): Promise<NotificationResult> {
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > MAX_LIFETIME_MS) throw new Error('invalid notification timeout');
  return new Promise(resolve => {
    const startedAt = performance.now();
    let child: ChildProcess;
    try {
      child = spawn(command.file, command.args, {
        shell: false, detached: process.platform !== 'win32', windowsHide: true,
        stdio: ['ignore', 'pipe', 'pipe'],
      });
    } catch {
      resolve({ state: 'failed', reason: 'spawn_error', cleanup: 'complete' });
      return;
    }
    let settled = false;
    let timedOut = false;
    let stderr = '';
    let launchError: NodeJS.ErrnoException | undefined;
    const finish = (result: NotificationResult) => {
      if (settled) return;
      settled = true;
      clearTimeout(stopTimer);
      clearTimeout(deadlineTimer);
      resolve(result);
    };
    child.stdout?.on('data', () => {});
    child.stderr?.on('data', (chunk: Buffer) => {
      if (stderr.length < 2048) stderr += chunk.toString('utf8').slice(0, 2048 - stderr.length);
    });
    child.on('error', (error: NodeJS.ErrnoException) => { launchError = error; });
    child.on('close', (code: number | null) => {
      if (timedOut) finish({ state: 'timed_out', reason: 'deadline_exceeded', cleanup: 'complete' });
      else if (launchError) finish({ state: 'failed', reason: launchError.code === 'ENOENT' ? 'missing_executable' : launchError.code === 'EACCES' ? 'denied' : 'spawn_error', cleanup: 'complete' });
      else if (code === 0) finish({ state: 'submitted', cleanup: 'complete' });
      else finish({ state: 'failed', reason: failureReason(command, code, stderr), cleanup: 'complete' });
    });
    const remainingMs = Math.max(1, timeoutMs - (performance.now() - startedAt));
    const cleanupBudgetMs = Math.min(200, Math.max(1, Math.floor(remainingMs / 4)));
    const stopTimer = setTimeout(() => {
      if (settled) return;
      timedOut = true;
      killOwned(child);
    }, Math.max(0, remainingMs - cleanupBudgetMs));
    const deadlineTimer = setTimeout(() => {
      if (settled) return;
      killOwned(child);
      child.stdout?.destroy();
      child.stderr?.destroy();
      child.unref();
      finish({ state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' });
    }, remainingMs);
  });
}
