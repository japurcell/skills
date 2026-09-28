# High-Rate Hook Performance Review

**Type:** grilling
**Status:** open
**Blocked By:** provider-lifecycle-facts.md, repository-state-retirement.md, markdown-health-retirement.md
**Research Dir:** none

## Question

Which retained hook registrations can run once per tool call or more often in each provider, including events beyond pre- and post-tool use? Decide the review's measurement method, representative workloads, baseline and comparison evidence, acceptable latency and noise, review findings format, and when a finding requires an implementation fix. Account for process startup, synchronous work, timeouts, and any notification overhead without inventing a performance target before measuring.

---
