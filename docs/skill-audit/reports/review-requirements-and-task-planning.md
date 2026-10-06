# Review Requirements and Task Planning

Status: static investigation complete for four skills and 232 check rows. Human proposal review complete on 2026-10-06; native evidence not run.

Source baseline: `b4d0b428aaccdc1d4f7661129c7e4c78ef85425f`. Static paper review only. No native runs, target helpers, installers, packaging, issue publication or workflow activation. The domain-modeling waiver is effort-local.

## Protected contracts

| Skill | Purpose | Preserved boundaries and deliverables |
| --- | --- | --- |
| prd | Implementation-ready requirements from conversation and codebase | Explicit invocation control and false implicit sidecar; no code/no interview; safe assumptions or blocker stop; conditional Explore; Delegate when useful; never replace existing PRD; unused suffixed scratchpad path; canonical template and stable FR/US IDs; save failure stop; final name/path/pass-fail/readiness. |
| spec-to-tasks | Requirements to independently implementable vertical slices | Delegate/conditional Explore; missing source ask/stop; unsafe conflict ask/stop before writing; output path precedence; tasks.json with T001 task IDs; false passes/empty notes; Typecheck and conditional browser criteria; no spec authoring/implementation; final count/path/Ralph readiness. |
| to-issues | Approved vertical slices on project tracker | Explicit invocation control; tracker/triage prerequisite; fetch issue body/comments; numbered breakdown and live approval before publication; dependency order and real identifiers; template and triage label; never modify/close parent. |
| architecture-design-contest | Decision-quality alternatives and recommendation before implementation | Both invocation controls; minimum 2 explorers for existing codebase and 3 architects; Delegate/Explore and current-doc requirements; structurally distinct options; read key evidence; no code/files before explicit switch; recommendation/rejected alternative/hybrid split/main tension; final human design choice. |


## Exact primary inventory

Twelve maintained primary files include evaluation definitions and their grader. Evaluation fixtures are excluded from the primary count and recorded separately below. No generated output or snapshot is a primary input. Every bundle file was read in full.

| File | Lines | SHA256 | Baseline identical | Shipment |
| --- | --- | --- | --- | --- |
| [skills/prd/SKILL.md](../../../skills/prd/SKILL.md) | 163 | `516ba841eb3b3c7e513210c65b64bdfbc7aa0437d8d113cf1be8c7f782dffce5` | Yes | Shipped by both selection routines |
| [skills/prd/agents/openai.yaml](../../../skills/prd/agents/openai.yaml) | 5 | `df3c6c1458f3f4604b8b7044a5700d23af28015009d8397bb3b55382e01d2112` | Yes | Shipped by both selection routines |
| [skills/spec-to-tasks/SKILL.md](../../../skills/spec-to-tasks/SKILL.md) | 100 | `ac043a1bf2027a7ac586039b3711af23a1ec42c6ef9a7714dc66fd7de3b1f265` | Yes | Shipped by both selection routines |
| [skills/spec-to-tasks/evals/evals.json](../../../skills/spec-to-tasks/evals/evals.json) | 55 | `9daf4ab34fb2dc792cd90656b25965270fed394f229cea88403f6a968d5f82e5` | Yes | Pruned: evals/ |
| [skills/spec-to-tasks/evals/grade_benchmark.py](../../../skills/spec-to-tasks/evals/grade_benchmark.py) | 479 | `1c3a22138ab11abe292bb38db63fcd33e5f801503cdc1f00cda47449b2db2a37` | Yes | Pruned: evals/ |
| [skills/spec-to-tasks/references/prd-handling.md](../../../skills/spec-to-tasks/references/prd-handling.md) | 25 | `7656827a1fa1247c73d0a91e55b23f124779eaf7d008c38aa1ad3245d2c24a15` | Yes | Shipped by both selection routines |
| [skills/spec-to-tasks/references/task-schema.md](../../../skills/spec-to-tasks/references/task-schema.md) | 56 | `e31db92fce84622fd0dcb54eccf5309d809ba6f6c3a47df4e7f4c6b41435cf88` | Yes | Shipped by both selection routines |
| [skills/spec-to-tasks/references/validation.md](../../../skills/spec-to-tasks/references/validation.md) | 22 | `6b0e111e06e17cdeb32b945fe8efe14dc60f1cee7a9d299991eaee105c34b8f9` | Yes | Shipped by both selection routines |
| [skills/to-issues/SKILL.md](../../../skills/to-issues/SKILL.md) | 84 | `f8a72a5bc88aa830ae62b323a52b08934da52851b010984c55829a644c7f6ba6` | Yes | Shipped by both selection routines |
| [skills/architecture-design-contest/SKILL.md](../../../skills/architecture-design-contest/SKILL.md) | 165 | `8bfa2c5af202962a5859248a49cba846c92ac20469f7904157ad4617f1a6744b` | Yes | Shipped by both selection routines |
| [skills/architecture-design-contest/agents/openai.yaml](../../../skills/architecture-design-contest/agents/openai.yaml) | 5 | `c4030a7d6d999f276657ec8a32b27cfa4c5acac0c3193a2aa39b39e686771f81` | Yes | Shipped by both selection routines |
| [skills/architecture-design-contest/evals/evals.json](../../../skills/architecture-design-contest/evals/evals.json) | 98 | `fa4ca05b1f21767b7deacf21d94cdeec82626043b0d4c9d694ea6f2fca857697` | Yes | Pruned: evals/ |

## Separately reviewed fixtures

| File | Lines | SHA256 | Baseline identical | Shipment |
| --- | --- | --- | --- | --- |
| [skills/spec-to-tasks/evals/files/task-statuses-prd.md](../../../skills/spec-to-tasks/evals/files/task-statuses-prd.md) | 13 | `ecd7c0f4810406522bdf98da6713c72f84cd6fab56503bb066478fa5275e0af4` | Yes | Pruned: evals/ |
| [skills/spec-to-tasks/evals/files/workspace-member-management-prd.md](../../../skills/spec-to-tasks/evals/files/workspace-member-management-prd.md) | 13 | `cce6c28d3d58ea18ec4583789ebc9fefb7b521c6e2c641383e9f8696a7604d37` | Yes | Pruned: evals/ |

Both fixtures are thirteen-line requirements inputs with no executing instructions or fixture entry points. Task Statuses covers persistent defaults, updates, badge and filter behavior. Workspace Member Management covers invite, role change, revoke and audit behavior. Their exact useful behavior requirements can survive the obsolete evaluation output oracle repair; no fixture was executed.

## Bounded dependency fingerprints

Whole-file SHA256 identifies each dependency; the read scope column bounds the content reviewed. Hashing a whole file does not claim full content audit. No imported helper became primary scope.

| Dependency | SHA256 | Exact read scope / owner |
| --- | --- | --- |
| [skills/delegate-to-subagents/SKILL.md](../../../skills/delegate-to-subagents/SKILL.md) | `670318c390b55da662f617e2e1d2538da299f4f151b3c82f03bb9443ffa9ef32` | Full; required consumer procedure; owner Delegation and Discovery |
| [skills/explore/SKILL.md](../../../skills/explore/SKILL.md) | `5fefe9f992e78ddac3642698d1ea824f54e1216c7b63b42441640b02b826f83b` | Full; context and architecture consumer branches; owner Delegation and Discovery |
| [skills/subagent-model-router/SKILL.md](../../../skills/subagent-model-router/SKILL.md) | `7de60f23f3152164ee4b9dd0c7caa329b9aa42f57f44677c14f54b26b61a5ac1` | Full; transitive required routing; owner Delegation and Discovery |
| [skills/subagent-model-router/reference/model-catalog.md](../../../skills/subagent-model-router/reference/model-catalog.md) | `49a4f81bace60ad3d68842e677e6163789813572366adf55cee9e76e8697a3b7` | Full; provisional task/configuration and provider-family constraint only; remote status unverified |
| [agents/code-explorer.md](../../../agents/code-explorer.md) | `e6d92f5082b25afa56bdfc4715f87bb894f42ae38285a2355b2788e7d55a0775` | Full; named role existence and bounded exploration deliverable |
| [agents/code-architect.md](../../../agents/code-architect.md) | `1739e7ccef638cb2cb66479e4212179f33a3ce5f472d4a9c20f971e6aad48aaa` | Full; named role existence and design-only brief compatibility |
| [skills/prd-ralph/SKILL.md](../../../skills/prd-ralph/SKILL.md) | `f78491b499431fa951db0573d073efb654655471641166cce40776d8d38ce703` | Full; tasks consumer field and eligibility contracts only; owner Execution and Handoff |
| [skills/prd-ralph-loop/SKILL.md](../../../skills/prd-ralph-loop/SKILL.md) | `2cbc991e5bd29e88b6d7174565556fce75c9f4bf1f88194ebdeff6e06c356910` | Full; tasks consumer, sequential fresh-task orchestration and blindness only; owner Execution and Handoff |
| [skills/dotnet/SKILL.md](../../../skills/dotnet/SKILL.md) | `4160d151f90c0fc9b24b6f21d5ba80bf316d9ad1f27a2091dcf342dbe683c93c` | Line 3 only from scoped consumer search; framework-context precedence; owner .NET batch |
| [scripts/install.sh](../../../scripts/install.sh) | `a7cd93792b919a2773c8a79061359dc54d023381024e5a47d6be0a6f3d5e35fa` | Lines 1-85; copy_skills selection/pruning and Markdown role copy only |
| [scripts/install.ps1](../../../scripts/install.ps1) | `9b4b245ceae22c533f26c87f6a0bf86ab150b7174a77881dbfab658e8ee2b022` | Lines 240-284; Copy-Skills selection/pruning and role copy only |
| [scripts/install-codex-agents.py](../../../scripts/install-codex-agents.py) | `f2442b0f64f93fbcb3fe909d75b697209bb7931a26c9e2092838408eedd3af01` | Lines 174-187,280-291; top-level role selection/TOML rendering only |
| [.editorconfig](../../../.editorconfig) | `a50eaf42f688b51cc2c008c7288b9dc26030a38462ee033d5b0b5d3477ec1ce2` | Full; source formatting contract |
| [docs/skill-audit/research/provider-compatibility/findings.md](../../../docs/skill-audit/research/provider-compatibility/findings.md) | `fd2c4a71fed2244fc51123c830c4a52f023d0475fdd9bd3b91edfd69d42ff24a` | Full; dated approved comparison, not refreshed provider research |

