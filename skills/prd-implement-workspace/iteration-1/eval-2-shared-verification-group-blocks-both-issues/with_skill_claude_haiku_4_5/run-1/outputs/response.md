**Verification blocked — cannot close either issue**

The verification plan uses a shared command group `bundle exec rspec spec/requests/admin/export_spec.rb` to validate both #6101 and #6102. This shared coverage means both issues are blocked by the same verification result.

The required verification binary `bundle` is not available in the environment (`/bin/sh: bundle: command not found`). Per the verification contract in the SKILL rules, this is a blocker without a human-approved alternative path:

- The child issues specify `bundle exec rspec` as the required verification framework, not a fallback list of alternatives
- The verification strength rule: "Do not replace framework-native verification with static analysis, source inspection, or generic 'looks correct' reasoning"
- The shared command group rule: "Do not close any child issue covered by a shared command group unless that shared group passes"

**Action required:**

1. Set up the Ruby/Rails environment with Bundler installed, or
2. Update the issue verification steps to include a fallback verification method if RSpec is unavailable (this requires human approval and GitHub issue edits)

**Issue state:**

- #6101 and #6102 remain open
- Implementation and review are complete
- Verification is blocked and both issues cannot be closed until either the environment is fixed or verification is re-specified

Do not close #6101 based on diff inspection. Verification strength requires running the specified framework test suite, not code review.
