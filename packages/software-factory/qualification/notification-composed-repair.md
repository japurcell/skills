# Notification composed qualification repair

## Findings

The composed run at the notification-controls baseline recorded 425 passing tests out of 427. The nested native identities browser test failed its existing 2,000 ms Back scroll assertion at `test/browser/ui.test.mjs:518`, and the public notification dispatch assertion exceeded its existing 15,000 ms bound at `test/dispatch.test.mjs:25`. The retained baseline log is `/tmp/factory-notification-controls-base-composed.log`.

Browser instrumentation showed that heading visibility precedes reader restoration. After a Back navigation, the heading was visible with `scrollY` at 0 while `history.state.reader.top` was 452; the restore calls arrived about 139 ms later. In the preceding nested history sequence, a programmatic scroll reached 1,663 px, then a pending route restore returned the page to 452 px about 1 ms later. The fixed 100 ms pause could therefore capture a position before the prior route had finished restoring it.

A second public E2E held the saved-event request during Back restoration and used an actual mouse wheel while the timeline heading was visible. Before the fix, the saved position was 300 px, the wheel reached 807 px, and the asynchronous reader restore reset the page to 300 px. This confirmed that active user scrolling could be lost during restoration.

Independent review found two remaining browser failures. After Repository runs was saved at 180 px, scrolling the intervening timeline to 550 px made Back land at 392 px because the history snapshot held a page-global input counter. In a second real browser path, a held run request let the user scroll the still-visible page to 300 px, but the early run render unconditionally reset it to the saved 180 px. Both public repros failed before this repair.

The notification group originally kept two bounded, never-settling sender cases in the same test file. The public selector log shows the first case taking 6,153 ms, followed by other serial work; the nested dispatch process reached 15,007 ms and was terminated with status 143 before the group completed.

## Repair

Reader snapshots retain the saved window position without a user-input counter. Each route restoration captures a transient input generation when it begins. Its early run render, deferred reader restoration, and click completion share one window-position decision: newer wheel, touch, scroll-key, or scrollbar input prevents a saved position from replacing the user's current position. Input on an intervening route is already accounted for when the next restoration starts. The composed browser test waits for completed route replay before setting its reading position and waits for the browser scroll event instead of sleeping for a fixed 100 ms. Its original 2,000 ms assertion and visible position checks remain unchanged.

The two slow sender cases now live in separately scheduled public test files and share the same private fixture helper, which continues to copy the package's own `node_modules` into each disposable repository. The notification selector runs its six independent files with concurrency 4. The dispatch assertion remains at 15,000 ms and all existing sender deadlines and assertions remain unchanged.

## Verification

Before the first repair, the held saved-event E2E failed with actual scroll 300 px versus expected 807 px. It still passes after this repair. Two new public browser tests reproduced the review findings with 392 versus 180 px and 180 versus 300 px. Both pass after rebuilding the web asset, and the two exact independent Chromium repro scripts now report 180 versus 180 px and 300 versus 300 px. The focused native-identity Back case also passes with its original 2,000 ms assertion.

The public dispatch selector passed under outer test concurrency 2 in 7,635 ms, below its unchanged 15,000 ms bound. The complete notification group passed all 22 tests in 7,629 ms, including the unchanged bounded sender cases. Full web passed all 86 tests in 34,019 ms. Package typecheck and build both passed with Node 24.22.1. These checks used local fixtures and Chromium; no live desktop sender or provider was invoked.
