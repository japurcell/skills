# Research: Release Calendar Role Controls

## Decision 1: Model roles and workflow states as shared typed unions across backend and frontend

- **Decision**: Define `viewer`, `editor`, `release_manager` roles and the five release-window states as shared TypeScript types/enums used by backend policies, API contracts, and Next.js UI helpers.
- **Rationale**: The feature depends on consistent interpretation of permissions and legal transitions across a Node backend and a Next.js frontend. TypeScript's standard type system is sufficient to model these values precisely and avoids `any`-driven drift between request validation, response presentation, and client-side affordances.
- **Official docs reviewed**:
  - TypeScript Handbook — Everyday Types: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
- **Version/context checked**: Current TypeScript Handbook guidance for primitive types, arrays, annotations, and avoiding implicit `any` where typed domain values are expected.
- **Alternatives considered**: Unstructured string literals repeated in each package (rejected because they drift easily); frontend-only type definitions (rejected because backend policy and validation must use the same role/state vocabulary).

## Decision 2: Split the Next.js calendar page into server-rendered data shells and client-only interactive controls

- **Decision**: Render the calendar page and grouped approval data with server-capable Next.js components, and keep editing, proposing, and approval actions inside small client components and hooks.
- **Rationale**: Next.js documents that Server Components are the default and are best for fetching data close to the source, while Client Components are the right place for state, event handlers, and browser APIs. React's render-purity guidance reinforces isolating side effects to event handlers/effects, which fits the release-calendar dialogs and optimistic UI updates.
- **Official docs reviewed**:
  - Next.js — Server and Client Components: https://nextjs.org/docs/app/getting-started/server-and-client-components
  - React — Components and Hooks must be pure: https://react.dev/reference/rules/components-and-hooks-must-be-pure
- **Version/context checked**: Next.js docs last updated April 15, 2026; current React reference guidance on purity and side effects outside render.
- **Alternatives considered**: Making the whole calendar feature a client-only subtree (rejected because it sends more JavaScript and weakens first render behavior); putting mutation side effects directly in render-time code (rejected because React explicitly warns against render side effects).

## Decision 3: Use additive OpenAPI-described HTTP endpoints for transitions and grouped pending approvals

- **Decision**: Add a single transition endpoint and a grouped pending-approvals endpoint, describe them with an OpenAPI 3.1 contract, and keep existing read endpoints additive and backward compatible for one quarter.
- **Rationale**: The OpenAPI Specification is designed to make HTTP APIs understandable without source access and is an effective source of truth for additive request/response changes. A single transition endpoint keeps workflow validation centralized, while the grouped approvals endpoint directly serves the manager queue requirement without breaking legacy consumers.
- **Official docs reviewed**:
  - OpenAPI Specification (latest HTML source of truth): https://spec.openapis.org/oas/latest.html
- **Version/context checked**: Latest OpenAPI HTML specification page, currently publishing version 3.2.0 as the source-of-truth document while remaining compatible with OpenAPI 3.1 document structure for this contract.
- **Alternatives considered**: Separate `/approve`, `/reject`, `/block`, and `/cancel` endpoints (rejected because they duplicate transition logic); immediate breaking v2 endpoints (rejected because the spec requires backward-compatible API behavior for one quarter).

## Decision 4: Persist approvals/rejections for asynchronous notification dispatch instead of relying on inline in-process listeners

- **Decision**: Write notification-dispatch work durably as part of the transition transaction and process it asynchronously through a dispatcher/worker.
- **Rationale**: Node's `EventEmitter` listeners run synchronously and unhandled `'error'` events can terminate the process, so naïve in-process fire-and-forget listeners are a poor fit for approval/rejection notifications that must not compromise workflow reliability or UI latency. A durable dispatch record preserves traceability and keeps external notification calls off the critical request path.
- **Official docs reviewed**:
  - Node.js Documentation — Events / `EventEmitter`: https://nodejs.org/api/events.html
- **Version/context checked**: Current Node.js events documentation covering synchronous listener execution, `once()`, and the requirement to handle `'error'` events safely.
- **Alternatives considered**: Inline synchronous notification-service calls inside the approval request (rejected because they threaten latency and couple user actions to network failures); raw in-process event listeners only (rejected because process crashes or unhandled errors can lose notifications).

## Decision 5: Test workflow legality with Jest and role-based UX paths with Playwright

- **Decision**: Use Jest for focused backend/service tests around policies, transitions, compatibility fields, and dispatcher behavior, and use Playwright for browser-level role and approval workflow coverage.
- **Rationale**: Jest is already the repository test tool for JavaScript/TypeScript logic and is appropriate for fast, targeted service assertions. Playwright automatically waits for actionability, provides isolated browser contexts per test, and is well suited for validating that viewers stay read-only, editors can propose, and release managers can approve/reject through the real UI.
- **Official docs reviewed**:
  - Jest — Getting Started: https://jestjs.io/docs/getting-started
  - Playwright — Writing Tests: https://playwright.dev/docs/writing-tests
- **Version/context checked**: Current Jest getting-started docs and current Playwright test-writing docs covering assertions, automatic waiting, and test isolation.
- **Alternatives considered**: E2E-only coverage (rejected because state-machine edge cases and compatibility fields need faster unit/service checks); backend-only tests without browser coverage (rejected because permission affordances and approval dialogs are user-visible requirements).

## Decision 6: Keep manager queues query-efficient by grouping pending approvals at the API layer

- **Decision**: Build `GET /api/release-windows/approvals/pending` as a backend query that groups proposed windows by `productArea`, orders items predictably, and returns pagination metadata.
- **Rationale**: The feature explicitly calls for grouping by product area and must support 300 concurrent users during planning week. Returning already-grouped data reduces frontend processing, keeps payloads predictable, and aligns with the server-first data-fetching approach in the Next.js architecture chosen above.
- **Official docs reviewed**:
  - Next.js — Server and Client Components: https://nextjs.org/docs/app/getting-started/server-and-client-components
  - OpenAPI Specification (latest HTML source of truth): https://spec.openapis.org/oas/latest.html
- **Version/context checked**: Current Next.js server/client guidance and latest OpenAPI specification page used for grouped response modeling.
- **Alternatives considered**: Fetching all proposed windows and grouping in the browser (rejected for latency and payload size); scheduled materialized views (rejected because approval queues need near-real-time accuracy during planning week).
