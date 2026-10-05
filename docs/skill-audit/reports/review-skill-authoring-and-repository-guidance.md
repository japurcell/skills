# Review Skill Authoring and Repository Guidance

Static investigation and human proposal review complete. Source revision: `91ba7ab941450327c8d178c27966d1150bd0b74b`. No skill workflow, installer, imported refresh, grader, native skill-evaluation run, benchmark, or behavioral test has been executed. Four separate decisions remain pending; accepted repairs are later plan scope only.

## Scope and evidence limits

Six primary skills: `create-skill`, `improve-skill`, `agents-md-improver`, `create-agentsmd`, `guidance-review`, `self-improve`. Every file below is maintained bundle source or a static eval/fixture input. Fixture entry points are evidence only. Snapshots, generated outputs/workspaces, imported bundles, and external sites are not primary targets. Hashes describe current working-tree bytes, not a behavioral baseline. All maintained source and fixture files have been read; all six catalog matrices are complete.

## Reviewed-file inventory

The six bundles contain 45 reviewed files. All are accounted for with SHA256 below. The source revision applies to each inventory record. Fixture SKILL/AGENTS files remain evidence only.

| File | SHA256 | Evidence role | Review state |
| --- | --- | --- | --- |
| [skills/create-skill/SKILL.md](../../../skills/create-skill/SKILL.md) | `d623cc5ea5579b552b1cc92786ceacbcaa2f6b2dce14e3a78df577656029dca2` | maintained entry/resource | read |
| [skills/create-skill/evals/evals.json](../../../skills/create-skill/evals/evals.json) | `9a1bb79a78d3a5a66f9653e6ba030b0a4b7134f3bb217b47c12f2439fe107405` | static eval definition/utility | read |
| [skills/create-skill/evals/files/plan-maker-request.md](../../../skills/create-skill/evals/files/plan-maker-request.md) | `1eb489e1151386fd857ebe06dd2c6a3b81b34d77718cb434573d9fa4e4580ec5` | fixture | read |
| [skills/create-skill/evals/files/release-notes-brief.md](../../../skills/create-skill/evals/files/release-notes-brief.md) | `34deaa7d04e0df9a280a9aff5e704aeefb3ddede33b2c6805be56088904aae4e` | fixture | read |
| [skills/create-skill/evals/files/review-handoff-draft/SKILL.md](../../../skills/create-skill/evals/files/review-handoff-draft/SKILL.md) | `7aff1500bd82617a5c4bc8d1e9b11e80b686ef735a48012d4f8107dca36a98c1` | fixture | read |
| [skills/create-skill/evals/files/task-wave-draft/SKILL.md](../../../skills/create-skill/evals/files/task-wave-draft/SKILL.md) | `f7cd954b7c76aef2dfee9ce73cc480bef86ccb2a091cd4ed206755d514203e46` | fixture | read |
| [skills/create-skill/evals/grade_benchmark.py](../../../skills/create-skill/evals/grade_benchmark.py) | `979e481d07fdd2a40180d1a4c658efa474a6d93bd6d950d2b1f1f4e4c8654b73` | static eval definition/utility | read |
| [skills/improve-skill/SKILL.md](../../../skills/improve-skill/SKILL.md) | `09f3463e21c07d695cb11fbbd80537d7d872727ab3228990d8003a949c510bd6` | maintained entry/resource | read |
| [skills/improve-skill/evals/evals.json](../../../skills/improve-skill/evals/evals.json) | `2feaa5f6cb5a697bb5ed7b8e0624a30246c90782ffe7673fa6e6ec188b9745b6` | static eval definition/utility | read |
| [skills/improve-skill/evals/grade_benchmark.py](../../../skills/improve-skill/evals/grade_benchmark.py) | `999225ac433b8cef5e165184d267d66aa94a61ccf41e4df9d60ecbba755c5d83` | static eval definition/utility | read |
| [skills/agents-md-improver/SKILL.md](../../../skills/agents-md-improver/SKILL.md) | `219cc5fd29347e8aad68eba0d07022e1c641db6711b32d28d079cd0453e1c037` | maintained entry/resource | read |
| [skills/agents-md-improver/references/quality-criteria.md](../../../skills/agents-md-improver/references/quality-criteria.md) | `9c875355ba2f5c938487f2f3349d2bafb9f2c1da8f958ffcee6dd9c8861c1d7e` | maintained entry/resource | read |
| [skills/agents-md-improver/references/templates.md](../../../skills/agents-md-improver/references/templates.md) | `d14185555d8bd1a0e88ad4597096b4eb0f4ef8ce663fec47c25174fff8f28a43` | maintained entry/resource | read |
| [skills/agents-md-improver/references/update-guidelines.md](../../../skills/agents-md-improver/references/update-guidelines.md) | `b4a0f947ef82fd68d72b39b0b2b98e0bd1cf0b2821c1f8928bca512d6ef8538e` | maintained entry/resource | read |
| [skills/create-agentsmd/SKILL.md](../../../skills/create-agentsmd/SKILL.md) | `4bde38e95db200857e709a57cb2a6b526018c75c4a203a080b207490ffd97e93` | maintained entry/resource | read |
| [skills/create-agentsmd/agents/openai.yaml](../../../skills/create-agentsmd/agents/openai.yaml) | `669950ec5acef448d6a6883f017ba18a402b19624e978fe336cea03adc42cb9b` | maintained entry/resource | read |
| [skills/guidance-review/SKILL.md](../../../skills/guidance-review/SKILL.md) | `30c3994ca6f014843d961719d8be7d944a8ea30f534475e3434de6ad2dc2a6d9` | maintained entry/resource | read |
| [skills/guidance-review/agents/openai.yaml](../../../skills/guidance-review/agents/openai.yaml) | `a1499d95abd8447558c535fe5554adcc3c9b988a0a39264a6283d430effe1e94` | maintained entry/resource | read |
| [skills/self-improve/DURABLE_LEARNINGS.md](../../../skills/self-improve/DURABLE_LEARNINGS.md) | `938ba49f3ec62b56b2f01f90090d45d36e342f4127e323e7aa2a507a006372b8` | maintained entry/resource | read |
| [skills/self-improve/INSTRUCTION_STRUCTURE.md](../../../skills/self-improve/INSTRUCTION_STRUCTURE.md) | `11a2a82b23effdf2474616a81dcf1b95537037414ac6daf400b163336c65138f` | maintained entry/resource | read |
| [skills/self-improve/SKILL.md](../../../skills/self-improve/SKILL.md) | `cf3899133effb2ee23b51a3767136fa9af122b78f490191a0391c7c0d244c115` | maintained entry/resource | read |
| [skills/self-improve/evals/evals.json](../../../skills/self-improve/evals/evals.json) | `10d3c2f5799e0680303d4877240d28e50e7ada1fe9df7146cc7ea1e63c0e8558` | static eval definition/utility | read |
| [skills/self-improve/evals/files/create-root-fixture/deploy/service.yml](../../../skills/self-improve/evals/files/create-root-fixture/deploy/service.yml) | `8f9b1f922b0e11563e46a1d115cbdbc7237bb63179d3a9aecb3bbdd85bd28069` | fixture | read |
| [skills/self-improve/evals/files/create-root-fixture/scripts/check-config.py](../../../skills/self-improve/evals/files/create-root-fixture/scripts/check-config.py) | `29a2293851db063c261c7eb71668bd4faf99d7132f9399d4f3b07bd167150b9c` | fixture | read |
| [skills/self-improve/evals/files/create-root-fixture/session_notes.md](../../../skills/self-improve/evals/files/create-root-fixture/session_notes.md) | `fd32ba358c69a3aa0a083ef76e497dc377f69f0bbca1ff628af741f7fd819278` | fixture | read |
| [skills/self-improve/evals/files/create-root-fixture/src/generated/client.py](../../../skills/self-improve/evals/files/create-root-fixture/src/generated/client.py) | `537e82f1cc2d103e865ee7a6baa7dd76233363ab84a48478ed6752395f5ceabe` | fixture | read |
| [skills/self-improve/evals/files/create-root-fixture/tests/integration/test_sync.py](../../../skills/self-improve/evals/files/create-root-fixture/tests/integration/test_sync.py) | `84e32c048528e4d78da737203cf76e73b6551205d4a4ae48530ded9754f3a14e` | fixture | read |
| [skills/self-improve/evals/files/execution-friction-fixture/AGENTS.md](../../../skills/self-improve/evals/files/execution-friction-fixture/AGENTS.md) | `0b65741c429457870beb8641beb23f3a7c3ae73822d264491930a15cd29f52eb` | fixture | read |
| [skills/self-improve/evals/files/execution-friction-fixture/docs/workflow.md](../../../skills/self-improve/evals/files/execution-friction-fixture/docs/workflow.md) | `316b2e0597304ce31c286c313658ae7f9b5f7b55e71fa6207c64b43a7a90996e` | fixture | read |
| [skills/self-improve/evals/files/execution-friction-fixture/session_notes.md](../../../skills/self-improve/evals/files/execution-friction-fixture/session_notes.md) | `88d43bd4ec6064d3b29e7e59d5e634bab28da92d7138524e8f723d1068d8c56e` | fixture | read |
| [skills/self-improve/evals/files/linked-doc-fixture/AGENTS.md](../../../skills/self-improve/evals/files/linked-doc-fixture/AGENTS.md) | `d44ea774d04aaf2d4615f5efe79950396734ff501f180e178e177c9d47ae3750` | fixture | read |
| [skills/self-improve/evals/files/linked-doc-fixture/docs/release.md](../../../skills/self-improve/evals/files/linked-doc-fixture/docs/release.md) | `0e66fdadd1c727083487001ad7fe6451fa4b972ecd252fd9845f6c5f3eb6d0a9` | fixture | read |
| [skills/self-improve/evals/files/linked-doc-fixture/rollout/prod.yml](../../../skills/self-improve/evals/files/linked-doc-fixture/rollout/prod.yml) | `288d859c915ab10c61b4c020e9f0f129294f72891e2664160760e900728e38ea` | fixture | read |
| [skills/self-improve/evals/files/linked-doc-fixture/session_notes.md](../../../skills/self-improve/evals/files/linked-doc-fixture/session_notes.md) | `2ee8e10462b7a3d0d43876ff6b0d376c0c96a6172941a7711daca58b6746678c` | fixture | read |
| [skills/self-improve/evals/files/noop-fixture/AGENTS.md](../../../skills/self-improve/evals/files/noop-fixture/AGENTS.md) | `9be79360de5414997641d9321254e2e979548922261bc2f09455ca1f8d1e7cdf` | fixture | read |
| [skills/self-improve/evals/files/noop-fixture/README.md](../../../skills/self-improve/evals/files/noop-fixture/README.md) | `c62448e9940a678c97e4088f5a86e5ad6e4ad00c9efd7e9a61de1b23932243ca` | fixture | read |
| [skills/self-improve/evals/files/noop-fixture/session_notes.md](../../../skills/self-improve/evals/files/noop-fixture/session_notes.md) | `c20551b0dbe08f2024074e070ad6f3caab8459eca624e0dce452e40e2bcd44dc` | fixture | read |
| [skills/self-improve/evals/files/progress-fixture/AGENTS.md](../../../skills/self-improve/evals/files/progress-fixture/AGENTS.md) | `ffaf28592ba2ace3ccaf8f3d5f1358329d025595d3c03d3c9b9d7d738174b907` | fixture | read |
| [skills/self-improve/evals/files/progress-fixture/docs/auth.md](../../../skills/self-improve/evals/files/progress-fixture/docs/auth.md) | `dc502cc65cb3d0833711bb90a86ed8e1a814fae620182617a9a40d98a04638bd` | fixture | read |
| [skills/self-improve/evals/files/progress-fixture/progress.txt](../../../skills/self-improve/evals/files/progress-fixture/progress.txt) | `c2ed31de969db63d3d6cc13486b434aa9cb4cd0abc1830b6da6bcbab9adf2209` | fixture | read |
| [skills/self-improve/evals/files/scoped-refactor-fixture/AGENTS.md](../../../skills/self-improve/evals/files/scoped-refactor-fixture/AGENTS.md) | `115a4993c73bae0ce422daa4a2c73f455b0d6528492694c746ebda6c2bc03f77` | fixture | read |
| [skills/self-improve/evals/files/scoped-refactor-fixture/api/schema/user.json](../../../skills/self-improve/evals/files/scoped-refactor-fixture/api/schema/user.json) | `e8913be795db95725c9e338576a74e85db7b59b9f7318ee1acf9bd1b3ebf94aa` | fixture | read |
| [skills/self-improve/evals/files/scoped-refactor-fixture/session_notes.md](../../../skills/self-improve/evals/files/scoped-refactor-fixture/session_notes.md) | `81e8eeab78cecaf33fdafc017ce19ccacf1dddc6c4cd30f2f197ceaf9b1b888c` | fixture | read |
| [skills/self-improve/evals/files/scoped-refactor-fixture/web/src/app.ts](../../../skills/self-improve/evals/files/scoped-refactor-fixture/web/src/app.ts) | `b32edcda54b7a6a91fe24df4c2938a2b9734a74fca4411591d33f5c2af13fcde` | fixture | read |
| [skills/self-improve/evals/grade_benchmark.py](../../../skills/self-improve/evals/grade_benchmark.py) | `b807d9d38c910787307de5f0dfd3b79706961d5593224c4ebbe97c24540bdda5` | static eval definition/utility | read |

