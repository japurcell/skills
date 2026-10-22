# T11 dashboard UI race qualification

Status: private repair candidate on macOS arm64, 2026-10-22. This note supplements `web.md`; canonical plan and release acceptance remain with the integration owner.

The public seam is the loopback observation host in real Playwright Chromium, backed by disposable Git repositories and committed SQLite history. Tests use pinned Node 24.22.1 and Playwright Chromium 1248 from `/tmp/software-factory-playwright-browsers`.

## Ownership and committed cursor

The existing snapshot generation now owns a complete view intent: navigation, Follow, Freeze, event/history/capture paging, capture selection, and lane/collapse controls. Starting an intent aborts its predecessor's read controller and stream, invalidates its queued projections, and immediately proceeds. It never awaits obsolete I/O. All JSON reads use that controller plus a 10-second timeout and check cancellation after body decoding. Route and tuple checks remain where they describe the displayed identity. Independent index/run/event/reader/outcome/card request counters and the Follow lock were removed.

SSE projections remain serial. The applied cursor advances only when the current stream's complete essential projection succeeds; index card, invocation outcome, saved question, capture summary and followed output failures reject into disconnect/replay. Catch-up heads are read through the same owned resume path before Connected. New intents replay from the last fully applied cursor. Frozen replay deduplicates against the bounded deferred window's highest cursor, including events already evicted from its 200-row buffer.

Capture identity, page and origin commit together after successful reads. Optional reader restoration errors remain visible as alerts without corrupting the capture identity or stopping live history. Output following rechecks scroll/selection intent after reading saved bytes. An old route's buttons are disabled during navigation to a different route, while links remain usable to supersede that navigation.

## Recovery, membership and explicit navigation

A transient catch-up head failure after capture selection now retries automatically, with a 300ms initial delay capped at five seconds and each read retaining the existing 10-second JSON timeout. The existing snapshot generation owns every retry, so a newer intent supersedes recovery without another counter or lock. The public regression timed out at two seconds before the change, then observed the newly committed event and Connected cursor after automatic recovery.

Live index projections reapply the same search and outcome predicate used by initial rendering. A card leaving the predicate is removed, and a newly matching card is inserted at its position in the loaded page. Unaffected cards are not recreated. An unchanged empty-filter message likewise retains its Clear filters button and focus; review reproduced that focus loss before the no-op membership guard. The public regression first observed a Failed card incorrectly retained by Running, then passed both outcome removal and metadata-driven search entry. A separate 32-run check proves off-page changes do not fetch or expand the 30-card page, paging retains its anchors and order, and an untouched card retains its DOM, focus and selected text. New runs retain the existing explicit Refresh run order policy; there is no unbounded history read.

Explicit links, Back/Forward, run paging and invocation paging end Freeze before loading current projections. The destination remains Catching up until the committed cursor includes its required reads. Same-view Freeze and its reader controls keep their existing pinned behavior. The frozen run chip states that navigation follows latest history. The navigation regression timed out before the fix when a current Failed card remained labeled Frozen at the old cursor; it now observes Failed with the new Connected cursor and an unpressed Freeze control at 390px. The existing delayed Follow race now explicitly freezes the destination before releasing the obsolete Follow; all its original frozen assertions remain intact. Its former implicit cross-route Freeze expectation conflicted with showing current destination projections truthfully.

## Earlier ownership repair red/green evidence

The public seam is unchanged: real Chromium against the real authenticated loopback host and committed disposable SQLite history. Required projections use intercepted public HTTP responses to reproduce failures; assertions observe rendered output and connection status.

- Before source edits, all three review reproducers failed: a failed card read was accepted without replay, navigation still showed the old Run heading after 750ms of a held output read, and an earlier page replaced Freeze's cursor 212 with cursor 13. Their public regressions now pass without longer deadlines.
- Persistent outcome/question failures leave Running visible and observation disconnected until replay succeeds; the finalized cursor then accompanies Failed. A transient card failure likewise retries before Connected advances.
- Failed capture selection retained a new identity with the old page, so later bytes could not follow the displayed capture. Its public test timed out at the original two-second deadline before the atomic commit fix and now passes.
- Scrolling away during a held append read still appended the deferred tail. The new test failed on that visible tail before the post-read pause check and now passes; explicit Load new saved text still follows it.
- Follow silently stopped after its catch-up head failed. The new test failed to reach Disconnected within two seconds and now passes, including recovery after another Freeze/Follow in that earlier case. Automatic recovery without another action is now covered above.
- Reconnecting a frozen reader after 205 deferred events doubled its pending count to 410. The new test observed that exact failure before high-water deduplication and now retains 205, with at most 200 event rows.
- Additional public tests prove Freeze supersedes a held next-output page and optional Back capture restoration fails visibly while outcome updates remain usable.

