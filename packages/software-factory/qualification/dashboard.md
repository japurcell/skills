# Observation host API qualification

Status: server/API proof on macOS arm64, 2026-10-22. UI, lifecycle boot wiring, notification delivery and native cross-platform qualification are outside T10. Schema remains version 3. No repository installation, release, daemon, scheduler or workflow execution was performed by the browser/API.

## Authority and read contract

`startObservationHost({ store, port?, notificationWrite? })` returns `{ url, reused, close }`; a newly owned host also returns an in-memory `sessionToken`. A reused handle has no credential and `close()` does not stop the actual host. The caller owns the store lifetime and must close the owned host before closing that store. No process signals are installed or stored PIDs killed.

The host claims the repository's dashboard resource with `currentOwner()` and binds IPv4 `127.0.0.1` before publishing `{ url, instanceId }` in that exact claim's JSON. Binding failure closes sockets and releases only the still-matching claim. A failed or unpublished endpoint never permits automatic takeover. Reuse requires local boot/start inspection to report `known_live`, a one-second HTTP challenge, and an unchanged exact repository/claim/token/owner/endpoint after that probe. The HMAC proof covers repository ID, claim ID, owner identity, endpoint and fresh nonce; neither the claim token nor the host session credential travels to the probed endpoint. Probe responses are limited to 4096 bytes with redirects denied. Every served request and SSE poll rechecks the exact current claim.

The HTTP Host must be the published IPv4 authority including its port. Foreign/malformed Referer, foreign Origin and cross-site browser requests are denied. Duplicate authority/credential/cursor headers, duplicate or unknown query parameters, encoded/backslash/traversal paths, and invalid/out-of-range cursors are rejected. Captures are JSON text with `nosniff`, `no-store` and a restrictive CSP. No CORS permission is emitted.

| GET route | Saved result and bounds |
| --- | --- |
| `/api/events?after=0&limit=200` | Decimal-string event cursor; at most 200 rows and 1 MiB serialized response; `gap` marks an unavailable applied cursor. |
| `/api/stream?after=0` | SSE observation events, or `Last-Event-ID` instead of query cursor; never both. |
| `/api/invocations?after=0&limit=30` | At most 100 invocation summaries (metadata omitted) with `nextCursor`/`hasMore`; aggregate data budget 1047552 bytes. |
| `/api/invocations/:id?afterAttempt=0&afterCapture=0&limit=50` | Existing bounded history detail with independent attempt/capture cursors, accounting and worktree. Maximum page count 100; captured previews share a 256 KiB budget. |
| `/api/invocations/:id/sessions?after=0&limit=50` | Native session rows with unknown optional evidence preserved, at most 200 and 1047552 bytes. |
| `/api/invocations/:id/sessions/:sessionId` | One saved session scoped to the selected invocation. |
| `/api/invocations/:id/attempts/:attemptId` | One saved attempt scoped to the selected invocation. |
| `/api/invocations/:id/captures/:captureId?after=0&limit=50` | Scoped chunk sequence page, at most 200 chunks and 1047552 bytes, with explicit completeness/pruned state. |
| `/api/identity?challenge=:nonce` | Bounded fresh-nonce claim proof and public repository/claim/instance IDs. |

All JSON responses are finally capped at 1 MiB, including envelope overhead. Oversized detail responses fail with 413 rather than truncating saved facts. Missing/unreadable saved details return a generic 503; this API currently distinguishes a foreign attempt with 404 but does not distinguish every absent record from essential-store failure. Unknown routes return 404, unsupported methods 405. Read routes have no workflow, command, answer, clearance, install or deletion handler.

## Stream and notification boundaries

