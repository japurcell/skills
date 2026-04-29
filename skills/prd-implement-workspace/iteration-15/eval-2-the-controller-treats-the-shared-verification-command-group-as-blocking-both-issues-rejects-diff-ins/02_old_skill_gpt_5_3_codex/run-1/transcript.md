# Prompt

You are executing /prd-implement for PRD #6000. The lowest open wave is W4. The parent PRD issue still shows `- [ ] W4 - #6101 CSV export filters - AFK - blocked by #6099` and `- [ ] W4 - #6102 CSV export download audit log - AFK - blocked by #6101`. AFK child issues #6101, "CSV export filters," and #6102, "CSV export download audit log," finished implementation and review. The controller's verification plan uses one shared command group for both issues because each child issue says verification is `bundle exec rspec spec/requests/admin/export_spec.rb`. The verification subagent reports `/bin/sh: bundle: command not found`. Another agent suggests closing #6101 anyway because its diff looks correct and leaving only #6102 open. Produce the controller's response.

# Response

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
