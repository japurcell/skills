# Review Execution and Handoff

Status: static investigation complete for five skills and 290 individual check rows; parent source reconciliation complete; human dispositions pending. Source baseline: `8d563fae209c5b3583eacb7e7f4056783279aff0`. This is source inspection, not execution or native conformance evidence.

Scope: `skills/prd-ralph/`, `skills/prd-ralph-loop/`, `skills/execplan-implement/`, `skills/commit/`, `skills/handoff/`. Excludes generated outputs, archive, sibling workspaces and snapshots. Fixtures are evidence inputs, never primary entry points.

The source reviewer owned only this report and released ownership after structural verification. The parent now owns report reconciliation, shared coverage, findings, decision tickets, handoff and canonical knowledge. The source review did not run audited graders, validators, clients, installers, importers, git mutations or procedure implementation. Parent documentation commits are separate from audited procedure execution.

## Inventory checkpoint

Recursive enumeration includes dot directories: five primary skills, 22 primary maintained files and 20 fixture files. All 42 existing files were read in full and matched byte-for-byte against the baseline with read-only `git show`; missing declared files are separately recorded below. SHA256 identifies unchanged source inputs, not a behavioral run snapshot.

## Remaining work

Live Grilling dispositions and any precise separate behavior decisions remain pending. No native case, audited grader/validator, packaging, installer, imported refresh, audited git workflow or skill edit ran. Parent canonical-document lint and the documentation commit are separate from target procedure execution. The seven-model medium-effort matrix, three fresh repetitions, native discovery/activation traces, permission isolation, workflow and output grading remain later evidence work under `tickets/set-audit-evidence-and-model-coverage.md:28-72`. No baseline case is selected here.

## Primary maintained files

| File | SHA256 | Lines | Baseline identical | Shipment |
| --- | --- | --- | --- | --- |
| `skills/prd-ralph/SKILL.md` | `f78491b499431fa951db0573d073efb654655471641166cce40776d8d38ce703` | 187 | Yes | Shipped by both selection routines |
| `skills/prd-ralph/references/browser-verification.md` | `8ceee140db517f9f54a6eb557170970c3cdfd240ac9a60fb118dbf3f401d2ca4` | 50 | Yes | Shipped by both selection routines |
| `skills/prd-ralph/references/commit.md` | `baaecb3a0f76d7b1b510ce1bdee54b4428fae78de5a8b3a82f065ccc469d2452` | 100 | Yes | Shipped by both selection routines |
| `skills/prd-ralph/references/failures.md` | `f501ac5503893c8520456da61503eea2080179e8952f87f9ac0e8eec59b9d69b` | 34 | Yes | Shipped by both selection routines |
| `skills/prd-ralph/references/progress.md` | `38b92c3793cbe470d6849c716b57d72ac0285af8cb5fb2cb3d9fc40a7e8f71e1` | 57 | Yes | Shipped by both selection routines |
| `skills/prd-ralph/references/verification.md` | `bc511423e242cf72d9c603485a54de3c002e0b92de3a84ce2066a11c9efdd23e` | 49 | Yes | Shipped by both selection routines |
| `skills/prd-ralph-loop/SKILL.md` | `2cbc991e5bd29e88b6d7174565556fce75c9f4bf1f88194ebdeff6e06c356910` | 40 | Yes | Shipped by both selection routines |
| `skills/prd-ralph-loop/evals/evals.json` | `1b3dd9838a61b19e71597878e5f8dd5cadbc8861a121b681c0e366c5f27841d2` | 44 | Yes | Pruned: evals/ |
| `skills/prd-ralph-loop/evals/grade_benchmark.py` | `824255146aa4e4851c883d6bb5ff5b860842b8a2b4111db970ac7d5a959b8168` | 160 | Yes | Pruned: evals/ |
| `skills/execplan-implement/SKILL.md` | `7a9050934b9ca639eaffc909ccf8bb07ccf401f255eeb40ff117686f991cf5e5` | 80 | Yes | Shipped by both selection routines |
| `skills/execplan-implement/agents/openai.yaml` | `9dcd9cd61b27f948d63c38512dab8b18148f549d102778cf275a4c4af9cc3018` | 5 | Yes | Shipped by both selection routines |
| `skills/execplan-implement/references/message.md` | `205ca83a018bfe530ad559b322fd307e24108a6b1dd3b580e9e49a39a355bd1d` | 77 | Yes | Shipped by both selection routines |
| `skills/commit/SKILL.md` | `3cb7a9d103d180a9648ecbdbce5fabb84f0626885aa9e900bb86026cc9349218` | 104 | Yes | Shipped by both selection routines |
| `skills/commit/evals/evals.json` | `1216b2cd896b4319f50094d402b2dfc3984d4aea5d2ac01e82001ddad6920ac0` | 63 | Yes | Pruned: evals/ |
| `skills/commit/evals/grade_benchmark.py` | `a04964cf0fc565ebc5bef7cc2f10f2b6a0d4e5f7829c914429ef815d5e321aa1` | 292 | Yes | Pruned: evals/ |
| `skills/commit/references/branch-names.md` | `f37502ff861e41afe8fa41265c8d2dae164f9e5c3634734344870b6e183f9261` | 33 | Yes | Shipped by both selection routines |
| `skills/commit/references/dry-run.md` | `46655b186502fa5f17b277c7d320f35456dd28c9acc5eff7f883a45afa44d75d` | 22 | Yes | Shipped by both selection routines |
| `skills/commit/references/message.md` | `205ca83a018bfe530ad559b322fd307e24108a6b1dd3b580e9e49a39a355bd1d` | 77 | Yes | Shipped by both selection routines |
| `skills/commit/references/pr.md` | `904101580f5eb40c468e1ccfa2ac330cdb874aa354bd9eaec3846426ca52219d` | 35 | Yes | Shipped by both selection routines |
| `skills/handoff/SKILL.md` | `4dd3058fc31ce425d48a7a3ae92160804d79cdfb4199f69eb7cdcf13cd9e7be5` | 97 | Yes | Shipped by both selection routines |
| `skills/handoff/evals/evals.json` | `ec0fb25931efde364bb07715c081b611d80fde5d2daa210daa5b4bfcc965dd8f` | 83 | Yes | Pruned: evals/ |
| `skills/handoff/evals/grade_benchmark.py` | `1891eb9766698b34244546f9af1f8b81c143a9790c542d08fb3b86cd84eaceec` | 277 | Yes | Pruned: evals/ |

## Fixture files

| File | SHA256 | Lines | Baseline identical | Shipment |
| --- | --- | --- | --- | --- |
| `skills/prd-ralph-loop/evals/files/complete/prd.json` | `2dacc80f111d3840f31a6659316d516945715fbaa8abef2ae25fe51258e4c5d2` | 18 | Yes | Pruned: evals/ |
| `skills/prd-ralph-loop/evals/files/incomplete/prd.json` | `bdb43f2a904ac8c70d8e710e7daeac5286d2717c61a67365947ee05494c509ba` | 18 | Yes | Pruned: evals/ |
| `skills/prd-ralph-loop/evals/files/invalid/prd.json` | `1054b0b91536bedd7374765261d516af72e7871f7e0e41b6fd2878ad6af293d3` | 3 | Yes | Pruned: evals/ |
| `skills/commit/evals/files/ambiguous-multi-surface/input.json` | `acb868dea1dca108d283b6159040b0e52d4291e1edbaf12726b9b3e8d70d2a02` | 29 | Yes | Pruned: evals/ |
| `skills/commit/evals/files/generated-artifact-stop/input.json` | `89137e447a29489ea0f42f218451443b1cfe3af00b6657d93a396f875f169ae0` | 30 | Yes | Pruned: evals/ |
| `skills/commit/evals/files/single-file-on-main/input.json` | `781e6a52cf72963f8d40ba798b96850eca167bb0f97255b673acaf4c5c2cec06` | 32 | Yes | Pruned: evals/ |
| `skills/commit/evals/files/staged-bugfix-pr/input.json` | `6781f5a9fad83571ac1db8ecb14fdc04b5e386daa4fed19a15b070ac44c8aed9` | 33 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/fallback-noise-fixture/diffs/patch.diff` | `a665c96ea6b24d4cd507fab0896d347a33cd4ee0acce684dec228a772c93c434` | 4 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/fallback-noise-fixture/session_notes.md` | `0555c7f9686a68f72e3e1c3802b5b9296f321cfb07b11b6ae04ef51cc5a6024d` | 17 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/fallback-noise-fixture/src/sync_retry.py` | `b179e5d4d8bd454536d1d43650cafd7c4fa2cef462fcf2057341311a0dbe301e` | 2 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/fallback-noise-fixture/tests/test_sync_retry.py` | `8170f0a3f096b1af511ffe42d3ce240516e540d4020dd559ff4d76766382349d` | 5 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/feature-update-fixture/.agents/scratchpad/payments/handoff.md` | `3f03e3fd6729695bd141fe08ef5129ba5552556c90d9ec2684a2637bd1e1ea20` | 10 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/feature-update-fixture/reports/benchmark.txt` | `373e8fa865bc350920e5e5df441c8ee2513dfd9490408cb7eaffd550d635d13b` | 3 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/feature-update-fixture/session_notes.md` | `a52a8317b75628b9d58c2cad2d83ec9f7e160b8c876ec8d66586f533b44bd477` | 17 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/feature-update-fixture/src/payment_retry.py` | `062cfe77548b2a1c798dc9e8300b697559fcfb2440cb0e9305299441afb9e645` | 2 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/feature-update-fixture/tests/test_payment_retry.py` | `0eab07befc00ab3c8e6cfc4180a4f8f158f5a275ac7cb49f5677a3c3624df587` | 5 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/root-create-fixture/plans/refresh-plan.md` | `5e0aaefc31884fc1b913d5edde3da3d3c9d1845410cc9c10585136fdc8b85a97` | 4 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/root-create-fixture/session_notes.md` | `26b2681a43a41e156d1f187311ba64685d7a85ae2d8dc153e161062695274351` | 19 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/root-create-fixture/src/auth_refresh.py` | `c725d2f1e090b8f63013c33386fa269e7b381c2eda59c071e1c7474f5a12ff55` | 2 | Yes | Pruned: evals/ |
| `skills/handoff/evals/files/root-create-fixture/tests/test_auth_refresh.py` | `3ee5029f5c121b2f4cfe4a484c4cd25eb0bdffb98ab4272b246de3aba0181f14` | 5 | Yes | Pruned: evals/ |



## Protected contracts and per-skill source summaries

| Skill | Purpose, identity and triggers | Preserved controls, boundaries and output |
| --- | --- | --- |
| prd-ralph | Name/directory `prd-ralph`; complete at most one eligible task (`skills/prd-ralph/SKILL.md:2-8`). Required `prd_file`, optional task/progress/commit inputs (:10-16). | No interview and no invented requirements (:20-22); mandatory TDD (:89); eligibility/priority/dependencies (:67-85); exact verification plus conditional browser (:105-111); progress and all failures/commits (:160-171); at most one scoped commit, no PRD/progress/unrelated/failing commit (:24-32,133-158); exact COMPLETE only when all tasks pass and commit gate holds (:173-177). |
| prd-ralph-loop | Name/directory `prd-ralph-loop`; explicit invocation for all PRD tasks rather than one (:2-4). Ask for missing PRD path (:11). | Retain `disable-model-invocation: true`; baseline git state or stop (:15-18); required Delegate (:19); sequential fresh Ralph workers (:20-22); parent must not implement or read PRD to select tasks (:34-40); three consecutive failure stop (:34); only after loop read progress and invoke Self Improve (:28-30); report full committed/staged/unstaged/relevant-untracked scope (:23-30). |
| execplan-implement | Name/directory `execplan-implement`; implement supplied ExecPlan into commits on one branch (:2-9). | Both invocation controls (`SKILL.md:4`, `agents/openai.yaml:4-5`); mandatory ExecPlans/Delegate (:19); task graph/frontier and fresh-per-node workers (:13-15,27-35); TDD and isolated private worktrees (:32-35); message reference before every primary/worker commit (:11,34); serial rebase/clean/ff-only/tip integration (:37-46); paused repair and living plan (:27,40-41,48); remove only clean integrated worker branches/worktrees, preserve base/unrelated (:44); human-review-ready branch after completion (:50). |
| commit | Name/directory `commit`; current-worktree commit/save/stage/push/PR triggers (:2-3,10-17). | Exactly one commit, conditional push/PR (:8,64-75); state inspection before mutation (:23-36); blocker stops (:38-46); staged-only then one-file/one-directory auto-stage, otherwise ask (:53-60); generated/local/sensitive state exclusion unless explicit request (:59-60); branch rules (:48-51); required message and trailers (`references/message.md:17-21,66-77`); dry-run/PR references (:72-75); branch/SHA/subject/URL or blocker final (:77-82). |
| handoff | Name/directory `handoff`; literal handoff/path/read/summary/check/update and resume/continue/pick-up/next-step/checkpoint/transfer triggers (`SKILL.md:2-3`). | Load before tools and update when state changes/before stopping (:3); active context and exact verification (:14-19); named path precedence, then single matching feature scratchpad folder, then root, invalid/ambiguous fallback explained (:21-26); existing-file update, close inherited next step, reread patch section (:28-32); review corrections/errors/lessons/anchors (:33-38,48-56); redact and inline write-failure fallback (:38-39); final written path, root/feature scope and one next step (:41-44). |

