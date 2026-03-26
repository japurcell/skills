## Uncertainties

- Policy strictness boundary for Standard track is still a product decision: always require artifact vs require only on deferred/delegated work.
- If future workflow introduces implementation-brief.md again, policy must avoid conflicting artifact types.

## Trade-offs

- Stronger MUST-level enforcement increases reliability and evalability, but adds overhead for bounded tasks.
- Keeping handoff-plan.md as the single enforced artifact minimizes migration risk and aligns with current feature-dev template.
- Adding eval assertions for physical artifact creation improves confidence but may require fixture updates when benchmark structure evolves.

## Human Review Items

- Confirm desired Standard-track behavior for same-turn completed implementation.
- Confirm whether enforcement language should use strict RFC-2119 terms throughout SKILL.md for consistency.
