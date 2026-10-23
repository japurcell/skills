---
name: execplan-implement-loop
description: Run an authorized ExecPlan to verified, committed completion through a bounded Gemini CLI loop.
disable-model-invocation: true
argument-hint: "<execplan-path> [runner options]"
---

Run the bundled deterministic runner once, then explain its report. The runner owns task selection, retries, verification, plan updates, commits, and statistics. Gemini implements one assigned task per fresh session.

1. Activate the `exec-plans` skill. Resolve the supplied plan path and the installed directory containing this SKILL.md. Honor the user's authorization and repository instructions. Read [plan format](references/plan-format.md) when checking or authoring an input plan. Existing prose plans need explicit conversion to the supported format before execution; preserve requirements and declared verification policy.
2. Validate without model calls:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md --validate-only

   Stop on invalid input and report the diagnostic. Do not invent missing commands, silently convert scope, or weaken acceptance.
3. Launch once, passing the user's runner options:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md

   Defaults are 3,600 seconds total and 1,200 seconds per Gemini iteration. The runner requires Python 3.12+, macOS/Linux, Git, Gemini CLI 0.65.0, and Gemini-visible `exec-plans` and `tdd` skills. New execution requires a clean Git worktree. Keep exclusive worktree ownership while it runs. Inherit Gemini approval policy and configured model unless the user supplies explicit options. Never silently enable yolo. If the hosting tool returns a running session, keep waiting on that session rather than launching another runner.
4. Read the final stdout JSON and process exit code. Read [protocol](references/protocol.md) for field meanings, errors, progress events, limits, and exit codes. Report status and reason, tasks/milestones completed, commit SHAs, unfinished task/phase, elapsed time, retries/timeouts, verification failures, available usage, and evidence/run-directory paths. Distinguish invocation statistics from cumulative history. Missing usage is unknown. Never claim completion from progress events or plan checkboxes alone.
5. For a recognized interrupted run, resume only when authorized, using the same plan:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md --resume /absolute/run-directory

   Resume grants a fresh invocation budget and preserves history. A commit failure resumes its transaction without rerunning Gemini implementation. For `unclean_execution_requires_reconciliation`, stop the recorded child tree and inspect the task delta, HEAD, index, and plan before an operator explicitly supplies `--acknowledge-unclean-stop`. This flag asserts reconciliation; it does not prove it or bypass contract/Git checks. Preserve work on blockers. Never reset, stash, discard, or push automatically.

The runner sends Gemini the bundled [worker prompt](references/worker-prompt.md) and [commit-message rules](references/message.md). Read those only when diagnosing worker behavior or reviewing a proposed message. Gemini must activate `tdd` for source changes, return typed results, and propose a message. The runner commits only after declared checks pass. Copilot attribution is explicitly declined for these worker commits.

For owner-run provider qualification on another machine, use the [live qualification guide](references/live-qualification.md). Keep live acceptance pending until its evidence is reviewed.
