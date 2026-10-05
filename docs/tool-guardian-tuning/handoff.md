# Tool Guardian tuning handoff

## Goal and status

The original implementation is committed on `codex/tool-guardian-tuning` at `4bade608b9483944e69da0e424f10d113f011012`. Independent review on 2026-10-05 found four issues and milestone 6 reopened acceptance. Repair is in progress in `/private/tmp/tool-guardian-review-repair`, branch `codex/tool-guardian-review-repair`. Shared root currently contains plan, handoff and review-log updates only. Both original reviewers successfully resumed and completed preparation; actual re-review awaits frozen source. No push, real installation, or user-global configuration change occurred.

**Decision settled on 2026-10-05:** after a visual explanation, the user accepted strict fallback and its possible false alarms for harmless but unproved positional arguments. No additional positional-data proofs are required for this repair. Preserve all established proven data exemptions. The user subsequently authorized delegated implementation, repeated repair/re-review until every finding closes, and a work log from every subagent.

**Next step:** finish milestone 6 in the ExecPlan. The isolated repair agent owns canonical policy, generated outputs and regressions; root coordinates original-reviewer re-review, serialized integration, frozen performance validation and the final documentation pass. All subagents keep separate logs under `repair-logs/`; root's orchestration log records ownership, deadlines and the corrected worktree setup. Do not reopen the settled tradeoff. Real installation remains the user's later step, after repair validation and review.

## Review findings and proposed repairs

Review range: `git diff 9bcc6ff56cf916f848e4b32314ded35757d240c2...HEAD`. Standards reports two P1 findings; Spec reports two P1 and one P2. The shell-argument issue appears on both axes, giving four unique issues. Root independently reproduced each at all three public provider entrypoints, with disposable logs and no execution of represented operations.

- **R1, P1: pipeline intermediates bypass existing protection.** `hooks/families/tool_guard.py:1274-1282` records only adjacent downloader/interpreter pairs; `:1188` suppresses the original matcher using that map. Insert `cat`, `tee`, or `head` into the corpus download-execution operation: baseline denies, candidate silently allows. Proposal: restore the existing two bounded pipeline matchers on retained executable text, preserving proven data exemptions.
- **R2, P1: shell positional arguments escape inspection.** `hooks/families/tool_guard.py:1355-1358` proves the invocation from its body and omits remaining arguments. Public reproduction: `sh -c 'exec "$@"' _ <OPERATIONS['force_push_protected_branch']>`. Baseline denies in block mode and warns in warn mode; candidate silently allows. Proposal: inspect the body and retain strict scanning of unproved positional arguments, including producer input feeding an interpreter. An optional narrow positional-data proof requires explicit supported harmless forms and paired execution controls.
- **R3, P1: attached unresolved Python code is missed.** `hooks/families/tool_guard.py:1224-1227` returns before attached `-c` recognition at `:1235-1236`. Candidate denies `python3 -c "$BODY"` but permits `python3 -c"$BODY"` and `python3 "-c$BODY"`, including warn mode. Attached syntax was confirmed with a harmless local interpreter command. This is incomplete new fail-closed handling, not a baseline regression. Recognize the code option first and deny unresolved operands.
- **R4, P2: normalized aggregate accounting is wrong.** `hooks/families/tool_guard.py:759-766` validates normalized fragments separately but charges raw UTF-8 bytes. `sh -c` around a quoted `echo ` body with 700 U+FDFA characters allows in block and warn modes: raw aggregate 4,218 bytes, normalized aggregate 46,218. ASCII aggregate 34,018 correctly denies. Charge normalized length while retaining raw source provenance and existing nested-fragment accounting.

These findings align with ExecPlan requirements at `docs/tool-guardian-tuning/ExecPlan.md:109`, `:155`, `:224`, and `:226`, and `.agents/instructions/hooks.md:25`. Preserve every established native, search, writer, and survey data exemption. Unknown roles retain strict inspection rather than automatic denial; recognized unresolved execution and incomplete inspection deny even in warn mode. Blanket bans on shell arguments or Python would violate the repair constraint.

A possible Python builtin-alias issue was excluded: unsupported alias/value flows explicitly retain whole-source strict scanning, and general language interpretation is outside the agreed design. Do not inflate the four verified findings with that ambiguous inference gap.

## Discussion artifact

- `/Users/adam/.codex/visualizations/2026/10/01/01a0f977-1649-7383-9ffb-61ebb3f65d69/.lavish/tool-guardian-repairs.html` contains the four proposals, tradeoff controls, and the requested toy-robot explanation. Current local review URL: `http://127.0.0.1:4387/session/ebc9e0053ce165cc`.
- The user initially queued `strict-fallback` with "Explain this to me like I'm 5", explicitly discussion only. The page and `round1-reply.md` were updated; Lavish accepted the response with exit 0. A later show-me explanation used execution-versus-printing examples and a Mermaid diagram in chat; the user then accepted the strict-fallback tradeoff. This handoff records the latest decision; the Lavish page retains the earlier discussion state. No poll remains active. Resume polling only when further Lavish discussion is requested; never claim unattended monitoring. If the user ends the session, do not reopen it uninvited.
- Dark, light, and narrow previews rendered; local selection changes did not queue feedback. `repair-simple.png` records the delivered explanation. No repository source or tests changed during review or discussion; this checkpoint update is the only repository edit.

