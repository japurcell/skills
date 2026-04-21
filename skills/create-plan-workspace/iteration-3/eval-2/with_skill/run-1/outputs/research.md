# Research: Release Calendar Role Controls

## Decision 1: Baseline runtime and verification stack

- Decision: Plan against an existing Node.js LTS backend and retain Jest + Playwright as the verification stack, with targeted package-manager passthrough commands instead of inventing a new monorepo-wide runner.
- Rationale: The spec already fixes the backend/frontend stack and current test tools. Node.js LTS is the safest baseline for a planning artifact intended for near-term implementation, and targeted commands align with the benchmark repository guidance that there is no single repo-wide test command.
- Official docs reviewed:
  - Node.js Releases — https://nodejs.org/en/about/previous-releases
  - Jest Getting Started — https://jestjs.io/docs/getting-started
  - Jest CLI — https://jestjs.io/docs/cli
  - Playwright Parallelism — https://playwright.dev/docs/test-parallel
- Version/context checked: On 2026-04-21 the Node.js releases page listed Node 24, 22, and 20 as LTS lines, confirming LTS is the production-safe baseline. Jest current docs confirm package-manager passthrough (`npm test -- ...`) and focused CLI targeting. Playwright current docs confirm file-level parallelism by default and worker controls for CI tuning.
- Alternatives considered:
  - Upgrading the plan target to a bleeding-edge Node Current line: rejected because the spec does not ask for a platform migration.
  - Replacing Jest/Playwright with a new test framework: rejected because the spec explicitly says those tools are already in use.

## Decision 2: HTTP contract strategy and compatibility model

- Decision: Keep the API evolution additive by introducing one transition endpoint (`POST /api/release-windows/{releaseWindowId}/transitions`) plus one grouped approvals read endpoint (`GET /api/release-windows/approvals/pending`), and document both in an OpenAPI contract that stays compatible with existing read consumers.
- Rationale: A single transition endpoint centralizes workflow validation, makes the role/state matrix testable in one place, and satisfies the one-quarter backward-compatibility window by avoiding a forced v2 cutover. An OpenAPI contract gives `/create-tasks` a concrete interface artifact to implement and test.
- Official docs reviewed:
  - OpenAPI Specification — https://spec.openapis.org/oas/latest.html
- Version/context checked: The official OpenAPI HTML source-of-truth page identifies the latest specification stream (3.2.0). The contract artifact in this run uses an OpenAPI 3.1-compatible shape for broad tooling interoperability while staying within standard OAS semantics.
- Alternatives considered:
  - Separate action endpoints such as `/approve`, `/reject`, and `/cancel`: rejected because validation and audit logic would fragment.
  - A breaking `/v2` workflow API immediately: rejected because the spec explicitly requires one quarter of backward-compatible changes.

## Decision 3: Next.js rendering and data freshness strategy

- Decision: Use Server Components for initial calendar and approval-queue data fetches, isolate interactive controls in Client Components, and avoid shared static caching for role-sensitive approval data so managers always see current pending items.
- Rationale: Next.js guidance recommends Server Components for fetching close to the source and Client Components only where stateful interaction is needed. Route Handlers and role-sensitive approval data should stay request-time rather than statically cached, while focused client-side refetch after mutations preserves the perceived-latency budget without introducing real-time infrastructure.
- Official docs reviewed:
  - Next.js Server and Client Components — https://nextjs.org/docs/app/getting-started/server-and-client-components
  - Next.js Route Handlers — https://nextjs.org/docs/app/getting-started/route-handlers
  - Next.js Caching and Revalidating — https://nextjs.org/docs/app/getting-started/caching-and-revalidating
- Version/context checked: The referenced Next.js App Router docs were updated April 15, 2026. They confirm Server Components as the default, Client Components for interactivity, and that Route Handlers are not cached by default unless `GET` caching is explicitly enabled.
- Alternatives considered:
  - Making the entire calendar feature a large Client Component tree: rejected because it increases shipped JavaScript and weakens server-side data locality.
  - Static caching of the pending approvals queue: rejected because approval state is role-sensitive and changes frequently during planning week.
  - Adding WebSocket synchronization in the initial slice: rejected as unnecessary scope for the stated feature goals.

