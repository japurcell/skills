# Agent Asset Distribution

## Destination

Produce a decision-ready recommendation for distributing selected skills, custom agents, hooks, and instructions at repository scope, including easy updates to installed assets, while preserving the current user-global installation workflow. Compare native plugins and extensions with simpler distribution methods across major coding agents before changing installers.

## Notes

- This effort is research and planning. Do not implement installer or package changes.
- The user explicitly promoted this entire effort from .agents/scratchpad/agent-asset-distribution to docs/agent-asset-distribution on 2026-09-29. Keep the map, tickets, and cited findings here.
- Primary clients: Codex, GitHub Copilot (CLI and VS Code), Gemini CLI, Claude Code, Cursor, and OpenCode. Survey secondary clients when they affect portability.
- Support both committed team setup and local untracked setup, with committed team setup as the default. The user confirmed this preference on 2026-09-29.
- Prefer quality, simplicity, robustness, reproducibility, scalability, and long-term maintainability over development cost.
- Distinguish package distribution, installation scope, activation scope, and repository configuration. Project-scoped enablement does not necessarily place package files in a repository.
- Consult wayfinder, research, and official-sources; use openai-docs for Codex. Use grilling for human decisions. The referenced domain-modeling skill remains unavailable after checking repository sources, installed skills, and plugin caches. On 2026-09-29, the user explicitly authorized proceeding with grilling and the completed research without that skill.
- Research date: 2026-09-29. Record preview and experimental status, product surface, version evidence, trust requirements, and uncertainty.
- Research agents own only their assigned ticket and research directory. The coordinating agent owns this map, synthesis, and local inventory.
- Existing installers and installed user directories remain unchanged during this effort.
- Read the [distribution recommendation](recommendation.md) for the synthesis and the [current source inventory](local-inventory.md) for repository-specific constraints. Recommendations remain distinct from approved implementation decisions.
- The human decision interview is complete. The separate [implementation ExecPlan](../agent-asset-installer/ExecPlan.md) is prepared. Use the [current handoff](handoff.md) for the resume gate and next milestone; the closed decision ticket is the contract's authority.

## Decisions so far

- [Codex and Copilot Distribution Support](tickets/codex-copilot-distribution.md): Shared skills and plugin core coexist with native agent, hook, and product-surface constraints.
- [Claude Code and Gemini Distribution Support](tickets/claude-gemini-distribution.md): Native package formats differ, and committed workspace activation does not install teammates' package copies.
- [Portable Distribution Methods and Additional Clients](tickets/portable-distribution-methods.md): Committed copies plus selective client adapters cover complete bundles; skills tooling and shared plugins cover narrower portable components.
- [Choose the Distribution Contract](tickets/choose-distribution-contract.md): Selective installation, explicit updates, and safe managed pruning; native packages later, without a rollback feature.

## Not yet specified

<!-- FOG START -->
The route is clear and this map's destination is reached. All four tickets are closed, with no remaining in-scope decision or fog. Implementation planning is a separate next effort.
<!-- FOG END -->

## Out of scope

- Implementing installers, publishing packages or marketplaces, changing user-global configuration, and installing experimental clients during this research session.
- Building a remote service solely to distribute existing local instruction files.
- Implementation ExecPlans, executable migration steps, release automation, and live compatibility fixtures. These belong to a separate effort after this approved distribution contract.
