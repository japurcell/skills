# Controller Stop: Shared Verification Command Group Blocked for Both Issues

**Issues #6101 and #6102 cannot be closed.** Both are covered by a shared verification command group that has failed due to a missing tool.

## Shared Verification Command Group

The verification plan for wave W4 identified that both child issues require the same verification command:
```
bundle exec rspec spec/requests/admin/export_spec.rb
```

This command validates the behavior of both:
- #6101: CSV export filters
- #6102: CSV export download audit log

Because both issues list the same verification step, the controller created **one shared command group covering both #6101 and #6102**.

## Blocker: Missing `bundle` Command

The verification subagent attempted to run the shared command and reported:
```
/bin/sh: bundle: command not found
```

The `bundle` command (Ruby Bundler) is not available in the current environment. Without it, `bundle exec rspec` cannot run, and the shared verification command group **fails closed**.

## Controller Decision: Both Issues Remain Open

Per the skill rules (line 247): **"Do not close any child issue covered by a shared command group unless that shared group passes."**

Since the shared group failed, closure is blocked for **both** #6101 and #6102, regardless of how correct their diffs appear.

A suggestion to close #6101 because "its diff looks correct" does not override this rule. Diff inspection is not a substitute for the required verification command. The shared command group must pass, or the verification plan must be updated by the human before closure can proceed.

## Action Required

To proceed:

1. **Install Ruby Bundler** in the checkout so `bundle exec rspec spec/requests/admin/export_spec.rb` can run successfully for both issues.
2. **Or**: Update the verification steps in both child issues if the shared `bundle exec rspec` command is no longer applicable, and have the controller build a new verification plan.

**Current state:**
- Issue #6101: open, awaiting shared verification command to pass
- Issue #6102: open, awaiting shared verification command to pass
- Task-graph lines: both remain `[ ]`
- Wave W4: halted until blocker is resolved
