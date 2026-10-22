import { createHash } from 'node:crypto';
import { readFile, realpath, stat } from 'node:fs/promises';
import { win32 } from 'node:path';
import { environmentRedactionPolicy, RedactionPolicy, redactText } from '../redaction.js';
import { executeNotificationProcess } from './notification-transport.js';
import type { NativeNotificationCommand, NotificationResult } from './notification-transport.js';

export type { NotificationState, NotificationReason, NotificationResult } from './notification-transport.js';
export type NotificationPlatform = 'darwin' | 'linux' | 'win32';

export interface DesktopNotification {
  title: string;
  body: string;
  /** Additional literal secrets to filter before either value reaches a process argument. */
  secrets?: readonly string[];
  /** For qualification only. Values above five seconds are rejected. */
  timeoutMs?: number;
}

const MAX_LIFETIME_MS = 5000;
const HELPER_NAME = 'windows-notify.exe';

/** Internal T15 handoff, read from trusted installation state, never from a notification. */
export interface WindowsNotificationInstallation {
  readonly installRoot: string;
  readonly helperRelativePath: 'windows-notify.exe';
  readonly helperSha256: string;
  readonly repositoryCommonDirectory: string;
  /** Cryptographically random 128-bit install token recorded by the native helper. */
  readonly shortcutOwnerToken: string;
}

/** Stable, repository-scoped identity; callers must register the same identity with the owned shortcut. */
export function repositoryNotificationAppId(repositoryCommonDirectory: string) {
  if (typeof repositoryCommonDirectory !== 'string' || !repositoryCommonDirectory || repositoryCommonDirectory.includes('\0')) throw new Error('invalid repository identity');
  return `SoftwareFactory.Repository.${createHash('sha256').update(repositoryCommonDirectory).digest('hex').slice(0, 24).toUpperCase()}`;
}

function validatedText(value: unknown, name: string, maxBytes: number) {
  if (typeof value !== 'string' || !value.trim() || value.includes('\0') || Buffer.byteLength(value) > maxBytes || Buffer.from(value).toString('utf8') !== value) {
    throw new Error(`invalid notification ${name}`);
  }
  return value;
}

function xmlText(value: string) {
  return value.replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[character]!);
}

function filteredContent(input: DesktopNotification) {
  const extraSecrets = new RedactionPolicy(input.secrets ?? []);
  const policy = new RedactionPolicy([...new Set([...environmentRedactionPolicy().secrets, ...extraSecrets.secrets])]);
  const title = validatedText(redactText(validatedText(input.title, 'title', 256), policy), 'title', 256);
  const body = validatedText(redactText(validatedText(input.body, 'body', 4096), policy), 'body', 4096);
  return { title, body };
}

/** Exact command construction is internal to the native sender, never a caller-supplied executable. */
export function notificationCommand(input: DesktopNotification, platform: NotificationPlatform): NativeNotificationCommand {
  const { title, body } = filteredContent(input);
  if (platform === 'darwin') return {
    file: '/usr/bin/osascript',
    args: ['-e', 'on run argv', '-e', 'display notification (item 2 of argv) with title (item 1 of argv)', '-e', 'end run', '--', title, body],
  };
  if (platform === 'linux') return { file: '/usr/bin/notify-send', args: ['--app-name=Software Factory', '--', title, validatedText(xmlText(body), 'body', 4096)] };
  if (platform === 'win32') throw new Error('Windows notification registration missing');
  throw new Error('unsupported notification platform');
}

async function installedWindowsCommand(input: DesktopNotification, descriptor: WindowsNotificationInstallation, signal: AbortSignal): Promise<NativeNotificationCommand> {
  if (!descriptor || typeof descriptor.installRoot !== 'string' || !/^[A-Za-z]:\\/.test(descriptor.installRoot) ||
      !win32.isAbsolute(descriptor.installRoot) || descriptor.helperRelativePath !== HELPER_NAME ||
      !/^[0-9a-fA-F]{64}$/.test(descriptor.helperSha256) || !/^[0-9A-F]{32}$/.test(descriptor.shortcutOwnerToken)) {
    throw new Error('invalid Windows notification installation');
  }
  const root = await realpath(descriptor.installRoot);
  if (root.toLowerCase() !== descriptor.installRoot.toLowerCase()) throw new Error('uncanonical Windows notification installation');
  const helper = win32.join(root, HELPER_NAME);
  const resolvedHelper = await realpath(helper);
  if (resolvedHelper.toLowerCase() !== helper.toLowerCase()) throw new Error('unowned Windows notification helper');
  const file = await stat(helper);
  if (!file.isFile() || file.size > 32 * 1024 * 1024) throw new Error('invalid Windows notification helper');
  const bytes = await readFile(helper, { signal });
  if (createHash('sha256').update(bytes).digest('hex').toLowerCase() !== descriptor.helperSha256.toLowerCase()) throw new Error('changed Windows notification helper');
  const { title, body } = filteredContent(input);
  return { file: helper, args: ['send', repositoryNotificationAppId(descriptor.repositoryCommonDirectory), descriptor.shortcutOwnerToken, title, body] };
}

/** A submitted result means native API/command acceptance, never visible delivery. */
async function send(input: DesktopNotification, installation?: WindowsNotificationInstallation): Promise<NotificationResult> {
  const startedAt = performance.now();
  if (input === null || typeof input !== 'object' || Array.isArray(input)) {
    return { state: 'failed', reason: 'invalid_request', cleanup: 'complete' };
  }
  const timeoutMs = input.timeoutMs ?? MAX_LIFETIME_MS;
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > MAX_LIFETIME_MS) {
    return { state: 'failed', reason: 'invalid_request', cleanup: 'complete' };
  }
  if (process.platform !== 'darwin' && process.platform !== 'linux' && process.platform !== 'win32') return { state: 'failed', reason: 'unsupported_platform', cleanup: 'complete' };
  if (process.platform === 'win32' && !installation) return { state: 'failed', reason: 'registration_missing', cleanup: 'complete' };
  const abort = new AbortController();
  const timer = setTimeout(() => abort.abort(), timeoutMs);
  try {
    const deadline = new Promise<never>((_, reject) => {
      abort.signal.addEventListener('abort', () => reject(new Error('notification deadline exceeded')), { once: true });
    });
    const preflight = process.platform === 'win32'
      ? installedWindowsCommand(input, installation!, abort.signal)
      : Promise.resolve(notificationCommand(input, process.platform));
    const command = await Promise.race([preflight, deadline]);
    const remainingMs = Math.floor(timeoutMs - (performance.now() - startedAt));
    if (abort.signal.aborted || remainingMs < 1) return { state: 'timed_out', reason: 'deadline_exceeded', cleanup: 'complete' };
    return await executeNotificationProcess(command, remainingMs);
  } catch {
    if (abort.signal.aborted) return { state: 'timed_out', reason: 'deadline_exceeded', cleanup: 'complete' };
    return { state: 'failed', reason: process.platform === 'win32' ? 'registration_missing' : 'invalid_request', cleanup: 'complete' };
  } finally { clearTimeout(timer); }
}

export function sendDesktopNotification(input: DesktopNotification): Promise<NotificationResult> {
  return send(input);
}

/** Only the T15 installation loader should call this with its trusted, persisted manifest. */
export function createInstalledDesktopNotificationSender(installation: WindowsNotificationInstallation) {
  const descriptor = Object.freeze({ ...installation });
  return (input: DesktopNotification): Promise<NotificationResult> => send(input, descriptor);
}