## Historical verification and pending validation

- Earlier source passes both 147-case warm pairs: maximum median deltas -1.841/-0.727 ms, p95 +1.618/+2.445 ms. Cold evidence retains 7,350 launches and three initial failures; all three exact 150-launch repeats pass. Resources: 90 cases, maximum 49.085958 ms, peak native macOS RSS 22,413,312 bytes. Four-worker comparisons retain 1,200 correct calls and improve each provider. Raw failures remain preserved.
- Guardian/generator suites passed on native macOS Python 3.14.6 and 3.13.14. Aggregate evidence is 39/41 before fixture repairs plus both repaired suites independently passing, not a fresh 41/41 run. Formal documentation/freshness checks passed; see the scoped records below.
- New review verifies all 39 current source hashes, four raw warm-report hashes, both warm gates, full cold/repeat counts and exact repeat set, raw summary arithmetic, and resources. No new timing probes ran. Passing historical suites did not catch these gaps. Repaired source needs public regressions, retained harmless controls, regeneration, relevant suites, and fresh frozen warm/cold/resource comparisons. Native Windows remains unverified.
- This Markdown-only checkpoint passes `git diff --check`; runtime suites were not rerun. Protected AGENTS sections remain unchanged.

## Evidence and replay

Historical runtime acceptance: `docs/tool-guardian-tuning/evidence/cold-profile-final-comparison.json`; raw reports and manifests remain alongside it. `cold-profile-notes.md` explains the sanitizer repair; `final-doc-notes.md` records documentation validation. `evidence/implementation-dispatch-audit.json` preserves earlier partial review timeouts and routing history; neither timed-out review was approval. The latest two-axis review used fresh independent Premium agents configured as `gpt-6.1-sol/high`, followed by root public reproductions. Runtime-reported execution configuration remains unconfirmed.

Immutable original baseline `/private/tmp/tool-guardian-baseline`; exact repaired snapshot `/private/tmp/tool-guardian-profile-candidate`; extracted checkpoint `/private/tmp/tool-guardian-profile-checkpoint`. Preserve these snapshots and retained source/payload/runner/corpus hashes. Optional optimization replay requires a disposable worktree at 84eae394; today's extracted entrypoints are not that inline ablation source. See `optimization-validation-notes.md`.

Historical zero-budget failures remain failures under their original criterion. The rejected literal-scan experiment showed no attributable full-hook gain; runtime changes were restored and its exact patch, failed reports and useful public characterizations remain at 15e323e5. Timed-out reviews supply partial findings, not security approval.

## Contract and durable findings

Per provider/case budgets: warm +2 ms median/+5 ms p95; cold fresh copy with zero provider bytecode +5/+10 ms; finite resource ceiling 500 ms. Preserve original failures when repeating isolated noise. Never raise budgets silently, pool cases, weaken inspection or skip logging.

Required contract: exact validated native schemas and proven shell/Python roles receive data treatment; unsupported forms retain strict inspection; unresolved inspection fails closed. The findings above expose incomplete implementation of that contract. Provider-local policy helpers remain generated identically and delivered with adapters; edit `hooks/families/tool_guard.py` and regenerate, never patch generated outputs directly. Ordinary bytecode only.

Native aggregate 65,536 bytes; unsupported/executable 32,768; structure depth 32/nodes 256/strings 128; executable depth 16/commands 128/tokens 256; Python syntax depth 32/tokens 1,024 and AST depth 32/nodes 2,048. Some later bounds are dominated. Raw JSON decoding precedes bounded traversal. Patch deletion/move checks protect source removals under existing policy, with no general destination or saved-script-inspection claim. Canonical current details are routed from `.agents/memory/API_MAP.md`.

Until the user installs, the old installed guardian can reject benign multiline patches above 128 segments. Split edits and construct dangerous fixture vocabulary dynamically; never disable the guard. Run generator mutable fixtures and installers serially; timing probes must run alone on frozen source. Source proof does not establish installed observability or provider-delivery timing.

Use `RTK_DB_PATH=/private/tmp/tool-guardian-rtk.db rtk ...` inside this sandbox. The default RTK database is unwritable. Git metadata outside the sandbox needs approved escalation. `/usr/bin/time -l` sandbox collection fails with `time: sysctl kern.clockrate: Operation not permitted`; approved native collection succeeds, with macOS RSS in bytes and wrapper cost excluded from latency. No automatic review rejection occurred.

Lavish/npm guidance calls failed under the sandbox with `ENOTCACHED` and an unwritable npm log directory; approved escalated `rtk proxy npx -y lavish-axi ...` succeeded. Do not repeat the failed offline route or install globally. A large HTML writer was blocked by the old installed guardian's 128-segment cap; smaller independent patches succeeded. Artifact code examples were constructed as data, not executed. Browser wheel scrolling had no effect and body `press` timed out; native labeled controls, DOM reads, and screenshots verified rendering. Do not use read-only browser evaluation for DOM mutation.

For authorized repair, use `exec-plans`, `tdd`, and security/performance validation guidance; run one formal `update-agent-docs` pass at the end of that source-edit session. For further visual discussion use `lavish`, its current CLI playbooks, and a tracked foreground poll with bounded harness waits.
