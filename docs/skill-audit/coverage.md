# Skill Audit Coverage

Started 2026-10-05. Source baseline: `91ba7ab9` (full revision below). This index records review coverage, not passing skill behavior.

## Record semantics

- The authoring source snapshot is dated 2026-10-01. The approved adoption policy qualifies Claude-specific constraints against required Codex, Copilot CLI/VS Code, and Gemini CLI surfaces. Links below identify the original rule; they do not assert current runtime conformance.
- Every skill matrix records each stable check separately: applicability, adoption disposition, current compliance, source evidence, finding IDs, and unresolved gaps. `adopt`/`adapt` chooses a criterion, never a passing result. `not applicable` needs its concrete condition; `incompatible` needs a required-client constraint plus unsuccessful equivalent adaptations.
- Compliance may be satisfied statically, defective, partially evidenced, or unresolved. Runtime checks stay unresolved without usable run artifacts. Static review can be complete with defects and disclosed runtime gaps. Human proposal disposition and later candidate acceptance are separate.
- Split a check with suffixed IDs when subconditions have different outcomes; retain its parent source. No silent blanket passes or invented exclusion reasons. New applicable requirements receive stable IDs with source and condition.
- The catalog contains every one of the 36 source checklist bullets, splitting metadata into three checks, plus four security checks and sixteen repository/client checks. The source final condensed checklist adds no distinct criterion.

## Check catalog

### Authoring checks

