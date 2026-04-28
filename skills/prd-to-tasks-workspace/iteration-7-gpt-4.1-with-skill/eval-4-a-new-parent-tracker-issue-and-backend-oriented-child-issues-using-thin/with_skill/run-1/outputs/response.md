# Parent tracker draft

**Title:** Webhook Retry Operations: Delivery Persistence, Replay API, and Metrics

## Source

This tracker covers the implementation of webhook retry operations as described in the PRD: when a delivery fails, the service should persist retry attempts, expose an internal admin API to replay a failed delivery, and emit retry outcome metrics to logs. No end-user or admin UI is included in this phase; work is limited to API handlers, background workers, and persistence.

## Task graph

- [ ] W1 - Persist webhook retry attempts - AFK - blocked by none
- [ ] W2 - Internal admin API to replay failed delivery - AFK - blocked by #<child-1>
- [ ] W3 - Emit retry outcome metrics to logs - AFK - blocked by #<child-2>

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.
