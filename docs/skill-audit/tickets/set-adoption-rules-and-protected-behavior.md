# Set Adoption Rules and Protected Behavior

**Type:** grilling
**Status:** closed
**Blocked By:** extract-complete-authoring-checklist.md, establish-provider-compatibility-constraints.md
**Research Dir:** not applicable

## Question

How should every researched authoring recommendation be assessed against repository intent and provider compatibility, and which behaviors must improvements preserve?

The human chose authoring improvements that preserve intended behavior and approval rules, with behavior redesigns presented separately. Define evidence-backed dispositions: adopt, adapt, not applicable to this skill, or incompatible with a required provider. Require a rationale for adaptations and exclusions. Distinguish requirements from conditional advice and heuristics, including length guidance. Decide how findings expose trigger gaps, unclear branches, excessive context, missing feedback loops, stale references, and behavior changes while preserving user-owned approval boundaries and invocation controls.

The decision must define the rubric, finding severity and evidence fields, exception handling, and how to present semantic changes for a separate human decision.

---

## Resolution

The human confirmed all five policies below in two rounds on 2026-10-01. They govern the audit and proposed implementation plan; they do not authorize skill implementation.

### Adoption rubric

Review the complete [authoring checklist](../research/authoring-checklist/findings.md) for each in-scope maintained skill, using the [provider comparison](../research/provider-compatibility/findings.md) to qualify client-specific claims. Scope is governed by [Decide Skill Ownership and Import Handling](decide-skill-ownership-and-import-handling.md); the later exclusion of imported skills does not change this rubric. Record each check's source, applicability conditions, and strength: repository requirement, required-client requirement, or advisory guidance. Cite the actual requirement rather than transferring a Claude constraint into another provider's contract.

Use four dispositions:

- **Adopt:** Apply the recommendation as written where its conditions hold and required clients support it. This disposition selects an audit criterion; it does not mean the existing skill already satisfies it.
- **Adapt:** Preserve the recommendation's purpose using a supported form that preserves the skill's intended behavior. Record the original guidance, adaptation, affected surfaces, evidence, and rationale.
- **Not applicable:** The recommendation's condition does not occur in this skill. Record the specific reason, such as no bundled executable resources.
- **Incompatible with a required provider:** A documented client constraint prevents adoption and no supported adaptation preserves the contract. Name the affected surface and constraint, and record adaptations considered.

Missing evidence is an unresolved evidence state, not a fifth disposition or proof of incompatibility. Track it without selecting an unsupported disposition. Keep applicability, disposition, and current compliance distinct.

Treat actual repository and required-client requirements as binding within their documented scope, subject to explicit user-approved exceptions. Advisory guidance prompts inspection and judgment. The 500-line body target, 100-line reference navigation target, Claude's suggested evaluation counts, naming preferences, and writing patterns are not automatic audit failures. Identify the concrete clarity, retrieval, reliability, or context problem before recommending a change. Do not remove useful instructions or controls merely to satisfy a length target.

### Protected behavior and intended scope

Define intent from documented purpose, explicit instructions, and user-approved decisions. Existing evaluations and usage evidence support that definition but cannot override its contracts. When those sources conflict or leave intent unclear, record the conflict and leave the behavior decision unresolved.

Authoring improvements preserve intended task scope and triggers; invocation controls; approval boundaries; required dependencies and delegation; stopping and handoff rules; output contracts; existing directory and frontmatter names; and document-only constraints. Wording, reordering, deduplication, and reference moves qualify only when they preserve these outcomes and prerequisites, including unique exceptions. Description improvements that activate the skill within its documented intended scope qualify as authoring.

Changes to task scope, approval or autonomy rules, required dependencies, skill names, output contracts, or other observable behavior require a separate human decision. In particular, making a required dependency optional is a redesign. A user waiver for one effort does not authorize a repository-wide rewrite of that dependency.

Preserve the invocation and document-only controls of `dotnet-upgrade`, including its separately scoped installation and live-evaluation restrictions. Audit inclusion does not grant execution approval. Follow the [skills instructions](../../../.agents/instructions/skills.md) and [document-review acceptance scope](../../../.agents/memory/testing/skills.md#dotnet-upgrade-document-review).

### Exception handling

Prefer a supported, behavior-equivalent adaptation before excluding guidance. Provider adapters and metadata are surface-specific; evidence of one client's behavior does not establish another client's enforcement.

When validation tooling rejects a retained invocation control, record the tooling gap and its consequence for validation. Do not remove the control or report the rejected validation as passing. The repository's [known validator/control incompatibility](../../../.agents/memory/known-issues/skills.md) is a recorded example. Its document-only exception remains scoped.

Every adaptation, exclusion, or approved exception records the affected skill/check and client surface, source or user decision, rationale, and remaining evidence limits. Apply an exception only within its approved scope. Unsupported runtime or model assumptions remain unverified and feed later evidence work.

### Finding severity and evidence

Rank findings by consequence rather than word count or number of checklist deviations:

| Severity | Meaning |
| --- | --- |
| Blocker | Unsafe behavior or an unusable required operation. |
| Major | Likely wrong results or failure of the intended workflow. |
| Minor | A localized clarity or navigation problem. |
| Observation | A suggestion without demonstrated impact. |

State the failure path and impact supporting the severity. Label predicted runtime impact as an inference. Confidence and severity are separate: incomplete evidence does not make a potential serious consequence harmless.

Each finding records:

- Affected skill and file with a line anchor.
- Checklist source or repository/client requirement, applicability, and disposition or unresolved evidence state.
- Concrete evidence and failure mechanism, with artifact links where available.
- Affected provider/client surface, and model/version/configuration when behavioral evidence exists.
- Proposed improvement and whether it preserves the contract or requires a separate behavior decision.
- Severity, confidence with its basis, adaptation/exception rationale where relevant, and validation still needed.

Distinguish static observations, observed runtime behavior, and untested claims. Static evidence can establish a textual contradiction, missing resource, or documented contract mismatch without proving a behavioral failure. Runtime claims require actual run artifacts for the tested configuration. Existing eval files alone do not establish coverage or passing behavior. The evidence and model ticket determines the precise run matrix and validation gates.

### Downstream use

Accepted authoring proposals enter the implementation plan with their evidence and validation obligations. Present semantic changes separately with current behavior, proposed behavior, rationale, tradeoffs, and the exact human decision needed. Do not silently treat an unresolved proposal as an accepted improvement.

This resolution unblocks [Decide Skill Ownership and Import Handling](decide-skill-ownership-and-import-handling.md). Evidence/model coverage and batch/report decisions remain separate tickets.
