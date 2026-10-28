---
name: execplan-implement-loop
description: Run an authorized ExecPlan to verified, committed completion through a bounded Gemini CLI loop.
disable-model-invocation: true
argument-hint: "<execplan-path> [runner options]"
---

Run the bundled deterministic runner once, then explain its report. The runner owns task selection, retries, verification, plan updates, commits, and statistics. Gemini implements one assigned task per fresh session.

1. Activate the `exec-plans` skill. Resolve the supplied plan path and the installed directory containing this SKILL.md. Honor the user's authorization and repository instructions. Read [plan format](references/plan-format.md) when checking or authoring an input plan. Existing prose plans need explicit conversion to the supported format before execution; preserve requirements and declared verification policy.
2. Validate the static contract without model calls:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md --validate-only

   Stop on invalid input and report the diagnostic. Do not invent missing commands, silently convert scope, or weaken acceptance.
3. Before a provider attempt, diagnose local readiness with the same plan and any selected provider options:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md --doctor

   `--doctor` makes bounded local checks, including `gemini --version`, but sends no prompt, activates no skills, runs no acceptance commands, creates no run directory or lock, and changes no Git or configuration files. It returns one JSON object with `status: "diagnosed"`, `readiness`, and `blockers`. `readiness.status` is `blocked` or `unknown`, never `ready`. Exit 0 and `can_attempt: true` mean only that diagnosis found no known local blocker. Authentication, project trust, effective permission, and permission to make a paid request remain unknown. A readable policy or skill file does not prove those conditions. Stop on a known blocker or invalid input. For an explicitly reviewed policy, pass the same `--policy /absolute/reviewed-policy.toml` to doctor and execution. Each new provider iteration, including a resume that needs another provider iteration, rechecks readiness. Doctor is a snapshot, not authorization.
4. Launch once, passing the user's runner options:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md

   Defaults are 3,600 seconds total and 1,200 seconds per Gemini iteration. The runner requires Python 3.12+, macOS/Linux, Git, Gemini CLI 0.65.0, and Gemini-visible `exec-plans` and `tdd` skills. New execution requires a clean Git worktree. Keep exclusive worktree ownership while it runs. Inherit Gemini approval policy and configured model unless the user supplies explicit options. An explicit `--policy PATH` must name one already-reviewed regular UTF-8 TOML file of at most 1 MiB. The runner records its physical path and exact-byte hash, passes it to Gemini, and checks it again before each spawn. A changed file blocks until the caller reviews and explicitly selects the intended bytes. `--policy` adds an input; it does not erase inherited user policy. The historical qualification used `~/.gemini/policies/qualification.toml`; if present, ask its owner to review it through their normal configuration process. The runner never edits or deletes global policy. Do not write global policy, add broad grants, or silently enable yolo. If the hosting tool returns a running session, keep waiting on that same session rather than launching another runner.
5. Read the final stdout JSON and process exit code. Read [protocol](references/protocol.md) for field meanings, errors, progress events, limits, readiness, blockers, usage, and exit codes. Report status and reason, tasks/milestones completed, commit SHAs, unfinished task/phase, elapsed time, retries/timeouts, verification failures, available usage, blockers, and evidence/run-directory paths. Distinguish invocation statistics from cumulative history. Missing usage is unknown. Never claim completion from progress events or plan checkboxes alone.
6. For a recognized interrupted run, resume only when authorized, using the same plan:

       python3 /installed/execplan-implement-loop/scripts/run.py /absolute/ExecPlan.md --resume /absolute/run-directory

   Resume grants a fresh invocation budget and preserves history. A commit failure resumes its transaction without rerunning Gemini implementation. For `unclean_execution_requires_reconciliation`, confirm the recorded child tree has stopped and inspect the task delta, HEAD, index, and plan before an operator explicitly supplies `--acknowledge-unclean-stop`. This flag asserts reconciliation; it does not prove it or bypass contract/Git checks. For `cleanup_unconfirmed`, do not start a replacement process while child cleanup is uncertain. Confirm owned children have stopped and inspect the saved worktree, state, and lock ownership before any recovery. Never acknowledge blindly or delete a lock as a shortcut. Preserve work on blockers. Never reset, stash, discard, or push automatically.

The runner sends Gemini the bundled [worker prompt](references/worker-prompt.md) and [commit-message rules](references/message.md). Read those only when diagnosing worker behavior or reviewing a proposed message. Gemini must activate `tdd` for source changes, return typed results, and propose a message. The runner commits only after declared checks pass. Copilot attribution is explicitly declined for these worker commits.

Tool-specific inability to read or write a path does not grant authority to use another path. Use an alternate I/O method only for the same already-authorized paths; user, sandbox, policy, filesystem, and path restrictions remain blockers.

For owner-run qualification, follow the [live qualification guide](references/live-qualification.md). Its bundled helper prepares and collects evidence locally and runs in the foreground. The `run` command requires both `--authorize-paid-run` and actual user authorization; it runs doctor before the provider. Keep the same long-session tool active and wait on that session. The original adapter qualification on 2026-10-27 is historical evidence only. It does not establish current-machine readiness or qualify the new follow-up behavior; do not claim new live proof until fresh evidence is reviewed.
