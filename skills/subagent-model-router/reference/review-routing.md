# Review Routing

Use for `code-reviewer`, `security-review`, PR review, diff review, audit, test review, or security-sensitive changes.

## Order

1. If security-sensitive, use `security-review` + Premium, or `code-reviewer` + Premium for code-correctness review of security-sensitive code.
2. Else if tiny style-only, use `code-reviewer` + Fast.
3. Else use `code-reviewer` + Standard.
4. Escalate to Premium when subtle correctness, high stakes, or prior misses apply.

## Fast review: allowed only when all are true

- Single file.
- Tiny diff.
- Style/comment/format only.
- Low stakes.
- No logic, tests, auth, data, API contract, migration, permission, redirect, secret, payment, deletion, or policy change.

Route: `code-reviewer` + Fast + `gpt-5-mini`.

## Standard review: default

Use for meaningful code review, including:

- normal feature/fix PRs
- multi-file diffs
- backend + frontend changes
- tests, fixtures, mocks, assertions, or guard changes
- more than 3 touched files
- maintainability or design tradeoffs

Route: `code-reviewer` + Standard + `gpt-5.4-mini` or same-tier capable fallback.

## Premium review

Use Premium for:

- auth, redirects, permissions, identity, secrets, sensitive data
- payments, deletion, migrations, policy enforcement
- security controls or security-sensitive validation
- subtle correctness or compatibility
- false-pass tests
- cross-file contracts, schemas, serialization, API compatibility
- race conditions, concurrency, caching, distributed behavior
- high or unclear production blast radius
- broad security/architecture audit
- previous Standard review missed an issue in the same task class
- user asks for best available review quality

Routes:

- Security audit/sensitive flow: `security-review` + Premium.
- Subtle code correctness: `code-reviewer` + Premium.
- Preferred code model: `gpt-5.3-codex`.
- If unavailable, choose another Premium model suited to code/security reasoning.

## Review defaults

| Situation | Route |
|---|---|
| Tiny single-file style-only diff | `code-reviewer` + Fast + `gpt-5-mini` |
| Normal review | `code-reviewer` + Standard + `gpt-5.4-mini` |
| Backend + frontend | `code-reviewer` + Standard + `gpt-5.4-mini` |
| Tests/guards | Standard; Premium if false-pass risk is subtle |
| Auth/permissions/security-sensitive | Premium |
| Subtle correctness/cross-file contracts | Premium + `gpt-5.3-codex` |
| Security review | `security-review` + Premium; never cheapest |

## Missed-issue rule

If a prior review missed an issue later found, escalate the next same-class review by one tier:

- Fast missed issue → Standard.
- Standard missed issue → Premium.
- Premium missed issue → Premium again, but split the task or use a stronger suited model.

Do not downshift until the task class has clean review history.
