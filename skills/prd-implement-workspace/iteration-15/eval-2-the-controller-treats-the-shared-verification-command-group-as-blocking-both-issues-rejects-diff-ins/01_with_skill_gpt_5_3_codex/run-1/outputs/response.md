PRD execution status for #6000

Completed this run:

- none

Blocked / waiting:

1. #6101 CSV export filters - Shared verification command group failed: `bundle exec rspec spec/requests/admin/export_spec.rb` could not run (`/bin/sh: bundle: command not found`). #6101 remains open.
2. #6102 CSV export download audit log - Covered by the same shared verification command group, so failure blocks closure for this issue as well. #6102 remains open.

Next ready work:

- none

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- Diff inspection is not a valid substitute for required verification.
- Do not close either child issue until the shared command group passes.
- parent PRD issue remains open.
