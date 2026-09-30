# Context Organization and Skill Boundary

**Type:** grilling
**Status:** closed
**Blocked By:** reference-evidence.md, context-retrieval-contract.md, lifecycle-guarantees.md
**Research Dir:** not applicable

## Question

Which knowledge representation and workflow boundary satisfy the selected retrieval and lifecycle contracts with one authoritative home for each rule?

Compare the current indexed .agents knowledge base, nested AGENTS.md, and a hybrid against the agreed contracts. Decide whether lifecycle guidance belongs in one progressively disclosed skill, several skills, executable components, or a combination. Define responsibility for routing, knowledge storage, and maintenance, including compatibility with existing source ingestion. Choose names only after the boundary is settled.

Implement the self-contained units, required references, applicability, uncertainty, scoped reuse, and lightweight delivery information agreed in [Context Retrieval Contract](context-retrieval-contract.md). Select their representation and responsibility without introducing detailed usage attribution or weakening explicit complete-artifact loading requirements.

Apply [Lifecycle Guarantees](lifecycle-guarantees.md) when choosing components and provider wiring. Separate event detection, delivery, actual work invocation, and outcome enforcement. Select automatic native or supervised paths for the chosen desktop/CLI surfaces and entry modes; instruction injection alone is insufficient. Keep first-version VS Code support deferred.

---

## Resolution

The user confirms this contract on 2026-09-29 after accepting Q1-Q15 and the repository-onboarding and publisher/consumer clarifications. Simplicity and compatibility across CLI providers govern this organization decision. This contract plans the system; no skill, CLI, hook, or installation is implemented here.

### Names and semantic responsibilities

Agent-brain is both the publishable skill name and CLI command name. Both expose at least these stages:

| Stage | Semantic responsibility |
| --- | --- |
| recall | Retrieve the context map and task-relevant guidance, evaluate scope, and establish sufficient context before dependent work. |
| learn | Add or correct evidenced knowledge and refresh knowledge affected by the completed work, including verified no-change where appropriate. |
| dream | Consolidate, repair, reorganize, and prune knowledge under the accepted evidence policy. |

The active foreground provider agent performs semantic reasoning through one progressively disclosed skill. This includes interactive agents and foreground headless task agents. The shared CLI supplies stage inputs, deterministic retrieval and state operations, and observable outcome checks. Thin native adapters detect lifecycle events, initiate stages automatically, deliver context, and gate required outcomes.

The first-version core does not require independent model sessions, a maintenance subagent, or a daemon. Existing delegated task work still follows the closed child-context and completion contracts. Standalone autonomous semantic execution from an ordinary terminal would require an additional provider invocation adapter; returning a stage prompt does not perform learn or dream.

### Authoritative knowledge and repository boundaries

Keep indexed Markdown as the authoritative knowledge layer. The default homes are .agents/instructions/ for policy and procedures and .agents/memory/ for durable descriptive knowledge. Preserve existing authoritative instructions, their scope, and explicit loading order. The root entrypoint, INDEX, and provider entrypoints remain compact maps rather than parallel stores of learned knowledge.

Nested AGENTS.md may retain unique scoped policy or routing. Do not depend on uniform native nested-file discovery. Every rule and learned claim has one authoritative home; derived indexes and provider routing do not create a second authority.

Share software, adapters, and the lifecycle skill across repositories. Keep knowledge, evidence, candidates, and pending obligations isolated by repository and worktree. The first version does not automatically generalize or copy lessons between repositories. Applicable existing user/global instructions still govern.

For a repository with an existing KB, configure mappings rather than forcing a new tree or duplicating content. For a repository without a KB, begin with a minimal map and add focused knowledge from actual work. Existing AGENTS.md and testing documentation can be mapped in place. Exact onboarding, migration, and activation remain for [Adoption and Validation Contract](adoption-and-validation-contract.md).

### Guidance units and metadata

A guidance unit is one coherent section or small document. Keep applicability, important exceptions, and required dependencies with its meaning; do not turn each sentence into a claim record. Explicit whole-artifact reads remain mandatory.

Preserve existing OKF frontmatter and its path-based document identity. Add compact agent-brain JSON metadata comments for document defaults and section overrides using one schema. Stable retrieval IDs are separate from document paths and survive relocation. Configuration can register protected or externally owned artifacts as whole-document units without rewriting them.

