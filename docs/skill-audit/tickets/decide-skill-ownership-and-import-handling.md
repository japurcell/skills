# Decide Skill Ownership and Import Handling

**Type:** grilling
**Status:** closed
**Blocked By:** set-adoption-rules-and-protected-behavior.md
**Research Dir:** not applicable

## Question

How should accepted improvements be maintained for imported skills, repository-local workflow skills, and shared resources without losing changes during source refresh?

Use the inventory and importer source to distinguish repository-owned skills from imported bundles. Decide local deviations, source-refresh reconciliation, provenance, and shared-reference handling. The user explicitly includes all five `.agents/skills/` entry points in audit scope despite their default edit restriction. Identify authoring or evaluation constraints that differ between roots, and changes that need a separately scoped importer or validator proposal.

The decision must establish ownership and maintenance rules that the final ExecPlan can apply to each accepted finding.

---

## Resolution

Confirmed by the human on 2026-10-01. The human narrowed the audit rather than adding maintenance infrastructure for imported bundles. This supersedes the earlier derivative-maintenance and provenance-recording choices discussed in this session.

### Scope and admission

Exclude imported skill entry points from the audit and implementation plan. The current importer mappings identify 23 excluded published entries: 19 multi-source imports and four Addy imports. Their names, configured origins, and source-level refresh behavior are recorded in [Import and Packaging Evidence](../import-ownership-evidence.md). The remaining audit pool contains 32 published candidates and five repository-local candidates, for 37 total; [the current inventory](../local-inventory.md#current-audit-scope) lists them.

Review those remaining candidates. Remove any additional imports established by clear evidence encountered during scope intake or review. A configured importer relationship is enough to exclude its target here; an absent mapping does not prove repository authorship. Unknown historical origin alone does not block reviewing a remaining candidate.

Do not perform historical provenance recovery, establish imported local derivatives, maintain upstream deviation records, plan refresh reconciliation, or create a lasting provenance ledger in this effort. Imported skill quality, evaluation, and improvement work are outside the destination. The proposed `docs/skill-provenance/` ledger is rejected for this effort and must not appear as an implementation target.

### Ownership of included skills

The repository maintains the included published and repository-local skills. The eventual ExecPlan includes accepted authoring improvements in both roots and lists their exact skill targets. This decision sets planning scope; implementation authorization comes later.

Repository-local workflow skills retain their repository-specific paths, document-loading rules, and workflow contracts. Published skills retain their intended portable workflows and client constraints. Do not impose published installation or workspace conventions blindly on repository-local skills. Preserve the [adoption policy](set-adoption-rules-and-protected-behavior.md#resolution), including intended triggers, names, approval rules, required dependencies, and document-only acceptance.

The explicit inclusion of the five repository-local skills permits their audit and planning. It does not let automated documentation maintenance edit `.agents/skills/`; that workflow remains restricted to canonical instructions and memory.

### Shared resources and installed files

Inspect shared resources only as dependencies of included skills: identify required ownership, relative paths, availability, and the relevant installed file set. Keep existing sharing where those contracts are explicit. Move or duplicate references only when an accepted improvement preserves the included skill's behavior and required access.

Do not audit or revise excluded skill bundles or their imported resources. An included skill's dependency on an excluded skill remains a dependency contract to inspect; exclusion does not authorize removing that dependency or redesigning the excluded skill.

For published candidates, assess references against the actual installer rules. The Bash installer omits per-skill evaluations, README.md, LICENSE.txt, and LICENSE.md, while shared references copy when their repository source exists. Repository-local skills are not published by that installer. The linked evidence describes source behavior, not runtime validation or PowerShell conformance.

### Tooling and follow-on boundaries

Concrete importer, installer, or validator findings that affect included skills are separate scoped proposals, with their dependency on the accepted authoring change stated. This decision does not authorize broad infrastructure repair. Do not add imported refresh automation or ledger work to the ExecPlan.

Keep human-only import scripts human-run. No importer, installer, upstream fetch, live model baseline, or skill implementation ran in this session.

### Map consequences

Apply the reduced scope to the map, effort brief, evidence/model ticket, batch/report ticket, and completion gates. Preserve the 60-entry inventory as the original total and record the 23 known exclusions separately; do not report those exclusions as reviewed or improved skills.

Only [Set Audit Evidence and Model Coverage](set-audit-evidence-and-model-coverage.md) remains on the open frontier. The batch/report ticket still waits on that evidence decision. This session resolves only the ownership ticket.