| ID | Check | Strength and applicability | Source |
| --- | --- | --- | --- |
| A01 | Concise task-specific instructions | Advisory; All instructions. | [Concise is key](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#concise-is-key) |
| A02 | Specificity fits risk and variation | Advisory; All workflows. | [Set appropriate degrees of freedom](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#set-appropriate-degrees-of-freedom) |
| A03 | Intended model coverage | Advisory; Model behavior claims; use approved native matrix, not Claude example names. | [Test with all models you plan to use](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#test-with-all-models-you-plan-to-use) |
| A04-F | SKILL.md and parsed required YAML | Required repository/client entry file and string name/description; malformed parsing is not a pass | [YAML frontmatter requirements](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#yaml-frontmatter-requirements); [provider comparison](research/provider-compatibility/findings.md#compatibility-constraints) |
| A04-N | Name syntax and length | Required tightest documented client constraint: VS Code parent-directory match, lowercase letters/digits/hyphens, <=64 characters; Claude reserved-word advice alone is not binding | [YAML frontmatter requirements](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#yaml-frontmatter-requirements); [provider comparison](research/provider-compatibility/findings.md#compatibility-constraints) |
| A04-D | Description metadata bounds | Nonempty description required; Claude <=1,024 characters/no XML tags remain source-specific, qualify any required-client bounds separately | [YAML frontmatter requirements](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#yaml-frontmatter-requirements); [provider comparison](research/provider-compatibility/findings.md#compatibility-constraints) |
| A05 | Meaningful consistent name | Advisory; Every skill; preserve existing name. | [Naming conventions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#naming-conventions) |
| A06 | Useful bounded description | Advisory; Every skill; activation behavior requires later trace. | [Writing effective descriptions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions) |
| A07 | Focused entry body | Advisory; Every entry; 500 body lines is advisory inspection signal. | [Progressive disclosure patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns) |
| A08 | Progressive disclosure | Advisory; Entry plus resources; retain essential controls. | [Progressive disclosure patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns) |
| A09 | Advanced detail selection | Advisory; When optional advanced branches exist. | [Progressive disclosure patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns) |
| A10 | Direct reference navigation | Advisory; When references exist; preserve supported shared-resource layout. | [Avoid deeply nested references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-deeply-nested-references) |
| A11 | Long-reference navigation | Advisory; References over 100 lines; inspect concrete retrieval impact. | [Structure longer reference files with table of contents](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#structure-longer-reference-files-with-table-of-contents) |
| A12 | Descriptive portable paths | Advisory; Every documented resource path. | [Runtime environment](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#runtime-environment) |
| A13 | Sequential workflow and progress | Advisory; Multi-step workflows. | [Use workflows for complex tasks](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#use-workflows-for-complex-tasks) |
| A14 | Quality feedback loop | Advisory; Quality-sensitive outputs. | [Implement feedback loops](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#implement-feedback-loops) |
| A15 | Dated facts and legacy separation | Advisory; Time-sensitive claims or historical instructions. | [Avoid time-sensitive information](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-time-sensitive-information) |
| A16 | Consistent terminology | Advisory; Entry plus resources. | [Use consistent terminology](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#use-consistent-terminology) |
| A17 | Output template fidelity | Advisory; Structured output contract. | [Template pattern](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#template-pattern) |
| A18 | Representative examples | Advisory; Style or output shape matters. | [Examples pattern](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#examples-pattern) |
| A19 | Conditional branches | Advisory; Methods differ by case. | [Conditional workflow pattern](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#conditional-workflow-pattern) |
| A20 | Recommended default and exceptions | Advisory; Alternatives exist. | [Avoid offering too many options](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-offering-too-many-options) |
| A21 | Baseline-driven improvement | Advisory; Skill changes/evaluation claims; count of three advisory except repo-specific contract. | [Build evaluations first](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first) |
| A22 | Observable inspectable evaluations | Advisory; Eval prompts, inputs and expected outcomes. | [Build evaluations first](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first) |
| A23 | Reusable knowledge from real work | Advisory; Authoring/learning rules or claimed task history. | [Develop Skills iteratively with Claude](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#develop-skills-iteratively-with-claude) |
| A24 | Fresh-session real-task iteration | Advisory; Behavioral evaluation claims. | [Develop Skills iteratively with Claude](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#develop-skills-iteratively-with-claude) |
| A25 | Team feedback | Advisory; Evidence of team use/feedback; absent history is unresolved, not invented. | [Develop Skills iteratively with Claude](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#develop-skills-iteratively-with-claude) |
| A26 | Observed navigation and activation | Advisory; Behavioral retrieval/discovery claims. | [Observe how Claude navigates Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#observe-how-claude-navigates-skills) |
| A27 | Script error and fallback handling | Advisory; Bundled executable resources. | [Solve, don't defer](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#solve-dont-defer) |
| A28 | Explained non-obvious constants | Advisory; Configurable script constants. | [Solve, don't defer](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#solve-dont-defer) |
| A29 | Reusable deterministic utilities | Advisory; Repeated deterministic operations. | [Provide utility scripts](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#provide-utility-scripts) |
| A30 | Execute versus read script contract | Advisory; Scripts named or bundled. | [Provide utility scripts](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#provide-utility-scripts) |
| A31 | Visual inspection where useful | Advisory; Layout/spatial inputs and capable supported host. | [Use visual analysis](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#use-visual-analysis) |
| A32 | Validated intermediate plan | Advisory; Risky batch/destructive/complex-rule actions. | [Create verifiable intermediate outputs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#create-verifiable-intermediate-outputs) |
| A33 | Package assumptions | Advisory; External packages required. | [Package dependencies](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#package-dependencies) |
| A34 | Actual file-access/loading evidence | Advisory; Source paths plus installed/runtime claims. | [Runtime environment](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#runtime-environment) |
| A35 | Qualified MCP tool references | Advisory; MCP tool names used; adapt syntax to actual host. | [MCP tool references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#mcp-tool-references) |
| A36 | Tool/package prerequisites | Advisory; Commands, dependencies or host tools required. | [Avoid assuming tools are installed](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-assuming-tools-are-installed) |

### Security checks

The overview security clarification is advisory software-risk guidance translated to the actual host. Static review does not establish absence of vulnerabilities.

| ID | Check | Applicability | Source |
| --- | --- | --- | --- |
| S01 | Purpose and trust boundaries | Advisory; All instructions and bundled resources; inspect operations outside stated purpose. | [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations) |
| S02 | Unexpected network/file/tool access | Advisory; Resource operations and permissions; identify targets and scope. | [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations) |
| S03 | Sensitive-data handling | Advisory; Inputs, traces, outputs and command logging that can expose sensitive data. | [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations) |
| S04 | External instruction trust | Advisory; External URLs or dependency instructions; distinguish source data from governing authority. | [Security considerations](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations) |

### Repository and required-client checks

Repository instructions apply to work in this checkout. Published skills must retain portable purpose and defer to applicable host/repository requirements. Effort decisions bind this audit and candidate proposals, not every outside repository.

| ID | Check | Strength and applicability | Source |
| --- | --- | --- | --- |
| R01 | Preserve intended scope, names and triggers | Audit requirement for every proposal; identify explicit intent and ambiguous contracts. | [Source](tickets/set-adoption-rules-and-protected-behavior.md#protected-behavior-and-intended-scope) |
| R02 | Preserve invocation controls | Repository/audit requirement where controls exist; no unapproved control removal. | [Source](../../.agents/instructions/skills.md) |
| R03 | Approval and autonomy boundaries | Audit requirement; changes or contradictions require separate human choice. | [Source](tickets/set-adoption-rules-and-protected-behavior.md#protected-behavior-and-intended-scope) |
| R04 | Required dependencies and delegation | Audit requirement; check availability and consumer contracts without redesigning excluded helpers. | [Source](tickets/set-adoption-rules-and-protected-behavior.md#protected-behavior-and-intended-scope) |
| R05 | Stopping and handoff rules | Audit requirement; preserve stopping conditions and explicit handoff contracts. | [Source](tickets/set-adoption-rules-and-protected-behavior.md#protected-behavior-and-intended-scope) |
| R06 | Output contracts | Audit requirement; preserve required files, reports, review results and no-op behavior. | [Source](tickets/set-adoption-rules-and-protected-behavior.md#protected-behavior-and-intended-scope) |
| R07 | Repository document authority and edit boundaries | Repository requirement in this checkout; preserve protected AGENTS sections and local skill boundaries. | [Source](../../AGENTS.md#protected-sections) |
| R08 | Benchmark artifact/source separation | Repository requirement for generated runs; sibling workspaces, canonical per-eval directory, fixture exclusions. | [Source](../../.agents/instructions/skills.md#benchmarking) |
| R09 | Scoped validation and prerequisites | Repository requirement for skill changes; retained-validator exceptions remain scoped and explicit. | [Source](../../.agents/memory/testing/skills.md) |
| R10 | Upgrade paper-review boundary | Audit exception only for Upgrade instructions/resources or proposed consumers; no execution/install/packaging/live-validation approval. | [Source](tickets/choose-audit-batches-and-evidence-format.md#shared-resources-scope-and-exceptions) |
| R11 | Evidence and grading integrity | Audit requirement where evaluation/compliance claims occur; source, trace and output grading distinct, no self-report proof. | [Source](tickets/set-audit-evidence-and-model-coverage.md#resolution) |
| R12 | Source formatting | Repository requirement: LF text, space indentation, no trailing or blank-line whitespace; applicable scoped EditorConfig settings. | [Conventions](../../.agents/memory/CONVENTIONS.md#code-style); [EditorConfig](../../.editorconfig) |
| C01 | Discovery and activation contract | Required-client behavior; metadata/source inspection separate from native explicit/implicit activation traces. | [Source](research/provider-compatibility/findings.md#findings) |
| C02 | Actual shipped resource set | Repository packaging fact plus required-client path access; evals/README/licenses stripped from installed skills. | [Source](import-ownership-evidence.md) |
| C03 | Client-specific metadata adapters | Required-client compatibility; sidecar/invocation fields do not imply universal enforcement. | [Source](research/provider-compatibility/findings.md#compatibility-constraints) |
| C04 | Tool and activation consent | Required-client tool permissions; skill activation or a script command is not a portable grant. | [Source](research/provider-compatibility/findings.md#compatibility-constraints) |

## Candidate index

Original inventory: 55 published plus five repository-local entry points. Current candidates: 32 published plus five local = 37. Twenty-three known imports are excluded. Unknown historical origin does not imply import or block static review. No additional import has been established in this batch.

Full source revision: `91ba7ab941450327c8d178c27966d1150bd0b74b`. Per-file SHA256 evidence belongs in batch reports. Current source hashes describe unchanged skill inputs, not a model-run snapshot.

| Candidate | Root | Review owner | Static coverage | Behavioral coverage |
| --- | --- | --- | --- | --- |
| `create-skill` | `skills/` | [Owner](tickets/review-skill-authoring-and-repository-guidance.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `improve-skill` | `skills/` | [Owner](tickets/review-skill-authoring-and-repository-guidance.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `agents-md-improver` | `skills/` | [Owner](tickets/review-skill-authoring-and-repository-guidance.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `create-agentsmd` | `skills/` | [Owner](tickets/review-skill-authoring-and-repository-guidance.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `guidance-review` | `skills/` | [Owner](tickets/review-skill-authoring-and-repository-guidance.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `self-improve` | `skills/` | [Owner](tickets/review-skill-authoring-and-repository-guidance.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `clean-agent-docs` | `.agents/skills/` | [Owner](tickets/review-repository-local-workflows.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `exec-plans` | `.agents/skills/` | [Owner](tickets/review-repository-local-workflows.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `ingest-source` | `.agents/skills/` | [Owner](tickets/review-repository-local-workflows.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `okf-authoring` | `.agents/skills/` | [Owner](tickets/review-repository-local-workflows.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `update-agent-docs` | `.agents/skills/` | [Owner](tickets/review-repository-local-workflows.md) | Static investigation and human proposal review complete (58 checks) | Not run; not selected |
| `delegate-to-subagents` | `skills/` | [Owner](tickets/review-delegation-and-discovery.md) | Not started | Not run; not selected |
| `subagent-model-router` | `skills/` | [Owner](tickets/review-delegation-and-discovery.md) | Not started | Not run; not selected |
| `explore` | `skills/` | [Owner](tickets/review-delegation-and-discovery.md) | Not started | Not run; not selected |
| `official-sources` | `skills/` | [Owner](tickets/review-delegation-and-discovery.md) | Not started | Not run; not selected |
| `explain-your-thinking` | `skills/` | [Owner](tickets/review-delegation-and-discovery.md) | Not started | Not run; not selected |
| `adversarial-review` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `code-review` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `code-simplify` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `fixing-accessibility` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `techdebt` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `harness-analysis` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `improve-repo-harness` | `skills/` | [Owner](tickets/review-quality-and-harness-skills.md) | Not started | Not run; not selected |
| `prd` | `skills/` | [Owner](tickets/review-requirements-and-task-planning.md) | Not started | Not run; not selected |
| `spec-to-tasks` | `skills/` | [Owner](tickets/review-requirements-and-task-planning.md) | Not started | Not run; not selected |
| `to-issues` | `skills/` | [Owner](tickets/review-requirements-and-task-planning.md) | Not started | Not run; not selected |
| `architecture-design-contest` | `skills/` | [Owner](tickets/review-requirements-and-task-planning.md) | Not started | Not run; not selected |
| `prd-ralph` | `skills/` | [Owner](tickets/review-execution-and-handoff.md) | Not started | Not run; not selected |
| `prd-ralph-loop` | `skills/` | [Owner](tickets/review-execution-and-handoff.md) | Not started | Not run; not selected |
| `execplan-implement` | `skills/` | [Owner](tickets/review-execution-and-handoff.md) | Not started | Not run; not selected |
| `commit` | `skills/` | [Owner](tickets/review-execution-and-handoff.md) | Not started | Not run; not selected |
| `handoff` | `skills/` | [Owner](tickets/review-execution-and-handoff.md) | Not started | Not run; not selected |
| `gh-cli` | `skills/` | [Owner](tickets/review-github-cli-guidance.md) | Not started | Not run; not selected |
| `dotnet` | `skills/` | [Owner](tickets/review-dotnet-and-ui-guidance.md) | Not started | Not run; not selected |
| `dotnet-ui-app` | `skills/` | [Owner](tickets/review-dotnet-and-ui-guidance.md) | Not started | Not run; not selected |
| `code-modernization` | `skills/` | [Owner](tickets/review-modernization-instructions.md); resource scope: review-modernization-workflows-and-assets | Not started | Not run; not selected |
| `dotnet-upgrade` | `skills/` | [Owner](tickets/review-upgrade-instructions-and-templates.md); resource scope: review-upgrade-route-and-source-records | Not started | Not run; not selected |

## Exclusions and scope history

The [current inventory](local-inventory.md#current-audit-scope) and [configured-import evidence](import-ownership-evidence.md) retain original totals and origins. This list is current exclusion evidence, not historical provenance recovery.

| Excluded entry points | Reason | Evidence |
| --- | --- | --- |
| `caveman`, `frontend-design`, `skill-creator`, `code-review-biaxis`, `codebase-design`, `improve-codebase-architecture`, `prototype`, `research`, `resolving-merge-conflicts`, `tdd`, `wayfinder`, `retro`, `grilling`, `teach`, `writing-for-agents`, `web-accessibility`, `web-best-practices`, `web-performance`, `show-me` | Configured imports; excluded by human decision | [Import mappings](import-ownership-evidence.md) |
| `addy-code-review-and-quality`, `addy-code-simplification`, `addy-performance-optimization`, `addy-security-and-hardening` | Four configured Addy imports | [Import mappings](import-ownership-evidence.md) |
| Nested fixture SKILL/AGENTS entry points, sibling `*-workspace/`, snapshots and generated outputs | Test/history evidence, not maintained primary skills | [Inventory](local-inventory.md#maintained-entry-points) |

## Shared resources and consumer checks

| Resource/dependency | Content owner | Consumers checked | Coverage/evidence limit |
| --- | --- | --- | --- |
| Excluded `skill-creator` | Excluded imported helper; no primary audit or proposed edits | Authoring batch: bounded consumer checks complete | Check only required invocation, paths and installed helper commands; preserve dependency |
| Repository `.agents/` documentation contract | Repository-local workflows review | Five local bundles and their direct maintenance/OKF chain reviewed statically; first-batch consumer checks retained | Source review complete; native ordering/permission evidence and cross-batch reconciliation remain outstanding |
| `prd-ralph-loop` self-improve call | Review Execution and Handoff | `self-improve` consumer boundary checked at `prd-ralph-loop/SKILL.md:19-39` | Preserve delayed load/stop and progress-file context; full owning review remains unstarted |
| Upgrade document-review metadata comparison | Review Upgrade Instructions and Templates | `guidance-review` controls checked at `dotnet-upgrade/references/document-review.md:27` | Bounded paper dependency only; no procedure activation or enforcement claim |
| Installer shipped-resource set | Authoring/guidance batch owns this bounded consumer check | All six entry/resource sets checked against both installer source exclusions | Non-eval files shipped; installed access untested; no full tooling audit or installer proposal selected |

## Review records

- [Review Skill Authoring and Repository Guidance](tickets/review-skill-authoring-and-repository-guidance.md): closed after the 2026-10-05 live human review; [report](reports/review-skill-authoring-and-repository-guidance.md) records 45 bundle files, supporting-source scopes, and six 58-check matrices. All fourteen findings have a recorded disposition; four separate decisions remain pending.
- [Finding register](findings.md): owns seventeen findings with recorded human dispositions; five precise questions have linked open, unblocked decision tickets. Acceptance of routing does not resolve their underlying choices.
- [Review Repository-local Workflows](tickets/review-repository-local-workflows.md): closed after the 2026-10-05 live human review. Source baseline is `bd7b1a68a081ea847b2e6c1712363000ef01751f`; the [report](reports/review-repository-local-workflows.md) records sixteen unchanged-source files, eighteen fixture dependencies, and five complete matrices (290 rows). RLW-001/RLW-003 are accepted later authoring scope; RLW-002 retains its separate pending decision. No native baseline exists for this batch.
- All other batch reports remain unstarted. Full static review, reconciliation, baseline sample selection, native launch setup, required runs, final audit and ExecPlan remain outstanding.

The repository-local report records its own source baseline; the initial catalog revision above is not substituted for later per-batch evidence. Total completed static investigation and human proposal review: eleven candidates, 638 check rows, and 61 primary file hashes. Seventeen findings have recorded dispositions; five underlying decisions remain pending.