Metadata identifies the unit, its applicability, policy/fact classification, established or uncertain/candidate state, required guidance references, and compact evidence/verification references. Inherit document defaults and record overrides only where needed. Canonical prose remains the guidance and keeps its qualifications. Required references distinguish linked units from explicit complete-artifact obligations.

Update the repository's authoring and lint contracts during implementation before introducing these annotations into canonical docs. Generated indexes locate units and expand their references; they remain rebuildable and are never authoritative copies of guidance. Relocation, consolidation, and retirement preserve valid references and the accepted reversible history.

### Evidence, candidates, and storage

Apply [Knowledge Evidence Policy](knowledge-evidence-policy.md) without increasing its evidence burden. Keep compact source and verification notes beside the canonical unit, inheriting shared source references when appropriate. Reference raw inputs and summaries separately rather than copying them into every unit. Retain source identity, applicable revision/version, verification date and result, scope, and attributable change rationale.

Ordinary retrieval delivers applicability, exceptions, relevant uncertainty, and a short source reference. Load detailed evidence when verification or maintenance needs it. Full traces and replayable reproductions are not routine requirements. The existing [Tool Guardian tip](../../../.agents/memory/known-issues/hooks.md) remains one scoped operational observation, not a record for every sentence or proof of universal behavior.

Version repository configuration, canonical guidance/evidence, and durable unverified candidate notes. Keep candidates separately identified and excluded from ordinary established-guidance lookup; expose them only for relevant investigation. Existing draft source-summary states retain their own contracts.

The default configuration is .agents/context/config.json. Put rebuildable indexes, lightweight delivery records, temporary candidates, stage results, and persistent pending-work records in ignored .agents/context/state/, isolated per worktree. Existing layouts may configure other locations. Pending state must survive normal interruption; it is operational state, not established knowledge. Retention, atomicity, ownership, and recovery details remain for [Failure and Concurrency Contract](failure-and-concurrency-contract.md) and [Maintenance Scheduling and Pruning](maintenance-scheduling-and-pruning.md).

### Retrieval and scoped reuse

Use explicit routes for paths, concepts, actions, dependencies, and provider/runtime scope, with text search. Agents interpret task relevance and broaden uncertain scope. The shared runtime expands required references and checks known mandatory coverage and complete delivery. Rebuild indexes from canonical content and configured mappings. Embeddings are not required in the first version; demonstrated gaps can motivate a later decision.

Apply [Context Retrieval Contract](context-retrieval-contract.md) to startup, newly dependent work, read-only conclusions, changed scope, compaction, resume, and children. Retrieve before dependent work. A failed lookup does not establish that no guidance applies.

Retain lightweight delivery identity and current unit/revision information sufficient to expose missing or incomplete delivery. Reuse only guidance still available, current, and applicable in the executing agent's context. A record of earlier delivery does not prove availability after compaction or in a child. This does not require detailed usage attribution.

### Cooperative invocation and outcomes

Use one common stage input/work/result contract across providers. Inputs identify the workspace/worktree, task and agent, stage, current scope, and relevant evidence references. The foreground agent executes the semantic procedure. Results identify completed, no-change, or incomplete outcomes with applicable changes, evidence, and checks.

Mutating learn/dream operations require valid integration-issued invocation context. Missing or mismatched context produces an actionable nonzero error before mutation. Do not infer supported invocation solely from a provider-named environment variable. The check establishes registered invocation context; semantic execution and completion still need observable evidence. Exact identity, expiry, pause/cancellation, and recovery mechanics belong to [Failure and Concurrency Contract](failure-and-concurrency-contract.md).

Help and standalone informational recall remain available outside an agent. Printing a map to a terminal does not prove its delivery to an executing agent. A successful CLI process exit, injected instructions, or an agent's completion claim alone does not establish completed semantic work.

The runtime verifies applicable artifacts and checks before accepting an outcome. Required learning/refresh and delegated obligations finish before successful work-session completion. Preserve explicit incomplete outcomes and pending work across interruption or provider limits. Do not start a new model session implicitly to work around an invalid invocation. These requirements preserve [Lifecycle Guarantees](lifecycle-guarantees.md).

### CLI help and automation

Use the raw repository references [12 Factor CLI Apps](../../../.agents/sources/12-factor-cli-apps.md), [CLI Design Guidelines](../../../.agents/sources/cli-design-guidelines.md), and [clig.dev](../../../.agents/sources/clig-dev.md). Their summaries route discovery; raw sources inform the contract.

