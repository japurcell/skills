# Benchmark workspace layout

For an improved existing skill, use a sibling workspace with the original draft saved as the baseline:

```text
skills/task-wave-workspace/
  skill-snapshot/
    SKILL.md
    evals/
      evals.json
  iteration-1/
    eval-0-multi-surface-skill-update/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
      old_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
    eval-1-rewrite-vague-plan/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
      old_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
    eval-2-installer-validation-wave/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
      old_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
    eval-3-no-wave-needed/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
      old_skill/
        run-1/
          outputs/
          transcript.md
          timing.json
          grading.json
    benchmark.json
    benchmark.md
    review.html
```

Notes:

- Keep benchmark artifacts out of `skills/task-wave/`; they belong in the sibling `skills/task-wave-workspace/`.
- Use `old_skill/` as the baseline because this task improves an existing draft rather than creating a brand-new skill.
- Put the revised skill outputs only in `with_skill/.../outputs/` and keep timing/grading files next to each run so aggregation can compare both configurations cleanly.
