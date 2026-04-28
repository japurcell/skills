PRD execution status for #6000

Completed this run:

1. None

Blocked / waiting:

1. #6101 CSV export filters - blocked by shared verification; `bundle exec rspec spec/requests/admin/export_spec.rb` failed with `/bin/sh: bundle: command not found`
2. #6102 CSV export download audit log - blocked by the same shared verification failure

Next ready work:

- None

Notes:

- Do not close #6101 independently; the shared verification command covers both issues and must pass before either can close.
