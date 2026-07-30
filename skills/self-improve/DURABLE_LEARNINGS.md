# Durable Learnings

Use this when deciding whether a lesson is worth preserving.

## Keep Only If All Are True

- Likely to recur.
- Actionable.
- Specific to this repo, project, workflow, environment, or user preference.
- Not already documented.

## High-Value Signals

- Non-default commands.
- Build, test, typecheck, lint, deploy, or validation steps.
- Required command flags or ordering.
- Generated-code rules.
- Repo-specific architecture or style constraints.
- Environment quirks, permissions, caches, fixtures, ports, or secrets handling.
- Repeated human corrections.
- Review findings that reveal a reusable repo rule.
- Known flaky-test causes and stable fixes.
- Concrete ways to avoid wasted tool calls, timeouts, or false failures.

## Skip

- Temporary blockers.
- One-time failures.
- Ticket/story IDs.
- Files opened during the session.
- Obvious README or tree facts.
- Generic reminders like "be careful."
- Speculation.
- Broad rules that are less useful than the source detail.

## Good Examples

- `pnpm test -- --runInBand` - required because parallel tests conflict with shared fixtures.
- Use `src/generated/` types instead of hand-written API interfaces.
- Run `make validate-config` after editing deployment YAML.
- Jasmine forbids nested `it`; keep specs at the `describe` level.
- Use `aria-describedby` for this form’s error text because tests assert that accessibility contract.

## Poor Examples

- The user asked about tests.
- The agent opened `package.json`.
- The repo has a README.
- This test failed once.
- Remember to be careful.

## Mining Work Artifacts

For session logs, handoffs, progress files, and notes:

- Read more than the summary when detailed sections contain commands, gotchas, patterns, or validation rules.
- Preserve reusable context that changes future coding, testing, validation, or environment behavior.
- Keep exact technical terms when they carry the rule, such as `shareReplay(1)`, `aria-describedby`, nested `it`, or `single-rule`.
- Drop temporary status, story IDs, stale blockers, and one-off paths.
- If one artifact has several durable lessons, keep representative coverage instead of only the first item.

## Common Rationalizations

| Rationalization | Better rule |
| --- | --- |
| “The user did not ask me to remember this.” | Preserve durable guidance when warranted. |
| “That command is obvious.” | Non-default commands are high value. |
| “Only the summary matters.” | Durable rules often live in gotchas and details. |
| “Broader wording is safer.” | Specific rules are more useful. |
| “I should update something anyway.” | Make no change for low-value material. |
