# Instruction Structure

Use when placing, refactoring, or resolving conflicts in instruction files.

## Placement

| Location | Use for |
| --- | --- |
| `./AGENTS.md` | Repo-wide guidance that should always load. |
| `./**/AGENTS.md` | Rules for a directory, module, package, or subsystem. |
| Linked docs | Long procedures, examples, architecture notes, release steps, migrations, generated-code rules, or rare/branch-specific workflows. |

Keep root short. Link instead of repeating.

## Root `AGENTS.md`

Usually include only:

- Short project description.
- Non-default package manager, runtime, or setup.
- Universal build/test/typecheck/validation commands.
- Repo-wide style or workflow constraints.
- Links to major topic docs.

## Scoped `AGENTS.md`

Use for:

- Frontend-only, backend-only, or package-specific commands.
- Directory-specific tests or fixtures.
- Module architecture constraints.
- Migration, deployment, or generated-code rules for that scope.

## Linked Docs

Use when guidance is:

- Long or procedural.
- Example-heavy.
- Rarely needed.
- Split by workflow branch, subsystem, or role.
- Too detailed for root but still durable.

## Refactor When

- Root is hard to scan, roughly over 120 lines, or full of rare detail.
- Global and scoped rules are mixed.
- Multiple files repeat the same rule.
- Rules conflict.
- Linked docs are stale, missing, ignored, or orphaned.
- User asked for cleanup.

## Usually Do Not Refactor When

- Current files are short and clear.
- Only one small durable learning needs to be added.
- Structure is imperfect but not harmful.
- Refactoring would create unnecessary files.

## Conflict Rules

- Prefer the most specific applicable scope.
- Prefer current, tested, repo-specific guidance over generic wording.
- Resolve contradictions; do not preserve both.
- If uncertain, make the best supported choice and state the assumption.
- When moving guidance, add it to the destination before deleting the source.

## Final Check

- Relevant `AGENTS.md` files found.
- Direct linked docs reviewed.
- Durable guidance kept; low-value items skipped.
- Guidance placed at the right scope.
- Root remains minimal.
- Moved rules exist at the destination.
- Duplicates removed or justified.
- Conflicts resolved or assumptions stated.
- No orphan links remain.
