PRD execution status for #6000

Completed this run:

- none

Blocked / waiting:

1. #6101 CSV export filters - shared required verification command group failed: `bundle exec rspec spec/requests/admin/export_spec.rb` -> `/bin/sh: bundle: command not found`.
2. #6102 CSV export download audit log - blocked by the same failed shared verification command group.

Next ready work:

- none (W4 cannot advance while shared verification coverage is failing)

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- #6101 remains open.
- #6102 remains open.
- parent PRD issue remains open.
- Closing #6101 early based on diff inspection is not allowed because shared verification for both issues did not pass.
