# Just-in-time Context Brief

## Destination

Plan an implementation-ready specification for a reusable, autonomous context management system. Pilot it in this repository and support Codex, Copilot, and Gemini in the first version.

The active [Just-in-time Context map](map.md) and its tickets are stored in this directory, as explicitly requested by the user. The map resolves decisions before implementation begins.

## Original idea

The current agent knowledge and memory workflow is spread across AGENTS.md, .agents/skills/update-agent-docs, and .agents/skills/clean-agent-docs:

1. At session startup, Agent Orientation directs agents to the knowledge map and relevant context.
2. At the end of a work session, update-agent-docs repairs and refreshes knowledge with durable findings.
3. Periodically, clean-agent-docs removes stale, irrelevant, or duplicated guidance.

The goal is a self-improving context management system that manages knowledge through structured processes and hooks without depending on agents remembering to update or refresh it.

Two proposed mechanisms require validation and may be rejected:

- A single progressively disclosed lifecycle skill with subcommands such as /agent-brain recall, /agent-brain learn, and /agent-brain dream. Hooks would trigger the appropriate stage.
- Nested AGENTS.md files as a mechanism for loading relevant guidance when work reaches a particular area.

## Agreed scope

- Build a reusable system for the user's repositories, with this repository as the pilot.
- Support Codex, Copilot, and Gemini. Research must establish each provider's supported surfaces and guarantees.
- Permit automatic additions, corrections, reorganization, and pruning. Maintenance is reversible and supported by source evidence; explicit user instructions remain authoritative.
- Produce decisions and an implementation-ready specification. Do not implement or install the system during wayfinding.
- Domain-modeling is not required for this effort, as explicitly directed by the user.
- Store the map and supporting artifacts under docs/just-in-time-context/.

## References

- [Harness engineering repository](https://github.com/lopopolo/harness-engineering)
- [Just-in-time context](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/just-in-time-context)
- [Use AGENTS.md as a map](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/just-in-time-context#use-agentsmd-as-a-map)
- [Feedback](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/feedback)
- [Domain modeling](https://github.com/lopopolo/harness-engineering/tree/trunk/docs/domain-modeling)
- [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/html/2510.04618v3), originally labeled "Self-improving LLMs" in the idea inbox
- [A Complete Guide to AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md)

These references are evidence to evaluate, not an architecture mandate.
