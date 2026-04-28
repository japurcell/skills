PRD execution status for #6000

Completed this run:

- none

Blocked / waiting:

1. #6101 CSV export filters - shared verification command `bundle exec rspec spec/requests/admin/export_spec.rb` could not run because `bundle` is unavailable (`/bin/sh: bundle: command not found`).
2. #6102 CSV export download audit log - same shared verification failure; do not close #6101 independently.

Next ready work:

- none

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- The shared verification group blocks both child issues.
- The parent task-graph lines for #6101 and #6102 remain [ ].