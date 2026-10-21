# Accomplishment report evaluation

- Selected runs: `eval-1` through `eval-3`, `with_skill` from agent `eval_with`, `without_skill` from fresh agent `baseline_clean`.
- Model: `gpt-6-luna`, reasoning effort `max`, both configurations. Three prompts were batched into each agent. Synthetic prompt facts substituted for a real repository and plan; no live completion event or installer execution was tested.
- Results: 11/11 with-skill assertions and 7/11 baseline assertions. The skill supplied dated agency alignment, explicit oversight accounting, and exact output paths. Both configurations calculated the measured base case correctly and rejected false completion. The assertions are scenario checks, not a general proof of report quality.
- The initial baseline read the rubric accidentally and was interrupted before producing outputs. It is excluded. `baseline-prompts.json` contains the prompt-only input used for the replacement.
- The coordinator supplied a nonexistent `skills/default/exec-plans/SKILL.md` path. The with-skill agent found `.agents/skills/exec-plans/SKILL.md`; the baseline reported the missing path. This asymmetry limits attribution of score differences to the new skill alone.
- Per-scenario runtime and token measurements were unavailable. `timing.json` records nulls; benchmark metrics omit them. No zero or character-count proxies represent measured usage. One sample per scenario cannot establish repeated-run variance.
- `review.html` shows reports and grading. `review-preview.md` files are copies for the viewer, which only loads immediate output files; nested reports retain their tested destinations. Source packets are explicitly synthetic.
- Validation: skill-creator `quick_validate.py` passed; repository `scripts/validate-skill-sources.py skills` passed; reference arithmetic and output table arithmetic were independently checked. No runtime code changed.
- Reflection: estimation safeguards live in the new skill. No additional brain note was needed. Suggested create-skill workflow improvement: pass executors prompt-only files, keeping expected outputs and assertions in coordinator-owned grading inputs.
