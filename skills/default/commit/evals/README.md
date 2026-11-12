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
Read-only skill snapshots are accepted. Preparation temporarily enables writes
on the copied `scripts/` directory while installing the validator observer, then
restores that copied directory's original mode. The source snapshot is unchanged.

Write `eval_metadata.json` beside the configuration directories with `eval_id: 4`,
the scenario name, prompt, and assertions from `evals.json`. Replace `<run-dir>`
in that prompt with the prepared absolute path, then give the prompt to the agent.
The agent may change only the draft and fixture repository and write its response
under `outputs/`. It must preserve the supplied skill, instrumentation, and Git
configuration. Prohibit direct edits to `fixture.json` and `events.jsonl`, while
explicitly allowing the bundled validator and Git hook to append their own
observations to `events.jsonl`.

Run each provider turn with the prepared `repo/` as its working directory. For
Codex workspace-write sessions, pass the absolute run directory with `--add-dir`
on both the initial invocation and the resume, so observers can append evidence
and message drafts can be written outside `repo/`. Resume the same persistent
session for contribution and commit turns; do not use an ephemeral session.
For Copilot, use `--session-id` for the new session, `--resume=<id>` for the
second turn, and `--add-dir` for the run directory. Do not combine `--trust-folder`
with `--session-id`: the CLI rejects that combination. Record provider versions,
model and reasoning settings, and use the same settings for paired runs.
For parallel runs, require a distinct message-file path inside each disposable
run directory. Otherwise run comparisons sequentially. Audit the observed
message paths and provider-turn times for overlaps, and retain any collisions
as failed or excluded evidence.

The copied validator records its actual exit status, input path, and message in
`events.jsonl`, including the actual argument vector passed to the validator. A
commit-message hook records each commit attempt without blocking it. These
observers do not fix the message or enforce the evaluated workflow. `fixture.json`
records the initial commit and expected fixture content. The grader checks event
ordering and content against actual Git history; the agent's written claims are
not grading evidence. Keep the raw events, response, timing, and snapshots for
each run.

Scenario 5 exercises Codex default attribution with a fixture that leaves the
change for the agent to make. Prepare it with the scenario fixture:

```sh
python3 skills/default/commit/evals/prepare_validation_workflow.py \
  <iteration>/eval-5-codex-default-attribution/with_skill/run-1 \
  <skill-snapshot> \
  --fixture skills/default/commit/evals/files/agent-attribution/input.json
```

Its fixture metadata supplies the expected identity to the grader. The grader
requires the final successful validator invocation to pass that identity once
with `--co-author`, and checks that the actual Git message contains the matching
trailer exactly once. Missing or malformed argument evidence fails grading.
Use one Codex CLI session from the prepared `repo/` directory. Send the
scenario's `contribution_prompt` first, then resume that same session with its
ordinary `prompt`; the commit prompt contains no attribution hint.

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

Scenario 6 checks Copilot attribution after a same-session contribution. Prepare
it using the Copilot fixture:

```sh
python3 skills/default/commit/evals/prepare_validation_workflow.py \
  <iteration>/eval-6-copilot-default-attribution/<configuration>/run-1 \
  <skill-snapshot> \
  --fixture skills/default/commit/evals/files/copilot-attribution/input.json
```

Use one Copilot CLI session for both scenario prompts. From the prepared `repo/`
directory, send `contribution_prompt` first and verify the edit without
committing; resume that same session with the ordinary `prompt`. Do not add
attribution hints. Run the baseline from `iteration-5/baseline-skill/` and the
candidate from a frozen candidate snapshot, with identical model settings per
provider. Record CLI version, selected model, transcripts, actual validator
arguments, committed message, and initial/final author metadata. Keep each run
in a fresh directory. The grader inspects the argument vector, final Git
message, changed paths, and unchanged fixture author; agent claims are not
grading evidence.

Use actual Codex and Copilot CLIs for their respective cases. Scenario 6 stores
two prompts so the commit request itself remains neutral: the preceding turn
establishes contribution, then the ordinary commit prompt measures attribution.

Scenarios 7-12 exercise attribution precedence and exclusions with the same
observed workflow grader: explicit identity, explicit opt-out, repository
suppression, user identity over conflicting repository policy, no contribution,
and preservation/deduplication of an existing matching trailer plus another
established contributor. Prepare each from the fixture path named in
`evals.json`. When a `contribution_prompt` exists, send it first in the same
provider session and resume with that scenario's `prompt`. Scenario 11 has no
contribution turn and starts with another person's staged change. Scenarios 9
and 10 commit their repository policy in `AGENTS.md` as initial fixture state.
The fixture's `expected_coauthors` is grading metadata; do not disclose it to
the provider unless the scenario prompt itself supplies an explicit user
identity. Keep the observed validator options and commit message for every run.

Scenarios 13 and 14 start with another person's staged change and no agent
contribution turn. Scenario 13 supplies a human identity explicitly; scenario
14 establishes a human contributor in the supplied draft. Each must retain the
human identity in both the commit and validator arguments without inventing an
agent identity. Compare both against the immutable pre-fix skill snapshot.