Metadata parses as mappings with string names/descriptions, directory-matching lowercase hyphenated names under 64 characters. Description lengths are respectively 116,116,30,164,389 characters at each `SKILL.md:2-3`. Entries contain 187,40,80,104,97 total lines respectively. No length threshold alone is a finding. Ralph's five directly named references are 50,100,34,57,49 lines and are conditional at :36-42. Commit's four references are 33,22,77,35 lines, selected at :51,62,74-75. Execplan has one 77-line message reference directly linked at :11,34. Loop and Handoff keep their essential controls in small entries. No automatic seven-heading anatomy is required by this report.

Ralph has no bundled eval; Execplan has no bundled eval. Those are evidence gaps, not automatic defects. Loop has three paper dry-run cases; Commit four paper cases explicitly prohibit git mutation; Handoff three fixture-copy artifact cases. All three eval JSON documents parse; all three graders and six Python fixture files parse as Python AST in memory. No import or call to any audited grader/validator occurred. All 42 files have LF bytes and no trailing/blank-line whitespace or indentation tabs under `.editorconfig:6-19` and `.agents/memory/CONVENTIONS.md:29-32`.

## Bounded consumer and shipping checks

| Consumer / dependency | Exact source | Static result and remaining limit |
| --- | --- | --- |
| Ralph -> TDD | `skills/prd-ralph/SKILL.md:20,89-102`; `skills/tdd/SKILL.md:3,20-26,34-38` | Required imported helper exists. Ralph explicitly loads it; Execplan explicitly tells each worker to load it (:32). Only required consumer ordering/seam/refactor controls were inspected, not imported helper quality. Unconfirmed seams expose EH-006; no execution was activated. |
| Spec -> Ralph | `skills/spec-to-tasks/references/task-schema.md:10-32,47-56`; `skills/prd-ralph/SKILL.md:67-95` | Current tasks/description/acceptance/pass/priority fields align; absent dependsOn is accepted. Ralph does not require a particular task ID prefix, so Loop fixture US IDs alone are not a defect. Missing description/criteria in the incomplete fixture are consequential only if used as executable Ralph input. RPT-001 owns obsolete Spec oracle repair; this batch does not change task output. |
| Loop -> Ralph | `skills/prd-ralph-loop/SKILL.md:20-22,34-40`; `skills/prd-ralph/SKILL.md:8,65-85,173-187` | Fresh sequential worker chooses at most one task. Worker completion signal ends loop; other worker reports are brief completed/blocked/verification/commit evidence. Parent stays blind. The `commit` input flag in Ralph is not a call to Commit; Ralph has its own stricter commit reference. |
| Loop / Execplan -> Delegate | `skills/prd-ralph-loop/SKILL.md:19-22,34`; `skills/execplan-implement/SKILL.md:19,29-35`; `skills/delegate-to-subagents/SKILL.md:38-55,63-96,158-177,237-248` | Exact route, ownership, verification and enforced runtime prerequisites apply transitively. The short caller brief must be enriched by required Delegate workflow, not interpreted as a waiver. Default no nested delegation applies. New task nodes and replacements are distinct; EH-005 below preserves both retry limits. Native route/dispatch capability is unverified. |
| Loop -> Self Improve | `skills/prd-ralph-loop/SKILL.md:28-30,39`; `skills/self-improve/SKILL.md:8-10,19-40` | Delayed progress read supplies durable learnings/workarounds to helper; helper can legitimately make no change. This does not authorize early progress reads. Source does not specify whether failure stop skips or performs post-loop maintenance; recorded as a coverage gap, not invented approval. Prior SAG/RLW owners retain document-maintenance facts. |
| Execplan -> ExecPlans | `skills/execplan-implement/SKILL.md:7,19,27,40-41,48-50`; `.agents/skills/exec-plans/SKILL.md:11-17,56-76` | Mandatory helper exists only under repository-local source, not published `skills/exec-plans/`; living sections, synchronization and validation apply. EH-008 records supply uncertainty. No plan or implementation was created by reading this helper. |
| Execplan -> message / integration | `skills/execplan-implement/SKILL.md:11,34,37-46`; `references/message.md:5-21,66-77` | Local message resource resolves and ships; it has the same bytes as Commit's message reference. Do not replace the multi-commit workflow with Commit's exactly-one workflow. Repair/rebase tests and final tested-tip wording expose EH-007. |
| Handoff -> repo path override | `skills/handoff/SKILL.md:21-26,31-39`; `.agents/instructions/repo.md:10-14` | User named path precedes feature-scratchpad/root defaults. Active research records live under docs/effort; explicitly promoted feature handoff stays there. `docs/handoff.md` is not invalid merely because it is outside scratchpad. Existing hidden fixture path was enumerated and read. |
| Installer -> five bundles | `scripts/install.sh:40-55`; `scripts/install.ps1:251-276` | All 16 non-eval primary entries/references/sidecar ship by selection source. Six eval resources and all 20 existing fixtures are pruned. No runtime entry requires pruned eval content. Top-level README/licenses and workspace/archive exclusions remain. Installed paths and access were not tested; no installer ran. |
| Graders -> artifacts / source identity | `prd-ralph-loop/evals/grade_benchmark.py:41-44,119-153`; `commit/evals/grade_benchmark.py:44-47,250-285`; `handoff/evals/grade_benchmark.py:86-98,262-270` | Loop and Commit inspect current checkout skill anatomy rather than the per-run old/current source. Handoff infers eval ID from metadata or folder and skips unresolved IDs. Root JSON shape is not validated. Existing DD-004 owns invalid/incomplete protocols; SAG-003 owns authoring anatomy intent. |
| Other consumers | Bounded search of maintained Markdown under `skills/`, `.agents/skills/`, excluding evals/archive/workspaces; `skills/spec-to-tasks/SKILL.md:100` | Only Spec readiness and this batch's internal Ralph call were found for literal Ralph/Execplan entry names; generic mentions are not proof of dependency closure. Handoff repo override is the found canonical path consumer. No migration bundle was loaded. |

## Failure-count investigation

Successive Ralph workers after successful task completion are new task runs, not replacements. A fresh worker can select a different task because prior `passes` changed; caller :35 deliberately prevents parent selection. Delegate's replacement rule applies to a failed/timed-out compliant subagent (`skills/delegate-to-subagents/SKILL.md:239-246`), with an at-most-one replacement unless actual user retry authorization exists. Loop's :34 independently caps consecutive failures at three.

There is a genuinely ambiguous overlap: a worker can fail while its selected task stays unfinished, so the next fresh worker retries the same eligible node. After two such failures, a third dispatch would be a second replacement under that reading. Conversely, a normally returned blocked-task report may be a completed worker assignment rather than a failed subagent execution. Source does not define which failure category or task identity drives the loop count, whether the requested Loop invocation supplies additional retry authorization, or how reset/no-progress behavior is counted. The source contains no actual execution invocation or explicit human retry consent. This audit invocation authorizes paper review only. Thus successful-task progression is compatible; the repeated-failure branch requires EH-005's precise decision. Neither source limit is declared contradictory or waived.

## Findings awaiting live human review

The single [findings register](../findings.md) owns full source, mechanism, proposal and validation details. These ten findings have no human disposition or native evidence yet.

