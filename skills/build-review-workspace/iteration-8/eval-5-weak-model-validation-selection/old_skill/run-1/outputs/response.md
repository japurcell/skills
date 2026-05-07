From `/home/adam/dev/personal/skills/skills/build-review-workspace/skill-snapshot-iteration-8/SKILL.md`, the manager should **dispatch immediately with a lean handoff**, not pre-read or pre-solve. That handoff should contain only:

```md
Task: [next plan task text]
Success criteria:
- [expected behavior for scripts/addy-install.sh]
- [expected behavior for skills/build-review/evals/grade_benchmark.py]

Known constraints / validation commands:
- Choose validation by the slice's stack; do not default to generic frontend commands.
- Shell validation: bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh
- Python validation: python3 -m py_compile skills/build-review/evals/grade_benchmark.py
- If grader behavior changes, run the grader on a relevant benchmark fixture/run dir.

Already-known file hints:
- scripts/addy-install.sh
- skills/build-review/evals/grade_benchmark.py
```

Everything else stays with the implementer: **repo discovery, pattern lookup, first-pass design, code changes, and final verification selection**. The implementer should infer the slice’s **surface and stack first**. Since this slice is **shell + Python**, the matching checks are shell/Python checks, not `npm`, frontend build, or generic UI commands. If only the installer changes, run the shell checks; if only the grader changes, run the Python checks; if grader logic changes materially, add a targeted run like `python3 skills/build-review/evals/grade_benchmark.py skills/build-review-workspace/iteration-7/eval-5-weak-model-validation-selection`. That is the guardrail that keeps a weaker model from falling back to generic frontend validation.
