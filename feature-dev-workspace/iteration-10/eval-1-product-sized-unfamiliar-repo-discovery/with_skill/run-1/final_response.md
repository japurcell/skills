# Response: Feature-dev for Product-Sized Work in Unfamiliar Repos

**Track**: Standard. The request is to analyze one well-defined skill file against a specific use case gap, identify what needs to change, and formulate questions. There's meaningful ambiguity about what "product-sized" means — enough to warrant a handful of targeted questions — but the scope is bounded. Deep is unwarranted here.

---

## Understanding

The user wants `feature-dev` to hold up when two conditions stack: **product-scale scope** (work that spans multiple subsystems or requires product-level decisions, not just technical ones) and **unfamiliar repositories** (no prior mental model of the codebase, team, or dev environment). The request stops at discovery — "before editing anything" — so this response covers findings, open questions, and a recommended approach only.

---

## Relevant Findings

From reading `skills/feature-dev/SKILL.md` (current iteration-10 version):

**1. "Unfamiliar codebases" appears in the description but has no procedural counterpart.**
The frontmatter says "Structured feature development for medium-to-large changes in unfamiliar codebases," but Phase 2 has no step that operationalizes "unfamiliar." There's no orientation step, no instruction to read the README or locate the CI config before launching code-explorer agents. When a repo is genuinely foreign, agents walk straight into feature-targeted exploration without anchoring in the actual dev environment, test runner, or team conventions.

**2. All Phase 2 code-explorer prompt templates are feature-scoped.**
The four example prompts in Phase 2: "Find features similar to...", "Map the architecture...", "Analyze the current implementation...", "Identify UI patterns, testing approaches, or extension points." Every one assumes you already know roughly where you are. There's no template for: "I've never been in this repo — orient me to its structure, dev environment, and ownership model before I dig into feature specifics."

**3. Phase 3 clarifying questions are implementation-layer only.**
The guidance lists: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs. These are all technical. For product-sized work in an unfamiliar repo, the first blocking unknowns are often one level up: release milestone, migration plan, which team owns the affected area, whether a breaking change is acceptable to stakeholders, or whether the work overlaps an active sprint elsewhere. Nothing in the current Phase 3 surfaces these.

**4. The Deep track is for "large, risky, cross-cutting" work — but not for product-contextually uncertain work.**
Deep addresses size and technical complexity. It doesn't address the scenario where you know roughly what to build technically but have no context on the product domain, release cadence, or ownership model. These are different axes. Large + well-understood product context is a Deep track problem. Large + unfamiliar product context is a gap the skill doesn't name.

**5. Phase 5 (TDD) and Phase 6 (code-simplifier + code-reviewer) are already well-handled.**
Phase 5 mandates TDD with an explicit red-green-refactor loop on every track and says "do not bypass it." Phase 6 now has two mandatory steps: (1) launch an independent code-simplifier subagent for refactoring opportunities, (2) run independent code-reviewer subagents — Light: at least one; Standard/Deep: multiple in parallel with different focuses. These are correct and complete. Any implementation of the proposed changes must preserve these requirements exactly — they don't need to change.

---

## Open Questions

Three questions that materially affect which changes to make and how far to go:

1. **What's the most common failure mode you've encountered?**
   Possible failures point to different fixes:
   - Agent never checks how to build or test the repo → fix is a repo-orientation step in Phase 2
   - Agent asks technically correct questions but misses the product blocker (release freeze, migration policy) → fix is a product-context question cluster in Phase 3
   - Agent produces a technically sound plan that the team can't use because it ignores ownership or constraints → fix is a broader product-context orientation early in the process
     Knowing which is the primary failure narrows the scope significantly.

2. **Is "product-sized" primarily about scope or context?**
   - Scope: work spans multiple subsystems or will take multiple sprints
   - Context: you don't know the product domain, team structure, or release constraints
     Both are problems, but the fixes are different. Scope → the existing Deep track mostly handles it if its exploration guidance is improved. Context → requires actively surfacing product-layer questions that don't currently appear anywhere in the skill.

