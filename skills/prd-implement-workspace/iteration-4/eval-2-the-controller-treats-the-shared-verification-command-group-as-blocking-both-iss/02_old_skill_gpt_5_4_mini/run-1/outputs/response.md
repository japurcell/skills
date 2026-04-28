PRD execution status for #6000

Completed this run:

- none

Blocked / waiting:

1. #6101 CSV export filters - shared verification command `bundle exec rspec spec/requests/admin/export_spec.rb` failed because `bundle` is unavailable (`/bin/sh: bundle: command not found`).
2. #6102 CSV export download audit log - blocked by the same shared verification failure.

Next ready work:

- none

Notes:

- Do not close either child issue until the shared verification passes.
