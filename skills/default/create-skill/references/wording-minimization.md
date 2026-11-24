# Minimize skill wording

1. **Freeze the baseline.** Snapshot the complete bundle, dependencies and input fixtures outside the source tree. Preserve frontmatter, especially the trigger description, unless trigger tuning was requested. For new skills retain both the uncut draft and a without-skill control.
2. **Map obligations to evidence.** For each required decision, exception, authority boundary and output, record the original phrase, smallest distinguishing scenario, expected observation, and where to inspect it. If the skill promises fallback, include a case that requires it. For orchestration, inspect the native trace for actual tool calls, worker identity and ordering alongside the final artifact. Tabletop responses establish what an agent can describe.
3. **Establish the comparison.** Use the target's documented harness, grader and acceptance scope. Record provider, CLI version, model, effort, capabilities, prompt, fixture revision and bundle identity. Reuse retained baseline runs when those inputs match. Verify baseline evidence for every obligation before attributing a failure to a cut. A without-skill control can reveal native defaults when attribution matters.
4. **Try one cut.** Start with duplicated rules or passages already supplied by a required skill. Among remaining cuts try the largest first. Copy the current shortest passing bundle and delete one independently testable phrase. Use the helper below. Run only its distinguishing case in a fresh isolated project. Use Codex by default and reserve Copilot runs for requested or provider-specific evidence. Reuse results only for identical candidates and conditions.
5. **Decide from the evidence.** Record the candidate hash, parent, cut, body words, case, run path, observed decision and verdict. Keep raw outputs, traces, grader results and failed candidates. A failed obligation rejects the cut. Repeat a borderline pass in a fresh session when evidence is indirect, outcomes disagree or the model could succeed through a different path. If outcomes differ, retain the wording and describe the variance. Mark missing capabilities or inconclusive evidence unresolved.
6. **Verify the winner.** Continue from the shortest passing candidate until remaining meaningful cuts fail or lack support. Run the full applicable suite on that exact bundle; count already completed cases with matching conditions. Restore wording for any regression and verify the restored candidate. Report old and selected body word counts, selected runs, rejected cuts and the observations that justified retention. Claim the shortest version tested. Word counts measure text length; report token usage only when measured.

## Prepare a candidate offline

Use Python 3.9+ with the standard library. Set `helper` to this skill's [scripts/wording_trial.py](../scripts/wording_trial.py), `baseline` to the trusted self-contained bundle and `work` to a fresh external trial directory. For example, with a skill containing “Explain local fallback.” in its body, run the following.

```sh
mkdir -p "$work"
python3 "$helper" cut "$baseline" "$work/cut-local" 'local ' > "$work/cut-local.json"
diff -u "$baseline/SKILL.md" "$work/cut-local/SKILL.md"
```

The helper copies the complete bundle, preserves frontmatter bytes and deletes an exact body substring occurring once. For repeated text, use a manual contextual edit in a fresh copy and inspect the diff. Give each trial and its JSON file a new name. No stdin. Standard output contains JSON with both SKILL.md hashes, body word counts and cut text. Diagnostics go to standard error. Exit 0 indicates success, exit 2 an invalid invocation or preparation error. Use `--help` for arguments. The expected one-line change gives `diff` exit 1. Run the maintained scenario harness against the candidate to obtain behavioral evidence.

## Reuse evidence and select a candidate

Declare the applicable suite once in a JSON file. Paths resolve relative to that file. Each value names a file or self-contained directory of immutable inputs.

```json
{"conditions":"session-inputs","cases":{"directory":"cases/directory","fallback":"cases/fallback"}}
```

Place provider settings, tool versions, harness and grader revisions, shared prompts and external dependency snapshots in the conditions input. Put each case's prompt, fixtures and rubric in its case input. Keep candidates, ledger, run outputs and conditions in separate locations. Supply only trusted regular files and directories. Freeze read-only inputs before launching the harness and use the same snapshots when recording its result.

```sh
python3 "$helper" status "$suite" "$work/runs.db" "$baseline" "$work/cut-local"
python3 "$helper" record "$suite" "$work/runs.db" "$work/cut-local" fallback fail "$run_dir"
```

Use one unique evidence path per independent execution, containing the grader result and supporting artifacts. Record a clear pass or failure after inspecting the evidence. Record an indirect or uncertain pass as `borderline`. Record unavailable capabilities as `blocked` with the diagnostic. Skip blocked cases until conditions change or fresh evidence shows the capability is available. The ledger rejects duplicate evidence paths and keeps earlier verdicts. Use fresh, immutable paths for later runs.

Run `status` again after each result. It hashes complete candidate trees, conditions and case inputs, then verifies retained evidence for matching identities. Reuse `passed` cases, run `pending` cases and give `repeat` cases an independent execution. Inspect changed or missing evidence and restore the original artifact before relying on its verdict. Any recorded failure rejects that candidate under those conditions, including mixed pass/fail results. Stop spending runs on a rejected candidate. The winner has the fewest body words among supplied candidates passing every declared case; input order breaks ties. A null winner leaves each outstanding decision visible under `cases`. The helper checks provenance and coverage. The maintained harness and reviewer establish behavioral verdicts.

For an existing grader that writes `grading.json` with boolean `expectations[].passed` and integer `summary.passed`, `failed` and `total`, import its verdict directly. The CLI verifies nonempty, consistent results and retains the run directory as evidence. For other grader schemas, map the documented verdict field to `pass` or `fail` with that harness's existing tooling.

```sh
python3 "$helper" record "$suite" "$work/runs.db" "$candidate" "$case" graded "$run_dir"
```

An unavailable provider yields a diagnostic instead of a grade. Record it once so future status checks can skip the run.

```sh
python3 "$helper" record "$suite" "$work/runs.db" "$candidate" "$case" blocked "$diagnostic"
```

A blocked case leaves the candidate ineligible. Changed conditions create a fresh pending case. If independent evidence shows that a transient outage ended under identical settings, retain that evidence with a fresh execution and record its result; the ledger preserves both observations.
