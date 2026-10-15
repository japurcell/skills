# Tightening summary

- Preserved the skill identity as `review-handoff` and rewrote the description to be trigger-oriented instead of repetitive.
- Replaced duplicated draft guidance with one explicit workflow: read the real diff and validation, write the handoff with the exact heading order, name concrete commands, say `- None.` when no follow-up remains, and keep each risk or gap in one section.
- Tightened the body around reviewer decisions: `Files to Review` now requires `path` - why it matters, `Reviewer Focus` owns risks and edge cases, and `Validation` bans vague phrases like "normal tests."
- Added benchmark assets under `review-handoff/evals/`: `evals.json` covers backend, mixed API/UI, migration, and no-validation edge cases, and `grade_benchmark.py` deterministically checks heading order, concrete validation, deduped bullets, and scenario-specific requirements.

# Benchmark plan

Use this revised skill as `with_skill` and compare it against an explicit `old_skill` or draft snapshot baseline, for example `old_skill/review-handoff/` populated from `skills/create-skill/evals/files/review-handoff-draft/`.

From the repo root:

1. Validate the generated skill:
   - `python3 skills/skill-creator/scripts/quick_validate.py skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/with_skill/run-1/outputs/review-handoff`
   - `python3 -m py_compile skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/with_skill/run-1/outputs/review-handoff/evals/grade_benchmark.py`
2. Run live `copilot -p` benchmarks with prompts that point at the exact local `skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/with_skill/run-1/outputs/review-handoff/SKILL.md` path and explicitly say to ignore other installed copies of `review-handoff`.
3. Save response, transcript, and timing artifacts under a dedicated `skills/review-handoff-workspace/iteration-N/` directory, then grade them with:
   - `python3 skills/create-skill-workspace/iteration-2/eval-1-modify-existing-skill-to-dedupe/with_skill/run-1/outputs/review-handoff/evals/grade_benchmark.py skills/review-handoff-workspace/iteration-N`
