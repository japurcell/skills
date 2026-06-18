Branch decision: current branch is `main` (base branch), so dry run selects creating `feat/123-invoice-csv-export` (`branch_action=create`).

Commit scope: there are no staged changes and exactly one unstaged changed file, so selected scope is `src/invoice/export_csv.py`.

Commit message: `feat(invoice): add invoice CSV export for accountants` with body sections `Summary`, `Rationale`, and `Tests`, followed by `Refs #123` and Copilot co-author trailer.

Push/PR decision: user explicitly asked to push, so `push_requested=true` and `should_push=true`; PR was not requested (`pr_requested=false`, `should_create_pr=false`).