## Source reading checkpoint

All maintained bundle files, three graders, and fixture inputs below have now been read. Six frontmatter records were parsed with the checked-in vendored YAML runtime without executing the skill validator. Each has a string name matching its directory and a nonempty description. Name lengths are 12, 13, 18, 15, 15 and 12 characters; description lengths are 390, 281, 338, 56, 109 and 354 characters in inventory skill order. Body lengths are 96, 83, 176, 243, 18 and 47 lines. These lengths are inventory facts, not defects or behavioral evidence.

Required imported helper instructions and exact validator/package implementation were inspected only as dependency source. Optimization implementation was inspected only at dependency/CLI anchors. Neither excluded helper nor installer was activated or run. Per-skill matrices and proposals are recorded against the shared 58-check catalog. Human disposition and runtime evidence remain pending.

## Purpose and protected contracts

| Skill | Purpose and preserved contracts | Source anchors |
| --- | --- | --- |
| create-skill | Repository-specific authoring/eval/benchmark guidance. Preserve identity and dedupe, mandatory skill-creator, realistic evals, deterministic grading where practical, sibling artifacts, baseline and packaging only on request. | `SKILL.md:10-12,24-49,68-72,94-99` |
| improve-skill | Durable session lessons for loaded skills, response-only proposals, no broad exploration, minimal scope, no weakening rules, exact no-op output. | `SKILL.md:6-18,33-43,49-69,71-86` |
| agents-md-improver | Audit AGENTS files, numeric per-file report and targeted additions. Preserve explicit invocation field, report before edits, user approval, additions-only focus, diffs and existing structure. | `SKILL.md:3-4,11,54-99,101-140` |
| create-agentsmd | Accurate root AGENTS guidance from actual repo workflows. Preserve name, both implicit-invocation controls, root output, project-specific adaptation, nested scope and accurate commands. | `SKILL.md:2-4,9,29-31,198-247`; `agents/openai.yaml:4-5` |
| guidance-review | File plus readable local guidance references, or literal text. Preserve controls, bounded traversal, no external links or revisits, category/location/evidence/correction report, definite versus possible omissions and no-issue result. | `SKILL.md:3-11,13-23`; `agents/openai.yaml:1-2` |
| self-improve | Durable lessons into AGENTS/linked docs, minimal scope refactor. Preserve durable-only/no-op branch, creation only if asked or strong lessons exist, exact technical terms, destination-before-source moves, short root and move/conflict/assumption report. | `SKILL.md:8-50`; `DURABLE_LEARNINGS.md:5-10,25-46`; `INSTRUCTION_STRUCTURE.md:5-42,60-78` |

## Dependencies, consumers and shipped resources

- Create-skill requires imported `skill-creator` (`SKILL.md:12,30,95`) and three repo guidance files (`31`). Its exact commands assume this checkout as working directory, consistent with its repository-specific purpose. Installed use requires a checkout; these paths are not universal portability requirements.
- Imported helper source was inspected only for this consumer: entry procedure, validator/package scripts, and exact CLI/import anchors in description optimization. The helper uses Claude runs and `scripts.run_loop --model` (`skill-creator/SKILL.md:163-245,333-404,432-454`). `run_eval.py:23-30,45-89` uses `.claude/commands` and `claude -p`; `improve_description.py:20-45` calls the same CLI. Required dependency remains protected and excluded from primary audit/edit targets.
- Validator imports PyYAML (`quick_validate.py:9`), rejects invocation/argument fields (`42-50`), and package imports that validator (`package_skill.py:17,70-76`). Repository known issues record the vendored-runtime workaround and retained-field limitation. No validator/package was run.
- Installers ship all six source entries and their non-eval resources, and remove per-skill evals (`install.sh:40-55`; `install.ps1:251-269`). Installer destination set includes account-level skills/agents/hooks/instructions/settings (`install.sh:26-38,183-207`). Thus eval utilities are repository evidence/tools, not available inside the installed bundle. No installation/access test occurred.
- Agents-md-improver directly links rubric and templates (`SKILL.md:33,144`), but never selects its bundled update guidelines. Self-improve has understandable direct textual pointers to both references (`SKILL.md:22,28`); provider loading/navigation remains untested.
- Named consumer search, bounded to maintained source and excluding workspace/archive/fixture trees, finds `prd-ralph-loop/SKILL.md:19-29,34-39` loading self-improve after its loop and progress-file read. Preserve its delayed-read/stopping contract. Owning execution batch reviews that consumer fully.
- `dotnet-upgrade/references/document-review.md:27` compares guidance-review metadata while explicitly withholding enforcement claims. Preserve those controls; owning upgrade batch reviews the bundle. No upgrade instructions were activated.
- No additional named direct calls were found in the bounded search. This does not prove semantic dependency closure. An initially incorrectly bounded search matched workspace text; those matches are excluded from inventory and conclusions.

## Findings and human review

