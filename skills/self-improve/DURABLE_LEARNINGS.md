# Durable Learnings

Use when deciding whether a lesson is worth preserving.

## Keep Only If All Are True

- Likely to recur.
- Actionable.
- Specific to this repo, workflow, environment, or user preference.
- Not already documented.

## Prefer

- Non-default commands, flags, ordering, or required validation steps.
- Build, test, typecheck, lint, deploy, migration, or release rules.
- Generated-code rules.
- Repo architecture, style, fixture, cache, port, permission, or secrets-handling constraints.
- User corrections.
- Review findings that reveal reusable repo rules.
- Known flaky-test causes and stable fixes.
- Ways to avoid wasted tool calls, false failures, or timeouts.
- Coordination or stale-context signals that reveal a reusable workflow rule.

## Skip

- Temporary blockers.
- One-time failures.
- Ticket/story IDs.
- Files merely opened during the session.
- Obvious README, package, or tree facts.
- Generic reminders such as “be careful.”
- Speculation.
- Broad summaries that lose the useful source detail.

## Mining Artifacts

For logs, handoffs, progress files, and notes:

- Read beyond summaries when details may contain commands, gotchas, patterns, or validation rules.
- Preserve reusable context that changes future coding, testing, validation, or environment behavior.
- Treat churn as a signal, not proof: repeated retries, stale paths, or subagent rework count only if they imply a stable rule.
- Keep exact technical terms when they carry the rule, such as `shareReplay(1)`, `aria-describedby`, `nested it`, or `single-rule`.
- If an artifact has several durable lessons, keep representative coverage.
- Make no change for low-value material.

## Examples

Good:

- `pnpm test -- --runInBand` is required because parallel tests conflict with shared fixtures.
- Use `src/generated/` types instead of hand-written API interfaces.
- Run `make validate-config` after editing deployment YAML.
- Jasmine forbids nested `it`; keep specs at the `describe` level.
- Use `aria-describedby` for this form’s error text because tests assert that accessibility contract.

Poor:

- The user asked about tests.
- The agent opened `package.json`.
- The repo has a README.
- This test failed once.
- Remember to be careful.
