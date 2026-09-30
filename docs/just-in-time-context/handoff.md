# Just-in-time Context Handoff

## Goal and status

Knowledge Evidence Policy is closed after the user confirms its contract on 2026-09-29. The map contains ten tickets: four closed and six open. The frontier contains Context Retrieval Contract and Lifecycle Guarantees. Only Knowledge Evidence Policy is resolved in this decision session; Success Criteria remains unchanged.

## Agreed constraints

- Reusable across the user's repositories, piloted here.
- First version supports Codex, Copilot, and Gemini; exact surfaces and guarantees remain open.
- Additions, corrections, reorganization, and pruning run automatically with reversible, evidenced maintenance.
- Explicit user instructions remain authoritative.
- The user says domain-modeling is not needed. Do not block on that missing dependency.
- The user requires the map under docs/<feature-slug> rather than .agents/scratchpad/<feature-slug>. All effort artifacts are in docs/just-in-time-context/.
- Unified skill subcommands and nested AGENTS.md remain hypotheses.

## Next step

Start a new Wayfinder decision session with tickets/context-retrieval-contract.md. Verify that its exact blockers, provider-lifecycle-capabilities.md, reference-evidence.md, and knowledge-evidence-policy.md, are closed. Claim the ticket with a six-character assignee ID before work. Use grilling to define always-present and task-scoped guidance, relevance, scope expansion, completeness, and delivery of uncertain or disputed knowledge under the closed evidence policy. Resolve only that human decision ticket and update this handoff before stopping. Lifecycle Guarantees is independently unblocked for a separate session.

## Artifacts and verification

- map.md indexes resolved tickets and carries the remaining fog.
- tickets/ contains questions and their exact dependency filenames.
- baseline.md records current source-inspected behavior. Research documents official contracts; installed-version behavior remains unverified.
- brief.md retains the original idea, agreed scope, and source references.
- The prior Success Criteria commit is b84ff7b. The worktree is clean when this decision session starts. This session changes the Knowledge Evidence Policy resolution, the map's closed-ticket index and fog, dependent retrieval and maintenance questions, and this handoff. No product source, hook configuration, or installed behavior changes.
- Both research investigations are complete. Current validation confirms ten tickets, four closed and six open, an acyclic dependency graph, twenty-four valid local Markdown links, and the frontier named above. Only Knowledge Evidence Policy changes ticket status in this session.
- `rtk proxy python3 scripts/lint-okf.py` exits 0 across both canonical bundles. `rtk git diff --check` passes. No product build or runtime test is needed for these documentation changes; no live provider probe, paper reproduction, or acceptance measurement was performed.
- The formal update-agent-docs pass is complete. Existing routing in repo.md and FILE_MAP.md remains accurate; this session changes no current behavior, canonical rules, file locations, or indexes. No canonical knowledge edit is needed. Accepted feature decisions remain in their ticket rather than being duplicated as current repository behavior.
- Planning artifacts and synchronized knowledge documentation belong in one commit under the repository's validation contract. No push is requested.

## Execution findings

- The user finds full replayable evidence for every lesson excessive. Do not restore that rejected universal requirement. Use compact claim-specific evidence and stronger checks for broader or higher-impact claims. When explaining this policy, prefer a concrete existing KB entry over a hypothetical example; the Tool Guardian patch-limit entry is used here without claiming a replay was performed.
- The user accepts inactivity only as a review signal. Delivery does not prove application, and missing reads may expose routing failures. Detailed usage attribution is not required. Follow the closed Knowledge Evidence Policy rather than inferring deletion authority from age or retrieval counts.

- Success Criteria sets product targets, not measured results. Its full Resolution owns thresholds, counting definitions, failure gates, and measurement limitations. Baseline values, concrete pilot cases, repetitions, and instrumentation are not yet selected or measured.
- All predefined critical checks must pass on every supported surface, including after repeated maintenance cycles. The token metric counts delivered guidance and attributable maintenance, not total billed input tokens. Reading guidance alone and agent self-reports do not establish correctness.

- Tool Guardian rejects a large apply_patch input with "129 segments exceeds limit 128 segments". Smaller focused patches succeed. Do not retry the full multi-file patch unchanged.
- The sandbox denies creating directories under the read-only .agents tree. No scratchpad files were created. The user-selected docs/ location is writable and version controlled.
- Verified paper inspection identifies arxiv 2510.04618v3 as Agentic Context Engineering, which evaluates external-context adaptation. Do not assume it studies model-weight training. Harmful updates and context collapse are relevant to acceptance criteria.
- Hook context injection does not itself execute semantic maintenance. Shutdown and idle-work guarantees differ by provider and harness. These facts constrain later decisions without selecting an architecture.
- No skill improvements are proposed. The domain-modeling waiver and docs/ path choice are explicit user overrides, not blockers or global skill changes.
