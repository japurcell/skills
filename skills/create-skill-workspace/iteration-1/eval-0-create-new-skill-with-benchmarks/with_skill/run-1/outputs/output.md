# Commands

Run these from the repository root:

## Validate the generated skill files

```bash
python3 skills/skill-creator/scripts/quick_validate.py skills/create-skill-workspace/iteration-1/eval-0-create-new-skill-with-benchmarks/with_skill/run-1/outputs/release-notes-skill
python3 -m py_compile skills/create-skill-workspace/iteration-1/eval-0-create-new-skill-with-benchmarks/with_skill/run-1/outputs/release-notes-skill/evals/grade_benchmark.py
```

## Grade benchmark-style runs for this skill

```bash
python3 skills/create-skill-workspace/iteration-1/eval-0-create-new-skill-with-benchmarks/with_skill/run-1/outputs/release-notes-skill/evals/grade_benchmark.py skills/release-notes-skill-workspace/iteration-1
```

## Refresh installed copies after promoting the skill into `skills/release-notes-skill/`

```bash
./scripts/copilot-install.sh
```
