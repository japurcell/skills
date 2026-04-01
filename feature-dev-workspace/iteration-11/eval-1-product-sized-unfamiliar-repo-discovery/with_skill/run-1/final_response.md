# Response: Feature-dev for Product-Sized Work in Unfamiliar Repos

**Track**: Standard. Improving one well-scoped skill file against a specific use-case gap is bounded enough to avoid the overhead of the Deep track. There is real ambiguity about what "product-sized" and "unfamiliar" mean in practice — enough to warrant a small set of targeted questions — but the scope is contained.

---

## Understanding

The user wants `feature-dev` to hold up when two conditions stack: **product-scale scope** (work that spans multiple subsystems or requires product-level decisions, not just technical ones) and **unfamiliar repositories** (no prior mental model of the codebase, team, dev environment, or release cadence). The request stops at discovery — "before editing anything" — so this response covers findings, open questions, and a recommended approach only.

---

## Relevant Findings

From reading `skills/feature-dev/SKILL.md` (current iteration-11 version):

**1. "Unfamiliar codebases" appears in the description but has no procedural counterpart.**
The frontmatter says "Structured feature development for medium-to-large changes in unfamiliar codebases," but Phase 2 has no step that operationalizes "unfamiliar." There is no orientation step, no instruction to read the README or locate the CI config before launching code-explorer agents. When a repo is genuinely foreign, agents walk straight into feature-targeted exploration without anchoring in the actual dev environment, test runner, or team conventions.

**2. All Phase 2 agent prompt templates are feature-scoped.**
The four example prompts in Phase 2 are: "Find features similar to...", "Map the architecture...", "Analyze the current implementation...", "Identify UI patterns, testing approaches, or extension points." Every one assumes you already know roughly where you are. There is no template for: "I have never been in this repo — orient me to its structure, dev environment, and ownership model before I dig into feature specifics."

**3. Phase 3 clarifying question categories are all implementation-layer.**
The listed categories are: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs. These are technical. For product-sized work in an unfamiliar repo, the first blocking unknowns are often one level up: release milestone, migration policy, which team owns the affected area, whether a breaking change is acceptable to stakeholders, or whether the work overlaps an active sprint elsewhere. Nothing in Phase 3 surfaces these.

**4. The Deep track addresses size and technical risk, not product-contextual uncertainty — a distinct axis.**
Deep is for "large, risky, cross-cutting, or highly ambiguous work." It doesn't explicitly address the scenario where you know roughly what to build technically but have no context on product domain, release cadence, or ownership model. Large + well-understood product context is a Deep track problem. Large + unfamiliar product context is a gap the skill doesn't name or address.

**5. Phase 5 TDD and Phase 6 quality steps are already well-enforced in the current skill.**
Phase 5 mandates TDD with an explicit red-green-refactor loop on every track and says "Treat this as required for Implementation on every track; do not bypass it." Phase 6 now has two mandatory steps in sequence: (1) launch an independent code-simplifier subagent for refactoring opportunities after implementation, then (2) run independent code-reviewer subagents — Light: at least one; Standard/Deep: multiple in parallel with different focuses. These are correct, complete, and do not need to change. Any implementation of the proposed additions must preserve them exactly.

---

## Open Questions

Three questions that materially affect which changes to make and how far to go:

1. **What is the most common failure mode you have actually encountered?**
   Possible failures point to different fixes:
   - Agent never checks how to build or test the repo → fix is a repo-orientation step in Phase 2
   - Agent asks technically correct questions but misses a product blocker (release freeze, migration policy) → fix is a product-context question cluster in Phase 3
   - Agent produces a technically sound plan that the team cannot use because it ignores ownership or in-flight constraints → fix is a broader product-context orientation earlier in the process
     Knowing which failure is most common narrows the scope significantly and avoids over-engineering the skill.

2. **Is "product-sized" primarily about scope or context?**
   - Scope: work spans multiple subsystems or will take multiple sprints
   - Context: you don't know the product domain, team structure, or release constraints
     Both are problems, but the fixes are different. Scope → the existing Deep track mostly handles it if its exploration guidance is improved. Context → requires actively surfacing product-layer questions that currently appear nowhere in the skill.

