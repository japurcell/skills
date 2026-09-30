# Just-in-time Context

## Destination

An implementation-ready specification for a reusable, autonomous context management system, piloted in this repository and supporting Codex, Copilot, and Gemini. The route is clear when retrieval, learning, maintenance, provider guarantees, validation, and adoption have no unresolved decisions that block implementation.

## Notes

- This effort plans the system. It does not implement or install it.
- The user chooses a reusable system across their repositories, with this repository as the pilot.
- The first version supports Codex, Copilot, and Gemini. Exact supported surfaces and guarantees require evidence.
- The user authorizes automatic additions, corrections, reorganization, and pruning. Maintenance must be reversible and supported by evidence; explicit user instructions remain authoritative.
- A unified skill with recall, learn, and dream entry points and nested AGENTS.md files are hypotheses, not selected architecture.
- Use wayfinder and grilling for decision sessions. The user explicitly waives wayfinder's domain-modeling dependency for this effort.
- Research sessions use research and official-sources. Codex product research also uses openai-docs. Do not resolve human decision tickets while charting this map.
- Resolve at most one human decision ticket per session. Research tickets may resolve in parallel. Each assignee owns its ticket and research directory; only the coordinating session updates this map.
- The user explicitly chooses docs/just-in-time-context/ for the map and supporting artifacts, overriding wayfinder's scratchpad default.
- The original idea and source references are in [Just-in-time Context Brief](brief.md). Local findings are in [Current Context Lifecycle](baseline.md).
- Discover open decisions in tickets/. Verify every exact filename in Blocked By before claiming a ticket.

## Decisions so far

<!-- Closed tickets only. Gist each result here; its full resolution lives in its ticket. -->

- [Provider Lifecycle Capabilities](tickets/provider-lifecycle-capabilities.md): Providers differ in context delivery, continuation, shutdown, and idle execution; supported surfaces need deployed-version proof.
- [Reference Evidence](tickets/reference-evidence.md): ACE directly evaluates incremental external-context adaptation; nested instruction discovery and autonomous publication require separate contracts.
- [Success Criteria](tickets/success-criteria.md): Quality and recovery gates accompany measurable context savings, bounded latency, and paired longitudinal evidence on every supported surface.
- [Knowledge Evidence Policy](tickets/knowledge-evidence-policy.md): Compact, proportional evidence preserves explicit policy; uncertain claims remain candidates and pruning requires evidence beyond inactivity.

## Not yet specified

<!-- FOG START -->

- Provider-specific exceptions may expose new decisions when documented capabilities and acceptance measurements are exercised on selected deployed versions and harnesses. Whether native context delivery and maintenance work are fully observable may depend on those selections.
- A concrete walkthrough of the selected lifecycle may reveal missing knowledge states, recovery cases, or task boundaries that cannot yet be specified, including exceptional transitions involving candidates and disputed sources.
- Repository-specific migration exceptions and the shape of a minimal pilot remain unclear until the knowledge representation and lifecycle contracts are selected. The final scenario mix may expose further gaps in the accepted quality checks and repeated-cycle evidence.

<!-- FOG END -->

## Out of scope

- Product implementation, installation, rollout, and migration execution in this planning effort.
- Changes to model weights or model training. Self-improving context means improving external knowledge and its management.
- The other ideas in docs/ideas.md, except evidence relevant to this context management system.
