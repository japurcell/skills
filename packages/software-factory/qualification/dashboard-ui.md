# T11 dashboard UI race qualification

Status: private repair candidate on macOS arm64, 2026-10-22. This note supplements `web.md`; canonical plan and release acceptance remain with the integration owner.

The public seam is the loopback observation host in real Playwright Chromium, backed by disposable Git repositories and committed SQLite history. Tests use pinned Node 24.22.1 and Playwright Chromium 1248 from `/tmp/software-factory-playwright-browsers`.

## Reproduced failures and repairs

- A Back restore of open capture A held its capture GET. A newer same-invocation snapshot held stale detail and event pages. Releasing A, committing capture B, then releasing the newer reads left B absent on committed source `f8ea2e6f` even after the page reported Connected. The older restore now checks snapshot and route ownership after every wait, and a same-invocation navigation carries the reader's disclosure and capture selection into the newer snapshot. The public test is `an older Back reader restore cannot resume SSE during a newer same-route snapshot`.
- An index route read held a stale Running card while a finalized event committed. The stream reported Connected before its card refresh completed. Every route, initial, page and gap resnapshot now samples an event head and keeps the stream in Catching up until all events through that head have been projected. The held-card route test was red before this change and green afterward.
- Freeze during an awaited card refresh changed a frozen card from Running to Failed while its cursor stayed pinned. Async refreshes now check Freeze and snapshot ownership before mutation; the event is deferred and Follow rebuilds it. The held-card Freeze test was red before this change and green afterward.
- A selected capture append advanced the Connected cursor while its saved text read was held. Output reads now belong to the event projection. Newer saved capture events may appear as bounded pending rows while their projections wait, preserving the existing rapid-append test; the cursor advances in order only after projection. Failed reads disconnect and replay from the last applied cursor. Both a held read and a transient 503 are exercised in Chromium.
- With 49 saved captures, live captures 50 and 51 made Next show capture 50 again. A capture creation now reloads the bounded current summary page to obtain its authoritative next anchor. The 49/50/51 pagination test was red before this change and green afterward.
- The existing Back exact-scroll assertion failed intermittently. A delayed breadcrumb test reproduced the browser's pre-click scroll-to-top after a reading pause. Repeated suite diagnostics found a second cause: a prior route saved 1663px while the current page's actual reading position was 452px. Scroll intent survives the breadcrumb's automatic scroll and resets on history route changes. Neither exact-coordinate assertion or its two-second wait was widened.

## Verification

From `packages/software-factory`, with pinned Node on `PATH` and `PLAYWRIGHT_BROWSERS_PATH=/tmp/software-factory-playwright-browsers`:

- `npm run typecheck`: passed strict source and qualification checks.
- `npm run build`: passed and copied the repaired authored UI into ignored `dist/web` for the browser host.
- `node --test test/browser/ui.test.mjs test/browser/scale.test.mjs`: 43 passed. Index display was 631.9ms and committed-event p95 was 115.7ms over 20 samples; DOM bounds remained 30 cards, 50 lanes and 200 events.
- `npm run test:web -- --suite server`: 22 passed.
- `npm run test:store`: 30 passed.
- `npm run test:lifecycle`: 65 passed.
- Ten repeated focused Chromium runs of four Back, scroll and output timing cases passed after the scroll reset. Three consecutive full 42-check browser/scale runs passed before the final transient-read test was added; the final 43-check run passed.

The browser checks use a real local host and Chromium but do not establish native Windows/Linux UI timing or desktop assistive-technology acceptance. Integration, canonical plan updates and final release qualification remain outside this private candidate.
