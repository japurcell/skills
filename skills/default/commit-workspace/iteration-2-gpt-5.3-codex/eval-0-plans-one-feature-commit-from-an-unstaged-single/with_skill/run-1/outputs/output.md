Branch decision: current branch is `main` (base branch), so dry run selects creating `feat/123-invoice-csv-export` (`branch_action=create`).

Commit scope: no staged changes exist and exactly one unstaged file changed, so selected scope is `src/invoice/export_csv.py`.

Commit message: `feat(invoice): add invoice CSV export for accountants` with required body sections (`Summary`, `Rationale`, `Tests`), `Refs #123`, and Copilot co-author trailer.

Push/PR decision: user explicitly asked to push, so `push_requested=true` and `should_push=true`; PR was not requested (`pr_requested=false`, `should_create_pr=false`).
