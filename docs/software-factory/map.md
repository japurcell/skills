# Customizable software factory

## Destination

An implementation-ready specification for a fully customizable, code-controlled agentic factory: its workflow and task contracts, execution model, skill installation, live session UI, and improvement process are decided well enough to implement and test.

## Notes

- This is a planning map. The user chose this destination on 2026-10-12. Building the earlier Restate prototype is deferred.
- Consult wayfinder and the narrow skills needed for the selected ticket. Use grilling plus codebase-design for design conversations. The user explicitly approved this substitute for the unavailable domain-modeling skill on 2026-10-12.
- Consult prototype for a prototype ticket and research for a research ticket. Research tickets require an assigned research directory and a delegated researcher. No new research was launched merely to repeat the retained studies.
- Work one decision ticket per session, except delegated research. Claim its file before work. Check the exact filenames in Blocked By; only closed prerequisites unblock it. Human decisions require a live exchange.
- Closed requirements imported below come from the prior conversation. This charting session resolves no new design ticket. Recommendations remain proposals until their owning ticket records a resolution.
- Discover open sessions by searching the tickets directory. The map deliberately does not duplicate the open-ticket list.
- Preserve quality, simplicity, robustness, scalability, and long-term maintainability over development cost.
- Evidence entry points: [initial research](research.md) and [reviewable architecture documents](README.md). Source studies and simulations have different evidentiary limits.
- The user promoted this map and its tickets to `docs/software-factory/` on 2026-10-12 for version control. Resume wayfinder in this directory; do not recreate a scratchpad map.
- The [handoff](handoff.md) tracks current progress, verification limits, and the next session. Keep decision details in their owning tickets.

## Decisions so far

- [Confirmed factory requirements](tickets/confirmed-factory-requirements.md): code-owned deterministic flows, fully customizable workflows, per-step agent choices, skill installation, and real-time session visibility.

## Not yet specified

<!-- FOG START -->
- Additional workflow patterns and extension pressures may emerge when the authoring contract is exercised against real repository examples beyond the default six-stage use case.
- The chosen deployment and harness combination may reveal platform-specific process, permission, or recovery constraints not yet sharp enough to turn into a separate investigation.
- Observed improvement proposals may expose evaluation domains or ownership conflicts that need their own decisions after the core learning contract is set.
<!-- FOG END -->

## Out of scope

- Building or deploying the factory, installing a runtime into target repositories, and executing the earlier Restate prototype during this map's charting session.
- Performing application changes, creating PRs, or applying skill/prompt improvements as a side effect of planning.
- Implementation task decomposition and rollout scheduling; these follow the specification unless the user explicitly changes this map's destination.

