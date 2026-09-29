# Agent Asset Distribution

## Destination

Produce a decision-ready recommendation for distributing selected skills, custom agents, hooks, and instructions at repository scope while preserving the current user-global installation workflow. Compare native plugins and extensions with simpler distribution methods across major coding agents before changing installers.

## Notes

- This effort is research and planning. Do not implement installer or package changes.
- The user explicitly promoted this entire effort from .agents/scratchpad/agent-asset-distribution to docs/agent-asset-distribution on 2026-09-29. Keep the map, tickets, and cited findings here.
- Primary clients: Codex, GitHub Copilot (CLI and VS Code), Gemini CLI, Claude Code, Cursor, and OpenCode. Survey secondary clients when they affect portability.
- Support both committed team setup and local untracked setup, with committed team setup as the default. The user confirmed this preference on 2026-09-29.
- Prefer quality, simplicity, robustness, reproducibility, scalability, and long-term maintainability over development cost.
- Distinguish package distribution, installation scope, activation scope, and repository configuration. Project-scoped enablement does not necessarily place package files in a repository.
- Consult wayfinder, research, and official-sources; use openai-docs for Codex. Use grilling for human decisions. The referenced domain-modeling skill is unavailable in installed and repository skill locations; research does not depend on it. Revisit that dependency before a design interview.
- Research date: 2026-09-29. Record preview and experimental status, product surface, version evidence, trust requirements, and uncertainty.
- Research agents own only their assigned ticket and research directory. The coordinating agent owns this map, synthesis, and local inventory.
- Existing installers and installed user directories remain unchanged during this effort.
- Read the [distribution recommendation](recommendation.md) for the synthesis and the [current source inventory](local-inventory.md) for repository-specific constraints. Recommendations remain distinct from approved implementation decisions.

## Decisions so far

- [Codex and Copilot Distribution Support](tickets/codex-copilot-distribution.md): Shared skills and plugin core coexist with native agent, hook, and product-surface constraints.
- [Claude Code and Gemini Distribution Support](tickets/claude-gemini-distribution.md): Native package formats differ, and committed workspace activation does not install teammates' package copies.
- [Portable Distribution Methods and Additional Clients](tickets/portable-distribution-methods.md): Committed copies plus selective client adapters cover complete bundles; skills tooling and shared plugins cover narrower portable components.

## Not yet specified

<!-- FOG START -->
No additional research question is currently too vague to ticket. The remaining distribution choice is an open decision ticket; its prerequisites are closed. Implementation planning follows after that choice.
<!-- FOG END -->

## Out of scope

- Implementing installers, publishing packages or marketplaces, changing user-global configuration, and installing experimental clients during this research session.
- Building a remote service solely to distribute existing local instruction files.
- Designing executable migration steps, release automation, and live compatibility fixtures before the distribution contract is chosen.
