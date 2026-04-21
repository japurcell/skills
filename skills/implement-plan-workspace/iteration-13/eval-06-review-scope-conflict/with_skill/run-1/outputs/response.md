## Code Review Findings

The controller-defined `review_scope_files` are authoritative:
- `src/api.ts`
- `src/service.ts`
- `docs/notes.md`

Review Scope Coverage
- Total Changed (Uncommitted) Files: 3
- Total Reviewed Files: 2
- Missing Files: 1
- Missing File List: `docs/notes.md`
- Excluded Files: none
- Completion Gate: Missing Files > 0 => INCOMPLETE (requires explicit deferment/approval)

Scope conflict
- Reviewer-A reported: `src/api.ts`, `src/service.ts`
- Reviewer-B reported: `src/api.ts`, `scripts/helper.sh`
- Reviewer file-list mismatch detected
- Missing in-scope file: `docs/notes.md`
- Extra out-of-scope file: `scripts/helper.sh`

Safe resolution
- Count only in-scope reviewed files toward completion
- Do not treat `scripts/helper.sh` as reviewed scope coverage
- Re-run or redirect review so `docs/notes.md` is reviewed against the controller-defined scope
- Keep review status INCOMPLETE until the conflict is resolved or explicitly deferred

Highest-severity issues to fix: review coverage mismatch; no consolidated code findings are final until scope is reconciled.
