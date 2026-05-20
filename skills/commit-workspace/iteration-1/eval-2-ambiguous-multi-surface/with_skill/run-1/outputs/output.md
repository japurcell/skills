# Commit Skill Dry-Run: ambiguous-multi-surface

## Status
**STOPPED** — Ambiguous file scope. Cannot auto-select files.

## Reason
No staged changes exist, and the 2 unstaged files live in different top-level directories:
- `src/report/api.py` (implementation)
- `docs/report-api.md` (documentation)

Per SKILL.md Step 4, the commit scope selection rule is:
1. If only 1 file changed → commit it
2. If all files live under 1 top-level directory → commit them all
3. Otherwise → stop and ask

This is case 3 (ambiguous multi-surface).

## Branch Decision
**Keep:** `feat/report-api`
- Current branch is a valid feature branch (not main/master/empty, Step 3)
- No feature_branch override provided
- Branch action: `keep`

## Next Action
Ask the user to clarify scope:
- Commit both API and docs together (likely, but not certain)
- Commit API only (possible — docs might be in a follow-up)
- Commit docs only (unlikely, but possible — docs might be separate)

## Why Stopping Is Correct
SKILL.md red flags explicitly include: "Unstaged noise is included even though staged changes existed" — in this case, there's no clear signal whether both files belong in one commit. The skill refuses to guess at scope.

Scope ambiguity is a blocker because:
- Commit type differs (feat for API, docs for docs?)
- Subject differs (implementation vs documentation)
- Future PR/issue linkage might differ
- Reviewability depends on clear scope
