# Just-in-time Context

## Destination

An implementation-ready specification for a reusable, autonomous context management system, piloted in this repository and supporting Codex, Copilot, and Gemini. The route is clear when retrieval, learning, maintenance, provider guarantees, validation, and adoption have no unresolved decisions that block implementation.

## Notes

- This effort plans the system. It does not implement or install it.
- The user chooses a reusable system across their repositories, with this repository as the pilot.
- The first-version scope and lifecycle guarantees are selected in [Lifecycle Guarantees](tickets/lifecycle-guarantees.md). Deployed versions and entry paths require certification before support is claimed.
- The user authorizes automatic additions, corrections, reorganization, and pruning. Maintenance must be reversible and supported by evidence; explicit user instructions remain authoritative.
- Knowledge representation and skill/CLI boundaries are selected in [Context Organization and Skill Boundary](tickets/context-organization-and-skill-boundary.md). That ticket owns the names, responsibilities, and integration boundaries.
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
- [Context Retrieval Contract](tickets/context-retrieval-contract.md): Scoped guidance arrives before dependent work, preserves meaning and uncertainty, and is checked and restored across context changes.
- [Lifecycle Guarantees](tickets/lifecycle-guarantees.md): Codex desktop and three CLIs require automatic stages, verified completion, next-event recovery, and separately certified native or fallback paths.
- [Context Organization and Skill Boundary](tickets/context-organization-and-skill-boundary.md): Indexed knowledge and the cooperative agent-brain skill/CLI use foreground semantics, compact metadata, and separately certified native adapters.
- [Maintenance Scheduling and Pruning](tickets/maintenance-scheduling-and-pruning.md): Foreground dream uses periodic bounded review with rotating coverage, evidenced pruning, and retention that protects unfinished work and reversible history.

## Not yet specified

<!-- FOG START -->

- Capability certification may expose an unexpected interaction among native events, invocation-context binding, and foreground continuation that requires another integration choice. Revisit exceptions beyond the selected lifecycle and scheduling contracts and the unsupported-path policy.
- A concrete legacy-repository pilot may expose unanticipated interactions among protected documents, existing metadata, custom hooks, and worktree state. Ordinary setup, batch limits, retention implementation, recovery, and pilot validation belong to the live tickets; newly exposed exceptions may need another decision.

<!-- FOG END -->

## Out of scope

- Product implementation, installation, rollout, and migration execution in this planning effort.
- First-version VS Code Local and Copilot Agent Host support is deferred to a later version by [Lifecycle Guarantees](tickets/lifecycle-guarantees.md).
- Changes to model weights or model training. Self-improving context means improving external knowledge and its management.
- The other ideas in docs/ideas.md, except evidence relevant to this context management system.
