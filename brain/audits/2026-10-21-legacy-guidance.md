# Legacy guidance preservation audit

- Audited 83 immutable source entries and 7,389 lines, including both root-instruction variants, retired skills, raw references, ideas, and ADRs.
- Tracked 1,046 initial rows, two independently discovered legacy clauses, and one current-evidence correction. Each row has source spans, original strength, current ownership, and a final disposition in [the obligation ledger](../archive/plans/2026-10-21-legacy-guidance-audit/obligations.json).
- Restored reusable procedures in matching authoring, planning, task, handoff, reflection, review, and performance skills. Restored project-specific hook, script, installer, security, and test contracts in focused codebase notes.
- Restored mandatory reference TOCs over 100 lines, direct one-level reference navigation, invocation-control approval boundaries, historical-completion checks, admission gates, secret redaction, scope boundaries, and exact conditional validation routes.
- Preserved research-only context without adopting proposals as policy. Todos 2 and 6 regain original scope; todo 4 remains unchanged and owned elsewhere. Todo 13 captures the pre-existing cleanup defect.
- Preserved brain intent: no legacy roots, ingestion, OKF/frontmatter, semantic maintenance hooks, global guards, new runtime machinery, or global installations.
- Independent authoring, hooks, and knowledge reviewers compared all assigned legacy clauses. Follow-up review closed every guidance-restoration finding. Source tests do not prove live provider behavior or sampled model performance.
- Existing authoring CLI checks passed 111 tests; all 15 applicable changed skill definitions passed validation. See [validation evidence](../archive/plans/2026-10-21-legacy-guidance-audit/validation.json) and [the completed plan](../archive/plans/2026-10-21-legacy-guidance-audit/ExecPlan.md).

## Remaining implementation limits

- The observability helper already deleted entries older than seven days even when SQLite reported active sessions. The later explicit policy requires age over 24 hours and terminal/absent state. Guidance is restored; [todo 13](../todos.md) scopes runtime repair.
- The custom-agent converter accepts single-quoted empty metadata. The nonempty authoring rule is explicit again; this audit does not claim converter enforcement or change installer behavior.

Evidence: immutable legacy revision `092038394a2e3bb0cc21fffdec2eb60a12cece29`, root variants captured in the ledger, and current baseline `378f49c40abcadf34e765a8a4d5a6fd580008ba6`; checked 2026-10-21. Recheck affected dispositions after policy, provider, ownership, or loading-contract changes. This is historical audit evidence, not another instruction system.
