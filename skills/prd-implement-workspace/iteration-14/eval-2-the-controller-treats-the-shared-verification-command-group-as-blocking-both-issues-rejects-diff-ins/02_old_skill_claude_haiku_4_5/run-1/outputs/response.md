# Verification blocker for W4 shared command group

The verification subagent reports `/bin/sh: bundle: command not found` when attempting to run:
```
bundle exec rspec spec/requests/admin/export_spec.rb
```

This command covers both #6101 "CSV export filters" and #6102 "CSV export download audit log" as a shared verification group.

## Controller assessment

The skill rules are explicit:
- **Shared command groups:** "Do not close any child issue covered by a shared command group unless that shared group passes."
- **Blocker handling:** "If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker."

The proposed substitute (closing #6101 anyway because the diff looks correct) is **not acceptable** because:
1. It violates the shared-command-group rule: both issues are covered by the same verification command
2. Code inspection is not the framework-native verification step
3. The Verification section does not list an alternative to `bundle exec rspec`

## Outcome

- #6101 remains open.
- #6102 remains open.
- Verification is blocked for both issues: the required shared command `bundle exec rspec spec/requests/admin/export_spec.rb` cannot run due to missing `bundle` CLI.
- Landing status: no commit, push, or PR actions performed in this run.

Next step: Ensure the `bundle` CLI is available in the verification environment, or update both child issues' Verification sections with an explicit fallback before this run resumes.