# Review 1: scheduler pilot harness

## Pinned scope and commands

Both independent review axes examined the integration diff from base `5db7440017e081b4d391c92f28d325b2fccf95a0` to target `10b9d80806604a15355b2dc343743118d52374ac`; merge base equals base. The exact diff SHA-256 was `538af6d89acbf7258f03443729c41ac2f286b026907038532b49f3694f4aedb4`. The captured review command record is [source.json](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/source.json).

```text
git diff 5db7440017e081b4d391c92f28d325b2fccf95a0...10b9d80806604a15355b2dc343743118d52374ac
git log 5db7440017e081b4d391c92f28d325b2fccf95a0..10b9d80806604a15355b2dc343743118d52374ac --oneline
rtk proxy python3 /var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/standards-probe/probe.py
rtk proxy python3 /var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/spec-repro.py
```

The pinned tree was clean. Reproductions used extracted pinned source and disposable fake-provider roots on macOS/Python 3.14.6; no model calls or source changes occurred. The full captured output is retained in [standards probe results](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/standards-probe/results.json) and [spec reproduction commands/results](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/spec-repro-commands.json). The review source files remain available as [standards.md](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/standards.md) and [spec.md](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-1/spec.md).

## Standards review

Documented-standard breaches:

1. **P1 - Inherited permissions/settings defeat frozen isolation.** `scheduler_pilot.py:329-334` inherits the complete environment; `:197-208` omits available config-isolation/temp controls. Copilot can inherit `COPILOT_ALLOW_ALL` or assisted approval despite narrow argv; user/global provider configuration is neither frozen nor rejected. Static finding corroborated by retained `T4-preflight/prerequisites.md`, items 2-5; no native model execution claimed. Violates `create-skill/references/provider-runs.md`, unsupported-harness requirement to preserve immutable inputs/provider-settings evidence and prohibit permission bypasses.

2. **P1 - Copilot write grant does not cover descendants.** `scheduler_pilot.py:204` grants `write(repo)` while output files are beneath `repo/outputs/`; installed permission help requires recursive `write(repo/**)` (retained preflight item 1). Native readiness remains unverified. Violates `repository-workflow.md`, “Keep README examples aligned with source” because `README.md` promises repo-scoped writes; `provider-runs.md` requires a harness suitable for permission needs.

3. **P1 - Timeout can leave running descendants.** `scheduler_pilot.py:289-301` returns when leader/pipes finish after TERM, without killing surviving group members. Disposable public CLI reproduction returned **124**, while a TERM-ignoring descendant with closed output pipes survived; explicitly killed after observation. `test_scheduler_pilot.py:162-172,224-240` lacks descendant assertions. Violates `scripts-and-installers.md`, cancellation cleanup, and `script-testing.md`, graceful/forced descendant termination after leader exit.

4. **P1 - Unexecuted code counts as execution evidence.** `scheduler_pilot.py:254-268` accepts a literal `subprocess.run(...,check=True)` inside `if False`; the wrapper exits **0** without invoking the scheduler. The focused pinned-function reproduction returned `accepted_as_execution=true`. Violates `create-skill/references/validation.md`, “do not invent missing ... tool activity.”

5. **P2 - Malformed grading artifacts crash.** `scheduler_pilot.py:417-424` accepts `{"assignments":[]}` then calls `.get`; public `grade` returned **1**, traceback, no JSON grade. Violates `scripts-and-installers.md`, predictable malformed-input handling, and `validation.md`, malformed artifacts must fail assertions.

Reproduction: macOS, Python 3.14.6; exact driver and full argv/exits/output are linked above. No provider calls. Baseline smells: none worth reporting.

## Spec review

Pinned target: `10b9d80806604a15355b2dc343743118d52374ac`. H = `skills/default/delegate-to-subagents/evals/scheduler_pilot.py`.

