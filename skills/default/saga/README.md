# Saga skill maintenance and evaluation

Use this README when changing the Saga skill or its evaluation assets. Runtime behavior belongs in `SKILL.md` and the linked references; keep evaluation setup and maintenance steps here.

## Evaluation set

`evals/evals.json` covers three distinct decisions:

1. Create a Phase 1 saga from a realistic medium-sized feature request, and stop for approval before implementation.
2. Resume a supplied saga by reconciling its progress record against branch and worktree evidence.
3. Avoid creating a duplicate saga when a small requested change already belongs to an existing plan.

The fixture trees under `evals/files/` are inputs. Keep them immutable during runs. Copy each selected fixture into a fresh disposable repository outside the maintained skill bundle. Never run an evaluation against a real user repository or allow fixture prompts to write outside their disposable root.

## Paired live runs

For behavior changes, create an immutable pre-change snapshot of the skill at `<evaluation-root>/old_skill/` before making changes, then compare the current skill against it. Use a fresh agent context for each run, the same model and task prompt within a pair, and the exact skill source path for that configuration. Tell each agent to ignore installed copies. The baseline for this existing skill is `old_skill`, not `without_skill`.

Keep run-specific snapshots and baseline evidence outside this bundle. The bounded path-selection baseline asks only what path the old skill selects and what action comes next; it creates no saga files. Keep it distinct from the full paired runs, which execute Phase 1 only inside a disposable fixture.

Use this output layout for paired runs:

```text
<evaluation-root>/iteration-1/
└── eval-0-create-planning-only-saga/
    ├── eval_metadata.json
    ├── old_skill/run-1/
    │   ├── response.md
    │   ├── transcript.md
    │   └── timing.json
    └── with_skill/run-1/
        ├── response.md
        ├── transcript.md
        └── timing.json
```

Use matching eval names for IDs 1 and 2. Record exact source paths, model, run identity, fixture copy path, and selected configuration in `eval_metadata.json`. Preserve complete responses and transcripts before grading. Capture token and elapsed-time data only when the runner reports measured values; use `null` or mark the field unavailable otherwise. Do not infer duration or tokens from character counts.

## Grading

Run the focused CLI grader for each saved run. Give it the immutable fixture as `--source-fixture` and that run's separate copy as `--fixture-root`; its checks require the creation output to be directly under `<fixture-root>/brain/sagas/<id>`, require the SAGA/PROGRESS path records to match, and compare other fixture files against the source. Resume and duplicate-avoidance runs must leave the fixture byte-identical. Missing response/transcript files and malformed CLI arguments are invalid inputs and return 2. A valid run with failed expectations still writes `grading.json` and returns 0, so inspect `summary.failed`.

```sh
python3 skills/default/saga/evals/grade_evals.py \
  --eval-id 0 \
  --source-fixture /path/to/immutable/cache-refresh-repo \
  --fixture-root /path/to/run/repo-copy \
  --response /path/to/run/response.md \
  --transcript /path/to/run/transcript.md \
  --output /path/to/run/grading.json
```

The CLI grader covers deterministic file and response checks: 5 checks for creation, and 2 each for resume and duplicate avoidance. It checks the actual disposable fixture contents, not only the response. A resolved absolute saga path is valid when both spec files record that same path. Generated `brain/index.md` navigation links are allowed only when they append links to files in the new saga and leave existing index content intact. The runner's empty `nested/` working directory is the sole ignored directory-only change.

The manifest has additional behavior expectations, including worker dispatch and source-edit constraints. Review the saved operation log for those, but classify claims as agent-reported when no host trace is available. An agent-recorded log and unchanged fixture cannot independently prove that no worker was dispatched. Report deterministic grader results separately from unverified trace-dependent expectations. Record each check as `{ "text": "...", "passed": true, "evidence": "..." }` in `grading.json`, with a `summary.failed` count.

These are three targeted scenarios, not a statistical benchmark or a general guarantee about Saga behavior. Report sampled output quality separately from instruction-coverage checks. Preserve valid failures; revise the skill only when a run demonstrates a real behavior gap.

## Focused validation

From the repository root, validate the manifest and grader. Activate `skill-creator`, resolve its installed skill directory, and run its validator from that location:

```sh
python3 -m json.tool skills/default/saga/evals/evals.json >/dev/null
python3 -m unittest discover -s skills/default/saga/evals -p test_grade_evals.py
python3 <resolved-skill-creator-directory>/scripts/quick_validate.py skills/default/saga
```

The JSON tool checks manifest syntax, the unittest command exercises the public grader CLI including invalid inputs, and the validator checks the skill package shape. These commands do not run a behavioral Saga evaluation.