SSE pages are fully materialized by `readEvents` before writing HTTP bytes; no SQLite statement or read transaction spans a socket write, drain wait or polling delay. Polls use at most 100 committed events. Each event carries its decimal cursor as `id`, and event metadata/capture references as JSON. Clients must apply/deduplicate before retaining that cursor. Reconnection after the last applied cursor catches up on saved observations only. A gap emits `event: gap` with `/api/invocations` as the snapshot route and ends the stream. Store/claim failure ends with `event: unavailable` or destroys the connection; clients must resynchronize. Snapshot/reconnect/render behavior belongs to T11.

Each viewer's pending Node response bytes are capped at 1 MiB. A false `response.write` pauses delivery until `drain`, with no retained page queue; failure to drain in one second disconnects the viewer. The page being processed is also bounded by store limits. Polling is 100 ms when idle, heartbeat 15 seconds, maximum 16 streams and 32 sockets, 16 KiB HTTP high-water mark, 8 KiB headers, five-second header/request timeout and one-second keepalive timeout. These are application bounds, not a claim about total V8 heap, OS socket buffers, or universal latency. A paused 16 MB committed-event backlog was disconnected while another history read remained responsive. A WAL truncate checkpoint while a paused stream existed completed without a busy reader; shutdown under that load completed within the test's two-second deadline and a new host could bind.

Only POST `/api/notifications/preferences` and `/api/notifications/acknowledgments` can call the optional notification handler. They require an exact same Origin, a timing-safe bearer comparison against the in-memory host credential, `application/json`, valid UTF-8 JSON and at most 8192 bytes. No handler returns 501. Handler input is untrusted and its domain validation remains the notification module's responsibility. At most four callbacks may be pending. If shutdown finds a callback still pending, it closes sockets immediately but rejects close and retains the exact claim. After the callback settles, an explicit later `close()` rechecks and releases only that same claim; no retry timer or new cleanup deadline is introduced. It does not pretend an arbitrary callback can be forcibly cancelled. Credentials are never returned by HTTP, saved in SQLite, or printed. T11 must define a same-origin UI credential bootstrap; T12 owns notification validation, persistence and actual delivery. No desktop sender was implemented.

## Verification

Working directory: `packages/software-factory`, using the pinned `node-v24.22.1-darwin-arm64/bin` first on PATH plus `/opt/homebrew/bin:/usr/bin:/bin`. Native `ps`/`sysctl` inspection and loopback sockets ran outside sandbox restrictions; sandbox denial was not counted as platform evidence.

- `npm run typecheck`: both strict projects passed.
- `npm run build`: passed.
- `node --test test/dashboard.test.mjs`: 13 passed, public HTTP E2E suite, including real recorder committed-before-SSE, paging/reconnect/gap, malformed/hostile headers/paths/cursors/credentials, notification write authorization and pending-write shutdown, uncertain/unpublished and stale/wrong-repository claims, port conflict, failed recorder persistence, unavailable store, viewer disconnection/cap reclamation, bounded identity response, scoped native session/attempt/capture detail, slow viewer and WAL/shutdown proof.
- `npm run test:fixtures`: 7 passed.
- `npm run test:store`: 30 passed.
- `npm run test:lifecycle`: 65 passed.
- `npm run test:adapters -- --provider fake`: 42 passed.

Parent integration owns adding this suite to `scripts/test.mjs` as `web`/`suite: server` and rerunning `npm run test:web -- --suite server`. The explicit dashboard file invocation is the current proof; no empty registered suite is claimed as passing. No live harness/provider, desktop notification, UI, Linux/Windows native, release or install qualification is claimed.

The source follows the pinned [Node 24.22.1 HTTP documentation](https://nodejs.org/docs/latest-v24.x/api/http.html#responsewritechunk-encoding-callback) for backpressure/drain, `writableLength`, and closing all connections after `server.close()`.

## Reflection

Reviewed implementation and verification at this checkpoint. Durable invariants are encoded in exact-claim runtime checks, public HTTP E2E and the owning lifecycle contract. The pending notification-write ownership finding is recorded above and enforced in code. No separate brain note or skill change is needed; parent owns canonical plan reconciliation and integration evidence.
