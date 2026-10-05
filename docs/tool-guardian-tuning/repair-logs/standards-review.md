# Standards repair review work log

## Scope and continuity

The original Standards reviewer is available for the repair review. This log belongs to that reviewer. Write ownership is limited to this file; the coordinator owns the execution plan, handoff, and final documentation pass, and the repair agent owns policy source, generated outputs, and tests. Other agents are working in the same checkout.

The original review covered the changes from `9bcc6ff56cf916f848e4b32314ded35757d240c2` to `4bade608b9483944e69da0e424f10d113f011012`. The repair review will inspect a candidate frozen and identified by the coordinator, verify the two original Standards findings, and check for related regressions. It will preserve the existing proven native, search, Python writer, and survey data exemptions. The user accepted strict inspection of unproved positional inputs and its possible harmless false alarms; this review will not reopen that tradeoff or require general shell interpretation.

## Original findings

Both findings violated `.agents/instructions/hooks.md:25`, which requires whole-input inspection, inspection of interpreter flags and nested sinks, and denial on incomplete inspection. The contract at `.agents/memory/API_MAP.md:58` also requires unresolved inspection to deny in block and warn modes. Source line numbers below identify the original reviewed revision.

- R2, P1: `hooks/families/tool_guard.py:1355-1358` treated successful inspection of an inline shell body as proof for the entire invocation and omitted its remaining arguments. All three public provider entrypoints allowed `sh -c '$1' sh '<protected operation>'`; a producer forwarding a positional value into a downstream shell was also allowed. The coordinator independently confirmed that an equivalent `exec "$@"` positional-argument case was denied by the original baseline. The protected operation was constructed from the maintained corpus, and only hooks were invoked. Remaining unproved arguments and producer inputs need strict inspection or an explicit supported proof.
- R3, P1: `hooks/families/tool_guard.py:1224-1227` returned before attached Python `-c` recognition at lines 1235-1236 when the option word was not literal. All three entrypoints denied `python3 -c "$GUARD_REVIEW_CODE"` but allowed `python3 -c"$GUARD_REVIEW_CODE"` and `python3 "-c$GUARD_REVIEW_CODE"`, in both block and warn modes. Harmless local Python execution confirmed that attached `-c` syntax is valid. This was incomplete new fail-closed handling rather than a baseline regression. The repair must recognize the code option and deny unresolved code.

An apparent Python builtin-alias inference gap was excluded from the original final report because the accepted design permits unsupported alias/value flows to retain strict scanning. It is not an additional required repair.

## Preparation on 2026-10-05

Recovered the original findings from this conversation, read the current feature handoff, and read milestone 6. Loaded the handoff and exec-plans skills and the repository memory index and architecture. Existing conventions and scoped hook, script, and repository guidance were already loaded during the original review.

Preparation commands used `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk proxy` from `/Users/adam/.codex/worktrees/e61c/skills`:

    cat /Users/adam/.agents/skills/handoff/SKILL.md
    cat .agents/memory/INDEX.md .agents/memory/ARCHITECTURE.md docs/tool-guardian-tuning/handoff.md
    rg -n -A 95 -B 12 'Milestone 6|milestone 6|## 6|repair' docs/tool-guardian-tuning/ExecPlan.md
    sed -n '194,206p' docs/tool-guardian-tuning/ExecPlan.md
    cat /Users/adam/.codex/worktrees/e61c/skills/.agents/skills/exec-plans/SKILL.md
    git status --short

Results: milestone 6 is in progress and acceptance is not met. The shared checkout contains coordinator documentation changes and repair-agent test changes. This reviewer has not inspected unfinished repair source, run repair tests, run timing probes, or changed installed hooks. No preparation command failed. The only reviewer edit is this log.

## Next step

Ready for the coordinator to provide the frozen candidate identity and review instructions. No repair finding is closed yet. Record each review round, exact verification commands, failures, and results here. Run no tests or timing probes until the coordinator confirms the source freeze and permitted verification window.
