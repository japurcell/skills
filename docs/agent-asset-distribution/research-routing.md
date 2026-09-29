# Research Routing

These provisional routes follow the installed subagent-model-router catalog and the runtime's exact model identifiers. The chosen model and effort are explicitly applied at launch.

## Route for all three research tickets

- tier: Standard
- model: gpt-6-luna
- effort: max
- reason: Primary-source research requires careful reconciliation of evolving package standards, installation scope, product surfaces, and unsupported capabilities. Comparing mechanisms requires synthesis beyond bounded fact lookup. The catalog lists this as the cheapest Standard candidate. Task-specific accuracy remains unproven, so the coordinating agent will review citations and qualify uncertain support.
- escalation_trigger: Conflicting primary sources, inaccessible current documentation, or incorrect cross-surface or package compatibility claims.
- fallback: gpt-6-sol with medium effort.

Tickets: Codex and Copilot Distribution Support; Claude Code and Gemini Distribution Support; Portable Distribution Methods and Additional Clients. Each has non-overlapping write ownership.

## Route for the release-policy fact check

- tier: Fast
- model: gpt-6-luna
- effort: medium
- reason: Bounded, read-only inspection of local Git tags and existing release/update conventions. No implementation, external research, or security judgment. The lowest capable exposed model is provisional; results require source evidence. Exact token pricing was not needed for this route.
- escalation_trigger: Conflicting release conventions or inability to distinguish observed local tags from promised release behavior.
- fallback: gpt-5.6-luna with medium effort if unavailable; gpt-6.1-sol with medium effort only if focused verification cannot resolve a conflict.

The runtime explicitly applied the selected model and effort with no inherited turns. The agent had no write ownership. Its scoped findings are recorded in [the source inventory](local-inventory.md); no remote release state was checked.

## Routes for the existing-repository design review

For Evaluate APM Reuse and Evaluate ECC Ownership:

- tier: Standard
- model: gpt-6-luna
- effort: max
- reason: Reconcile first-party documentation with connected lifecycle code and the explicit requirements supplied in the task. This is external architectural fact-finding, with no implementation or general security audit. The catalog's lowest-cost Standard candidate is provisional; the coordinator will review evidence and qualify unexecuted behavior. Copilot pricing is only a routing reference, not this runtime's measured billing.
- escalation_trigger: Documentation/source disagreement that cannot be resolved by focused inspection, missing implementation evidence for safety claims, or inability to distinguish wrapping from duplicating lifecycle responsibility.
- fallback: gpt-6.1-sol with medium effort.

For Evaluate Distribution References:

- tier: Fast
- model: gpt-6-luna
- effort: medium
- reason: Bounded first-party documentation and targeted source lookup across four narrower examples. No implementation, installation, or high-stakes safety judgment. Use exact source evidence and report uncertainty rather than extrapolating.
- escalation_trigger: Conflicting documentation/source that affects a recommended contract change, or insufficient evidence for integrity/update semantics.
- fallback: gpt-5.6-luna with medium effort for availability; gpt-6.1-sol with medium effort for unresolved reasoning gaps.

Each agent owns only its assigned research ticket and findings directory. Model and effort are applied explicitly with no inherited turns. The coordinator owns synthesis, map, handoff, and any approved plan amendment.
