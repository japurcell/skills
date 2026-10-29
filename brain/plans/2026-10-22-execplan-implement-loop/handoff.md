# Start here: owner-run Gemini qualification

Updated 2026-10-29. Feature-scoped handoff for a novice agent assisting the owner on a machine with Gemini CLI.

## First action

Read the [qualification guide](../../../skills/default/execplan-implement-loop/references/live-qualification.md), starting with **Record configuration before starting**. Fill that record in an owner-selected location outside all qualification roots. Report missing owner inputs before launching any provider command. The immediate goal is a complete configuration record, not another implementation task.

Repository at this checkpoint: `/Users/adam/.codex/worktrees/6b50/skills`. On another machine, locate its checkout and substitute that absolute repository path. The bundle is `skills/default/execplan-implement-loop/` beneath that checkout. Run qualification commands from the selected checkout; the guide uses absolute bundle and root paths so another working directory is also supported.

This handoff authorizes preparation guidance only. Live execution remains an owner action requiring explicit paid-use authorization. Do not infer authorization from this handoff, historical runs, or `--authorize-paid-run`. No Gemini command, including a local version probe, was run to prepare this handoff.

## Current state

- Implementation tasks T1-T44 and documentation task T45 are complete locally. The [ExecPlan](ExecPlan.md) contains the contract, historical findings, and evidence; it is not a runner-compatible input. Use the helper's bundled disposable fixture for qualification.
- Last committed checkpoint: `9289f9054bcc7fc29e353b06fc8a8175e37c7309`. The updated guide, `evals/evals.json`, and ExecPlan are uncommitted at this handoff's creation. Preserve these changes. A checkout of the commit alone lacks the newest guide. Transfer the current bundle and guide together, then record the new setup digest.
- Current repaired bundle still needs live qualification. Historical successful runs establish functional results for older source only. A later session audit found worker boundary/scope problems, which motivated the completed local repairs.
- Three implementation review cycles are exhausted. Cycle 3 found two issues; fixes passed tests but were not independently rereviewed. Do not launch a fourth code-review cycle or reopen implementation from historical task instructions.

## Inputs to settle with the owner

- Selected absolute bundle path, Python 3.12+ executable, Git, and absolute Gemini CLI 0.65.0 executable path. Newer Gemini versions are untested; do not change global installations automatically.
- Real `exec-plans` and `tdd` skill source directories, or confirmed discovery. Use setup's source options to copy missing skills before the baseline commit.
- Three distinct fresh roots with existing parents, plus an external operator report location. Keep all operator notes outside the entire helper roots.
- Authentication through the owner's normal process; account-specific Cloud project requirements and launching-process variable presence only. Never record values or credentials.
- Model selection or inherited/default selection, owner-reviewed functional and denial policy files, and authorization scope for each run/resume. Explicit policy supplements inherited policy.
- Exact disposable operation/target for C's denial test. The owner reviews the narrow policy; do not invent policy syntax, broaden grants, or test against private data.

## Execute the guide in this order

1. Complete the configuration record. Resolve literal paths; examples are placeholders. Preserve one bundle snapshot across A/B/C.
2. Set up A's new disposable project with `qualify.py setup`. Review its JSON, physical root, manifest, bundle digest, and baseline. Setup makes no Gemini call. Copy skills through setup options only.
3. Have the owner review trust for that exact `project/` folder through the ordinary interactive flow. Trust changes and paid calls require their own owner decisions. Doctor cannot prove trust or authentication.
4. Use the guide's doctor command with the selected absolute `--gemini`. Exit 0 means no known local blocker, not readiness or authorization. Resolve exit 3 blockers through authorized paths; exit 2 means invalid inputs.
5. After explicit owner authorization, use `qualify.py run` in one foreground session. Wait on that same session. Helper limits are 600 seconds total and 300 seconds per iteration. Scheduling, verification, and commits belong to the runner; do not execute tasks or commit worker changes yourself.
6. Collect A's evidence and audit its Gemini sessions using the guide's checklist. Then repeat with separate new roots for B (reviewed explicit policy) and C (reviewed narrow denial policy). Pass the same selected executable and policy to each scenario's doctor/run commands.
7. Complete the guide's report template outside every root. Link the numbered collections and normal Gemini session identifiers. Update the plan with measured outcomes and remaining blockers, preserving prior evidence.

The guide contains runnable setup/doctor/run/collect templates, resume instructions, required artifacts, and outcome definitions. Use actual reported run directories instead of guessing attempt numbers. Do not run its examples as an unattended batch.

## Completion and stopping rules

- A/B need all three fixture tasks and one milestone accepted, passing verification, matching runner commits, and clean Git. Behavioral acceptance separately needs session evidence of skill activation, red-before-source TDD, task scope, and runner-owned Git mutations after verification.
- B also needs reviewed policy path/hash matched to recorded selection. Selection does not prove inherited policy was disabled.
- C passes only after an actual required-operation tool denial, worker `blocked`, no bypass, and no completion commit for that blocked task. Pruned/unavailable tools or an unsupported denial claim are inconclusive. Partial test files may remain.
- Missing session audit or required evidence means incomplete qualification. Functional exit 0 alone is insufficient. Report unknown usage/cost as unknown. Do not copy raw transcripts or secrets into the report.
- Preserve failures and partial work. Resume only the reported run after review and fresh owner authorization. `qualification_attempt_incomplete`, `cleanup_unconfirmed`, or `unclean_execution_requires_reconciliation` requires owner-directed reconciliation; do not blindly acknowledge, clear locks, reset files, or launch overlapping replacements.
- Stop on actual access denial. Preserve its evidence rather than retrying through another tool, shell, alias, or unrelated source search. Do not change global trust/policy, edit manifests, or add undeclared helper-root files.

## Verified evidence and limits

- [T44 source proof](t44-source-hashes.md): runner 102/102 and helper 33/33 passed on recorded implementation source. These are local fake-provider results, not new live evidence.
- T45: packaging passed 5/5 in 9.654 seconds; helper command flags, guide anchors, eval JSON, skill validation, punctuation and whitespace checks passed. One planning-only novice comparison passed new guide 6/6 assertions versus old guide 4/6. Runtime files were unchanged.
- T45 evaluation artifacts are local-only at `/private/tmp/execplan-guide-eval-20261029/`; they may not exist on the next machine and are not prerequisites. Token/time usage is unknown. The guide and repository evidence remain the portable starting point.
- Historical live reports and reviews beside this handoff are background evidence. They do not authorize new calls or qualify the current bundle.
