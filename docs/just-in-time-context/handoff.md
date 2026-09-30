# Just-in-time Context Handoff

## Goal and status

Success Criteria is closed after the user confirms its acceptance contract on 2026-09-29. The map contains ten tickets: two research tickets and one human decision ticket are closed; seven human decision tickets remain open. The next frontier contains Knowledge Evidence Policy and Lifecycle Guarantees. Only Success Criteria is resolved in this decision session.

## Agreed constraints

- Reusable across the user's repositories, piloted here.
- First version supports Codex, Copilot, and Gemini; exact surfaces and guarantees remain open.
- Additions, corrections, reorganization, and pruning run automatically with reversible, evidenced maintenance.
- Explicit user instructions remain authoritative.
- The user says domain-modeling is not needed. Do not block on that missing dependency.
- The user requires the map under docs/<feature-slug> rather than .agents/scratchpad/<feature-slug>. All effort artifacts are in docs/just-in-time-context/.
- Unified skill subcommands and nested AGENTS.md remain hypotheses.

## Next step

Start a new Wayfinder decision session with tickets/knowledge-evidence-policy.md. Verify that its exact blocker, reference-evidence.md, is closed; claim the ticket with a six-character assignee ID before work. Use grilling to decide which evidence supports automatic knowledge publication, correction, and pruning while explicit user instructions remain authoritative. Read the closed Success Criteria contract as needed. Resolve only that human decision ticket and update this handoff before stopping. Lifecycle Guarantees is also unblocked and can be worked in a separate session.

## Artifacts and verification

- map.md indexes resolved tickets and carries the remaining fog.
- tickets/ contains questions and their exact dependency filenames.
- baseline.md records current source-inspected behavior. Research documents official contracts; installed-version behavior remains unverified.
- brief.md retains the original idea, agreed scope, and source references.
- The prior charting commit is 58b6fc1. The worktree is clean when this decision session starts. This session changes the Success Criteria resolution, the map's closed-ticket index and fog, and this handoff. No product source, hook configuration, or installed behavior changes.
- Both research investigations are complete. Current validation confirms ten tickets, three closed and seven open, an acyclic dependency graph, thirteen valid local Markdown links, and the frontier named above.
- `rtk proxy python3 scripts/lint-okf.py` exits 0 across both canonical bundles. `rtk git diff --check` passes. No product build or runtime test is needed for these documentation changes; no live provider probe, paper reproduction, or acceptance measurement was performed.
- The formal update-agent-docs pass is complete. Existing routing in repo.md and FILE_MAP.md remains accurate; this session changes no current behavior, canonical rules, file locations, or indexes. No canonical knowledge edit is needed. Accepted feature decisions remain in their ticket rather than being duplicated as current repository behavior.
- Planning artifacts and synchronized knowledge documentation belong in one commit under the repository's validation contract. No push is requested.

## Execution findings

- Success Criteria sets product targets, not measured results. Its full Resolution owns thresholds, counting definitions, failure gates, and measurement limitations. Baseline values, concrete pilot cases, repetitions, and instrumentation are not yet selected or measured.
- All predefined critical checks must pass on every supported surface, including after repeated maintenance cycles. The token metric counts delivered guidance and attributable maintenance, not total billed input tokens. Reading guidance alone and agent self-reports do not establish correctness.

- Tool Guardian rejects a large apply_patch input with "129 segments exceeds limit 128 segments". Smaller focused patches succeed. Do not retry the full multi-file patch unchanged.
- The sandbox denies creating directories under the read-only .agents tree. No scratchpad files were created. The user-selected docs/ location is writable and version controlled.
- Verified paper inspection identifies arxiv 2510.04618v3 as Agentic Context Engineering, which evaluates external-context adaptation. Do not assume it studies model-weight training. Harmful updates and context collapse are relevant to acceptance criteria.
- Hook context injection does not itself execute semantic maintenance. Shutdown and idle-work guarantees differ by provider and harness. These facts constrain later decisions without selecting an architecture.
- No skill improvements are proposed. The domain-modeling waiver and docs/ path choice are explicit user overrides, not blockers or global skill changes.
