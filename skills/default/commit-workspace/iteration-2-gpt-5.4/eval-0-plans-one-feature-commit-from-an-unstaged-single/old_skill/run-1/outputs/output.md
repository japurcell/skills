# Commit Dry Run

- **Branch:** Create `feat/123-invoice-csv-export` because current branch is `main`, which requires a feature branch for this commit.
- **Scope:** Commit only `src/invoice/export_csv.py` because there are no staged changes and exactly one unstaged file.
- **Message:** Use `feat: add invoice CSV export support` with a body that summarizes the CSV export change, explains the accountant-facing rationale, records `Tests: not run (dry run; repo mutation and git commands disabled)`, and adds `Refs #123` plus the Copilot trailer.
- **Push/PR:** Push is requested and therefore should happen after the commit in a real run. PR creation was not requested, so no PR should be created.
