import { createHash } from 'node:crypto';
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
  /** Required only on Windows. Installation owns this executable and its matching shortcut. */
  windowsHelper?: string;
  windowsAppId?: string;
  /** For qualification only. Values above five seconds are rejected. */
  timeoutMs?: number;
}

const APP_ID = /^SoftwareFactory\.Repository\.[0-9A-F]{24}$/;
const MAX_LIFETIME_MS = 5000;

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

/** Exact command construction is internal to the native sender, never a caller-supplied executable. */
export function notificationCommand(input: DesktopNotification, platform: NotificationPlatform): NativeNotificationCommand {
  const extraSecrets = new RedactionPolicy(input.secrets ?? []);
  const policy = new RedactionPolicy([...new Set([...environmentRedactionPolicy().secrets, ...extraSecrets.secrets])]);
  const title = validatedText(redactText(validatedText(input.title, 'title', 256), policy), 'title', 256);
  const body = validatedText(redactText(validatedText(input.body, 'body', 4096), policy), 'body', 4096);
  if (platform === 'darwin') return {
    file: '/usr/bin/osascript',
    args: ['-e', 'on run argv', '-e', 'display notification (item 2 of argv) with title (item 1 of argv)', '-e', 'end run', '--', title, body],
  };
  if (platform === 'linux') return { file: '/usr/bin/notify-send', args: ['--app-name=Software Factory', '--', title, validatedText(xmlText(body), 'body', 4096)] };
  if (platform === 'win32') {
    if (!input.windowsHelper || !/^[A-Za-z]:\\/.test(input.windowsHelper) || !win32.isAbsolute(input.windowsHelper) || win32.basename(input.windowsHelper).toLowerCase() !== 'windows-notify.exe') throw new Error('Windows notification helper must be an absolute managed path');
    if (!input.windowsAppId || !APP_ID.test(input.windowsAppId)) throw new Error('invalid Windows notification identity');
    return { file: input.windowsHelper, args: ['send', input.windowsAppId, title, body] };
  }
  throw new Error('unsupported notification platform');
}

/** A submitted result means native API/command acceptance, never visible delivery. */
export async function sendDesktopNotification(input: DesktopNotification): Promise<NotificationResult> {
  if (!Number.isInteger(input.timeoutMs ?? MAX_LIFETIME_MS) || (input.timeoutMs ?? MAX_LIFETIME_MS) < 1 || (input.timeoutMs ?? MAX_LIFETIME_MS) > MAX_LIFETIME_MS) {
    return { state: 'failed', reason: 'invalid_request', cleanup: 'complete' };
  }
  if (process.platform !== 'darwin' && process.platform !== 'linux' && process.platform !== 'win32') return { state: 'failed', reason: 'unsupported_platform', cleanup: 'complete' };
  try { return await executeNotificationProcess(notificationCommand(input, process.platform), input.timeoutMs); }
  catch { return { state: 'failed', reason: 'invalid_request', cleanup: 'complete' }; }
}