1. **P1 - Copilot cannot satisfy required rejection evidence** (H:231-235, 407-410). T2 requires “successful and denied execution” and retained native exit results. Copilot parsing converts every tool result into exit 0/1, while the required premature transfer must match exit 2. The existing good fake Copilot scenario therefore grades valid setup but failed output/behavior. Preserve actual child status rather than substituting tool success. Reproduction: public smoke/scenario exit 0; grade exit 0, `valid/fail/fail`.

2. **P1 - Dead wrapper code counts as execution** (H:258-268). T2 requires “exact immutable argv and exit results” for wrapped invocation evidence. Walking every AST node accepts `if False: subprocess.run([...], check=True)`; outer exit success proves no child execution. Replacing native command strings and corresponding evidence with these dead wrappers still produces grade exit 0 and behavior pass. This invalidates immutable-execution, independent-progress and acknowledgment assertions.

3. **P1 - Action labels are not tied to command semantics** (H:407-428). T2 requires scoring “stop timing, no second extension/reset” and exclusive ownership. Any matching command/exit pair validates an action; the grader never checks that its command performed that action, used its claimed time, or retained the state at that point. The pinned good fixture even uses invalid `tick A` commands and has no follow-up at 150, yet receives behavior pass. Negative fixtures merely remove selected labels, leaving this semantic gap untested.

4. **P2 - Evidence traversal escapes outputs** (H:401-416). The frozen scenario requires “repo-relative paths under outputs/”. Checking only the first component and confinement to the entire run root accepts `outputs/../../evidence/outside-outputs.json`. Public grading with this replacement exits 0 and still passes. Confine resolved evidence to this cell's outputs directory.

5. **P2 - Scenario starts before provider-wide smoke gate** (H:315-318). T5 requires “both variant smokes before its scored cells.” Public candidate scenario execution succeeds with baseline smoke absent; only the same cell's receipt is inspected.

Verification: `rtk proxy python3 review-1/spec-repro.py` exited 0 against extracted pinned source, using disposable fake-provider roots. Full public argv, exits and artifacts are in the linked reproduction results; no inference or source changes. Known permission-preflight gaps remain prerequisites, and pending T4/T5 are not completion defects.

## Consolidated fix mapping

These are distinct findings from the two independent axes; item R1.3 maps the duplicate dead-wrapper finding from both axes to one fix.

| Fix item | Finding mapping | Required correction |
|---|---|---|
| R1.1 Provider-control contract | Standards 1-2 plus T4 preflight findings | Correct recursive Copilot write grants and temp handling; bound or fail closed on inherited/global Copilot permission/config and trusted `.github` settings; account for Codex `--ignore-user-config`/`--ignore-rules`; document that Codex workspace-write is not a native command allowlist. Keep Copilot Sol/medium compatibility unresolved until valid evidence exists. |
| R1.2 Timeout cleanup | Standards 3 | On timeout, terminate and reap the process group, including descendants that survive leader exit or close inherited pipes; test graceful then forced cleanup and no surviving descendant. |
| R1.3 Execution proof | Standards 4 + Spec 2 | Reject dead/unreachable subprocess calls as execution evidence; tie wrapper acceptance to an actually executed child with immutable argv and captured exit result. |
| R1.4 Malformed grading | Standards 5 | Validate input artifact shape and emit a stable failed-grade result/diagnostic, never a traceback. |
| R1.5 Copilot exit fidelity | Spec 1 | Preserve child command exit code (including 2) through Copilot result parsing and retained native evidence. |
| R1.6 Action semantics | Spec 3 | Tie labels to executed command meaning, timestamp and resulting state; cover positive and negative transition semantics rather than label presence. |
| R1.7 Output confinement | Spec 4 | Resolve and confine evidence paths to the current cell's `outputs/` directory, rejecting traversal and symlink escapes. |
| R1.8 Provider-wide smoke gate | Spec 5 | Require both variant smoke receipts for a provider before any scored scenario for that provider. |

The separate full review texts above remain authoritative for severity, file/line locations, standard/spec rationale and repro details. The T4 preflight also records that selected Copilot model/effort compatibility is not established from local help and that no final immutable manifest was prepared. Do not convert these findings into permission redesign or live-call authorization.
