# Self Improve Reference

Use this reference when deciding whether to refactor `AGENTS.md` files, resolve conflicts, or reject low-value updates.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I can't decide which conflicting rule to keep." | Use best judgment and explain the choice. |
| "The root file is enough." | Scoped or linked docs may own that guidance better. |
| "That command is obvious." | Non-default commands are often high-value. |
| "The user didn't ask me to remember this." | Capture durable guidance when warranted. |
| "Broader wording is safer." | Specific rules are more useful. |
| "Leaving redundant rules is harmless." | Redundancy causes drift. |
| "I should update something anyway." | Do not force low-value changes. |
| "I moved it, so deleting the old text is enough." | Verify the destination doc was updated in the same change. |

## Red Flags

- Missing, empty, or overly long root `AGENTS.md`
- Mixed global and scoped guidance
- Duplicate or conflicting rules
- Missing, stale, or orphaned linked docs
- Vague or non-actionable rules
- Durable learnings not captured
- Non-standard commands or validation undocumented
- User corrections not preserved
- One-offs added as standing instructions
- Linked docs not checked before editing `AGENTS.md`
- Guidance removed from `AGENTS.md` without appearing in the destination doc

## Durable Learning Test

A learning is worth preserving when it is:

- Likely to recur
- Actionable by a future agent
- Specific to this repository, project, workflow, or user preference
- Not already documented

Good examples:

- `pnpm test -- --runInBand` - required because parallel tests conflict with shared fixtures.
- Use `src/generated/` types instead of hand-written API interfaces.
- Run `make validate-config` after editing deployment YAML.

Poor examples:

- The user asked a question about tests.
- The agent opened `package.json`.
- The repository has a README.
- Remember to be careful.

## Work-Artifact Mining

When session logs, handoff notes, or similar work artifacts exist, mine more than the summary:

- Read the summary and the detailed learning sections.
- Keep reusable rules from patterns, gotchas, or useful context when they explain future coding, testing, validation, or environment behavior.
- Good examples: test-framework constraints, validation rules that prevent false negatives, stable cache or replay fix shapes, anti-flake assertion tactics, and setup needed to reach production-only branches in tests.
- Poor examples: story IDs, temporary blockers, one-off filenames, or "this specific test failed once."

## Refactor Judgment Guide

Refactor when the current structure makes future behavior worse.

Usually refactor:

- Root `AGENTS.md` is too long to scan quickly
- Different scopes are mixed together
- Multiple files repeat the same rule
- Linked docs exist but are stale or ignored
- Rules conflict and would cause inconsistent agent behavior

Usually do not refactor:

- The file is short and clear
- There is only one small durable learning to add
- The structure is imperfect but not harmful
- Refactoring would create more files than the project needs

## Scope Placement Examples

Root `AGENTS.md`:

- Project-wide package manager
- Universal validation commands
- Repository-wide style constraints
- Links to major topic docs

Scoped `AGENTS.md`:

- Frontend-only commands
- Backend-only architecture rules
- Test fixture rules for one directory
- Deployment rules for an infra folder

Linked docs:

- Long testing instructions
- Architecture notes
- Release process details
- Generated-code conventions
- Migration or deployment procedures
