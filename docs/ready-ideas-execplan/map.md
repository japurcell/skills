## Destination

Produce one self-contained, implementation-ready ExecPlan at `docs/ready-ideas-execplan/ExecPlan.md` covering all eight problems in the Ready section of `docs/ideas.md`. Its independently verifiable milestones must cover Copilot, Gemini, and Codex on supported platforms. Windows-specific reports require automated tests and a precise live-check checklist; live Windows runs are not an acceptance gate.

## Notes

This map plans the work; it does not implement the eight changes. Keep each underlying problem in scope even when its proposed fix proves unsuitable. Use the `exec-plans` skill for the destination, `grilling` for human decisions, and `research` for external facts. The referenced `domain-modeling` skill is not installed, so use Wayfinder's explicit question, dependency, and resolution structure. `docs/ideas.md` and generated-hook rules in `.agents/instructions/hooks.md` provide starting context. Installed hook behavior differs from repository source and must be distinguished in the ExecPlan.

## Decisions so far

- [Provider Hook Capabilities](tickets/provider-hook-capabilities.md): provider-specific hook contracts permit pre-tool checks, with different display, timeout, trust, and Windows rules.

## Not yet specified

<!-- FOG START -->
Further decisions may emerge from Markdown link policy, command redaction, and limits of repository guardrails. The final milestone order and shared test matrix depend on the eight item decisions.
<!-- FOG END -->

## Out of scope

Implementing the eight changes during this wayfinding effort. The destination is an ExecPlan for that work.
