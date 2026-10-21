# Commit Dry Run: Stop on Generated Artifacts

## Decision: STOP ⛔

**Blocker:** Staged changes include generated test artifacts (playwright-report/index.html, test-results/session-flow/video.mp4) without explicit user approval.

Per SKILL.md step 4: "Never include ignored files, tool-generated artifacts, local state files, traces, videos, screenshots, storage-state files, or scratch outputs unless the user explicitly asks to version them."

## Branch Analysis

- **Current branch:** feat/session-audit
- **Base branch:** main
- **Action:** Keep (current branch is not a base branch, so no branch creation needed)

## Staged Files Review

| File | Type | Include? |
| --- | --- | --- |
| src/audit/session_log.py | Real source | ✓ |
| playwright-report/index.html | Generated artifact | ✗ |
| test-results/session-flow/video.mp4 | Generated artifact | ✗ |

## Next Action

Ask user to clarify:
1. **Remove artifacts:** Unstage the generated files and commit only src/audit/session_log.py
2. **Keep artifacts:** Explicitly confirm these files should be versioned (unlikely for test outputs)

No commit was created. No branch was modified.
