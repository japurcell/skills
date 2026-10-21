# Commit Skill Eval: staged-bugfix-pr (Dry Run)

## Input Summary
- **User request:** "Turn the staged rate-limit bugfix into one clean commit and open a PR for issue 456."
- **Current branch:** fix/rate-limit-backoff
- **Staged files:** src/rate_limit.py, tests/test_rate_limit.py
- **Unstaged files:** README.md
- **Issue:** #456
- **Create PR:** yes

## Algorithm Application

### 1) Issues
- Parse from `issue_numbers`: [456]
- User language: "bugfix" → explicit fix context
- **Trailer verb:** `Fixes` (explicit fix/close language per spec §1)
- Deduplicated: [456]

### 2) Branch Selection
- `feature_branch` is null → check current branch
- Current `fix/rate-limit-backoff` ≠ base_branch (main) and ≠ main/master/empty
- **Action:** keep current branch
- **branch_action:** keep

### 3) File Selection
- Staged changes exist: [src/rate_limit.py, tests/test_rate_limit.py]
- **Decision:** commit staged paths only (spec §3: if staged changes exist, commit staged only)
- Exclude unstaged README.md

### 4) Commit Type
- Context: "rate-limit bugfix" (explicit)
- Summary: "Fixes the retry backoff for the rate-limit bug and adds coverage"
- **Type:** fix

### 5) Branch Name
- Not creating new branch (using existing)
- Skipped

### 6) Subject Line
- Action summary from change context
- **Subject:** "Fix rate-limit retry backoff"

### 7) Commit Message
```
fix: Fix rate-limit retry backoff

Fixes #456
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```
- Format: type: subject + blank + trailers (no blank between trailers)

### 8) Commit Creation
- Status check: in repo ✓, author configured ✓, changes exist ✓, no conflicts ✓, not detached ✓
- **Status:** commit

### 9) PR Decision
- Requested: create_pr=true
- No blockers detected (gh assumed available)
- **should_create_pr:** true
- Title = subject (not full conventional-commit line)
- Body: summary + issues section

## Output Summary

| Key | Value |
|-----|-------|
| Status | commit |
| Branch | fix/rate-limit-backoff (keep) |
| Files | 2 staged |
| Type | fix |
| Subject | Fix rate-limit retry backoff |
| PR | Create required |

✓ All stops checked, no blockers
✓ Ready to execute commit and PR creation
