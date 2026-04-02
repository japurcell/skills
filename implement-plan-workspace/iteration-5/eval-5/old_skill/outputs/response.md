## Code Review Findings

1. High: Review scope is incomplete and will cause scope drift if only src/staged_api.ts is reviewed.
- Evidence: Changed set includes staged API + staged docs + unstaged service + untracked script.
- Missing from proposed review: docs/staged_notes.md, src/unstaged_service.ts, scripts/new_check.sh.
- Required fix: Block approval until all changed files are reviewed as one atomic change set.

2. High: API/doc contract drift risk between src/staged_api.ts and docs/staged_notes.md.
- Evidence: API code and notes changed together, but proposal excludes docs validation.
- Required fix: Add an explicit API-to-doc parity check in review findings before merge.

3. Medium: Behavioral drift risk from unreviewed service logic in src/unstaged_service.ts.
- Evidence: Unstaged service changes can alter runtime behavior behind staged API surfaces.
- Required fix: Include unstaged service diff in the same review pass or require it to be excluded from the feature branch before approval.

4. Medium: Process/tooling drift risk from unreviewed executable in scripts/new_check.sh.
- Evidence: New untracked script may introduce undocumented validation paths not reflected in plan scope.
- Required fix: Either add script to scoped implementation artifacts and review it, or remove it from this change set.

5. Required gate to prevent further scope drift:
- Scope gate: Reject "partial-file review" when any staged, unstaged, or untracked files exist.
- Minimum review set for this task: src/staged_api.ts, docs/staged_notes.md, src/unstaged_service.ts, scripts/new_check.sh.
- Decision: FAIL until full-set review is completed.
