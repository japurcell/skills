# Research: Release Calendar Role Controls

## Decision 1

Decision: Enforce role-based permissions on the server for every release-calendar read/write/transition endpoint, and expose derived capabilities to the UI rather than trusting the client to infer permissions.

Rationale: The feature introduces distinct roles with materially different privileges, so least-privilege checks must be centralized server-side. Returning derived capabilities lets the Next.js UI render the right controls without making the client the source of truth.

Official docs reviewed:
- OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

Version/context checked: OWASP cheat sheet reviewed on 2026-04-21 against the spec's `viewer` / `editor` / `release_manager` role matrix.

Alternatives considered:
- UI-only role gating — rejected because it allows direct API misuse.
- Collapsing `editor` and `release_manager` into one elevated role — rejected because the spec explicitly separates proposing from approving.

## Decision 2

Decision: Preserve one-quarter backward compatibility by making the new workflow contract additive: keep existing calendar reads stable, add optional capability/transition metadata to responses, and introduce new approval-focused endpoints instead of changing existing write semantics in place.

Rationale: The spec explicitly requires backward-compatible API changes for one quarter. An additive contract minimizes risk for existing clients while still giving the new UI explicit endpoints for proposing, deciding, and listing pending approvals.

Official docs reviewed:
- OpenAPI Specification 3.1.0 — https://spec.openapis.org/oas/v3.1.0
- HTTP Semantics (RFC 9110) — https://httpwg.org/specs/rfc9110.html#section-9.3.3

Version/context checked: OpenAPI 3.1.0 and RFC 9110 reviewed on 2026-04-21; plan uses POST-based transition/decision commands and additive response fields to avoid breaking existing clients.

Alternatives considered:
- Breaking existing release-window endpoints to require new role fields immediately — rejected because it violates the compatibility window.
- Hiding workflow changes behind undocumented behavior in old endpoints — rejected because it creates client ambiguity and weakens contract clarity.

## Decision 3

Decision: Keep perceived latency under 150ms by caching read-heavy calendar and approval-summary queries in the Next.js app where safe, using focused grouped-approval endpoints, and revalidating affected views immediately after mutations.

Rationale: The spec sets a strict perceived-latency target for interactive calendar usage. Narrow approval-summary endpoints plus targeted revalidation reduce overfetching and let the UI stay responsive even during planning-week load.

Official docs reviewed:
- Next.js Caching and Revalidating — https://nextjs.org/docs/app/getting-started/caching-and-revalidating
- Next.js Route Handlers — https://nextjs.org/docs/app/building-your-application/routing/route-handlers

Version/context checked: Next.js docs last updated 2026-04-15 and reviewed on 2026-04-21; plan assumes the existing monorepo can use its current Next.js data fetching and route-handling patterns.

Alternatives considered:
- Refetching the full calendar after every edit — rejected because it increases UI latency and server load.
- Aggressively caching transition decisions without revalidation — rejected because approval state must be fresh for coordinators and managers.

## Decision 4

Decision: Record every release-window transition in an immutable transition log and publish notification work asynchronously after the state change commits, with rejection represented as a `proposed -> draft` transition carrying a rejection reason.

Rationale: The spec requires every transition to include reason and actor metadata, and it separately requires approval/rejection notifications. An immutable ledger supports auditability, while post-commit asynchronous notification dispatch keeps decision latency low and avoids sending notifications for rolled-back changes.

Official docs reviewed:
- Node.js Events API — https://nodejs.org/docs/latest/api/events.html
- HTTP Semantics (RFC 9110) — https://httpwg.org/specs/rfc9110.html#section-9.3.3

Version/context checked: Node.js latest Events API and RFC 9110 reviewed on 2026-04-21; design assumes the existing Node backend can emit internal domain events or queue messages after persistence succeeds.

Alternatives considered:
- Sending notifications inline before the state transition commits — rejected because it can increase decision latency and produce false notifications on failure.
- Introducing a new persistent `rejected` state — rejected because the spec fixes the state set to `draft`, `proposed`, `approved`, `blocked`, and `cancelled`.

## Decision 5

Decision: Use Jest for fast permission/state-machine coverage and Playwright for end-to-end validation of role-specific calendar UI behavior and approval flows.

Rationale: The spec names Jest and Playwright as the current test stack, and the feature spans both backend workflow logic and frontend interaction. Splitting validation this way keeps most checks fast while still proving that the UI renders the right controls for each role.

Official docs reviewed:
- Jest Getting Started — https://jestjs.io/docs/getting-started
- Playwright Introduction — https://playwright.dev/docs/intro

Version/context checked: Jest and Playwright documentation reviewed on 2026-04-21; no new test framework is introduced.

Alternatives considered:
- Relying on Playwright only — rejected because permission and transition rules need fast unit/integration feedback.
- Relying on Jest only — rejected because the feature's main risk includes role-specific UI affordances and approval UX wiring.
