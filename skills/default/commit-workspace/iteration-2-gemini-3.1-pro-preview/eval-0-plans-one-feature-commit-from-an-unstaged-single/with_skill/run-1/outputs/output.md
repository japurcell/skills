# Commit Plan

**Branch Decision:** 
Created new branch `feat/123-export-csv` because the current branch is `main`.

**Commit Scope:** 
Auto-selected `src/invoice/export_csv.py` since it is the only changed file and there are no staged changes.

**Commit Message:**
```
feat: add invoice CSV export support

Summary:
- Adds invoice CSV export support for accountants
Rationale:
- Implements user request for invoice CSV export
Tests:
- not run (reason: dry run)
Refs #123
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

**Push / PR Decision:**
Push was explicitly requested by the user, so `should_push` is true. No PR was requested.