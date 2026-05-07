# Validation, benchmarking, and refresh

These commands assume the generated artifact has been promoted into `skills/release-notes-skill/` and benchmark runs will live under `skills/release-notes-skill-workspace/iteration-N/`.

## 1. Validate the skill files

```bash
python3 skills/skill-creator/scripts/quick_validate.py skills/release-notes-skill
python3 -m py_compile skills/release-notes-skill/evals/grade_benchmark.py
```

## 2. Benchmark the skill against a baseline

For a brand-new skill, use `without_skill` as the baseline and save run artifacts under `skills/release-notes-skill-workspace/iteration-N/eval-*/{with_skill,without_skill}/run-1/`.

```bash
python3 skills/release-notes-skill/evals/grade_benchmark.py skills/release-notes-skill-workspace/iteration-N
PYTHONPATH=skills/skill-creator python3 -m scripts.aggregate_benchmark \
  skills/release-notes-skill-workspace/iteration-N \
  --skill-name release-notes-skill
PYTHONPATH=skills/skill-creator python3 skills/skill-creator/eval-viewer/generate_review.py \
  skills/release-notes-skill-workspace/iteration-N \
  --skill-name "release-notes-skill" \
  --benchmark skills/release-notes-skill-workspace/iteration-N/benchmark.json \
  --static skills/release-notes-skill-workspace/iteration-N/review.html
```

## 3. Refresh installed copies after the repo skill is updated

```bash
./scripts/copilot-install.sh
```
