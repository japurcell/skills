Based on my reading of the SKILL.md file, I now have the authoritative answer. The key rule is at lines 204 and 108 of the skill file, and the critical principle is stated throughout:

**"After all implementation work in the wave finishes, run one review phase over the full changed-file set for that wave before any child issue in the wave can move to closeout."** (line 204)

**"After every wave, wait for all implementation results, inspect each result, run one wave-level review phase across the combined changed-file set, rerun review after any review-driven fixes, then verify covered child issues, then update issue state."** (line 108)

And from lines 114-117:
1. Finish all implementation work launched for the current wave.
2. Run the controller checkpoint, then one review phase for the whole wave.
3. After that review phase succeeds, run verification for the covered child issues.
4. Only after review and verification are clear may the implementation subagents perform GitHub closeout for those child issues.

Here is the controller's user-facing response for the scenario:

---

**W3 implementation status:** #9401 completed RED → GREEN → REFACTOR with passing targeted tests. #9402 still running.

**Controller decision:** Hold #9401 for wave-level review. **Cannot start early review or close #9401 until:**
1. #9402 finishes implementation (still pending)
2. Controller checkpoint passes on both tasks
3. Full W3 review phase completes across the combined changed-file set from both #9401 and #9402
4. Verification passes for all issues in the wave

**Reason:** The skill requires one wave-level review phase across the entire changed-file set for each wave *before* any child issue in that wave can move to closeout. Review cannot start until both parallel tasks finish, even if one finishes early with passing tests. Early individual review or premature closure of #9401 would violate the required wave completion sequencing.

**Next step:** Wait for #9402 to finish. Once both implementation results are in, run controller checkpoint, then unified W3 review, then verification, then closeout.
