# Commit Dry Run: single-file-on-main

## Decision
**Status:** Ready to commit

## Analysis

### Blockers
None. All preconditions met.

### Branch
- **Current:** `main`
- **Decision:** Create new branch
- **Name:** `feat/123-invoice-export`
- **Reason:** On base_branch (`main`); SKILL.md step 3 requires branch creation

### Commit Scope
- **Selected:** `src/invoice/export_csv.py`
- **Staged:** None
- **Unstaged:** 1 file
- **Selection rule:** SKILL.md step 4—single changed file → use it

### Type & Subject
- **Type:** `feat`
- **Subject:** `add invoice CSV export support`
- **Reason:** New user-facing capability per change_summary

### Issue Trailer
- **Issue:** `#123`
- **Trailer:** `Refs #123`
- **Reason:** User did not say "fix"—use `Refs` not `Fixes`

## Commit Message
```
feat: add invoice CSV export support

Refs #123
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Actions
- **Push:** Yes—user explicitly requested: "push the branch when you're done"
- **Create PR:** No (`create_pr=false`)
- **Co-author:** Default Copilot trailer included per SKILL.md step 7

## Plan
1. Create branch `feat/123-invoice-export`
2. Stage `src/invoice/export_csv.py`
3. Commit with message above
4. Push to remote
