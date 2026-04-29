PRD execution status for #6000

Completed this run:

- none

Blocked / waiting:

1. #6101 CSV export filters - Required shared verification command `bundle exec rspec spec/requests/admin/export_spec.rb` failed with `/bin/sh: bundle: command not found`; shared verification group did not pass.
2. #6102 CSV export download audit log - Covered by the same failed shared verification group and still blocked by #6101.

Next ready work:

- none

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- Do **not** close #6101 based on diff inspection alone; required verification is blocked and cannot be downgraded to “looks correct.”
- Parent task-graph checkboxes are informational only; stale `[ ]` lines are not the blocker here.
- #6101 remains open.
- #6102 remains open.
- parent PRD issue remains open.