## Decision 4: Workflow state model and audit trail

- Decision: Implement a single backend transition service with an explicit allowed-transition matrix, append-only transition history, and optimistic concurrency checks on the canonical release-window row.
- Rationale: The spec requires actor metadata and a reason for every state transition, which maps naturally to an immutable audit log and a single authoritative transition service. Optimistic locking protects concurrent edits during planning week without introducing long-lived locks that would hurt responsiveness.
- Official docs reviewed: none applicable beyond the product stack above; this decision is driven by domain requirements in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-release-calendar-roles.md`, not by a vendor-specific library contract.
- Version/context checked: N/A — internal domain design choice based on the spec's required states, roles, and concurrency target.
- Alternatives considered:
  - Free-form status updates validated separately by each handler: rejected because audit and authorization behavior would drift.
  - Database triggers as the sole workflow guard: rejected because application error handling and testability would be weaker.
  - Pessimistic row locking on every mutation: rejected because it risks harming the 150ms perceived-latency goal under concurrent planning activity.

## Decision 5: Notification integration boundary

- Decision: Treat the notification service as an external dependency behind a provider-agnostic adapter and durable outbox, and limit this plan to approval/rejection event contracts plus retry semantics until provider-specific documentation is known.
- Rationale: The spec requires notification integration but does not identify the vendor or payload contract. An adapter boundary and outbox let implementation proceed safely without pretending unsupported details are settled, while still giving `/create-tasks` concrete work items around event publishing, retries, and observability.
- Official docs reviewed: none available from the spec because the notification provider is unspecified.
- Version/context checked: N/A — provider-specific documentation remains an implementation follow-up.
- Alternatives considered:
  - Hard-coding a specific notification vendor now: rejected because the spec does not authorize that assumption.
  - Inline synchronous delivery during approval/rejection requests: rejected because transient notification failures would either slow the UX or incorrectly fail workflow transitions.

## Decision 6: End-to-end role testing strategy

- Decision: Use distinct authenticated Playwright states for viewer/editor/release-manager flows and keep backend workflow assertions in Jest integration tests, including async assertions around outbox creation and grouped approval reads.
- Rationale: Playwright's auth guidance recommends avoiding a shared authenticated state when tests mutate server-side state, which this workflow does. Jest remains the fastest place to prove role-policy, state-machine, and persistence rules, while Playwright verifies the user-visible role gating and approval flows.
- Official docs reviewed:
  - Playwright Authentication — https://playwright.dev/docs/auth
  - Playwright Parallelism — https://playwright.dev/docs/test-parallel
  - Jest Async Testing — https://jestjs.io/docs/next/asynchronous
- Version/context checked: Playwright current docs note that one shared account is inappropriate when tests modify server-side state and describe per-worker/per-project auth strategies. Jest current async docs confirm promise/async-await patterns needed to assert notification enqueueing and other async side effects deterministically.
- Alternatives considered:
  - UI-only validation with no backend integration tests: rejected because authorization and state-machine bugs would be slower to isolate.
  - One shared Playwright account for all roles: rejected because role-specific state and approval mutations would interfere across tests.

## Unknown resolution summary

Resolved items for planning:

- The implementation baseline stays on the existing Node.js + Next.js + Jest + Playwright stack described by the spec.
- The external interface surface is narrowed to one additive transition write endpoint and one grouped pending-approvals read endpoint.
- The frontend/backed boundary, caching posture, and test responsibilities are explicit enough for `/create-tasks` decomposition.
- The unspecified notification vendor remains a follow-up risk, but it no longer blocks planning because the adapter/outbox boundary is defined.

Remaining follow-up (non-blocking): confirm the actual notification provider contract and the exact monorepo package names before coding.
