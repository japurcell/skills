Checklist Gate
- Not started yet.

Implementation Context Loaded
- Review scope derived from the provided uncommitted file set: src/staged_api.ts, docs/staged_notes.md, src/unstaged_service.ts, scripts/new_check.sh.

Phase Execution
- Pending this phase.
- Checkpoint Decision
  - Status: FAIL
  - Evidence: Code review input is incomplete because the reviewer covered only 1 of 4 changed files.
  - Integrity check: Review scope drift detected before phase completion.
  - Next Action: Re-run review against the full uncommitted scope before advancing.

Code Review Findings
- Severity: High — Scope conflict / reviewer file-list mismatch. The reviewer narrowed scope to src/staged_api.ts, but review_scope_files must include all uncommitted changed files and reviewers must not recompute or narrow scope independently.

Review Scope Coverage
- Total Changed (Uncommitted) Files: 4
- Total Reviewed Files: 1
- Missing Files: 3
- Missing File List: docs/staged_notes.md, src/unstaged_service.ts, scripts/new_check.sh
- Excluded Files: none
- Completion Gate: Missing Files > 0 => INCOMPLETE (requires explicit deferment/approval)

- Required controller action: reject the partial review as incomplete, reconcile the scope conflict explicitly, and relaunch review for the missing files. Do not treat findings from src/staged_api.ts alone as sufficient to close the review step.
- Highest-priority fix: enforce full review coverage across staged, unstaged, and untracked files before reporting review completion, or explicitly defer the uncovered files.

Completion Validation
- FAIL — Code review cannot be marked complete because 3 in-scope files were not reviewed. Prevent scope drift by holding completion until docs/staged_notes.md, src/unstaged_service.ts, and scripts/new_check.sh are reviewed or explicitly deferred.
