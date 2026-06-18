Next orchestrator actions (dry-run) after implementer returned from mode: review_fix for story-billing-retry

1. Confirm implementer Progress block appended.
   - Evidence: progress.txt shows implementer return at 2026-06-10T11:50:00Z with Status = DONE and note that latest code-affecting change was the review fix.
   - If missing: append corrective orchestrator entry and STOP.

2. Rerun code-simplifier on combined final state (dry-run).
   - Append code-simplifier Progress block to progress_file immediately.

3. Run requirements-collector on combined final state (dry-run).
   - Append requirements-collector Progress block immediately.

4. Run addy-code-reviewer on simplified, requirement-checked combined state (dry-run).
   - Append reviewer Progress block immediately. Record review findings and whether review is clean.

5. Branch on reviewer outcome:
   A) If review is clean:
      - Run final verification checks specified by story and repo guidance (dry-run).
      - Append orchestrator verification entry.
      - If Completion Gate satisfied, set story `passes: true` in prd_file (record planned change) and append finalization orchestrator entry.
      - Produce distilled self-improve summary from progress_file and prepare AGENTS.md handoff (dry-run note).

   B) If review finds issues:
      - Read review-fix iteration count from progress_file (current = 1).
      - If count < 3:
         - Increment iteration count (record in progress_file as planned append) to count+1.
         - Dispatch fresh implementer with mode: review_fix and full findings; require Progress block appended before consuming.
         - After implementer Progress block, go to step 2 (rerun simplifier -> reqs -> review).
      - If count >= 3:
         - Append orchestrator stop-state entry stating review-fix iteration limit reached.
         - Do not dispatch another review-fix implementer.
         - Reread prd_file, append stop-state, and ask user to decide/unblock.

6. Verification checklist before marking `passes: true` (dry-run assertions):
   - Latest code-affecting change came from fresh implementer.
   - Code-simplifier ran after that change.
   - addy-code-reviewer ran after that change and review is clean.
   - Final verification checks passed.
   - All subagent Progress blocks were appended before consumption.

7. Recording and handoff (dry-run):
   - Append orchestrator final-state entry to progress_file with summary, files, verification outcomes, and learnings.
   - Distill durable learnings from progress_file and prepare concise handoff for AGENTS.md (validation rules, testing anti-flakes, UX constraints, env/setup notes).

Notes (dry-run):
- Do not modify repository files in this run; record planned changes only.
- If any Stop Condition arises (contradiction, missing details, or real blocker), append stop-state and ask user.
