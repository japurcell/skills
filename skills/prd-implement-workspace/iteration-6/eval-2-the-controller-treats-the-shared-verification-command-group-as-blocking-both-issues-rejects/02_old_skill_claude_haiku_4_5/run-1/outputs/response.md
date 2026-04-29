# PRD #6000 Verification Blocker: Shared Command Group Failed; Both Issues Blocked

**Status:** Shared verification command group failed; both child issues #6101 and #6102 remain open.

## Verification plan and failure

The controller created a shared verification command group:
- **Covered issues:** #6101 (CSV export filters) and #6102 (CSV export download audit log)
- **Shared command:** `bundle exec rspec spec/requests/admin/export_spec.rb`
- **Result:** `/bin/sh: bundle: command not found`

The verification subagent cannot proceed because `bundle` (Ruby bundler) is not available.

## Blockage rule: Shared command groups are atomic

Per the prd-implement skill rules (section "Verification subagents and issue updates"):

> Do not close any child issue covered by a shared command group unless that shared group passes.

And per rule 223:

> If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker.

## Why we cannot close #6101 alone

Another agent proposes closing #6101 anyway because its diff looks correct. **This proposal is rejected.**

- #6101 is covered by the shared command group.
- The shared group did not pass.
- Diff inspection or "looks correct" reasoning is not a substitute for the required verification command.
- Per the skill: "do not replace framework-native verification with static analysis, source inspection, or generic 'looks correct' reasoning."
- If we close #6101 without passing the shared group, we break the verification contract for #6102, which uses the same test suite and would no longer be verifiable.

## Current state

- Child issue #6101 **remains open**
- Child issue #6102 **remains open**
- Parent PRD task-graph line for #6101 **remains `[ ]` unchecked**
- Parent PRD task-graph line for #6102 **remains `[ ]` unchecked**
- Wave W4 is **blocked** on the missing `bundle` CLI
- Both issues are covered by the same blocker; neither can close independently

## Next step

The missing `bundle` command (Ruby environment) must be resolved before verification can proceed. Stop here and escalate to the user. Do not proceed to close either issue or advance to the next wave.
