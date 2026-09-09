# OKF Authoring Skill Contract

**Type:** grilling
**Status:** closed
**Blocked By:** in-place-okf-document-contract.md
**Research Dir:** N/A

## Question

When must the repository's OKF authoring skill trigger, what workflow and progressive references should it teach, how should it preserve the existing `update-agent-docs` responsibility, and what explicit completion checks must it require for new or modified canonical OKF documents?

---

<!-- Resolution will be appended here -->

## Resolution

The repository adopts this OKF authoring-skill contract:

### Invocation and scope

- Publish a model-invoked skill named `okf-authoring` for creating, modifying, migrating, or reviewing Markdown documents under `.agents/instructions/` and `.agents/memory/`, including work performed through `update-agent-docs` and `ingest-source`.
- Ordinary reads and work outside those two canonical roots do not trigger the skill. The two in-place bundles remain its complete document scope; it does not author a sidecar, select prompt context, or modify immutable `.agents/sources/`.
- Review and question workflows remain read-only unless the user authorized changes.

### Responsibility and orchestration

- `update-agent-docs` remains the semantic owner. It decides whether knowledge is durable, chooses instruction versus memory placement, performs routing and index maintenance, and removes stale or duplicated guidance.
- After its semantic pass modifies canonical documents, `update-agent-docs` invokes `okf-authoring` to apply and verify the representation contract. `okf-authoring` never invokes `update-agent-docs`, keeping orchestration one-way and non-recursive.
- `ingest-source` retains its existing responsibility for raw-source integration and reaches OKF authoring indirectly through its final `update-agent-docs` step. The authoring skill does not replace manifest freshness, orphan cleanup, log updates, or immutable-source protections.

### Workflow and progressive references

The skill teaches agents to:

1. Identify each affected bundle and path-derived document type.
2. Load the shared repository profile and only the branch reference applicable to the document.
3. Preserve stable paths and unrelated body content; metadata-only conformance work does not rewrite bodies.
4. Author or review standard metadata, file-relative links, provenance, and lifecycle semantics under the closed **In-Place OKF Document Contract**.
5. Confirm that `update-agent-docs` handled applicable routing and index implications.
6. Run the canonical linter across both bundles and inspect the scoped diff.

Keep invocation, orchestration, the short workflow, and completion criteria in `SKILL.md`. Put the shared type, metadata, link, provenance, and lifecycle profile in `references/profile.md`. Put source-summary-specific rules and examples in `references/source-summaries.md`, loaded only for that branch. Add no general examples reference unless implementation evaluations show that it materially improves reliability.

### Completion contract

- The future canonical lint entry point is the final mechanical authority and validates both bundles so cross-bundle links and repository-wide reserved-path rules are covered. Its exact command and diagnostic IDs are decided by **OKF Linter and Provider Hooks Contract**, not this ticket.
- An authoring change is complete only when lint succeeds and the scoped diff confirms that paths, bodies, and unrelated content were preserved as required. If lint cannot run, report the work as unverified with the exact reason and do not claim completion.
- Report affected canonical paths and their derived types, branch references loaded, routing or index implications checked by `update-agent-docs`, and the exact lint command and result.
- Migration sequencing must make the linter available before converted documents depend on this completion gate.

### Implementation acceptance

Implementation evaluations cover at least: creating an ordinary canonical concept; metadata-only migration that preserves path and body; draft and completed source-summary branches; composition with `update-agent-docs`; read-only conformance review; a negative case outside the canonical roots; and an unavailable-linter case that refuses a completion claim. Prefer deterministic assertions and compare the new skill against a no-skill baseline.
