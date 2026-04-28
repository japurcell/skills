PRD execution status for #6000

Completed this run:

1. None

Blocked / waiting:

1. #6101 CSV export filters - shared verification command `bundle exec rspec spec/requests/admin/export_spec.rb` failed with `/bin/sh: bundle: command not found`; that missing `bundle` tool blocks closure for both covered issues.
2. #6102 CSV export download audit log - same shared verification blocker; diff inspection or “looks correct” reasoning is not a substitute for the required shared verification command.

Next ready work:

- none

Notes:

- Leave the parent PRD task-graph lines for #6101 and #6102 unchecked until the shared verification command passes.
