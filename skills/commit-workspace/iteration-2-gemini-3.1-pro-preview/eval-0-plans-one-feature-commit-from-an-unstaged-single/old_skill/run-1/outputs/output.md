# Commit Plan

**Branch Decision**: The current branch is `main`, which matches the base branch. Therefore, a new branch `feat/123-invoice-csv-export` will be created.
**Commit Scope**: Since there are no staged files and exactly one unstaged file (`src/invoice/export_csv.py`), this single file will be committed.
**Commit Message**: A `feat` type will be used with the issue reference appended as `Refs #123`.
**Push/PR Decision**: The user explicitly requested to push the branch (`push_requested=true`), but a PR was not requested. Therefore, the branch will be pushed (`should_push=true`) but no PR will be created (`should_create_pr=false`).