### Supporting audit records

These record hashes capture this read checkpoint, not permanent source or behavioral snapshots. Parent-owned records may change during coordination.

| Record | SHA256 | Read scope |
| --- | --- | --- |
| [.agents/memory/INDEX.md](../../../.agents/memory/INDEX.md) | `af22f36d840527d0b09b7751d72efdef63a6386dfed760243b1aecbbe651fde5` | Full orientation |
| [.agents/memory/ARCHITECTURE.md](../../../.agents/memory/ARCHITECTURE.md) | `18adb924fd5172cda1833172916cbbb5fccc254c55fc829e7f2babc23094f55c` | Full orientation |
| [.agents/memory/CONVENTIONS.md](../../../.agents/memory/CONVENTIONS.md) | `a6da962bc0127e428f76576c7de91bb6b7190c8ae4bbc0edaa33ccec89588bde` | Full orientation |
| [.agents/instructions/repo.md](../../../.agents/instructions/repo.md) | `5f658f2ce9f9c97b8581d683e21ce3339f5ef61996ed1c92826ace671e69c132` | Full reporting boundary and checkpoint policy |
| [.agents/instructions/skills.md](../../../.agents/instructions/skills.md) | `9dbb3ff52bb5fa630d9825efce0682bedbd3aab890e0387d7a44f80f84435a14` | Full scope, controls and benchmark separation |
| [.agents/memory/known-issues/skills.md](../../../.agents/memory/known-issues/skills.md) | `95fef495fc78aa946319c78d2514ebd53a307f34101ffbe23f4e83b57a19aa30` | Full existing defect routing |
| [.agents/memory/testing/skills.md](../../../.agents/memory/testing/skills.md) | `b76425b2bce06122e0eba6c06626354cf089a60ca3549bf1f0c626dbcf2f0e92` | Full; commands are audit material, not run |
| [docs/skill-audit/tickets/review-requirements-and-task-planning.md](../../../docs/skill-audit/tickets/review-requirements-and-task-planning.md) | `dbd091537f0996b0461e3d3295533f454a6b4956e41048ada4a7028eacc4585d` | Full assignment |
| [docs/skill-audit/tickets/set-adoption-rules-and-protected-behavior.md](../../../docs/skill-audit/tickets/set-adoption-rules-and-protected-behavior.md) | `4850b02b3acc5b7041e3092286398aac52a724b634647eab597922ed6d3ae10d` | Full closed policy |
| [docs/skill-audit/tickets/choose-audit-batches-and-evidence-format.md](../../../docs/skill-audit/tickets/choose-audit-batches-and-evidence-format.md) | `83a446f1463e03550193e8636d3ee48309a30988615e50bdb7baf3df149b9105` | Full closed policy |
| [docs/skill-audit/tickets/set-audit-completion-and-implementation-gates.md](../../../docs/skill-audit/tickets/set-audit-completion-and-implementation-gates.md) | `151493967cbc1878d9801aa161c2b96325d2bfb41cfb2dafc4f54f3a47c563fe` | Full closed policy |
| [docs/skill-audit/tickets/set-audit-evidence-and-model-coverage.md](../../../docs/skill-audit/tickets/set-audit-evidence-and-model-coverage.md) | `e22ffbf2d4d271b23b1ccf8f73203df04bd0894afbff9a4a6bebc84780f446b8` | Full closed policy |
| [docs/skill-audit/coverage.md](../../../docs/skill-audit/coverage.md) | `ffa6c5b4ea96f52e3de81b2918e48f2d1bd372349cb996b9787bc275159e5180` | Check catalog and scope/exclusion/shared-record sections |
| [docs/skill-audit/findings.md](../../../docs/skill-audit/findings.md) | `3eaf0ba9b1d8713c7089ed4e8015b33c5bbb699c219b847fe696b0bdc07b7c7e` | Scoped index/search and lines 140-173,306-330; existing SAG-008/DD-004 ownership only |
| [docs/skill-audit/reports/review-quality-and-harness-skills.md](../../../docs/skill-audit/reports/review-quality-and-harness-skills.md) | `5d1f9234ede58df3c678168f99b12c8c4efa14ad31ceabbf80bfcde4dc294fe0` | Lines 1-150; record structure and shared findings example |
| [docs/skill-audit/reports/review-delegation-and-discovery.md](../../../docs/skill-audit/reports/review-delegation-and-discovery.md) | `1d83f8786b598132f47d29c063d3eb5e49d4b8ebe95322d25a2b18ed1118e4b9` | Scoped matching consumer, shared metric/failure and ownership lines only |

## Consumer and path checks

| Consumer | Exact source | Result and limit |
| --- | --- | --- |
| PRD -> Spec | prd/SKILL.md:36,38-146; spec-to-tasks/SKILL.md:38-39; references/prd-handling.md:5-25 | Canonical PRD sections and IDs align; downstream task extraction preserves mandatory versus recommended order and excludes out-of-scope items. No native conversion occurred. |
| Spec -> Ralph | spec-to-tasks/references/task-schema.md:9-55; prd-ralph/SKILL.md:50,67-82,95-100 | tasks array and description/criteria/files/guidance/pass/priority fields align. Ralph accepts absent dependsOn as no dependencies; this does not justify adding an unapproved required field or retaining the evals userStories schema. Actual readiness remains untested. |
| PRD / Spec -> Delegate and Explore | prd/SKILL.md:16,29-30; spec-to-tasks/SKILL.md:35,40; explore/SKILL.md:13-15; delegate-to-subagents/SKILL.md:17,85-110,152-177 | Named maintained helpers exist; conditional context acquisition and useful delegation align with narrow direct reads and routing. Routing and approval metadata belong to orchestrator. Native host naming/access untested. |
| Architecture -> Explore / roles / Delegate | architecture-design-contest/SKILL.md:41-50,58-86,140-142; explore/SKILL.md:13-15,32-33; agents/code-explorer.md:1-5,46-55; agents/code-architect.md:1-5,21-34 | Both named role sources exist. Contest-specific evidence/output briefs can narrow general roles. Reachable narrow-context branch conflict is RPT-003; role availability in installed hosts remains untested. |
| Architecture -> Router / model diversity | architecture-design-contest/SKILL.md:58; router/SKILL.md:33-48,94-112; model-catalog.md:12-27 | Different families are a preference when available; required exact route/capability floor remains protected. No conflicting mandatory provider choice established; no model/provider availability claim made. |
| To Issues -> tracker / setup | to-issues/SKILL.md:11,17,51-57,84 | Tracker and labels must be known and publication follows approved breakdown. setup-matt-pocock-skills is absent from maintained skills inventory. Host-specific installed existence unverified. Preserve publication approval and parent non-mutation. |
| PRD / Spec -> browser helper | prd/SKILL.md:70,105; spec-to-tasks/SKILL.md:81-84; references/validation.md:17 | Literal playwright-cli helper is absent from this repository skill source. UI verification requirement remains protected. External/host supply and supported mapping require a decision, not inferred universal absence. |
| Installer -> four bundles | install.sh:40-55; install.ps1:251-276 | Nine primary entry/reference/sidecar files ship; three primary eval resources and two fixtures are pruned. No entry links a stripped eval as runtime resource. README/license and workspace/archive exclusions preserved exactly. No installer execution. |
| Role installer -> named roles | install.sh:58-61; install.ps1:279-284; install-codex-agents.py:174-187,280-291 | Markdown roles are copied to Copilot/Gemini; top-level definitions feed Codex TOML. Selection source is not proof of actual installed access or dispatch support. |
| Other consumer | dotnet/SKILL.md:3 | .NET context precedes relevant PRD workflow. Bounded description search only; full .NET audit remains with its owner. |

Consumer searches used `**/*-workspace/**`, `**/evals/**` and `**/archive/**` exclusions. Fourteen enumerated bundle files establish assigned inventory, not dependency closure. No upstream refresh, provenance recovery, imported-primary review, external issue creation or current-doc research occurred. Required cross-batch ownership remains with existing owners.

