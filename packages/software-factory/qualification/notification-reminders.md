# Grouped reminder qualification

One dashboard host owns the repository reminder timer. The saved `reminders` preference defaults to off. Enabling it, or starting a host with it already enabled, schedules the first tick 15 minutes later. Rewriting `true` to `true` and changing only success notices leave that deadline intact. Disabling cancels the timer. A restarted host starts a fresh 15-minute interval and never catches up missed ticks. Reusing the same dashboard claim returns its existing host and does not create a second timer.

The finalization transaction indexes only invocations with a saved issue: non-success outcome, unknown execution cleanup, or at least one complete request capture. Acknowledgments exclude only their selected finalized invocation from later reminder groups. They do not change its execution facts, saved question, cleanup, or initial delivery. Each tick reads no more than 101 unacknowledged attention IDs, keeps at most 100, and records `hasMore` if a further ID exists. The fixed native title and count-only body contain no captured text, paths, or secrets. A truncated group says `100 or more runs need attention`.

Before external submission, the store commits a fresh group ID, its bounded membership, and `reserved` state under the exact dashboard claim. A crash never replays that ID. Sender acceptance, failure, timeout, or unknown cleanup updates the same record; `visibleDelivery` stays `false`. The trusted sender has the existing five-second result bound. Missing binding is saved as `failed` with `unbound_sender`; rejection after possible submission, malformed results, a nonsettling sender, and uncertain result persistence retain the original dashboard claim. A late sender result cannot rewrite a terminal record. Host close sets stopping immediately, cancels the timer, waits for the active reserve/send/result operation, and releases the claim only after known clean completion. A reserved or unknown group also blocks automatic store claim release. A changed claim cannot submit or record against its replacement. The authenticated group read is bounded and uses the existing bearer, origin, header, and response-size controls. This version never calls a real desktop provider in qualification.

## Explicit forward schema step for T16

Fresh stores use schema version 7. Normal opening of version 6 or older stores refuses before configuration or mutation. The previously documented explicit 5-to-6 step remains necessary. Later explicit, quiescent maintenance must apply this exact 6-to-7 transaction to a verified version 6 store. It indexes existing finalized issues without creating or replaying any reminder groups:

```sql
BEGIN IMMEDIATE;
CREATE TABLE notification_attention(invocation_id TEXT PRIMARY KEY REFERENCES invocations(id));
CREATE TABLE notification_reminder_groups(id TEXT PRIMARY KEY, claim_id TEXT NOT NULL, unsettled INTEGER NOT NULL CHECK(unsettled IN (0,1)), data TEXT NOT NULL CHECK(json_valid(data)));
CREATE INDEX notification_reminder_unsettled ON notification_reminder_groups(claim_id,unsettled);
INSERT INTO notification_attention(invocation_id)
SELECT i.id FROM invocations AS i
WHERE json_extract(i.data,'$.stage')='finalized'
  AND (json_extract(i.data,'$.outcome')!='succeeded'
    OR json_extract(i.data,'$.cleanup')='unknown'
    OR EXISTS (SELECT 1 FROM captures AS c WHERE c.invocation_id=i.id AND c.channel='request' AND c.state='complete'));
PRAGMA user_version=7;
COMMIT;
```

No migration is implemented in normal startup. The old version 6 `notification_deliveries` table remains initial-notice-only, with its original `invocation_id NOT NULL` and `kind='initial'` constraint. Reminder groups have their own table and durable identity.

## Local verification

With pinned Node 24.22.1 and an independent offline dependency install, package typecheck and build passed. The two public reminder files passed 12/12 together in 5.13 seconds, including the unchanged five-second sender bound and a late completion. The existing notification selector passed 22/22 in 7.06 seconds; store passed 33/33; web passed 86/86, including Chromium at 390 px; release passed 23/23. Narrow-width screenshots were inspected. All sends used trusted fakes; no desktop provider was called. Parent registration and composed proof are separate integration evidence.

## Independent review repairs

An authenticated HTTP race reproduced a persisted `reminders=true` setting with no scheduled tick when two saves overlapped. The host now serializes preference writes through their schedule/cancel decision, reads the preceding committed setting inside that sequence, and refuses a queued write after close or claim loss. The public HTTP test covers both overlap orders; a later `true` save gets a full 15-minute interval, while `true` to `true` keeps the existing timer. A real Chromium run also reproduced a stale open dashboard after a submitted reminder. The dashboard now refreshes only the latest bounded reminder metadata on `notification.reminder_reserved` and `notification.reminder_recorded` and at stream connection, updating the status text in place. Submitted and uncertain browser cases preserve selection, scroll position, and the open panel.

After these repairs, pinned Node 24.22.1 typecheck and build pass. The focused reminder pair passes 13/13 in 5.15 seconds, including the unchanged five-second sender bound. The registered notification selector passes 22/22 in 7.65 seconds, below its 15-second bound. The registered web selector passes 86/86 in 33.68 seconds after the final stream cleanup change, including the unchanged Back reading-position case near its two-second bound. The two new Chromium reminder cases pass 2/2 in 1.05 seconds at 390 px, with no horizontal overflow; both screenshots were inspected. All reminder sends used fake senders and fake schedules; no desktop provider was called. Parent owns registration and composed proof after integrating this candidate.

A later independent HTTP reproducer found that disabling and reenabling while a reservation waited could let the old tick submit immediately. The active tick now retains its enable generation through reserve-to-submit; a changed generation records stopped-before-submit and schedules a fresh full interval after settlement. The maintained public test checks no old send, a clean canceled reservation, the new fifteen-minute interval, and a distinct submitted group on the next tick. Pinned strict checks/build and all fourteen maintained reminder cases, two Chromium cases, and the retained external reproducer pass together: 17/17 in 5.262 seconds, zero skips (`/tmp/factory-reminder-enable-epoch-green.log`). Parent registration and composed integration remain pending.