## Earlier retained regression evidence

- A Back restore of open capture A held its capture GET. A newer same-invocation snapshot held stale detail and event pages. Releasing A, committing capture B, then releasing the newer reads left B absent on committed source `f8ea2e6f` even after the page reported Connected. The older restore now checks snapshot and route ownership after every wait, and a same-invocation navigation carries the reader's disclosure and capture selection into the newer snapshot. The public test is `an older Back reader restore cannot resume SSE during a newer same-route snapshot`.
- An index route read held a stale Running card while a finalized event committed. The stream reported Connected before its card refresh completed. Every route, initial, page and gap resnapshot now samples an event head and keeps the stream in Catching up until all events through that head have been projected. The held-card route test was red before this change and green afterward.
- Freeze during an awaited card refresh changed a frozen card from Running to Failed while its cursor stayed pinned. Async refreshes now check Freeze and snapshot ownership before mutation; the event is deferred and Follow rebuilds it. The held-card Freeze test was red before this change and green afterward.
- A selected capture append advanced the Connected cursor while its saved text read was held. Output reads now belong to the event projection. Newer saved capture events may appear as bounded pending rows while their projections wait, preserving the existing rapid-append test; the cursor advances in order only after projection. Failed reads disconnect and replay from the last applied cursor. Both a held read and a transient 503 are exercised in Chromium.
- With 49 saved captures, live captures 50 and 51 made Next show capture 50 again. A capture creation now reloads the bounded current summary page to obtain its authoritative next anchor. The 49/50/51 pagination test was red before this change and green afterward.
- The existing Back exact-scroll assertion failed intermittently. A delayed breadcrumb test reproduced the browser's pre-click scroll-to-top after a reading pause. Repeated suite diagnostics found a second cause: a prior route saved 1663px while the current page's actual reading position was 452px. Scroll intent survives the breadcrumb's automatic scroll and resets on history route changes. Neither exact-coordinate assertion or its two-second wait was widened.

## Verification

From `packages/software-factory`, with pinned Node 24.22.1 on `PATH` and `PLAYWRIGHT_BROWSERS_PATH=/tmp/software-factory-playwright-browsers`:

- `npm run typecheck`: passed strict source and qualification checks after the final source edits.
- `npm run build`: passed and copied authored UI into ignored `dist/web`.
- `node --test test/browser/ui.test.mjs test/browser/scale.test.mjs`: all 58 passed in 32.127 seconds on the final source and tests. Index display was 598.0ms and committed-event p95 was 113.6ms over 20 samples; unchanged DOM assertions retained 30 cards, at most 50 lanes and at most 200 events. Log: `/tmp/factory-ui-membership-browser.log`.
- `npm run test:web -- --suite server`: all 22 passed in 5.222 seconds. Host/security source is unchanged.
- `npm run test:store`: all 30 passed in 2.243 seconds. Log: `/tmp/factory-ui-membership-store.log`.
- `npm run test:lifecycle`: all 65 passed in 51.751 seconds. Log: `/tmp/factory-ui-membership-lifecycle.log`.
- The preceding full 52-case and 53-case browser/scale runs also passed before the final added error-path/buffer cases. The original exact scroll, focus, selection, tuple, 49/50/51 capture paging, rapid-append and catch-up assertions were retained.
- Inspected rendered 390px index, run and frozen run screenshots in `/tmp/factory-ui-membership-screenshots`. Controls, wrapped identities, disclosures and recorded event text remain contained and legible; automated 200% CSS zoom and narrow overflow assertions pass. These screenshots are temporary evidence, not repository artifacts.
- `git diff --check`: passed. Reflection found the durable async ownership lessons encoded in runtime boundaries and public tests; no additional brain or skill write is needed.

This is an unpushed private repair candidate, not T11 acceptance. Independent review, maintained registration and composed integration remain with the parent owner. Native Windows/Linux UI timing, real browser/native zoom, manual assistive technology and schema-4 forward maintenance remain later gates. No host/security, schema, registry, execution control or canonical plan files changed.