Provide top-level and per-command help, with purposes, inputs, effects, common examples, and cooperative-execution requirements. Support conventional help entrypoints, including --help and -h. Bare top-level invocation lists commands and begins no work. Help is available before active-agent validation and has no semantic or knowledge-mutating side effects.

Clearly explain that learn and dream use the active provider agent and that the CLI does not launch a model session by default. For missing supported invocation context, an illustrative human diagnostic is:

> agent-brain learn: a supported active-agent invocation is required. No knowledge was changed. Run this stage through an enabled integration. See agent-brain learn --help.

Errors explain the cause and next action, return nonzero, and occur before mutation. Preserve structured results on stdout and diagnostics/progress on stderr; this resolves the sources' stream recommendation difference in favor of clean machine output. Provide an explicit JSON mode. Avoid hidden prompts in noninteractive use and disable terminal-only presentation when output is piped. A warning or informational message must never substitute for a required failed stage outcome.

### Source-ingestion compatibility

Keep one source-change detector and manifest as the owner of source freshness and pending ingestion. Learn invokes the existing focused ingestion workflow for changed sources, then refreshes affected guidance in one coordinated pass. Preserve immutable raw sources and existing summary/manifest states.

Existing completion gates join the same obligation rather than beginning duplicate learning. Existing update-agent-docs and clean-agent-docs entrypoints remain compatible by delegating to the canonical learn and dream procedures without duplicate execution. Keep ingestion-specific work focused. Repositories without that workflow need no source-ingestion adapter. Exact deduplication and reentry mechanics remain for [Failure and Concurrency Contract](failure-and-concurrency-contract.md).

### Distribution and provider integration

Bundle the Python 3 CLI with skills/agent-brain/, alongside SKILL.md and progressively loaded references. Dependencies are explicit; installers expose the agent-brain command with platform launchers. Maintain thin provider adapters in this publishing repository's canonical hooks/families/ sources and generate provider-local outputs. Adapters invoke the installed shared CLI and do not import peer-provider hooks.

Distribute runnable adapters and registration templates. Consuming repositories need neither hooks/families nor a generator. Onboarding registers required native hooks when absent or adds managed entries while preserving unrelated existing hooks. Installing the skill alone does not activate automatic events. Registration locations, dependencies, upgrade/rollback, and platform checks remain for [Adoption and Validation Contract](adoption-and-validation-contract.md).

Target native foreground integrations for Codex desktop and Codex/Copilot/Gemini CLIs under the closed lifecycle scope. Startup/task/action/restore/child events feed the shared protocol; native continuation gates request foreground stage execution and enforce verified results. Map event names and payloads per provider rather than assuming a universal schema.

The [stage invocation findings](../research/context-stage-invocation/findings.md) explain why independent headless jobs are possible but not required by this selected core. They establish no supported attachment to an existing desktop conversation. Do not depend on that unverified interface. Copilot resume/headless startup restrictions and bounded stop continuations, Gemini advisory compaction/shutdown and unverified child paths, and Codex desktop-versus-CLI proof requirements still constrain certification. Exact native wiring and permissions need deployed-version tests; a registration or injected prompt is not execution proof.

Every target version/mode and child path needs separate certification. If a native or otherwise validated automatic integration cannot meet the closed contract, declare the path unsupported. Preserve next-eligible-event recovery and the absence of an unconditional idle/shutdown execution promise. VS Code harnesses remain outside the first version.

### Usage visibility, remaining decisions, and validation

The pilot also reports total provider-reported task usage or credits where available, alongside the delivered-guidance metric in [Success Criteria](success-criteria.md). Record stage boundaries and include all model executors if any are added. Unavailable usage is a disclosed measurement gap. Do not require precise per-stage attribution or add a new cost threshold. Guidance delivered, actual model usage, and billed credits remain distinct quantities.

[Maintenance Scheduling and Pruning](maintenance-scheduling-and-pruning.md) selects dream schedules, eligibility checks, and retention. [Failure and Concurrency Contract](failure-and-concurrency-contract.md) selects concrete invocation identity, ownership, deduplication, reentry, retries, publication, and recovery mechanisms. [Adoption and Validation Contract](adoption-and-validation-contract.md) selects installation/activation, concrete schemas and pinned versions, capability probes, workloads, instrumentation, and rollback proof within this organization.

Preserve the accepted quality, policy, recovery, guidance-volume, and latency gates. This session gathers current repository and primary-source facts and writes planning documents. It performs no product implementation, installation, live provider probe, runtime certification, or acceptance measurement.
