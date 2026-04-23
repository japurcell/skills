# Deterministic workflow

This file is the canonical workflow contract.

## Inputs

- Work item description (feature/bug/spec)
- Optional parent GitHub issue
- Base branch (default `main`)

## Phase contract

| Phase | ID | Required output | Parallelism | Depends on | Exit criteria |
|---|---:|---|---|---|---|
| Intake | 00 | `00-intake.md` | No | none | Problem, constraints, and acceptance criteria captured |
| Worktree setup | 01 | `01-worktree.md` | No | 00 | Branch + worktree created and recorded |
| Codebase exploration | 02 | `02-exploration-summary.md` | Yes (subagents) | 01 | Relevant files/patterns/open questions documented |
| Online research | 03 | `03-research-findings.md` | Yes (subagents) | 02 | Sources, findings, and decisions captured |
| Clarifications | 04 | `04-clarifications.md` | No | 03 | Remaining blocking questions sent to human/resolved |
| Plan | 05 | `05-plan.md` | No | 04 | Detailed implementation + verification strategy defined |
| TDD task graph | 06 | `06-task-graph.yaml` | Mixed | 05 | Red/Green/Refactor DAG with dependencies and parallel flags |
| Implementation | 07 | commits + notes | Mixed by DAG | 06 | Tasks completed according to DAG |
| Review | 08 | `08-code-review.md`, `08-security-review.md`, `08-tech-debt.md` | Yes | 07 | Code review, security, and tech debt checks completed |
| Verification | 09 | `09-verification.md` | No | 08 | Tests/checks/manual verification passed and recorded |
| PR | 10 | Pull request | No | 09 | Branch pushed, PR opened, artifacts linked |

## Rules

1. Do not skip phases.
2. Do not implement before phases 05 and 06 are complete.
3. Do not open PR before phase 09 passes stop gates.
4. Persist artifacts under `.ai/artifacts/<work-id>/`.
5. Use GitHub parent -> phase -> task issue hierarchy for tracking.

See `stop-gates.md` for enforcement and `.ai/scripts/validate-artifacts.py` for lightweight checks.
