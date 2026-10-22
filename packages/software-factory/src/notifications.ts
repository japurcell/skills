import type { DesktopNotification, NotificationResult } from './native/notifications.js';
import type { NotificationDelivery, RepositoryStore } from './store.js';

export type NotificationSender = (message: DesktopNotification) => Promise<NotificationResult>;

function messageFor(record: NotificationDelivery): DesktopNotification {
  const parts: string[] = [];
  if (record.issues.questions) parts.push(`${record.issues.questions} question${record.issues.questions === 1 ? ' needs' : 's need'} input`);
  const outcomeLabels: Record<string, string> = { failed: 'run failed', needs_input: 'run needs input', interrupted: 'run interrupted', cancelled: 'run cancelled' };
  const outcome = outcomeLabels[record.issues.outcome] ?? 'run ended with an issue';
  if (record.issues.outcome !== 'succeeded') parts.push(outcome);
  if (record.issues.cleanup === 'unknown') parts.push('cleanup unknown');
  return { title: 'Software Factory needs attention', body: parts.join('; ').slice(0, 512) };
}

/** The reservation makes an uncertain crash or commit failure non-retryable. */
export async function sendInitialNotification(store: RepositoryStore, invocationId: string, sender?: NotificationSender): Promise<NotificationDelivery | null> {
  const reserved = await store.reserveInitialNotification(invocationId);
  if (!reserved) return store.readNotificationDeliveries(invocationId)[0] ?? null;
  if (!sender) return store.saveInitialNotificationResult(reserved.id, { state: 'failed', reason: 'unbound_sender', cleanup: 'complete' });

  let timer: ReturnType<typeof setTimeout> | undefined;
  let result: NotificationResult;
  try {
    result = await Promise.race([
      Promise.resolve().then(() => sender(messageFor(reserved))),
      new Promise<NotificationResult>(resolve => { timer = setTimeout(() => resolve({ state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' }), 5000); }),
    ]);
    if (!result || !['submitted','failed','timed_out','unknown'].includes(result.state) || !['complete','unknown'].includes(result.cleanup) ||
        (result.cleanup === 'unknown' && result.state !== 'unknown') ||
        (result.reason !== undefined && (typeof result.reason !== 'string' || !/^[a-z_]{1,64}$/.test(result.reason)))) {
      result = { state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' };
    }
  } catch {
    // A sender can submit before rejecting; failure would falsely claim no submission.
    result = { state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' };
  } finally { if (timer) clearTimeout(timer); }
  return store.saveInitialNotificationResult(reserved.id, result);
}