| ID | Finding | Severity | Human status |
| --- | --- | --- | --- |
| [EH-001](../findings.md#eh-001-loop-paper-grader-does-not-establish-blind-orchestration) | Loop paper grader does not establish blind orchestration | Major | Pending human batch review |
| [EH-002](../findings.md#eh-002-commit-evaluations-cover-a-pr-title-override-without-default-coverage) | Commit evaluations cover a PR title override without default coverage | Observation | Pending human batch review |
| [EH-003](../findings.md#eh-003-handoff-grader-rejects-a-valid-requested-path) | Handoff grader rejects a valid requested path | Major | Pending human batch review |
| [EH-004](../findings.md#eh-004-handoff-evaluations-declare-two-missing-logs) | Handoff evaluations declare two missing logs | Minor | Pending human batch review |
| [EH-005](../findings.md#eh-005-ralph-loop-failure-counting-and-retry-consent-are-unresolved) | Ralph Loop failure counting and retry consent are unresolved | Major | Pending human batch review |
| [EH-006](../findings.md#eh-006-ralph-and-tdd-have-unresolved-approval-and-refactor-ordering) | Ralph and TDD have unresolved approval and refactor ordering | Major | Pending human batch review |
| [EH-007](../findings.md#eh-007-execplan-integration-has-unresolved-tested-tip-validation) | ExecPlan integration has unresolved tested-tip validation | Major | Pending human batch review |
| [EH-008](../findings.md#eh-008-published-execplan-requires-a-helper-with-unestablished-supply) | Published Execplan requires a helper with unestablished supply | Minor | Pending human batch review |
| [EH-009](../findings.md#eh-009-loop-and-commit-graders-inspect-unrelated-current-source-headings) | Loop and Commit graders inspect unrelated current-source headings | Major | Pending human batch review |
| [EH-010](../findings.md#eh-010-commit-dry-run-mutation-and-output-boundaries-are-unclear) | Commit dry-run mutation and output boundaries are unclear | Major | Pending human batch review |

## Proposed shared scope and retained boundaries

[SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) and [DD-004](../findings.md#dd-004-graders-can-announce-success-without-grading-runs-and-do-not-validate-json-shape) own the exact three proposed Loop/Commit/Handoff grader additions. Accepted targets remain nine producers/six protocol graders until the live decision; proposed totals are twelve/nine. Representations, outcomes, identities and compatibility remain unresolved. Measured character counts and useful checks stay protected.

EH-009 owns this batch's current-source/anatomy predicate mechanism. SAG-003 retains only its existing Create Skill body-contract question; no global anatomy rule or automatic SAG-007 scope expansion follows. Explicit PR-title overrides remain valid; EH-002 is an observation. Ralph's direct browser consumer allows an explicit repo command and blocks missing/failing supply (`skills/prd-ralph/references/browser-verification.md:19-24,45-50`); RPT-005 retains its separate planning-helper question. No installer/validator/target workflow or native baseline ran.

## Individual checklist matrices

Each skill has exactly the 58 catalog IDs in the order of `docs/skill-audit/coverage.md:19-90`. Seven columns separate applicability, adoption, compliance, exact source evidence, findings and gaps. `adopt` or `adapt` selects an inspection criterion and does not imply passed behavior. Criterion sources and strength are the individual catalog rows; the complete extracted source is `research/authoring-checklist/findings.md:14-69` and the dated required-client qualification is `research/provider-compatibility/findings.md:5-25`. All matrix source paths below resolve from the explicitly named bundle, except named cross-bundle dependencies, canonical .agents paths and installer anchors. Script assertions are inspected only; they are not runtime results. No check is marked incompatible because no required-client constraint with exhausted equivalent adaptations was established.

### prd-ralph matrix

Source prefix: `skills/prd-ralph/`. `local exec-plans` / `exec-plans` denotes `.agents/skills/exec-plans/SKILL.md`, and other named helper paths denote their existing `skills/<helper>/` source. Installer selection always denotes `scripts/install.sh:40-55` and `scripts/install.ps1:251-276`. Missing fixture anchors point to declarations, not nonexistent source lines.

| ID | Applicability | Adoption disposition | Current compliance | Evidence/source anchor | Findings | Unresolved gap |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Yes - All instructions | adopt | Satisfied statically | `SKILL.md:8,18-32 - one task and explicit gates` | None | Native behavior not inferred from source. |
| A02 | Yes - Workflow risk/variation | adopt | Unresolved consumer branch | `SKILL.md:65-85,123-158 - strict eligibility, safe assumptions and commit modes` | EH-006 | Already-confirmed seams can satisfy both; absent-confirmation and refactor-stage precedence unresolved. |
| A03 | Yes - Intended native model coverage | adapt - approved native seven-model medium matrix | Unresolved runtime/history | `SKILL.md:89-111 - required TDD/verification behavior to test` | None | No native seven-model medium-effort cases/repetitions. |
| A04-F | Yes - Required entry/YAML | adopt | Satisfied statically | `SKILL.md:1-4 - parsed YAML name/description strings` | None | Native behavior not inferred from source. |
| A04-N | Yes - Required client name constraint | adapt - VS Code directory/64-character rule; no Claude reserved-word transfer | Satisfied statically | `SKILL.md:2 - prd-ralph matches directory; 9 characters` | None | Native behavior not inferred from source. |
| A04-D | Yes - Required nonempty description | adapt - required nonempty string; Claude 1024/XML bounds not universal | Satisfied statically | `SKILL.md:3 - nonempty 116-character description` | None | Native behavior not inferred from source. |
| A05 | Yes - Every skill identity | adopt | Satisfied statically | `SKILL.md:2,6-8 - stable activity name and single-task identity` | None | Native behavior not inferred from source. |
| A06 | Yes - Every discovery description | adopt | Satisfied statically | `SKILL.md:3,8 - concrete one-task output; body inputs:10-16` | None | Native behavior not inferred from source. |
| A07 | Yes - Entry-body focus | adapt - inspect focus; 500 lines advisory | Satisfied statically | `SKILL.md:1-187 - essential gates retained; advisory length only` | None | Native behavior not inferred from source. |
| A08 | Yes - Entry/resource loading | adapt - conditional source navigation; client preloading unverified | Satisfied statically | `SKILL.md:36-42 - five conditional resources` | None | Native behavior not inferred from source. |
| A09 | Yes - Optional advanced branch | adopt | Satisfied statically | `SKILL.md:39-42 - browser, failure, commit/progress detail selected by trigger` | None | Native behavior not inferred from source. |
| A10 | Yes - Bundled reference navigation | adapt - direct bundle/shared navigation; preserve layout | Satisfied statically | `SKILL.md:38-42 - direct resource paths resolve` | None | Native behavior not inferred from source. |
| A11 | No - No bundled reference exceeds 100 lines. | not applicable - No bundled reference exceeds 100 lines. | Not applicable | `references/commit.md:1-100 - longest reference equals 100, not over` | None | None for this condition; no global waiver. |
| A12 | Yes - Documented paths | adopt | Satisfied statically | `SKILL.md:13,38-42 - portable progress/resource paths` | None | Native behavior not inferred from source. |
| A13 | Yes - Multi-step workflow | adopt | Satisfied statically | `SKILL.md:46-187 - prepare/select/implement/verify/finish/final` | None | Native behavior not inferred from source. |
| A14 | Yes - Quality-sensitive output | adopt | Satisfied statically | `references/verification.md:25-49; SKILL.md:123-158 - verify or block` | None | Native behavior not inferred from source. |
| A15 | No - No dated provider/version guidance or legacy procedure; session dates are evidence. | not applicable - No dated provider/version guidance or legacy procedure; session dates are evidence. | Not applicable | `SKILL.md:57-59; references/progress.md:11 - current HEAD/date captured, no version promise` | None | None for this condition; no global waiver. |
| A16 | Yes - Entry/resources terminology | adopt | Satisfied statically | `SKILL.md:25-32; references/progress.md:26-32 - passes/task/session commit vocabulary` | None | Native behavior not inferred from source. |
| A17 | Yes - Structured output | adopt | Satisfied statically | `references/progress.md:15-38; SKILL.md:173-177 - exact progress fields and COMPLETE` | None | Native behavior not inferred from source. |
| A18 | Yes - Output-shape examples | adopt | Satisfied statically | `references/browser-verification.md:34-41; references/commit.md:53-62 - concrete evidence/message examples` | None | Native behavior not inferred from source. |
| A19 | Yes - Conditional methods | adopt | Unresolved consumer branch | `SKILL.md:75-85,100-102,133-158 - explicit selection/doc/commit branches` | EH-006 | Already-confirmed seams can satisfy both; absent-confirmation and refactor-stage precedence unresolved. |
| A20 | Yes - Defaults/exceptions | adopt | Satisfied statically | `SKILL.md:13,15-16,76-78 - default progress, commit enabled, priority tie order` | None | Native behavior not inferred from source. |
| A21 | Yes - Baseline/evaluation claims | adapt - unchanged native diagnostic baseline before candidate comparison | Unresolved runtime/history | `SKILL.md:3,89-111 - no local evaluation baseline in maintained bundle` | None | No matched current-skill baseline in reviewed maintained resources; generated histories excluded. |
| A22 | Yes - Observable evaluation evidence | adapt - artifact predicates separate from native workflow traces | Unresolved evidence | `SKILL.md:110,160-171 - task output demands evidence, no shipped eval` | None | No bundled eval; absence alone is not a defect. Later cases must preserve single eligible PRD task with progress/commit gate. |
| A23 | Yes - Reusable real-work knowledge | adopt | Satisfied statically | `references/progress.md:35-36,44-56 - record mistakes/corrections/patterns` | None | Native behavior not inferred from source. |
| A24 | Yes - Fresh-session behavior | adapt - fresh native sessions and fixture state | Unresolved runtime/history | `SKILL.md:3,89-111 - fresh native task evidence absent` | None | Fresh using-session traces and task outcomes absent. |
| A25 | Conditional - team use unestablished | adopt | Unresolved history | `references/progress.md:45-46 - human corrections captured; usage history absent` | None | No independently verified team-use/feedback history supplied. |
| A26 | Yes - Observed retrieval/activation | adapt - trace required reads/activation; metadata is not observation | Unresolved runtime/history | `SKILL.md:36-42 - intended retrieval ordering; actual reads not observed` | None | No trace establishes resource reads, activation or ordering. |
| A27 | No - No bundled executable resource. | not applicable - No bundled executable resource. | Not applicable | `references/failures.md:1-34 - workflow failures documented, no executable resource` | None | None for this condition; no global waiver. |
| A28 | No - No bundled executable resource. | not applicable - No bundled executable resource. | Not applicable | `SKILL.md:1-187 - no configurable script constants` | None | None for this condition; no global waiver. |
| A29 | Yes - Repeated deterministic operations | adopt | Satisfied statically | `SKILL.md:117-121; references/commit.md:66-86 - reusable deterministic git audit commands` | None | Deterministic source utility/command reuse inspected; usefulness/runtime performance unmeasured. |
| A30 | No - No bundled executable resource. | not applicable - No bundled executable resource. | Not applicable | `SKILL.md:38-42 - references are read; no bundled executable` | None | None for this condition; no global waiver. |
| A31 | Yes - Browser/spatial task inputs | adapt - task browser/visual evidence with supported host | Partially evidenced | `references/browser-verification.md:7-24,45-50 - browser-visible checks required` | None | Browser/task-specific inspection must be exercised with supported host; no visual run evidence. |
| A32 | Yes - Complex/risky operations | adopt | Satisfied statically | `SKILL.md:67-85,115-158 - inspect task and gate edits/pass state` | None | Native behavior not inferred from source. |
| A33 | No - No external package dependency in owned executable resources; host tools are A36. | not applicable - No external package dependency in owned executable resources; host tools are A36. | Not applicable | `references/browser-verification.md:21-22,48 - playwright-cli supply required, no automatic install` | None | None for this condition; no global waiver. |
| A34 | Yes - File access/loading | adapt - source paths, shipment and actual access separate | Unresolved runtime/history | `SKILL.md:38-42 - all five source resources present and shipped` | None | Source presence does not establish installed or native access. |
| A35 | No - No specific MCP server/tool identifier is named. | not applicable - No specific MCP server/tool identifier is named. | Not applicable | `SKILL.md:1-187; references/failures.md:15 - no specific MCP server/tool ID` | None | None for this condition; no global waiver. |
| A36 | Yes - Tool/helper prerequisites | adopt | Satisfied statically | `SKILL.md:55-63,89; references/browser-verification.md:48 - repo/git/TDD/browser prerequisites` | None | Native behavior not inferred from source. |
| S01 | Yes - Purpose/trust boundaries | adopt | Partially evidenced | `SKILL.md:8,22-32,90-95 - selected task scope and source-of-truth boundary` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S02 | Yes - File/network/tool access | adopt | Partially evidenced | `references/commit.md:18,32,41-51 - explicit scoped git/file mutations; no push directive` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S03 | Yes - Potential sensitive context | adopt | Partially evidenced | `references/failures.md:21-25; references/progress.md:24-36 - exact output may contain sensitive data; no explicit redaction rule` | None | No explicit redaction rule in owned entry; actual sensitive input/output handling untested. |
| S04 | Yes - External/dependency authority | adopt | Partially evidenced | `SKILL.md:21-22,55,90-95 - PRD/repo input authority, no remote instructions fetched` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| R01 | Yes - Protected identity/intent | adopt | Satisfied statically | `SKILL.md:2-8,12-16 - preserve name/at-most-one trigger and inputs` | None | Native behavior not inferred from source. |
| R02 | No - No invocation-disable/sidecar control exists to preserve. | not applicable - No invocation-disable/sidecar control exists to preserve. | Not applicable | `SKILL.md:1-4 - no invocation-disable or sidecar control present` | None | None for this condition; no global waiver. |
| R03 | Yes - Approval/autonomy | adopt | Unresolved consumer branch | `SKILL.md:20,24-32,89; references/commit.md:90 - autonomy/commit/TDD confirmation boundary` | EH-006 | Already-confirmed seams can satisfy both; absent-confirmation and refactor-stage precedence unresolved. |
| R04 | Yes - Required dependencies | adopt | Unresolved consumer branch | `SKILL.md:89; references/browser-verification.md:19-24 - required helper/tool consumer` | EH-006; RPT-005 | Already-confirmed seams can satisfy both; absent-confirmation and refactor-stage precedence unresolved. |
| R05 | Yes - Stops/handoff | adopt | Unresolved consumer branch | `SKILL.md:48-51,63,79-85,123-158 - explicit blocker/complete stops` | EH-006 | Already-confirmed seams can satisfy both; absent-confirmation and refactor-stage precedence unresolved. |
| R06 | Yes - Required outputs | adopt | Satisfied statically | `references/progress.md:15-38; SKILL.md:173-187 - exact output plus brief blocked result` | None | Native behavior not inferred from source. |
| R07 | Yes - Repository authority | adopt | Satisfied statically for audit boundary | `SKILL.md:55,90-95 - follow applicable repo guidance; audit writes only report` | None | Parent owns canonical doc maintenance; dependent helper writes remain subject to repo authority. |
| R08 | No - No maintained benchmark resource or generated run output contract. | not applicable - No maintained benchmark resource or generated run output contract. | Not applicable | `SKILL.md:1-187 - no generated artifact directory claimed in maintained bundle` | None | None for this condition; no global waiver. |
| R09 | Yes - Scoped verification prerequisites | adopt | Partially evidenced | `SKILL.md:105-111; references/verification.md:13-34 - scoped task verification` | None | Scoped source verification rules read; audited commands/validators deliberately not run. |
| R10 | No - No Upgrade procedure or dependency in this bounded scope. | not applicable - No Upgrade procedure or dependency in this bounded scope. | Not applicable | `SKILL.md:1-187 - no Upgrade procedure/dependency in inspected scope` | None | None for this condition; no global waiver. |
| R11 | Yes - Evidence/grading claims | adapt - source/artifact/trace grades separate; unknown protocol pending | Satisfied statically | `SKILL.md:110,162-171 - demands real evidence; no run or eval grade inferred` | None | Native behavior not inferred from source. |
| R12 | Yes - Scoped source formatting | adopt | Satisfied statically | `SKILL.md:1-187; references/*.md - byte scan LF/no trailing whitespace/tabs` | None | Native behavior not inferred from source. |
| C01 | Yes - Native discovery/activation | adapt - native discovery/activation; replay is supplementary | Unresolved runtime/history | `SKILL.md:2-3 - portable discovery metadata; no activation trace` | None | Explicit/implicit native activation not tested. |
| C02 | Yes - Published resource selection | adapt - installer selection then actual client access | Satisfied selection source | `SKILL.md:38-42; scripts/install.sh:40-55; scripts/install.ps1:251-276 - six non-eval files ship` | None | Installed resource access/loader behavior untested; evals/fixtures are repository-only. |
| C03 | No - Core portable metadata only; no client-specific adapter field. | not applicable - Core portable metadata only; no client-specific adapter field. | Not applicable | `SKILL.md:1-4 - portable metadata only; no client adapter` | None | None for this condition; no global waiver. |
| C04 | Yes - Tool/activation consent | adapt - activation consent separate from tool permission | Unresolved runtime/history | `SKILL.md:89,105-111 - loading/command intent is not host tool consent` | None | Actual sandbox/tool consent enforcement untested. |

### prd-ralph-loop matrix

Source prefix: `skills/prd-ralph-loop/`. `local exec-plans` / `exec-plans` denotes `.agents/skills/exec-plans/SKILL.md`, and other named helper paths denote their existing `skills/<helper>/` source. Installer selection always denotes `scripts/install.sh:40-55` and `scripts/install.ps1:251-276`. Missing fixture anchors point to declarations, not nonexistent source lines.

| ID | Applicability | Adoption disposition | Current compliance | Evidence/source anchor | Findings | Unresolved gap |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Yes - All instructions | adopt | Satisfied statically | `SKILL.md:9-40 - small orchestration-only entry` | None | Native behavior not inferred from source. |
| A02 | Yes - Workflow risk/variation | adopt | Unresolved protected contract | `SKILL.md:15-22,34-35 - baseline and sequential/failure rules` | EH-005 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| A03 | Yes - Intended native model coverage | adapt - approved native seven-model medium matrix | Unresolved runtime/history | `SKILL.md:19-22 - native blind/delegated behavior needs model matrix` | None | No native seven-model medium-effort cases/repetitions. |
| A04-F | Yes - Required entry/YAML | adopt | Satisfied statically | `SKILL.md:1-5 - parsed mapping with name/description and retained boolean` | None | Native behavior not inferred from source. |
| A04-N | Yes - Required client name constraint | adapt - VS Code directory/64-character rule; no Claude reserved-word transfer | Satisfied statically | `SKILL.md:2 - directory match, lowercase-hyphen name, 14 characters` | None | Native behavior not inferred from source. |
| A04-D | Yes - Required nonempty description | adapt - required nonempty string; Claude 1024/XML bounds not universal | Satisfied statically | `SKILL.md:3 - nonempty 116-character description` | None | Native behavior not inferred from source. |
| A05 | Yes - Every skill identity | adopt | Satisfied statically | `SKILL.md:2-3 - loop name distinguishes single Ralph` | None | Native behavior not inferred from source. |
| A06 | Yes - Every discovery description | adopt | Satisfied statically | `SKILL.md:3-4 - all-task orchestration and explicit-only control` | None | Native behavior not inferred from source. |
| A07 | Yes - Entry-body focus | adapt - inspect focus; 500 lines advisory | Satisfied statically | `SKILL.md:1-40 - short body; retained controls` | None | Native behavior not inferred from source. |
| A08 | Yes - Entry/resource loading | adapt - conditional source navigation; client preloading unverified | Satisfied statically | `SKILL.md:19,21,29 - required helper names; no ancillary runtime resource` | None | Native behavior not inferred from source. |
| A09 | No - No optional advanced resource/feature branch. | not applicable - No optional advanced resource/feature branch. | Not applicable | `SKILL.md:1-40 - no optional advanced feature resource` | None | None for this condition; no global waiver. |
| A10 | No - No bundled runtime reference navigation. | not applicable - No bundled runtime reference navigation. | Not applicable | `SKILL.md:19,21,29 - named dependencies; no bundled reference document` | None | None for this condition; no global waiver. |
| A11 | No - No bundled runtime reference. | not applicable - No bundled runtime reference. | Not applicable | `SKILL.md:1-40 - no bundled reference over 100 lines` | None | None for this condition; no global waiver. |
| A12 | Yes - Documented paths | adopt | Satisfied statically | `evals/evals.json:9,22,35 - all three declared fixture paths exist` | None | Native behavior not inferred from source. |
| A13 | Yes - Multi-step workflow | adopt | Satisfied statically | `SKILL.md:15-30 - baseline/loop/scope/learning/report ordering` | None | Native behavior not inferred from source. |
| A14 | Yes - Quality-sensitive output | adopt | Satisfied statically | `SKILL.md:34; prd-ralph/SKILL.md:123-158 - repeated worker and verification stop` | None | Native behavior not inferred from source. |
| A15 | No - No dated provider/version guidance or legacy procedure; session dates are evidence. | not applicable - No dated provider/version guidance or legacy procedure; session dates are evidence. | Not applicable | `SKILL.md:16-17 - captures session baseline, no fixed model/version claim` | None | None for this condition; no global waiver. |
| A16 | Yes - Entry/resources terminology | adopt | Unresolved protected contract | `SKILL.md:20-22,34-35; evals/evals.json:19-27 - task/failure/paper-selection distinction` | EH-001; EH-005 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| A17 | Yes - Structured output | adopt | Satisfied statically | `SKILL.md:22,30; evals/evals.json:6-14 - worker completion versus eval decision schema` | EH-001; EH-009 | Native behavior not inferred from source. |
| A18 | Yes - Output-shape examples | adopt | Satisfied statically | `evals/evals.json:6-40 - complete/incomplete/invalid paper examples` | EH-001 | Native behavior not inferred from source. |
| A19 | Yes - Conditional methods | adopt | Unresolved protected contract | `SKILL.md:34-40 - failure, blindness and stop branches` | EH-005 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| A20 | Yes - Defaults/exceptions | adopt | Unresolved protected contract | `SKILL.md:11,20-22 - missing input ask then one fresh worker per sequential run` | EH-005 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| A21 | Yes - Baseline/evaluation claims | adapt - unchanged native diagnostic baseline before candidate comparison | Unresolved runtime/history | `evals/evals.json:3-43 - scenarios present, no matched native baseline` | EH-009 | No matched current-skill baseline in reviewed maintained resources; generated histories excluded. |
| A22 | Yes - Observable evaluation evidence | adapt - artifact predicates separate from native workflow traces | Defective/partial oracle | `evals/grade_benchmark.py:93-115 - inspectable status/token/target predicates` | EH-001; EH-009 | Exact COMPLETE and conjunction predicates do not establish stated artifacts/workflow; simulation must be distinguished from trace. |
| A23 | Yes - Reusable real-work knowledge | adopt | Satisfied statically | `SKILL.md:28-29 - progress-fed durable learning after loop` | None | Native behavior not inferred from source. |
| A24 | Yes - Fresh-session behavior | adapt - fresh native sessions and fixture state | Unresolved runtime/history | `evals/evals.json:6,19,32 - dry runs explicitly forbid real subagents` | None | Fresh using-session traces and task outcomes absent. |
| A25 | Conditional - team use unestablished | adopt | Unresolved history | `SKILL.md:29 - self-improve input exists; user feedback history not supplied` | None | No independently verified team-use/feedback history supplied. |
| A26 | Yes - Observed retrieval/activation | adapt - trace required reads/activation; metadata is not observation | Unresolved runtime/history | `SKILL.md:19-22,29,39 - load/read order declared; no trace confirms it` | None | No trace establishes resource reads, activation or ordering. |
| A27 | Yes - Bundled executable error handling | adopt | Partially evidenced | `evals/grade_benchmark.py:24-30,119-156 - JSON shape/no-run protocol incomplete` | DD-004 (proposed addition) | Wrong JSON shape and empty/skipped run outcomes need existing DD-004 protocol decision. |
| A28 | Yes - Script constants | adopt | Defective source predicate | `evals/grade_benchmark.py:8-15,41-44 - heading constants lack approved output contract` | SAG-003 (owner context); EH-009 | Current cwd heading test is unrelated to paper artifact; run/source identity needs repair. |
| A29 | Yes - Repeated deterministic operations | adopt | Satisfied statically | `evals/grade_benchmark.py:93-130 - repeated artifact grading utility` | None | Deterministic source utility/command reuse inspected; usefulness/runtime performance unmeasured. |
| A30 | Yes - Bundled script use contract | adapt - repository eval CLI usage; not published runtime | Satisfied statically | `evals/grade_benchmark.py:133-156 - CLI iteration input and grading.json output` | None | CLI usage/output documented; no target utility executed. |
| A31 | Yes - Browser/spatial task inputs | adapt - task browser/visual evidence with supported host | Partially evidenced | `SKILL.md:21; prd-ralph/references/browser-verification.md:7-24 - browser gate delegated` | None | Browser/task-specific inspection must be exercised with supported host; no visual run evidence. |
| A32 | Yes - Complex/risky operations | adopt | Satisfied statically | `SKILL.md:15-19,23-27 - baseline/full scope precede and record execution` | None | Native behavior not inferred from source. |
| A33 | No - No external package dependency in owned executable resources; host tools are A36. | not applicable - No external package dependency in owned executable resources; host tools are A36. | Not applicable | `evals/grade_benchmark.py:3-6 - standard-library imports only` | None | None for this condition; no global waiver. |
| A34 | Yes - File access/loading | adapt - source paths, shipment and actual access separate | Unresolved runtime/history | `SKILL.md:19,21,29 - source helpers exist; installed loader access untested` | None | Source presence does not establish installed or native access. |
| A35 | No - No specific MCP server/tool identifier is named. | not applicable - No specific MCP server/tool identifier is named. | Not applicable | `SKILL.md:1-40; evals/grade_benchmark.py:3-6 - no MCP server/tool ID` | None | None for this condition; no global waiver. |
| A36 | Yes - Tool/helper prerequisites | adopt | Satisfied statically | `SKILL.md:15-19; delegate-to-subagents/SKILL.md:38-55 - git/exact route/runtime prerequisites` | None | Native behavior not inferred from source. |
| S01 | Yes - Purpose/trust boundaries | adopt | Partially evidenced | `SKILL.md:34-40 - parent stays blind and does not implement` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S02 | Yes - File/network/tool access | adopt | Partially evidenced | `SKILL.md:16-17,21,29 - scoped git reads/worker edits/helper doc writes` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S03 | Yes - Potential sensitive context | adopt | Partially evidenced | `SKILL.md:28-29; evals/grade_benchmark.py:50,153 - progress/transcript may be sensitive; no explicit redaction` | None | No explicit redaction rule in owned entry; actual sensitive input/output handling untested. |
| S04 | Yes - External/dependency authority | adopt | Partially evidenced | `SKILL.md:21,35 - delegated PRD input; required helper authority retained` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| R01 | Yes - Protected identity/intent | adopt | Satisfied statically | `SKILL.md:2-4,34-40 - all-task scope, existing name and blindness` | None | Native behavior not inferred from source. |
| R02 | Yes - Present invocation controls | adopt | Satisfied statically | `SKILL.md:4 - explicit invocation control retained` | None | Native behavior not inferred from source. |
| R03 | Yes - Approval/autonomy | adopt | Unresolved protected contract | `SKILL.md:11,34; delegate-to-subagents/SKILL.md:246 - missing path/retry authorization` | EH-005 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| R04 | Yes - Required dependencies | adopt | Unresolved protected contract | `SKILL.md:19-22,29 - Delegate/Ralph/Self Improve retained` | EH-005; EH-001 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| R05 | Yes - Stops/handoff | adopt | Unresolved protected contract | `SKILL.md:22,34,39 - COMPLETE/three-failure/read-order stops` | EH-005; EH-001 | Task/worker-failure/replacement identities and actual retry authorization require separate choice. |
| R06 | Yes - Required outputs | adopt | Satisfied statically | `SKILL.md:23-30 - full scope/report; eval dry-run output separate` | EH-001; EH-009 | Native behavior not inferred from source. |
| R07 | Yes - Repository authority | adopt | Satisfied statically for audit boundary | `SKILL.md:29; self-improve/SKILL.md:14-40 - maintenance remains applicable repo-scoped` | None | Parent owns canonical doc maintenance; dependent helper writes remain subject to repo authority. |
| R08 | Yes - Benchmark/source separation | adopt | Satisfied statically | `evals/grade_benchmark.py:135,143-153 - sibling iteration/run outputs; fixtures separate` | None | Native behavior not inferred from source. |
| R09 | Yes - Scoped verification prerequisites | adopt | Partially evidenced | `SKILL.md:19-22; evals/grade_benchmark.py:133-141 - helper and directory prerequisites` | None | Scoped source verification rules read; audited commands/validators deliberately not run. |
| R10 | No - No Upgrade procedure or dependency in this bounded scope. | not applicable - No Upgrade procedure or dependency in this bounded scope. | Not applicable | `SKILL.md:1-40 - no Upgrade procedure/dependency in scope` | None | None for this condition; no global waiver. |
| R11 | Yes - Evidence/grading claims | adapt - source/artifact/trace grades separate; unknown protocol pending | Defective source predicate | `evals/grade_benchmark.py:57-78,93-115,143-156 - metrics/protocol/oracle limits` | EH-001; EH-009; SAG-008/DD-004 (proposed additions) | Current cwd heading test is unrelated to paper artifact; run/source identity needs repair. |
| R12 | Yes - Scoped source formatting | adopt | Satisfied statically | `SKILL.md:1-40; evals/* - byte scan LF/no trailing whitespace/tabs` | None | Native behavior not inferred from source. |
| C01 | Yes - Native discovery/activation | adapt - native discovery/activation; replay is supplementary | Unresolved runtime/history | `SKILL.md:2-4 - metadata/disable field; no native explicit-only activation test` | None | Explicit/implicit native activation not tested. |
| C02 | Yes - Published resource selection | adapt - installer selection then actual client access | Satisfied selection source | `scripts/install.sh:40-55; scripts/install.ps1:251-276; SKILL.md:1-40 - one shipped entry, two eval files/three fixtures pruned` | None | Installed resource access/loader behavior untested; evals/fixtures are repository-only. |
| C03 | Yes - Client metadata adapters | adapt - retain surface-specific controls without universal enforcement | Partially evidenced | `SKILL.md:4 - Copilot field, no Codex sidecar; client equivalence unverified` | None | Controls preserved as source; Codex/Copilot/Gemini enforcement not interchangeable or tested. |
| C04 | Yes - Tool/activation consent | adapt - activation consent separate from tool permission | Unresolved runtime/history | `SKILL.md:19-22; delegate-to-subagents/SKILL.md:179-189 - approval applies before dispatch` | None | Actual sandbox/tool consent enforcement untested. |
### execplan-implement matrix

Source prefix: `skills/execplan-implement/`. `local exec-plans` / `exec-plans` denotes `.agents/skills/exec-plans/SKILL.md`, and other named helper paths denote their existing `skills/<helper>/` source. Installer selection always denotes `scripts/install.sh:40-55` and `scripts/install.ps1:251-276`. Missing fixture anchors point to declarations, not nonexistent source lines.

| ID | Applicability | Adoption disposition | Current compliance | Evidence/source anchor | Findings | Unresolved gap |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Yes - All instructions | adopt | Satisfied statically | `SKILL.md:7-50 - focused task-graph implementation entry` | None | Native behavior not inferred from source. |
| A02 | Yes - Workflow risk/variation | adopt | Satisfied statically | `SKILL.md:29-46 - fresh-node ownership and serialized clean integration` | None | Native behavior not inferred from source. |
| A03 | Yes - Intended native model coverage | adapt - approved native seven-model medium matrix | Unresolved runtime/history | `SKILL.md:15,31-35 - parallel implementation behavior needs model matrix` | None | No native seven-model medium-effort cases/repetitions. |
| A04-F | Yes - Required entry/YAML | adopt | Satisfied statically | `SKILL.md:1-5 - parsed YAML metadata and retained boolean` | None | Native behavior not inferred from source. |
| A04-N | Yes - Required client name constraint | adapt - VS Code directory/64-character rule; no Claude reserved-word transfer | Satisfied statically | `SKILL.md:2 - directory match, lowercase-hyphen name, 18 characters` | None | Native behavior not inferred from source. |
| A04-D | Yes - Required nonempty description | adapt - required nonempty string; Claude 1024/XML bounds not universal | Satisfied statically | `SKILL.md:3 - nonempty 30-character description` | None | Native behavior not inferred from source. |
| A05 | Yes - Every skill identity | adopt | Satisfied statically | `SKILL.md:2,7-9 - stable ExecPlan implementation identity` | None | Native behavior not inferred from source. |
| A06 | Yes - Every discovery description | adopt | Satisfied statically | `SKILL.md:3-4 - explicit plan/code purpose; implicit invocation disabled` | None | Native behavior not inferred from source. |
| A07 | Yes - Entry-body focus | adapt - inspect focus; 500 lines advisory | Satisfied statically | `SKILL.md:1-80 - compact body, commands and controls retained` | None | Native behavior not inferred from source. |
| A08 | Yes - Entry/resource loading | adapt - conditional source navigation; client preloading unverified | Satisfied statically | `SKILL.md:11,19,34 - commit reference and mandatory helpers` | None | Native behavior not inferred from source. |
| A09 | Yes - Optional advanced branch | adopt | Satisfied statically | `SKILL.md:23,39 - optional exploration/exclusive merger branch` | None | Native behavior not inferred from source. |
| A10 | Yes - Bundled reference navigation | adapt - direct bundle/shared navigation; preserve layout | Satisfied statically | `SKILL.md:11,34 - direct message link; mandatory named helper at :19` | None | Native behavior not inferred from source. |
| A11 | No - No bundled reference exceeds 100 lines. | not applicable - No bundled reference exceeds 100 lines. | Not applicable | `references/message.md:1-77 - no over-100-line reference` | None | None for this condition; no global waiver. |
| A12 | Yes - Documented paths | adopt | Partially evidenced dependency | `SKILL.md:11,33,54-72 - portable relative message/worktree paths` | EH-008 | ExecPlans exists repo-locally but is not selected for publishing; independent host supply unverified. |
| A13 | Yes - Multi-step workflow | adopt | Satisfied statically | `SKILL.md:19-50 - task graph/frontier/integration loop` | None | Native behavior not inferred from source. |
| A14 | Yes - Quality-sensitive output | adopt | Unresolved protected contract | `SKILL.md:27,39-43,48 - validation/repair loop but no-conflict rerun ambiguity` | EH-007 | Human must define conflict-free tested-state/validation meaning while preserving serial integration. |
| A15 | No - No dated provider/version guidance or legacy procedure; session dates are evidence. | not applicable - No dated provider/version guidance or legacy procedure; session dates are evidence. | Not applicable | `SKILL.md:41 - refresh rebased SHAs; no model/version date claim` | None | None for this condition; no global waiver. |
| A16 | Yes - Entry/resources terminology | adopt | Satisfied statically | `SKILL.md:13,29,37-50 - node/frontier/base/private worker terminology` | None | Native behavior not inferred from source. |
| A17 | Yes - Structured output | adopt | Satisfied statically | `references/message.md:45-77; SKILL.md:50 - commit format/human-ready branch` | None | Native behavior not inferred from source. |
| A18 | Yes - Output-shape examples | adopt | Satisfied statically | `SKILL.md:56-73; references/message.md:7-15,47-64 - worktree/message examples` | None | Native behavior not inferred from source. |
| A19 | Yes - Conditional methods | adopt | Satisfied statically | `SKILL.md:23,25,39-40 - exploration/base-branch/conflict/failure branches` | None | Native behavior not inferred from source. |
| A20 | Yes - Defaults/exceptions | adopt | Satisfied statically | `SKILL.md:29-35,37-46 - isolated fresh node, private branch, serial ff-only default` | None | Native behavior not inferred from source. |
| A21 | Yes - Baseline/evaluation claims | adapt - unchanged native diagnostic baseline before candidate comparison | Unresolved runtime/history | `SKILL.md:7-50 - no maintained eval or baseline bundle` | None | No matched current-skill baseline in reviewed maintained resources; generated histories excluded. |
| A22 | Yes - Observable evaluation evidence | adapt - artifact predicates separate from native workflow traces | Unresolved evidence | `SKILL.md:39-50 - intended integration outputs inspectable; no bundled eval` | None | No bundled eval; absence alone is not a defect. Later cases must preserve isolated task graph integration. |
| A23 | Yes - Reusable real-work knowledge | adopt | Satisfied statically | `SKILL.md:27,40-41; exec-plans/SKILL.md:70-76 - discoveries/living plan updates` | None | Native behavior not inferred from source. |
| A24 | Yes - Fresh-session behavior | adapt - fresh native sessions and fixture state | Unresolved runtime/history | `SKILL.md:7-50 - fresh worker behavior asserted, no native fresh-session data` | None | Fresh using-session traces and task outcomes absent. |
| A25 | Conditional - team use unestablished | adopt | Unresolved history | `SKILL.md:50 - human review endpoint; usage/team feedback absent` | None | No independently verified team-use/feedback history supplied. |
| A26 | Yes - Observed retrieval/activation | adapt - trace required reads/activation; metadata is not observation | Unresolved runtime/history | `SKILL.md:11,19,32-34 - required loads declared; no performed-read evidence` | None | No trace establishes resource reads, activation or ordering. |
| A27 | No - No bundled executable resource. | not applicable - No bundled executable resource. | Not applicable | `SKILL.md:1-80 - no bundled executable resource` | None | None for this condition; no global waiver. |
| A28 | No - No bundled executable resource. | not applicable - No bundled executable resource. | Not applicable | `SKILL.md:1-80 - no configurable script constants` | None | None for this condition; no global waiver. |
| A29 | Yes - Repeated deterministic operations | adopt | Satisfied statically | `SKILL.md:56-73 - deterministic worktree command example; no wrapper needed by evidence` | None | Deterministic source utility/command reuse inspected; usefulness/runtime performance unmeasured. |
| A30 | No - No bundled executable resource. | not applicable - No bundled executable resource. | Not applicable | `SKILL.md:1-80 - no bundled/named executable script` | None | None for this condition; no global waiver. |
| A31 | Yes - Browser/spatial task inputs | adapt - task browser/visual evidence with supported host | Partially evidenced | `SKILL.md:21,32; exec-plans/SKILL.md:56 - plan-defined observable validation` | None | Browser/task-specific inspection must be exercised with supported host; no visual run evidence. |
| A32 | Yes - Complex/risky operations | adopt | Unresolved protected contract | `SKILL.md:7,21,27,39-43 - supplied plan and integrated validation` | EH-007 | Human must define conflict-free tested-state/validation meaning while preserving serial integration. |
| A33 | No - No external package dependency in owned executable resources; host tools are A36. | not applicable - No external package dependency in owned executable resources; host tools are A36. | Not applicable | `SKILL.md:54-73 - git commands; no external package specified` | None | None for this condition; no global waiver. |
| A34 | Yes - File access/loading | adapt - source paths, shipment and actual access separate | Partially evidenced dependency | `SKILL.md:11,19 - message resolves, local-only ExecPlans supply unresolved` | EH-008 | ExecPlans exists repo-locally but is not selected for publishing; independent host supply unverified. |
| A35 | No - No specific MCP server/tool identifier is named. | not applicable - No specific MCP server/tool identifier is named. | Not applicable | `SKILL.md:1-80; agents/openai.yaml:1-5 - no specific MCP tool ID` | None | None for this condition; no global waiver. |
| A36 | Yes - Tool/helper prerequisites | adopt | Partially evidenced dependency | `SKILL.md:19,32-35,38-44 - required helper/worktree/git/cleanliness prerequisites` | EH-008 | ExecPlans exists repo-locally but is not selected for publishing; independent host supply unverified. |
| S01 | Yes - Purpose/trust boundaries | adopt | Partially evidenced | `SKILL.md:9,29-35,44 - plan purpose, private isolated ownership and cleanup scope` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S02 | Yes - File/network/tool access | adopt | Partially evidenced | `SKILL.md:38-44,68-72 - local rebase/ff-only/clean branch cleanup; no push` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S03 | Yes - Potential sensitive context | adopt | Partially evidenced | `references/message.md:59-77 - optional reliable session note/trailers; no log-redaction rule` | None | No explicit redaction rule in owned entry; actual sensitive input/output handling untested. |
| S04 | Yes - External/dependency authority | adopt | Partially evidenced | `SKILL.md:19,21,23 - approved plan and required helper context, optional external docs` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| R01 | Yes - Protected identity/intent | adopt | Satisfied statically | `SKILL.md:2-9,29 - name/plan graph identity and fresh-node rule retained` | None | Native behavior not inferred from source. |
| R02 | Yes - Present invocation controls | adopt | Satisfied statically | `SKILL.md:4; agents/openai.yaml:4-5 - both invocation controls present` | None | Native behavior not inferred from source. |
| R03 | Yes - Approval/autonomy | adopt | Satisfied statically | `SKILL.md:35,39-44,50 - private branches, repair stop, clean deletion, human review` | None | Native behavior not inferred from source. |
| R04 | Yes - Required dependencies | adopt | Partially evidenced dependency | `SKILL.md:19,32; local exec-plans/SKILL.md:2-3 - required helpers including local-only supply` | EH-008 | ExecPlans exists repo-locally but is not selected for publishing; independent host supply unverified. |
| R05 | Yes - Stops/handoff | adopt | Unresolved protected contract | `SKILL.md:27,40,44,50 - repair pause, clean scoped cleanup and completion` | EH-007 | Human must define conflict-free tested-state/validation meaning while preserving serial integration. |
| R06 | Yes - Required outputs | adopt | Unresolved protected contract | `SKILL.md:9,11,41,50 - commits, living plan and human-ready base branch` | EH-007 | Human must define conflict-free tested-state/validation meaning while preserving serial integration. |
| R07 | Yes - Repository authority | adopt | Satisfied statically for audit boundary | `SKILL.md:19; exec-plans/SKILL.md:70-76 - plan sync; local helper edit protection retained` | None | Parent owns canonical doc maintenance; dependent helper writes remain subject to repo authority. |
| R08 | No - No maintained benchmark resource or generated run output contract. | not applicable - No maintained benchmark resource or generated run output contract. | Not applicable | `SKILL.md:23 - saved exploration notes beside plan, no generated benchmark artifacts` | None | None for this condition; no global waiver. |
| R09 | Yes - Scoped verification prerequisites | adopt | Unresolved protected contract | `SKILL.md:27,39-43 - conflict tests and validated progress; no-conflict state gap` | EH-007 | Human must define conflict-free tested-state/validation meaning while preserving serial integration. |
| R10 | No - No Upgrade procedure or dependency in this bounded scope. | not applicable - No Upgrade procedure or dependency in this bounded scope. | Not applicable | `SKILL.md:1-80 - no Upgrade procedure/dependency in scope` | None | None for this condition; no global waiver. |
| R11 | Yes - Evidence/grading claims | adapt - source/artifact/trace grades separate; unknown protocol pending | Unresolved protected contract | `SKILL.md:39-43 - tested-state claims require independently recorded verification` | EH-007 | Human must define conflict-free tested-state/validation meaning while preserving serial integration. |
| R12 | Yes - Scoped source formatting | adopt | Satisfied statically | `SKILL.md:1-80; references/message.md:1-77 - byte scan LF/no trailing whitespace/tabs` | None | Native behavior not inferred from source. |
| C01 | Yes - Native discovery/activation | adapt - native discovery/activation; replay is supplementary | Unresolved runtime/history | `SKILL.md:2-4; agents/openai.yaml:4-5 - source discovery/control only` | None | Explicit/implicit native activation not tested. |
| C02 | Yes - Published resource selection | adapt - installer selection then actual client access | Partially evidenced dependency | `scripts/install.sh:40-55; scripts/install.ps1:251-276; SKILL.md:11,19 - three files ship; required local helper unshipped` | EH-008 | ExecPlans exists repo-locally but is not selected for publishing; independent host supply unverified. |
| C03 | Yes - Client metadata adapters | adapt - retain surface-specific controls without universal enforcement | Partially evidenced | `SKILL.md:4; agents/openai.yaml:4-5 - Codex sidecar/Copilot control, no universal proof` | None | Controls preserved as source; Codex/Copilot/Gemini enforcement not interchangeable or tested. |
| C04 | Yes - Tool/activation consent | adapt - activation consent separate from tool permission | Unresolved runtime/history | `SKILL.md:19,32-35 - helper activation is not host approval for git mutations` | None | Actual sandbox/tool consent enforcement untested. |

### commit matrix

Source prefix: `skills/commit/`. `local exec-plans` / `exec-plans` denotes `.agents/skills/exec-plans/SKILL.md`, and other named helper paths denote their existing `skills/<helper>/` source. Installer selection always denotes `scripts/install.sh:40-55` and `scripts/install.ps1:251-276`. Missing fixture anchors point to declarations, not nonexistent source lines.

| ID | Applicability | Adoption disposition | Current compliance | Evidence/source anchor | Findings | Unresolved gap |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Yes - All instructions | adopt | Satisfied statically | `SKILL.md:8,17,19-82 - bounded single commit workflow` | None | Native behavior not inferred from source. |
| A02 | Yes - Workflow risk/variation | adopt | Satisfied statically | `SKILL.md:38-60,72-75 - strict mutation scope and explicit publication` | None | Native behavior not inferred from source. |
| A03 | Yes - Intended native model coverage | adapt - approved native seven-model medium matrix | Unresolved runtime/history | `SKILL.md:53-75 - permission/staging/publication behavior needs matrix` | None | No native seven-model medium-effort cases/repetitions. |
| A04-F | Yes - Required entry/YAML | adopt | Satisfied statically | `SKILL.md:1-4 - parsed name/description mapping` | None | Native behavior not inferred from source. |
| A04-N | Yes - Required client name constraint | adapt - VS Code directory/64-character rule; no Claude reserved-word transfer | Satisfied statically | `SKILL.md:2 - directory match, lowercase name, 6 characters` | None | Native behavior not inferred from source. |
| A04-D | Yes - Required nonempty description | adapt - required nonempty string; Claude 1024/XML bounds not universal | Satisfied statically | `SKILL.md:3 - nonempty 164-character description` | None | Native behavior not inferred from source. |
| A05 | Yes - Every skill identity | adopt | Satisfied statically | `SKILL.md:2,8 - activity name aligns exact one commit` | None | Native behavior not inferred from source. |
| A06 | Yes - Every discovery description | adopt | Satisfied statically | `SKILL.md:3,10-17 - commit/save/stage/push/PR triggers and exclusions` | None | Native behavior not inferred from source. |
| A07 | Yes - Entry-body focus | adapt - inspect focus; 500 lines advisory | Satisfied statically | `SKILL.md:1-104 - gates stay in focused body` | None | Native behavior not inferred from source. |
| A08 | Yes - Entry/resource loading | adapt - conditional source navigation; client preloading unverified | Satisfied statically | `SKILL.md:51,62,74-75 - four selective references` | None | Native behavior not inferred from source. |
| A09 | Yes - Optional advanced branch | adopt | Satisfied statically | `SKILL.md:72-75 - PR/dry-run detail conditional` | None | Native behavior not inferred from source. |
| A10 | Yes - Bundled reference navigation | adapt - direct bundle/shared navigation; preserve layout | Satisfied statically | `SKILL.md:51,62,74-75 - direct links; references/pr.md:29-33 reuses directly linked message` | None | Native behavior not inferred from source. |
| A11 | No - No bundled reference exceeds 100 lines. | not applicable - No bundled reference exceeds 100 lines. | Not applicable | `references/message.md:1-77 - longest reference below 100 lines` | None | None for this condition; no global waiver. |
| A12 | Yes - Documented paths | adopt | Satisfied statically | `SKILL.md:51,62,74-75; evals/evals.json:9,24,39,53 - all local paths resolve` | None | Native behavior not inferred from source. |
| A13 | Yes - Multi-step workflow | adopt | Unresolved protected dry-run boundary | `SKILL.md:21-82 - inspect/stop/branch/scope/message/commit/publication/final` | EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| A14 | Yes - Quality-sensitive output | adopt | Satisfied statically | `SKILL.md:94-104 - final verification checklist and required-command failure stop :46` | None | Native behavior not inferred from source. |
| A15 | No - No dated provider/version guidance or legacy procedure; session dates are evidence. | not applicable - No dated provider/version guidance or legacy procedure; session dates are evidence. | Not applicable | `references/branch-names.md:25 - real date fallback rather than stale fixed date` | None | None for this condition; no global waiver. |
| A16 | Yes - Entry/resources terminology | adopt | Satisfied statically | `references/message.md:8-15; evals/evals.json:21 - first line versus subject override` | EH-002 (observation) | Native behavior not inferred from source. |
| A17 | Yes - Structured output | adopt | Satisfied statically | `references/message.md:45-77; references/dry-run.md:5-22 - required structured output` | EH-002 (observation); EH-009 | Native behavior not inferred from source. |
| A18 | Yes - Output-shape examples | adopt | Satisfied statically | `references/branch-names.md:27-33; message.md:47-64 - examples` | None | Native behavior not inferred from source. |
| A19 | Yes - Conditional methods | adopt | Unresolved protected dry-run boundary | `SKILL.md:38-60,72-75 - state/scope/PR/dry-run branches` | EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| A20 | Yes - Defaults/exceptions | adopt | Unresolved protected dry-run boundary | `SKILL.md:53-60,87,90-91 - staged-first/default-main/default-trailer with exceptions` | EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| A21 | Yes - Baseline/evaluation claims | adapt - unchanged native diagnostic baseline before candidate comparison | Unresolved runtime/history | `evals/evals.json:3-62 - four paper cases, no current matched baseline` | EH-009 | No matched current-skill baseline in reviewed maintained resources; generated histories excluded. |
| A22 | Yes - Observable evaluation evidence | adapt - artifact predicates separate from native workflow traces | Defective source predicate | `evals/grade_benchmark.py:130-247 - artifact/scope/message predicates` | EH-002 (observation); EH-009 | Current cwd heading test is unrelated to paper artifact; run/source identity needs repair. |
| A23 | Conditional - authoring provenance/history not supplied | adopt | Unresolved history | `SKILL.md:21 - use conversation rationale/tests; no authoring task history claimed` | None | Conversation-based output intent is documented; no real-work authoring history inferred. |
| A24 | Yes - Fresh-session behavior | adapt - fresh native sessions and fixture state | Unresolved runtime/history | `evals/evals.json:6,21,36,50 - no-git paper contexts, no native sessions` | None | Fresh using-session traces and task outcomes absent. |
| A25 | Conditional - team use unestablished | adopt | Unresolved history | `SKILL.md:21,58,60 - user intent and required asks; team feedback history absent` | None | No independently verified team-use/feedback history supplied. |
| A26 | Yes - Observed retrieval/activation | adapt - trace required reads/activation; metadata is not observation | Unresolved runtime/history | `SKILL.md:51,62,74-75 - resource selection declared, actual access untested` | None | No trace establishes resource reads, activation or ordering. |
| A27 | Yes - Bundled executable error handling | adopt | Partially evidenced | `evals/grade_benchmark.py:27-33,250-288 - invalid-root/no-run behavior incomplete` | DD-004 (proposed addition) | Wrong JSON shape and empty/skipped run outcomes need existing DD-004 protocol decision. |
| A28 | Yes - Script constants | adopt | Defective source predicate | `evals/grade_benchmark.py:9-18 - trailer sourced, headings not approved contract` | SAG-003 (owner context); EH-009 | Current cwd heading test is unrelated to paper artifact; run/source identity needs repair. |
| A29 | Yes - Repeated deterministic operations | adopt | Satisfied statically | `evals/grade_benchmark.py:50-81 - reusable deterministic message-shape utility` | None | Deterministic source utility/command reuse inspected; usefulness/runtime performance unmeasured. |
| A30 | Yes - Bundled script use contract | adapt - repository eval CLI usage; not published runtime | Satisfied statically | `evals/grade_benchmark.py:265-288 - iteration CLI, grading.json outputs` | None | CLI usage/output documented; no target utility executed. |
| A31 | No - No layout/spatial source input requiring visual analysis. | not applicable - No layout/spatial source input requiring visual analysis. | Not applicable | `SKILL.md:59 - screenshots/video are generated artifacts to exclude, not visual input requirement` | None | None for this condition; no global waiver. |
| A32 | Yes - Complex/risky operations | adopt | Satisfied statically | `SKILL.md:23-60; references/dry-run.md:5-22 - inspect state/scope before commit` | None | Native behavior not inferred from source. |
| A33 | No - No external package dependency in owned executable resources; host tools are A36. | not applicable - No external package dependency in owned executable resources; host tools are A36. | Not applicable | `evals/grade_benchmark.py:3-6; references/pr.md:9-12 - stdlib grader, gh prerequisite` | None | None for this condition; no global waiver. |
| A34 | Yes - File access/loading | adapt - source paths, shipment and actual access separate | Unresolved runtime/history | `SKILL.md:51,62,74-75 - references present and shipped; fixture paper inputs exist` | None | Source presence does not establish installed or native access. |
| A35 | No - No specific MCP server/tool identifier is named. | not applicable - No specific MCP server/tool identifier is named. | Not applicable | `SKILL.md:1-104; references/pr.md:22 - gh CLI, no MCP ID` | None | None for this condition; no global waiver. |
| A36 | Yes - Tool/helper prerequisites | adopt | Satisfied statically | `SKILL.md:38-46; references/pr.md:7-12 - repo/identity/state/gh/auth prerequisites` | None | Native behavior not inferred from source. |
| S01 | Yes - Purpose/trust boundaries | adopt | Partially evidenced | `SKILL.md:8,17,53-60 - single current scope/no history rewrite/generated gate` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S02 | Yes - File/network/tool access | adopt | Partially evidenced | `SKILL.md:64-75; references/pr.md:16-25 - scoped git mutation and explicit network publication` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S03 | Yes - Potential sensitive context | adopt | Satisfied statically | `SKILL.md:59-60 - local state/traces/storage/screenshots excluded unless explicit` | None | Explicit local/sensitive-artifact gate exists; actual staging/approval untested. |
| S04 | Yes - External/dependency authority | adopt | Partially evidenced | `SKILL.md:21 - conversation governs scope; no fetched external instruction` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| R01 | Yes - Protected identity/intent | adopt | Satisfied statically | `SKILL.md:2-3,8,17 - name/trigger/single-commit protected` | None | Native behavior not inferred from source. |
| R02 | No - No invocation-disable/sidecar control exists to preserve. | not applicable - No invocation-disable/sidecar control exists to preserve. | Not applicable | `SKILL.md:1-4 - no invocation-disable or sidecar control` | None | None for this condition; no global waiver. |
| R03 | Yes - Approval/autonomy | adopt | Unresolved protected dry-run boundary | `SKILL.md:53-60,73; references/pr.md:3 - approval scope and publication` | EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| R04 | Yes - Required dependencies | adopt | Satisfied statically | `references/pr.md:9-12; SKILL.md:51,62,74-75 - git/gh/direct resources, no mandatory helper skill call` | None | Native behavior not inferred from source. |
| R05 | Yes - Stops/handoff | adopt | Unresolved protected dry-run boundary | `SKILL.md:38-46,58,60 - blocker/ambiguous/generated stops` | EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| R06 | Yes - Required outputs | adopt | Unresolved protected dry-run boundary | `SKILL.md:77-82; references/pr.md:29-33 - final commit and default PR identity` | EH-002 (observation); EH-009; EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| R07 | Yes - Repository authority | adopt | Satisfied statically for audit boundary | `SKILL.md:21,53-60 - chosen repository scope; no authority to edit protected docs` | None | Parent owns canonical doc maintenance; dependent helper writes remain subject to repo authority. |
| R08 | Yes - Benchmark/source separation | adopt | Satisfied statically | `evals/grade_benchmark.py:267,275-285 - sibling iteration/run grading; four fixtures separate` | None | Native behavior not inferred from source. |
| R09 | Yes - Scoped verification prerequisites | adopt | Partially evidenced | `SKILL.md:94-104; references/pr.md:7-12 - final source rules/gh checks` | None | Scoped source verification rules read; audited commands/validators deliberately not run. |
| R10 | No - No Upgrade procedure or dependency in this bounded scope. | not applicable - No Upgrade procedure or dependency in this bounded scope. | Not applicable | `SKILL.md:1-104 - no Upgrade procedure/dependency in scope` | None | None for this condition; no global waiver. |
| R11 | Yes - Evidence/grading claims | adapt - source/artifact/trace grades separate; unknown protocol pending | Defective grader; unresolved dry-run boundary | `evals/grade_benchmark.py:94-115,196-199,275-288 - unknown metrics/default oracle/protocol` | EH-009; SAG-008/DD-004 (proposed additions); EH-010 | Early inspection/mutation/final-SHA dry-run contract requires human choice. |
| R12 | Yes - Scoped source formatting | adopt | Satisfied statically | `SKILL.md:1-104; references/*.md; evals/* - byte scan LF/no trailing whitespace/tabs` | None | Native behavior not inferred from source. |
| C01 | Yes - Native discovery/activation | adapt - native discovery/activation; replay is supplementary | Unresolved runtime/history | `SKILL.md:2-3 - portable metadata, no runtime activation trace` | None | Explicit/implicit native activation not tested. |
| C02 | Yes - Published resource selection | adapt - installer selection then actual client access | Satisfied selection source | `scripts/install.sh:40-55; scripts/install.ps1:251-276; SKILL.md:51,62,74-75 - five files ship, two eval/four fixtures pruned` | None | Installed resource access/loader behavior untested; evals/fixtures are repository-only. |
| C03 | No - Core portable metadata only; no client-specific adapter field. | not applicable - Core portable metadata only; no client-specific adapter field. | Not applicable | `SKILL.md:1-4 - portable metadata, no adapter-required claim` | None | None for this condition; no global waiver. |
| C04 | Yes - Tool/activation consent | adapt - activation consent separate from tool permission | Unresolved runtime/history | `SKILL.md:53-60,73; references/pr.md:3 - tool consent and explicit push/PR boundary` | None | Actual sandbox/tool consent enforcement untested. |


### handoff matrix

Source prefix: `skills/handoff/`. `local exec-plans` / `exec-plans` denotes `.agents/skills/exec-plans/SKILL.md`, and other named helper paths denote their existing `skills/<helper>/` source. Installer selection always denotes `scripts/install.sh:40-55` and `scripts/install.ps1:251-276`. Missing fixture anchors point to declarations, not nonexistent source lines.

| ID | Applicability | Adoption disposition | Current compliance | Evidence/source anchor | Findings | Unresolved gap |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Yes - All instructions | adopt | Satisfied statically | `SKILL.md:14-19,58-62 - compact active context, no raw chat/log dump` | None | Native behavior not inferred from source. |
| A02 | Yes - Workflow risk/variation | adopt | Satisfied statically | `SKILL.md:21-39 - precise path/update/redaction/error behavior` | None | Native behavior not inferred from source. |
| A03 | Yes - Intended native model coverage | adapt - approved native seven-model medium matrix | Unresolved runtime/history | `SKILL.md:3,21-44 - trigger/order/path/stop behavior needs matrix` | None | No native seven-model medium-effort cases/repetitions. |
| A04-F | Yes - Required entry/YAML | adopt | Satisfied statically | `SKILL.md:1-4 - parsed metadata mapping` | None | Native behavior not inferred from source. |
| A04-N | Yes - Required client name constraint | adapt - VS Code directory/64-character rule; no Claude reserved-word transfer | Satisfied statically | `SKILL.md:2 - directory match, lowercase name, 7 characters` | None | Native behavior not inferred from source. |
| A04-D | Yes - Required nonempty description | adapt - required nonempty string; Claude 1024/XML bounds not universal | Satisfied statically | `SKILL.md:3 - nonempty 389-character description` | None | Native behavior not inferred from source. |
| A05 | Yes - Every skill identity | adopt | Satisfied statically | `SKILL.md:2,10 - existing handoff name and resume-ready purpose` | None | Native behavior not inferred from source. |
| A06 | Yes - Every discovery description | adopt | Satisfied statically | `SKILL.md:3 - literal and broader resume/read/check triggers` | None | Native behavior not inferred from source. |
| A07 | Yes - Entry-body focus | adapt - inspect focus; 500 lines advisory | Satisfied statically | `SKILL.md:1-97 - compact body with controls in main entry` | None | Native behavior not inferred from source. |
| A08 | Yes - Entry/resource loading | adapt - conditional source navigation; client preloading unverified | Satisfied statically | `SKILL.md:14-19 - read only relevant artifacts, no supplemental runtime reference` | None | Native behavior not inferred from source. |
| A09 | No - No optional advanced resource/feature branch. | not applicable - No optional advanced resource/feature branch. | Not applicable | `SKILL.md:1-97 - no separate advanced feature resource` | None | None for this condition; no global waiver. |
| A10 | No - No bundled runtime reference navigation. | not applicable - No bundled runtime reference navigation. | Not applicable | `SKILL.md:1-97 - no bundled runtime references` | None | None for this condition; no global waiver. |
| A11 | No - No bundled runtime reference. | not applicable - No bundled runtime reference. | Not applicable | `SKILL.md:1-97 - no reference over 100 lines` | None | None for this condition; no global waiver. |
| A12 | Yes - Documented paths | adopt | Defective evaluation evidence | `SKILL.md:23-26; evals/evals.json:11,62 - named/default paths and missing log fixtures` | EH-003; EH-004 | Named-path oracle disagrees with current rule; two declared logs absent; native behavior untested. |
| A13 | Yes - Multi-step workflow | adopt | Satisfied statically | `SKILL.md:14-44 - gather/path/update/report sequence` | None | Native behavior not inferred from source. |
| A14 | Yes - Quality-sensitive output | adopt | Satisfied statically | `SKILL.md:30-32,85-97 - stale cleanup/reread/final verification` | None | Native behavior not inferred from source. |
| A15 | No - No dated provider/version guidance or legacy procedure; session dates are evidence. | not applicable - No dated provider/version guidance or legacy procedure; session dates are evidence. | Not applicable | `SKILL.md:18,30-31 - current state and inherited next step replace stale content` | None | None for this condition; no global waiver. |
| A16 | Yes - Entry/resources terminology | adopt | Satisfied statically | `SKILL.md:24-26,42-44 - root/feature scope terms; eval fallback disagrees` | EH-003 | Native behavior not inferred from source. |
| A17 | Yes - Structured output | adopt | Satisfied statically | `SKILL.md:33,41-44 - flexible body default, required path/scope/next-step report` | EH-003 | Native behavior not inferred from source. |
| A18 | Yes - Output-shape examples | adopt | Satisfied statically | `evals/files/feature-update-fixture/.agents/scratchpad/payments/handoff.md:1-10 - stale input example, not final template` | None | Native behavior not inferred from source. |
| A19 | Yes - Conditional methods | adopt | Satisfied statically | `SKILL.md:23-26,30-39 - named/default/invalid/update/write-failure branches` | EH-003 | Native behavior not inferred from source. |
| A20 | Yes - Defaults/exceptions | adopt | Satisfied statically | `SKILL.md:23-26 - explicit path first, then single feature, then root` | EH-003 | Native behavior not inferred from source. |
| A21 | Yes - Baseline/evaluation claims | adapt - unchanged native diagnostic baseline before candidate comparison | Unresolved runtime/history | `evals/evals.json:3-82 - three artifact cases, no matched native baseline` | None | No matched current-skill baseline in reviewed maintained resources; generated histories excluded. |
| A22 | Yes - Observable evaluation evidence | adapt - artifact predicates separate from native workflow traces | Defective evaluation evidence | `evals/grade_benchmark.py:114-239 - path/content/redaction artifact predicates` | EH-003; EH-004 | Named-path oracle disagrees with current rule; two declared logs absent; native behavior untested. |
| A23 | Yes - Reusable real-work knowledge | adopt | Satisfied statically | `SKILL.md:15-18,35,51-54,95 - durable mistakes/corrections/workarounds` | None | Native behavior not inferred from source. |
| A24 | Yes - Fresh-session behavior | adapt - fresh native sessions and fixture state | Unresolved runtime/history | `evals/evals.json:6,32,58 - copied artifact fixtures, no native fresh session` | None | Fresh using-session traces and task outcomes absent. |
| A25 | Conditional - team use unestablished | adopt | Unresolved history | `SKILL.md:15-16,35,95 - human corrections retained; usage history absent` | None | No independently verified team-use/feedback history supplied. |
| A26 | Yes - Observed retrieval/activation | adapt - trace required reads/activation; metadata is not observation | Unresolved runtime/history | `SKILL.md:3,19,32 - before-tool/relevant read/reread mandates, no trace proof` | None | No trace establishes resource reads, activation or ordering. |
| A27 | Yes - Bundled executable error handling | adopt | Partially evidenced | `evals/grade_benchmark.py:13-29,86-98,262-273 - JSON shape/skip/no-run protocol incomplete` | DD-004 (proposed addition) | Wrong JSON shape and empty/skipped run outcomes need existing DD-004 protocol decision. |
| A28 | Yes - Script constants | adopt | Partially evidenced | `evals/grade_benchmark.py:228-230 - 90-line heuristic has no documented source rationale` | EH-003 (heuristic context) | 90-line eval heuristic is not a production limit; retrieval impact unobserved. |
| A29 | Yes - Repeated deterministic operations | adopt | Satisfied statically | `evals/grade_benchmark.py:101-111,114-239 - reusable lexical/path checks` | None | Deterministic source utility/command reuse inspected; usefulness/runtime performance unmeasured. |
| A30 | Yes - Bundled script use contract | adapt - repository eval CLI usage; not published runtime | Satisfied statically | `evals/grade_benchmark.py:252-273 - iteration CLI and grading.json output` | None | CLI usage/output documented; no target utility executed. |
| A31 | No - No layout/spatial source input requiring visual analysis. | not applicable - No layout/spatial source input requiring visual analysis. | Not applicable | `SKILL.md:37,62 - reference artifacts; no layout/spatial input requirement` | None | None for this condition; no global waiver. |
| A32 | Yes - Complex/risky operations | adopt | Satisfied statically | `SKILL.md:21-32 - choose path and reread existing section before writes` | None | Native behavior not inferred from source. |
| A33 | No - No external package dependency in owned executable resources; host tools are A36. | not applicable - No external package dependency in owned executable resources; host tools are A36. | Not applicable | `evals/grade_benchmark.py:3-6 - standard-library imports only` | None | None for this condition; no global waiver. |
| A34 | Yes - File access/loading | adapt - source paths, shipment and actual access separate | Unresolved runtime/history | `evals/evals.json:11,62 - two missing declared logs; hidden feature fixture exists` | EH-004 | Source presence does not establish installed or native access. |
| A35 | No - No specific MCP server/tool identifier is named. | not applicable - No specific MCP server/tool identifier is named. | Not applicable | `SKILL.md:1-97; evals/grade_benchmark.py:3-6 - no MCP server/tool ID` | None | None for this condition; no global waiver. |
| A36 | Yes - Tool/helper prerequisites | adopt | Satisfied statically | `SKILL.md:29,32,39 - file read/write required; write-failure fallback explicit` | EH-004 | Native behavior not inferred from source. |
| S01 | Yes - Purpose/trust boundaries | adopt | Partially evidenced | `SKILL.md:10,14-19,38 - resume purpose and redacted active-context boundary` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S02 | Yes - File/network/tool access | adopt | Partially evidenced | `SKILL.md:23-39 - explicit path-targeted file read/write, no network requirement` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| S03 | Yes - Potential sensitive context | adopt | Satisfied statically | `SKILL.md:38; evals/grade_benchmark.py:140,228 - redact secrets/PII; synthetic-token checks limited` | None | Redaction source rule and narrow synthetic checks do not prove all outputs safe. |
| S04 | Yes - External/dependency authority | adopt | Partially evidenced | `SKILL.md:16,19,37 - source artifacts inform context, no remote instruction fetch` | None | Operations fit stated purpose in inspected source; trust/permission behavior is untested. |
| R01 | Yes - Protected identity/intent | adopt | Satisfied statically | `SKILL.md:2-3,10 - stable name and broad read/resume triggers retained` | None | Native behavior not inferred from source. |
| R02 | No - No invocation-disable/sidecar control exists to preserve. | not applicable - No invocation-disable/sidecar control exists to preserve. | Not applicable | `SKILL.md:1-4 - no invocation-disable or sidecar control` | None | None for this condition; no global waiver. |
| R03 | Yes - Approval/autonomy | adopt | Satisfied statically | `SKILL.md:23,31-39 - named destination/update/error boundary` | None | Native behavior not inferred from source. |
| R04 | Yes - Required dependencies | adopt | Satisfied statically | `SKILL.md:14-19,32 - contextual artifacts/read tools, no required helper skill` | None | Native behavior not inferred from source. |
| R05 | Yes - Stops/handoff | adopt | Satisfied statically | `SKILL.md:3,31,39 - before-stop update/inherited-next-step/error fallback` | EH-003; EH-004 | Native behavior not inferred from source. |
| R06 | Yes - Required outputs | adopt | Defective evaluation evidence | `SKILL.md:21-26,41-44 - chosen path and scope/next-step identity` | EH-003 | Named-path oracle disagrees with current rule; two declared logs absent; native behavior untested. |
| R07 | Yes - Repository authority | adopt | Satisfied statically for audit boundary | `.agents/instructions/repo.md:10-14; SKILL.md:23 - active docs/promoted handoff override` | None | Parent owns canonical doc maintenance; dependent helper writes remain subject to repo authority. |
| R08 | Yes - Benchmark/source separation | adopt | Satisfied statically | `evals/grade_benchmark.py:254,262-270 - sibling iteration/run grading; 13 fixtures separate` | None | Native behavior not inferred from source. |
| R09 | Yes - Scoped verification prerequisites | adopt | Partially evidenced | `SKILL.md:85-97 - final checklist with evidence/error/secret rules` | None | Scoped source verification rules read; audited commands/validators deliberately not run. |
| R10 | No - No Upgrade procedure or dependency in this bounded scope. | not applicable - No Upgrade procedure or dependency in this bounded scope. | Not applicable | `SKILL.md:1-97 - no Upgrade procedure/dependency in scope` | None | None for this condition; no global waiver. |
| R11 | Yes - Evidence/grading claims | adapt - source/artifact/trace grades separate; unknown protocol pending | Defective evaluation evidence | `evals/grade_benchmark.py:50-71,114-239,262-273 - metrics/artifact/protocol limitations` | EH-003; EH-004; SAG-008/DD-004 (proposed additions) | Named-path oracle disagrees with current rule; two declared logs absent; native behavior untested. |
| R12 | Yes - Scoped source formatting | adopt | Satisfied statically | `SKILL.md:1-97; evals/* - byte scan LF/no trailing whitespace/tabs` | None | Native behavior not inferred from source. |
| C01 | Yes - Native discovery/activation | adapt - native discovery/activation; replay is supplementary | Unresolved runtime/history | `SKILL.md:3 - broad metadata trigger only; activation/order untested` | None | Explicit/implicit native activation not tested. |
| C02 | Yes - Published resource selection | adapt - installer selection then actual client access | Satisfied selection source | `scripts/install.sh:40-55; scripts/install.ps1:251-276 - one entry ships; two eval/13 fixture files pruned` | EH-004 (repo fixture only) | Installed resource access/loader behavior untested; evals/fixtures are repository-only. |
| C03 | No - Core portable metadata only; no client-specific adapter field. | not applicable - Core portable metadata only; no client-specific adapter field. | Not applicable | `SKILL.md:1-4 - portable metadata, no client-specific adapter` | None | None for this condition; no global waiver. |
| C04 | Yes - Tool/activation consent | adapt - activation consent separate from tool permission | Unresolved runtime/history | `SKILL.md:23,29,38-39 - path intent/redaction/fallback do not grant tool permissions` | None | Actual sandbox/tool consent enforcement untested. |

## Bounded dependency fingerprints

Whole-file hashes identify bytes; read-scope bounds content inspection. No imported dependency becomes primary audit scope.

| Dependency | SHA256 | Read scope / owner |
| --- | --- | --- |
| `skills/delegate-to-subagents/SKILL.md` | `670318c390b55da662f617e2e1d2538da299f4f151b3c82f03bb9443ffa9ef32` | 1-100,155-250; required routing/approval/replacement consumer; Delegation owner |
| `skills/self-improve/SKILL.md` | `cf3899133effb2ee23b51a3767136fa9af122b78f490191a0391c7c0d244c115` | 1-50; delayed durable-learning consumer; Authoring owner |
| `.agents/skills/exec-plans/SKILL.md` | `c9819fd42e17879fee33e0b7546b98b07b8088f0f6334b9966b180689490693c` | full; required living-plan consumer; Local Workflows owner |
| `skills/tdd/SKILL.md` | `7c09709d9a8ebea6c3286c14d7ba25ee0957de08d8d9a921752177a4640ac5c0` | 1-38; mandatory consumer/seam/refactor gate only; excluded import |
| `skills/spec-to-tasks/references/task-schema.md` | `e31db92fce84622fd0dcb54eccf5309d809ba6f6c3a47df4e7f4c6b41435cf88` | 1-56; tasks-to-Ralph fields; Requirements owner |
| `scripts/install.sh` | `a7cd93792b919a2773c8a79061359dc54d023381024e5a47d6be0a6f3d5e35fa` | 35-75; skill selection/pruning only |
| `scripts/install.ps1` | `9b4b245ceae22c533f26c87f6a0bf86ab150b7174a77881dbfab658e8ee2b022` | 245-282; skill selection/pruning only |
| `.editorconfig` | `a50eaf42f688b51cc2c008c7288b9dc26030a38462ee033d5b0b5d3477ec1ce2` | full; formatting contract |
| `skills/skill-creator/SKILL.md` | `c6815e8017fc4be2813271b005b035cea173c8be603bc949e0a3082942e5ecd3` | 135-280 plus authoring anatomy context; imported assessment helper, not primary audit |

## Checkpoint-only supporting audit records

These hashes identify this read checkpoint. Parent-owned audit/canonical records can change later; these are neither source-baseline nor behavioral snapshots. Prior report is navigation/format only, not source truth.

| Record | SHA256 |
| --- | --- |
| `.agents/memory/INDEX.md` | `af22f36d840527d0b09b7751d72efdef63a6386dfed760243b1aecbbe651fde5` |
| `.agents/memory/ARCHITECTURE.md` | `18adb924fd5172cda1833172916cbbb5fccc254c55fc829e7f2babc23094f55c` |
| `.agents/memory/CONVENTIONS.md` | `a6da962bc0127e428f76576c7de91bb6b7190c8ae4bbc0edaa33ccec89588bde` |
| `.agents/instructions/repo.md` | `5f658f2ce9f9c97b8581d683e21ce3339f5ef61996ed1c92826ace671e69c132` |
| `.agents/instructions/skills.md` | `9dbb3ff52bb5fa630d9825efce0682bedbd3aab890e0387d7a44f80f84435a14` |
| `.agents/memory/known-issues/skills.md` | `806bc51b3fb40893f977e2428d1d9d79a432687d29231fb58defca9f53a7a1da` |
| `.agents/memory/testing/skills.md` | `b76425b2bce06122e0eba6c06626354cf089a60ca3549bf1f0c626dbcf2f0e92` |
| `docs/skill-audit/tickets/review-execution-and-handoff.md` | `fcb87ed23cebede0f5561b26bc7a919281ffce95e8afa7719f7b2a4794a232b9` |
| `docs/skill-audit/tickets/choose-audit-batches-and-evidence-format.md` | `83a446f1463e03550193e8636d3ee48309a30988615e50bdb7baf3df149b9105` |
| `docs/skill-audit/tickets/set-adoption-rules-and-protected-behavior.md` | `4850b02b3acc5b7041e3092286398aac52a724b634647eab597922ed6d3ae10d` |
| `docs/skill-audit/tickets/set-audit-evidence-and-model-coverage.md` | `e22ffbf2d4d271b23b1ccf8f73203df04bd0894afbff9a4a6bebc84780f446b8` |
| `docs/skill-audit/tickets/set-audit-completion-and-implementation-gates.md` | `151493967cbc1878d9801aa161c2b96325d2bfb41cfb2dafc4f54f3a47c563fe` |
| `docs/skill-audit/coverage.md` | `984cf11c54594e912077408d17cb6093fcd8f576212ede0e0b2921509def3697` |
| `docs/skill-audit/findings.md` | `6db6b91082ce5f10bba5a80b7067719b8e1162929a36c9249959e66176d0fe46` |
| `docs/skill-audit/research/authoring-checklist/findings.md` | `c865605d8784066cec68c1d193020038750fe461d9df03d7a720e559a729d560` |
| `docs/skill-audit/research/provider-compatibility/findings.md` | `fd2c4a71fed2244fc51123c830c4a52f023d0475fdd9bd3b91edfd69d42ff24a` |
| `docs/skill-audit/reports/review-requirements-and-task-planning.md` | `34a320581d9691aff071573a05d4047cbcace0607ba068646e4d4fe816731522` |

## Loaded assessment skills, separate from baseline

These installed instructions governed this audit session. They are not the audited source baseline, are not imported primary scope, and were not used to execute target procedures. Grilling supplies the later human decision boundary; Create Skill and Skill Creator supply authoring/evaluation assessment. The actual human review remains pending.

| Installed skill path | SHA256 | Load scope |
| --- | --- | --- |
| `/Users/adam/.agents/skills/handoff/SKILL.md` | `092e757cf8c2470c57bc01d1c3cbbea8777e9fc528c71a351cfe99cf45c8caf5` | Entry instruction read; assessment only |
| `/Users/adam/.agents/skills/grilling/SKILL.md` | `ccf2607fc8d62a7300197d9ab16ba4a83943f81165f5caee2d3eeb30fa779291` | Entry instruction read; assessment only |
| `/Users/adam/.agents/skills/create-skill/SKILL.md` | `d623cc5ea5579b552b1cc92786ceacbcaa2f6b2dce14e3a78df577656029dca2` | Entry instruction read; assessment only |
| `/Users/adam/.agents/skills/skill-creator/SKILL.md` | `c6815e8017fc4be2813271b005b035cea173c8be603bc949e0a3082942e5ecd3` | Entry instruction read; assessment only |

## Verification and remaining evidence

- Verified recursive dot-directory-aware enumeration, 22 primary/20 fixture SHA256 fingerprints and byte identity against source baseline. Sixteen non-eval files are selected for shipment; six eval resources and all twenty existing fixtures are pruned by both inspected installer routines. Two declared Handoff logs remain absent rather than receiving fabricated hashes.
- Verified five parsed YAML entry mappings, portable directory/name syntax, required string descriptions, three valid eval JSON documents, three Python grader ASTs and six Python fixture ASTs. Parsing is not importing or executing these procedures. No target formatter/validator/packager or build/test/application command ran.
- Verified five matrices, exactly 58 catalog IDs each in order and seven columns, for 290 rows. Report text has no em dash, trailing whitespace or blank-line whitespace. Canonical doc maintenance and git mutations remain parent-owned and were not performed by this worker.
- Ten registered findings remain pending human dispositions. EH-001/EH-003/EH-004/EH-009 concern exact paper oracle/fixture evidence; EH-002 is an observation about default-title coverage behind a valid explicit override. EH-005/EH-006/EH-007/EH-008/EH-010 retain precise counting, dependency, validation and mutation-authority decisions. No proposed redesign is accepted or implemented.
- Native activation, required loads, real task execution, worker/replacement counting, approval/tool containment, commit/staging/publication, browser verification, plan integration and handoff write-failure behavior are untested. Safe current-contract fixtures, competing installed copies, user-request overrides and future source/trace/artifact grading require later design and evidence. Existing paper graders cannot substitute for native proof.
- Bounded dependency investigation is complete for this assigned report, not proof of repository-wide dependency closure. All cross-skill/shared proposed scope additions require parent reconciliation and human disposition; exactly three metric producers and three protocol targets were proposed, never approved here. No audit sample or evidence waiver was selected.
- Audit tooling friction: Tool Guardian rejected an oversized initial shell payload and a 77KB matrix patch before mutation. Shorter report writes and two bounded matrix patches succeeded. This is a tooling-input limit encountered during evidence authoring, not an audited skill failure or outstanding blocker.

Reviewer handback: report ownership was released to the parent after structural verification. No other file was changed by this worker. The sections below record later parent reconciliation and verification separately.

## Parent reconciliation and dispatch evidence

The parent registered EH-001 through EH-010 in the single findings register and created five exact behavior routes, each blocked by the unclosed batch. Coverage distinguishes 32 completed static investigations from 27 completed human reviews, five pending human reviews and five unstarted candidates. The 47 registered findings include 37 earlier human dispositions and ten pending findings. The proposed three grader additions do not change the accepted nine metric producers or six protocol graders before live review. No behavior, protocol, fixture/oracle identity, implementation, evidence waiver or residual risk was approved during source reconciliation.

The final reviewer handback before parent edits had SHA256 `bbcbe89357809da95065f8807f99942beb87c424beebca3d37179fd44d6d1c51`. This checkpoint identity is distinct from the current reconciled report and unchanged audited source hashes. Parent reconciliation retained the valid higher-priority PR-title override: EH-002 is an observation about absent default coverage, not a proven native instruction violation. EH-009 independently owns the concrete unrelated-source predicate defect. Fixture and matrix table widths were verified after repairing a missing pipe in a reviewer checkpoint.

```yaml
subtask_id: execution_handoff_static
agent: /root/execution_handoff_static
selection_basis: provisional Premium for cross-file approval, retry, integration and evidence risks
selected:
  model: gpt-6.1-sol
  reasoning_effort: high
submitted:
  model: gpt-6.1-sol
  reasoning_effort: high
executed:
  model: unconfirmed
  reasoning_effort: unconfirmed
fallback:
  model: gpt-6-sol
  reasoning_effort: high
  used: false
routing_compliant: true
status: completed
initial_clock_bound: 2026-10-06 23:45:30 UTC
initial_limit_minutes: 20
initial_deadline: 2026-10-07 00:05:30 UTC
checkpoint_minutes: 5
initial_saved_checkpoint_read: 2026-10-06 23:46:50 UTC
source_checkpoint_read: 2026-10-06 23:50:01 UTC
five_minute_status_observed: 2026-10-06 23:50:43 UTC
five_minute_status: running; saved inventory and mechanisms inspected; matrices underway
ten_minute_status_observed: 2026-10-06 23:56:00 UTC
ten_minute_status: running; saved candidate and matrix checkpoint inspected
completion_observed: 2026-10-06 23:59:22 UTC
ownership_released: true
interruption: false
replacement: false
extension: false
usage: unconfirmed
```

The clock bound was recorded after dispatch, not as an exact start time. Five- and ten-minute status observations occurred thirteen and thirty seconds after their nominal checkpoints. Saved progress was usable and inspected. Completion was observed before the initial deadline; exact completion time is unconfirmed. Runtime model/effort and usage were not independently reported, so selection and submission are not execution evidence. Routing metadata stayed outside the task prompt. No exact dollar or runtime-cost claim is made. The native seven-model matrix is separate and remains unrun.

Parent verification uses an inspectable temporary script outside the repository. An initial inline command was rejected by Tool Guardian before execution; replacing it with the saved script resolved that tooling limitation. Supporting checkpoint hashes were separated from immutable source hashes, and inventory classification follows each report's declared primary/fixture sections. Those checker corrections preserve source-byte and per-check assertions; they are not target behavior failures or waived checks.

## Parent verification and canonical documentation pass

`rtk proxy python3 /private/tmp/skill-audit-verify-execution.py` passed unchanged 22 primary/twenty fixture/nine bounded dependency hashes, ten JSON/nine AST parses, five ordered 58-row seven-column matrices, aggregate six-report inventories, the acyclic 41-ticket graph (twelve closed/twenty-eight open/one claim), sixteen unblocked earlier routes/five blocked proposed routes, 47 unique owning findings (37 prior dispositions/ten pending), exact accepted nine/six grader targets, 27 human-reviewed/five pending/five unstarted candidates, and twelve authorized documentation paths with valid links, anchors, whitespace, fog and protected-source boundaries. The mixed prior finding formats were parsed by their actual table columns and severity-bearing fields; no assertion or audited check was dropped. A blank line splitting the findings index was removed before the successful rerun.

`rtk proxy python3 /private/tmp/skill-audit-verify-dependencies-and-git.py` passed its five previously bounded source dependency hashes and clean merge/rebase/cherry-pick/revert operation-state checks. These inspectable temporary verification scripts are outside the repository; no target grader, validator, native client or baseline ran.

The formal Update Agent Docs pass added three focused contract-issue pointers for Ralph/TDD, Execplan integration/supply and Commit dry run, and refreshed the existing grader-integrity pointer. `.agents/memory/known-issues/skills.md` is the only canonical changed path, derived type Known Issue. Existing INDEX/FILE_MAP/instruction routing covers this effort; no new canonical file, API, test-strategy, source-skill or routing change is needed. OKF loaded only the shared profile branch; `rtk proxy ./scripts/lint-okf.py` exited 0 across both bundles. The scoped canonical diff contains exactly the authorized known-issues file. Added: three focused issue pointers. Changed: grader-integrity pointer. Split or moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.
