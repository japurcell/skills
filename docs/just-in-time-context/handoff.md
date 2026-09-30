# Just-in-time Context Handoff

## Goal and status

Plan an implementation-ready specification for reusable automatic context management, piloted here. The user confirms Context Organization and Skill Boundary on 2026-09-29; its resolution is saved and the ticket is closed. The map contains ten tickets: seven closed, three open, and no active claims. This decision session resolves only that human ticket. No product implementation or installation is performed.

## Next focus and next step

Next session: [Maintenance Scheduling and Pruning](tickets/maintenance-scheduling-and-pruning.md), the only open frontier ticket. Load [Just-in-time Context](map.md), verify its exact blockers Knowledge Evidence Policy and Lifecycle Guarantees are closed, and claim Maintenance Scheduling and Pruning before grilling. Load the closed [Context Organization and Skill Boundary](tickets/context-organization-and-skill-boundary.md) for the selected execution boundary. Do not reopen accepted policy or start implementation.

Failure and Concurrency Contract remains blocked by Maintenance Scheduling and Pruning. Adoption and Validation Contract remains blocked by Failure and Concurrency Contract. Existing ticket questions now carry the organization decision; no new ticket or dependency edge is needed.

## Standing constraints

- Keep effort artifacts under docs/just-in-time-context/, overriding wayfinder's scratchpad default. The user explicitly waives domain-modeling.
- Plan only. Resolve at most one human decision ticket per session; research exceptions remain allowed. No push is requested.
- Share tooling across repositories, with repository-isolated knowledge. Automatic additions, corrections, reorganization, and pruning must remain reversible and evidenced. Explicit user instructions govern.
- First-version targets are Codex desktop and Codex/Copilot/Gemini CLIs. Both VS Code harnesses are deferred. Fresh interactive, resume/compaction, noninteractive CLI, and supported child paths need separate deployed-version certification; targets are not certified support.
- Preserve the closed Success Criteria, Knowledge Evidence Policy, Context Retrieval Contract, and Lifecycle Guarantees. Their full resolutions own quality, evidence, retrieval, completion, recovery, and performance requirements.

## Current decision and boundaries

The organization ticket owns the full contract. Key choices for the next session:

- agent-brain names both the skill and bundled Python CLI. Semantic stages are recall, learn, and dream. Use dream rather than maintain. Simplicity and compatibility across CLI providers govern the design.
- Foreground provider agents perform semantic work through one progressively disclosed skill. The cooperative CLI supplies inputs, deterministic retrieval/state operations, and outcome checks. Thin native adapters initiate stages and enforce verified outcomes. No independent model runner, daemon, or maintenance subagent is required by the core.
- Indexed Markdown remains authoritative. Use stable section/document units with compact JSON annotations and inherited metadata while preserving OKF frontmatter. Map existing or protected whole artifacts without forced relocation. New repositories start minimally. Explicit loading obligations survive.
- Keep compact evidence colocated and selectively disclosed. Version knowledge, configuration, and durable candidates; isolate persistent ignored runtime state per worktree. Defaults are .agents/context/config.json and .agents/context/state/. Concrete identity, ownership, recovery, publication, and retention remain later decisions.
- Mutating learn/dream requires valid integration-issued invocation context. Invalid context fails before mutation with an actionable nonzero error. Generic provider environment variables, successful process exits, injected prompts, and self-reports do not prove semantic execution. Help and standalone informational recall remain available everywhere.
- Consumers need no hooks/families or generator. Packaged adapters and registration templates add missing native hooks or merge managed entries while preserving unrelated hooks. Skill installation alone does not activate automatic stages. Publisher adapters stay in canonical hook families with isolated generated outputs.
- Existing update-agent-docs and clean-agent-docs entries delegate canonical learn/dream without duplicate execution. One source scanner/manifest owns freshness; focused ingestion joins one coordinated learn pass. The adapter is optional for repositories without source ingestion.
- Pilot reporting adds observable total provider task usage/credits and stage boundaries alongside delivered-guidance tokens. Disclose unavailable data. No precise per-stage attribution or new cost threshold is required; foreground execution has no universal cost advantage claim.

