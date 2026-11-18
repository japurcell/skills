# Outcome-Oriented Execution

**Principle:** Optimize for the intended, verifiable end state rather than preserving smooth intermediate states.

## Why

In large refactors and migrations, forcing every intermediate step to stay fully stable often creates temporary compatibility code that becomes long-lived debt. The cleaner strategy is to converge directly on the target architecture and prove correctness at explicit verification boundaries.

## Core Rule

- Prioritize end-state integrity over transitional stability.
- Intermediate breakage is acceptable when it is planned, scoped, and reversible.
- Final verification is non-negotiable.

## Guardrails

- Use this for planned rewrites/migrations with explicit phase boundaries.
- Declare where temporary breakage is acceptable and where it is not.
- Keep high-signal checks for actively touched areas while migrating.
- Require full static and runtime verification at plan completion.

For a coordinated internal API change, migrate all callers and their contract tests in the same wave, then remove the old entry point and tests that only exercise its obsolete implementation. Preserve compatibility for external consumers who still depend on it.

## Anti-Pattern

Preserving obsolete paths only to keep every intermediate step green when no long-term compatibility is needed.

## Relationship to Other Principles

This complements [principles/subtract-before-you-add](subtract-before-you-add.md) by making outcome-first sequencing explicit.

It also reinforces [principles/prove-it-works](prove-it-works.md): the outcome must be proven, not assumed.

[upstream principle-migrate-callers-then-delete-legacy-apis](https://github.com/cursor/plugins/blob/35a90942a7f02e1ebbc2443643179815f2147954/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md)
