# Notification metadata controls qualification

This slice adds repository-wide preferences and one durable acknowledgment per finalized invocation. Both preferences default to `false`. The reminder preference is saved metadata only; this version has no reminder delivery or scheduling loop. Acknowledgment records that an invocation was seen. It does not answer a question, alter its outcome or cleanup, change its exit status, or clear an owner.

The loopback observation host serves `GET /api/notifications/preferences` with its existing in-memory bearer credential. It serves `POST /api/notifications/preferences` with exactly two booleans, `successNotices` and `reminders`, and `POST /api/notifications/acknowledgments` with exactly one `invocationId`. Writes also require the exact host Origin and `application/json`; the existing 8 KiB body bound, four concurrent write bound, duplicate authority header check, and pending-write shutdown retention apply. The existing authenticated invocation detail includes the selected acknowledgment. Unknown IDs return 404; malformed bodies and active invocation targets return 400 without mutation. Repeating an acknowledgment returns its original identity and timestamp without a second event.

Successful invocations read the saved success preference in the finalization transaction. With the default `false`, finalization and owner release remain atomic. With `true`, finalization saves a plan to deliver one `initial` notice and retains the original owner until the bounded sender result is durably recorded and its cleanup is known. The fixed message is `Software Factory completed` / `1 run succeeded`; no captured question, user text, or secret enters it. A failed or unavailable sender does not change the saved success or exit code. Unknown delivery or uncertain result persistence retains the original claim and cannot be resent automatically. A preference change after finalization cannot change that saved delivery decision. Delivery continues through the trusted injected native sender; tests use fake senders only.

## Explicit forward schema step for T16

New stores initialize at schema version 6. Version 5 stores refuse normal open before any mutation. The later explicit, quiescent maintenance procedure must apply the following forward DDL to a verified version 5 store, preserving existing rows and applying the complete transaction or none of it:

```sql
BEGIN IMMEDIATE;
CREATE TABLE notification_preferences(
  id INTEGER PRIMARY KEY CHECK(id=1),
  success_notices INTEGER NOT NULL CHECK(success_notices IN (0,1)),
  reminders INTEGER NOT NULL CHECK(reminders IN (0,1)),
  updated_at TEXT NOT NULL
);
CREATE TABLE notification_acknowledgments(
  invocation_id TEXT PRIMARY KEY REFERENCES invocations(id),
  acknowledged_at TEXT NOT NULL
);
PRAGMA user_version=6;
COMMIT;
```

An absent preferences row means both settings are off. No automatic migration runs during normal open.

## Verification

Public tests exercise disposable repository stores, real loopback HTTP, invocation summaries, fake senders, and a Playwright browser at 390 px. They cover defaults, persistence after reopen, selected finalization, idempotence, malformed and unauthorized writes, quiet success, opted-in success failure and bounded uncertainty, and browser keyboard/focus and saved state. No test submits to a desktop notification provider.