3. **Should the changes be purely additive, or is a new track worth considering?**
   A named "Product track" (between Standard and Deep) could explicitly target product-scale + unfamiliar-repo work. Alternatively, focused additions to Phase 2 and Phase 3 would cover both without introducing a new branch. Additive is lower risk and easier to calibrate; a new track makes the distinction more visible. The right answer depends on how often this combined case actually comes up in practice.

---

## Recommendation

Three targeted additions — each tied to a concrete gap in the current skill. These are independent; any subset could be applied based on answers to the questions above.

---

### Change 1 — Repo orientation sub-step in Phase 2

**Gap**: Code-explorer agents in unfamiliar repos launch directly into feature-scoped exploration without any anchoring in the actual dev environment, leaving them able to produce plans that are technically accurate but operationally wrong.

**Proposed addition**: Before launching code-explorer agents, add an explicit orientation step that triggers when the repo is unfamiliar (indicated by user context or the agent's own assessment). The agent does a short self-directed pass: read the README, find the CI config (`.github/workflows`, `Makefile`, `Taskfile`, etc.), identify the test runner, note the build system. This takes minimal time and provides the anchor that downstream agents need to give actionable — not theoretical — findings.

**Why this specifically helps unfamiliar repos**: Without it, exploration can produce plans like "run `pytest`" in a repo that uses a custom test runner, or "extend the config module" in a repo where config is managed by a service mesh the agent never discovered. Orientation prevents these mismatches before they reach design or implementation.

---

### Change 2 — Product-context question cluster in Phase 3

**Gap**: Phase 3 question categories are all implementation-level. Product-scale work in an unfamiliar repo commonly blocks on product-layer constraints that currently never get asked.

**Proposed addition**: Add a named product-context question cluster to Phase 3, surfaced conditionally for large or product-sized work. Examples include: release milestone or code freeze, migration or backward-compatibility policy, which team owns the affected area, whether a breaking change requires stakeholder sign-off, and known in-flight work that may intersect. These should be surfaced before implementation-layer questions when scope is large, not as an afterthought.

**Why this specifically helps product-sized work**: A technically complete plan that ignores a two-week code freeze or a migration policy creates rework. Surfacing these constraints early means the design can account for them rather than discovering them mid-implementation.

---

### Change 3 — Repo-orientation agent prompt template in Phase 2

**Gap**: All four existing example agent prompts assume you already know where you are. There is no template for the "I have never been in this repo" case, so agents default to architecture exploration when dev context is the higher-priority gap.

**Proposed addition**: Add one new example prompt to the Deep-track agent prompt list (or as a conditional addition for any unfamiliar-repo scenario): _"Map this repository's development environment: how to build, test, and run the project; the CI/CD pipeline; major naming and testing conventions; and the ownership model for its main areas. Surface anything a developer who has never seen this repo would need to know before making a large change."_ This gives agents a concrete, repeatable orientation prompt with no ambiguity about what to cover.

---

## What to Keep Unchanged

- **Phase 5 TDD requirement** — "Treat this as required for Implementation on every track; do not bypass it" is already in the skill. Any implementation of the above changes must continue to enforce TDD with the explicit red-green-refactor loop. This should not be weakened or made conditional.
- **Phase 6, Step 1: code-simplifier subagent** — already required as the first independent pass after implementation. Any implementation of the above changes must keep this step mandatory and sequenced before the reviewer pass.
- **Phase 6, Step 2: independent code-reviewer subagents** — already required on every track (Light: at least one; Standard/Deep: multiple in parallel with focused areas). Any implementation of the above changes must keep this step mandatory.

These three requirements are established at the right scope and should not be disturbed when adding repo-orientation or product-context guidance.

---

## Next Step

Awaiting answers to the three open questions above before editing. Once the primary failure mode and the scope-vs-context framing are confirmed, the right subset of changes can be drafted precisely.
