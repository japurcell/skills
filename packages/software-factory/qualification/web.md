# Saved observation browser qualification

Status: T11 browser, CLI and host proof on macOS arm64, 2026-10-22. This is a read-only local observer. It has no workflow launch, answer, approval, clearance, PID termination, native result mutation, installation or notification delivery control.

## Owner handoff and serving boundary

An actual owner handle can mint a cryptographically random, one-use, 60-second handoff ticket with `createUiHandoff()`. The ticket is in a URL fragment, so it is not sent on the initial GET. An inline script removes it synchronously with `history.replaceState` before loading an external script or making a request. Same-origin `POST /api/ui-session`, with an exact Origin and Host and a bounded JSON body, redeems it once. The response provides the host's existing bearer only to the page's memory. The ticket never becomes the bearer, is not persisted in the store, and cannot be minted through a public HTTP route. There are at most eight pending tickets and 32 failed redemption attempts per host. Cross-process reuse has no read credential and cannot create a handoff. Its CLI attempt refuses without closing the existing owner.

Only `/` and the two built assets `/assets/app.js` and `/assets/style.css` are served. Static paths are an exact allowlist, with no arbitrary file read. The UI has no third-party assets, scripts or referrers. Responses use no-store, no-referrer, nosniff, DENY framing and a restrictive CSP. Saved-data routes, including new run, event-head and selected-invocation pages, require the same bearer as T10 and retain exact local authority and browser-origin checks. Browser SSE uses a `fetch` stream with an Authorization header, following the [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) instead of native [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource/EventSource), whose constructor has no custom-header option. The bearer is not sent in a URL, query, metadata, endpoint claim or console output.

The `dashboard --repository PATH` CLI opens an existing compatible store, starts an owned loopback host, prints only the one-use handoff URL, and closes the handle it owns on SIGINT or SIGTERM. It does not seize another process's claim. The owner must keep the process running for browser reads.

## Saved data and bounded state

The browser uses grouped run pages of 30 cards, chronological per-run invocation pages, at most 50 timeline lanes, 200 selected-invocation event rows and one bounded capture chunk page. Attempt, session and capture pagination replaces the current 50-row page and retains only page cursors for backward navigation. Latest invocation status, outcome, cleanup uncertainty and operator clearance are shown independently; a clearance never rewrites an earlier result. Native child sessions use their saved reported parent IDs and can be collapsed. Capture content is rendered as inert text with explicit continuation, completeness and pruned state. Local search and filters apply to the currently loaded page. An unknown or unavailable deep link is disclosed without falling back to a different run.

The store uses indexed run and invocation selectors, a constant-time saved event head, and an indexed `invocationId` expression selector for selected event pages. The browser reads the committed head before its snapshot, then follows events strictly after its applied cursor. It deduplicates cursors and resnapshots on a gap or reconnect while preserving the selected run, focused input and reader position. Freeze retains the displayed page and counts pending observations; Follow applies the saved stream. Connection loss marks the display as the last known update. No unbounded history scan or event transfer is used to obtain a page.

New repositories use schema 4 for the run and invocation event indexes. An existing schema 3 store is explicitly refused without modifying its data. T16 must provide an explicit, maintenance-locked 3-to-4 migration that creates these indexes and advances the version only after success. T11 does not auto-migrate on ordinary open.

## Verification

Working directory: `packages/software-factory`. Used pinned Node 24.22.1 and offline installed Playwright 1.64.1 Chromium 1248, with `PLAYWRIGHT_BROWSERS_PATH=/tmp/software-factory-playwright-browsers`.

- `npm run typecheck`: strict source and qualification projects passed.
- `npm run build`: passed and copied the authored browser assets to `dist/web`.
- `npm run test:store`: 30 passed.
- `npm run test:lifecycle`: 65 passed after the schema and CLI changes.
- `npm run test:web -- --suite server`: 21 passed, including T10 adversarial HTTP checks plus grouped run pages, exact static allowlist, ticket redemption/replay/origin denial, new route bearer denial, indexed event linkage, old-schema preservation and clearance display facts.
- `node --test test/cli.test.mjs`: 3 passed, including live owner handoff and cross-process refusal without closing the owner.
- `node --test test/browser/ui.test.mjs test/browser/scale.test.mjs`: 5 passed in real Chromium. Browser proof covered fragment removal, bearer-free URL, grouped cards, real recorder capture/SSE, inert hostile markup, keyboard skip link, freeze/follow, invalid deep links, a deleted saved event gap with focus preservation, host disconnection, 390 CSS-pixel viewport and 200% root zoom without page overflow.

The scale fixture held 10,000 runs, 1,000 reported nested sessions, 100,000 saved events and 50 capture chunks of 65,536 bytes (3.125 MiB). With 20 fresh real recorder append events in that database, the final screenshot-generating browser run measured first run-page display at 593.4 ms and committed-event display p95 at 116.4 ms. At that point the DOM held 30 run cards, at most 50 lanes and at most 200 event rows. The capture reader stayed below 1,047,552 displayed characters per page and required an explicit next-page action. These are local measurements, not cross-platform guarantees or a claim about total browser/SQLite memory.

Reviewed screenshots from real host pages were retained outside source at `/tmp/factory-ui-evidence/`: `index-390.png`, `index-200-percent.png`, `run-390.png`, `run-200-percent.png`, `history-scale.png`. Rerun the browser tests with `FACTORY_SCREENSHOT_DIR` set to a local evidence directory to refresh them. The 200% case uses CSS root zoom in Chromium, not the browser's native zoom menu. Manual VoiceOver or other screen-reader testing, other browser engines, Linux and Windows browser qualification were not performed. The browser can identify a saved external evidence reference but cannot verify an external file's current contents. A selected invocation detail whose complete JSON exceeds the T10 1 MiB response cap is reported as unavailable; it is not silently truncated. Notification preference/acknowledgment persistence and delivery remain T12.

## Reflection

The durable boundary is owner-only ticket minting, exact redemption and in-memory bearer use, alongside indexed and bounded saved reads. The old-schema migration prerequisite is recorded above for T16. No additional brain note is needed at this checkpoint.
