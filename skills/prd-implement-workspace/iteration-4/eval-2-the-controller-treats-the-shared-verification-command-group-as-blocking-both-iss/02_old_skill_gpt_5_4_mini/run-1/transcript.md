# Prompt
You are executing /prd-implement for PRD #6000. The lowest open wave is W4. The parent PRD issue still shows `- [ ] W4 - #6101 CSV export filters - AFK - blocked by #6099` and `- [ ] W4 - #6102 CSV export download audit log - AFK - blocked by #6101`. AFK child issues #6101, "CSV export filters," and #6102, "CSV export download audit log," finished implementation and review. The controller's verification plan uses one shared command group for both issues because each child issue says verification is `bundle exec rspec spec/requests/admin/export_spec.rb`. The verification subagent reports `/bin/sh: bundle: command not found`. Another agent suggests closing #6101 anyway because its diff looks correct and leaving only #6102 open. Produce the controller's response.

# Response
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
