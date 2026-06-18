# Commit Dry Run Output

## Branch Decision
Keep current branch `fix/rate-limit-backoff` since it is not empty, `main`, or `master`.

## Commit Scope
Commit staged files only (`src/rate_limit.py` and `tests/test_rate_limit.py`).

## Commit Message
```text
fix: update retry backoff

Summary:
- Fix the retry backoff logic
- Add test coverage
Rationale:
- Resolve rate-limit bug
Tests:
- not run
Fixes #456
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Push/PR Decision
- **Push requested:** false (user did not explicitly ask to push, but asked for PR)
- **Should push:** true (required to open PR)
- **PR requested:** true (user asked to open a PR)
- **Should create PR:** true (no blockers found)
