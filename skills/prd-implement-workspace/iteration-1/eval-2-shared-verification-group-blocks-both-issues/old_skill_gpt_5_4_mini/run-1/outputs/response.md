PRD execution status for #6000

Completed this run:

None.

Blocked / waiting:

1. #6101 CSV export filters - shared verification failed (`/bin/sh: bundle: command not found`), so it cannot be closed.
2. #6102 CSV export download audit log - shared verification failed (`/bin/sh: bundle: command not found`), so it cannot be closed.

Next ready work:

- W4: #6101 CSV export filters
- W4: #6102 CSV export download audit log

Notes:

- Do not close #6101 based on diff review alone; the shared verification group must pass first.
- Rerun `bundle exec rspec spec/requests/admin/export_spec.rb` after Bundler is available.
