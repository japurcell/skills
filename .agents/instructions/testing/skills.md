---
type: Agent Instruction
description: Validation and public grader tests for publishable and repo-local skills
---

# Skills - Testing

- Run `rtk proxy env PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>` (use `.agents/skills/<skill-name>` for local workflows) after changing a skill definition, except for the explicitly scoped `dotnet-upgrade` document review below.
- If packaging behavior changed, run `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`.
- If a skill ships `evals/grade_benchmark.py` and you edited it, run `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py`.
- If benchmark grading behavior changed, run `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>`.
- Treat `skills/*-workspace/**/outputs/` as generated artifacts, not maintained source.

## Document-maintenance graders

`skills/handoff/evals/` covers creation, feature updates, invalid-path fallback, stale-history resume, and pending owner rollout. `.agents/skills/exec-plans/evals/` covers novice plan creation, two resumed code checkpoints, and completed code with pending owner approval and recovery. Each contains its own fixtures, assertions, grader, and public-CLI tests.

Handoff [guidance scenarios](../../../skills/handoff/evals/guidance-scenarios.json) supplement the deterministic suite with read-only review, a supplied path among several feature folders, and history updates with retained lessons and existing archive content. They use `files/guidance-edges-fixture/` and are outside the public grader's five supported cases. Check fixture bytes before and after each run, then review commands, observed errors, lesson placement, owner limits, and reporting semantics; passing selected assertions does not establish every output requirement.

ExecPlan [authoring scenarios](../../skills/exec-plans/evals/authoring-scenarios.md) add qualitative prototype/migration cases and task boundaries using the large-input brief and existing create-plan project. Review feasibility, both-path validation, task prerequisites, shared invariants, integrated proof, owner boundaries, and exact commands manually; these cases are outside the deterministic grader's three supported scenarios. Preserve instruction-coverage findings separately from sampled agent-performance claims.

Run the focused suites from the repository root:

```bash
rtk proxy python3 -m unittest discover -s skills/handoff/evals -p test_grade_benchmark.py
rtk proxy python3 -m unittest discover -s .agents/skills/exec-plans/evals -p test_grade_benchmark.py
```

Both graders consume canonical iteration directories. Exit `0` means grading files were written, including failing assertions; inspect `expectations` and `summary.failed` for acceptance. Invalid invocation or input errors exit nonzero. Public cases cover valid wording and line ranges alongside stale actions, missing archive evidence, history-only recovery, unauthorized agent or contributor actions, and contradictory proof claims. Conditional wording and descriptive modifiers must not hide a separate factual claim in a comma, coordinated, or contrasting clause. These are scenario-specific heuristics, not a general natural-language verifier.

Use `PYTHONPATH=scripts/vendor` for skill definition validation. In a sandbox that protects `.agents/`, compile with `PYTHONPYCACHEPREFIX` pointing to a writable temporary directory so bytecode generation does not attempt to edit the protected bundle. See [benchmark reporting limitations](../../memory/known-issues/skills.md) before interpreting absent runtime metrics.

## Task workflow graders

Run the public CLI suites from the repository root; both are registered in `scripts/test-all.py`:

```bash
rtk proxy python3 skills/spec-to-tasks/evals/test_grade_benchmark.py
rtk proxy python3 skills/prd-ralph-loop/evals/test_grade_benchmark.py
```

Producer cases preserve status/member/notification/token requirements and add lifecycle and inline-document inputs. The spec grader checks complete fields, references, graph shape, applicability, readiness, and scenario-specific coverage. A valid fixture must include the original task fields as well as enriched fields; a passing grade for an incomplete fixture is a grader defect. Public controls distinguish backend database tables/rows/filters from browser UI, reject malformed references including NUL paths, and preserve unavailable metrics for non-object timing data. Synthetic command strings exercise grading logic, not real project command provenance.

The loop suite covers exact completion, blind continuation, blocked stops, forwarded constraints, complete and consistent decision fields, malformed decisions and unavailable metrics. It checks the simulated run's outputs without reading the current skill to score a frozen baseline. `skills/execplan-implement/evals/evals.json` provides document-only orchestration scenarios. `skills/prd-ralph/evals/evals.json` defines disposable execution scenarios for complete task input, incomplete all-true input, unresolved verification, and commit audits; read-only protocol interpretations do not establish that those sandbox executions passed. Semantic review remains required for current authority, context sufficiency, actual dependencies, negative cases, and integrated acceptance. See the [producer eval guide](../../../skills/spec-to-tasks/evals/README.md) and [loop grader](../../../skills/prd-ralph-loop/evals/grade_benchmark.py) for artifact and CLI details.

## dotnet-upgrade document review

The approved acceptance scope is document review and non-mutating JSON/whitespace checks. Review the provenance ledger, bundled navigation, evidence scope, exact invocation controls and six paper scenarios. Parse `references/provenance/source-map.json` and `evals/evals.json` with `python3 -m json.tool`; check scoped diffs with `git diff --check`. Run `./scripts/lint-okf.py` for canonical agent-document changes.

Do not run `quick_validate.py`, archive packaging, live models, benchmarks, trial upgrades, application commands or installers as acceptance gates. The requested frontmatter incompatibility is retained, not waived as a passing result. The integrated document-only acceptance record is [references/document-review.md](../../../skills/dotnet-upgrade/references/document-review.md); it covers ledger, navigation and paper scenarios, not migration behavior, refreshed vendor facts or live client enforcement.

For maintained synthetic fixtures, keep narrow `.gitignore` exceptions and check `git ls-files --others --exclude-standard` before staging. Generated run logs remain disposable.
