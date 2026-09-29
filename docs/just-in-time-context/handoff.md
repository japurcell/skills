# Just-in-time Context Handoff

## Goal and status

Charting is complete. The map contains ten tickets: two research tickets are closed and eight human decision tickets remain open. Cited findings are linked from the closed tickets and indexed in map.md. No human decision ticket is resolved during charting.

## Agreed constraints

- Reusable across the user's repositories, piloted here.
- First version supports Codex, Copilot, and Gemini; exact surfaces and guarantees remain open.
- Additions, corrections, reorganization, and pruning run automatically with reversible, evidenced maintenance.
- Explicit user instructions remain authoritative.
- The user says domain-modeling is not needed. Do not block on that missing dependency.
- The user requires the map under docs/<feature-slug> rather than .agents/scratchpad/<feature-slug>. All effort artifacts are in docs/just-in-time-context/.
- Unified skill subcommands and nested AGENTS.md remain hypotheses.

## Next step

Start a new Wayfinder decision session with tickets/success-criteria.md. Verify its blockers, claim it with a six-character assignee ID before work, then use grilling to establish measurable acceptance criteria with the user. Resolve only that human decision ticket in the session and update the map's frontier and fog.

## Artifacts and verification

- map.md indexes resolved tickets and carries the remaining fog.
- tickets/ contains questions and their exact dependency filenames.
- baseline.md records current source-inspected behavior. Research documents official contracts; installed-version behavior remains unverified.
- brief.md retains the original idea, agreed scope, and source references.
- The initial repository worktree is clean. No product source, hook configuration, or installed behavior changes.
- Both research investigations are complete. The ticket dependency graph is acyclic and local links pass validation.
- `rtk proxy python3 scripts/lint-okf.py` exits 0 across both canonical bundles. `rtk git diff --check` passes. No product build or runtime test is needed for these documentation changes; no live provider probe or paper reproduction was performed.
- The formal documentation pass updates hooks.md for VS Code harness-specific contracts and Copilot argument rewriting, adds effort routing in repo.md and FILE_MAP.md, and records the large-patch guard limit in known-issues/hooks.md. No canonical document is added, moved, split, or removed; INDEX.md needs no change.
- Planning artifacts and synchronized knowledge documentation belong in one commit under the repository's validation contract. No push is requested.

## Execution findings

- Tool Guardian rejects a large apply_patch input with "129 segments exceeds limit 128 segments". Smaller focused patches succeed. Do not retry the full multi-file patch unchanged.
- The sandbox denies creating directories under the read-only .agents tree. No scratchpad files were created. The user-selected docs/ location is writable and version controlled.
- Verified paper inspection identifies arxiv 2510.04618v3 as Agentic Context Engineering, which evaluates external-context adaptation. Do not assume it studies model-weight training. Harmful updates and context collapse are relevant to acceptance criteria.
- Hook context injection does not itself execute semantic maintenance. Shutdown and idle-work guarantees differ by provider and harness. These facts constrain later decisions without selecting an architecture.
- No skill improvements are proposed. The domain-modeling waiver and docs/ path choice are explicit user overrides, not blockers or global skill changes.
