# Tightening summary

- Preserved the skill identity as `review-handoff` and rewrote the description so it says what the skill does and when to use it.
- Replaced the draft's repeated wording with one explicit workflow: read the real diff and validation, write the handoff with fixed reviewer-facing headings, and keep each risk, gap, or follow-up in only one section.
- Tightened the guidance around reviewer decisions: `Files to Review` now requires `path` - why it matters, `Reviewer Focus` owns risks and edge cases, and `Validation` bans vague phrases like "normal tests."
- Added benchmark assets under `review-handoff/evals/`: `evals.json` covers backend, mixed API/UI, migration, and no-validation edge cases, and `grade_benchmark.py` deterministically checks heading order, concrete validation, and duplicate-free handoffs.

# Benchmark plan

Use this revised skill as `with_skill` and compare it against an `old_skill` or snapshot baseline copied from `skills/create-skill/evals/files/review-handoff-draft/`.

From the repo root:

1. Validate the generated skill:
   - `python3 skills/skill-creator/scripts/quick_validate.py skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/without_skill/run-1/outputs/review-handoff`
   - `python3 -m py_compile skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/without_skill/run-1/outputs/review-handoff/evals/grade_benchmark.py`
2. Run live `copilot -p` benchmarks with prompts that point at `skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/without_skill/run-1/outputs/review-handoff/SKILL.md` and explicitly say to ignore other installed copies of `review-handoff`.
3. Save response, transcript, and timing artifacts under `skills/review-handoff-workspace/iteration-N/`, then grade them with:
   - `python3 skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/without_skill/run-1/outputs/review-handoff/evals/grade_benchmark.py skills/review-handoff-workspace/iteration-N`
4. If this revision is promoted into `skills/review-handoff/`, rerun `./scripts/copilot-install.sh` before checking installed behavior.
