# Evaluating agency-priorities

Run the prompts in `evals.json` with only the assigned `SKILL.md`. Do not supply a source packet, allow browsing, or permit reading any linked files. For revision comparisons, assign the saved previous `SKILL.md` to the baseline under the same constraints. Save responses in sibling `agency-priorities-workspace/iteration-N/eval-<id>/{with_skill,old_skill}/run-1/outputs/` directories.

Review each assertion semantically and retain evidence in each run's `grading.json`. Check completeness against the six USDA goals and eight Forest Service priorities embedded in the revised skill. Require explicit framework status, snapshot date, FY26 scope, and supported project mappings. Confirm from the execution record that the agent used only the assigned file; final prose alone cannot prove that boundary.

These cases cover creating a briefing, correcting a justification, and declining unsupported temporal and project-alignment claims. They test self-contained use, not live source retrieval or automatic skill triggering. No deterministic prose grader is shipped because keyword matching cannot establish attribution, temporal scope, or causal validity. Use the repository validator and JSON/link checks for structural validation. Report unavailable runtime metrics explicitly.

The earlier iteration-1 results used a shared source packet and do not establish that the skill alone supplied the required knowledge.
