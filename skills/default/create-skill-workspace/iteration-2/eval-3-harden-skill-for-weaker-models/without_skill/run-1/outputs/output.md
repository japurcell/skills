# Benchmark workspace layout

Use the canonical sibling pattern `skills/<skill>-workspace/iteration-N/`. For this revision, the concrete workspace would be `skills/task-wave-workspace/iteration-N/`, with the original draft saved once as the baseline snapshot.

```text
skills/<skill>-workspace/
  skill-snapshot/
    SKILL.md
    evals/
      evals.json
      grade_benchmark.py
  iteration-N/
    eval-0-multi-surface-skill-update/
      eval_metadata.json
      with_skill/
        run-1/
          outputs/
            response.md
            metrics.json
          transcript.md
          timing.json
          grading.json
      old_skill/
        run-1/
          outputs/
            response.md
            metrics.json
          transcript.md
          timing.json
          grading.json
    eval-1-rewrite-vague-plan/
      ...
    eval-2-installer-validation-wave/
      ...
    eval-3-no-wave-needed/
      ...
    benchmark.json
    benchmark.md
    review.html
```

Concrete example for this skill:

```text
skills/task-wave-workspace/
  skill-snapshot/
    SKILL.md
    evals/
      evals.json
      grade_benchmark.py
  iteration-1/
    eval-0-multi-surface-skill-update/
    eval-1-rewrite-vague-plan/
    eval-2-installer-validation-wave/
    eval-3-no-wave-needed/
```

Layout notes:

- Keep generated runs out of `skills/task-wave/`; this repo treats `skills/*-workspace/**/outputs/` as benchmark artifacts.
- Use `old_skill/` with `skill-snapshot/` as the baseline because this task improves an existing draft rather than creating a brand-new skill.
- Keep one canonical `eval_metadata.json` beside each `eval-*` directory so local graders and aggregation scripts can walk the iteration cleanly.
- Point live prompts at the exact local `skills/task-wave/SKILL.md` or snapshot path and tell the model to ignore other installed copies of the same skill name.
- After runs finish, grade with `python3 skills/task-wave/evals/grade_benchmark.py skills/task-wave-workspace/iteration-N`, aggregate with `python -m scripts.aggregate_benchmark skills/task-wave-workspace/iteration-N --skill-name task-wave`, then generate `review.html`.
