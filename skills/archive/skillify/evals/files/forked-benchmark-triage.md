# Confirmed Session Summary: benchmark-triage

## What Happened

- The user wanted to capture a repeatable workflow for triaging benchmark results after a skill evaluation run.
- The source session reviewed `benchmark.json`, grouped failing expectations, inspected a few outlier evals, and produced a short triage report with suggested next edits.
- The work was self-contained and did not require the user to answer questions once the benchmark path was known.

## Confirmed Answers

- Confirmed skill name: `benchmark-triage`
- Confirmed save location: `.agents/skills/benchmark-triage/SKILL.md`
- Confirmed invocation style: `/benchmark-triage $benchmark_path`
- Confirmed arguments:
  - `$benchmark_path`: path to the benchmark.json or iteration directory to inspect
- Confirmed context choice: `fork`, because the workflow should run as a self-contained subagent

## Inputs And Success Criteria

- Inputs: benchmark results plus any nearby eval directories
- Success artifact: a triage report that clusters failures, calls out flaky assertions, and proposes concrete next edits
- Hard success criteria:
  - The skill is self-contained and forked
  - It preserves the per-eval deep-dive pattern from the source session
  - It records the benchmark-analysis tool mix accurately
  - The final output tells the user where the skill belongs and how to invoke it

## Observed Workflow Steps

1. Read the benchmark summary and identify the weakest assertions and highest-variance evals.
2. Split per-eval deep dives into parallel reviews where helpful.
3. Inspect representative failing outputs or transcripts.
4. Synthesize repeated failure patterns and likely root causes.
5. Produce a short triage report with the next skill edits to try.

## User Corrections And Preferences

- The user explicitly wanted this workflow to fork rather than interrupt the current conversation.
- The user preferred using a task agent for per-eval deep dives instead of handling each one serially in the parent agent.
- The user wanted benchmark tooling captured narrowly, including local Python helpers when needed.

## Tools And Agents Used

- `Read`
- `Grep`
- `Glob`
- `Edit`
- `Write`
- `Bash(python:*)`
- Task agent for per-eval deep dives
