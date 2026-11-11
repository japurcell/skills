# Commit skill validation evaluations

## Focused checks

From the repository root:

```sh
python3 skills/default/commit/evals/test_validate_message.py
python3 skills/default/commit/evals/test_grade_benchmark.py
```

The first suite checks the public validator CLI, including LF and CRLF structure,
Unicode separators, required sections, trailers, and input errors. The second
exercises the workflow grader with real disposable Git repositories. It checks
successful recovery and rejects missing validation, missing revalidation, changed
messages after validation, and missing or malformed evidence.

## Live workflow scenario

Scenario 4 in `evals.json` checks failure, repair, revalidation, and commit using
actual commands. It is separate from the older dry-run scenarios. Run it against
immutable snapshots of the candidate skill and the pre-change skill in a fresh
sibling `commit-workspace/iteration-N/` directory. Use identical prompts and model
settings for the two configurations, with a fresh agent for each.

Record the baseline's origin explicitly. This scenario requires a bundled
validator in both snapshots. For the newline repair, use the task-start snapshot
that already contained the validation workflow, not a revision from before the
validator was introduced. This comparison measures recovery from the malformed
draft; it does not measure whether the skill independently chooses to validate
without the scenario's explicit instruction.

For each configuration, prepare a new run directory:

```sh
python3 skills/default/commit/evals/prepare_validation_workflow.py \
  <iteration>/eval-4-validation-before-commit/<configuration>/run-1 \
  <skill-snapshot>
```

The run directory must not exist. Preparation copies only the runtime skill,
creates a disposable repository with one staged documentation change, and writes
a draft containing Unicode line separators. Local Git identity, signing, and hook
settings affect only that fixture repository. No remote is configured.

Write `eval_metadata.json` beside the configuration directories with `eval_id: 4`,
the scenario name, prompt, and assertions from `evals.json`. Replace `<run-dir>`
in that prompt with the prepared absolute path, then give the prompt to the agent.
The agent may change only the draft and fixture repository and write its response
under `outputs/`. It must preserve the supplied skill, instrumentation, Git
configuration, and evidence files.

The copied validator records its actual exit status, input path, and message in
`events.jsonl`. A commit-message hook records each commit attempt without blocking
it. These observers do not fix the message or enforce the evaluated workflow.
`fixture.json` records the initial commit. The grader checks event ordering and
content against actual Git history; the agent's written claims are not grading
evidence. Keep the raw events, response, timing, and snapshots for each run.

Grade the completed iteration:

```sh
python3 skills/default/commit/evals/grade_benchmark.py <iteration>
```

Inspect each `grading.json` file's `summary.failed`; the grader exits zero after
writing reports even when assertions fail. Missing or malformed evidence fails
grading. Preserve failed baseline results. One run per configuration demonstrates
the observed case, not reliability across repeated model runs. Report measured
wall time separately from unavailable token usage; the shared aggregator may
substitute output characters for missing tokens.
