# In-Place Migration Sequencing and Verification

**Type:** grilling
**Status:** closed
**Blocked By:** in-place-okf-document-contract.md, okf-authoring-skill-contract.md, okf-linter-and-provider-hooks-contract.md
**Research Dir:** N/A

## Question

In what dependency order should the canonical documents, routing instructions, authoring skill, linter, and both provider hook registrations change, and what fixtures, commands, rollback boundary, and compatibility checks prove the migration without introducing a second knowledge-loading path?

---

## Resolution

- Implement on one feature branch in dependency-ordered stages: dormant linter and fixtures; authoring-skill integration; complete canonical-corpus and source-summary-scaffold migration; green full-corpus lint; provider adapters and regression tests; then hook enablement only after live capability gates pass. Do not add compatibility modes or temporary lint exceptions.
- Use one small checked-in valid two-bundle fixture. Each diagnostic test copies it into a temporary repository and mutates only the condition under test.
- Treat required live Copilot and Gemini capability probes as a merge gate for the entire migration, not merely for hook registration. A failed probe may leave the implementation branch available for diagnosis, but the migration cannot merge or be claimed complete.
- Treat the merged migration as one rollback unit even if its implementation history contains reviewable staged commits. Any post-merge conformance or enforcement regression reverts the whole migration rather than leaving OKF documents, authoring guidance, lint tooling, or provider gates at mismatched versions.
- Register source-ingest and OKF lint as independent hooks in that order. Introduce a thin provider coordinator only if live simultaneous-failure probes prove that the deployed host loses one reason; the coordinator may compose results but may not merge validator responsibilities or state.
- Run live probes in disposable worktrees containing the candidate repository-local configuration and deliberately invalid canonical fixtures. Record commands, tested CLI versions, event observations, normalized diagnostics, simultaneous-failure behavior, and full-corpus duration in the implementation ExecPlan; do not create a separate verification-report artifact by default.
- Use six implementation gates: (1) baseline inventory and failing fixture tests; (2) provider-neutral linter, vendored parser, and green fixture suite; (3) `okf-authoring`, its evaluations, and one-way `update-agent-docs` integration; (4) atomic migration of all canonical documents together with both source-summary scaffold producers, ending with green full-corpus lint; (5) provider adapters, registrations, parity tests, and source-ingest regressions; and (6) disposable-worktree live probes, final compatibility evidence, documentation synchronization, and merge readiness.
- At each gate run its targeted tests. Final acceptance runs the new linter and adapter suites, both existing source-ingest suites, affected startup/configuration/install tests, authoring-skill validation and evaluations, full-corpus lint in human and JSON modes, repository-local link checks, `git diff --check`, and all required live provider probes. Unrelated repository suites are not a blanket gate.
- The implementation ExecPlan must assign non-overlapping ownership for linter/fixtures, authoring skill/evaluations, canonical migration/scaffold producers, and dual-provider adapters/tests. One coordinating owner retains shared configuration and final integration; shared-path ownership transfers only between sequential gates.

### Required command matrix

The ExecPlan may add narrower red/green commands within a gate, but final acceptance must include these stable repository entry points:

```text
bash scripts/test-okf-lint.sh
./scripts/lint-okf.py
./scripts/lint-okf.py --format json
bash scripts/test-hooks-okf-lint.sh
bash scripts/test-gemini-hooks-okf-lint.sh
bash scripts/test-hooks-auto-ingest.sh
bash scripts/test-gemini-hooks-auto-ingest.sh
bash scripts/test-hooks-startup.sh
bash scripts/test-gemini-hooks-startup.sh
bash scripts/test-install.sh
PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py .agents/skills/okf-authoring
git diff --check
```

The ExecPlan must also record the exact `okf-authoring` evaluation/baseline commands selected from the repository skill-creator harness, a repository-local relative-link check over the active migration and canonical documents, and the provider-specific live probe commands. Those commands depend on artifacts created by the implementation and must be made exact before their gate begins. Run `./scripts/install.sh` before live checks of installed skill or hook behavior, as required by repository convention.

### Gate and rollback semantics

- Gates 1–3 may be reviewable commits while the current canonical corpus still fails the dormant linter; no hook is enabled and no conformance claim is made in that state.
- Gate 4 is indivisible: migrate the complete two-bundle corpus and every supported source-summary scaffold writer together, preserve `AGENTS.md` → `.agents/memory/INDEX.md`, and require both human and JSON lint modes to succeed before proceeding.
- Gate 5 adds thin adapters and candidate repository-local registrations only after the corpus is green. Static and simulated hook tests must prove identical normalized diagnostics and retain independent source-ingest behavior.
- Gate 6 is the release boundary. Required live events, mutation matchers, timeouts, subagent behavior, retry behavior, and simultaneous source-ingest/lint failures must pass in disposable worktrees before merge.
- Failure before merge leaves the branch diagnosable but unshippable. Failure after merge reverts the complete migration merge unit. Re-enablement requires a root cause, regression coverage, a green full matrix, and fresh live capability evidence.

This sequence introduces no compatibility parser, temporary lint suppression, second knowledge copy, selector, or prompt-time OKF injection. The next session may translate these closed decisions into an ExecPlan without reopening them.
