# Reference Evidence

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/reference-evidence/

## Question

Which mechanisms in the user-provided references support or challenge a unified lifecycle skill, nested AGENTS.md routing, autonomous knowledge refresh, and periodic pruning?

Inspect the harness-engineering repository's just-in-time context, feedback, and domain-modeling examples; Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models at https://arxiv.org/html/2510.04618v3; and A Complete Guide to AGENTS.md at https://www.aihero.dev/a-complete-guide-to-agents-md. Trace platform-behavior claims in the guide to primary sources. Distinguish source code, reported practice, experiments, and unsupported assumptions. Identify where the paper's evaluated context-adaptation mechanisms and results do or do not establish claims about external repository memory. Include concrete counterexamples and limits without selecting an architecture.

The original URLs are retained in docs/just-in-time-context/brief.md. Write cited findings to the assigned research directory. Append a concise factual Resolution here before closing this ticket. Do not resolve human decision tickets or update map.md.

---

## Resolution

[Reference findings](../research/reference-evidence/findings.md) distinguish design guidance, reported practice, source-code mechanisms, empirical context adaptation, and untested transfer assumptions. The cited paper is Agentic Context Engineering (ACE), which adapts external context without model-weight changes. Incremental updates and evidence-backed promotion have support; whole-context rewrites, raw telemetry promotion, and uniform nested-file behavior have concrete limitations. Provider-specific primary documentation qualifies the AIHero guide. No lifecycle architecture was selected and no implementation or configuration was changed.
