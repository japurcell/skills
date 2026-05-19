---
name: ship
description: Run a parallel pre-launch review with three specialist personas, then merge the results into a go/no-go decision with a rollback plan.
---

`/ship` is a fan-out orchestrator. It reviews the current change by running three specialist personas independently, then synthesizes their reports into one go/no-go decision with a rollback plan.

## Phase A — Fan-out

Use the Agent tool to start these three subagents concurrently in one assistant turn. Do not call them sequentially.

In Claude Code, set `subagent_type` to the persona name:

1. `addy-code-reviewer` — Review staged changes or recent commits across correctness, readability, architecture, security, and performance. Return the standard review template.
2. `addy-security-auditor` — Review for vulnerabilities and threats, including OWASP Top 10, secrets handling, auth/authz, and dependency CVEs. Return the standard audit report.
3. `addy-test-engineer` — Review test coverage and identify gaps in happy path, edge cases, error paths, and concurrency. Return the standard coverage analysis.

If no Agent tool is available, run the three persona prompts separately and treat the results as parallel inputs for Phase B.

Subagent constraints:

- Subagents must not spawn other subagents.
- Each subagent works in its own context and returns only its report.
- If collaboration between specialists is required, use Agent Teams instead of this command.

Persona resolution:

- If custom personas with the same names exist in `.claude/agents/` or `~/.claude/agents/`, use those instead of plugin defaults.
- User-defined personas take precedence by design.

## Phase B — Merge

After all three reports return, the main agent merges them in the main context:

1. **Code Quality** — Combine Critical and Important findings from `addy-code-reviewer` with any failing tests, lint, or build output. Remove duplicates.
2. **Security** — Treat any Critical or High finding from `addy-security-auditor` as a launch blocker. Cross-check with `addy-code-reviewer` security findings.
3. **Performance** — Use `addy-code-reviewer` performance findings and check Core Web Vitals if relevant.
4. **Accessibility** — Verify keyboard navigation, screen reader support, and contrast directly, or run an accessibility checklist.
5. **Infrastructure** — Verify env vars, migrations, monitoring, and feature flags directly.
6. **Documentation** — Verify README, ADRs, and changelog directly.

## Phase C — Decision

Return exactly one final report:

```markdown
## Code Review Decision: GO | NO-GO

### Blockers (must fix before ship)

- [Source persona: finding + file:line]

### Recommended fixes (should fix before ship)

- [Source persona: finding + file:line]

### Acknowledged risks (shipping anyway)

- [Risk + mitigation]

### Rollback plan

- Trigger conditions: [signals that would prompt rollback]
- Rollback procedure: [exact steps]
- Recovery time objective: [target]

### Specialist reports (full)

- [addy-code-reviewer report]
- [addy-security-auditor report]
- [addy-test-engineer report]
```

## Rules

1. In Phase A, run all three personas in parallel, not sequentially.
2. Personas do not call each other; the main agent merges all results.
3. A rollback plan is required before any GO decision.
4. If any persona reports a Critical finding, default to NO-GO unless the user explicitly accepts the risk.
5. Skip fan-out only if all are true:
   - the change touches 2 files or fewer
   - the diff is under 50 lines
   - it does not affect auth, payments, data access, or config/env

Otherwise, use fan-out by default. `/ship` is intended for production-bound changes, especially when blast radius is non-trivial.
