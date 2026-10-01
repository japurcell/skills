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

## Safety and initial-delivery clarification, 2026-10-01

The user selects trusted-workspace safety and capability-specific release gates, then explicitly confirms that Windows has the same initial-delivery target as non-Windows. Windows is not reduced to a skills/agents-only release. Codex, Copilot CLI/VS Code, and Gemini retain skills, custom agents, required-skill startup/context hooks, Tool Guardian, and secret scanning. Claude Code, Cursor, and OpenCode retain skills and supporting references only. Optional observability/capture remains accompanying hook functionality, not a separate selectable catalog asset. Team, local/private, and personal scopes and the full normal lifecycle remain in scope.

A trusted workspace means the installer protects against mistakes, ordinary file edits, concurrent installer invocations, and interrupted operations, while assuming another process does not deliberately replace the directory tree or forge recovery authority during execution. Preserve unrelated data/settings, immutable provenance and ownership validation, edit-conflict refusal, exact-byte offline audit, current-record restore, and consistent interrupted-operation recovery. Preserve ordinary access permissions and known mandatory integrity labels, or refuse known loss before changing the destination. Continue refusing existing links/reparse paths and malformed or inconsistent records. Deliberate concurrent directory/file substitution and malicious rewriting of recovery state are outside the required guarantee; arbitrary audit-SACL preservation is still not a universal requirement.

Capability-specific gates distinguish installer lifecycle, skill/agent rendering, installed-hook protocol behavior, opt-in capture, clone/relocation, runtime/OS execution, and actual native-client discovery/events. Every advertised capability needs its own passing evidence. Known-broken required hooks cannot be described as supported, and a core-only checkpoint is not the complete initial target. Unavailable link fixtures, other hosts/runtimes, and live-client checks remain explicitly pending; they do not erase independently demonstrated capabilities or become passed by changing this contract. Keep file installation/protocol support distinct from verified native loading. Do not delete, disable, weaken or relabel failing assertions to obtain a green result.

Windows-only clone acceptance may use a genuine Windows-installed committed payload once the writer is verified. Auditing the same payload across different operating systems remains a separate evidence target; an unavailable POSIX-produced bundle is not intrinsically required for the Windows-only proof.

The next implementation attempt has a user-selected 30-minute active runtime ceiling, including validation and review, with no automatic retries, increases, replacement agents or rewrites at the boundary. No numeric AI-credit ceiling was supplied; do not invent one. Implementation and test spending remain frozen during this requirements clarification. Preserve existing working code rather than starting another backend rewrite merely because some tests assume POSIX. Earlier stronger safety and all-matrix delivery gates are superseded by this clarification; implementation and measured support have not changed.

## Validation allocation constraint, 2026-09-30

During implementation, the user reports that the available native Windows environment has only Copilot CLI and Gemini CLI and prohibits installing other providers. Require native Windows client discovery/trust/events only for those existing CLI clients. Allocate Codex CLI, Copilot VS Code, and skills-only OpenCode native proof to authorized non-Windows hosts. Their Windows native loading remains unverified and is outside this delivery's required native gates. Reported availability is not execution evidence.

The user subsequently explicitly defers Claude Code and Cursor native verification for the initial release. Their skills-only asset representations and automated file/path tests remain. Native discovery/reference access stays unverified on every OS and is not an initial release gate. This does not remove OpenCode's required native skill/reference check or authorize suppressing automated assertions.

The three-OS installer/updater target and initial six-client asset scope remain unchanged. Preserve Windows filesystem, ownership, mutation, interruption/recovery, clone, quoting, PowerShell, and direct installed-hook protocol requirements within the subsequently clarified trusted-workspace contract. Rendering another provider's assets in a disposable fixture does not install that provider client. Native client/OS allocation remains unchanged, but the 2026-10-01 capability-specific gates replace treating all unavailable evidence as one global delivery blocker. The current [ExecPlan](../../agent-asset-installer/ExecPlan.md) and [client evidence](../../agent-asset-installer/client-validation.md) record the allocated pairs and remaining work.

## Consequences and next effort

This contract guides the separate [implementation ExecPlan](../../agent-asset-installer/ExecPlan.md), which translates it into the asset catalog, declared dependencies, provenance/ownership records, client adapters, and public-process validation. The original planning decision made no installer or user-directory changes; the user's subsequent execution request authorized implementation. Use the [current handoff](../handoff.md) for delivered behavior and remaining acceptance.

Use [the recommendation](../recommendation.md) for comparative evidence and [the current source inventory](../local-inventory.md) for existing constraints. The installer currently refreshes assets from its local checkout; the scoped release check does not establish a stable release channel. Native trust requirements and the research's unverified product-surface limits still apply.