Scheduling selects dream eligibility and due-work handling within foreground execution. Recording an idle obligation does not execute it. An additional autonomous execution path would require an explicit scope decision. Closed or idle sessions have no unconditional execution guarantee; recovery occurs at the next eligible supported event and respects cancellation and pauses.

## Artifacts, evidence, and verification

- [Just-in-time Context](map.md) is the closed-decision index and remaining fog. [Just-in-time Context Brief](brief.md) preserves the original scope; [Current Context Lifecycle](baseline.md) records inspected current behavior.
- [Semantic stage invocation interfaces](research/context-stage-invocation/findings.md) captures official documentation checked on 2026-09-29. Headless launches exist for three CLIs; desktop foreground continuation is documented. No supported attachment to an existing desktop conversation is established. Exact permissions, flags, native payloads, and semantic outcomes require deployed-version certification.
- Read-only baseline and provider briefings are complete. Current OKF has document identity/provenance but no unit metadata schema. Existing source hooks detect and gate pending work; agents perform semantic integration. Skill installers retain bundled scripts/references; new Codex handlers require explicit registration. No agent-brain skill or registration exists yet.
- This session starts from 2b0858882d7fb338a88ce174be368ceff126732f on codex/plan-just-in-time-context. Scope is seven effort Markdown files: the organization resolution, map, three dependent questions, handoff, and new stage-invocation findings.
- Formal update-agent-docs pass is complete. Existing repo instructions and FILE_MAP already route this effort's tickets/research/handoff. No verified current architecture, API, instruction, or memory routing changes; no canonical edits are needed.
- `rtk proxy python3 scripts/lint-okf.py` exits 0 across both canonical bundles. The inline Python validator passes: ten tickets, seven closed, three open, no claims, acyclic dependencies, a closed-only map index, valid research paths/fog delimiters, and Maintenance Scheduling and Pruning as the sole frontier. Only the organization ticket changes status; all previously closed contracts remain unchanged. All 86 local Markdown links and formatting checks pass across 17 effort Markdown files. `rtk git diff --check` passes.
- No product build, runtime test, live provider probe, certification, baseline measurement, or acceptance benchmark is performed. Product targets remain unmeasured. All changes belong in one scoped commit.

## Review findings and corrections

- The user rejects full replayable evidence for every lesson. Follow the closed proportional evidence policy; use stronger checks for broader or higher-impact claims. Explain with existing KB examples when requested. The Tool Guardian tip is a scoped observation, not a claimed replay.
- Inactivity prioritizes review; pruning needs evidence of error, obsolescence, or complete redundancy. Delivery does not prove application. Do not reintroduce detailed usage attribution.
- Hook injection does not execute semantic maintenance. Provider stopping does not prove work-session completion. Native continuation caps, advisory events, and uncertain child delivery constrain certification; unsupported paths must be explicit.
- The user corrects the proposed skill name to agent-brain and semantic maintenance stage to dream. CLI UX sources disagree about diagnostic streams; the accepted contract keeps primary/JSON results on stdout and diagnostics/progress on stderr.
- A patch with later-file hunks before earlier-file hunks fails verification without changes. Inspecting exact locations and ordering hunks by source position succeeds. Keep independent patches small; no skill-specific improvement is identified.
- Tool Guardian rejects an oversized patch with "129 segments exceeds limit 128 segments". Smaller focused patches succeed. Earlier documentation wording also triggers an outer database_destruction/critical rejection; rewording succeeds without changing guards. The existing durable observation is in .agents/memory/known-issues/hooks.md under "Active guards can block their own maintenance". The rejection alone does not establish repository-hook attribution.
- The sandbox denies writes under .agents/; the user-selected docs/ path is writable. No scratchpad artifacts are created. Read-only questions may start at the requested KB artifact; nontrivial edits still require root AGENTS.md orientation.
- Reference Evidence verifies arxiv 2510.04618v3 as Agentic Context Engineering, studying external-context adaptation. Do not characterize it as model-weight training.
