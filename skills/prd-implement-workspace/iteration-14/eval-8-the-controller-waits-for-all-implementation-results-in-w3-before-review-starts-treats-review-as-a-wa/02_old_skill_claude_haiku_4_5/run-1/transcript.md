## Prompt

You are executing /prd-implement for PRD #9400. Current wave W3 has AFK child issues #9401, "Backfill invoice timezone," and #9402, "Add invoice timezone admin filter." Both were launched in parallel because their likely files do not overlap. #9401 finishes first with a clean RED -> GREEN -> REFACTOR chain and passing targeted tests. #9402 is still running and has not returned yet. Another agent proposes starting review on #9401 now and, if it looks good, closing #9401 immediately so W4 can start sooner. Show the controller's response.

## Response

# Wave W3 parallelism and review sequencing for #9401 and #9402

Current state:
- #9401 "Backfill invoice timezone" — implementation complete, RED → GREEN → REFACTOR chain verified, passing targeted tests
- #9402 "Add invoice timezone admin filter" — still in progress
- Proposal: start review on #9401 now, and close #9401 immediately if review passes

## Controller assessment

The skill rules require strict wave sequencing:

- **Wave execution lifecycle:** "Finish all implementation work launched for the current wave... run one review phase for the whole wave... only after review and verification are clear may the implementation subagents perform GitHub closeout."
- **Blocking rule:** "After every wave, wait for all implementation results, inspect each result, run one wave-level review phase across the combined changed-file set."

The proposal to close #9401 early while #9402 is still in progress violates this rule. W3 review must cover the combined file set for both issues, not a partial review of #9401 alone.

## Outcome

- #9401 implementation is complete but remains open pending full W3 review.
- #9402 is still in progress.
- The controller must wait for all W3 implementation to finish before launching the W3 review phase.
- Landing status: no commit, push, or PR actions performed in this run.

Next step: Wait for #9402 implementation to complete, then run one unified W3 review phase across both issues' file sets.
