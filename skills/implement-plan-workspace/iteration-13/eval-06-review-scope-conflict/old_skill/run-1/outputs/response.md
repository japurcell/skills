## Code Review Findings

review_scope_files:
- `src/api.ts`
- `src/service.ts`
- `docs/notes.md`

Reviewer file-list mismatch detected.
- Reviewer-A reported: `src/api.ts`, `src/service.ts`
- Reviewer-B reported: `src/api.ts`, `scripts/helper.sh`

Scope conflict reconciliation
- Valid in-scope reviewed files: `src/api.ts`, `src/service.ts`
- Missing in-scope files: `docs/notes.md`
- Extra out-of-scope files: `scripts/helper.sh`

Review Scope Coverage
- Total Changed (Uncommitted) Files: 3
- Total Reviewed Files: 2
- Missing Files: 1
- Missing File List: `docs/notes.md`
- Excluded Files: none
- Completion Gate: Missing Files > 0 => INCOMPLETE (requires explicit deferment/approval); current status: INCOMPLETE

Next action: do not give review credit for `scripts/helper.sh`, reconcile Reviewer-B back to the controller-defined scope, and complete review of `docs/notes.md` before closing the review.
