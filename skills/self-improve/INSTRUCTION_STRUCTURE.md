# Instruction Structure

Use this when placing guidance, refactoring files, or resolving conflicts.

## Placement

| Location | Use for |
| --- | --- |
| `./AGENTS.md` | Project-wide guidance that should always load. |
| `./**/AGENTS.md` | Rules for a directory, module, package, or subsystem. |
| Linked docs | Long procedures, examples, architecture notes, release steps, migrations, generated-code rules, or rare workflows. |

Keep root short and prompt-light. Link instead of repeating.

## Root `AGENTS.md` Should Usually Contain

- Short project description.
- Package manager or runtime if non-default.
- Universal build/test/typecheck/validation commands.
- Repo-wide style or workflow constraints.
- Links to major topic docs.

## Scoped `AGENTS.md` Should Usually Contain

- Frontend-only or backend-only commands.
- Directory-specific testing rules.
- Module architecture constraints.
- Fixture, migration, deployment, or generated-code rules for that scope.

## Refactor When

- Root is hard to scan, roughly over 120 lines, or full of rare detail.
- Global and scoped rules are mixed.
- Multiple files repeat the same rule.
- Rules conflict.
- Linked docs are stale, ignored, missing, or orphaned.
- The user asked for cleanup.

## Usually Do Not Refactor When

- The current file is short and clear.
- Only one small durable learning needs to be added.
- The structure is imperfect but not harmful.
- Refactoring would create more files than the project needs.

## Conflict Rules

- Resolve contradictions; do not keep both.
- Prefer the most specific applicable scope.
- Prefer current, tested, repo-specific guidance over generic wording.
- If uncertain, make the best supported choice and state the assumption.
- When moving guidance, update the destination in the same change before deleting the source.

## Red Flags

- Missing, empty, or oversized root `AGENTS.md`.
- Mixed global and scoped guidance.
- Duplicate or conflicting rules.
- Missing, stale, or orphaned linked docs.
- Vague or non-actionable rules.
- Durable learnings not captured.
- Non-standard commands undocumented.
- User corrections not preserved.
- One-offs added as standing instructions.
- Guidance removed from one file without appearing in the destination.

## Final Check

- Relevant `AGENTS.md` files found.
- Direct linked instruction docs reviewed.
- Durable items kept; low-value items skipped.
- Guidance placed at the right scope.
- Root remains minimal.
- Moved rules exist in the destination.
- Duplicates removed or justified.
- Conflicts resolved or assumptions stated.
- No orphan links remain.