3. **Should the changes be purely additive, or is there a case for a new track?**
   A "Product track" (between Standard and Deep) could explicitly target product-scale + unfamiliar-repo work as a named category. Alternatively, targeted additions to Phase 2 and Phase 3 would cover both without introducing another branch. The additive approach is lower risk and easier to calibrate; a new track signals the distinction more clearly. Will depend on how often this case actually comes up in practice.

---

## Recommendation

Three targeted additions — each tied to a concrete gap. Whether all three are needed depends on answers to the questions above, but each is independent enough that any subset could be made.

---

### Change 1 — Repo orientation sub-step in Phase 2

**Gap**: Code-explorer agents in unfamiliar repos produce accurate architecture summaries but may miss foundational conventions because they launch without any orientation.

**Proposed addition**: Before launching code-explorer agents, add an explicit orientation step triggered when the repo is unfamiliar (indicated by user context or the agent's own assessment). The agent itself does a short pass: read the README, find CI config (`.github/workflows`, `Makefile`, `Taskfile`, etc.), identify the test runner, note the build system. This takes less than a minute and provides the anchor that downstream agents need to give actionable rather than theoretical findings.

**Why this specifically helps unfamiliar repos**: Without it, exploration is technically accurate but can produce plans like "run `pytest`" in a repo that uses a custom test runner, or "extend the config module" in a repo where config is managed by a service mesh the agent never discovered. Orientation prevents these mismatches.

---

### Change 2 — Product-context question cluster in Phase 3

**Gap**: Phase 3 question categories are all implementation-level; product-scale work commonly blocks on product-layer constraints that never get asked.

**Proposed addition**: Add a named product-context question cluster to Phase 3, surfaced conditionally for large or product-sized work. Examples: release milestone or code freeze, migration or backward-compatibility strategy, which team owns the affected area, whether a breaking change requires stakeholder sign-off, and known in-flight work that might intersect. These are asked before implementation-layer questions when scope is large, not after.

**Why this specifically helps product-sized work**: A technically complete plan that ignores a two-week code freeze or a migration policy creates rework. Surfacing these constraints early means the design can account for them rather than discovering them mid-implementation.

---

### Change 3 — Repo-orientation agent prompt template in Phase 2

**Gap**: All four existing agent prompt templates assume you already know where you are. There's no template for the "I've never been in this repo" case.

**Proposed addition**: Add one new example prompt to the Deep track agent prompt list: _"Map this repository's development environment: how to build, test, and run the project; the CI/CD pipeline; major naming and testing conventions; and the ownership model for its main areas. Surface anything a developer who has never seen this repo would need to know before making a large change."_ This gives agents a concrete, repeatable orientation prompt rather than defaulting to architecture exploration when dev context is the higher-priority gap.

---

## What to Keep Unchanged

- **Phase 5 TDD requirement** — mandatory on every track with explicit red-green-refactor loop; "do not bypass it" is already in the skill. Any implementation of the above changes must continue to require this.
- **Phase 6, Step 1: code-simplifier subagent** — mandatory after implementation on every track. Any implementation of the above changes must continue to require this.
- **Phase 6, Step 2: independent code-reviewer subagents** — mandatory on every track (Light: at least one; Standard/Deep: multiple in parallel). Any implementation of the above changes must continue to require this.

These three requirements are the right constraints at the right scope. They should not be weakened or made conditional when adding repo-orientation or product-context guidance.

---

## Next Step

Answers to the three open questions above would confirm whether all three changes are needed or which one is the primary fix. If the failure mode is primarily dev-environment orientation (Change 1 + 3), the product-context question cluster (Change 2) can be deferred. If the main failure is product-layer blocking questions being skipped, Change 2 is the priority and the exploration changes follow. Once direction is confirmed, implementation via the TDD loop on the current skill file is straightforward.
