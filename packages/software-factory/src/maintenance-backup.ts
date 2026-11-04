import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { closeSync, constants, fstatSync, fsyncSync, lstatSync, openSync, readSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { LiveProcessScope } from './native/process.js';
import { writePublicationRecord } from './install-publication-state.js';
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function maintenanceBackupPath(common: string, operationId: string, backupId: string) {
  if (!UUID.test(operationId) || !UUID.test(backupId)) throw new Error('invalid forward backup identity');
  return join(common, 'factory', 'maintenance-backups', operationId, backupId, 'history.sqlite');
}

export function openImmutableMaintenanceBackup(path: string) {
  const url = pathToFileURL(path);
  url.searchParams.set('mode', 'ro');
  url.searchParams.set('immutable', '1');
  return new DatabaseSync(url, { readOnly: true, timeout: 100 });
}

export function backupFileDigest(path: string): { sha256: string; identity: string; bytes: number } {
  const observed = lstatSync(path, { bigint: true });
  if (!observed.isFile() || observed.isSymbolicLink() || observed.nlink !== 1n || observed.ino === 0n
    || observed.size < 1n || observed.size > 512n * 1024n * 1024n
    || (process.platform !== 'win32' && (observed.mode & 0o777n) !== 0o600n))
    throw new Error('invalid private forward backup');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
  try {
    const opened = fstatSync(fd, { bigint: true }), digest = createHash('sha256'), buffer = Buffer.allocUnsafe(1024 * 1024);
    if (opened.dev !== observed.dev || opened.ino !== observed.ino || opened.size !== observed.size)
      throw new Error('forward backup identity changed');
    let offset = 0;
    while (offset < Number(opened.size)) {
      const count = readSync(fd, buffer, 0, Math.min(buffer.length, Number(opened.size) - offset), offset);
      if (!count) throw new Error('forward backup truncated');
      digest.update(buffer.subarray(0, count)); offset += count;
    }
    const ended = fstatSync(fd, { bigint: true }), current = lstatSync(path, { bigint: true });
    if (ended.size !== opened.size || ended.mtimeNs !== opened.mtimeNs || current.dev !== opened.dev || current.ino !== opened.ino)
      throw new Error('forward backup changed while hashing');
    fsyncSync(fd);
    return { sha256: digest.digest('hex'), identity: `${opened.dev}:${opened.ino}`, bytes: Number(opened.size) };
  } finally { closeSync(fd); }
}

export async function runMaintenanceBackup(source: string, target: string) {
  const requestPath = join(dirname(target), 'backup-request.json');
  writePublicationRecord(requestPath, { source, target });
  return executeMaintenanceBackupRequest(requestPath);
}

/** Executes only the fixed adjacent helper; caller binds the private request before this boundary. */
export async function executeMaintenanceBackupRequest(requestPath: string) {
  const target = join(dirname(requestPath), 'history.sqlite');
  const child = spawn(process.execPath, [fileURLToPath(new URL('./forward-backup-entry.js', import.meta.url)), '--request', requestPath],
    { detached: process.platform !== 'win32', stdio: ['ignore', 'pipe', 'pipe'], env: { PATH: process.env.PATH ?? '', HOME: dirname(target) } });
  const scope = new LiveProcessScope(child, process.platform === 'win32');
  let stdout = '', stderr = '';
  child.stdout?.on('data', bytes => { stdout += String(bytes); if (Buffer.byteLength(stdout) > 8192) void scope.stop(500); });
  child.stderr?.on('data', bytes => { stderr += String(bytes); if (Buffer.byteLength(stderr) > 8192) void scope.stop(500); });
  const timer = setTimeout(() => { void scope.stop(500); }, 30000);
  try {
    const result = await scope.result(500);
    if (result.code !== 0 || result.signal || result.error || !result.quiescent || scope.interrupted || stdout !== '{"completed":true}\n') {
      await scope.stop(500);
      throw new Error('forward backup helper failed or closure uncertain');
    }
  } finally { clearTimeout(timer); }
}


export function flushBackupDirectory(path: string): void {
  if (process.platform === 'win32') throw new Error('backup durability is unqualified on Windows');
  const fd = openSync(path, constants.O_RDONLY);
  try { fsyncSync(fd); } finally { closeSync(fd); }
}
