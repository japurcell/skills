# Benchmark workspace layout

For an existing-skill benchmark in this repo, I would keep the source skill clean and put all benchmark artifacts in a sibling workspace:

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
            task-wave/
              SKILL.md
              evals/
                evals.json
          response.md
          transcript.md
          timing.json
          grading.json
      without_skill/
        run-1/
          outputs/
            task-wave/
              SKILL.md
              evals/
                evals.json
          response.md
          transcript.md
          timing.json
          grading.json
    eval-1-rewrite-vague-plan/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
      without_skill/
        run-1/
          outputs/
    eval-2-installer-validation-wave/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
      without_skill/
        run-1/
          outputs/
    eval-3-no-wave-needed/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
      without_skill/
        run-1/
          outputs/
    benchmark.json
    benchmark.md
    review.html
```

Notes:

- Keep benchmark artifacts out of `skills/task-wave/`; this repo treats workspace outputs as generated fixtures.
- Keep one canonical `eval-*` directory per scenario, with a single `eval_metadata.json` beside the compared configurations, because the local grading helpers expect that layout.
- Use `skill-snapshot/` for the baseline skill definition, then compare `with_skill/` and `without_skill/` runs inside the same iteration so transcripts, timings, and grading stay aligned.