The single [finding register](../findings.md) owns SAG-001 through SAG-014 and their human dispositions. On 2026-10-05 the human accepted authoring and evaluation repair scope and retained four separate pending decisions. The [owning ticket Resolution](../tickets/review-skill-authoring-and-repository-guidance.md#resolution) records the live review. No risk acceptance, evidence waiver, or implementation authorization is recorded.

## Per-skill coverage matrices

Each matrix accounts for every shared catalog check. Applicability, disposition, current compliance, source evidence, findings and unresolved gaps are separate. `adapt` preserves advice purpose for the actual host rather than importing Claude-only runtime assumptions. Static satisfaction does not establish behavior. File anchors are relative to the named skill unless a shared path is given. No row claims measured runtime performance, activation or permissions.

### create-skill

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | All procedure text | adopt | Static: task-specific instructions | SKILL.md:24-49,53-72,90-99 |  | Runtime context cost unmeasured |
| A02 | Repo refresh authority | adapt | Unresolved: owner instruction conflict | SKILL.md:49,99 and .agents/instructions/scripts.md:24 | [SAG-002](../findings.md#sag-002-installer-ownership-conflict) | Separate human authority decision, no install |
| A03 | Model behavior claims | adapt | Unresolved | Shared native evidence matrix |  | No current intended-model runs or waivers |
| A04-F | Entry metadata | adapt | Static: YAML parsed and required strings present | SKILL.md:1-5 and metadata checkpoint |  | Native client parser untested |
| A04-N | Name format | adapt | Static: directory match, lowercase and <=64 characters | SKILL.md:2 and metadata checkpoint |  | Tightest documented VS Code condition used |
| A04-D | Description metadata | adapt | Static: nonempty <=1024 chars without XML | SKILL.md:3 and metadata checkpoint |  | Claude bounds are source-specific, not universal requirement |
| A05 | Meaningful name | adopt | Static: name identifies purpose | SKILL.md:2-3 |  | Names preserved |
| A06 | Description capability/triggers | adapt | Static: stated capability matches procedure | SKILL.md:3 and SKILL.md:24-49,53-72,90-99 |  | Actual activation not tested |
| A07 | Focused entry body | adapt | Static: body covers core task | Metadata body-length checkpoint and SKILL.md:24-49,53-72,90-99 |  | Length alone is not a defect |
| A08 | Mandatory helper/repo guidance | adapt | Static: direct required invocation/reference | SKILL.md:12,29-31,95 |  | Required helper preserved and excluded from primary audit |
| A09 | Packaging/weak-model/helper optional optimization | adapt | Partial: branch selected with host qualifications | SKILL.md:48,59-72 and skill-creator/SKILL.md:333-454 |  | Claude-only optimization does not prove other clients |
| A10 | Mandatory helper/repo guidance | adapt | Static: direct required invocation/reference | SKILL.md:12,29-31,95 |  | Required helper preserved and excluded from primary audit |
| A11 | Procedure references >100 lines | not applicable | Not applicable: no qualifying reference | Reviewed-file inventory |  | No arbitrary splitting for length |
| A12 | Dedupe fixture/oracle | adapt | Defective: oracle names absent skills | evals/evals.json:34-40 and grader:226,233-245 | [SAG-004](../findings.md#sag-004-stale-duplicate-avoidance-oracle), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Bounded current overlap checked, no 1:1 successor invented |
| A13 | Sequential procedure | adopt | Static: Scope/load/draft/eval/validate sequence | SKILL.md:24-49,53-72,90-99 |  | Native workflow outcome untested |
| A14 | Validator/package prerequisites and controls | adapt | Defective: known runtime/control mismatch omitted | SKILL.md:45-48 and validator:9,42-50 | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Preserve controls and vendor runtime, no validator/package run |
| A15 | Dedupe fixture/oracle | adapt | Defective: oracle names absent skills | evals/evals.json:34-40 and grader:226,233-245 | [SAG-004](../findings.md#sag-004-stale-duplicate-avoidance-oracle), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Bounded current overlap checked, no 1:1 successor invented |
| A16 | Terminology | adopt | Static: concepts consistent within procedure | SKILL.md:24-49,53-72,90-99 |  | Native workflow outcome untested |
| A17 | Anatomy output intent | adapt | Unresolved: seven headings are grader-only expectation | SKILL.md:10,96 and grader:10-18 | [SAG-003](../findings.md#sag-003-undefined-anatomy-expectation) | Separate output-contract decision needed |
| A18 | Expected output style | adapt | Static: concrete report/checklist guidance | SKILL.md:24-49,53-72,90-99 |  | Examples optional where prose already defines shape |
| A19 | Conditional procedure branches | adopt | Static: conditions/no-op alternatives identified | SKILL.md:24-49,53-72,90-99 |  | Native workflow outcome untested |
| A20 | Default and scoped exceptions | adopt | Static: one primary procedure | SKILL.md:24-49,53-72,90-99 |  | Native workflow outcome untested |
| A21 | Baseline-driven improvement | adapt | Unresolved | Static-only scope and approved evidence contract |  | No current matched baseline or historical output review |
| A22 | Dedupe fixture/oracle | adapt | Defective: oracle names absent skills | evals/evals.json:34-40 and grader:226,233-245 | [SAG-004](../findings.md#sag-004-stale-duplicate-avoidance-oracle), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Bounded current overlap checked, no 1:1 successor invented |
| A23 | Authoring intent from real task | adapt | Partial: helper directs mining actual session | skill-creator/SKILL.md:47-60 |  | No real source-task provenance reviewed |
| A24 | Fresh using-session iteration | adapt | Unresolved | Static-only scope |  | No fresh native task runs |
| A25 | Team feedback condition unknown | adapt | Unresolved | No feedback corpus in scope |  | No invented claim of team use or incorporation |
| A26 | Observed navigation/activation | adapt | Unresolved | Source navigation only |  | No retrieval or activation traces |
| A27 | Bundled grader errors/fallbacks | adapt | Partial: missing skill/utility checks exist, metadata/subprocess failures lack structured recovery | evals/grade_benchmark.py:27-30,56-75,302-309,357-380 | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation) | Missing/malformed artifact and timeout paths untested |
| A28 | Named grader constants | adapt | Partial: anatomy headings and reference phrase blacklist named, three-eval bound matches entry | evals/grade_benchmark.py:10-24,167-169 and SKILL.md:39 |  | No universal optimal threshold inferred, body-contract intent is SAG-003 |
| A29 | Repeated deterministic grading | adopt | Static: reusable utility performs repeated artifact checks and writes structured grading | evals/grade_benchmark.py usage/main |  | Utility correctness separate from reuse, no native grader run |
| A30 | Validator/package prerequisites and controls | adapt | Defective: known runtime/control mismatch omitted | SKILL.md:45-48 and validator:9,42-50 | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Preserve controls and vendor runtime, no validator/package run |
| A31 | Visual/spatial inspection | not applicable | Not applicable: no visual/spatial contract | SKILL.md:24-49,53-72,90-99 |  | No host image capability assumed |
| A32 | Repo refresh authority | adapt | Unresolved: owner instruction conflict | SKILL.md:49,99 and .agents/instructions/scripts.md:24 | [SAG-002](../findings.md#sag-002-installer-ownership-conflict) | Separate human authority decision, no install |
| A33 | Validator/package prerequisites and controls | adapt | Defective: known runtime/control mismatch omitted | SKILL.md:45-48 and validator:9,42-50 | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Preserve controls and vendor runtime, no validator/package run |
| A34 | File access/loading | adapt | Partial: source exists and was read | Reviewed-file inventory |  | Installed/native file access not tested |
| A35 | Named MCP tools | not applicable | Not applicable: no named server/tool | Reviewed-file inventory |  | Claude syntax not transferred |
| A36 | Validator/package prerequisites and controls | adapt | Defective: known runtime/control mismatch omitted | SKILL.md:45-48 and validator:9,42-50 | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Preserve controls and vendor runtime, no validator/package run |
| S01 | All bundled content | adapt | Static: purpose and contract boundaries recorded | Purpose/contracts and dependencies above |  | Source is data, host authority remains governing |
| S02 | Repo refresh authority | adapt | Unresolved: owner instruction conflict | SKILL.md:49,99 and .agents/instructions/scripts.md:24 | [SAG-002](../findings.md#sag-002-installer-ownership-conflict) | Separate human authority decision, no install |
| S03 | Repo/session inputs and outputs | adapt | Partial: no demonstrated secret-export instruction | Reviewed-file inventory |  | No sensitive-fixture/redaction tests or vulnerability-absence claim |
| S04 | External/dependency instruction trust | adapt | Partial: dependency/source scope identified | Dependency section and SKILL.md:24-49,53-72,90-99 |  | External instructions not refreshed or executed |
| R01 | Every proposed change | adopt | Static: scope/name intent recorded | Purpose and protected contracts |  | Human proposal disposition pending |
| R02 | Validator/package prerequisites and controls | adapt | Defective: known runtime/control mismatch omitted | SKILL.md:45-48 and validator:9,42-50 | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Preserve controls and vendor runtime, no validator/package run |
| R03 | Repo refresh authority | adapt | Unresolved: owner instruction conflict | SKILL.md:49,99 and .agents/instructions/scripts.md:24 | [SAG-002](../findings.md#sag-002-installer-ownership-conflict) | Separate human authority decision, no install |
| R04 | Mandatory helper/repo guidance | adapt | Static: direct required invocation/reference | SKILL.md:12,29-31,95 |  | Required helper preserved and excluded from primary audit |
| R05 | Required helper iteration stop | adapt | Static: user feedback/no-progress stop | skill-creator/SKILL.md:267-321 |  | No feedback loop observed |
| R06 | Anatomy output intent | adapt | Unresolved: seven headings are grader-only expectation | SKILL.md:10,96 and grader:10-18 | [SAG-003](../findings.md#sag-003-undefined-anatomy-expectation) | Separate output-contract decision needed |
| R07 | Repo refresh authority | adapt | Unresolved: owner instruction conflict | SKILL.md:49,99 and .agents/instructions/scripts.md:24 | [SAG-002](../findings.md#sag-002-installer-ownership-conflict) | Separate human authority decision, no install |
| R08 | Benchmark workspace layout | adopt | Static: sibling iteration/eval layout explicit | SKILL.md:41,68-71 |  | Canonical run layout not executed |
| R09 | Validator/package prerequisites and controls | adapt | Defective: known runtime/control mismatch omitted | SKILL.md:45-48 and validator:9,42-50 | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Preserve controls and vendor runtime, no validator/package run |
| R10 | Broad edit/validation includes upgrade exception | adapt | Partial: generic validation misses scoped paper review | SKILL.md:17,45-48 and repo document-review rules | [SAG-001](../findings.md#sag-001-validation-prerequisites-and-retained-control-exceptions) | Upgrade document-only exception retained |
| R11 | Shipped evaluation/grading claims | adopt | Defective predicates and unmeasured metrics | evals/grade_benchmark.py | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | No current model/grader runs |
| R12 | Source formatting | adopt | Static: parent byte scan found no CR/tab/trailing whitespace | Parent whole-bundle scan on 2026-10-05 |  | No source edit or formatting repair here |
| C01 | Native activation/discovery | adapt | Unresolved | Parsed metadata and provider research |  | No explicit/implicit native traces |
| C02 | Actually shipped resources | adapt | Partial: installer copies non-evals and strips evals | scripts/install.sh:40-55 and install.ps1:251-269 |  | Installed copy/file access untested |
| C03 | Provider-specific adapter | not applicable | Not applicable: no sidecar/explicit-only field | SKILL.md:1-5 and inventory |  | Optional UI sidecar not universally required |
| C04 | Repo refresh authority | adapt | Unresolved: owner instruction conflict | SKILL.md:49,99 and .agents/instructions/scripts.md:24 | [SAG-002](../findings.md#sag-002-installer-ownership-conflict) | Separate human authority decision, no install |

### improve-skill

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | All procedure text | adopt | Static: task-specific instructions | SKILL.md:6-18,33-43,49-86 |  | Runtime context cost unmeasured |
| A02 | Workflow risk and variation | adopt | Static: exact steps plus scoped judgment | SKILL.md:6-18,33-43,49-86 |  | Native workflow outcome untested |
| A03 | Model behavior claims | adapt | Unresolved | Shared native evidence matrix |  | No current intended-model runs or waivers |
| A04-F | Entry metadata | adapt | Static: YAML parsed and required strings present | SKILL.md:1-5 and metadata checkpoint |  | Native client parser untested |
| A04-N | Name format | adapt | Static: directory match, lowercase and <=64 characters | SKILL.md:2 and metadata checkpoint |  | Tightest documented VS Code condition used |
| A04-D | Description metadata | adapt | Static: nonempty <=1024 chars without XML | SKILL.md:3 and metadata checkpoint |  | Claude bounds are source-specific, not universal requirement |
| A05 | Meaningful name | adopt | Static: name identifies purpose | SKILL.md:2-3 |  | Names preserved |
| A06 | Description capability/triggers | adapt | Static: stated capability matches procedure | SKILL.md:3 and SKILL.md:6-18,33-43,49-86 |  | Actual activation not tested |
| A07 | Focused entry body | adapt | Static: body covers core task | Metadata body-length checkpoint and SKILL.md:6-18,33-43,49-86 |  | Length alone is not a defect |
| A08 | Procedure/resource selection | adapt | Static: core procedure in entry | SKILL.md:6-18,33-43,49-86 |  | Selective client loading untested |
| A09 | Specialized optional details | not applicable | Not applicable: no advanced optional procedure | SKILL.md:6-18,33-43,49-86 |  | Basic input/no-op branches reviewed separately |
| A10 | Direct procedure references | not applicable | Not applicable: self-contained procedure | SKILL.md:6-18,33-43,49-86 |  | Eval resources are separate tooling |
| A11 | Procedure references >100 lines | not applicable | Not applicable: no qualifying reference | Reviewed-file inventory |  | No arbitrary splitting for length |
| A12 | Declared eval notes inputs | adopt | Defective: three fixture notes absent | evals/evals.json:8-10,29-31,50-52 | [SAG-006](../findings.md#sag-006-missing-improve-skill-fixture-inputs) | Incomplete setup is not failed skill behavior |
| A13 | Sequential procedure | adopt | Static: Loaded target/durable lesson/scoped response or no-op | SKILL.md:6-18,33-43,49-86 |  | Native workflow outcome untested |
| A14 | Quality-sensitive output | adapt | Partial: final report/checks present | SKILL.md:6-18,33-43,49-86 |  | Actual validation/correction behavior untested |
| A15 | Dated product/version facts | not applicable | Not applicable: no time-sensitive product claim | SKILL.md:6-18,33-43,49-86 |  | Future repo facts still need source cross-check |
| A16 | Terminology | adopt | Static: concepts consistent within procedure | SKILL.md:6-18,33-43,49-86 |  | Native workflow outcome untested |
| A17 | Response-only/loaded-target eval contract | adopt | Defective: eval rewards prohibited writes | SKILL.md:8,12-14,49-69 and evals | [SAG-005](../findings.md#sag-005-improve-skill-evals-reward-prohibited-writes), [SAG-006](../findings.md#sag-006-missing-improve-skill-fixture-inputs), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Align evals to protected intent, redesign requires separate approval |
| A18 | Suggested-edit response shape | adopt | Static: edit/reason template and exact no-op | SKILL.md:53-69 |  | Native behavior untested |
| A19 | Conditional procedure branches | adopt | Static: conditions/no-op alternatives identified | SKILL.md:6-18,33-43,49-86 |  | Native workflow outcome untested |
| A20 | Default and scoped exceptions | adopt | Static: one primary procedure | SKILL.md:6-18,33-43,49-86 |  | Native workflow outcome untested |
| A21 | Baseline-driven improvement | adapt | Unresolved | Static-only scope and approved evidence contract |  | No current matched baseline or historical output review |
| A22 | Response-only/loaded-target eval contract | adopt | Defective: eval rewards prohibited writes | SKILL.md:8,12-14,49-69 and evals | [SAG-005](../findings.md#sag-005-improve-skill-evals-reward-prohibited-writes), [SAG-006](../findings.md#sag-006-missing-improve-skill-fixture-inputs), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Align evals to protected intent, redesign requires separate approval |
| A23 | Durable current-session knowledge | adopt | Static: actionable repeated observed facts only | SKILL.md:16-43 |  | Native behavior untested |
| A24 | Fresh using-session iteration | adapt | Unresolved | Static-only scope |  | No fresh native task runs |
| A25 | Team feedback condition unknown | adapt | Unresolved | No feedback corpus in scope |  | No invented claim of team use or incorporation |
| A26 | Observed navigation/activation | adapt | Unresolved | Source navigation only |  | No retrieval or activation traces |
| A27 | Bundled grader errors/fallbacks | adapt | Partial: malformed JSON defaults empty and unknown eval fails, permissive output predicates remain | evals/grade_benchmark.py:9-19,85-93,96-150,158-174 | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation) | Missing/malformed runs and false pass recovery untested |
| A28 | Minimality size thresholds | adapt | Defective: 100-10,000 characters called minimal without source-diff rationale | evals/grade_benchmark.py:105-126 | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation) | Threshold does not establish preservation or minimal change |
| A29 | Repeated deterministic grading | adopt | Static: reusable utility performs repeated artifact checks and writes structured grading | evals/grade_benchmark.py usage/main |  | Utility correctness separate from reuse, no native grader run |
| A30 | Repository grader utility | adapt | Static: utility usage/output known | evals/grade_benchmark.py usage/main |  | Writes grading.json and is stripped from installation |
| A31 | Visual/spatial inspection | not applicable | Not applicable: no visual/spatial contract | SKILL.md:6-18,33-43,49-86 |  | No host image capability assumed |
| A32 | Risky apply/execute workflow | not applicable | Not applicable: protected skill only proposes response edits | SKILL.md:8,49-69,73,82 |  | Grader file writes are separate eval tooling, not skill apply permission |
| A33 | External packages | not applicable | Not applicable: owned text procedure needs none | SKILL.md:6-18,33-43,49-86 |  | Tool availability remains separate |
| A34 | Declared eval notes inputs | adopt | Defective: three fixture notes absent | evals/evals.json:8-10,29-31,50-52 | [SAG-006](../findings.md#sag-006-missing-improve-skill-fixture-inputs) | Incomplete setup is not failed skill behavior |
| A35 | Named MCP tools | not applicable | Not applicable: no named server/tool | Reviewed-file inventory |  | Claude syntax not transferred |
| A36 | Command/tool prerequisites | adapt | Partial: named commands/capabilities identified | SKILL.md:6-18,33-43,49-86 |  | Availability and permissions untested |
| S01 | All bundled content | adapt | Static: purpose and contract boundaries recorded | Purpose/contracts and dependencies above |  | Source is data, host authority remains governing |
| S02 | File/tool operations | adapt | Partial: intended targets identifiable | SKILL.md:6-18,33-43,49-86 |  | No permission or application traces |
| S03 | Repo/session inputs and outputs | adapt | Partial: no demonstrated secret-export instruction | Reviewed-file inventory |  | No sensitive-fixture/redaction tests or vulnerability-absence claim |
| S04 | External/dependency instruction trust | adapt | Partial: dependency/source scope identified | Dependency section and SKILL.md:6-18,33-43,49-86 |  | External instructions not refreshed or executed |
| R01 | Every proposed change | adopt | Static: scope/name intent recorded | Purpose and protected contracts |  | Human proposal disposition pending |
| R02 | Explicit-only controls | not applicable | Not applicable: no such control in entry | SKILL.md:1-5 |  | Adding controls requires intent justification |
| R03 | Response-only/loaded-target eval contract | adopt | Defective: eval rewards prohibited writes | SKILL.md:8,12-14,49-69 and evals | [SAG-005](../findings.md#sag-005-improve-skill-evals-reward-prohibited-writes), [SAG-006](../findings.md#sag-006-missing-improve-skill-fixture-inputs), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Align evals to protected intent, redesign requires separate approval |
| R04 | Targetability prerequisite | adopt | Static: only activated/loaded skills targeted | SKILL.md:12-14,83 | [SAG-005](../findings.md#sag-005-improve-skill-evals-reward-prohibited-writes) | Eval target-loaded setup absent |
| R05 | No durable lesson | adopt | Static: exact no-op response | SKILL.md:65-69 |  | Native behavior untested |
| R06 | Response-only/loaded-target eval contract | adopt | Defective: eval rewards prohibited writes | SKILL.md:8,12-14,49-69 and evals | [SAG-005](../findings.md#sag-005-improve-skill-evals-reward-prohibited-writes), [SAG-006](../findings.md#sag-006-missing-improve-skill-fixture-inputs), [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Align evals to protected intent, redesign requires separate approval |
| R07 | Document authority in this checkout | adapt | Partial: generic procedure must defer to host owners | AGENTS.md and .agents/instructions/repo.md |  | Protected root sections and .agents ownership retained |
| R08 | Source/eval/generated separation | adapt | Static: this audit separates evidence fixtures from targets | Inventory and repository exclusions |  | No generated run/output reviewed |
| R09 | Repo validation prerequisites | adapt | Partial: scoped tooling limitations documented | .agents/memory/testing/skills.md and known-issues/skills.md |  | No validator/package/live check executed |
| R10 | Upgrade consumer procedure | not applicable | Not applicable: no upgrade call/action | SKILL.md:6-18,33-43,49-86 |  | Paper audit does not activate upgrade |
| R11 | Shipped evaluation/grading claims | adopt | Defective predicates and unmeasured metrics | evals/grade_benchmark.py | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | No current model/grader runs |
| R12 | Source whitespace | adopt | Defective: three whitespace-only lines | evals/grade_benchmark.py:133,139,142 | [SAG-014](../findings.md#sag-014-trailing-whitespace-in-improve-skill-grader) | Parent byte scan, no source repair authorized |
| C01 | Native activation/discovery | adapt | Unresolved | Parsed metadata and provider research |  | No explicit/implicit native traces |
| C02 | Actually shipped resources | adapt | Partial: installer copies non-evals and strips evals | scripts/install.sh:40-55 and install.ps1:251-269 |  | Installed copy/file access untested |
| C03 | Provider-specific adapter | not applicable | Not applicable: no sidecar/explicit-only field | SKILL.md:1-5 and inventory |  | Optional UI sidecar not universally required |
| C04 | Activation/tool permissions | adapt | Unresolved: activation is not tool permission | Provider research and protected contracts |  | No permission/client enforcement traces |

### agents-md-improver

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | All procedure text | adopt | Static: task-specific instructions | SKILL.md:11-44,54-140,142-180 |  | Runtime context cost unmeasured |
| A02 | Workflow risk and variation | adopt | Static: exact steps plus scoped judgment | SKILL.md:11-44,54-140,142-180 |  | Native workflow outcome untested |
| A03 | Model behavior claims | adapt | Unresolved | Shared native evidence matrix |  | No current intended-model runs or waivers |
| A04-F | Entry metadata | adapt | Static: YAML parsed and required strings present | SKILL.md:1-5 and metadata checkpoint |  | Native client parser untested |
| A04-N | Name format | adapt | Static: directory match, lowercase and <=64 characters | SKILL.md:2 and metadata checkpoint |  | Tightest documented VS Code condition used |
| A04-D | Description metadata | adapt | Static: nonempty <=1024 chars without XML | SKILL.md:3 and metadata checkpoint |  | Claude bounds are source-specific, not universal requirement |
| A05 | Meaningful name | adopt | Static: name identifies purpose | SKILL.md:2-3 |  | Names preserved |
| A06 | Description capability/triggers | adapt | Static: stated capability matches procedure | SKILL.md:3 and SKILL.md:11-44,54-140,142-180 |  | Actual activation not tested |
| A07 | Focused entry body | adapt | Static: body covers core task | Metadata body-length checkpoint and SKILL.md:11-44,54-140,142-180 |  | Length alone is not a defect |
| A08 | Resource navigation/Markdown templates | adapt | Defective: unlinked guide and mismatched fences | SKILL.md:33,144 and references/templates.md:36-46,126-223 | [SAG-010](../findings.md#sag-010-broken-template-fences-and-unreachable-update-guide) | No render or native navigation test |
| A09 | Project template variants | adopt | Static: project relevance controls template selection | SKILL.md:142-144,171-179 and templates |  | Native behavior untested |
| A10 | Resource navigation/Markdown templates | adapt | Defective: unlinked guide and mismatched fences | SKILL.md:33,144 and references/templates.md:36-46,126-223 | [SAG-010](../findings.md#sag-010-broken-template-fences-and-unreachable-update-guide) | No render or native navigation test |
| A11 | Three references >100 lines | adapt | Partial: section headings aid navigation without TOC | references/{quality-criteria,templates,update-guidelines}.md |  | No length-only defect, concrete selection issue in A10 |
| A12 | AGENTS discovery in this checkout | adapt | Defective: capped all-file search without scope exclusions | SKILL.md:17-20 and repo fixture/workspace rules | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Uncapped scoped discovery not executed |
| A13 | AGENTS discovery in this checkout | adapt | Defective: capped all-file search without scope exclusions | SKILL.md:17-20 and repo fixture/workspace rules | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Uncapped scoped discovery not executed |
| A14 | Report-before-approval-before-update | adopt | Static: report/diff/confirmation required | SKILL.md:11,54-140 |  | No native approval/action trace |
| A15 | Dated product/version facts | not applicable | Not applicable: no time-sensitive product claim | SKILL.md:11-44,54-140,142-180 |  | Future repo facts still need source cross-check |
| A16 | Terminology | adopt | Static: concepts consistent within procedure | SKILL.md:11-44,54-140,142-180 |  | Native workflow outcome untested |
| A17 | Resource navigation/Markdown templates | adapt | Defective: unlinked guide and mismatched fences | SKILL.md:33,144 and references/templates.md:36-46,126-223 | [SAG-010](../findings.md#sag-010-broken-template-fences-and-unreachable-update-guide) | No render or native navigation test |
| A18 | Expected output style | adapt | Static: concrete report/checklist guidance | SKILL.md:11-44,54-140,142-180 |  | Examples optional where prose already defines shape |
| A19 | Conditional procedure branches | adopt | Static: conditions/no-op alternatives identified | SKILL.md:11-44,54-140,142-180 |  | Native workflow outcome untested |
| A20 | Default and scoped exceptions | adopt | Static: one primary procedure | SKILL.md:11-44,54-140,142-180 |  | Native workflow outcome untested |
| A21 | Baseline-driven improvement | adapt | Unresolved | Static-only scope and approved evidence contract |  | No current matched baseline or historical output review |
| A22 | Inspectable evaluation outcomes | adapt | Unresolved: no shipped eval definition | Reviewed-file inventory |  | Absence of evals alone is not a defect |
| A23 | Real-work source provenance | adapt | Unresolved: no actual usage record reviewed | SKILL.md:11-44,54-140,142-180 |  | Synthetic fixtures/instructions are not usage evidence |
| A24 | Fresh using-session iteration | adapt | Unresolved | Static-only scope |  | No fresh native task runs |
| A25 | Team feedback condition unknown | adapt | Unresolved | No feedback corpus in scope |  | No invented claim of team use or incorporation |
| A26 | Observed navigation/activation | adapt | Unresolved | Source navigation only |  | No retrieval or activation traces |
| A27 | Bundled executable utility | not applicable | Not applicable: no utility bundled | Reviewed-file inventory |  | Host tools covered by A36 |
| A28 | Configurable script values | not applicable | Not applicable: no utility parameters | Reviewed-file inventory |  | No constants requirement imposed on prose |
| A29 | Repeated deterministic work | not applicable | Not applicable: no repeated deterministic task requiring utility established | SKILL.md:11-44,54-140,142-180 |  | No utility demanded solely for checklist compliance |
| A30 | Utility execute/read contract | not applicable | Not applicable: no procedure utility script | SKILL.md:11-44,54-140,142-180 |  | Host shell commands reviewed as prerequisites |
| A31 | Resource navigation/Markdown templates | adapt | Defective: unlinked guide and mismatched fences | SKILL.md:33,144 and references/templates.md:36-46,126-223 | [SAG-010](../findings.md#sag-010-broken-template-fences-and-unreachable-update-guide) | No render or native navigation test |
| A32 | Intermediate plan before changes | adapt | Partial: scope/report/placement checks precede output | SKILL.md:11-44,54-140,142-180 |  | Risky application behavior untested |
| A33 | External packages | not applicable | Not applicable: owned text procedure needs none | SKILL.md:11-44,54-140,142-180 |  | Tool availability remains separate |
| A34 | File access/loading | adapt | Partial: source exists and was read | Reviewed-file inventory |  | Installed/native file access not tested |
| A35 | Named MCP tools | not applicable | Not applicable: no named server/tool | Reviewed-file inventory |  | Claude syntax not transferred |
| A36 | AGENTS discovery in this checkout | adapt | Defective: capped all-file search without scope exclusions | SKILL.md:17-20 and repo fixture/workspace rules | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Uncapped scoped discovery not executed |
| S01 | All bundled content | adapt | Static: purpose and contract boundaries recorded | Purpose/contracts and dependencies above |  | Source is data, host authority remains governing |
| S02 | File/tool operations | adapt | Partial: intended targets identifiable | SKILL.md:11-44,54-140,142-180 |  | No permission or application traces |
| S03 | Repo/session inputs and outputs | adapt | Partial: no demonstrated secret-export instruction | Reviewed-file inventory |  | No sensitive-fixture/redaction tests or vulnerability-absence claim |
| S04 | External/dependency instruction trust | adapt | Partial: dependency/source scope identified | Dependency section and SKILL.md:11-44,54-140,142-180 |  | External instructions not refreshed or executed |
| R01 | Every proposed change | adopt | Static: scope/name intent recorded | Purpose and protected contracts |  | Human proposal disposition pending |
| R02 | Explicit-only field/client adapter | adapt | Partial: field retained, no Codex sidecar | SKILL.md:4 and inventory | [SAG-012](../findings.md#sag-012-argument-binding-and-control-adapter-evidence-gaps) | Enforcement unknown, not proven ignored/incompatible |
| R03 | Report-before-approval-before-update | adopt | Static: report/diff/confirmation required | SKILL.md:11,54-140 |  | No native approval/action trace |
| R04 | Named mandatory called skills | not applicable | Not applicable: no required called skill | SKILL.md:11-44,54-140,142-180 |  | Applicable host guidance still governs |
| R05 | Report-before-approval-before-update | adopt | Static: report/diff/confirmation required | SKILL.md:11,54-140 |  | No native approval/action trace |
| R06 | Numeric report and additions-only update | adopt | Static: report/template/diff constraints | SKILL.md:60-140 |  | Do not infer refactor/removal authority |
| R07 | AGENTS discovery in this checkout | adapt | Defective: capped all-file search without scope exclusions | SKILL.md:17-20 and repo fixture/workspace rules | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Uncapped scoped discovery not executed |
| R08 | AGENTS discovery in this checkout | adapt | Defective: capped all-file search without scope exclusions | SKILL.md:17-20 and repo fixture/workspace rules | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Uncapped scoped discovery not executed |
| R09 | Repo validation prerequisites | adapt | Partial: scoped tooling limitations documented | .agents/memory/testing/skills.md and known-issues/skills.md |  | No validator/package/live check executed |
| R10 | Upgrade consumer procedure | not applicable | Not applicable: no upgrade call/action | SKILL.md:11-44,54-140,142-180 |  | Paper audit does not activate upgrade |
| R11 | Evidence integrity | adopt | Static: source/runtime distinction retained | Report evidence limits |  | No runtime passing claim or human waiver |
| R12 | Source formatting | adopt | Static: parent byte scan found no CR/tab/trailing whitespace | Parent whole-bundle scan on 2026-10-05 |  | No source edit or formatting repair here |
| C01 | Native activation/discovery | adapt | Unresolved | Parsed metadata and provider research |  | No explicit/implicit native traces |
| C02 | Actually shipped resources | adapt | Partial: installer copies non-evals and strips evals | scripts/install.sh:40-55 and install.ps1:251-269 |  | Installed copy/file access untested |
| C03 | Explicit-only field/client adapter | adapt | Partial: field retained, no Codex sidecar | SKILL.md:4 and inventory | [SAG-012](../findings.md#sag-012-argument-binding-and-control-adapter-evidence-gaps) | Enforcement unknown, not proven ignored/incompatible |
| C04 | Activation/tool permissions | adapt | Unresolved: activation is not tool permission | Provider research and protected contracts |  | No permission/client enforcement traces |

### create-agentsmd

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | All procedure text | adopt | Static: task-specific instructions | SKILL.md:9-31,108-164,196-247 |  | Runtime context cost unmeasured |
| A02 | Workflow risk and variation | adopt | Static: exact steps plus scoped judgment | SKILL.md:9-31,108-164,196-247 |  | Native workflow outcome untested |
| A03 | Model behavior claims | adapt | Unresolved | Shared native evidence matrix |  | No current intended-model runs or waivers |
| A04-F | Entry metadata | adapt | Static: YAML parsed and required strings present | SKILL.md:1-5 and metadata checkpoint |  | Native client parser untested |
| A04-N | Name format | adapt | Static: directory match, lowercase and <=64 characters | SKILL.md:2 and metadata checkpoint |  | Tightest documented VS Code condition used |
| A04-D | Description metadata | adapt | Static: nonempty <=1024 chars without XML | SKILL.md:3 and metadata checkpoint |  | Claude bounds are source-specific, not universal requirement |
| A05 | Meaningful name | adopt | Static: name identifies purpose | SKILL.md:2-3 |  | Names preserved |
| A06 | Codex UI scope/policy metadata | adapt | Defective UI describes different task, policy retained | SKILL.md:3,9 and agents/openai.yaml:2-5 | [SAG-011](../findings.md#sag-011-misleading-codex-sidecar-scope) | Codex UI behavior untested and sidecar not universal |
| A07 | Focused entry body | adapt | Static: body covers core task | Metadata body-length checkpoint and SKILL.md:9-31,108-164,196-247 |  | Length alone is not a defect |
| A08 | Procedure/resource selection | adapt | Static: core procedure in entry | SKILL.md:9-31,108-164,196-247 |  | Selective client loading untested |
| A09 | Specialized optional details | not applicable | Not applicable: no advanced optional procedure | SKILL.md:9-31,108-164,196-247 |  | Basic input/no-op branches reviewed separately |
| A10 | Direct procedure references | not applicable | Not applicable: self-contained procedure | SKILL.md:9-31,108-164,196-247 |  | Eval resources are separate tooling |
| A11 | Procedure references >100 lines | not applicable | Not applicable: no qualifying reference | Reviewed-file inventory |  | No arbitrary splitting for length |
| A12 | Named paths | adapt | Static: descriptive forward-slash paths | SKILL.md:9-31,108-164,196-247 |  | Native path access untested |
| A13 | Sequential procedure | adopt | Static: Analyze actual repo/draft customized sections/validate | SKILL.md:9-31,108-164,196-247 |  | Native workflow outcome untested |
| A14 | Quality-sensitive output | adapt | Partial: final report/checks present | SKILL.md:9-31,108-164,196-247 |  | Actual validation/correction behavior untested |
| A15 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |
| A16 | Codex UI scope/policy metadata | adapt | Defective UI describes different task, policy retained | SKILL.md:3,9 and agents/openai.yaml:2-5 | [SAG-011](../findings.md#sag-011-misleading-codex-sidecar-scope) | Codex UI behavior untested and sidecar not universal |
| A17 | Customized root AGENTS template | adopt | Static: explicit template and labeled sample | SKILL.md:108-194 |  | Sample stack does not establish universal commands |
| A18 | Customized root AGENTS template | adopt | Static: explicit template and labeled sample | SKILL.md:108-194 |  | Sample stack does not establish universal commands |
| A19 | Conditional procedure branches | adopt | Static: conditions/no-op alternatives identified | SKILL.md:9-31,108-164,196-247 |  | Native workflow outcome untested |
| A20 | Default and scoped exceptions | adopt | Static: one primary procedure | SKILL.md:9-31,108-164,196-247 |  | Native workflow outcome untested |
| A21 | Baseline-driven improvement | adapt | Unresolved | Static-only scope and approved evidence contract |  | No current matched baseline or historical output review |
| A22 | Inspectable evaluation outcomes | adapt | Unresolved: no shipped eval definition | Reviewed-file inventory |  | Absence of evals alone is not a defect |
| A23 | Real-work source provenance | adapt | Unresolved: no actual usage record reviewed | SKILL.md:9-31,108-164,196-247 |  | Synthetic fixtures/instructions are not usage evidence |
| A24 | Fresh using-session iteration | adapt | Unresolved | Static-only scope |  | No fresh native task runs |
| A25 | Team feedback condition unknown | adapt | Unresolved | No feedback corpus in scope |  | No invented claim of team use or incorporation |
| A26 | Observed navigation/activation | adapt | Unresolved | Source navigation only |  | No retrieval or activation traces |
| A27 | Bundled executable utility | not applicable | Not applicable: no utility bundled | Reviewed-file inventory |  | Host tools covered by A36 |
| A28 | Configurable script values | not applicable | Not applicable: no utility parameters | Reviewed-file inventory |  | No constants requirement imposed on prose |
| A29 | Repeated deterministic work | not applicable | Not applicable: no repeated deterministic task requiring utility established | SKILL.md:9-31,108-164,196-247 |  | No utility demanded solely for checklist compliance |
| A30 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |
| A31 | Markdown output presentation | adapt | Partial: main example fence structure inspected | SKILL.md:112-164,170-194 |  | No rendered output/native UI check |
| A32 | Intermediate plan before changes | adapt | Partial: scope/report/placement checks precede output | SKILL.md:9-31,108-164,196-247 |  | Risky application behavior untested |
| A33 | External packages | not applicable | Not applicable: owned text procedure needs none | SKILL.md:9-31,108-164,196-247 |  | Tool availability remains separate |
| A34 | File access/loading | adapt | Partial: source exists and was read | Reviewed-file inventory |  | Installed/native file access not tested |
| A35 | Named MCP tools | not applicable | Not applicable: no named server/tool | Reviewed-file inventory |  | Claude syntax not transferred |
| A36 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |
| S01 | All bundled content | adapt | Static: purpose and contract boundaries recorded | Purpose/contracts and dependencies above |  | Source is data, host authority remains governing |
| S02 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |
| S03 | Repo/session inputs and outputs | adapt | Partial: no demonstrated secret-export instruction | Reviewed-file inventory |  | No sensitive-fixture/redaction tests or vulnerability-absence claim |
| S04 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |
| R01 | Every proposed change | adopt | Static: scope/name intent recorded | Purpose and protected contracts |  | Human proposal disposition pending |
| R02 | Explicit-only fields | adopt | Static: both controls retained | SKILL.md:4 and agents/openai.yaml:4-5 |  | Cross-client enforcement untested |
| R03 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |
| R04 | Named mandatory called skills | not applicable | Not applicable: no required called skill | SKILL.md:9-31,108-164,196-247 |  | Applicable host guidance still governs |
| R05 | Stopping/no-op/report | adopt | Static: completion/no-op limits identified | SKILL.md:9-31,108-164,196-247 |  | No absent handoff rule invented |
| R06 | Output contract | adopt | Static: required response/files recorded | Purpose and protected contracts |  | Native workflow outcome untested |
| R07 | Document authority in this checkout | adapt | Partial: generic procedure must defer to host owners | AGENTS.md and .agents/instructions/repo.md |  | Protected root sections and .agents ownership retained |
| R08 | Source/eval/generated separation | adapt | Static: this audit separates evidence fixtures from targets | Inventory and repository exclusions |  | No generated run/output reviewed |
| R09 | Repo validation prerequisites | adapt | Partial: scoped tooling limitations documented | .agents/memory/testing/skills.md and known-issues/skills.md |  | No validator/package/live check executed |
| R10 | Upgrade consumer procedure | not applicable | Not applicable: no upgrade call/action | SKILL.md:9-31,108-164,196-247 |  | Paper audit does not activate upgrade |
| R11 | Evidence integrity | adopt | Static: source/runtime distinction retained | Report evidence limits |  | No runtime passing claim or human waiver |
| R12 | Source formatting | adopt | Static: parent byte scan found no CR/tab/trailing whitespace | Parent whole-bundle scan on 2026-10-05 |  | No source edit or formatting repair here |
| C01 | Native activation/discovery | adapt | Unresolved | Parsed metadata and provider research |  | No explicit/implicit native traces |
| C02 | Actually shipped resources | adapt | Partial: installer copies non-evals and strips evals | scripts/install.sh:40-55 and install.ps1:251-269 |  | Installed copy/file access untested |
| C03 | Codex UI scope/policy metadata | adapt | Defective UI describes different task, policy retained | SKILL.md:3,9 and agents/openai.yaml:2-5 | [SAG-011](../findings.md#sag-011-misleading-codex-sidecar-scope) | Codex UI behavior untested and sidecar not universal |
| C04 | Public examples and command validation authority | adapt | Unresolved currency/execution scope, customization labels present | SKILL.md:9,23,110,166-194,198-242 | [SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) | No external refresh or setup/deploy execution |

### guidance-review

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | All procedure text | adopt | Static: task-specific instructions | SKILL.md:8-23 |  | Runtime context cost unmeasured |
| A02 | Workflow risk and variation | adopt | Static: exact steps plus scoped judgment | SKILL.md:8-23 |  | Native workflow outcome untested |
| A03 | Model behavior claims | adapt | Unresolved | Shared native evidence matrix |  | No current intended-model runs or waivers |
| A04-F | Entry metadata | adapt | Static: YAML parsed and required strings present | SKILL.md:1-5 and metadata checkpoint |  | Native client parser untested |
| A04-N | Name format | adapt | Static: directory match, lowercase and <=64 characters | SKILL.md:2 and metadata checkpoint |  | Tightest documented VS Code condition used |
| A04-D | Description metadata | adapt | Static: nonempty <=1024 chars without XML | SKILL.md:3 and metadata checkpoint |  | Claude bounds are source-specific, not universal requirement |
| A05 | Meaningful name | adopt | Static: name identifies purpose | SKILL.md:2-3 |  | Names preserved |
| A06 | Description capability/triggers | adapt | Static: stated capability matches procedure | SKILL.md:3 and SKILL.md:8-23 |  | Actual activation not tested |
| A07 | Focused entry body | adapt | Static: body covers core task | Metadata body-length checkpoint and SKILL.md:8-23 |  | Length alone is not a defect |
| A08 | Procedure/resource selection | adapt | Static: core procedure in entry | SKILL.md:8-23 |  | Selective client loading untested |
| A09 | Specialized optional details | not applicable | Not applicable: no advanced optional procedure | SKILL.md:8-23 |  | Basic input/no-op branches reviewed separately |
| A10 | Readable same-set local references | adapt | Static: bounded traversal, external links/revisits forbidden | SKILL.md:10 |  | Actual retrieval/trust behavior untested |
| A11 | Procedure references >100 lines | not applicable | Not applicable: no qualifying reference | Reviewed-file inventory |  | No arbitrary splitting for length |
| A12 | Supplied path/text and placeholder input | adapt | Unresolved argument binding, sidecar retained | SKILL.md:4-5,10-11 and agents/openai.yaml:1-2 | [SAG-012](../findings.md#sag-012-argument-binding-and-control-adapter-evidence-gaps) | No portable placeholder/control behavior assumed |
| A13 | Sequential procedure | adopt | Static: File or text input/five categories/concise result | SKILL.md:8-23 |  | Native workflow outcome untested |
| A14 | Review response only | adapt | Static: categories/location/issue/correction/uncertainty | SKILL.md:13-23 |  | No edit or iterative application workflow implied |
| A15 | Dated product/version facts | not applicable | Not applicable: no time-sensitive product claim | SKILL.md:8-23 |  | Future repo facts still need source cross-check |
| A16 | Terminology | adopt | Static: concepts consistent within procedure | SKILL.md:8-23 |  | Native workflow outcome untested |
| A17 | Review response only | adapt | Static: categories/location/issue/correction/uncertainty | SKILL.md:13-23 |  | No edit or iterative application workflow implied |
| A18 | Review response only | adapt | Static: categories/location/issue/correction/uncertainty | SKILL.md:13-23 |  | No edit or iterative application workflow implied |
| A19 | Conditional procedure branches | adopt | Static: conditions/no-op alternatives identified | SKILL.md:8-23 |  | Native workflow outcome untested |
| A20 | Default and scoped exceptions | adopt | Static: one primary procedure | SKILL.md:8-23 |  | Native workflow outcome untested |
| A21 | Baseline-driven improvement | adapt | Unresolved | Static-only scope and approved evidence contract |  | No current matched baseline or historical output review |
| A22 | Inspectable evaluation outcomes | adapt | Unresolved: no shipped eval definition | Reviewed-file inventory |  | Absence of evals alone is not a defect |
| A23 | Real-work source provenance | adapt | Unresolved: no actual usage record reviewed | SKILL.md:8-23 |  | Synthetic fixtures/instructions are not usage evidence |
| A24 | Fresh using-session iteration | adapt | Unresolved | Static-only scope |  | No fresh native task runs |
| A25 | Team feedback condition unknown | adapt | Unresolved | No feedback corpus in scope |  | No invented claim of team use or incorporation |
| A26 | Observed navigation/activation | adapt | Unresolved | Source navigation only |  | No retrieval or activation traces |
| A27 | Bundled executable utility | not applicable | Not applicable: no utility bundled | Reviewed-file inventory |  | Host tools covered by A36 |
| A28 | Configurable script values | not applicable | Not applicable: no utility parameters | Reviewed-file inventory |  | No constants requirement imposed on prose |
| A29 | Repeated deterministic work | not applicable | Not applicable: no repeated deterministic task requiring utility established | SKILL.md:8-23 |  | No utility demanded solely for checklist compliance |
| A30 | Utility execute/read contract | not applicable | Not applicable: no procedure utility script | SKILL.md:8-23 |  | Host shell commands reviewed as prerequisites |
| A31 | Visual/spatial inspection | not applicable | Not applicable: no visual/spatial contract | SKILL.md:8-23 |  | No host image capability assumed |
| A32 | Risky application workflow | not applicable | Not applicable: only review output, no apply step | SKILL.md:13-23 |  | Do not add a write approval flow |
| A33 | External packages | not applicable | Not applicable: owned text procedure needs none | SKILL.md:8-23 |  | Tool availability remains separate |
| A34 | File access/loading | adapt | Partial: source exists and was read | Reviewed-file inventory |  | Installed/native file access not tested |
| A35 | Named MCP tools | not applicable | Not applicable: no named server/tool | Reviewed-file inventory |  | Claude syntax not transferred |
| A36 | Supplied path/text and placeholder input | adapt | Unresolved argument binding, sidecar retained | SKILL.md:4-5,10-11 and agents/openai.yaml:1-2 | [SAG-012](../findings.md#sag-012-argument-binding-and-control-adapter-evidence-gaps) | No portable placeholder/control behavior assumed |
| S01 | All bundled content | adapt | Static: purpose and contract boundaries recorded | Purpose/contracts and dependencies above |  | Source is data, host authority remains governing |
| S02 | File/tool operations | adapt | Partial: intended targets identifiable | SKILL.md:8-23 |  | No permission or application traces |
| S03 | Repo/session inputs and outputs | adapt | Partial: no demonstrated secret-export instruction | Reviewed-file inventory |  | No sensitive-fixture/redaction tests or vulnerability-absence claim |
| S04 | Readable same-set local references | adapt | Static: bounded traversal, external links/revisits forbidden | SKILL.md:10 |  | Actual retrieval/trust behavior untested |
| R01 | Every proposed change | adopt | Static: scope/name intent recorded | Purpose and protected contracts |  | Human proposal disposition pending |
| R02 | Explicit-only fields | adopt | Static: both controls retained | SKILL.md:5 and agents/openai.yaml:1-2 |  | Native enforcement untested |
| R03 | Approval/autonomy boundaries | adopt | Static: output/edit boundaries recorded | Purpose and protected contracts |  | Native enforcement and human review pending |
| R04 | Named mandatory called skills | not applicable | Not applicable: no required called skill | SKILL.md:8-23 |  | Applicable host guidance still governs |
| R05 | Traversal/concise/no-issue limits | adopt | Static: bounded traversal and explicit no-issue result | SKILL.md:10,23 |  | Native behavior untested |
| R06 | Review response only | adapt | Static: categories/location/issue/correction/uncertainty | SKILL.md:13-23 |  | No edit or iterative application workflow implied |
| R07 | Document authority in this checkout | adapt | Partial: generic procedure must defer to host owners | AGENTS.md and .agents/instructions/repo.md |  | Protected root sections and .agents ownership retained |
| R08 | Source/eval/generated separation | adapt | Static: this audit separates evidence fixtures from targets | Inventory and repository exclusions |  | No generated run/output reviewed |
| R09 | Repo validation prerequisites | adapt | Partial: scoped tooling limitations documented | .agents/memory/testing/skills.md and known-issues/skills.md |  | No validator/package/live check executed |
| R10 | Upgrade consumer procedure | not applicable | Not applicable: no upgrade call/action | SKILL.md:8-23 |  | Paper audit does not activate upgrade |
| R11 | Evidence integrity | adopt | Static: source/runtime distinction retained | Report evidence limits |  | No runtime passing claim or human waiver |
| R12 | Source formatting | adopt | Static: parent byte scan found no CR/tab/trailing whitespace | Parent whole-bundle scan on 2026-10-05 |  | No source edit or formatting repair here |
| C01 | Native activation/discovery | adapt | Unresolved | Parsed metadata and provider research |  | No explicit/implicit native traces |
| C02 | Actually shipped resources | adapt | Partial: installer copies non-evals and strips evals | scripts/install.sh:40-55 and install.ps1:251-269 |  | Installed copy/file access untested |
| C03 | Supplied path/text and placeholder input | adapt | Unresolved argument binding, sidecar retained | SKILL.md:4-5,10-11 and agents/openai.yaml:1-2 | [SAG-012](../findings.md#sag-012-argument-binding-and-control-adapter-evidence-gaps) | No portable placeholder/control behavior assumed |
| C04 | Activation/tool permissions | adapt | Unresolved: activation is not tool permission | Provider research and protected contracts |  | No permission/client enforcement traces |

### self-improve

| Check | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | All procedure text | adopt | Static: task-specific instructions | SKILL.md:8-50 and both bundled references |  | Runtime context cost unmeasured |
| A02 | Workflow risk and variation | adopt | Static: exact steps plus scoped judgment | SKILL.md:8-50 and both bundled references |  | Native workflow outcome untested |
| A03 | Model behavior claims | adapt | Unresolved | Shared native evidence matrix |  | No current intended-model runs or waivers |
| A04-F | Entry metadata | adapt | Static: YAML parsed and required strings present | SKILL.md:1-5 and metadata checkpoint |  | Native client parser untested |
| A04-N | Name format | adapt | Static: directory match, lowercase and <=64 characters | SKILL.md:2 and metadata checkpoint |  | Tightest documented VS Code condition used |
| A04-D | Description metadata | adapt | Static: nonempty <=1024 chars without XML | SKILL.md:3 and metadata checkpoint |  | Claude bounds are source-specific, not universal requirement |
| A05 | Meaningful name | adopt | Static: name identifies purpose | SKILL.md:2-3 |  | Names preserved |
| A06 | Description capability/triggers | adapt | Static: stated capability matches procedure | SKILL.md:3 and SKILL.md:8-50 and both bundled references |  | Actual activation not tested |
| A07 | Focused entry body | adapt | Static: body covers core task | Metadata body-length checkpoint and SKILL.md:8-50 and both bundled references |  | Length alone is not a defect |
| A08 | Durable/placement references and optional refactor | adopt | Static: direct textual selectors with use conditions | SKILL.md:22,28 and INSTRUCTION_STRUCTURE.md:44-65 |  | No length-only split, client loading untested |
| A09 | Durable/placement references and optional refactor | adopt | Static: direct textual selectors with use conditions | SKILL.md:22,28 and INSTRUCTION_STRUCTURE.md:44-65 |  | No length-only split, client loading untested |
| A10 | Durable/placement references and optional refactor | adopt | Static: direct textual selectors with use conditions | SKILL.md:22,28 and INSTRUCTION_STRUCTURE.md:44-65 |  | No length-only split, client loading untested |
| A11 | Procedure references >100 lines | not applicable | Not applicable: no qualifying reference | Reviewed-file inventory |  | No arbitrary splitting for length |
| A12 | Discovery and host doc ownership | adapt | Partial: git pruned, fixtures/workspaces not excluded | SKILL.md:15-16 and repo exclusions | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Generic scope must retain canonical .agents/protected host rules |
| A13 | Sequential procedure | adopt | Static: Discover/extract/place/edit/report and refactor branches | SKILL.md:8-50 and both bundled references |  | Native workflow outcome untested |
| A14 | Post-edit verification | adopt | Static: durable/scope/move/conflict/no-orphan checks | SKILL.md:43-50 and INSTRUCTION_STRUCTURE.md:68-78 |  | Grader does not prove all preserved rules |
| A15 | Dated product/version facts | not applicable | Not applicable: no time-sensitive product claim | SKILL.md:8-50 and both bundled references |  | Future repo facts still need source cross-check |
| A16 | Terminology | adopt | Static: concepts consistent within procedure | SKILL.md:8-50 and both bundled references |  | Native workflow outcome untested |
| A17 | Changes/moves/no-op report | adapt | Static: report contents vary by branch | SKILL.md:37-41 |  | Benchmark headings are scenario-specific |
| A18 | Durable lesson extraction/examples | adopt | Static: actionable recurrent specific nonduplicate bar | DURABLE_LEARNINGS.md:5-46,48-63 |  | Synthetic fixture coverage not real-task provenance |
| A19 | Conditional procedure branches | adopt | Static: conditions/no-op alternatives identified | SKILL.md:8-50 and both bundled references |  | Native workflow outcome untested |
| A20 | Default and scoped exceptions | adopt | Static: one primary procedure | SKILL.md:8-50 and both bundled references |  | Native workflow outcome untested |
| A21 | Baseline-driven improvement | adapt | Unresolved | Static-only scope and approved evidence contract |  | No current matched baseline or historical output review |
| A22 | Shipped grading/eval utility | adapt | Partial: static predicates do not prove contract preservation | evals/evals.json and grade_benchmark.py | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation) | No utility correctness/adversarial execution |
| A23 | Durable lesson extraction/examples | adopt | Static: actionable recurrent specific nonduplicate bar | DURABLE_LEARNINGS.md:5-46,48-63 |  | Synthetic fixture coverage not real-task provenance |
| A24 | Fresh using-session iteration | adapt | Unresolved | Static-only scope |  | No fresh native task runs |
| A25 | Team feedback condition unknown | adapt | Unresolved | No feedback corpus in scope |  | No invented claim of team use or incorporation |
| A26 | Observed navigation/activation | adapt | Unresolved | Source navigation only |  | No retrieval or activation traces |
| A27 | Bundled grader errors/fallbacks | adapt | Partial: absent text becomes empty, malformed timing defaults empty, metadata has fallback ID | evals/grade_benchmark.py:9-10,17-24,77-89,310-331 | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | Missing-root predicate can pass and unavailable metrics become zero |
| A28 | Fixture-specific assertion predicates | adapt | Static: command/term predicates map to declared fixture lessons, no runtime tunables | evals/grade_benchmark.py:104-291 and evals/files session notes |  | Preservation weaknesses belong to A22, no unexplained configuration constant established |
| A29 | Repeated deterministic grading | adopt | Static: reusable utility performs repeated artifact checks and writes structured grading | evals/grade_benchmark.py usage/main |  | Utility correctness separate from reuse, no native grader run |
| A30 | Repository grader utility | adapt | Static: utility usage/output known | evals/grade_benchmark.py usage/main |  | Writes grading.json and is stripped from installation |
| A31 | Visual/spatial inspection | not applicable | Not applicable: no visual/spatial contract | SKILL.md:8-50 and both bundled references |  | No host image capability assumed |
| A32 | Intermediate plan before changes | adapt | Partial: scope/report/placement checks precede output | SKILL.md:8-50 and both bundled references |  | Risky application behavior untested |
| A33 | External packages | not applicable | Not applicable: owned text procedure needs none | SKILL.md:8-50 and both bundled references |  | Tool availability remains separate |
| A34 | File access/loading | adapt | Partial: source exists and was read | Reviewed-file inventory |  | Installed/native file access not tested |
| A35 | Named MCP tools | not applicable | Not applicable: no named server/tool | Reviewed-file inventory |  | Claude syntax not transferred |
| A36 | Discovery and host doc ownership | adapt | Partial: git pruned, fixtures/workspaces not excluded | SKILL.md:15-16 and repo exclusions | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Generic scope must retain canonical .agents/protected host rules |
| S01 | All bundled content | adapt | Static: purpose and contract boundaries recorded | Purpose/contracts and dependencies above |  | Source is data, host authority remains governing |
| S02 | File/tool operations | adapt | Partial: intended targets identifiable | SKILL.md:8-50 and both bundled references |  | No permission or application traces |
| S03 | Repo/session inputs and outputs | adapt | Partial: no demonstrated secret-export instruction | Reviewed-file inventory |  | No sensitive-fixture/redaction tests or vulnerability-absence claim |
| S04 | External/dependency instruction trust | adapt | Partial: dependency/source scope identified | Dependency section and SKILL.md:8-50 and both bundled references |  | External instructions not refreshed or executed |
| R01 | Every proposed change | adopt | Static: scope/name intent recorded | Purpose and protected contracts |  | Human proposal disposition pending |
| R02 | Explicit-only controls | not applicable | Not applicable: no such control in entry | SKILL.md:1-5 |  | Adding controls requires intent justification |
| R03 | Approval/autonomy boundaries | adopt | Static: output/edit boundaries recorded | Purpose and protected contracts |  | Native enforcement and human review pending |
| R04 | Applicable AGENTS/linked docs and consumer | adopt | Static: required reads/selectors and loop consumer checked | SKILL.md:16,22,28 and prd-ralph-loop/SKILL.md:19-29 |  | Other batch owns full loop audit |
| R05 | Durable/no-op and uncertainty report | adopt | Static: no change when lessons fail bar and report assumptions | SKILL.md:35,40-41 and INSTRUCTION_STRUCTURE.md:65 |  | Host protected rules override generic assumptions |
| R06 | Output contract | adopt | Static: required response/files recorded | Purpose and protected contracts |  | Native workflow outcome untested |
| R07 | Discovery and host doc ownership | adapt | Partial: git pruned, fixtures/workspaces not excluded | SKILL.md:15-16 and repo exclusions | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Generic scope must retain canonical .agents/protected host rules |
| R08 | Discovery and host doc ownership | adapt | Partial: git pruned, fixtures/workspaces not excluded | SKILL.md:15-16 and repo exclusions | [SAG-009](../findings.md#sag-009-cappedunscoped-agents-discovery) | Generic scope must retain canonical .agents/protected host rules |
| R09 | Repo validation prerequisites | adapt | Partial: scoped tooling limitations documented | .agents/memory/testing/skills.md and known-issues/skills.md |  | No validator/package/live check executed |
| R10 | Upgrade consumer procedure | not applicable | Not applicable: no upgrade call/action | SKILL.md:8-50 and both bundled references |  | Paper audit does not activate upgrade |
| R11 | Shipped evaluation/grading claims | adopt | Defective predicates and unmeasured metrics | evals/grade_benchmark.py | [SAG-007](../findings.md#sag-007-grader-predicates-do-not-prove-preservation), [SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) | No current model/grader runs |
| R12 | Source formatting | adopt | Static: parent byte scan found no CR/tab/trailing whitespace | Parent whole-bundle scan on 2026-10-05 |  | No source edit or formatting repair here |
| C01 | Native activation/discovery | adapt | Unresolved | Parsed metadata and provider research |  | No explicit/implicit native traces |
| C02 | Actually shipped resources | adapt | Partial: installer copies non-evals and strips evals | scripts/install.sh:40-55 and install.ps1:251-269 |  | Installed copy/file access untested |
| C03 | Provider-specific adapter | not applicable | Not applicable: no sidecar/explicit-only field | SKILL.md:1-5 and inventory |  | Optional UI sidecar not universally required |
| C04 | Activation/tool permissions | adapt | Unresolved: activation is not tool permission | Provider research and protected contracts |  | No permission/client enforcement traces |

## Completion and outstanding evidence

Static source investigation, six 58-check matrices, parent canonical findings/shared-resource records, and live human proposal review are complete. The owning ticket is closed. Defects and partial/unresolved compliance stay visible; four separately routed decisions, cross-batch reconciliation, baseline selection, and native evidence remain outstanding. No runtime run or required model/client waiver occurred. Accepted proposals authorize later plan scope only; no implementation authorization is implied.

## Supporting source fingerprints

Supporting sources share baseline revision `91ba7ab941450327c8d178c27966d1150bd0b74b`. Hashes below capture the bytes examined at source-reading checkpoints, before parent record and known-issue updates. The reviewed-scope column distinguishes full reads from bounded dependency/consumer inspection. Partial inspection is not full helper audit. Audit decision/research files include working-tree planning changes and are captured as read during this review, not falsely claimed as immutable baseline contents. The evolving shared catalog is owned by parent and is not frozen here.

| Supporting source | SHA256 | Reviewed scope |
| --- | --- | --- |
| .agents/memory/INDEX.md | `af22f36d840527d0b09b7751d72efdef63a6386dfed760243b1aecbbe651fde5` | full routing guidance |
| .agents/memory/ARCHITECTURE.md | `18adb924fd5172cda1833172916cbbb5fccc254c55fc829e7f2babc23094f55c` | full repo architecture |
| .agents/memory/CONVENTIONS.md | `a6da962bc0127e428f76576c7de91bb6b7190c8ae4bbc0edaa33ccec89588bde` | full formatting boundaries |
| .agents/instructions/repo.md | `5f658f2ce9f9c97b8581d683e21ce3339f5ef61996ed1c92826ace671e69c132` | full owner guidance |
| .agents/instructions/skills.md | `9dbb3ff52bb5fa630d9825efce0682bedbd3aab890e0387d7a44f80f84435a14` | full skills guidance |
| .agents/instructions/scripts.md | `c75a1999dd62adfc93a8627c1c7f486ae507e34e51b7798ae7c795c61ac1356f` | full shell ownership guidance |
| .agents/memory/known-issues/skills.md | `df0abadf23e425d0f4c1b115a2b45a4ffa4a1c4eaee14b54fb550cfbb3109b27` | full validator limitations |
| .agents/memory/testing/skills.md | `b76425b2bce06122e0eba6c06626354cf089a60ca3549bf1f0c626dbcf2f0e92` | full validation scope |
| docs/skill-audit/tickets/review-skill-authoring-and-repository-guidance.md | `784fb513a086e3011a94cd13a0d5773e5b0123e463ad3e98e2d98c4f4533938f` | full assigned ticket |
| docs/skill-audit/tickets/choose-audit-batches-and-evidence-format.md | `83a446f1463e03550193e8636d3ee48309a30988615e50bdb7baf3df149b9105` | full approved decision |
| docs/skill-audit/tickets/set-adoption-rules-and-protected-behavior.md | `4850b02b3acc5b7041e3092286398aac52a724b634647eab597922ed6d3ae10d` | full approved decision |
| docs/skill-audit/tickets/set-audit-completion-and-implementation-gates.md | `151493967cbc1878d9801aa161c2b96325d2bfb41cfb2dafc4f54f3a47c563fe` | full approved decision |
| docs/skill-audit/research/authoring-checklist/findings.md | `c865605d8784066cec68c1d193020038750fe461d9df03d7a720e559a729d560` | full supplied source checklist |
| docs/skill-audit/research/provider-compatibility/findings.md | `fd2c4a71fed2244fc51123c830c4a52f023d0475fdd9bd3b91edfd69d42ff24a` | full supplied provider research |
| skills/skill-creator/SKILL.md | `c6815e8017fc4be2813271b005b035cea173c8be603bc949e0a3082942e5ecd3` | entry read as excluded required dependency only |
| skills/skill-creator/scripts/quick_validate.py | `67cf5703402013936c8fb75ad6a1afecd8841d45cc5e606b634eb05825fde365` | full exact validator dependency |
| skills/skill-creator/scripts/package_skill.py | `1a33059b0db1ef73375d46d513e5ea81369d2e8838c970597b0d52ddef8d1c0f` | full exact package dependency |
| scripts/install.sh | `a7cd93792b919a2773c8a79061359dc54d023381024e5a47d6be0a6f3d5e35fa` | 1-67 and 153-209 plus dependency operation search |
| scripts/install.ps1 | `9b4b245ceae22c533f26c87f6a0bf86ab150b7174a77881dbfab658e8ee2b022` | 251-269 and operation search only |
| skills/skill-creator/scripts/run_loop.py | `7bd6f674203168520517eec94c55f493c0d154339b061b4d7c0f0dad187d0f21` | module import and CLI dependency anchors only |
| skills/skill-creator/scripts/run_eval.py | `43e3b8f80dbf69c343967ba77e268fae991d9fa3ed68b32a0ff02532cd48657f` | 23-30,45-89 and CLI dependency anchors only |
| skills/skill-creator/scripts/improve_description.py | `87d864570220b699fac52da309d2d6efdb060647bfebc74f768128e646accf80` | 20-45 and CLI dependency anchors only |
| skills/skill-creator/scripts/aggregate_benchmark.py | `123ef128ea5ccc01a4b1ac212ef5567f21e9c13d3d240609780beeb3200c49aa` | 137-154,186-218,248-250,311-323 dependency anchors only |
| skills/skill-creator/eval-viewer/generate_review.py | `fc9d1b9243fe5ab6012ebd579bd76d0035de1b79fd3b969de114defab26478fb` | grading/benchmark reference search only |
| skills/skill-creator/eval-viewer/viewer.html | `a53213426ee1100441d701a3a0d49cda7a842f992d2c36463f4d3cc0258575fa` | metric consumer search only |
| skills/skill-creator/references/schemas.md | `8e8876180a8989b406a4d3edddf875b04cdfd5805cc8616686d552b11ce4455f` | 110-125,155,169-191 metric schema anchors only |
| skills/prd-ralph-loop/SKILL.md | `2cbc991e5bd29e88b6d7174565556fce75c9f4bf1f88194ebdeff6e06c356910` | 1-40 exact self-improve consumer contract only |
| skills/dotnet-upgrade/references/document-review.md | `1c775d00c8758a354496727730796f92fd1744e3463511c875bc89358393dccd` | 27 metadata comparison only |
| skills/prd/SKILL.md | `516ba841eb3b3c7e513210c65b64bdfbc7aa0437d8d113cf1be8c7f782dffce5` | 1-38 and output/workflow metadata anchors only |
| skills/spec-to-tasks/SKILL.md | `ac043a1bf2027a7ac586039b3711af23a1ec42c6ef9a7714dc66fd7de3b1f265` | 1-38 and output/workflow metadata anchors only |
| skills/to-issues/SKILL.md | `f8a72a5bc88aa830ae62b323a52b08934da52851b010984c55829a644c7f6ba6` | 1-38 and workflow metadata anchors only |
| .agents/skills/exec-plans/SKILL.md | `c9819fd42e17879fee33e0b7546b98b07b8088f0f6334b9966b180689490693c` | 1-38 and plan/output/research workflow anchors only |

## Delegation and parent verification

    subtask_id: authoring-guidance-static
    selected: {model: gpt-6.1-sol, reasoning_effort: high}
    submitted: {model: gpt-6.1-sol, reasoning_effort: high}
    executed: {model: unconfirmed, reasoning_effort: unconfirmed}
    runtime_limit: {value: 20-minute initial limit plus 10-minute extension, mechanism: parent clock/status checks and explicit extension, no interruption}
    status: completed
    output_verified: true
    routing_compliant: true

Dispatch began 2026-10-05 15:52:49 UTC. Initial-limit status was inspected before and after 16:12:49 UTC; source/proposal checkpoints were usable and the reviewer remained active. A bounded extension through 16:22:49 UTC covered matrix persistence and final verification after diagnosed tool-input limits. Completion was observed at 16:19:04 UTC. Actual runtime duration, executed settings, and usage were not reported. Source-review delegation is not a native audit baseline.

Parent checked consequential source anchors and amended ambiguity boundaries, confirmed all 45 bundle hashes against unchanged source, verified six matrices against all 58 catalog IDs, and checked formatting. R12 was added after parent found three whitespace-only violations in the Improve Skill grader; this changed audit coverage, not source. Parent canonicalized every finding, created four precise decision routes, and retained pending human states. No additional primary skill review, installer, grader, source implementation, or live evaluation was performed.

Tool Guardian rejected long prose/table shell inputs during assembly. Small direct patches and a disposable helper file with a short RTK invocation saved the records. No approval escalation or weaker safety setting was used. An initially overbroad consumer search was corrected to exclude workspaces; those matches did not become audit targets or evidence. These are evidence-assembly limits, not observed skill failures.