## Per-skill source summaries

### prd source

Owned files: SKILL.md and agents/openai.yaml, both shipped. Parsed name is `prd`; description is 185 characters. Entry is 163 lines with one inline canonical template. Controls are SKILL.md:4 and sidecar:4-5. Purpose/triggers are :3,9. No implementation, no interview, safe assumptions or stop, verified names, conditional Explore and never-overwrite rules are :13-21. Save and collision suffix are :23-25; ordered workflow/final response :29-36; observable outcome/error/test/rollout contracts :73-140; explicit validation :150-163. Sidecar says create/manage while body creates a new PRD; no rename/update authorization inferred from UI wording. No bundled eval exists, which limits evidence but is not automatically defective. Browser-helper mapping and local scratchpad versus active-doc placement remain qualified below.

### spec-to-tasks source

Owned primary files: SKILL.md, references/prd-handling.md, references/task-schema.md, references/validation.md, evals/evals.json and evals/grade_benchmark.py. Two fixture Markdown inputs are separate. Parsed name is `spec-to-tasks`; description is 165 characters. No explicit invocation-disable or sidecar exists. Inputs/output precedence are :10-31; extraction/delegation/context/conflict workflow :35-49; vertical/verifiable slice rules :53-62; criteria, exact-command discipline and browser branch :66-86; file confidence :88-92; final count/path/readiness :94-100. Three references load directly at :38,47-48 and are 25,56,22 lines. Four evals parse but use obsolete output contracts (RPT-001); the standard-library grader parses as Python AST, was never run and is not part of installed runtime resources. Its useful predicates and exact invalid/unknown measurement decisions are distinct.

### to-issues source

Sole owned file: SKILL.md, shipped. Parsed name is `to-issues`; description is 128 characters. Explicit invocation control :4; no sidecar. Purpose :3,9; missing tracker/label setup dependency :11; fetch existing issue body/comments :17; optional codebase/domain/ADR context :19-23; vertical slices/prefactoring :25-35; numbered breakdown and live approval :37-51; publish approved slices in dependency order with labels :53-57; exact Parent/What to build/Acceptance/Blocked by template :59-82; never close or modify parent :84. No bundled eval or script. Issue-body content is task data; permissions and actual connector/tool selection remain host-specific. No publication was performed.

### architecture-design-contest source

Owned files: SKILL.md, agents/openai.yaml and evals/evals.json; eval is pruned. Parsed name is `architecture-design-contest`; description is 470 characters. Both controls are :4 and sidecar:4-5. Purpose/success :9-19; limited questions/assumptions :23-35; existing-code minimum-two exploration with cited-file reads, or greenfield current research :39-54; minimum-three architects and distinct briefs :58-86; readable presentation/comparison :88-112; opinionated recommendation, rejected alternative, hybrid boundary and final choice :114-138; required Delegate :140-142; output shape :144-156; no file/code changes before explicit switch :163. Six evals parse. Absolute source paths and protected narrow-helper branch are recorded below. No cited remote content, family-diversity gain, native tool consent or actual independent design diversity was verified.

## Findings and recorded dispositions

