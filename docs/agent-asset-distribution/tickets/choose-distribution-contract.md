# Choose the Distribution Contract

**Type:** grilling
**Status:** closed
**Blocked By:** codex-copilot-distribution.md, claude-gemini-distribution.md, portable-distribution-methods.md
**Research Dir:** none

## Question

Given the verified capability matrix and this repository's current install flow, which distribution contract should be adopted first: a selective repository installer, native packages, or a layered combination? Decide required clients and asset types, committed versus local setup, release pinning, component selection, scope precedence, and ownership of updates and removals with the user. Support both committed team setup and local untracked setup, with committed team setup as default, as already authorized. Present a research-backed recommendation without treating it as an approved implementation design.

Updates from this source repository to installed assets must be supported and easy to perform. Treat update behavior as part of the distribution contract, not a deferred convenience feature.

---

## Resolution

The user approved the following distribution contract through the live interview on 2026-09-29. All interview branches are settled. This closes the planning decision; it does not establish implemented or live-tested support.

1. **Initial client scope:** Complete repository setup for the existing Codex, Copilot CLI/VS Code, and Gemini CLI workflows. Offer skills-only compatibility for Claude Code, Cursor, and OpenCode until their complete adapters are verified. Treat hosted/cloud support as a separate validation target; do not infer unsupported product capabilities.
2. **Component selection:** Support curated workflow bundles and individual skills, agents, and hooks, with required dependencies included.
3. **Committed team delivery:** Commit selected asset files together with the immutable upstream revision and digest. Teammates receive the asset files when cloning. Client runtimes and native trust approval remain necessary. Manifest-only bootstrap is not the chosen initial team delivery style.
4. **Installation modes:** Support committed team setup and local untracked setup, with committed team setup as the default. Preserve the current user-global installation workflow.
5. **Update requirement:** Provide an easy supported way to update installed assets from this repository as part of the initial distribution contract.
6. **Initial delivery channel:** Ship the selective installer first. Native plugins and extensions are a later additional delivery channel generated from the same maintained sources, carrying only components each client supports. No native-package release date is committed by this decision.
7. **Update invocation and scope:** Provide one explicit update command for user-global, committed repository, and local untracked installations. Remember installed component and client selections, retain provenance, and offer an optional preview. Leave committed team updates available for Git review; do not automatically commit them. Unattended background updates are not the chosen default.
8. **Edited installed assets:** Preserve local edits. If upstream changes conflict with them, stop before writing any update. Require explicit conflict resolution, then rerun the update. Automatic three-way merging or replacement with backups is not the chosen default.
9. **Source targeting and restoration:** An explicit update follows the configured source branch unless the user selects a tag or commit. Resolve the chosen source to an immutable commit and record its digest. Restore installations from their recorded revision rather than silently following a moving branch. The user explicitly excluded a rollback feature; do not provide a rollback command or retain installation history for that purpose.
10. **Managed ownership and dependency updates:** Track installer-owned files and configuration entries. Update selected bundles together with their declared required dependencies, reporting additions and removals. Preserve unrelated files and settings. Adopt an existing personal installation only when its files can be verified as matching known repository outputs; report ambiguous or modified copies as conflicts rather than silently claiming them.
11. **Pruning:** During an explicit update, remove an obsolete file or configuration entry only when the installer records its ownership, it remains unchanged locally, and no selected asset still requires it. This applies to items that leave the selected bundle or dependency closure. Locally edited managed items follow the conflict policy above, including stopping before any writes. Directory placement alone is not ownership.
12. **Project/global coexistence:** Follow each client's native precedence and report effective configuration, overlaps, and additive hook behavior. Avoid duplicate managed registrations where the client supports it. Preserve unrelated personal configuration. Universal isolation from personal configuration is not an initial requirement.
13. **Operating systems:** Target macOS, Linux, and Windows for the installer and updater. Document and check each selected asset's client and runtime restrictions rather than inferring universal feature availability.

## Consequences and next effort

The route to the map's destination is clear. Prepare an implementation plan in a separate effort when implementation work is requested. It must translate this contract into the asset catalog, declared dependency data, provenance/ownership records, client adapters, and public-process validation. Existing installers and user-global copies have not been changed by this decision.

Use [the recommendation](../recommendation.md) for comparative evidence and [the current source inventory](../local-inventory.md) for existing constraints. The installer currently refreshes assets from its local checkout; the scoped release check does not establish a stable release channel. Native trust requirements and the research's unverified product-surface limits still apply.
