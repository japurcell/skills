# Evaluating agency-priorities

Run each prompt in `evals.json` with the supplied offline source packet. Compare one agent using the exact local `SKILL.md` with a baseline that cannot read this skill or its reference notes. Both receive the same packet and cannot browse. Save responses under the sibling `agency-priorities-workspace/iteration-N/eval-<id>/{with_skill,without_skill}/outputs/`.

Review each assertion semantically and retain a supporting excerpt in the run's `grading.json`. These checks concern attribution, negation, temporal scope, and causal claims; keyword matching cannot establish their truth. No deterministic prose grader is shipped. Use the repository skill validator and JSON/link checks for structural validation.

The cases cover creating a briefing, correcting a project justification, and rejecting stale or unrelated alignment. They test use of supplied evidence, not live source discovery, PDF extraction, or automatic skill triggering. A passing baseline means the sample did not demonstrate added skill value. Do not infer a quality advantage from a tie.

For a separate live-source check, ask for a current briefing and inspect the retrieval trace: the agent should visit the USDA performance page, open its currently linked strategic PDF, read the Forest Service priorities page, and verify annual direction for the requested fiscal year. Grade inaccessible-source handling explicitly rather than treating failed access as a passing freshness check.