The [single register](../findings.md) owns all five findings. Source investigation, parent reconciliation and live proposal review are complete. The [batch Resolution](../tickets/review-requirements-and-task-planning.md#resolution) records accepted repairs and retained routes. Three underlying behavior questions remain open and unblocked; retention selects no behavior.

- [RPT-001: Spec evaluations require obsolete schema and horizontal tasks](../findings.md#rpt-001-spec-evaluations-require-obsolete-schema-and-horizontal-tasks).
- [RPT-002: To Issues names an unshipped setup helper](../findings.md#rpt-002-to-issues-names-an-unshipped-setup-helper).
- [RPT-003: Architecture Contest conflicts with Explore's narrow branch](../findings.md#rpt-003-architecture-contest-conflicts-with-explores-narrow-branch).
- [RPT-004: Architecture evaluations bind local absolute fixture paths](../findings.md#rpt-004-architecture-evaluations-bind-local-absolute-fixture-paths).
- [RPT-005: UI planning prescribes an unshipped browser helper](../findings.md#rpt-005-ui-planning-prescribes-an-unshipped-browser-helper).

## Accepted additions to existing shared findings

[SAG-008](../findings.md#sag-008-unmeasured-metrics-become-zero) and [DD-004](../findings.md#dd-004-graders-can-announce-success-without-grading-runs-and-do-not-validate-json-shape) own the additional Spec to Tasks producer/protocol evidence. Accepted additional target is exactly `skills/spec-to-tasks/evals/grade_benchmark.py`. The human accepted this addition on 2026-10-06, retaining earlier scope for nine metric producers and six protocol graders. Unknown representation and failure outcomes remain unresolved. Measured character counts, useful predicates and production task contracts remain protected.

## Evidence limits and positive results

All four names match directories, have valid required string YAML metadata, are below 64 characters and preserve existing controls. No bundled primary/fixture file has CR bytes or trailing whitespace. PRD has strong canonical definition, never-overwrite, no invention, risk/error/test and save/final-response rules. Spec has direct short references, precise JSON defaults, safe conflict stopping and output-path precedence. To Issues has live breakdown approval, real dependency IDs and parent non-mutation. Architecture has structurally distinct designs, key-file reads, explicit trade-off/rejected-alternative/hybrid explanation and design-only scope. None proves performed workflow, passing behavior or universal control enforcement.

No bundled eval exists for PRD or To Issues. Architecture has six inspectable paper scenarios with no grader; Spec has four and one grader. Missing evaluation files, entry length or lack of extra examples are not automatically defects. Native explicit/allowed-implicit/negative/failure coverage and seven-model medium-effort repetitions remain later evidence obligations; no skill has been selected by this report. Copilot CLI/VS Code and Gemini comparisons use the dated approved local research only. Desktop, remote documentation and current provider versions are unverified. Absolute-path architecture resources are dependency claims, not read upstream contents.

PRD's scratchpad save path is the published default. SKILL.md:17 requires checking workspace conventions, and this checkout's repo.md:8 requires active research/planning docs under docs/<effort>/. Apply instruction priority to adapt the save location within this checkout while retaining unused-path suffixes, no-overwrite behavior and the final exact-path handoff. This is a scoped adaptation to the current workspace, not a global output rewrite or separate behavior proposal. No result was written by an audited workflow and actual path/save behavior remains untested.

## Per-skill coverage matrices

Each matrix accounts for the exact 58 IDs and descriptive labels in [coverage.md](../coverage.md#check-catalog). Seven columns keep criterion selection, compliance, source evidence, findings and gaps separate. `adopt`/`adapt` selects an audit criterion. Static completeness is not passing compliance, native evidence or human acceptance. Sources/strength/applicability are owned by the catalog; evidence paths below are relative to each skill unless another root is named. Canonical findings have human dispositions and shared-target scope is accepted; actual behavior/representation/protocol choices remain pending.

### prd

| Check ID and label | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 - Concise task-specific instructions | Task-specific instruction body | adopt | Static: focused purpose and procedural instructions | SKILL.md:9-163 |  | Context/token cost unmeasured |
| A02 - Specificity fits risk and variation | Planning decisions with protected boundaries | adapt | Static: constraints leave task-specific judgment | SKILL.md:9-163 |  | Decision quality untested |
| A03 - Intended model coverage | Intended model behavior | adapt | Unresolved: no native model runs | SKILL.md:2-4; evidence ticket resolution |  | No selected cases or seven-model repetitions |
| A04-F - SKILL.md and parsed required YAML | Entry file and required YAML strings | adapt | Static: parsed name/description strings | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N - Name syntax and length | Directory/name syntax and bound | adapt | Static: matching lowercase kebab-case; below 64 chars | SKILL.md:2 |  | Native name resolution untested |
| A04-D - Description metadata bounds | Required nonempty description | adapt | Static: 185 characters; no XML tags | SKILL.md:3 |  | Claude 1024 bound remains source-specific |
| A05 - Meaningful consistent name | Meaningful identity | adopt | Static: preserved name matches task purpose | SKILL.md:2-9 |  | No rename proposed |
| A06 - Useful bounded description | Purpose and trigger metadata | adapt | Static: bounded trigger description | SKILL.md:3 |  | Activation traces unrun |
| A07 - Focused entry body | Focused entry body | adapt | Static: 163-line entry has task-focused structure | SKILL.md:9-163 |  | Line count advisory; no automatic failure |
| A08 - Progressive disclosure | Inline canonical template plus conditional helpers | adapt | Static: essential rules stay in entry | SKILL.md:13-36,38-146 |  | No reference split required by length |
| A09 - Advanced detail selection | No optional advanced resource branch | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A10 - Direct reference navigation | Named helper navigation | adapt | Partial: source dependencies checked | SKILL.md:9-163 |  | Host skill-name resolution untested |
| A11 - Long-reference navigation | No bundled reference longer than 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A12 - Descriptive portable paths | Output and dependency paths | adapt | Partial: source path contracts inspected | SKILL.md:9-163 |  | Installed/host access untested |
| A13 - Sequential workflow and progress | Draft, consistency, resolve, save, handoff | adopt | Static: ordered eight-step workflow | SKILL.md:29-36 |  | Native sequence untested |
| A14 - Quality feedback loop | PRD consistency and readiness | adopt | Static: explicit cross-section validation and checklist | SKILL.md:33-35,148-163 |  | Self-reported pass would need artifact evidence |
| A15 - Dated facts and legacy separation | No fixed dated vendor/version facts in owned source | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A16 - Consistent terminology | Task terminology | adopt | Static: consistent workflow terms | SKILL.md:9-163 |  | Runtime language unobserved |
| A17 - Output template fidelity | Canonical PRD sections and IDs | adopt | Static: inline full template and FR/US mapping | SKILL.md:38-146 |  | No written PRD inspected |
| A18 - Representative examples | Story and test-target shapes | adapt | Static: US example and named test target pattern | SKILL.md:59-72,128-132 |  | Representative success/failure narratives unrun |
| A19 - Conditional branches | Missing context/unsafe assumptions/path collision | adopt | Static: Explore, blocker stop and numeric suffix | SKILL.md:14-16,25,34 |  | No collision or failure run |
| A20 - Recommended default and exceptions | No interview and reasonable assumptions | adopt | Static: default and unsafe exception explicit | SKILL.md:14,46-48 |  | Assumption quality untested |
| A21 - Baseline-driven improvement | Baseline-driven improvement | adapt | Unresolved: source snapshot is not baseline execution | SKILL.md:1-163 |  | No baseline/candidate comparison |
| A22 - Observable inspectable evaluations | Inspectable evaluation evidence | adapt | Unresolved: no bundled eval | SKILL.md:1-163 |  | Absence is evidence limit, not automatic defect |
| A23 - Reusable knowledge from real work | Reusable planning knowledge | adapt | Static: reusable method; history unverified | SKILL.md:9-163 |  | No real-task learning corpus inspected |
| A24 - Fresh-session real-task iteration | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | SKILL.md:1-163 |  | No native runs |
| A25 - Team feedback | Team-use feedback | adapt | Unresolved: no feedback corpus inspected | SKILL.md:1-163 |  | Source is not team-use evidence |
| A26 - Observed navigation and activation | Observed activation/navigation | adapt | Unresolved: no native loading trace | SKILL.md:1-163 |  | Explicit/allowed-implicit/negative cases later |
| A27 - Script error and fallback handling | No bundled executable resources | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A28 - Explained non-obvious constants | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A29 - Reusable deterministic utilities | No repeated deterministic operation needing utility | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A30 - Execute versus read script contract | No named or bundled script execution | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A31 - Visual inspection where useful | UI requirements include browser verification | adapt | Partial: named browser helper absent locally | SKILL.md:70,105 | RPT-005 | External supply/mapping unresolved |
| A32 - Validated intermediate plan | Planning before consequential implementation | adapt | Static: intermediate structured output/control gate | SKILL.md:9-163 |  | No performed plan/approval evidence |
| A33 - Package assumptions | No external package imports required | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A34 - Actual file-access/loading evidence | Source and installed loading claims | adapt | Partial: exact source reads and hashes | Owned inventory; installer consumer table |  | No installed/native load |
| A35 - Qualified MCP tool references | No literal MCP tool names in source | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| A36 - Tool/package prerequisites | Explore/Delegate/browser helpers | adapt | Partial: maintained helpers exist; browser name absent | SKILL.md:16,29-30,70,105 | RPT-005 | Host-specific browser helper availability unverified |
| S01 - Purpose and trust boundaries | Task/source trust boundary | adapt | Static: bounded purpose and output intent | SKILL.md:9-163 |  | No malicious-input test or security guarantee |
| S02 - Unexpected network/file/tool access | Workflow file/tool/network access | adapt | Partial: named targets and scope inspected | SKILL.md:9-163 |  | Native permissions/access untested |
| S03 - Sensitive-data handling | Planning/source content may contain sensitive data | adapt | Partial: output content has no explicit secret filtering | SKILL.md:9-163 |  | Host no-secret rule retained; no sensitive fixtures run |
| S04 - External instruction trust | Source requirements and helper instruction trust | adapt | Partial: approved source authority boundaries inspected | SKILL.md:9-163 |  | External content treated as data; adversarial handling untested |
| R01 - Preserve intended scope, names and triggers | Intended scope/name/triggers | adopt | Static: protected purpose recorded | SKILL.md:2-9; protected contracts |  | No behavior redesign authorized |
| R02 - Preserve invocation controls | Both explicit-invocation adapters | adopt | Static: both controls retained | SKILL.md:4; agents/openai.yaml:4-5 |  | Actual required-client enforcement untested |
| R03 - Approval and autonomy boundaries | Approval/autonomy boundaries | adopt | Static: exact current boundaries recorded | SKILL.md:9-163 |  | No inferred new permission; native enforcement untested |
| R04 - Required dependencies and delegation | Context/delegation/UI dependency | adopt | Partial: Explore/Delegate present; browser mapping unknown | SKILL.md:16,29-30,70,105 | RPT-005 | Required UI outcome retained |
| R05 - Stopping and handoff rules | Unsafe/conflict/save-failure stop | adopt | Static: explicit stops and readiness handoff | SKILL.md:14,25,34,36 |  | No stopping trace |
| R06 - Output contracts | Never-overwrite PRD and final status | adopt | Static: suffixed unused path and final fields | SKILL.md:20,25,36,161-163 |  | Save/run not performed |
| R07 - Repository document authority and edit boundaries | Local active-doc placement versus published scratchpad default | adapt | Static: applicable workspace docs/effort rule overrides published default | SKILL.md:17,25; .agents/instructions/repo.md:8 |  | Scope only this checkout; preserve collision/no-overwrite/final path; actual save untested |
| R08 - Benchmark artifact/source separation | Primary versus fixtures/generated outputs | adopt | Static: scoped inventory excludes generated/history | Exact inventory; .agents/instructions/skills.md |  | No benchmark artifacts created |
| R09 - Scoped validation and prerequisites | Skill-change validation prerequisite | adapt | Static: no skill source edit; paper checks only | .agents/memory/testing/skills.md; verification record |  | No validator/packaging run claimed |
| R10 - Upgrade paper-review boundary | No Upgrade instructions or consumer proposal | not applicable | Not applicable: condition absent | SKILL.md:1-163 |  | No behavior claim |
| R11 - Evidence and grading integrity | Static versus behavioral evidence | adapt | Partial: report separates evidence classes | Evidence limits; owned inventory |  | No native grades/traces or human acceptance |
| R12 - Source formatting | Repository source formatting | adopt | Static: no CR/trailing whitespace in owned files | Non-mutating byte/line checks; .editorconfig |  | Authored report checked separately |
| C01 - Discovery and activation contract | Required-client discovery/activation | adapt | Partial: metadata source checked | SKILL.md:1-5; dated provider comparison |  | Native activation and discovery untested |
| C02 - Actual shipped resource set | Actual shipped source selection | adapt | Static: non-eval resources ship; evals pruned | Installer consumer table; exact inventory |  | Actual installed access untested |
| C03 - Client-specific metadata adapters | Codex sidecar versus other hosts | adapt | Partial: false implicit adapter; create/manage UI wording broader | agents/openai.yaml:2-5; SKILL.md:20,25 |  | No management/overwrite scope inferred |
| C04 - Tool and activation consent | Tool and activation consent | adapt | Unresolved: activation is not portable permission | Dated provider comparison; protected contracts |  | Actual consent/tool grants untested |

### spec-to-tasks

| Check ID and label | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 - Concise task-specific instructions | Task-specific instruction body | adopt | Static: focused purpose and procedural instructions | SKILL.md:9-100 |  | Context/token cost unmeasured |
| A02 - Specificity fits risk and variation | Planning decisions with protected boundaries | adapt | Static: constraints leave task-specific judgment | SKILL.md:9-100 |  | Decision quality untested |
| A03 - Intended model coverage | Intended model behavior | adapt | Unresolved: no native model runs | SKILL.md:2-4; evidence ticket resolution |  | No selected cases or seven-model repetitions |
| A04-F - SKILL.md and parsed required YAML | Entry file and required YAML strings | adapt | Static: parsed name/description strings | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N - Name syntax and length | Directory/name syntax and bound | adapt | Static: matching lowercase kebab-case; below 64 chars | SKILL.md:2 |  | Native name resolution untested |
| A04-D - Description metadata bounds | Required nonempty description | adapt | Static: 165 characters; no XML tags | SKILL.md:3 |  | Claude 1024 bound remains source-specific |
| A05 - Meaningful consistent name | Meaningful identity | adopt | Static: preserved name matches task purpose | SKILL.md:2-9 |  | No rename proposed |
| A06 - Useful bounded description | Purpose and trigger metadata | adapt | Static: bounded trigger description | SKILL.md:3 |  | Activation traces unrun |
| A07 - Focused entry body | Focused entry body | adapt | Static: 100-line entry has task-focused structure | SKILL.md:9-100 |  | Line count advisory; no automatic failure |
| A08 - Progressive disclosure | PRD branch/schema/validation references | adopt | Static: direct resources selected in workflow | SKILL.md:38,47-48 |  | Native resource reads untested |
| A09 - Advanced detail selection | Only PRD-style input needs PRD handling | adopt | Static: conditional reference rule | SKILL.md:38; references/prd-handling.md:3 |  | Raw-spec branch unrun |
| A10 - Direct reference navigation | Three directly linked references | adopt | Static: all paths exist and ship | SKILL.md:38,47-48 |  | No installed load trace |
| A11 - Long-reference navigation | No bundled reference longer than 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-100 |  | No behavior claim |
| A12 - Descriptive portable paths | Output precedence/direct paths | adapt | Partial: production paths valid; eval paths target wrong contract | SKILL.md:23-31; evals/evals.json:6-52 | RPT-001 | No observed conversion |
| A13 - Sequential workflow and progress | Multi-step planning workflow | adopt | Static: ordered steps and deliverables | SKILL.md:9-100 |  | Performed sequence untested |
| A14 - Quality feedback loop | Tasks validation before save | adopt | Static: dedicated 18-item checklist | SKILL.md:48-49; references/validation.md:5-22 |  | Checklist execution unverified |
| A15 - Dated facts and legacy separation | No fixed dated vendor/version facts in owned source | not applicable | Not applicable: condition absent | SKILL.md:1-100 |  | No behavior claim |
| A16 - Consistent terminology | Production tasks versus eval stories | adapt | Defective: eval terminology encodes different schema | references/task-schema.md:9-55; evals/evals.json:6-52 | RPT-001 | Do not rename production tasks to pass eval |
| A17 - Output template fidelity | tasks.json template fidelity | adapt | Defective: production schema and eval loader disagree | references/task-schema.md:9-55; evals/grade_benchmark.py:102-117,148-151 | RPT-001 | Current-contract fixture/oracle design needed |
| A18 - Representative examples | Schema example plus four evals | adapt | Defective: horizontal/storage-first examples rewarded | SKILL.md:53-62; evals/evals.json:8-15,47-52 | RPT-001 | Useful fixture behavior requirements retained |
| A19 - Conditional branches | Input/conflicts/PRD/UI versus backend | adapt | Partial: production branches clear; eval splits violate contract | SKILL.md:36-46,81-86; evals/evals.json:47-52 | RPT-001 | Unsafe branch stops untested |
| A20 - Recommended default and exceptions | Defaults and alternatives | adapt | Static: task-specific defaults | SKILL.md:9-100 |  | Default suitability untested |
| A21 - Baseline-driven improvement | Baseline-driven improvement | adapt | Unresolved: source snapshot is not baseline execution | SKILL.md:1-100 |  | No baseline/candidate comparison |
| A22 - Observable inspectable evaluations | Four inspectable prompts and grader | adapt | Defective: obsolete schema and unmeasured metrics | evals/evals.json:6-52; evals/grade_benchmark.py:52,62-72,102-117 | RPT-001; SAG-008 (accepted target) | No grades/traces; exact oracle and representation choices pending |
| A23 - Reusable knowledge from real work | Reusable planning knowledge | adapt | Static: reusable method; history unverified | SKILL.md:9-100 |  | No real-task learning corpus inspected |
| A24 - Fresh-session real-task iteration | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | SKILL.md:1-100 |  | No native runs |
| A25 - Team feedback | Team-use feedback | adapt | Unresolved: no feedback corpus inspected | SKILL.md:1-100 |  | Source is not team-use evidence |
| A26 - Observed navigation and activation | Observed activation/navigation | adapt | Unresolved: no native loading trace | SKILL.md:1-100 |  | Explicit/allowed-implicit/negative cases later |
| A27 - Script error and fallback handling | Grader error/no-run handling | adapt | Defective: shape assumptions and empty-loop success | evals/grade_benchmark.py:17-30,52,91-94,116-117,464-475 | DD-004 (accepted target) | Protocol choice pending; target scope accepted; no execution |
| A28 - Explained non-obvious constants | Grader timing/metric defaults | adapt | Defective: unknown measurements zero-filled | evals/grade_benchmark.py:52,62-72 | SAG-008 (accepted target) | Representation/consumer choice pending |
| A29 - Reusable deterministic utilities | Reusable deterministic grader | adapt | Static: utility exists; schema/oracle defects recorded | evals/grade_benchmark.py:102-439 | RPT-001; DD-004 (accepted target) | No helper execution |
| A30 - Execute versus read script contract | Eval utility distinct from runtime procedure | adapt | Static: CLI/main exist outside shipped runtime | evals/grade_benchmark.py:454-479; SKILL.md:35-49 |  | Audit read only; no execution authorization |
| A31 - Visual inspection where useful | UI-visible task criteria | adapt | Partial: named browser helper absent locally | SKILL.md:81-86; references/validation.md:17 | RPT-005 | Host browser mapping unverified |
| A32 - Validated intermediate plan | Planning before consequential implementation | adapt | Static: intermediate structured output/control gate | SKILL.md:9-100 |  | No performed plan/approval evidence |
| A33 - Package assumptions | Grader uses only standard-library imports | not applicable | Not applicable: condition absent | evals/grade_benchmark.py:3-7 |  | No behavior claim |
| A34 - Actual file-access/loading evidence | Source and installed loading claims | adapt | Partial: exact source reads and hashes | Owned inventory; installer consumer table |  | No installed/native load |
| A35 - Qualified MCP tool references | No literal MCP tool names in source | not applicable | Not applicable: condition absent | SKILL.md:1-100 |  | No behavior claim |
| A36 - Tool/package prerequisites | Host helpers and standard-library grader | adapt | Partial: Explore/Delegate present; browser name absent | SKILL.md:35,40,81-84; evals/grade_benchmark.py:3-7 | RPT-005 | Host tools/permissions unverified |
| S01 - Purpose and trust boundaries | Task/source trust boundary | adapt | Static: bounded purpose and output intent | SKILL.md:9-100 |  | No malicious-input test or security guarantee |
| S02 - Unexpected network/file/tool access | Workflow file/tool/network access | adapt | Partial: named targets and scope inspected | SKILL.md:9-100 |  | Native permissions/access untested |
| S03 - Sensitive-data handling | Planning/source content may contain sensitive data | adapt | Partial: output content has no explicit secret filtering | SKILL.md:9-100 |  | Host no-secret rule retained; no sensitive fixtures run |
| S04 - External instruction trust | Source requirements and helper instruction trust | adapt | Partial: approved source authority boundaries inspected | SKILL.md:9-100 |  | External content treated as data; adversarial handling untested |
| R01 - Preserve intended scope, names and triggers | Intended scope/name/triggers | adopt | Static: protected purpose recorded | SKILL.md:2-9; protected contracts |  | No behavior redesign authorized |
| R02 - Preserve invocation controls | No existing explicit invocation-disable control | not applicable | Not applicable: condition absent | SKILL.md:1-4 |  | No behavior claim |
| R03 - Approval and autonomy boundaries | Approval/autonomy boundaries | adopt | Static: exact current boundaries recorded | SKILL.md:9-100 |  | No inferred new permission; native enforcement untested |
| R04 - Required dependencies and delegation | Explore/Delegate/browser and Ralph handoff | adopt | Partial: schema aligns with Ralph; browser mapping unresolved | SKILL.md:35,40,84,100; consumer table | RPT-005 | No actual downstream execution |
| R05 - Stopping and handoff rules | Missing source/unsafe conflict stops and final handoff | adopt | Static: ask/stop before writing; readiness output | SKILL.md:36,44,94-100 |  | No stopping trace |
| R06 - Output contracts | tasks.json fields/path/final response | adapt | Defective: runtime contract sound but eval expects prd.json/stories | SKILL.md:23-31,94-100; references/task-schema.md:9-55; evals/evals.json:6-52 | RPT-001 | Preserve production output |
| R07 - Repository document authority and edit boundaries | Checkout guidance/edit authority | adapt | Partial: published procedure defers to applicable workspace rules | .agents/instructions/repo.md:6-8; audit boundary |  | Protected AGENTS/local skill paths not edited |
| R08 - Benchmark artifact/source separation | Primary versus fixtures/generated outputs | adopt | Static: scoped inventory excludes generated/history | Exact inventory; .agents/instructions/skills.md |  | No benchmark artifacts created |
| R09 - Scoped validation and prerequisites | Skill-change validation prerequisite | adapt | Static: no skill source edit; paper checks only | .agents/memory/testing/skills.md; verification record |  | No validator/packaging run claimed |
| R10 - Upgrade paper-review boundary | No Upgrade instructions or consumer proposal | not applicable | Not applicable: condition absent | SKILL.md:1-100 |  | No behavior claim |
| R11 - Evidence and grading integrity | Artifact/workflow/schema/metric/failure integrity | adapt | Defective: incompatible artifacts and assumed measurement/completion | evals/grade_benchmark.py:52,62-72,102-117,464-475 | RPT-001; SAG-008/DD-004 (accepted targets) | No native trace; pending exact protocols |
| R12 - Source formatting | Repository source formatting | adopt | Static: no CR/trailing whitespace in owned files | Non-mutating byte/line checks; .editorconfig |  | Authored report checked separately |
| C01 - Discovery and activation contract | Required-client discovery/activation | adapt | Partial: metadata source checked | SKILL.md:1-5; dated provider comparison |  | Native activation and discovery untested |
| C02 - Actual shipped resource set | Actual shipped source selection | adapt | Static: non-eval resources ship; evals pruned | Installer consumer table; exact inventory |  | Actual installed access untested |
| C03 - Client-specific metadata adapters | Surface-specific metadata adapters | adapt | Partial: controls qualified by host | SKILL.md:1-5; dated provider comparison |  | No universal enforcement claim |
| C04 - Tool and activation consent | Tool and activation consent | adapt | Unresolved: activation is not portable permission | Dated provider comparison; protected contracts |  | Actual consent/tool grants untested |

### to-issues

| Check ID and label | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 - Concise task-specific instructions | Task-specific instruction body | adopt | Static: focused purpose and procedural instructions | SKILL.md:9-84 |  | Context/token cost unmeasured |
| A02 - Specificity fits risk and variation | Planning decisions with protected boundaries | adapt | Static: constraints leave task-specific judgment | SKILL.md:9-84 |  | Decision quality untested |
| A03 - Intended model coverage | Intended model behavior | adapt | Unresolved: no native model runs | SKILL.md:2-4; evidence ticket resolution |  | No selected cases or seven-model repetitions |
| A04-F - SKILL.md and parsed required YAML | Entry file and required YAML strings | adapt | Static: parsed name/description strings | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N - Name syntax and length | Directory/name syntax and bound | adapt | Static: matching lowercase kebab-case; below 64 chars | SKILL.md:2 |  | Native name resolution untested |
| A04-D - Description metadata bounds | Required nonempty description | adapt | Static: 128 characters; no XML tags | SKILL.md:3 |  | Claude 1024 bound remains source-specific |
| A05 - Meaningful consistent name | Meaningful identity | adopt | Static: preserved name matches task purpose | SKILL.md:2-9 |  | No rename proposed |
| A06 - Useful bounded description | Purpose and trigger metadata | adapt | Static: bounded trigger description | SKILL.md:3 |  | Activation traces unrun |
| A07 - Focused entry body | Focused entry body | adapt | Static: 84-line entry has task-focused structure | SKILL.md:9-84 |  | Line count advisory; no automatic failure |
| A08 - Progressive disclosure | Tracker setup and input context | adapt | Partial: named setup procedure absent locally | SKILL.md:11,17 | RPT-002 | External host supply unverified |
| A09 - Advanced detail selection | No optional advanced resource branch | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A10 - Direct reference navigation | Named setup helper | adapt | Unresolved: no repository source for named procedure | SKILL.md:11; consumer table | RPT-002 | Supported prerequisite path needs decision |
| A11 - Long-reference navigation | No bundled reference longer than 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A12 - Descriptive portable paths | Issue references and setup name | adapt | Partial: real issue IDs required; setup source absent | SKILL.md:11,17,57 | RPT-002 | No actual issue fetch |
| A13 - Sequential workflow and progress | Multi-step planning workflow | adopt | Static: ordered steps and deliverables | SKILL.md:9-84 |  | Performed sequence untested |
| A14 - Quality feedback loop | Live breakdown feedback loop | adopt | Static: quiz and iterate until approval | SKILL.md:37-51 |  | No human product-workflow approval occurred |
| A15 - Dated facts and legacy separation | No fixed dated vendor/version facts in owned source | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A16 - Consistent terminology | Task terminology | adopt | Static: consistent workflow terms | SKILL.md:9-84 |  | Runtime language unobserved |
| A17 - Output template fidelity | Numbered breakdown and published issue template | adopt | Static: required titles/blockers/stories and body | SKILL.md:39-45,59-82 |  | No created issue |
| A18 - Representative examples | Template and no-blocker example | adapt | Static: small issue template and None example | SKILL.md:59-82 |  | No additional examples required automatically |
| A19 - Conditional branches | Missing setup/existing parent/optional exploration | adapt | Unresolved: missing setup branch has no shipped procedure | SKILL.md:11,17,19-23,62 | RPT-002 | Prerequisite behavior choice pending |
| A20 - Recommended default and exceptions | Prefactoring first and approved dependency order | adopt | Static: default ordering and triage exception | SKILL.md:33-35,55-57 |  | No inferred all-layer requirement for irrelevant layers |
| A21 - Baseline-driven improvement | Baseline-driven improvement | adapt | Unresolved: source snapshot is not baseline execution | SKILL.md:1-84 |  | No baseline/candidate comparison |
| A22 - Observable inspectable evaluations | Inspectable evaluation evidence | adapt | Unresolved: no bundled eval | SKILL.md:1-84 |  | Absence is evidence limit, not automatic defect |
| A23 - Reusable knowledge from real work | Reusable planning knowledge | adapt | Static: reusable method; history unverified | SKILL.md:9-84 |  | No real-task learning corpus inspected |
| A24 - Fresh-session real-task iteration | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | SKILL.md:1-84 |  | No native runs |
| A25 - Team feedback | Team-use feedback | adapt | Unresolved: no feedback corpus inspected | SKILL.md:1-84 |  | Source is not team-use evidence |
| A26 - Observed navigation and activation | Observed activation/navigation | adapt | Unresolved: no native loading trace | SKILL.md:1-84 |  | Explicit/allowed-implicit/negative cases later |
| A27 - Script error and fallback handling | No bundled executable resources | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A28 - Explained non-obvious constants | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A29 - Reusable deterministic utilities | No repeated deterministic operation needing utility | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A30 - Execute versus read script contract | No named or bundled script execution | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A31 - Visual inspection where useful | No spatial/layout inspection contract | not applicable | Not applicable: condition absent | SKILL.md:9-84 |  | No behavior claim |
| A32 - Validated intermediate plan | Approval before publication | adopt | Static: complete numbered intermediate breakdown | SKILL.md:37-57 |  | Actual approval/publication trace unrun |
| A33 - Package assumptions | No external package imports required | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A34 - Actual file-access/loading evidence | Source and installed loading claims | adapt | Partial: exact source reads and hashes | Owned inventory; installer consumer table |  | No installed/native load |
| A35 - Qualified MCP tool references | No literal MCP tool names in source | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| A36 - Tool/package prerequisites | Tracker, labels, setup and connector | adapt | Unresolved: setup source absent; actual tracker tools unspecified | SKILL.md:11,17,55-57 | RPT-002 | Supported external setup/auth prerequisite unknown |
| S01 - Purpose and trust boundaries | Task/source trust boundary | adapt | Static: bounded purpose and output intent | SKILL.md:9-84 |  | No malicious-input test or security guarantee |
| S02 - Unexpected network/file/tool access | External issue fetch/publication | adapt | Static: full body/comments and approved new issues only | SKILL.md:17,55-57,84 |  | Permissions/auth/partial publication untested |
| S03 - Sensitive-data handling | Planning/source content may contain sensitive data | adapt | Partial: output content has no explicit secret filtering | SKILL.md:9-84 |  | Host no-secret rule retained; no sensitive fixtures run |
| S04 - External instruction trust | Issue body/comments as external task data | adapt | Partial: no explicit untrusted-instruction branch | SKILL.md:17 |  | Do not treat comments as authorization; malicious-source test absent |
| R01 - Preserve intended scope, names and triggers | Intended scope/name/triggers | adopt | Static: protected purpose recorded | SKILL.md:2-9; protected contracts |  | No behavior redesign authorized |
| R02 - Preserve invocation controls | Existing invocation controls | adopt | Static: disable-model-invocation preserved | SKILL.md:4 |  | Cross-client enforcement untested |
| R03 - Approval and autonomy boundaries | Live user approval before issue publication | adopt | Static: approval loop and approved slices only | SKILL.md:47-55 |  | No new publication authority inferred |
| R04 - Required dependencies and delegation | Issue tracker/triage/setup dependency | adopt | Unresolved: named setup source absent | SKILL.md:11 | RPT-002 | Preserve prerequisite pending human choice |
| R05 - Stopping and handoff rules | Wait for approved breakdown; parent non-mutation | adopt | Partial: approval iteration explicit; failed publication recovery unspecified | SKILL.md:51,84 |  | No silent publish/retry policy inferred |
| R06 - Output contracts | Real blocker IDs/template/triage/parent | adopt | Static: output and parent invariants explicit | SKILL.md:55-84 |  | Partial-publication recovery not observed |
| R07 - Repository document authority and edit boundaries | Checkout guidance/edit authority | adapt | Partial: published procedure defers to applicable workspace rules | .agents/instructions/repo.md:6-8; audit boundary |  | Protected AGENTS/local skill paths not edited |
| R08 - Benchmark artifact/source separation | Primary versus fixtures/generated outputs | adopt | Static: scoped inventory excludes generated/history | Exact inventory; .agents/instructions/skills.md |  | No benchmark artifacts created |
| R09 - Scoped validation and prerequisites | Skill-change validation prerequisite | adapt | Static: no skill source edit; paper checks only | .agents/memory/testing/skills.md; verification record |  | No validator/packaging run claimed |
| R10 - Upgrade paper-review boundary | No Upgrade instructions or consumer proposal | not applicable | Not applicable: condition absent | SKILL.md:1-84 |  | No behavior claim |
| R11 - Evidence and grading integrity | Static versus behavioral evidence | adapt | Partial: report separates evidence classes | Evidence limits; owned inventory |  | No native grades/traces or human acceptance |
| R12 - Source formatting | Repository source formatting | adopt | Static: no CR/trailing whitespace in owned files | Non-mutating byte/line checks; .editorconfig |  | Authored report checked separately |
| C01 - Discovery and activation contract | Required-client discovery/activation | adapt | Partial: metadata source checked | SKILL.md:1-5; dated provider comparison |  | Native activation and discovery untested |
| C02 - Actual shipped resource set | Single entry ships; setup absent from source selection | adapt | Partial: shipped entry cannot provide named missing setup | SKILL.md:11; installer consumer table | RPT-002 | Actual external installation unverified |
| C03 - Client-specific metadata adapters | Surface-specific metadata adapters | adapt | Partial: controls qualified by host | SKILL.md:1-5; dated provider comparison |  | No universal enforcement claim |
| C04 - Tool and activation consent | Tool and activation consent | adapt | Unresolved: activation is not portable permission | Dated provider comparison; protected contracts |  | Actual consent/tool grants untested |

### architecture-design-contest

| Check ID and label | Applicability | Disposition | Current compliance | Evidence/source anchors | Finding IDs | Unresolved gaps |
| --- | --- | --- | --- | --- | --- | --- |
| A01 - Concise task-specific instructions | Task-specific instruction body | adopt | Static: focused purpose and procedural instructions | SKILL.md:9-165 |  | Context/token cost unmeasured |
| A02 - Specificity fits risk and variation | Design choices and minimum agent counts | adapt | Partial: structural diversity explicit; narrow helper conflict | SKILL.md:39-86; skills/explore/SKILL.md:13,32-33 | RPT-003 | Caller/helper precedence pending |
| A03 - Intended model coverage | Intended model behavior | adapt | Unresolved: no native model runs | SKILL.md:2-4; evidence ticket resolution |  | No selected cases or seven-model repetitions |
| A04-F - SKILL.md and parsed required YAML | Entry file and required YAML strings | adapt | Static: parsed name/description strings | SKILL.md:1-5 |  | Native parser/discovery untested |
| A04-N - Name syntax and length | Directory/name syntax and bound | adapt | Static: matching lowercase kebab-case; below 64 chars | SKILL.md:2 |  | Native name resolution untested |
| A04-D - Description metadata bounds | Required nonempty description | adapt | Static: 470 characters; no XML tags | SKILL.md:3 |  | Claude 1024 bound remains source-specific |
| A05 - Meaningful consistent name | Meaningful identity | adopt | Static: preserved name matches task purpose | SKILL.md:2-9 |  | No rename proposed |
| A06 - Useful bounded description | Purpose and trigger metadata | adapt | Static: bounded trigger description | SKILL.md:3 |  | Activation traces unrun |
| A07 - Focused entry body | Focused entry body | adapt | Static: 165-line entry has task-focused structure | SKILL.md:9-165 |  | Line count advisory; no automatic failure |
| A08 - Progressive disclosure | Codebase versus greenfield exploration | adapt | Partial: distinct branch and required helpers | SKILL.md:39-54,140-142 | RPT-003 | Narrow existing-code branch unresolved |
| A09 - Advanced detail selection | No optional advanced resource branch | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A10 - Direct reference navigation | Named helper navigation | adapt | Partial: source dependencies checked | SKILL.md:9-165 |  | Host skill-name resolution untested |
| A11 - Long-reference navigation | No bundled reference longer than 100 lines | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A12 - Descriptive portable paths | Paper-eval source paths | adapt | Defective: absolute unbundled checkout paths | evals/evals.json:9-13,27-31,56-60,73-78 | RPT-004 | No relocated fixture provision |
| A13 - Sequential workflow and progress | Frame/explore/contest/present/compare/recommend | adopt | Static: ordered decision workflow | SKILL.md:23-138 |  | Actual distinct-agent workflow unrun |
| A14 - Quality feedback loop | Cosmetic-option rejection and final choice | adopt | Static: rescope duplicates and opinionated comparison | SKILL.md:69-86,114-138 |  | Independent option quality untested |
| A15 - Dated facts and legacy separation | Current stack docs required | adapt | Partial: freshness obligation without fixed vendor fact | SKILL.md:54,78 |  | No current-doc retrieval or remote validation |
| A16 - Consistent terminology | Task terminology | adopt | Static: consistent workflow terms | SKILL.md:9-165 |  | Runtime language unobserved |
| A17 - Output template fidelity | Seven-part design response and final decision | adopt | Static: template and recommendation details explicit | SKILL.md:121-156 |  | No generated comparison inspected |
| A18 - Representative examples | Comparison/hybrid phrases and six paper scenarios | adapt | Partial: representative text and inputs inspectable | SKILL.md:112,129-138; evals/evals.json:6-94 | RPT-004 | Some fixtures need portable provision |
| A19 - Conditional branches | Existing/greenfield/narrow-context branches | adapt | Defective: existing narrow branch conflicts with Explore | SKILL.md:39-54; skills/explore/SKILL.md:13,32-33 | RPT-003 | Do not lower explicit counts before decision |
| A20 - Recommended default and exceptions | Minimum role counts and preferred diversity | adapt | Partial: 2+/3+ protected; different-family preference qualified | SKILL.md:41,58,140-142; skills/subagent-model-router/SKILL.md:94-112 | RPT-003 | Narrow helper precedence and actual availability unverified |
| A21 - Baseline-driven improvement | Baseline-driven improvement | adapt | Unresolved: source snapshot is not baseline execution | SKILL.md:1-165 |  | No baseline/candidate comparison |
| A22 - Observable inspectable evaluations | Six inspectable design paper cases | adapt | Partial: assertions capture outputs; absolute inputs unreproducible here | evals/evals.json:6-94 | RPT-004 | No routing/delegation/own-read traces; no grades |
| A23 - Reusable knowledge from real work | Reusable planning knowledge | adapt | Static: reusable method; history unverified | SKILL.md:9-165 |  | No real-task learning corpus inspected |
| A24 - Fresh-session real-task iteration | Fresh-session task iteration | adapt | Unresolved: no fresh-session evidence | SKILL.md:1-165 |  | No native runs |
| A25 - Team feedback | Team-use feedback | adapt | Unresolved: no feedback corpus inspected | SKILL.md:1-165 |  | Source is not team-use evidence |
| A26 - Observed navigation and activation | Observed activation/navigation | adapt | Unresolved: no native loading trace | SKILL.md:1-165 |  | Explicit/allowed-implicit/negative cases later |
| A27 - Script error and fallback handling | No bundled executable resources | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A28 - Explained non-obvious constants | No configurable executable constants | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A29 - Reusable deterministic utilities | No repeated deterministic operation needing utility | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A30 - Execute versus read script contract | No named or bundled script execution | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A31 - Visual inspection where useful | Architecture response; no visual-layout inspection requirement | not applicable | Not applicable: condition absent | SKILL.md:88-97 |  | No behavior claim |
| A32 - Validated intermediate plan | Design choice before implementation | adopt | Static: recommend and ask user choice; explicit switch for edits | SKILL.md:134-138,163 |  | No implementation approval inferred |
| A33 - Package assumptions | No external package imports required | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A34 - Actual file-access/loading evidence | Source plus paper-eval dependency loading | adapt | Partial: owned reads complete; absolute external paths unverified | evals/evals.json:9-13,27-31,56-60,73-78; exact inventory | RPT-004 | No fixture/runtime reads |
| A35 - Qualified MCP tool references | No literal MCP tool names in source | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| A36 - Tool/package prerequisites | Role dispatch/current research/helper prerequisites | adapt | Partial: named role/helper sources exist; exact host support unknown | SKILL.md:41,54,58,78,140-142; consumer table | RPT-003; RPT-004 | Native dispatch/network permissions untested |
| S01 - Purpose and trust boundaries | Task/source trust boundary | adapt | Static: bounded purpose and output intent | SKILL.md:9-165 |  | No malicious-input test or security guarantee |
| S02 - Unexpected network/file/tool access | Parallel agents, docs and codebase reads | adapt | Partial: purpose-bound access; evals name external checkout | SKILL.md:39-86; evals/evals.json:9-13 | RPT-004 | No actual network/file/agent access observed |
| S03 - Sensitive-data handling | Planning/source content may contain sensitive data | adapt | Partial: output content has no explicit secret filtering | SKILL.md:9-165 |  | Host no-secret rule retained; no sensitive fixtures run |
| S04 - External instruction trust | Current official or live references | adapt | Partial: citation requirement; host source trust remains necessary | SKILL.md:54,78 |  | No fetched authority or malicious-source tests |
| R01 - Preserve intended scope, names and triggers | Intended scope/name/triggers | adopt | Static: protected purpose recorded | SKILL.md:2-9; protected contracts |  | No behavior redesign authorized |
| R02 - Preserve invocation controls | Both explicit-invocation adapters | adopt | Static: both controls retained | SKILL.md:4; agents/openai.yaml:4-5 |  | Required-host enforcement untested |
| R03 - Approval and autonomy boundaries | Design-only until explicit execution switch | adopt | Static: no code/patch/file edit before switch; final human choice | SKILL.md:134-138,163 |  | No implicit publication/edit permission |
| R04 - Required dependencies and delegation | Required Explore/Delegate and named agent roles | adopt | Defective: reachable narrow helper stop conflicts with count | SKILL.md:41,58,140-142; skills/explore/SKILL.md:13,32-33 | RPT-003 | Role availability unverified; no dependency made optional |
| R05 - Stopping and handoff rules | Recommendation and next design decision | adopt | Static: final choice and anti-neutral-menu rule | SKILL.md:114-138,164 |  | No performed human design selection |
| R06 - Output contracts | Framing/findings/designs/comparison/recommendation | adopt | Static: output format/rejected alternative/hybrid/main tension | SKILL.md:121-156 |  | User-specific output override retained |
| R07 - Repository document authority and edit boundaries | Checkout guidance/edit authority | adapt | Partial: published procedure defers to applicable workspace rules | .agents/instructions/repo.md:6-8; audit boundary |  | Protected AGENTS/local skill paths not edited |
| R08 - Benchmark artifact/source separation | Primary versus fixtures/generated outputs | adopt | Static: scoped inventory excludes generated/history | Exact inventory; .agents/instructions/skills.md |  | No benchmark artifacts created |
| R09 - Scoped validation and prerequisites | Skill-change validation prerequisite | adapt | Static: no skill source edit; paper checks only | .agents/memory/testing/skills.md; verification record |  | No validator/packaging run claimed |
| R10 - Upgrade paper-review boundary | No Upgrade instructions or consumer proposal | not applicable | Not applicable: condition absent | SKILL.md:1-165 |  | No behavior claim |
| R11 - Evidence and grading integrity | Paper assertion versus performed contest evidence | adapt | Partial: inspectable cases; fixture/access/trace evidence missing | evals/evals.json:6-94 | RPT-004 | No activation or required delegation proof |
| R12 - Source formatting | Repository source formatting | adopt | Static: no CR/trailing whitespace in owned files | Non-mutating byte/line checks; .editorconfig |  | Authored report checked separately |
| C01 - Discovery and activation contract | Required-client discovery/activation | adapt | Partial: metadata source checked | SKILL.md:1-5; dated provider comparison |  | Native activation and discovery untested |
| C02 - Actual shipped resource set | Actual shipped source selection | adapt | Static: non-eval resources ship; evals pruned | Installer consumer table; exact inventory |  | Actual installed access untested |
| C03 - Client-specific metadata adapters | Codex sidecar/control adapters | adapt | Partial: false implicit control; short UI label generic | agents/openai.yaml:2-5; SKILL.md:3-4 |  | UI wording observation; no changed invocation intent |
| C04 - Tool and activation consent | Tool and activation consent | adapt | Unresolved: activation is not portable permission | Dated provider comparison; protected contracts |  | Actual consent/tool grants untested |

## Verification record and handback

Read all fourteen owned files; fingerprinted twelve primary files, two separately reviewed fixtures and fourteen bounded consumer dependencies. Sixteen supporting guidance/record hashes identify their read checkpoint. Exact bundle bytes match the supplied baseline revision. Parsed four frontmatters, two YAML sidecars, two JSON evaluation definitions and one Python AST. Non-mutating byte/line checks found no CR or trailing whitespace in owned source/fixtures. Report checks account for four exact 58-ID matrices (232 seven-column rows), full inventories and LF/no trailing whitespace/no authored em dash. No audited script, native evaluation, installer, import refresh, packaging, issue publication or validation helper ran.

Five canonical findings have recorded human dispositions; the exact Spec grader addition to two shared decisions is accepted. Parent verified source anchors and records; the single register owns finding details. No blocker finding is selected, and no behavioral failure is claimed. Full dependency closure, current vendor facts, installed/native access, actual agent roles/model diversity, consent, output quality and all behavioral baselines remain unverified. No evidence waiver or residual-risk acceptance is invented. Parent owns shared findings, coverage, ticket/map/handoff and canonical documentation writes.

## Parent reconciliation and delegation record

At the source checkpoint, parent verified source anchors, reachable consumer branches, current task schema and obsolete eval/grader flow. RPT-005 describes downstream acceptance wording, not browser execution during planning. RPT-003 concerns the actual narrow no-agent branch, not an incompatible numeric range. RPT-001/RPT-004 propose later evaluation repairs; three precise behavior questions have open routes blocked by this batch. Existing accepted metric/protocol target lists remain unchanged; adding exactly Spec to Tasks awaits live approval. Native evidence and human dispositions remain pending.

```yaml
dispatches:
  - subtask_id: requirements_planning_static
    selected:
      model: gpt-6.1-sol
      reasoning_effort: high
    submitted:
      model: gpt-6.1-sol
      reasoning_effort: high
    executed:
      model: unconfirmed
      reasoning_effort: unconfirmed
    runtime_limit:
      value: 20 minutes
      mechanism: Parent clock/status checks and five-minute saved checkpoints; status before interruption or a justified extension.
    status: completed
    output_verified: true
    routing_compliant: true
```

First post-dispatch clock bound: 2026-10-06 20:37:58 UTC; initial deadline: 20:57:58 UTC. Initial saved checkpoint was read by 20:39:25 UTC, complete checkpoint by 20:44:35 UTC. Running status was checked at 20:43:08 UTC, ten seconds after the nominal five-minute checkpoint; fresh saved progress was requested without interruption. Completion/ownership release were observed by 20:46:21 UTC, before the limit. Exact dispatch/completion times and runtime usage are unconfirmed. No interruption, fallback, replacement or extension occurred. Routing/selection/audit metadata stayed outside the task prompt; required task-source references remained inside. Provisional demanding-review selection and unused same-tier fallback were printed before dispatch. This source-review delegation is not native audit baseline evidence.

At the source checkpoint, `rtk proxy python3 /private/tmp/skill-audit-verify-requirements.py` passed record checks: four exact matrices, source/fixture/dependency hashes, graph/blockers/claim, owning finding index, candidate states, links/anchors/formatting/fog and protected-source boundaries. JSON/YAML/AST parsing does not execute the grader or prove workflow compliance. Scoped whitespace checks passed. No target workflow, grader/validator, installer, packaging, publication or native run occurred.

The source-checkpoint Update Agent Docs pass added a focused planning-prerequisite issue and changed the existing grader/caller-helper pointers in `.agents/memory/known-issues/skills.md`, path type Known Issue. Existing INDEX/FILE_MAP/instruction routes suffice; no API or testing entry changed. OKF loaded profile only; `rtk proxy ./scripts/lint-okf.py` exited 0 across both bundles. Scoped canonical diff contains exactly that authorized file. Added: planning prerequisite issue. Changed: grader/caller-helper pointers. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.

Process corrections: reviewer replaced a Tool Guardian-rejected long heredoc with inspectable patches and short calls. Parent read the updater's exact `refs/` links after guessed `references/` paths failed, repaired a blank line splitting the findings index, and reran checks. A shallow exclusion glob initially listed workspace snapshot names; corrected `!**/*-workspace/**` exclusion confirmed helper-source absence without reading or counting snapshots. No protected source was edited. Existing skills already specify exact reference links and representation checks; no actionable skill change is proposed from these execution mistakes.

## Live human-review closure

The human accepted all three recommendations on 2026-10-06. The [batch Resolution](../tickets/review-requirements-and-task-planning.md#resolution) owns this live decision. RPT-001/RPT-004 are accepted later evaluation repairs; three helper-contract routes remain pending and unblocked. Exactly Spec grader is added to SAG-008/DD-004, retaining previous targets for nine producers and six protocol graders. Representation, statuses, exits, schemas and compatibility remain unresolved. All sixteen underlying routes must appear in both final documents. Approval grants no implementation authority, native evidence waiver or residual-risk acceptance. No proposal was rejected/deferred and no audited helper or workflow ran.

Static investigation and human review now cover twenty-seven candidates and thirty-seven findings. Source compliance, hash baselines and evidence limits are unchanged. Exact fixture/oracle choices and genuine protocol prerequisites precede executable readiness. This closure claims no next ticket.

Closure verification passed with twelve closed/twenty-four open/no claimed tickets, all sixteen underlying routes open and unblocked, all thirty-seven findings disposed, exact nine-producer/six-grader scopes and twenty-seven human-reviewed/ten unstarted candidates. All 28 owned source/fixture/dependency fingerprints still match the source baseline. Five reports retain 1,566 check rows, 114 primary hashes and twenty-seven separately declared fixture hashes. The dependency/operation-state helper and scoped whitespace checks passed; no target grader or native run occurred.

The closure's formal Update Agent Docs pass changed only the existing accepted grader scope pointer in `.agents/memory/known-issues/skills.md`, type Known Issue. It retains unresolved representations and failure outcomes. Existing routing, indexes and API/testing guidance need no changes. OKF loaded profile only; `rtk proxy ./scripts/lint-okf.py` exited 0 across both bundles, with exactly that authorized canonical file in the scoped diff. Added: None. Changed: accepted grader scope pointer. Split/moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None.
